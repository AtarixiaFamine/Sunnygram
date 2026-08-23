# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Message identifiers.

A message id is a timestamp: the unix time in the high 32 bits and a fraction
of a second in the low 32. That makes it both an identifier and a rough clock,
which is why the protocol can use it to spot stale and replayed messages.

The low two bits carry the direction. Ours are always divisible by four; the
server answers with an id that is 1 modulo 4 when replying to something we sent
and 3 modulo 4 otherwise. So an id also says who minted it, and a message
claiming the wrong parity is not one we should be reading.

Ids have to increase within a session, and a clock that steps backwards must
not be able to break that, so the generator never returns anything it has
already handed out.
"""

from __future__ import annotations

import time

__all__ = ["MessageIdGenerator", "is_server_id", "msg_id_time"]


def msg_id_time(msg_id: int) -> float:
    """The unix time a message id encodes."""
    return msg_id / (1 << 32)


def is_server_id(msg_id: int) -> bool:
    """Whether this id was minted by the server, not by us."""
    return msg_id % 4 in (1, 3)


class MessageIdGenerator:
    """A source of increasing client message ids for one session."""

    __slots__ = ("time_offset", "_last")

    def __init__(self, time_offset: float = 0.0) -> None:
        # How far the server's clock is ahead of ours, learned during the
        # handshake. Left at zero the local clock is used as it is.
        self.time_offset = time_offset
        self._last = 0

    def adopt(self, offset: float) -> None:
        """Take a new offset because the server refused the ids we were minting.

        Ids normally never step back, which keeps a local clock jumping
        around from handing out the same one twice. But a server answering
        bad_msg_notification 17 is saying our ids run ahead of what it will
        accept, and the only way to obey is to let them come down again. So the
        floor is cleared here and nowhere else, and only for ids the server has
        already refused.
        """
        if offset != self.time_offset:
            self.time_offset = offset
            self._last = 0

    def next(self) -> int:
        """The next id: divisible by four, and larger than the last one."""
        now = time.time() + self.time_offset
        seconds = int(now)
        fraction = int((now - seconds) * (1 << 32))
        # Clearing the low two bits is what marks the id as ours.
        candidate = (seconds << 32) | (fraction & ~3)
        if candidate <= self._last:
            candidate = self._last + 4
        self._last = candidate
        return candidate
