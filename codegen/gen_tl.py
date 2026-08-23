"""Emit the generated raw package from the vendored TL schema.

    python codegen/gen_tl.py

Constructors go under raw/types, invokable functions under raw/functions, and
the set of forms an abstract type can take under raw/base. Modules are grouped
by TL namespace and each package's __init__ loads a module on first use, so
importing sunnygram costs nothing and reaching for one namespace does not drag
in the rest (rule P7). The grouping sits behind that lazy __init__, so it can be
made finer later without moving a single public name.

Neither schema names a namespace for its own core definitions, so there are two
modules for what TL leaves unnamed: mtproto.tl's go in mtproto and api.tl's in
_root. Splitting them is what lets the connection layer import the forty service
constructors it speaks in without the two thousand API ones it never touches.

The base aliases are for type checkers only. A union has no useful runtime form,
and building one would mean importing every constructor up front, which is what
the lazy layout exists to avoid.

Nothing under raw/ is hand-edited (rule H7); tests/test_codegen.py fails if the
tree on disk is not what this script produces.
"""

from __future__ import annotations

import json
import keyword
import shutil
from dataclasses import dataclass, field, replace
from pathlib import Path

import overrides
from parser import (
    SCHEMA_DIR,
    Definition,
    Generic,
    Param,
    ParamType,
    Primitive,
    Reference,
    Vector,
    parse_all,
    pascal_case,
)

RAW_DIR = Path(__file__).resolve().parents[1] / "src" / "sunnygram" / "raw"
ROOT = "_root"
MTPROTO = "mtproto"
FLAGS = Primitive("flags")
FLAG = Primitive("flag")

# The type variable a generated function names its result with. It lives in the
# codec beside TLFunction, so the generated tree imports it rather than
# declaring one per module.
RESULT_PARAM = "TLResult"

ANNOTATIONS = {
    "int": "int",
    "long": "int",
    "int128": "int",
    "int256": "int",
    "double": "float",
    "string": "str",
    "bytes": "bytes",
    "bool": "bool",
    "flag": "bool",
    "object": "TLObject",
}
READERS = {
    "int": "read_int",
    "long": "read_long",
    "int128": "read_int128",
    "int256": "read_int256",
    "double": "read_double",
    "string": "read_string",
    "bytes": "read_bytes",
    "bool": "read_bool",
    "object": "read_object",
}
WRITERS = {
    "int": "write_int",
    "long": "write_long",
    "int128": "write_int128",
    "int256": "write_int256",
    "double": "write_double",
    "string": "write_string",
    "bytes": "write_bytes",
    "bool": "write_bool",
}

# The primitives whose wire form is a fixed number of bytes that struct can lay
# out in one call, and the code for each. int128 and int256 are fixed-width too
# and are not here: struct has nothing that wide, so they would have to be built
# a half at a time, which is the field-by-field writing this exists to avoid.
PACKABLE = {"int": "i", "long": "q", "double": "d"}

# Below this, packing is not worth the second copy of the writing. Two fields
# measured 1.8x on ints and 4.4x on longs, one field is a call either way.
PACK_FROM = 2


@dataclass
class Context:
    """Where every generated name lives, resolved before a line is emitted."""

    # TL abstract type name to (module key, python class name).
    bases: dict[str, tuple[str, str]] = field(default_factory=dict)
    # TL constructor name to (module key, python class name).
    constructors: dict[str, tuple[str, str]] = field(default_factory=dict)
    # Fields that had to be spelled differently, reported after a run.
    renamed: dict[str, str] = field(default_factory=dict)

    def base_annotation(self, name: str) -> str:
        if name not in self.bases:
            raise SystemExit(f"nothing in the schema produces the type {name}")
        module, class_name = self.bases[name]
        namespace = module.split(".", 1)[1]
        if namespace == ROOT:
            return f"base.{class_name}"
        return f"base.{namespace}.{class_name}"

    def bare_class(self, name: str) -> str:
        if name not in self.constructors:
            raise SystemExit(f"bare reference to unknown constructor {name}")
        return self.constructors[name][1]


