# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Running a chat: who may do what, and what the chat itself looks like.

The awkwardness this module exists to absorb is that Telegram has two entirely
separate APIs for chats and applies them by chat type. A basic group is edited
through the messages namespace by a bare numeric id; a supergroup or channel is
edited through the channels namespace by an id and an access hash. They overlap
in what they can do and agree on almost none of the spelling, and a basic group
silently becomes a supergroup the first time someone does something a basic
group cannot.

So every function here takes a peer, works out which of the two it is looking
at, and says so plainly when the answer is that this cannot be done to that
kind of chat. Nothing is silently skipped.

Rights arrive as AdminRights and Permissions instead of as raw flags, because
the raw permission flags are inverted and getting that backwards is how a chat
ends up muted by accident. See types/rights.py for that.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from ..errors import SunnygramError
from ..network import Invoker
from ..peers import Target, as_channel, as_user, resolve
from ..raw import base, functions, types
from ..types.rights import AdminRights, Permissions

__all__ = [
    "add_chat_members",
    "approve_all_join_requests",
    "approve_join_request",
    "ban_member",
    "create_channel",
    "create_group",
    "delete_chat",
    "demote",
    "export_invite_link",
    "get_participant",
    "invite_links",
    "iter_admin_log",
    "kick_member",
    "promote",
    "restrict_member",
    "revoke_invite_link",
    "set_chat_description",
    "set_chat_permissions",
    "set_chat_photo",
    "set_chat_title",
    "set_slow_mode",
    "unban_member",
]

# What Telegram will answer with at once for the admin log, whatever is asked.
LOG_BATCH = 100

# How many messages a person added to a basic group can see behind them. Zero
# is the polite default: they see the conversation from where they joined.
FORWARD_LIMIT = 0


def _channel(where: base.InputPeer, doing: str) -> base.InputChannel:
    """The peer as a channel, or a refusal that says which call was wrong."""
    if isinstance(
        where, (types.InputPeerChannel, types.InputPeerChannelFromMessage)
    ):
        return as_channel(where)
    raise SunnygramError(
        f"{doing} is only possible in a supergroup or a channel, and this is a "
        f"{type(where).__name__}"
    )


async def promote(
    invoker: Invoker,
    peer: Target,
    user: Target,
    rights: AdminRights | None = None,
    *,
    title: str = "",
) -> Any:
    """Make someone an administrator, with the powers named and no others.

    Passing no rights promotes them to nothing, which is legal and is also how
    demote works. An account can only hand out powers it holds itself, so this
    fails on the ones it does not instead of quietly granting fewer.

    title is the custom rank shown next to their name. It is a supergroup
    feature and is ignored elsewhere.
    """
    where = await resolve(invoker, peer)
    who = await resolve(invoker, user)
    return await invoker.invoke(
        functions.channels.EditAdmin(
            channel=_channel(where, "promoting somebody"),
            user_id=as_user(who),
            admin_rights=(rights or AdminRights()).to_raw(),
            rank=title,
        )
    )


async def demote(invoker: Invoker, peer: Target, user: Target) -> Any:
    """Take every power back, leaving them an ordinary member."""
    return await promote(invoker, peer, user, AdminRights())


async def restrict_member(
    invoker: Invoker,
    peer: Target,
    user: Target,
    permissions: Permissions,
    *,
    until: int = 0,
) -> Any:
    """Limit what one person may do here, until a time or forever.

    until is a unix time, and zero means forever. Telegram treats anything less
    than thirty seconds or more than a year away as forever too, which is worth
    knowing before picking a short one.
    """
    where = await resolve(invoker, peer)
    who = await resolve(invoker, user)
    return await invoker.invoke(
        functions.channels.EditBanned(
            channel=_channel(where, "restricting somebody"),
            participant=who,
            banned_rights=permissions.to_raw(until=until),
        )
    )


