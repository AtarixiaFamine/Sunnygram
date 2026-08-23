# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""A session small enough to carry in an environment variable.

Everything a login produces, packed into 267 bytes and spelled in base64: the
datacenter, who you are, and the key. That is enough to start a client without
a file anywhere, which makes it the right shape for a container, a CI
secret, or moving a session between machines.

The first byte is a version. The format will grow, and a session written by a
later version has to fail loudly instead of be misread, since misreading it
means presenting a key as if it were something else.

What does not travel is the update state. A pts per channel is unbounded, and a
credential a person pastes has to stay one line, so a session restored from a
string starts by asking the server where the stream is. That costs one call and
means recent updates arrive as a difference rather than as they happened, which
is the right trade for something built to be portable. Use the sqlite backend
where picking up exactly where you left off matters.

It is a bearer credential in the most literal sense: whoever holds the string is
the account, with no code and no password. Treat it exactly as you would treat a
password, and never let one reach a log (rule S2, which is why nothing here has
a repr that includes it).
"""

from __future__ import annotations

import struct
from base64 import urlsafe_b64decode, urlsafe_b64encode

from ..crypto import AUTH_KEY_SIZE
from .base import SessionState
from .memory import MemoryStorage

__all__ = ["StringStorage", "decode_session", "encode_session"]

# version, dc_id, flags, user_id. The key follows, unprefixed, since its size is
# fixed by the protocol.
_HEADER = struct.Struct("<BBBq")
VERSION = 1
_SIZE = _HEADER.size + AUTH_KEY_SIZE

_TEST_MODE = 1 << 0
_IS_BOT = 1 << 1


def encode_session(state: SessionState) -> str:
    """Spell a session as a string.

    Only the key for the home datacenter travels. Keys for the others are worth
    keeping in a file, where re-negotiating one costs nothing, but not worth
    tripling the length of something a person has to paste.
    """
    key = state.auth_key()
    if key is None:
        raise ValueError(
            f"this session has no key for DC {state.dc_id}, so there is "
            "nothing to export yet"
        )
    flags = (_TEST_MODE if state.test_mode else 0) | (_IS_BOT if state.is_bot else 0)
    packed = _HEADER.pack(VERSION, state.dc_id, flags, state.user_id) + key
    # 267 bytes divides by three, so this comes out with no padding to strip.
    return urlsafe_b64encode(packed).decode()


def decode_session(text: str) -> SessionState:
    """Read a session back from a string, refusing anything that is not one."""
    try:
        packed = urlsafe_b64decode(text.strip() + "=" * (-len(text.strip()) % 4))
    except (ValueError, TypeError) as exc:
        raise ValueError("this is not a valid session string") from exc
    if len(packed) != _SIZE:
        raise ValueError(
            f"a session string holds {_SIZE} bytes, this one holds {len(packed)}"
        )

    version, dc_id, flags, user_id = _HEADER.unpack_from(packed)
    if version != VERSION:
        raise ValueError(
            f"this session string is version {version} and this build reads "
            f"version {VERSION}"
        )
    state = SessionState(
        dc_id=dc_id,
        test_mode=bool(flags & _TEST_MODE),
        user_id=user_id,
        is_bot=bool(flags & _IS_BOT),
    )
    state.set_auth_key(dc_id, packed[_HEADER.size :])
    return state


class StringStorage(MemoryStorage):
    """A session that came from a string, and can go back to being one.

    Built on the memory backend because that is what it is: nothing is written
    anywhere until someone asks for the string and puts it somewhere.
    """

    __slots__ = ()

    def __init__(self, session: str | None = None) -> None:
        super().__init__(None if session is None else decode_session(session))

    def __repr__(self) -> str:
        return f"StringStorage({self._state!r})"

    def export(self) -> str:
        """The string for the session as it stands.

        Sync, because there is nothing to wait for, and because the natural
        moment to call it is right after a login, printing the result once.
        """
        return encode_session(self._state)
