# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""The small events: records with nothing to do.

Five things a program can be told about that need no methods, because there is
nothing to do about them beyond knowing. Messages were deleted; someone came
online; someone is typing; someone blocked us; someone stopped a bot. They
share a file rather than having five of thirty lines each, since they are the
same kind of thing and would only ever change together.

The one that surprises people is deletion. Telegram says which messages were
deleted and, outside a channel, does not say where: the ids come from the
account's own numbering across every private chat and small group, so chat_id
is nothing at all instead of a guess. A program that has to know which chat a
deleted message was in has to have written that down when it arrived, which is
what the message cache is for.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..peers import mark_id, mark_peer
from ..raw import types
from ..storage import PeerKind

__all__ = ["Blocked", "DeletedMessages", "Status", "Stopped", "Typing"]

# What someone is doing, in the words a program would use. Telegram spells
# each as its own constructor, and the useful form is a word, since a handler
# almost always either shows it or ignores it.
_DOING: dict[type, str] = {
    types.SendMessageTypingAction: "typing",
    types.SendMessageCancelAction: "stopped",
    types.SendMessageRecordVideoAction: "record_video",
    types.SendMessageUploadVideoAction: "upload_video",
    types.SendMessageRecordAudioAction: "record_audio",
    types.SendMessageUploadAudioAction: "upload_audio",
    types.SendMessageUploadPhotoAction: "upload_photo",
    types.SendMessageUploadDocumentAction: "upload_document",
    types.SendMessageGeoLocationAction: "choose_location",
    types.SendMessageChooseContactAction: "choose_contact",
    types.SendMessageGamePlayAction: "play_game",
    types.SendMessageRecordRoundAction: "record_round",
    types.SendMessageUploadRoundAction: "upload_round",
    types.SpeakingInGroupCallAction: "speaking",
    types.SendMessageHistoryImportAction: "import_history",
    types.SendMessageChooseStickerAction: "choose_sticker",
    types.SendMessageEmojiInteraction: "emoji",
    types.SendMessageEmojiInteractionSeen: "emoji_seen",
}

# How recently someone was here, in the five degrees Telegram allows an
# account to be seen at. The vaguer three are a privacy setting instead of a
# measurement, which is why they carry no time.
_SEEN: dict[type, str] = {
    types.UserStatusOnline: "online",
    types.UserStatusOffline: "offline",
    types.UserStatusRecently: "recently",
    types.UserStatusLastWeek: "last_week",
    types.UserStatusLastMonth: "last_month",
    types.UserStatusEmpty: "unknown",
}


@dataclass(frozen=True, slots=True)
class DeletedMessages:
    """Messages that are gone, and where they were if that was said."""

    ids: tuple[int, ...]
    chat_id: int = 0
    raw: Any = None

    def __repr__(self) -> str:
        where = f" in {self.chat_id}" if self.chat_id else ""
        return f"DeletedMessages({len(self.ids)}{where})"

    @property
    def located(self) -> bool:
        """Whether Telegram said which chat these were deleted from.

        Only a channel says so. Everywhere else the ids belong to the account's
        own numbering across all of its private chats and small groups, and no
        chat is named, so this is False and chat_id is zero, not a
        plausible wrong answer.
        """
        return bool(self.chat_id)

    @classmethod
    def from_raw(cls, update: Any) -> DeletedMessages | None:
        """Wrap either of the two deletion updates."""
        if isinstance(update, types.UpdateDeleteChannelMessages):
            return cls(
                ids=tuple(update.messages),
                chat_id=mark_id(update.channel_id, PeerKind.CHANNEL),
                raw=update,
            )
        if isinstance(update, types.UpdateDeleteMessages):
            return cls(ids=tuple(update.messages), raw=update)
        return None