def corrected(definition: Definition) -> Definition:
    """Fix the fields the schema calls string but fills with binary.

    See the note on MTPROTO_TEXT_FIELDS. This only changes the Python type: TL
    encodes string and bytes identically, and the constructor id is hashed from
    the schema text either way, so nothing on the wire moves.
    """
    changed = False
    params = []
    for param in definition.params:
        key = f"{definition.name}.{param.name}"
        binary = param.type == Primitive("string") and (
            key in overrides.BYTES_FIELDS
            or (
                definition.schema == "mtproto"
                and key not in overrides.MTPROTO_TEXT_FIELDS
            )
        )
        if binary:
            changed = True
            params.append(replace(param, type=Primitive("bytes")))
        else:
            params.append(param)
    return replace(definition, params=tuple(params)) if changed else definition


def module_key(definition: Definition) -> str:
    """Which module a definition is emitted into.

    A TL namespace becomes a module of the same name. What is left over is the
    two schemas' own unnamed core, and those do not belong together: a
    connection speaks mtproto.tl and nothing else, so putting it in its own
    module is the difference between importing forty constructors and two
    thousand. A namespaced definition stays where its namespace says regardless
    of which file it was read from, which is why help.configSimple is still
    filed under help.
    """
    kind = "functions" if definition.is_function else "types"
    namespace = definition.namespace or (
        MTPROTO if definition.schema == "mtproto" else ROOT
    )
    return f"{kind}.{namespace}"


def base_key(base_name: str) -> str:
    return f"base.{base_name.rpartition('.')[0] or ROOT}"


def qualname(definition: Definition) -> str:
    """How to write this class in Python, which is also where it lives."""
    kind, namespace = module_key(definition).split(".", 1)
    prefix = f"{kind}." if namespace == ROOT else f"{kind}.{namespace}."
    return prefix + definition.class_name


def field_name(param: Param, containers: set[str], ctx: Context) -> str:
    """The Python name of a field.

    Only changed where keeping it would break the generated code: a Python
    keyword, or a clash with a local that read introduces.
    """
    name = overrides.RENAMED_FIELDS.get(param.name, param.name)
    if name in keyword.kwlist or name in {"r", "cls", "self"} or name in containers:
        ctx.renamed[param.name] = name + "_"
        return name + "_"
    return name


def annotation(param_type: ParamType, ctx: Context) -> str:
    if isinstance(param_type, Primitive):
        return ANNOTATIONS[param_type.kind]
    if isinstance(param_type, Reference):
        if param_type.bare:
            return ctx.bare_class(param_type.name)
        return ctx.base_annotation(param_type.name)
    if isinstance(param_type, Vector):
        return f"list[{annotation(param_type.item, ctx)}]"
    if isinstance(param_type, Generic):
        # The !X of a wrapper. Saying it is a function answered with TLResult,
        # rather than any object, is what lets the wrapper pass the wrapped
        # call's result type through to whoever invokes it.
        return f"TLFunction[{RESULT_PARAM}]"
    return "TLObject"


def result_parameter(definition: Definition, ctx: Context) -> str:
    """What a function is declared to be answered with.

    A wrapper such as invokeWithLayer is answered with whatever it wrapped, so
    it stays generic and takes its parameter from the query it carries.
    Everything else names its own result, spelled as a forward reference
    because the base package it lives in has no runtime form.
    """
    result = definition.result
    if isinstance(result, Reference) and result.name in definition.generics:
        return RESULT_PARAM
    return f'"{annotation(result, ctx)}"'


def read_expression(param_type: ParamType, ctx: Context, reader: str = "r") -> str:
    if isinstance(param_type, Primitive):
        return f"{reader}.{READERS[param_type.kind]}()"
    if isinstance(param_type, Reference):
        if param_type.bare:
            return f"{ctx.bare_class(param_type.name)}.read({reader})"
        return f"{reader}.read_object()"
    if isinstance(param_type, Vector):
        arguments = []
        item = _item_reader(param_type.item, ctx)
        if item:
            arguments.append(item)
        if not param_type.boxed:
            arguments.append("boxed=False")
        return f"{reader}.read_vector({', '.join(arguments)})"
    if isinstance(param_type, Generic):
        # The wire hands back a boxed anything, and the field says it is the
        # function this wrapper was built around. Only a server reads one of
        # these, so the assertion is never made against our own traffic.
        return f'cast("TLFunction[{RESULT_PARAM}]", {reader}.read_object())'
    return f"{reader}.read_object()"


