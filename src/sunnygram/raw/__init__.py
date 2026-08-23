# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""The generated wire layer, straight from the pinned TL schema.

Split three ways: types holds the constructors a server can send,
functions holds what a client can invoke, and base names the abstract
types for annotations. Submodules load on demand, so importing this
package costs nothing on its own.
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

__all__ = ["LAYER", "base", "functions", "types"]

# The schema layer these modules were generated from. The connection
# announces it with invokeWithLayer, so it has to be readable at runtime
# and not just recorded in a comment.
LAYER = 228

_SUBMODULES = frozenset({"base", "functions", "types"})

if TYPE_CHECKING:
    from . import base as base
    from . import functions as functions
    from . import types as types
else:

    def __getattr__(name: str) -> Any:
        if name not in _SUBMODULES:
            raise AttributeError(
                f"module {__name__!r} has no attribute {name!r}"
            )
        module = import_module(f".{name}", __name__)
        globals()[name] = module
        return module

    def __dir__() -> list[str]:
        return sorted(set(globals()) | _SUBMODULES)