@dataclass(frozen=True, slots=True)
class Status:
    """Someone being online, or having been, as far as they let us see."""

    user_id: int
    status: str = "unknown"
    expires: int = 0
    last_seen: int = 0
    raw: Any = None

    def __repr__(self) -> str:
        return f"Status({self.user_id} {self.status})"

    @property
    def online(self) -> bool:
        """Whether they are here right now."""
        return self.status == "online"

    @classmethod
    def from_raw(cls, update: Any) -> Status | None:
        """Wrap a status change off the wire."""
        if not isinstance(update, types.UpdateUserStatus):
            return None
        standing = update.status
        return cls(
            user_id=update.user_id,
            status=_SEEN.get(type(standing), "unknown"),
            expires=getattr(standing, "expires", 0) or 0,
            last_seen=getattr(standing, "was_online", 0) or 0,
            raw=update,
        )


@dataclass(frozen=True, slots=True)
class Typing:
    """Someone doing something in a chat that is worth showing.

    Typing is one of eighteen of these and the rest are just as real: recording
    a voice note, uploading a video, picking a sticker. They are all one event
    with a word for which, since a program either shows what someone is doing
    or ignores all of it.
    """

    chat_id: int
    user_id: int
    doing: str = "typing"
    topic_id: int = 0
    progress: int = 0
    raw: Any = None

    def __repr__(self) -> str:
        return f"Typing({self.user_id} {self.doing} in {self.chat_id})"

    @classmethod
    def from_raw(cls, update: Any) -> Typing | None:
        """Wrap any of the three updates that say someone is doing something."""
        if isinstance(update, types.UpdateUserTyping):
            # A private chat, where the person and the chat are the same peer.
            chat_id = user_id = mark_id(update.user_id, PeerKind.USER)
            topic = update.top_msg_id or 0
        elif isinstance(update, types.UpdateChatUserTyping):
            chat_id = mark_id(update.chat_id, PeerKind.CHAT)
            user_id = mark_peer(update.from_id) or 0
            topic = 0
        elif isinstance(update, types.UpdateChannelUserTyping):
            chat_id = mark_id(update.channel_id, PeerKind.CHANNEL)
            user_id = mark_peer(update.from_id) or 0
            topic = update.top_msg_id or 0
        else:
            return None

        action = update.action
        return cls(
            chat_id=chat_id,
            user_id=user_id,
            doing=_DOING.get(type(action), "typing"),
            topic_id=topic,
            progress=getattr(action, "progress", 0) or 0,
            raw=update,
        )


@dataclass(frozen=True, slots=True)
class Blocked:
    """Someone blocking this account, or unblocking it."""

    user_id: int
    blocked: bool = True
    stories_only: bool = False
    raw: Any = None

    def __repr__(self) -> str:
        return f"Blocked({self.user_id}, {'blocked' if self.blocked else 'unblocked'})"

    @classmethod
    def from_raw(cls, update: Any) -> Blocked | None:
        """Wrap a block off the wire."""
        if not isinstance(update, types.UpdatePeerBlocked):
            return None
        return cls(
            user_id=mark_peer(update.peer_id) or 0,
            blocked=bool(update.blocked),
            stories_only=bool(update.blocked_my_stories_from),
            raw=update,
        )


@dataclass(frozen=True, slots=True)
class Stopped:
    """Someone stopping a bot, or starting it again after having stopped it.

    The bot side of being blocked, and the one number every bot should watch:
    it is the difference between a quiet audience and one that has left.
    """

    user_id: int
    stopped: bool = True
    date: int = 0
    raw: Any = None

    def __repr__(self) -> str:
        return f"Stopped({self.user_id}, {'stopped' if self.stopped else 'restarted'})"

    @classmethod
    def from_raw(cls, update: Any) -> Stopped | None:
        """Wrap a bot being stopped off the wire."""
        if not isinstance(update, types.UpdateBotStopped):
            return None
        return cls(
            user_id=mark_id(update.user_id, PeerKind.USER),
            stopped=bool(update.stopped),
            date=update.date,
            raw=update,
        )
