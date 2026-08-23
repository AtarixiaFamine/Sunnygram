# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""A poll, and someone voting in one.

Two updates and they arrive for different reasons. The poll update says the
standing changed, which a program watching its own poll wants; the vote
update says one named person picked one named answer, and only a public poll
produces it, because an anonymous poll is precisely the promise not to say that.

The poll update has a shape worth knowing about before it surprises someone:
the question and the answers are optional and usually absent. Telegram sends
them when the poll itself changed, which is once, and sends only the results
every other time. So a poll that arrives with no question is the normal case
, not a fault, and known says which kind arrived. The results are named
by position, matching the way a poll is sent and voted in everywhere else here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..errors import SunnygramError
from ..peers import mark_peer
from ..raw import types

if TYPE_CHECKING:
    from ..client import Client

__all__ = ["Poll", "PollAnswer", "PollVote"]


@dataclass(frozen=True, slots=True)
class PollAnswer:
    """One of the things a poll offers, and how it is doing."""

    position: int
    text: str = ""
    option: bytes = b""
    voters: int = 0
    correct: bool = False
    chosen: bool = False

    def __repr__(self) -> str:
        return f"PollAnswer({self.position}: {self.text!r}, {self.voters} votes)"


@dataclass(slots=True)
class Poll:
    """A poll as it stands, as far as this update says."""

    id: int
    question: str = ""
    answers: tuple[PollAnswer, ...] = ()
    total_voters: int = 0
    closed: bool = False
    quiz: bool = False
    multiple: bool = False
    anonymous: bool = True
    solution: str = ""
    chat_id: int = 0
    message_id: int = 0
    topic_id: int = 0
    raw: Any = None
    client: Any = None

    def __repr__(self) -> str:
        return (
            f"Poll({self.id}, {self.question!r}, "
            f"{self.total_voters} voters{', closed' if self.closed else ''})"
        )

    @property
    def known(self) -> bool:
        """Whether this update carried the poll itself or only its results.

        Telegram sends the question and the answers when the poll changed and
        the results alone the rest of the time, so a program that wants to draw
        the whole poll from an update either keeps the first one it saw or asks
        for it with get_poll.
        """
        return bool(self.question)

    @property
    def located(self) -> bool:
        """Whether this update said which message the poll is in.

        It usually does not. The poll id is what Telegram considers the name of
        a poll, and the message is only mentioned when the update happens to
        have it, so anything acting on the message has to be told where it is.
        """
        return bool(self.chat_id and self.message_id)

    @property
    def winner(self) -> PollAnswer | None:
        """The answer with the most votes, or nothing if the poll is tied.

        Nothing instead of an arbitrary one: a tie is a real outcome and
        picking a side of it silently is the kind of thing that is found out
        much later.
        """
        if not self.answers:
            return None
        ranked = sorted(self.answers, key=lambda one: one.voters, reverse=True)
        if len(ranked) > 1 and ranked[0].voters == ranked[1].voters:
            return None
        return ranked[0]

    @property
    def correct(self) -> PollAnswer | None:
        """The right answer, for a quiz that has said which it is."""
        for answer in self.answers:
            if answer.correct:
                return answer
        return None

    async def close(self) -> None:
        """Stop the poll taking votes, which cannot be undone."""
        # Where it is comes first, because a poll update that did not say is
        # the usual case and is the more useful thing to be told about.
        chat_id, message_id = self._where()
        await self._acting().close_poll(chat_id, message_id)

    async def vote(self, *positions: int) -> Any:
        """Answer the poll by position, or with nothing to take a vote back."""
        chat_id, message_id = self._where()
        return await self._acting().vote(chat_id, message_id, *positions)

    async def refresh(self) -> Any:
        """Ask for the poll's standing instead of waiting to be told."""
        chat_id, message_id = self._where()
        return await self._acting().get_poll(chat_id, message_id)

    def _where(self) -> tuple[int, int]:
        if not self.located:
            raise SunnygramError(
                "this poll update did not say which message the poll is in, "
                "which is the usual case. Keep the message id from when the "
                "poll was sent, or act on the poll id instead"
            )
        return self.chat_id, self.message_id

    def _acting(self) -> Client:
        if self.client is None:
            raise SunnygramError(
                "this poll is not bound to a client, so it cannot act on its own"
            )
        client: Client = self.client
        return client

    @classmethod
    def from_raw(cls, update: Any, *, client: Any = None) -> Poll | None:
        """Wrap a poll update, with or without the poll itself in it."""
        if not isinstance(update, types.UpdateMessagePoll):
            return None
        poll = update.poll
        results = update.results
        return cls(
            id=update.poll_id,
            question=_text_of(getattr(poll, "question", None)),
            answers=_answers(poll, results),
            total_voters=results.total_voters or 0,
            closed=bool(getattr(poll, "closed", False)),
            quiz=bool(getattr(poll, "quiz", False)),
            multiple=bool(getattr(poll, "multiple_choice", False)),
            anonymous=not getattr(poll, "public_voters", False),
            solution=results.solution or "",
            chat_id=mark_peer(update.peer) or 0,
            message_id=update.msg_id or 0,
            topic_id=update.top_msg_id or 0,
            raw=update,
            client=client,
        )


