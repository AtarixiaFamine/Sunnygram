# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""The forms each abstract type in the channels namespace can take.

These aliases are for type checkers. They have no runtime form, because
building one would mean importing every constructor up front.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import channels as types_channels

    AdminLogResults = types_channels.AdminLogResults

    ChannelParticipant = types_channels.ChannelParticipant

    ChannelParticipants = (
        types_channels.ChannelParticipants
        | types_channels.ChannelParticipantsNotModified
    )

    SendAsPeers = types_channels.SendAsPeers

    SponsoredMessageReportResult = (
        types_channels.SponsoredMessageReportResultChooseOption
        | types_channels.SponsoredMessageReportResultAdsHidden
        | types_channels.SponsoredMessageReportResultReported
    )
