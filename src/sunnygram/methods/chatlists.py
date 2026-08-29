# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Sharing a folder, which is a folder that other people can join.

An ordinary folder is a private arrangement of your own dialogs, and is in
folders.py. This is the other half: a folder given a link, so that opening the
link adds somebody to every chat in it at once.

The two are the same object underneath, named here by the folder's id, which is
what a Folder carries. What makes a shared one different is that it goes on
being shared: chats added to it later are an update the people who joined can
take or ignore, which is what the updates calls below are for. Only public
chats and chats you can invite to can go in one, and the server says which by
refusing the rest rather than by dropping them quietly.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from ..network import Invoker
from ..peers import Target, resolve
from ..raw import functions, types

__all__ = [
    "delete_folder_link",
    "edit_folder_link",
    "folder_link_preview",
    "folder_links",
    "folder_updates",
    "hide_folder_updates",
    "join_folder_link",
    "join_folder_updates",
    "leave_folder",
    "leave_suggestions",
    "export_folder_link",
]


def _folder(folder_id: int) -> types.InputChatlistDialogFilter:
    """A folder named the way these calls want it, which is by its id."""
    return types.InputChatlistDialogFilter(filter_id=folder_id)


async def _peers(invoker: Invoker, peers: Sequence[Target]) -> list[Any]:
    return [await resolve(invoker, peer) for peer in peers]


async def export_folder_link(
    invoker: Invoker, folder_id: int, *, title: str = "", peers: Sequence[Target]
) -> Any:
    """Give a folder a link, naming which of its chats the link carries.

    Not every chat in a folder can be shared, so the ones that go in the link
    are named here rather than taken from the folder. Asking for one the server
    will not share is refused, which is the honest answer: a link that quietly
    carried fewer chats than asked for would be worse.
    """
    return await invoker.invoke(
        functions.chatlists.ExportChatlistInvite(
            chatlist=_folder(folder_id),
            title=title,
            peers=await _peers(invoker, peers),
        )
    )


async def folder_links(invoker: Invoker, folder_id: int) -> Any:
    """Every link this folder has been given."""
    return await invoker.invoke(
        functions.chatlists.GetExportedInvites(chatlist=_folder(folder_id))
    )


async def edit_folder_link(
    invoker: Invoker,
    folder_id: int,
    slug: str,
    *,
    title: str | None = None,
    peers: Sequence[Target] | None = None,
) -> Any:
    """Change a link's title, or which chats it carries.

    What is left out is left alone, so passing only a title keeps the chats.
    """
    return await invoker.invoke(
        functions.chatlists.EditExportedInvite(
            chatlist=_folder(folder_id),
            slug=slug,
            title=title,
            peers=await _peers(invoker, peers) if peers is not None else None,
        )
    )


async def delete_folder_link(invoker: Invoker, folder_id: int, slug: str) -> Any:
    """Take a link back. The people who already joined stay where they are."""
    return await invoker.invoke(
        functions.chatlists.DeleteExportedInvite(
            chatlist=_folder(folder_id), slug=slug
        )
    )


async def folder_link_preview(invoker: Invoker, slug: str) -> Any:
    """What is behind somebody else's folder link, without joining it.

    Answers with the folder's name and the chats in it, marking which ones this
    account is already in, which is what a client shows before asking.
    """
    return await invoker.invoke(functions.chatlists.CheckChatlistInvite(slug=slug))


async def join_folder_link(
    invoker: Invoker, slug: str, *, peers: Sequence[Target]
) -> Any:
    """Join a shared folder, taking the chats named and no others.

    The chats are named rather than implied because joining is the point: a
    link with twenty chats behind it should not put an account in twenty chats
    without being asked which.
    """
    return await invoker.invoke(
        functions.chatlists.JoinChatlistInvite(
            slug=slug, peers=await _peers(invoker, peers)
        )
    )


async def folder_updates(invoker: Invoker, folder_id: int) -> Any:
    """Chats added to a shared folder since this account joined it."""
    return await invoker.invoke(
        functions.chatlists.GetChatlistUpdates(chatlist=_folder(folder_id))
    )


async def join_folder_updates(
    invoker: Invoker, folder_id: int, *, peers: Sequence[Target]
) -> Any:
    """Take the chats a shared folder has gained, or the ones named of them."""
    return await invoker.invoke(
        functions.chatlists.JoinChatlistUpdates(
            chatlist=_folder(folder_id), peers=await _peers(invoker, peers)
        )
    )


async def hide_folder_updates(invoker: Invoker, folder_id: int) -> Any:
    """Decline what a shared folder has gained, without leaving it."""
    return await invoker.invoke(
        functions.chatlists.HideChatlistUpdates(chatlist=_folder(folder_id))
    )


async def leave_suggestions(invoker: Invoker, folder_id: int) -> Any:
    """Which chats leaving this folder could reasonably take with it.

    Telegram's own suggestion, and a suggestion is all it is: the chats a
    person joined through the folder and is in for no other reason.
    """
    return await invoker.invoke(
        functions.chatlists.GetLeaveChatlistSuggestions(chatlist=_folder(folder_id))
    )


async def leave_folder(
    invoker: Invoker, folder_id: int, *, peers: Sequence[Target] = ()
) -> Any:
    """Leave a shared folder, and the chats named with it.

    Naming none leaves the folder and stays in every chat, which is the safe
    default: leaving chats is the part that cannot be undone quietly.
    """
    return await invoker.invoke(
        functions.chatlists.LeaveChatlist(
            chatlist=_folder(folder_id), peers=await _peers(invoker, peers)
        )
    )