def _item_reader(param_type: ParamType, ctx: Context) -> str | None:
    """How to read one vector element, or None to read it as a boxed object."""
    if isinstance(param_type, Primitive):
        return f"TLReader.{READERS[param_type.kind]}"
    if isinstance(param_type, Reference):
        return f"{ctx.bare_class(param_type.name)}.read" if param_type.bare else None
    if isinstance(param_type, Vector):
        return f"lambda nested: {read_expression(param_type, ctx, 'nested')}"
    return None


def write_statement(param_type: ParamType, value: str, ctx: Context) -> str:
    if isinstance(param_type, Primitive):
        if param_type.kind == "object":
            return f"w.write_object({value})"
        return f"w.{WRITERS[param_type.kind]}({value})"
    if isinstance(param_type, Reference):
        return f"{value}.write_body(w)" if param_type.bare else f"{value}.write(w)"
    if isinstance(param_type, Vector):
        arguments = [value]
        item = _item_writer(param_type.item, ctx)
        if item:
            arguments.append(item)
        if not param_type.boxed:
            arguments.append("boxed=False")
        return f"w.write_vector({', '.join(arguments)})"
    return f"{value}.write(w)"


def _item_writer(param_type: ParamType, ctx: Context) -> str | None:
    if isinstance(param_type, Primitive):
        return f"TLWriter.{WRITERS[param_type.kind]}"
    if isinstance(param_type, Reference):
        return "lambda w, item: item.write_body(w)" if param_type.bare else None
    if isinstance(param_type, Vector):
        return f"lambda w, item: {write_statement(param_type, 'item', ctx)}"
    return None


def pack_name(definition: Definition) -> str:
    """What the module-level Struct for a constructor is called.

    Module level rather than a class attribute so that it is one global lookup
    at the point of use and so that it cannot collide with __slots__. Class
    names are unique within a generated module, so this is too.
    """
    return f"_PACK_{definition.class_name}"


def packed_layout(definition: Definition) -> str | None:
    """The struct format for a constructor that can be written in one call.

    Rule P3 says the reading side is shaped for speed; this is the writing side
    of the same argument. A constructor whose fields are all fixed-width and
    none of them conditional has a layout that is known when this file runs, so
    it can be laid out by one struct call instead of one method call per field.
    Measured on this machine: 1.8x at two int fields, 6.8x at thirty, and
    4.4x to 18x on longs, which are a call further from the buffer.

    None for everything else, and "everything else" is most of the schema: one
    flag, one string, one vector or one nested object and the layout stops being
    fixed. That is fine. The constructors this catches are the small dense ones,
    which are the ones sent in quantity.
    """
    if not definition.params:
        return None
    codes = []
    for param in definition.params:
        # A flags field makes the rest of the layout conditional, and a field
        # that is conditional is not always there to be packed.
        if param.optional or not isinstance(param.type, Primitive):
            return None
        code = PACKABLE.get(param.type.kind)
        if code is None:
            return None
        codes.append(code)
    if len(codes) < PACK_FROM:
        return None
    return "<" + "".join(codes)


