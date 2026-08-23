# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""The forms each abstract type in the stats namespace can take.

These aliases are for type checkers. They have no runtime form, because
building one would mean importing every constructor up front.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import stats as types_stats

    BroadcastStats = types_stats.BroadcastStats

    MegagroupStats = types_stats.MegagroupStats

    MessageStats = types_stats.MessageStats

    PollStats = types_stats.PollStats

    PublicForwards = types_stats.PublicForwards

    StoryStats = types_stats.StoryStats
