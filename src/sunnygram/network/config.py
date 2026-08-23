# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Reading the datacenter list the server hands out.

The built-in table next door has five addresses in it, which is enough to ask a
question and no more. Everything else a client needs to know about the network
comes back from help.getConfig: media-only addresses, addresses that have moved,
and the ones that matter here, the CDN datacenters.

A CDN datacenter is not a Telegram datacenter with a different number. It is a
third party paid to hold bytes, it has no idea who anybody is, and it is never
told: it hands over encrypted blocks that only the client can open, and the
client checks their hashes against what the real datacenter said they should be.
Two consequences show up in this module. Its address exists only in the config,
because the set of them changes, and it is named by its own RSA key from
help.getCdnConfig instead of by the built-in ones, because it is not Telegram.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..crypto import PublicKey
from ..errors import SunnygramError
from ..raw import types
from .datacenter import Address

__all__ = ["cdn_address", "cdn_keys"]


def cdn_address(
    options: Sequence[types.DcOption], dc_id: int, *, ipv6: bool = False
) -> Address:
    """Where a CDN datacenter can be reached, out of a config's dc_options.

    Only entries flagged as CDN count. An entry flagged tcpo_only is skipped:
    it wants the obfuscated transport, and a plain connection to one simply
    goes quiet rather than saying so.
    """
    usable = [
        option
        for option in options
        if option.id == dc_id and option.cdn and not option.tcpo_only
    ]
    for option in usable:
        if bool(option.ipv6) == ipv6:
            return Address(dc_id, option.ip_address, option.port)
    if usable:
        # The wanted family is not on offer for this one. The other is still a
        # working address, and refusing it would fail a download over a detail
        # the caller expressed a preference about instead of a requirement.
        first = usable[0]
        return Address(dc_id, first.ip_address, first.port)
    listed = sorted({option.id for option in options if option.cdn})
    raise SunnygramError(
        f"the server sent us to CDN datacenter {dc_id} and then did not say "
        f"where it is; its config lists {listed or 'none'}"
    )


def cdn_keys(config: types.CdnConfig, dc_id: int) -> tuple[PublicKey, ...]:
    """The public keys a CDN datacenter may be named by.

    Every key the config carries for that datacenter, since more than one is
    normal while a key is being rotated, and nothing else. A handshake offered
    a fingerprint outside this set is talking to something that is not the
    datacenter we were sent to, so it fails instead of falls back.
    """
    found = tuple(
        PublicKey.from_pem(key.public_key)
        for key in config.public_keys
        if key.dc_id == dc_id
    )
    if not found:
        raise SunnygramError(
            f"there is no public key for CDN datacenter {dc_id} in the config, "
            "so there is no way to tell it apart from anything else answering "
            "at that address"
        )
    return found