def emit_class(definition: Definition, ctx: Context) -> list[str]:
    containers = {param.name for param in definition.params if param.type == FLAGS}
    fields = [param for param in definition.params if param.type != FLAGS]
    names = {param.name: field_name(param, containers, ctx) for param in fields}

    if definition.is_function:
        summary = (
            f"The TL function {definition.name}#{definition.id:08x}, "
            f"answered with {definition.result_text}."
        )
    else:
        summary = (
            f"The TL type {definition.name}#{definition.id:08x}, "
            f"a form of {definition.result_text}."
        )

    lines = []
    prepared = packed_layout(definition)
    if prepared is not None:
        lines += [
            f'{pack_name(definition)} = struct.Struct("{prepared}")',
            "",
            "",
        ]
    if definition.is_function:
        base = f"TLFunction[{result_parameter(definition, ctx)}]"
    else:
        base = "TLObject"
    lines += [
        f"class {definition.class_name}({base}):",
        f'    """{summary}"""',
        "",
    ]
    if fields:
        slots = ", ".join(f'"{names[param.name]}"' for param in fields)
        lines.append(f"    __slots__ = ({slots},)")
    else:
        lines.append("    __slots__ = ()")
    lines += [
        "",
        f"    ID = 0x{definition.id:08X}",
        f'    QUALNAME = "{qualname(definition)}"',
    ]
    if definition.is_function:
        lines.append(f'    RESULT = "{definition.result_text}"')
    lines.append("")

    if fields:
        lines += ["    def __init__(", "        self,", "        *,"]
        for param in fields:
            hint = annotation(param.type, ctx)
            if param.type == FLAG:
                hint += " = False"
            elif param.optional:
                hint += " | None = None"
            lines.append(f"        {names[param.name]}: {hint},")
        lines.append("    ) -> None:")
        for param in fields:
            lines.append(f"        self.{names[param.name]} = {names[param.name]}")
        lines.append("")

    # A bitfield with nothing conditional on it still occupies four bytes, but
    # there is no mask to build for it.
    live = {
        param.flag[0] for param in fields if param.flag is not None
    } & containers

    layout = packed_layout(definition)
    lines.append("    def write_body(self, w: TLWriter) -> None:")
    body: list[str] = []
    for container in sorted(live):
        body.append(f"        {container} = 0")
        for param in fields:
            if param.flag is None or param.flag[0] != container:
                continue
            name = names[param.name]
            test = f"self.{name}" if param.type == FLAG else f"self.{name} is not None"
            body += [
                f"        if {test}:",
                f"            {container} |= 1 << {param.flag[1]}",
            ]
    for param in definition.params:
        if param.type == FLAGS:
            body.append(
                f"        w.write_int({param.name})"
                if param.name in live
                else "        w.write_int(0)"
            )
            continue
        if param.type == FLAG:
            continue
        name = names[param.name]
        statement = write_statement(param.type, f"self.{name}", ctx)
        if param.optional:
            body += [f"        if self.{name} is not None:", f"            {statement}"]
        else:
            body.append(f"        {statement}")
    if layout is None:
        lines += body or ["        pass"]
    else:
        # One struct call for the whole body, with the field-by-field writing
        # kept underneath as the fallback rather than replaced. struct is
        # stricter than this library is: write_long takes an id or a hash in
        # either spelling, signed or unsigned, and struct's q refuses anything
        # past 2**63. Those values are ordinary here, so the fast path has to be
        # allowed to fail, and what catches it has to be the writing that was
        # already correct. A pack that raises has written nothing, so the
        # fallback starts from where the fast path began.
        packed = ", ".join(f"self.{names[param.name]}" for param in fields)
        lines += [
            "        try:",
            f"            w.write_raw({pack_name(definition)}.pack({packed}))",
            "        except struct.error:",
        ]
        lines += [f"    {line}" for line in body]
    lines += ["", "    @classmethod", "    def read(cls, r: TLReader) -> Self:"]

    for param in definition.params:
        if param.type == FLAGS:
            lines.append(
                f"        {param.name} = r.read_int()"
                if param.name in live
                else "        r.read_int()"
            )
            continue
        name = names[param.name]
        if param.type == FLAG:
            assert param.flag is not None
            lines.append(
                f"        {name} = bool({param.flag[0]} & (1 << {param.flag[1]}))"
            )
            continue
        expression = read_expression(param.type, ctx)
        if param.optional:
            assert param.flag is not None
            guard = f"{param.flag[0]} & (1 << {param.flag[1]})"
            lines.append(f"        {name} = {expression} if {guard} else None")
        else:
            lines.append(f"        {name} = {expression}")
    # Built without going through __init__. Reading is the hot path of the
    # library, every field has just been read, and a keyword call that only
    # assigns what it was handed costs more than the assignments do. field_name
    # already keeps a field from being called self, so the local is safe.
    lines.append("        self = cls.__new__(cls)")
    for param in fields:
        lines.append(f"        self.{names[param.name]} = {names[param.name]}")
    lines.append("        return self")
    return lines


# Exhibit A of the Mozilla Public License 2.0, which the licence asks to be
# carried by each source file rather than only by the LICENSE at the root. The
# generated tree is source too, so the generator puts it there.
NOTICE = [
    "# This Source Code Form is subject to the terms of the Mozilla Public",
    "# License, v. 2.0. If a copy of the MPL was not distributed with this",
    "# file, You can obtain one at https://mozilla.org/MPL/2.0/.",
    "",
]


def header(layer: int) -> list[str]:
    return NOTICE + [
        f"# Generated from the TL schema at layer {layer}. Do not edit by hand;",
        "# run codegen/gen_tl.py instead.",
    ]


_WHERE = {
    ROOT: "the root namespace",
    MTPROTO: "the MTProto service schema",
}