async def ban_member(
    invoker: Invoker, peer: Target, user: Target, *, until: int = 0
) -> Any:
    """Remove someone and keep them out.

    A ban is the restriction with everything off, view_messages included, which
    is what makes it a ban, not a mute: they lose the chat instead of
    merely losing the ability to speak in it.
    """
    return await restrict_member(
        invoker, peer, user, Permissions.none(), until=until
    )


async def unban_member(invoker: Invoker, peer: Target, user: Target) -> Any:
    """Lift every restriction, so they may come back if they want to."""
    return await restrict_member(invoker, peer, user, Permissions.everything())


async def kick_member(invoker: Invoker, peer: Target, user: Target) -> Any:
    """Remove someone without keeping them out.

    Two calls, because Telegram has no third thing: a ban that is immediately
    lifted removes them and leaves them able to rejoin, which is what most
    people mean by kicking. A basic group has an actual call for it and takes
    that path instead.
    """
    where = await resolve(invoker, peer)
    who = await resolve(invoker, user)
    if isinstance(where, types.InputPeerChat):
        return await invoker.invoke(
            functions.messages.DeleteChatUser(
                chat_id=where.chat_id, user_id=as_user(who), revoke_history=False
            )
        )
    removed = await ban_member(invoker, where, who)
    await unban_member(invoker, where, who)
    return removed


async def get_participant(invoker: Invoker, peer: Target, user: Target) -> Any:
    """One person's standing here: member, admin, restricted or banned.

    Channels only, which is the half of this the protocol gives a call for. A
    basic group has no equivalent and goes through get_member instead.
    """
    where = await resolve(invoker, peer)
    who = await resolve(invoker, user)
    return await invoker.invoke(
        functions.channels.GetParticipant(
            channel=_channel(where, "asking about a participant"), participant=who
        )
    )


async def get_member(invoker: Invoker, peer: Target, user: Target) -> Any:
    """The raw standing of one person, in either kind of chat.

    A channel answers this directly. A basic group has no call for one member,
    so the whole membership is fetched and the one asked about is picked out of
    it. That is Telegram's shape instead of a choice here, and it is cheap for
    the only size a basic group is allowed to be.

    No one in the chat comes back as nothing, which is different from being
    refused: a channel says USER_NOT_PARTICIPANT and that stays an error.
    """
    where = await resolve(invoker, peer)
    if not isinstance(where, types.InputPeerChat):
        answer = await get_participant(invoker, where, user)
        return getattr(answer, "participant", None)

    who = await resolve(invoker, user)
    wanted = getattr(as_user(who), "user_id", 0)
    full = await invoker.invoke(functions.messages.GetFullChat(chat_id=where.chat_id))
    members = getattr(getattr(full, "full_chat", None), "participants", None)
    for participant in getattr(members, "participants", []) or []:
        if getattr(participant, "user_id", None) == wanted:
            return participant
    return None


async def set_chat_title(invoker: Invoker, peer: Target, title: str) -> Any:
    """Rename a chat, whichever kind it is."""
    where = await resolve(invoker, peer)
    if isinstance(where, types.InputPeerChat):
        return await invoker.invoke(
            functions.messages.EditChatTitle(chat_id=where.chat_id, title=title)
        )
    return await invoker.invoke(
        functions.channels.EditTitle(
            channel=_channel(where, "renaming a chat"), title=title
        )
    )


async def set_chat_photo(
    invoker: Invoker, peer: Target, photo: base.InputChatPhoto | None
) -> Any:
    """Change or remove a chat's picture.

    Passing nothing removes it, which the protocol spells as its own empty
    constructor instead of as an absent field.
    """
    chosen = photo if photo is not None else types.InputChatPhotoEmpty()
    where = await resolve(invoker, peer)
    if isinstance(where, types.InputPeerChat):
        return await invoker.invoke(
            functions.messages.EditChatPhoto(chat_id=where.chat_id, photo=chosen)
        )
    return await invoker.invoke(
        functions.channels.EditPhoto(
            channel=_channel(where, "changing a chat photo"), photo=chosen
        )
    )


