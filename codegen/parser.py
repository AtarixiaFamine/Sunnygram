"""Parse the vendored TL schema into definition records.

TL is a formal grammar, which is the whole reason the wire layer can be
generated instead of typed out. This module only understands the grammar.
Deciding what to emit, and what it looks like in Python, is gen_tl.py's job.

Everything the grammar can express and these schemas use is handled: namespaced
names, multiple flag bitfields with conditional fields, flag-only booleans that
occupy no bytes, boxed and bare vectors, bare constructor references, generic
functions, and constructor ids that the schema leaves implicit.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from zlib import crc32

SCHEMA_DIR = Path(__file__).resolve().parent / "schema"

# The codec handles these itself, so they are never generated. Bool is read as a
# Python bool and the bare primitives have no constructor of their own.
SKIPPED = {
    "int",
    "long",
    "double",
    "string",
    "bytes",
    "vector",
    "int128",
    "int256",
    "boolTrue",
    "boolFalse",
    "true",
}

# TL spellings that map onto a codec primitive rather than a generated class.
PRIMITIVE_KINDS = {
    "int": "int",
    "long": "long",
    "double": "double",
    "string": "string",
    "bytes": "bytes",
    "int128": "int128",
    "int256": "int256",
    "Bool": "bool",
    "true": "flag",
    "Object": "object",
}

_DEFINITION = re.compile(
    r"^(?P<name>[A-Za-z_][A-Za-z0-9_.]*)"
    r"(?:#(?P<id>[0-9a-fA-F]{1,8}))?"
    r"(?P<body>[^=]*)"
    r"=\s*(?P<result>[^;]+);"
)
_GENERIC_DECL = re.compile(r"\{([A-Za-z]\w*):Type\}")
_CONDITIONAL = re.compile(r"^(flags\d*)\.(\d+)\?(.+)$")
_FLAG_ONLY_ARG = re.compile(r"\s\w+:flags\d*\.\d+\?true")


@dataclass(frozen=True, slots=True)
class Primitive:
    """A type the codec reads directly.

    kind is one of the codec primitives, plus "flag" for a field whose only
    content is the flag bit itself, and "object" for a boxed anything.
    """

    kind: str


@dataclass(frozen=True, slots=True)
class Vector:
    """A repeated field. boxed is False for the bare lowercase spelling, which
    carries no vector constructor id on the wire."""

    item: ParamType
    boxed: bool


@dataclass(frozen=True, slots=True)
class Reference:
    """A reference to another TL type. bare means a specific constructor,
    written in lower case, whose id is not on the wire."""

    name: str
    bare: bool


@dataclass(frozen=True, slots=True)
class Generic:
    """The !X of a wrapper function, standing for any other function."""

    name: str


ParamType = Primitive | Vector | Reference | Generic


@dataclass(frozen=True, slots=True)
class Param:
    name: str
    type: ParamType
    # ("flags", 3) when the field is only present if that bit is set.
    flag: tuple[str, int] | None

    @property
    def optional(self) -> bool:
        return self.flag is not None


@dataclass(frozen=True, slots=True)
class Definition:
    name: str
    id: int
    params: tuple[Param, ...]
    result: ParamType
    result_text: str
    is_function: bool
    schema: str
    generics: tuple[str, ...]
    # The id the schema spelled out, if it did. Kept so a test can hold our
    # reading of the grammar against Telegram's own hashes.
    declared_id: int | None
    signature: str

    @property
    def namespace(self) -> str:
        head, _, tail = self.name.rpartition(".")
        return head

    @property
    def short_name(self) -> str:
        return self.name.rpartition(".")[2]

    @property
    def class_name(self) -> str:
        return pascal_case(self.short_name)

    @property
    def flag_fields(self) -> tuple[str, ...]:
        return tuple(
            param.name for param in self.params if param.type == Primitive("flags")
        )


def pascal_case(name: str) -> str:
    """req_pq_multi to ReqPqMulti, inputPeerEmpty to InputPeerEmpty.

    Only the first letter of each underscore-separated part is touched, so a
    part that is already shouting keeps its case: server_DH_params stays DH.
    """
    return "".join(part[:1].upper() + part[1:] for part in name.split("_") if part)


def parse_type(text: str) -> ParamType:
    text = text.strip()
    if text.startswith("!"):
        return Generic(text[1:])
    if text.startswith("%"):
        inner = parse_type(text[1:])
        if isinstance(inner, Reference):
            return Reference(inner.name, bare=True)
        return inner
    if text[:7].lower() == "vector<":
        return Vector(
            parse_type(text[text.index("<") + 1 : text.rindex(">")]),
            boxed=text[0] == "V",
        )
    kind = PRIMITIVE_KINDS.get(text)
    if kind is not None:
        return Primitive(kind)
    return Reference(text, bare=text.rpartition(".")[2][:1].islower())


def parse_param(token: str) -> Param:
    name, _, type_text = token.partition(":")
    if type_text == "#":
        return Param(name, Primitive("flags"), None)
    conditional = _CONDITIONAL.match(type_text)
    if conditional:
        return Param(
            name,
            parse_type(conditional[3]),
            (conditional[1], int(conditional[2])),
        )
    return Param(name, parse_type(type_text), None)


def _signature(name: str, body: str, result: str) -> str:
    """The text Telegram hashes to get a constructor id.

    Braces come off the generic declaration but the declaration itself stays,
    and so does the ! of a generic argument. Angle brackets become spaces,
    bytes is spelled string, and flag-only fields do not count because they
    occupy no bytes. Reproducing this is how the parser proves it read the
    grammar the same way Telegram did.
    """
    text = f"{name} {body} = {result}"
    text = text.replace("{", "").replace("}", "")
    text = text.replace(":bytes", ":string").replace("?bytes", "?string")
    text = text.replace("<", " ").replace(">", " ")
    text = _FLAG_ONLY_ARG.sub("", text)
    return " ".join(text.split())


def parse_schema(text: str, schema: str) -> list[Definition]:
    definitions: list[Definition] = []
    is_function = False
    for raw_line in text.splitlines():
        line = raw_line.split("//", 1)[0].strip()
        if not line:
            continue
        if line.startswith("---"):
            is_function = line.strip("- ") == "functions"
            continue

        match = _DEFINITION.match(line)
        if match is None:
            raise ValueError(f"cannot parse {schema}.tl line: {raw_line!r}")

        name = match["name"]
        if name in SKIPPED:
            continue

        body = match["body"]
        generics = tuple(_GENERIC_DECL.findall(body))
        tokens = _GENERIC_DECL.sub(" ", body).split()
        if any(token in {"?", "#"} or "*[" in token for token in tokens):
            # A core type declared in terms of itself, such as int ? = Int.
            continue

        signature = _signature(name, body, match["result"])
        declared_id = int(match["id"], 16) if match["id"] else None
        definitions.append(
            Definition(
                name=name,
                id=declared_id
                if declared_id is not None
                else crc32(signature.encode()),
                params=tuple(parse_param(token) for token in tokens),
                result=parse_type(match["result"]),
                result_text=match["result"].strip(),
                is_function=is_function,
                schema=schema,
                generics=generics,
                declared_id=declared_id,
                signature=signature,
            )
        )
    return definitions


def parse_all() -> list[Definition]:
    """Every definition from every vendored schema, mtproto first."""
    definitions: list[Definition] = []
    for schema in ("mtproto", "api"):
        path = SCHEMA_DIR / f"{schema}.tl"
        definitions += parse_schema(path.read_text(encoding="utf-8"), schema)
    return definitions


def main() -> None:
    definitions = parse_all()
    types = [d for d in definitions if not d.is_function]
    functions = [d for d in definitions if d.is_function]
    namespaces = {d.namespace for d in definitions}
    mismatched = [
        d
        for d in definitions
        if d.declared_id is not None and crc32(d.signature.encode()) != d.declared_id
    ]
    print(f"types      {len(types)}")
    print(f"functions  {len(functions)}")
    print(f"namespaces {len(namespaces) - 1} plus the root")
    print(f"implicit ids {sum(1 for d in definitions if d.declared_id is None)}")
    print(f"id mismatches {len(mismatched)}")
    for definition in mismatched[:10]:
        print(f"  {definition.name}: {definition.signature}")


if __name__ == "__main__":
    main()