def _mentions(param_type: ParamType, wanted: str) -> bool:
    if isinstance(param_type, Vector):
        return _mentions(param_type.item, wanted)
    if wanted == "base":
        return isinstance(param_type, Reference) and not param_type.bare
    # A wrapper's !X used to be spelled as any object. It now says which
    # function it holds, so it no longer reaches for TLObject.
    return param_type == Primitive("object")


def emit_definitions_module(
    key: str, definitions: list[Definition], ctx: Context, layer: int
) -> str:
    kind, namespace = key.split(".", 1)
    what = "TL functions" if kind == "functions" else "TL constructors"
    where = _WHERE.get(namespace, f"the {namespace} namespace")

    params = [param for definition in definitions for param in definition.params]
    base_in_fields = any(_mentions(param.type, "base") for param in params)
    needs_object = any(_mentions(param.type, "object") for param in params)
    # A function names its result in its own class header, so the base package
    # is needed by the header as well as by the fields.
    base_in_results = any(
        _mentions(definition.result, "base")
        for definition in definitions
        if definition.is_function
    )
    needs_base = base_in_fields or base_in_results
    # The wrappers, which are the only definitions that stay generic.
    wrappers = any(definition.generics for definition in definitions)

    imports = {"TLReader", "TLWriter"}
    imports.add("TLFunction" if kind == "functions" else "TLObject")
    if needs_object:
        imports.add("TLObject")
    if wrappers:
        imports.add(RESULT_PARAM)

    # Ordered the way ruff sorts a from-import: the constant, then the class,
    # then the function.
    typing_names = ["TYPE_CHECKING"] if needs_base else []
    typing_names.append("Self")
    if wrappers:
        typing_names.append("cast")

    packs = any(packed_layout(definition) for definition in definitions)

    lines = header(layer)
    lines += [
        f'"""{what} in {where}.',
        "",
        "read builds its object directly rather than calling __init__, which",
        "is worth the odd shape: it is the path every incoming byte takes.",
        "",
        "A constructor whose fields are all fixed-width and none of them",
        "conditional has a layout that is known here, so it is written by one",
        "struct call rather than one call per field. The field-by-field version",
        "is kept underneath as the fallback, because struct refuses values this",
        "library accepts: an id or a hash may arrive in either spelling.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "import struct" if packs else "",
        "",
        f"from typing import {', '.join(typing_names)}",
        "",
        f"from ...tl import {', '.join(sorted(imports))}",
    ]
    # An empty line where the import would have been leaves two blank lines in
    # a row, which ruff would rewrite and the drift guard would then fail on.
    lines = [line for index, line in enumerate(lines) if line or lines[index - 1]]
    if needs_base:
        # Where the only mention of base is the result named in a class header,
        # it sits inside a string that ruff does not read as a type, so it has
        # to be told the import is doing something.
        suffix = "" if base_in_fields else "  # noqa: F401"
        lines += ["", "if TYPE_CHECKING:", f"    from .. import base{suffix}"]
    for definition in definitions:
        lines += ["", ""]
        lines += emit_class(definition, ctx)
    return "\n".join(lines) + "\n"


def emit_base_module(
    key: str, unions: dict[str, list[Definition]], layer: int
) -> str:
    namespace = key.split(".", 1)[1]
    where = "the root namespace" if namespace == ROOT else f"the {namespace} namespace"
    modules = sorted({module_key(d) for members in unions.values() for d in members})

    lines = header(layer)
    lines += [
        f'"""The forms each abstract type in {where} can take.',
        "",
        "These aliases are for type checkers. They have no runtime form, because",
        "building one would mean importing every constructor up front.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import TYPE_CHECKING",
        "",
        "if TYPE_CHECKING:",
    ]
    for module in modules:
        lines.append(f"    from ..types import {module.split('.', 1)[1]} as {_alias(module)}")
    for base_name, members in sorted(unions.items()):
        lines.append("")
        class_name = pascal_case(base_name.rpartition(".")[2])
        rendered = [f"{_alias(module_key(d))}.{d.class_name}" for d in members]
        if len(rendered) == 1:
            lines.append(f"    {class_name} = {rendered[0]}")
        else:
            lines.append(f"    {class_name} = (")
            lines.append(f"        {rendered[0]}")
            lines += [f"        | {name}" for name in rendered[1:]]
            lines.append("    )")
    return "\n".join(lines) + "\n"