async def set_chat_description(invoker: Invoker, peer: Target, about: str) -> Any:
    """Set the description, which is the one call that takes a plain peer."""
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.messages.EditChatAbout(peer=where, about=about)
    )


async def set_chat_permissions(
    invoker: Invoker, peer: Target, permissions: Permissions
) -> Any:
    """What everybody who is not an administrator may do here.

    The same shape as restricting one person, applied to the chat. Anyone
    already restricted keeps their own, since a personal restriction is
    stricter than the default by definition.
    """
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.messages.EditChatDefaultBannedRights(
            peer=where, banned_rights=permissions.to_raw()
        )
    )


async def set_slow_mode(invoker: Invoker, peer: Target, seconds: int) -> Any:
    """How long a member must wait between messages, or zero for no wait.

    Telegram only accepts certain values and rejects the rest, so this passes
    what it is given, not rounding: a silently changed limit is worse
    than an error saying which values exist.
    """
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.channels.ToggleSlowMode(
            channel=_channel(where, "setting slow mode"), seconds=seconds
        )
    )


async def create_group(
    invoker: Invoker, title: str, users: list[Target]
) -> Any:
    """Start a basic group with some people in it.

    Telegram will not make an empty one, which is why the members are not
    optional. A basic group turns into a supergroup by itself the first time
    someone needs something only a supergroup has.
    """
    members = [as_user(await resolve(invoker, user)) for user in users]
    return await invoker.invoke(
        functions.messages.CreateChat(users=members, title=title)
    )


async def create_channel(
    invoker: Invoker,
    title: str,
    *,
    about: str = "",
    megagroup: bool = False,
    forum: bool = False,
) -> Any:
    """Start a broadcast channel, or a supergroup if megagroup is asked for.

    The two are one constructor with a flag, which is Telegram's own design and
    is why a supergroup is created by a call named for channels.
    """
    return await invoker.invoke(
        functions.channels.CreateChannel(
            title=title,
            about=about,
            megagroup=megagroup or forum,
            broadcast=not (megagroup or forum),
            forum=forum,
        )
    )


async def delete_chat(invoker: Invoker, peer: Target) -> Any:
    """Delete a chat for everybody in it, which only its owner can do."""
    where = await resolve(invoker, peer)
    if isinstance(where, types.InputPeerChat):
        return await invoker.invoke(
            functions.messages.DeleteChat(chat_id=where.chat_id)
        )
    return await invoker.invoke(
        functions.channels.DeleteChannel(
            channel=_channel(where, "deleting a chat")
        )
    )


async def add_chat_members(
    invoker: Invoker,
    peer: Target,
    users: list[Target],
    *,
    forward_limit: int = FORWARD_LIMIT,
) -> Any:
    """Put people into a chat directly, instead of handing them a link.

    Whether this works at all is up to the person being added: most accounts
    only allow it from a contact, and the call fails per person instead of
    for the batch, which is why a supergroup answers with a list of who could
    not be added rather than an error.

    forward_limit is how much history a person joining a basic group can see
    behind them, and a supergroup ignores it because its history is not per
    member.
    """
    where = await resolve(invoker, peer)
    members = [as_user(await resolve(invoker, user)) for user in users]
    if isinstance(where, types.InputPeerChat):
        if len(members) != 1:
            raise SunnygramError(
                "a basic group takes one person at a time; call this once each"
            )
        return await invoker.invoke(
            functions.messages.AddChatUser(
                chat_id=where.chat_id, user_id=members[0], fwd_limit=forward_limit
            )
        )
    return await invoker.invoke(
        functions.channels.InviteToChannel(
            channel=_channel(where, "adding members"), users=members
        )
    )


