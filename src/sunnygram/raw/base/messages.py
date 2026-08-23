# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""The forms each abstract type in the messages namespace can take.

These aliases are for type checkers. They have no runtime form, because
building one would mean importing every constructor up front.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import messages as types_messages

    AffectedFoundMessages = types_messages.AffectedFoundMessages

    AffectedHistory = types_messages.AffectedHistory

    AffectedMessages = types_messages.AffectedMessages

    AllStickers = (
        types_messages.AllStickersNotModified
        | types_messages.AllStickers
    )

    ArchivedStickers = types_messages.ArchivedStickers

    AvailableEffects = (
        types_messages.AvailableEffectsNotModified
        | types_messages.AvailableEffects
    )

    AvailableReactions = (
        types_messages.AvailableReactionsNotModified
        | types_messages.AvailableReactions
    )

    BotApp = types_messages.BotApp

    BotCallbackAnswer = types_messages.BotCallbackAnswer

    BotPreparedInlineMessage = types_messages.BotPreparedInlineMessage

    BotResults = types_messages.BotResults

    ChatAdminsWithInvites = types_messages.ChatAdminsWithInvites

    ChatFull = types_messages.ChatFull

    ChatInviteImporters = types_messages.ChatInviteImporters

    ChatInviteJoinResult = (
        types_messages.ChatInviteJoinResultOk
        | types_messages.ChatInviteJoinResultWebView
    )

    Chats = (
        types_messages.Chats
        | types_messages.ChatsSlice
    )

    CheckedHistoryImportPeer = types_messages.CheckedHistoryImportPeer

    ComposedMessageWithAI = types_messages.ComposedMessageWithAI

    ComposedRichMessageWithAI = types_messages.ComposedRichMessageWithAI

    DhConfig = (
        types_messages.DhConfigNotModified
        | types_messages.DhConfig
    )

    DialogFilters = types_messages.DialogFilters

    Dialogs = (
        types_messages.Dialogs
        | types_messages.DialogsSlice
        | types_messages.DialogsNotModified
    )

    DiscussionMessage = types_messages.DiscussionMessage

    EmojiGameInfo = (
        types_messages.EmojiGameUnavailable
        | types_messages.EmojiGameDiceInfo
    )

    EmojiGameOutcome = types_messages.EmojiGameOutcome

    EmojiGroups = (
        types_messages.EmojiGroupsNotModified
        | types_messages.EmojiGroups
    )

    ExportedChatInvite = (
        types_messages.ExportedChatInvite
        | types_messages.ExportedChatInviteReplaced
    )

    ExportedChatInvites = types_messages.ExportedChatInvites

    FavedStickers = (
        types_messages.FavedStickersNotModified
        | types_messages.FavedStickers
    )

    FeaturedStickers = (
        types_messages.FeaturedStickersNotModified
        | types_messages.FeaturedStickers
    )

    ForumTopics = types_messages.ForumTopics

    FoundStickerSets = (
        types_messages.FoundStickerSetsNotModified
        | types_messages.FoundStickerSets
    )

    FoundStickers = (
        types_messages.FoundStickersNotModified
        | types_messages.FoundStickers
    )

    HighScores = types_messages.HighScores

    HistoryImport = types_messages.HistoryImport

    HistoryImportParsed = types_messages.HistoryImportParsed

    InactiveChats = types_messages.InactiveChats

    InvitedUsers = types_messages.InvitedUsers

    MessageEditData = types_messages.MessageEditData

    MessageReactionsList = types_messages.MessageReactionsList

    MessageViews = types_messages.MessageViews

    Messages = (
        types_messages.Messages
        | types_messages.MessagesSlice
        | types_messages.ChannelMessages
        | types_messages.MessagesNotModified
    )

    MyStickers = types_messages.MyStickers

    PeerDialogs = types_messages.PeerDialogs

    PeerSettings = types_messages.PeerSettings

    PreparedInlineMessage = types_messages.PreparedInlineMessage

    QuickReplies = (
        types_messages.QuickReplies
        | types_messages.QuickRepliesNotModified
    )

    Reactions = (
        types_messages.ReactionsNotModified
        | types_messages.Reactions
    )

    RecentStickers = (
        types_messages.RecentStickersNotModified
        | types_messages.RecentStickers
    )

    SavedDialogs = (
        types_messages.SavedDialogs
        | types_messages.SavedDialogsSlice
        | types_messages.SavedDialogsNotModified
    )

    SavedGifs = (
        types_messages.SavedGifsNotModified
        | types_messages.SavedGifs
    )

    SavedReactionTags = (
        types_messages.SavedReactionTagsNotModified
        | types_messages.SavedReactionTags
    )

    SearchCounter = types_messages.SearchCounter

    SearchResultsCalendar = types_messages.SearchResultsCalendar

    SearchResultsPositions = types_messages.SearchResultsPositions

    SentEncryptedMessage = (
        types_messages.SentEncryptedMessage
        | types_messages.SentEncryptedFile
    )

    SponsoredMessages = (
        types_messages.SponsoredMessages
        | types_messages.SponsoredMessagesEmpty
    )

    StickerSet = (
        types_messages.StickerSet
        | types_messages.StickerSetNotModified
    )

    StickerSetInstallResult = (
        types_messages.StickerSetInstallResultSuccess
        | types_messages.StickerSetInstallResultArchive
    )

    Stickers = (
        types_messages.StickersNotModified
        | types_messages.Stickers
    )

    TranscribedAudio = types_messages.TranscribedAudio

    TranslatedRichMessage = types_messages.TranslatedRichMessage

    TranslatedText = types_messages.TranslateResult

    VotesList = types_messages.VotesList

    WebPage = types_messages.WebPage

    WebPagePreview = types_messages.WebPagePreview