def _alias(module: str) -> str:
    return module.replace(".", "_")


def emit_definitions_init(
    kind: str, grouped: dict[str, list[Definition]], layer: int
) -> str:
    namespaces = sorted(
        key.split(".", 1)[1]
        for key in grouped
        if key.startswith(f"{kind}.") and key.split(".", 1)[1] != ROOT
    )
    root = sorted(d.class_name for d in grouped.get(f"{kind}.{ROOT}", []))
    what = "functions" if kind == "functions" else "constructors"

    lines = header(layer)
    lines += [
        f'"""The generated TL {what}.',
        "",
        "A name in the root namespace is reachable straight from here, and a",
        "namespace is reachable as an attribute, so raw.types.Message and",
        "raw.types.messages.Messages both work. Either one imports only the",
        "module it needs.",
        "",
        "The mtproto attribute is not a TL namespace but the service schema,",
        "which is kept apart so that speaking the protocol does not mean loading",
        "the API.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from importlib import import_module",
        "from typing import TYPE_CHECKING, Any",
        "",
        "__all__ = [",
    ]
    lines += [f'    "{name}",' for name in namespaces + root]
    lines += ["]", "", "if TYPE_CHECKING:"]
    for namespace in namespaces:
        lines.append(f"    from . import {namespace} as {namespace}")
    for name in root:
        lines.append(f"    from .{ROOT} import {name} as {name}")
    lines += [
        "else:",
        f"    _NAMESPACES = frozenset({{{', '.join(repr(n) for n in namespaces)}}})",
        "    _EXPORTED = frozenset(__all__)",
        "",
        "    def __getattr__(name: str) -> Any:",
        "        if name in _NAMESPACES:",
        '            value: Any = import_module(f".{name}", __name__)',
        "        elif name in _EXPORTED:",
        f'            value = getattr(import_module(".{ROOT}", __name__), name)',
        "        else:",
        "            raise AttributeError(",
        '                f"module {__name__!r} has no attribute {name!r}"',
        "            )",
        "        globals()[name] = value",
        "        return value",
        "",
        "    def __dir__() -> list[str]:",
        "        # PEP 562 pairs __getattr__ with a __dir__. Without one, dir()",
        "        # and a REPL's tab completion see only what has already been",
        "        # imported, which on a fresh interpreter is nothing, and this",
        "        # is the layer docs/raw-api.md sends people to. Naming the",
        "        # names imports none of them, so rule P7 is untouched.",
        "        return sorted(set(globals()) | _EXPORTED | _NAMESPACES)",
    ]
    return "\n".join(lines) + "\n"


def emit_base_init(unions: dict[str, dict[str, list[Definition]]], layer: int) -> str:
    namespaces = sorted(
        key.split(".", 1)[1] for key in unions if key.split(".", 1)[1] != ROOT
    )
    root = sorted(
        pascal_case(name.rpartition(".")[2])
        for name in unions.get(f"base.{ROOT}", {})
    )
    lines = header(layer)
    lines += [
        '"""The abstract TL types, as aliases for type checkers.',
        "",
        "Nothing here exists at runtime; see the note in any of the modules.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import TYPE_CHECKING",
        "",
        "if TYPE_CHECKING:",
    ]
    for namespace in namespaces:
        lines.append(f"    from . import {namespace} as {namespace}")
    for name in root:
        lines.append(f"    from .{ROOT} import {name} as {name}")
    return "\n".join(lines) + "\n"


def emit_package_init(layer: int) -> str:
    lines = header(layer)
    lines += [
        '"""The generated wire layer, straight from the pinned TL schema.',
        "",
        "Split three ways: types holds the constructors a server can send,",
        "functions holds what a client can invoke, and base names the abstract",
        "types for annotations. Submodules load on demand, so importing this",
        "package costs nothing on its own.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from importlib import import_module",
        "from typing import TYPE_CHECKING, Any",
        "",
        '__all__ = ["LAYER", "base", "functions", "types"]',
        "",
        "# The schema layer these modules were generated from. The connection",
        "# announces it with invokeWithLayer, so it has to be readable at runtime",
        "# and not just recorded in a comment.",
        f"LAYER = {layer}",
        "",
        '_SUBMODULES = frozenset({"base", "functions", "types"})',
        "",
        "if TYPE_CHECKING:",
        "    from . import base as base",
        "    from . import functions as functions",
        "    from . import types as types",
        "else:",
        "",
        "    def __getattr__(name: str) -> Any:",
        "        if name not in _SUBMODULES:",
        "            raise AttributeError(",
        '                f"module {__name__!r} has no attribute {name!r}"',
        "            )",
        '        module = import_module(f".{name}", __name__)',
        "        globals()[name] = module",
        "        return module",
        "",
        "    def __dir__() -> list[str]:",
        "        return sorted(set(globals()) | _SUBMODULES)",
    ]
    return "\n".join(lines) + "\n"