async def export_invite_link(
    invoker: Invoker,
    peer: Target,
    *,
    title: str = "",
    expires: int = 0,
    usage_limit: int = 0,
    request_needed: bool = False,
) -> Any:
    """Make a new invite link, without touching the chat's primary one.

    expires is a unix time and usage_limit a count, both zero for no limit.
    request_needed makes the link ask instead of admit, so joining creates a
    request for an administrator to approve.

    A link that admits people and a link that has to be approved are different
    things to Telegram, and it refuses a usage limit on the second kind.
    """
    where = await resolve(invoker, peer)
    if request_needed and usage_limit:
        raise SunnygramError(
            "a link that has to be approved cannot also have a usage limit"
        )
    return await invoker.invoke(
        functions.messages.ExportChatInvite(
            peer=where,
            title=title or None,
            expire_date=expires or None,
            usage_limit=usage_limit or None,
            request_needed=request_needed,
        )
    )


async def revoke_invite_link(invoker: Invoker, peer: Target, link: str) -> Any:
    """Kill a link, so it admits no one else.

    Revoking the chat's primary link does not leave it without one: Telegram
    makes a replacement in the same breath, and it comes back in the answer.
    """
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.messages.EditExportedChatInvite(
            peer=where, link=link, revoked=True
        )
    )


async def invite_links(
    invoker: Invoker,
    peer: Target,
    *,
    admin: Target = "me",
    revoked: bool = False,
    limit: int = 100,
) -> Any:
    """The links one administrator has made here, live ones or revoked ones.

    Always by administrator, because that is how Telegram stores them: there is
    no call for every link in a chat, only for every link someone made.
    """
    where = await resolve(invoker, peer)
    who = await resolve(invoker, admin)
    return await invoker.invoke(
        functions.messages.GetExportedChatInvites(
            peer=where,
            admin_id=as_user(who),
            revoked=revoked,
            limit=limit,
        )
    )


async def approve_join_request(
    invoker: Invoker, peer: Target, user: Target, *, approved: bool = True
) -> Any:
    """Let someone in who asked, or turn them down."""
    where = await resolve(invoker, peer)
    who = await resolve(invoker, user)
    return await invoker.invoke(
        functions.messages.HideChatJoinRequest(
            peer=where, user_id=as_user(who), approved=approved
        )
    )


async def approve_all_join_requests(
    invoker: Invoker, peer: Target, *, approved: bool = True, link: str = ""
) -> Any:
    """Answer everybody waiting at once, instead of one at a time.

    One call for the whole queue, which is what a chat that has been away for a
    week needs: looping over the requests would be that many calls and the
    flood wait that comes with them. Naming a link narrows it to the people who
    used that one, which is how a chat lets in the ones who came from a
    campaign it trusts and leaves the rest waiting.
    """
    where = await resolve(invoker, peer)
    return await invoker.invoke(
        functions.messages.HideAllChatJoinRequests(
            peer=where, approved=approved, link=link or None
        )
    )


async def iter_admin_log(
    invoker: Invoker,
    peer: Target,
    *,
    limit: int = 100,
    query: str = "",
    batch: int = LOG_BATCH,
) -> AsyncIterator[Any]:
    """What administrators have done here, newest first, a page at a time.

    Paged backwards through an id rather than an offset, because entries are
    added while it is being read and an offset would show one twice or skip it.
    Telegram keeps these for a couple of days and no longer.
    """
    where = await resolve(invoker, peer)
    channel = _channel(where, "reading the admin log")
    max_id = 0
    seen = 0

    while seen < limit:
        page = await invoker.invoke(
            functions.channels.GetAdminLog(
                channel=channel,
                q=query,
                max_id=max_id,
                min_id=0,
                limit=min(batch, limit - seen),
            )
        )
        events = list(getattr(page, "events", ()) or ())
        if not events:
            return
        yield page
        seen += len(events)
        max_id = events[-1].id
