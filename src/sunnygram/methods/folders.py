# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Reading and changing the folders an account sorts its chats into.

Four calls, and one asymmetry worth knowing before using them: there is no
"create folder" and no "delete folder". updateDialogFilter does all three jobs,
telling them apart by whether a filter is given and whether the id is one that
already exists. So creating is saving under an unused id, and deleting is
saving nothing under a used one.
"""

from __future__ import annotations

from typing import Any

from ..network import Invoker
from ..peers import Target, resolve
from ..raw import base, functions, types

__all__ = [
    "build_folder",
    "delete_folder",
    "get_folders",
    "reorder_folders",
    "save_folder",
]


async def get_folders(invoker: Invoker) -> list[Any]:
    """Every folder this account has, in the order they are shown."""
    answer = await invoker.invoke(functions.messages.GetDialogFilters())
    if isinstance(answer, types.messages.DialogFilters):
        return list(answer.filters)
    return []


async def build_folder(
    invoker: Invoker,
    folder_id: int,
    title: str,
    *,
    include: list[Target] | None = None,
    exclude: list[Target] | None = None,
    pinned: list[Target] | None = None,
    contacts: bool = False,
    non_contacts: bool = False,
    groups: bool = False,
    broadcasts: bool = False,
    bots: bool = False,
    exclude_muted: bool = False,
    exclude_read: bool = False,
    exclude_archived: bool = False,
    emoticon: str | None = None,
) -> base.DialogFilter:
    """Assemble a folder, resolving every chat named in it.

    The peers are resolved here, not by the caller because a folder
    names a lot of them and each one is the same lookup a send would do.
    """

    async def peers(targets: list[Target] | None) -> list[base.InputPeer]:
        return [await resolve(invoker, one) for one in targets or []]

    return types.DialogFilter(
        id=folder_id,
        title=types.TextWithEntities(text=title, entities=[]),
        emoticon=emoticon,
        pinned_peers=await peers(pinned),
        include_peers=await peers(include),
        exclude_peers=await peers(exclude),
        contacts=contacts,
        non_contacts=non_contacts,
        groups=groups,
        broadcasts=broadcasts,
        bots=bots,
        exclude_muted=exclude_muted,
        exclude_read=exclude_read,
        exclude_archived=exclude_archived,
    )


async def save_folder(
    invoker: Invoker, folder_id: int, folder: base.DialogFilter
) -> bool:
    """Save a folder under an id, creating it if that id is free."""
    return bool(
        await invoker.invoke(
            functions.messages.UpdateDialogFilter(id=folder_id, filter=folder)
        )
    )


async def delete_folder(invoker: Invoker, folder_id: int) -> bool:
    """Remove a folder. The chats in it are not touched, only the rule."""
    return bool(
        await invoker.invoke(
            functions.messages.UpdateDialogFilter(id=folder_id, filter=None)
        )
    )


async def reorder_folders(invoker: Invoker, order: list[int]) -> bool:
    """Set the order the folders are shown in, by id."""
    return bool(
        await invoker.invoke(
            functions.messages.UpdateDialogFiltersOrder(order=list(order))
        )
    )
