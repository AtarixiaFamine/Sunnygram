# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Making and editing sticker sets, rather than sending what is in them.

Sending a sticker is in media.py and needs none of this. This is the other
side: a set that belongs to somebody, with stickers going in and out of it.

Two things shape the whole module. A set is named by a short name, not an id,
because the short name is what a t.me link carries and what every one of these
calls wants, so that is what the functions here take. And a sticker inside a
set is named by the document it is, not by a position, so removing one means
having the document in hand: read it off the set, or off a message carrying it.

Creating a set is the one call that names an owner, because a bot may make a
set on a person's behalf and the set belongs to the person either way.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from ..errors import SunnygramError
from ..network import Invoker
from ..peers import Target, as_user, resolve
from ..raw import functions, types

__all__ = [
    "StickerKind",
    "add_sticker",
    "create_sticker_set",
    "delete_sticker_set",
    "edit_sticker",
    "move_sticker",
    "remove_sticker",
    "rename_sticker_set",
    "replace_sticker",
    "set_sticker_set_thumb",
    "short_name_free",
    "sticker_item",
    "suggest_short_name",
    "upload_sticker",
]

# What a set holds. Telegram spells these as two independent flags rather than
# one choice, which reads as though a set could be both; it cannot.
StickerKind = Literal["regular", "mask", "emoji"]


def _set(short_name: str) -> types.InputStickerSetShortName:
    """A set named the way these calls want it."""
    return types.InputStickerSetShortName(short_name=short_name.strip().lstrip("@"))


def sticker_item(
    document: Any,
    emoji: str,
    *,
    keywords: Sequence[str] = (),
    mask_coords: Any = None,
) -> types.InputStickerSetItem:
    """One sticker on its way into a set: a file, and what it means.

    The emoji is not decoration. It is how the sticker is found when somebody
    types that emoji, so a set built with the same emoji on every sticker is a
    set nobody can search.
    """
    return types.InputStickerSetItem(
        document=document,
        emoji=emoji,
        keywords=",".join(keywords) if keywords else None,
        mask_coords=mask_coords,
    )


async def upload_sticker(
    invoker: Invoker,
    source: Any,
    emoji: str,
    *,
    keywords: Sequence[str] = (),
    mask_coords: Any = None,
    mime_type: str = "image/webp",
    **upload: Any,
) -> types.InputStickerSetItem:
    """Take a file off disk and turn it into a sticker ready to go in a set.

    The step in the middle is the one worth wrapping. A set is built out of
    documents, and an upload is not a document yet: it has to be registered
    with the server first, which is a second call whose answer carries the id
    and the access hash the set actually wants. Saved Messages is where it is
    registered, which costs nothing and sends nobody anything.

    The default mime type is webp because that is what a still sticker is.
    Pass "video/webm" for an animated one, or "application/x-tgsticker" for a
    Lottie.
    """
    from ..files import upload_file
    from .albums import register_media

    handle = await upload_file(invoker, source, **upload)
    registered = await register_media(
        invoker,
        "me",
        types.InputMediaUploadedDocument(
            file=handle, mime_type=mime_type, attributes=[]
        ),
    )
    document = getattr(registered, "id", None)
    if not isinstance(document, types.InputDocument):
        raise SunnygramError(
            "the server took the upload and did not answer with a document, "
            "so there is nothing a sticker set could be built from"
        )
    return sticker_item(
        document, emoji, keywords=keywords, mask_coords=mask_coords
    )