def emit_all_module(definitions: list[Definition], layer: int) -> str:
    lines = header(layer)
    lines += [
        '"""Every constructor id, and where to find the class that reads it.',
        "",
        "This is what the codec's resolver consults. Keeping it as a plain table",
        "means an incoming object costs one import of one module, rather than",
        "having the whole schema in memory to decode a single update.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from importlib import import_module",
        "",
        "from ..tl import TLObject",
        "",
        "CONSTRUCTORS: dict[int, tuple[str, str]] = {",
    ]
    for definition in sorted(definitions, key=lambda d: d.id):
        module = module_key(definition)
        lines.append(f'    0x{definition.id:08X}: ("{module}", "{definition.class_name}"),')
    lines += [
        "}",
        "",
        "",
        "def find(constructor_id: int) -> type[TLObject] | None:",
        '    """The class for a constructor id, importing its module on the way."""',
        "    entry = CONSTRUCTORS.get(constructor_id)",
        "    if entry is None:",
        "        return None",
        "    module_name, class_name = entry",
        '    module = import_module(f".{module_name}", __package__)',
        "    found: type[TLObject] = getattr(module, class_name)",
        "    return found",
    ]
    return "\n".join(lines) + "\n"


def build() -> dict[str, str]:
    """The whole raw package as a mapping of relative path to file text.

    Kept separate from writing it out so the drift test can compare what the
    generator produces now against what is committed, without touching the tree.
    """
    layer = int(json.loads((SCHEMA_DIR / "version.json").read_text())["layer"])
    definitions = [
        corrected(d) for d in parse_all() if d.name not in overrides.EXCLUDED
    ]

    invented = sorted(d.name for d in definitions if d.declared_id is None)
    if invented:
        raise SystemExit(
            "these definitions declare no constructor id, so generating them would "
            f"mean inventing one: {invented}"
        )

    ctx = Context()
    grouped: dict[str, list[Definition]] = {}
    for definition in definitions:
        grouped.setdefault(module_key(definition), []).append(definition)
        ctx.constructors[definition.name] = (
            module_key(definition),
            definition.class_name,
        )

    unions: dict[str, dict[str, list[Definition]]] = {}
    for definition in definitions:
        if definition.is_function:
            continue
        result = definition.result
        if not isinstance(result, Reference):
            raise SystemExit(f"{definition.name} does not produce a named type")
        key = base_key(result.name)
        unions.setdefault(key, {}).setdefault(result.name, []).append(definition)
        ctx.bases[result.name] = (key, pascal_case(result.name.rpartition(".")[2]))

    files: dict[str, str] = {}
    for key, members in sorted(grouped.items()):
        kind, namespace = key.split(".", 1)
        files[f"{kind}/{namespace}.py"] = emit_definitions_module(
            key, members, ctx, layer
        )
    for key, base_unions in sorted(unions.items()):
        namespace = key.split(".", 1)[1]
        files[f"base/{namespace}.py"] = emit_base_module(key, base_unions, layer)

    files["types/__init__.py"] = emit_definitions_init("types", grouped, layer)
    files["functions/__init__.py"] = emit_definitions_init("functions", grouped, layer)
    files["base/__init__.py"] = emit_base_init(unions, layer)
    files["__init__.py"] = emit_package_init(layer)
    files["all.py"] = emit_all_module(definitions, layer)

    if ctx.renamed:
        print("renamed fields:", ctx.renamed)
    return files


def main() -> None:
    files = build()
    if RAW_DIR.name != "raw":
        raise SystemExit("refusing to clear a directory that is not raw/")
    shutil.rmtree(RAW_DIR, ignore_errors=True)
    for relative, text in files.items():
        path = RAW_DIR / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(files)} modules")


if __name__ == "__main__":
    main()