@dataclass(frozen=True, slots=True)
class PollVote:
    """One person's vote in one poll.

    Only a public poll produces this. The answers are positions, which is how
    they are counted from when the poll is sent, so a program reads
    options[0] as an index into the answers it wrote.
    """

    poll_id: int
    voter_id: int
    options: tuple[int, ...] = ()
    raw: Any = None

    def __repr__(self) -> str:
        return f"PollVote({self.voter_id} voted {list(self.options)} in {self.poll_id})"

    @property
    def retracted(self) -> bool:
        """Whether this is someone taking their vote back, not casting one."""
        return not self.options

    @classmethod
    def from_raw(cls, update: Any) -> PollVote | None:
        """Wrap a vote off the wire."""
        if not isinstance(update, types.UpdateMessagePollVote):
            return None
        return cls(
            poll_id=update.poll_id,
            voter_id=mark_peer(update.peer) or 0,
            options=_positions(update),
            raw=update,
        )


def _positions(update: types.UpdateMessagePollVote) -> tuple[int, ...]:
    """Which answers were picked, as positions.

    The schema gives both spellings: the option bytes that went over the wire
    and the positions they stand for. The positions are read when they are
    there, and the bytes are read as what they are otherwise, since an option
    is one byte holding the answer's place in the list.
    """
    if update.positions:
        return tuple(update.positions)
    return tuple(one[0] for one in update.options if one)


def _answers(poll: Any, results: Any) -> tuple[PollAnswer, ...]:
    """The answers with their votes, matched up by the option bytes.

    Either half can be missing. A poll with no results yet has answers and no
    votes; an update carrying only results has votes and no text, and both are
    worth handing back instead of refusing.
    """
    voted: dict[bytes, Any] = {
        one.option: one for one in (getattr(results, "results", None) or [])
    }
    written = getattr(poll, "answers", None) or []

    if written:
        return tuple(
            PollAnswer(
                position=index,
                text=_text_of(answer.text),
                option=answer.option,
                voters=getattr(voted.get(answer.option), "voters", 0) or 0,
                correct=bool(getattr(voted.get(answer.option), "correct", False)),
                chosen=bool(getattr(voted.get(answer.option), "chosen", False)),
            )
            for index, answer in enumerate(written)
        )

    return tuple(
        PollAnswer(
            position=one.option[0] if one.option else index,
            option=one.option,
            voters=one.voters or 0,
            correct=bool(one.correct),
            chosen=bool(one.chosen),
        )
        for index, one in enumerate(voted.values())
    )


def _text_of(written: Any) -> str:
    """The words out of a TextWithEntities, or nothing when there are none."""
    found = getattr(written, "text", None)
    return found if isinstance(found, str) else ""