async def create_sticker_set(
    invoker: Invoker,
    owner: Target,
    *,
    title: str,
    short_name: str,
    stickers: Sequence[types.InputStickerSetItem],
    kind: StickerKind = "regular",
    thumb: Any = None,
    software: str | None = None,
) -> Any:
    """Make a new set, owned by somebody, with its first stickers in it.

    A set cannot be created empty, which is why the stickers are not optional.
    short_name is what the t.me link will carry and has to be free; ask
    short_name_free first, or let suggest_short_name pick one.
    """
    if not stickers:
        raise ValueError("a sticker set cannot be created empty")
    return await invoker.invoke(
        functions.stickers.CreateStickerSet(
            user_id=as_user(await resolve(invoker, owner)),
            title=title,
            short_name=short_name.strip().lstrip("@"),
            stickers=list(stickers),
            masks=kind == "mask",
            emojis=kind == "emoji",
            thumb=thumb,
            software=software,
        )
    )


async def add_sticker(
    invoker: Invoker, short_name: str, sticker: types.InputStickerSetItem
) -> Any:
    """Put one more sticker at the end of a set."""
    return await invoker.invoke(
        functions.stickers.AddStickerToSet(
            stickerset=_set(short_name), sticker=sticker
        )
    )


async def remove_sticker(invoker: Invoker, sticker: Any) -> Any:
    """Take a sticker out of whichever set it is in.

    Named by the document rather than by a set and a position, which is why no
    set is passed: the document already says which set it belongs to.
    """
    return await invoker.invoke(
        functions.stickers.RemoveStickerFromSet(sticker=sticker)
    )


async def move_sticker(invoker: Invoker, sticker: Any, position: int) -> Any:
    """Move a sticker to a place in its set, counting from zero."""
    return await invoker.invoke(
        functions.stickers.ChangeStickerPosition(sticker=sticker, position=position)
    )


async def edit_sticker(
    invoker: Invoker,
    sticker: Any,
    *,
    emoji: str | None = None,
    keywords: Sequence[str] | None = None,
    mask_coords: Any = None,
) -> Any:
    """Change what a sticker already in a set is found by.

    What is left out is left alone.
    """
    return await invoker.invoke(
        functions.stickers.ChangeSticker(
            sticker=sticker,
            emoji=emoji,
            keywords=",".join(keywords) if keywords is not None else None,
            mask_coords=mask_coords,
        )
    )


async def replace_sticker(
    invoker: Invoker, sticker: Any, replacement: types.InputStickerSetItem
) -> Any:
    """Swap one sticker for another, keeping its place in the set."""
    return await invoker.invoke(
        functions.stickers.ReplaceSticker(sticker=sticker, new_sticker=replacement)
    )


async def rename_sticker_set(invoker: Invoker, short_name: str, title: str) -> Any:
    """Change a set's title. The short name, and so the link, stays."""
    return await invoker.invoke(
        functions.stickers.RenameStickerSet(stickerset=_set(short_name), title=title)
    )


async def delete_sticker_set(invoker: Invoker, short_name: str) -> Any:
    """Delete a whole set. Not undoable, and the short name is not freed."""
    return await invoker.invoke(
        functions.stickers.DeleteStickerSet(stickerset=_set(short_name))
    )


async def set_sticker_set_thumb(
    invoker: Invoker,
    short_name: str,
    *,
    thumb: Any = None,
    document_id: int | None = None,
) -> Any:
    """Choose the picture a set is shown by.

    Either a file of your own, or the id of a sticker already in the set to
    stand for the rest of it. Neither one clears it back to the default.
    """
    return await invoker.invoke(
        functions.stickers.SetStickerSetThumb(
            stickerset=_set(short_name), thumb=thumb, thumb_document_id=document_id
        )
    )


async def suggest_short_name(invoker: Invoker, title: str) -> Any:
    """Ask the server for a free short name that suits this title."""
    return await invoker.invoke(functions.stickers.SuggestShortName(title=title))


async def short_name_free(invoker: Invoker, short_name: str) -> bool:
    """Whether a short name can still be taken.

    Answered as a plain yes or no, which is what the server means by it, rather
    than as the bare true the schema declares.
    """
    answer = await invoker.invoke(
        functions.stickers.CheckShortName(
            short_name=short_name.strip().lstrip("@")
        )
    )
    return bool(answer)
