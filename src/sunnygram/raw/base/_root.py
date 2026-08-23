# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""The forms each abstract type in the root namespace can take.

These aliases are for type checkers. They have no runtime form, because
building one would mean importing every constructor up front.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import _root as types__root
    from ..types import mtproto as types_mtproto

    AccessPointRule = types_mtproto.AccessPointRule

    AccountDaysTTL = types__root.AccountDaysTTL

    AiComposeTone = (
        types__root.AiComposeTone
        | types__root.AiComposeToneDefault
    )

    AiComposeToneExample = types__root.AiComposeToneExample

    AttachMenuBot = types__root.AttachMenuBot

    AttachMenuBotIcon = types__root.AttachMenuBotIcon

    AttachMenuBotIconColor = types__root.AttachMenuBotIconColor

    AttachMenuBots = (
        types__root.AttachMenuBotsNotModified
        | types__root.AttachMenuBots
    )

    AttachMenuBotsBot = types__root.AttachMenuBotsBot

    AttachMenuPeerType = (
        types__root.AttachMenuPeerTypeSameBotPM
        | types__root.AttachMenuPeerTypeBotPM
        | types__root.AttachMenuPeerTypePM
        | types__root.AttachMenuPeerTypeChat
        | types__root.AttachMenuPeerTypeBroadcast
    )

    AuctionBidLevel = types__root.AuctionBidLevel

    Authorization = types__root.Authorization

    AutoDownloadSettings = types__root.AutoDownloadSettings

    AutoSaveException = types__root.AutoSaveException

    AutoSaveSettings = types__root.AutoSaveSettings

    AvailableEffect = types__root.AvailableEffect

    AvailableReaction = types__root.AvailableReaction

    BadMsgNotification = (
        types_mtproto.BadMsgNotification
        | types_mtproto.BadServerSalt
    )

    BankCardOpenUrl = types__root.BankCardOpenUrl

    BaseTheme = (
        types__root.BaseThemeClassic
        | types__root.BaseThemeDay
        | types__root.BaseThemeNight
        | types__root.BaseThemeTinted
        | types__root.BaseThemeArctic
    )

    BindAuthKeyInner = types_mtproto.BindAuthKeyInner

    Birthday = types__root.Birthday

    Boost = types__root.Boost

    BotApp = (
        types__root.BotAppNotModified
        | types__root.BotApp
    )

    BotAppSettings = types__root.BotAppSettings

    BotBusinessConnection = types__root.BotBusinessConnection

    BotCommand = types__root.BotCommand

    BotCommandScope = (
        types__root.BotCommandScopeDefault
        | types__root.BotCommandScopeUsers
        | types__root.BotCommandScopeChats
        | types__root.BotCommandScopeChatAdmins
        | types__root.BotCommandScopePeer
        | types__root.BotCommandScopePeerAdmins
        | types__root.BotCommandScopePeerUser
    )

    BotInfo = types__root.BotInfo

    BotInlineMessage = (
        types__root.BotInlineMessageMediaAuto
        | types__root.BotInlineMessageText
        | types__root.BotInlineMessageMediaGeo
        | types__root.BotInlineMessageMediaVenue
        | types__root.BotInlineMessageMediaContact
        | types__root.BotInlineMessageMediaInvoice
        | types__root.BotInlineMessageMediaWebPage
        | types__root.BotInlineMessageRichMessage
    )

    BotInlineResult = (
        types__root.BotInlineResult
        | types__root.BotInlineMediaResult
    )

    BotMenuButton = (
        types__root.BotMenuButtonDefault
        | types__root.BotMenuButtonCommands
        | types__root.BotMenuButton
    )

    BotPreviewMedia = types__root.BotPreviewMedia

    BotVerification = types__root.BotVerification

    BotVerifierSettings = types__root.BotVerifierSettings

    BusinessAwayMessage = types__root.BusinessAwayMessage

    BusinessAwayMessageSchedule = (
        types__root.BusinessAwayMessageScheduleAlways
        | types__root.BusinessAwayMessageScheduleOutsideWorkHours
        | types__root.BusinessAwayMessageScheduleCustom
    )

    BusinessBotRecipients = types__root.BusinessBotRecipients

    BusinessBotRights = types__root.BusinessBotRights

    BusinessChatLink = types__root.BusinessChatLink

    BusinessGreetingMessage = types__root.BusinessGreetingMessage

    BusinessIntro = types__root.BusinessIntro

    BusinessLocation = types__root.BusinessLocation

    BusinessRecipients = types__root.BusinessRecipients

    BusinessWeeklyOpen = types__root.BusinessWeeklyOpen

    BusinessWorkHours = types__root.BusinessWorkHours

    CdnConfig = types__root.CdnConfig

    CdnPublicKey = types__root.CdnPublicKey

    ChannelAdminLogEvent = types__root.ChannelAdminLogEvent

    ChannelAdminLogEventAction = (
        types__root.ChannelAdminLogEventActionChangeTitle
        | types__root.ChannelAdminLogEventActionChangeAbout
        | types__root.ChannelAdminLogEventActionChangeUsername
        | types__root.ChannelAdminLogEventActionChangePhoto
        | types__root.ChannelAdminLogEventActionToggleInvites
        | types__root.ChannelAdminLogEventActionToggleSignatures
        | types__root.ChannelAdminLogEventActionUpdatePinned
        | types__root.ChannelAdminLogEventActionEditMessage
        | types__root.ChannelAdminLogEventActionDeleteMessage
        | types__root.ChannelAdminLogEventActionParticipantJoin
        | types__root.ChannelAdminLogEventActionParticipantLeave
        | types__root.ChannelAdminLogEventActionParticipantInvite
        | types__root.ChannelAdminLogEventActionParticipantToggleBan
        | types__root.ChannelAdminLogEventActionParticipantToggleAdmin
        | types__root.ChannelAdminLogEventActionChangeStickerSet
        | types__root.ChannelAdminLogEventActionTogglePreHistoryHidden
        | types__root.ChannelAdminLogEventActionDefaultBannedRights
        | types__root.ChannelAdminLogEventActionStopPoll
        | types__root.ChannelAdminLogEventActionChangeLinkedChat
        | types__root.ChannelAdminLogEventActionChangeLocation
        | types__root.ChannelAdminLogEventActionToggleSlowMode
        | types__root.ChannelAdminLogEventActionStartGroupCall
        | types__root.ChannelAdminLogEventActionDiscardGroupCall
        | types__root.ChannelAdminLogEventActionParticipantMute
        | types__root.ChannelAdminLogEventActionParticipantUnmute
        | types__root.ChannelAdminLogEventActionToggleGroupCallSetting
        | types__root.ChannelAdminLogEventActionParticipantJoinByInvite
        | types__root.ChannelAdminLogEventActionExportedInviteDelete
        | types__root.ChannelAdminLogEventActionExportedInviteRevoke
        | types__root.ChannelAdminLogEventActionExportedInviteEdit
        | types__root.ChannelAdminLogEventActionParticipantVolume
        | types__root.ChannelAdminLogEventActionChangeHistoryTTL
        | types__root.ChannelAdminLogEventActionParticipantJoinByRequest
        | types__root.ChannelAdminLogEventActionToggleNoForwards
        | types__root.ChannelAdminLogEventActionSendMessage
        | types__root.ChannelAdminLogEventActionChangeAvailableReactions
        | types__root.ChannelAdminLogEventActionChangeUsernames
        | types__root.ChannelAdminLogEventActionToggleForum
        | types__root.ChannelAdminLogEventActionCreateTopic
        | types__root.ChannelAdminLogEventActionEditTopic
        | types__root.ChannelAdminLogEventActionDeleteTopic
        | types__root.ChannelAdminLogEventActionPinTopic
        | types__root.ChannelAdminLogEventActionToggleAntiSpam
        | types__root.ChannelAdminLogEventActionChangePeerColor
        | types__root.ChannelAdminLogEventActionChangeProfilePeerColor
        | types__root.ChannelAdminLogEventActionChangeWallpaper
        | types__root.ChannelAdminLogEventActionChangeEmojiStatus
        | types__root.ChannelAdminLogEventActionChangeEmojiStickerSet
        | types__root.ChannelAdminLogEventActionToggleSignatureProfiles
        | types__root.ChannelAdminLogEventActionParticipantSubExtend
        | types__root.ChannelAdminLogEventActionToggleAutotranslation
        | types__root.ChannelAdminLogEventActionParticipantEditRank
    )

    ChannelAdminLogEventsFilter = types__root.ChannelAdminLogEventsFilter

    ChannelLocation = (
        types__root.ChannelLocationEmpty
        | types__root.ChannelLocation
    )

    ChannelMessagesFilter = (
        types__root.ChannelMessagesFilterEmpty
        | types__root.ChannelMessagesFilter
    )

    ChannelParticipant = (
        types__root.ChannelParticipant
        | types__root.ChannelParticipantSelf
        | types__root.ChannelParticipantCreator
        | types__root.ChannelParticipantAdmin
        | types__root.ChannelParticipantBanned
        | types__root.ChannelParticipantLeft
    )

    ChannelParticipantsFilter = (
        types__root.ChannelParticipantsRecent
        | types__root.ChannelParticipantsAdmins
        | types__root.ChannelParticipantsKicked
        | types__root.ChannelParticipantsBots
        | types__root.ChannelParticipantsBanned
        | types__root.ChannelParticipantsSearch
        | types__root.ChannelParticipantsContacts
        | types__root.ChannelParticipantsMentions
    )

    Chat = (
        types__root.ChatEmpty
        | types__root.Chat
        | types__root.ChatForbidden
        | types__root.Channel
        | types__root.ChannelForbidden
        | types__root.CommunityForbidden
        | types__root.Community
    )

    ChatAdminRights = types__root.ChatAdminRights

    ChatAdminWithInvites = types__root.ChatAdminWithInvites

    ChatBannedRights = types__root.ChatBannedRights

    ChatFull = (
        types__root.ChatFull
        | types__root.ChannelFull
        | types__root.CommunityFull
    )

    ChatInvite = (
        types__root.ChatInviteAlready
        | types__root.ChatInvite
        | types__root.ChatInvitePeek
    )

    ChatInviteImporter = types__root.ChatInviteImporter

    ChatOnlines = types__root.ChatOnlines

    ChatParticipant = (
        types__root.ChatParticipant
        | types__root.ChatParticipantCreator
        | types__root.ChatParticipantAdmin
    )

    ChatParticipants = (
        types__root.ChatParticipantsForbidden
        | types__root.ChatParticipants
    )

    ChatPhoto = (
        types__root.ChatPhotoEmpty
        | types__root.ChatPhoto
    )

    ChatReactions = (
        types__root.ChatReactionsNone
        | types__root.ChatReactionsAll
        | types__root.ChatReactionsSome
    )

    ChatTheme = (
        types__root.ChatTheme
        | types__root.ChatThemeUniqueGift
    )

    ClientDHInnerData = types_mtproto.ClientDHInnerData

    CodeSettings = types__root.CodeSettings

    CommunityPeer = types__root.CommunityPeer

    CommunityPeerRequest = types__root.CommunityPeerRequest

    Config = types__root.Config

    ConnectedBot = types__root.ConnectedBot

    ConnectedBotStarRef = types__root.ConnectedBotStarRef

    Contact = types__root.Contact

    ContactBirthday = types__root.ContactBirthday

    ContactStatus = types__root.ContactStatus

    DataJSON = types__root.DataJSON

    DcOption = types__root.DcOption

    DefaultHistoryTTL = types__root.DefaultHistoryTTL

    DestroyAuthKeyRes = (
        types_mtproto.DestroyAuthKeyOk
        | types_mtproto.DestroyAuthKeyNone
        | types_mtproto.DestroyAuthKeyFail
    )

    DestroySessionRes = (
        types_mtproto.DestroySessionOk
        | types_mtproto.DestroySessionNone
    )

    Dialog = (
        types__root.Dialog
        | types__root.DialogFolder
        | types__root.DialogCommunity
    )

    DialogFilter = (
        types__root.DialogFilter
        | types__root.DialogFilterDefault
        | types__root.DialogFilterChatlist
    )

    DialogFilterSuggested = types__root.DialogFilterSuggested

    DialogPeer = (
        types__root.DialogPeer
        | types__root.DialogPeerFolder
        | types__root.DialogPeerCommunity
    )

    DisallowedGiftsSettings = types__root.DisallowedGiftsSettings

    Document = (
        types__root.DocumentEmpty
        | types__root.Document
    )

    DocumentAttribute = (
        types__root.DocumentAttributeImageSize
        | types__root.DocumentAttributeAnimated
        | types__root.DocumentAttributeSticker
        | types__root.DocumentAttributeVideo
        | types__root.DocumentAttributeAudio
        | types__root.DocumentAttributeFilename
        | types__root.DocumentAttributeHasStickers
        | types__root.DocumentAttributeCustomEmoji
    )

    DraftMessage = (
        types__root.DraftMessageEmpty
        | types__root.DraftMessage
    )

    EmailVerification = (
        types__root.EmailVerificationCode
        | types__root.EmailVerificationGoogle
        | types__root.EmailVerificationApple
    )

    EmailVerifyPurpose = (
        types__root.EmailVerifyPurposeLoginSetup
        | types__root.EmailVerifyPurposeLoginChange
        | types__root.EmailVerifyPurposePassport
    )

    EmojiGroup = (
        types__root.EmojiGroup
        | types__root.EmojiGroupGreeting
        | types__root.EmojiGroupPremium
    )

    EmojiKeyword = (
        types__root.EmojiKeyword
        | types__root.EmojiKeywordDeleted
    )

    EmojiKeywordsDifference = types__root.EmojiKeywordsDifference

    EmojiLanguage = types__root.EmojiLanguage

    EmojiList = (
        types__root.EmojiListNotModified
        | types__root.EmojiList
    )

    EmojiStatus = (
        types__root.EmojiStatusEmpty
        | types__root.EmojiStatus
        | types__root.EmojiStatusCollectible
        | types__root.InputEmojiStatusCollectible
    )

    EmojiURL = types__root.EmojiURL

    EncryptedChat = (
        types__root.EncryptedChatEmpty
        | types__root.EncryptedChatWaiting
        | types__root.EncryptedChatRequested
        | types__root.EncryptedChat
        | types__root.EncryptedChatDiscarded
    )

    EncryptedFile = (
        types__root.EncryptedFileEmpty
        | types__root.EncryptedFile
    )

    EncryptedMessage = (
        types__root.EncryptedMessage
        | types__root.EncryptedMessageService
    )

    EphemeralMessage = types__root.EphemeralMessage

    Error = types__root.Error

    ExportedChatInvite = (
        types__root.ChatInviteExported
        | types__root.ChatInvitePublicJoinRequests
    )

    ExportedChatlistInvite = types__root.ExportedChatlistInvite

    ExportedContactToken = types__root.ExportedContactToken

    ExportedMessageLink = types__root.ExportedMessageLink

    ExportedStoryLink = types__root.ExportedStoryLink

    FactCheck = types__root.FactCheck

    FileHash = types__root.FileHash

    Folder = types__root.Folder

    FolderPeer = types__root.FolderPeer

    ForumTopic = (
        types__root.ForumTopicDeleted
        | types__root.ForumTopic
    )

    FoundStory = types__root.FoundStory

    FutureSalt = types_mtproto.FutureSalt

    FutureSalts = types_mtproto.FutureSalts

    Game = types__root.Game

    GeoPoint = (
        types__root.GeoPointEmpty
        | types__root.GeoPoint
    )

    GeoPointAddress = types__root.GeoPointAddress

    GlobalPrivacySettings = types__root.GlobalPrivacySettings

    GroupCall = (
        types__root.GroupCallDiscarded
        | types__root.GroupCall
    )

    GroupCallDonor = types__root.GroupCallDonor

    GroupCallMessage = types__root.GroupCallMessage

    GroupCallParticipant = types__root.GroupCallParticipant

    GroupCallParticipantVideo = types__root.GroupCallParticipantVideo

    GroupCallParticipantVideoSourceGroup = types__root.GroupCallParticipantVideoSourceGroup

    GroupCallStreamChannel = types__root.GroupCallStreamChannel

    HighScore = types__root.HighScore

    HttpWait = types_mtproto.HttpWait

    ImportedContact = types__root.ImportedContact

    InlineBotSwitchPM = types__root.InlineBotSwitchPM

    InlineBotWebView = types__root.InlineBotWebView

    InlineQueryPeerType = (
        types__root.InlineQueryPeerTypeSameBotPM
        | types__root.InlineQueryPeerTypePM
        | types__root.InlineQueryPeerTypeChat
        | types__root.InlineQueryPeerTypeMegagroup
        | types__root.InlineQueryPeerTypeBroadcast
        | types__root.InlineQueryPeerTypeBotPM
    )

    InputAiComposeTone = (
        types__root.InputAiComposeToneDefault
        | types__root.InputAiComposeToneID
        | types__root.InputAiComposeToneSlug
        | types__root.InputAiComposeToneSingleUse
    )

    InputAppEvent = types__root.InputAppEvent

    InputBotApp = (
        types__root.InputBotAppID
        | types__root.InputBotAppShortName
    )

    InputBotInlineMessage = (
        types__root.InputBotInlineMessageMediaAuto
        | types__root.InputBotInlineMessageText
        | types__root.InputBotInlineMessageMediaGeo
        | types__root.InputBotInlineMessageMediaVenue
        | types__root.InputBotInlineMessageMediaContact
        | types__root.InputBotInlineMessageGame
        | types__root.InputBotInlineMessageMediaInvoice
        | types__root.InputBotInlineMessageMediaWebPage
        | types__root.InputBotInlineMessageRichMessage
    )

    InputBotInlineMessageID = (
        types__root.InputBotInlineMessageID
        | types__root.InputBotInlineMessageID64
    )

    InputBotInlineResult = (
        types__root.InputBotInlineResult
        | types__root.InputBotInlineResultPhoto
        | types__root.InputBotInlineResultDocument
        | types__root.InputBotInlineResultGame
    )

    InputBusinessAwayMessage = types__root.InputBusinessAwayMessage

    InputBusinessBotRecipients = types__root.InputBusinessBotRecipients

    InputBusinessChatLink = types__root.InputBusinessChatLink

    InputBusinessGreetingMessage = types__root.InputBusinessGreetingMessage

    InputBusinessIntro = types__root.InputBusinessIntro

    InputBusinessRecipients = types__root.InputBusinessRecipients

    InputChannel = (
        types__root.InputChannelEmpty
        | types__root.InputChannel
        | types__root.InputChannelFromMessage
    )

    InputChatPhoto = (
        types__root.InputChatPhotoEmpty
        | types__root.InputChatUploadedPhoto
        | types__root.InputChatPhoto
    )

    InputChatTheme = (
        types__root.InputChatThemeEmpty
        | types__root.InputChatTheme
        | types__root.InputChatThemeUniqueGift
    )

    InputChatlist = types__root.InputChatlistDialogFilter

    InputCheckPasswordSRP = (
        types__root.InputCheckPasswordEmpty
        | types__root.InputCheckPasswordSRP
    )

    InputClientProxy = types__root.InputClientProxy

    InputCollectible = (
        types__root.InputCollectibleUsername
        | types__root.InputCollectiblePhone
    )

    InputContact = types__root.InputPhoneContact

    InputDialogPeer = (
        types__root.InputDialogPeer
        | types__root.InputDialogPeerFolder
        | types__root.InputDialogPeerCommunity
    )

    InputDocument = (
        types__root.InputDocumentEmpty
        | types__root.InputDocument
    )

    InputEncryptedChat = types__root.InputEncryptedChat

    InputEncryptedFile = (
        types__root.InputEncryptedFileEmpty
        | types__root.InputEncryptedFileUploaded
        | types__root.InputEncryptedFile
        | types__root.InputEncryptedFileBigUploaded
    )

    InputFile = (
        types__root.InputFile
        | types__root.InputFileBig
        | types__root.InputFileStoryDocument
    )

    InputFileLocation = (
        types__root.InputFileLocation
        | types__root.InputEncryptedFileLocation
        | types__root.InputDocumentFileLocation
        | types__root.InputSecureFileLocation
        | types__root.InputTakeoutFileLocation
        | types__root.InputPhotoFileLocation
        | types__root.InputPhotoLegacyFileLocation
        | types__root.InputPeerPhotoFileLocation
        | types__root.InputStickerSetThumb
        | types__root.InputGroupCallStream
    )

    InputFolderPeer = types__root.InputFolderPeer

    InputGame = (
        types__root.InputGameID
        | types__root.InputGameShortName
    )

    InputGeoPoint = (
        types__root.InputGeoPointEmpty
        | types__root.InputGeoPoint
    )

    InputGroupCall = (
        types__root.InputGroupCall
        | types__root.InputGroupCallSlug
        | types__root.InputGroupCallInviteMessage
    )

    InputInvoice = (
        types__root.InputInvoiceMessage
        | types__root.InputInvoiceSlug
        | types__root.InputInvoicePremiumGiftCode
        | types__root.InputInvoiceStars
        | types__root.InputInvoiceChatInviteSubscription
        | types__root.InputInvoiceStarGift
        | types__root.InputInvoiceStarGiftUpgrade
        | types__root.InputInvoiceStarGiftTransfer
        | types__root.InputInvoicePremiumGiftStars
        | types__root.InputInvoiceBusinessBotTransferStars
        | types__root.InputInvoiceStarGiftResale
        | types__root.InputInvoiceStarGiftPrepaidUpgrade
        | types__root.InputInvoicePremiumAuthCode
        | types__root.InputInvoiceStarGiftDropOriginalDetails
        | types__root.InputInvoiceStarGiftAuctionBid
    )

    InputMedia = (
        types__root.InputMediaEmpty
        | types__root.InputMediaUploadedPhoto
        | types__root.InputMediaPhoto
        | types__root.InputMediaGeoPoint
        | types__root.InputMediaContact
        | types__root.InputMediaUploadedDocument
        | types__root.InputMediaDocument
        | types__root.InputMediaVenue
        | types__root.InputMediaPhotoExternal
        | types__root.InputMediaDocumentExternal
        | types__root.InputMediaGame
        | types__root.InputMediaInvoice
        | types__root.InputMediaGeoLive
        | types__root.InputMediaPoll
        | types__root.InputMediaDice
        | types__root.InputMediaStory
        | types__root.InputMediaWebPage
        | types__root.InputMediaPaidMedia
        | types__root.InputMediaTodo
        | types__root.InputMediaStakeDice
    )

    InputMessage = (
        types__root.InputMessageID
        | types__root.InputMessageReplyTo
        | types__root.InputMessagePinned
        | types__root.InputMessageCallbackQuery
    )

    InputMessageReadMetric = types__root.InputMessageReadMetric

    InputNotifyPeer = (
        types__root.InputNotifyPeer
        | types__root.InputNotifyUsers
        | types__root.InputNotifyChats
        | types__root.InputNotifyBroadcasts
        | types__root.InputNotifyForumTopic
        | types__root.InputNotifyCommunity
    )

    InputPasskeyCredential = (
        types__root.InputPasskeyCredentialPublicKey
        | types__root.InputPasskeyCredentialFirebasePNV
    )

    InputPasskeyResponse = (
        types__root.InputPasskeyResponseRegister
        | types__root.InputPasskeyResponseLogin
    )

    InputPaymentCredentials = (
        types__root.InputPaymentCredentialsSaved
        | types__root.InputPaymentCredentials
        | types__root.InputPaymentCredentialsApplePay
        | types__root.InputPaymentCredentialsGooglePay
    )

    InputPeer = (
        types__root.InputPeerEmpty
        | types__root.InputPeerSelf
        | types__root.InputPeerChat
        | types__root.InputPeerUser
        | types__root.InputPeerChannel
        | types__root.InputPeerUserFromMessage
        | types__root.InputPeerChannelFromMessage
    )

    InputPeerNotifySettings = types__root.InputPeerNotifySettings

    InputPhoneCall = types__root.InputPhoneCall

    InputPhoto = (
        types__root.InputPhotoEmpty
        | types__root.InputPhoto
    )

    InputPrivacyKey = (
        types__root.InputPrivacyKeyStatusTimestamp
        | types__root.InputPrivacyKeyChatInvite
        | types__root.InputPrivacyKeyPhoneCall
        | types__root.InputPrivacyKeyPhoneP2P
        | types__root.InputPrivacyKeyForwards
        | types__root.InputPrivacyKeyProfilePhoto
        | types__root.InputPrivacyKeyPhoneNumber
        | types__root.InputPrivacyKeyAddedByPhone
        | types__root.InputPrivacyKeyVoiceMessages
        | types__root.InputPrivacyKeyAbout
        | types__root.InputPrivacyKeyBirthday
        | types__root.InputPrivacyKeyStarGiftsAutoSave
        | types__root.InputPrivacyKeyNoPaidMessages
        | types__root.InputPrivacyKeySavedMusic
    )

    InputPrivacyRule = (
        types__root.InputPrivacyValueAllowContacts
        | types__root.InputPrivacyValueAllowAll
        | types__root.InputPrivacyValueAllowUsers
        | types__root.InputPrivacyValueDisallowContacts
        | types__root.InputPrivacyValueDisallowAll
        | types__root.InputPrivacyValueDisallowUsers
        | types__root.InputPrivacyValueAllowChatParticipants
        | types__root.InputPrivacyValueDisallowChatParticipants
        | types__root.InputPrivacyValueAllowCloseFriends
        | types__root.InputPrivacyValueAllowPremium
        | types__root.InputPrivacyValueAllowBots
        | types__root.InputPrivacyValueDisallowBots
    )

    InputQuickReplyShortcut = (
        types__root.InputQuickReplyShortcut
        | types__root.InputQuickReplyShortcutId
    )

    InputReplyTo = (
        types__root.InputReplyToMessage
        | types__root.InputReplyToStory
        | types__root.InputReplyToMonoForum
        | types__root.InputReplyToEphemeralMessage
    )

    InputRichFile = (
        types__root.InputRichFilePhoto
        | types__root.InputRichFileDocument
    )

    InputRichMessage = (
        types__root.InputRichMessage
        | types__root.InputRichMessageHTML
        | types__root.InputRichMessageMarkdown
    )

    InputSavedStarGift = (
        types__root.InputSavedStarGiftUser
        | types__root.InputSavedStarGiftChat
        | types__root.InputSavedStarGiftSlug
    )

    InputSecureFile = (
        types__root.InputSecureFileUploaded
        | types__root.InputSecureFile
    )

    InputSecureValue = types__root.InputSecureValue

    InputSingleMedia = types__root.InputSingleMedia

    InputStarGiftAuction = (
        types__root.InputStarGiftAuction
        | types__root.InputStarGiftAuctionSlug
    )

    InputStarsTransaction = types__root.InputStarsTransaction

    InputStickerSet = (
        types__root.InputStickerSetEmpty
        | types__root.InputStickerSetID
        | types__root.InputStickerSetShortName
        | types__root.InputStickerSetAnimatedEmoji
        | types__root.InputStickerSetDice
        | types__root.InputStickerSetAnimatedEmojiAnimations
        | types__root.InputStickerSetPremiumGifts
        | types__root.InputStickerSetEmojiGenericAnimations
        | types__root.InputStickerSetEmojiDefaultStatuses
        | types__root.InputStickerSetEmojiDefaultTopicIcons
        | types__root.InputStickerSetEmojiChannelDefaultStatuses
        | types__root.InputStickerSetTonGifts
    )

    InputStickerSetItem = types__root.InputStickerSetItem

    InputStickeredMedia = (
        types__root.InputStickeredMediaPhoto
        | types__root.InputStickeredMediaDocument
    )

    InputStorePaymentPurpose = (
        types__root.InputStorePaymentPremiumSubscription
        | types__root.InputStorePaymentGiftPremium
        | types__root.InputStorePaymentPremiumGiftCode
        | types__root.InputStorePaymentPremiumGiveaway
        | types__root.InputStorePaymentStarsTopup
        | types__root.InputStorePaymentStarsGift
        | types__root.InputStorePaymentStarsGiveaway
        | types__root.InputStorePaymentAuthCode
    )

    InputTheme = (
        types__root.InputTheme
        | types__root.InputThemeSlug
    )

    InputThemeSettings = types__root.InputThemeSettings

    InputUser = (
        types__root.InputUserEmpty
        | types__root.InputUserSelf
        | types__root.InputUser
        | types__root.InputUserFromMessage
    )

    InputWallPaper = (
        types__root.InputWallPaper
        | types__root.InputWallPaperSlug
        | types__root.InputWallPaperNoFile
    )

    InputWebDocument = types__root.InputWebDocument

    InputWebFileLocation = (
        types__root.InputWebFileLocation
        | types__root.InputWebFileGeoPointLocation
        | types__root.InputWebFileAudioAlbumThumbLocation
    )

    Invoice = types__root.Invoice

    IpPort = (
        types_mtproto.IpPort
        | types_mtproto.IpPortSecret
    )

    JSONObjectValue = types__root.JsonObjectValue

    JSONValue = (
        types__root.JsonNull
        | types__root.JsonBool
        | types__root.JsonNumber
        | types__root.JsonString
        | types__root.JsonArray
        | types__root.JsonObject
    )

    JoinChatBotResult = (
        types__root.JoinChatBotResultApproved
        | types__root.JoinChatBotResultDeclined
        | types__root.JoinChatBotResultQueued
        | types__root.JoinChatBotResultWebView
    )

    KeyboardButton = (
        types__root.KeyboardButton
        | types__root.KeyboardButtonUrl
        | types__root.KeyboardButtonCallback
        | types__root.KeyboardButtonRequestPhone
        | types__root.KeyboardButtonRequestGeoLocation
        | types__root.KeyboardButtonSwitchInline
        | types__root.KeyboardButtonGame
        | types__root.KeyboardButtonBuy
        | types__root.KeyboardButtonUrlAuth
        | types__root.InputKeyboardButtonUrlAuth
        | types__root.KeyboardButtonRequestPoll
        | types__root.InputKeyboardButtonUserProfile
        | types__root.KeyboardButtonUserProfile
        | types__root.KeyboardButtonWebView
        | types__root.KeyboardButtonSimpleWebView
        | types__root.KeyboardButtonRequestPeer
        | types__root.InputKeyboardButtonRequestPeer
        | types__root.KeyboardButtonCopy
    )

    KeyboardButtonRow = types__root.KeyboardButtonRow

    KeyboardButtonStyle = types__root.KeyboardButtonStyle

    LabeledPrice = types__root.LabeledPrice

    LangPackDifference = types__root.LangPackDifference

    LangPackLanguage = types__root.LangPackLanguage

    LangPackString = (
        types__root.LangPackString
        | types__root.LangPackStringPluralized
        | types__root.LangPackStringDeleted
    )

    MaskCoords = types__root.MaskCoords

    MediaArea = (
        types__root.MediaAreaVenue
        | types__root.InputMediaAreaVenue
        | types__root.MediaAreaGeoPoint
        | types__root.MediaAreaSuggestedReaction
        | types__root.MediaAreaChannelPost
        | types__root.InputMediaAreaChannelPost
        | types__root.MediaAreaUrl
        | types__root.MediaAreaWeather
        | types__root.MediaAreaStarGift
    )

    MediaAreaCoordinates = types__root.MediaAreaCoordinates

    Message = (
        types__root.MessageEmpty
        | types__root.Message
        | types__root.MessageService
    )

    MessageAction = (
        types__root.MessageActionEmpty
        | types__root.MessageActionChatCreate
        | types__root.MessageActionChatEditTitle
        | types__root.MessageActionChatEditPhoto
        | types__root.MessageActionChatDeletePhoto
        | types__root.MessageActionChatAddUser
        | types__root.MessageActionChatDeleteUser
        | types__root.MessageActionChatJoinedByLink
        | types__root.MessageActionChannelCreate
        | types__root.MessageActionChatMigrateTo
        | types__root.MessageActionChannelMigrateFrom
        | types__root.MessageActionPinMessage
        | types__root.MessageActionHistoryClear
        | types__root.MessageActionGameScore
        | types__root.MessageActionPaymentSentMe
        | types__root.MessageActionPaymentSent
        | types__root.MessageActionPhoneCall
        | types__root.MessageActionScreenshotTaken
        | types__root.MessageActionCustomAction
        | types__root.MessageActionBotAllowed
        | types__root.MessageActionSecureValuesSentMe
        | types__root.MessageActionSecureValuesSent
        | types__root.MessageActionContactSignUp
        | types__root.MessageActionGeoProximityReached
        | types__root.MessageActionGroupCall
        | types__root.MessageActionInviteToGroupCall
        | types__root.MessageActionSetMessagesTTL
        | types__root.MessageActionGroupCallScheduled
        | types__root.MessageActionSetChatTheme
        | types__root.MessageActionChatJoinedByRequest
        | types__root.MessageActionWebViewDataSentMe
        | types__root.MessageActionWebViewDataSent
        | types__root.MessageActionGiftPremium
        | types__root.MessageActionTopicCreate
        | types__root.MessageActionTopicEdit
        | types__root.MessageActionSuggestProfilePhoto
        | types__root.MessageActionRequestedPeer
        | types__root.MessageActionSetChatWallPaper
        | types__root.MessageActionGiftCode
        | types__root.MessageActionGiveawayLaunch
        | types__root.MessageActionGiveawayResults
        | types__root.MessageActionBoostApply
        | types__root.MessageActionRequestedPeerSentMe
        | types__root.MessageActionPaymentRefunded
        | types__root.MessageActionGiftStars
        | types__root.MessageActionPrizeStars
        | types__root.MessageActionStarGift
        | types__root.MessageActionStarGiftUnique
        | types__root.MessageActionPaidMessagesRefunded
        | types__root.MessageActionPaidMessagesPrice
        | types__root.MessageActionConferenceCall
        | types__root.MessageActionTodoCompletions
        | types__root.MessageActionTodoAppendTasks
        | types__root.MessageActionSuggestedPostApproval
        | types__root.MessageActionSuggestedPostSuccess
        | types__root.MessageActionSuggestedPostRefund
        | types__root.MessageActionGiftTon
        | types__root.MessageActionSuggestBirthday
        | types__root.MessageActionStarGiftPurchaseOffer
        | types__root.MessageActionStarGiftPurchaseOfferDeclined
        | types__root.MessageActionNewCreatorPending
        | types__root.MessageActionChangeCreator
        | types__root.MessageActionNoForwardsToggle
        | types__root.MessageActionNoForwardsRequest
        | types__root.MessageActionPollAppendAnswer
        | types__root.MessageActionPollDeleteAnswer
        | types__root.MessageActionManagedBotCreated
        | types__root.MessageActionChangeCommunity
    )

    MessageEntity = (
        types__root.MessageEntityUnknown
        | types__root.MessageEntityMention
        | types__root.MessageEntityHashtag
        | types__root.MessageEntityBotCommand
        | types__root.MessageEntityUrl
        | types__root.MessageEntityEmail
        | types__root.MessageEntityBold
        | types__root.MessageEntityItalic
        | types__root.MessageEntityCode
        | types__root.MessageEntityPre
        | types__root.MessageEntityTextUrl
        | types__root.MessageEntityMentionName
        | types__root.InputMessageEntityMentionName
        | types__root.MessageEntityPhone
        | types__root.MessageEntityCashtag
        | types__root.MessageEntityUnderline
        | types__root.MessageEntityStrike
        | types__root.MessageEntityBankCard
        | types__root.MessageEntitySpoiler
        | types__root.MessageEntityCustomEmoji
        | types__root.MessageEntityBlockquote
        | types__root.MessageEntityFormattedDate
        | types__root.MessageEntityDiffInsert
        | types__root.MessageEntityDiffReplace
        | types__root.MessageEntityDiffDelete
    )

    MessageExtendedMedia = (
        types__root.MessageExtendedMediaPreview
        | types__root.MessageExtendedMedia
    )

    MessageFwdHeader = types__root.MessageFwdHeader

    MessageMedia = (
        types__root.MessageMediaEmpty
        | types__root.MessageMediaPhoto
        | types__root.MessageMediaGeo
        | types__root.MessageMediaContact
        | types__root.MessageMediaUnsupported
        | types__root.MessageMediaDocument
        | types__root.MessageMediaWebPage
        | types__root.MessageMediaVenue
        | types__root.MessageMediaGame
        | types__root.MessageMediaInvoice
        | types__root.MessageMediaGeoLive
        | types__root.MessageMediaPoll
        | types__root.MessageMediaDice
        | types__root.MessageMediaStory
        | types__root.MessageMediaGiveaway
        | types__root.MessageMediaGiveawayResults
        | types__root.MessageMediaPaidMedia
        | types__root.MessageMediaToDo
        | types__root.MessageMediaVideoStream
    )

    MessagePeerReaction = types__root.MessagePeerReaction

    MessagePeerVote = (
        types__root.MessagePeerVote
        | types__root.MessagePeerVoteInputOption
        | types__root.MessagePeerVoteMultiple
    )

    MessageRange = types__root.MessageRange

    MessageReactions = types__root.MessageReactions

    MessageReactor = types__root.MessageReactor

    MessageReplies = types__root.MessageReplies

    MessageReplyHeader = (
        types__root.MessageReplyHeader
        | types__root.MessageReplyStoryHeader
    )

    MessageReportOption = types__root.MessageReportOption

    MessageViews = types__root.MessageViews

    MessagesFilter = (
        types__root.InputMessagesFilterEmpty
        | types__root.InputMessagesFilterPhotos
        | types__root.InputMessagesFilterVideo
        | types__root.InputMessagesFilterPhotoVideo
        | types__root.InputMessagesFilterDocument
        | types__root.InputMessagesFilterUrl
        | types__root.InputMessagesFilterGif
        | types__root.InputMessagesFilterVoice
        | types__root.InputMessagesFilterMusic
        | types__root.InputMessagesFilterChatPhotos
        | types__root.InputMessagesFilterPhoneCalls
        | types__root.InputMessagesFilterRoundVoice
        | types__root.InputMessagesFilterRoundVideo
        | types__root.InputMessagesFilterMyMentions
        | types__root.InputMessagesFilterGeo
        | types__root.InputMessagesFilterContacts
        | types__root.InputMessagesFilterPinned
        | types__root.InputMessagesFilterPoll
    )

    MissingInvitee = types__root.MissingInvitee

    MsgDetailedInfo = (
        types_mtproto.MsgDetailedInfo
        | types_mtproto.MsgNewDetailedInfo
    )

    MsgResendReq = types_mtproto.MsgResendReq

    MsgsAck = types_mtproto.MsgsAck

    MsgsAllInfo = types_mtproto.MsgsAllInfo

    MsgsStateInfo = types_mtproto.MsgsStateInfo

    MsgsStateReq = types_mtproto.MsgsStateReq

    MyBoost = types__root.MyBoost

    NearestDc = types__root.NearestDc

    NewSession = types_mtproto.NewSessionCreated

    NotificationSound = (
        types__root.NotificationSoundDefault
        | types__root.NotificationSoundNone
        | types__root.NotificationSoundLocal
        | types__root.NotificationSoundRingtone
    )

    NotifyPeer = (
        types__root.NotifyPeer
        | types__root.NotifyUsers
        | types__root.NotifyChats
        | types__root.NotifyBroadcasts
        | types__root.NotifyForumTopic
        | types__root.NotifyCommunity
    )

    Null = types__root.Null

    OutboxReadDate = types__root.OutboxReadDate

    PQInnerData = (
        types_mtproto.PQInnerData
        | types_mtproto.PQInnerDataDc
        | types_mtproto.PQInnerDataTemp
        | types_mtproto.PQInnerDataTempDc
    )

    Page = types__root.Page

    PageBlock = (
        types__root.PageBlockUnsupported
        | types__root.PageBlockTitle
        | types__root.PageBlockSubtitle
        | types__root.PageBlockAuthorDate
        | types__root.PageBlockHeader
        | types__root.PageBlockSubheader
        | types__root.PageBlockParagraph
        | types__root.PageBlockPreformatted
        | types__root.PageBlockFooter
        | types__root.PageBlockDivider
        | types__root.PageBlockAnchor
        | types__root.PageBlockList
        | types__root.PageBlockBlockquote
        | types__root.PageBlockPullquote
        | types__root.PageBlockPhoto
        | types__root.PageBlockVideo
        | types__root.PageBlockCover
        | types__root.PageBlockEmbed
        | types__root.PageBlockEmbedPost
        | types__root.PageBlockCollage
        | types__root.PageBlockSlideshow
        | types__root.PageBlockChannel
        | types__root.PageBlockAudio
        | types__root.PageBlockKicker
        | types__root.PageBlockTable
        | types__root.PageBlockOrderedList
        | types__root.PageBlockDetails
        | types__root.PageBlockRelatedArticles
        | types__root.PageBlockMap
        | types__root.PageBlockHeading1
        | types__root.PageBlockHeading2
        | types__root.PageBlockHeading3
        | types__root.PageBlockHeading4
        | types__root.PageBlockHeading5
        | types__root.PageBlockHeading6
        | types__root.PageBlockMath
        | types__root.PageBlockThinking
        | types__root.InputPageBlockMap
        | types__root.PageBlockBlockquoteBlocks
    )

    PageCaption = types__root.PageCaption

    PageListItem = (
        types__root.PageListItemText
        | types__root.PageListItemBlocks
    )

    PageListOrderedItem = (
        types__root.PageListOrderedItemText
        | types__root.PageListOrderedItemBlocks
    )

    PageRelatedArticle = types__root.PageRelatedArticle

    PageTableCell = types__root.PageTableCell

    PageTableRow = types__root.PageTableRow

    PaidReactionPrivacy = (
        types__root.PaidReactionPrivacyDefault
        | types__root.PaidReactionPrivacyAnonymous
        | types__root.PaidReactionPrivacyPeer
    )

    Passkey = types__root.Passkey

    PasswordKdfAlgo = (
        types__root.PasswordKdfAlgoUnknown
        | types__root.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow
    )

    PaymentCharge = types__root.PaymentCharge

    PaymentFormMethod = types__root.PaymentFormMethod

    PaymentRequestedInfo = types__root.PaymentRequestedInfo

    PaymentSavedCredentials = types__root.PaymentSavedCredentialsCard

    Peer = (
        types__root.PeerUser
        | types__root.PeerChat
        | types__root.PeerChannel
    )

    PeerBlocked = types__root.PeerBlocked

    PeerColor = (
        types__root.PeerColor
        | types__root.PeerColorCollectible
        | types__root.InputPeerColorCollectible
    )

    PeerLocated = (
        types__root.PeerLocated
        | types__root.PeerSelfLocated
    )

    PeerNotifySettings = types__root.PeerNotifySettings

    PeerSettings = types__root.PeerSettings

    PeerStories = types__root.PeerStories

    PendingSuggestion = types__root.PendingSuggestion

    PhoneCall = (
        types__root.PhoneCallEmpty
        | types__root.PhoneCallWaiting
        | types__root.PhoneCallRequested
        | types__root.PhoneCallAccepted
        | types__root.PhoneCall
        | types__root.PhoneCallDiscarded
    )

    PhoneCallDiscardReason = (
        types__root.PhoneCallDiscardReasonMissed
        | types__root.PhoneCallDiscardReasonDisconnect
        | types__root.PhoneCallDiscardReasonHangup
        | types__root.PhoneCallDiscardReasonBusy
        | types__root.PhoneCallDiscardReasonMigrateConferenceCall
    )

    PhoneCallProtocol = types__root.PhoneCallProtocol

    PhoneConnection = (
        types__root.PhoneConnection
        | types__root.PhoneConnectionWebrtc
    )

    Photo = (
        types__root.PhotoEmpty
        | types__root.Photo
    )

    PhotoSize = (
        types__root.PhotoSizeEmpty
        | types__root.PhotoSize
        | types__root.PhotoCachedSize
        | types__root.PhotoStrippedSize
        | types__root.PhotoSizeProgressive
        | types__root.PhotoPathSize
    )

    Poll = types__root.Poll

    PollAnswer = (
        types__root.PollAnswer
        | types__root.InputPollAnswer
    )

    PollAnswerVoters = types__root.PollAnswerVoters

    PollResults = types__root.PollResults

    Pong = types_mtproto.Pong

    PopularContact = types__root.PopularContact

    PostAddress = types__root.PostAddress

    PostInteractionCounters = (
        types__root.PostInteractionCountersMessage
        | types__root.PostInteractionCountersStory
    )

    PremiumGiftCodeOption = types__root.PremiumGiftCodeOption

    PremiumSubscriptionOption = types__root.PremiumSubscriptionOption

    PrepaidGiveaway = (
        types__root.PrepaidGiveaway
        | types__root.PrepaidStarsGiveaway
    )

    PrivacyKey = (
        types__root.PrivacyKeyStatusTimestamp
        | types__root.PrivacyKeyChatInvite
        | types__root.PrivacyKeyPhoneCall
        | types__root.PrivacyKeyPhoneP2P
        | types__root.PrivacyKeyForwards
        | types__root.PrivacyKeyProfilePhoto
        | types__root.PrivacyKeyPhoneNumber
        | types__root.PrivacyKeyAddedByPhone
        | types__root.PrivacyKeyVoiceMessages
        | types__root.PrivacyKeyAbout
        | types__root.PrivacyKeyBirthday
        | types__root.PrivacyKeyStarGiftsAutoSave
        | types__root.PrivacyKeyNoPaidMessages
        | types__root.PrivacyKeySavedMusic
    )

    PrivacyRule = (
        types__root.PrivacyValueAllowContacts
        | types__root.PrivacyValueAllowAll
        | types__root.PrivacyValueAllowUsers
        | types__root.PrivacyValueDisallowContacts
        | types__root.PrivacyValueDisallowAll
        | types__root.PrivacyValueDisallowUsers
        | types__root.PrivacyValueAllowChatParticipants
        | types__root.PrivacyValueDisallowChatParticipants
        | types__root.PrivacyValueAllowCloseFriends
        | types__root.PrivacyValueAllowPremium
        | types__root.PrivacyValueAllowBots
        | types__root.PrivacyValueDisallowBots
    )

    ProfileTab = (
        types__root.ProfileTabPosts
        | types__root.ProfileTabGifts
        | types__root.ProfileTabMedia
        | types__root.ProfileTabFiles
        | types__root.ProfileTabMusic
        | types__root.ProfileTabVoice
        | types__root.ProfileTabLinks
        | types__root.ProfileTabGifs
    )

    PublicForward = (
        types__root.PublicForwardMessage
        | types__root.PublicForwardStory
    )

    QuickReply = types__root.QuickReply

    Reaction = (
        types__root.ReactionEmpty
        | types__root.ReactionEmoji
        | types__root.ReactionCustomEmoji
        | types__root.ReactionPaid
    )

    ReactionCount = types__root.ReactionCount

    ReactionNotificationsFrom = (
        types__root.ReactionNotificationsFromContacts
        | types__root.ReactionNotificationsFromAll
    )

    ReactionsNotifySettings = types__root.ReactionsNotifySettings

    ReadParticipantDate = types__root.ReadParticipantDate

    ReceivedNotifyMessage = types__root.ReceivedNotifyMessage

    RecentMeUrl = (
        types__root.RecentMeUrlUnknown
        | types__root.RecentMeUrlUser
        | types__root.RecentMeUrlChat
        | types__root.RecentMeUrlChatInvite
        | types__root.RecentMeUrlStickerSet
    )

    RecentStory = types__root.RecentStory

    ReplyMarkup = (
        types__root.ReplyKeyboardHide
        | types__root.ReplyKeyboardForceReply
        | types__root.ReplyKeyboardMarkup
        | types__root.ReplyInlineMarkup
    )

    ReportReason = (
        types__root.InputReportReasonSpam
        | types__root.InputReportReasonViolence
        | types__root.InputReportReasonPornography
        | types__root.InputReportReasonChildAbuse
        | types__root.InputReportReasonOther
        | types__root.InputReportReasonCopyright
        | types__root.InputReportReasonGeoIrrelevant
        | types__root.InputReportReasonFake
        | types__root.InputReportReasonIllegalDrugs
        | types__root.InputReportReasonPersonalDetails
    )

    ReportResult = (
        types__root.ReportResultChooseOption
        | types__root.ReportResultAddComment
        | types__root.ReportResultReported
    )

    RequestPeerType = (
        types__root.RequestPeerTypeUser
        | types__root.RequestPeerTypeChat
        | types__root.RequestPeerTypeBroadcast
        | types__root.RequestPeerTypeCreateBot
    )

    RequestedPeer = (
        types__root.RequestedPeerUser
        | types__root.RequestedPeerChat
        | types__root.RequestedPeerChannel
    )

    RequirementToContact = (
        types__root.RequirementToContactEmpty
        | types__root.RequirementToContactPremium
        | types__root.RequirementToContactPaidMessages
    )

    ResPQ = types_mtproto.ResPQ

    RestrictionReason = types__root.RestrictionReason

    RichMessage = types__root.RichMessage

    RichText = (
        types__root.TextEmpty
        | types__root.TextPlain
        | types__root.TextBold
        | types__root.TextItalic
        | types__root.TextUnderline
        | types__root.TextStrike
        | types__root.TextFixed
        | types__root.TextUrl
        | types__root.TextEmail
        | types__root.TextConcat
        | types__root.TextSubscript
        | types__root.TextSuperscript
        | types__root.TextMarked
        | types__root.TextPhone
        | types__root.TextImage
        | types__root.TextAnchor
        | types__root.TextMath
        | types__root.TextCustomEmoji
        | types__root.TextSpoiler
        | types__root.TextMention
        | types__root.TextHashtag
        | types__root.TextBotCommand
        | types__root.TextCashtag
        | types__root.TextAutoUrl
        | types__root.TextAutoEmail
        | types__root.TextAutoPhone
        | types__root.TextBankCard
        | types__root.TextMentionName
        | types__root.TextDate
        | types__root.TextDiff
    )

    RpcDropAnswer = (
        types_mtproto.RpcAnswerUnknown
        | types_mtproto.RpcAnswerDroppedRunning
        | types_mtproto.RpcAnswerDropped
    )

    RpcError = types_mtproto.RpcError

    SavedContact = types__root.SavedPhoneContact

    SavedDialog = (
        types__root.SavedDialog
        | types__root.MonoForumDialog
    )

    SavedReactionTag = types__root.SavedReactionTag

    SavedStarGift = types__root.SavedStarGift

    SearchPostsFlood = types__root.SearchPostsFlood

    SearchResultsCalendarPeriod = types__root.SearchResultsCalendarPeriod

    SearchResultsPosition = types__root.SearchResultPosition

    SecureCredentialsEncrypted = types__root.SecureCredentialsEncrypted

    SecureData = types__root.SecureData

    SecureFile = (
        types__root.SecureFileEmpty
        | types__root.SecureFile
    )

    SecurePasswordKdfAlgo = (
        types__root.SecurePasswordKdfAlgoUnknown
        | types__root.SecurePasswordKdfAlgoPBKDF2HMACSHA512iter100000
        | types__root.SecurePasswordKdfAlgoSHA512
    )

    SecurePlainData = (
        types__root.SecurePlainPhone
        | types__root.SecurePlainEmail
    )

    SecureRequiredType = (
        types__root.SecureRequiredType
        | types__root.SecureRequiredTypeOneOf
    )

    SecureSecretSettings = types__root.SecureSecretSettings

    SecureValue = types__root.SecureValue

    SecureValueError = (
        types__root.SecureValueErrorData
        | types__root.SecureValueErrorFrontSide
        | types__root.SecureValueErrorReverseSide
        | types__root.SecureValueErrorSelfie
        | types__root.SecureValueErrorFile
        | types__root.SecureValueErrorFiles
        | types__root.SecureValueError
        | types__root.SecureValueErrorTranslationFile
        | types__root.SecureValueErrorTranslationFiles
    )

    SecureValueHash = types__root.SecureValueHash

    SecureValueType = (
        types__root.SecureValueTypePersonalDetails
        | types__root.SecureValueTypePassport
        | types__root.SecureValueTypeDriverLicense
        | types__root.SecureValueTypeIdentityCard
        | types__root.SecureValueTypeInternalPassport
        | types__root.SecureValueTypeAddress
        | types__root.SecureValueTypeUtilityBill
        | types__root.SecureValueTypeBankStatement
        | types__root.SecureValueTypeRentalAgreement
        | types__root.SecureValueTypePassportRegistration
        | types__root.SecureValueTypeTemporaryRegistration
        | types__root.SecureValueTypePhone
        | types__root.SecureValueTypeEmail
    )

    SendAsPeer = types__root.SendAsPeer

    SendMessageAction = (
        types__root.SendMessageTypingAction
        | types__root.SendMessageCancelAction
        | types__root.SendMessageRecordVideoAction
        | types__root.SendMessageUploadVideoAction
        | types__root.SendMessageRecordAudioAction
        | types__root.SendMessageUploadAudioAction
        | types__root.SendMessageUploadPhotoAction
        | types__root.SendMessageUploadDocumentAction
        | types__root.SendMessageGeoLocationAction
        | types__root.SendMessageChooseContactAction
        | types__root.SendMessageGamePlayAction
        | types__root.SendMessageRecordRoundAction
        | types__root.SendMessageUploadRoundAction
        | types__root.SpeakingInGroupCallAction
        | types__root.SendMessageHistoryImportAction
        | types__root.SendMessageChooseStickerAction
        | types__root.SendMessageEmojiInteraction
        | types__root.SendMessageEmojiInteractionSeen
        | types__root.SendMessageTextDraftAction
        | types__root.InputSendMessageRichMessageDraftAction
        | types__root.SendMessageRichMessageDraftAction
    )

    ServerDHParams = (
        types_mtproto.ServerDHParamsFail
        | types_mtproto.ServerDHParamsOk
    )

    ServerDHInnerData = types_mtproto.ServerDHInnerData

    SetClientDHParamsAnswer = (
        types_mtproto.DhGenOk
        | types_mtproto.DhGenRetry
        | types_mtproto.DhGenFail
    )

    ShippingOption = types__root.ShippingOption

    SmsJob = types__root.SmsJob

    SponsoredMessage = types__root.SponsoredMessage

    SponsoredMessageReportOption = types__root.SponsoredMessageReportOption

    SponsoredPeer = types__root.SponsoredPeer

    StarGift = (
        types__root.StarGift
        | types__root.StarGiftUnique
    )

    StarGiftActiveAuctionState = types__root.StarGiftActiveAuctionState

    StarGiftAttribute = (
        types__root.StarGiftAttributeModel
        | types__root.StarGiftAttributePattern
        | types__root.StarGiftAttributeBackdrop
        | types__root.StarGiftAttributeOriginalDetails
    )

    StarGiftAttributeCounter = types__root.StarGiftAttributeCounter

    StarGiftAttributeId = (
        types__root.StarGiftAttributeIdModel
        | types__root.StarGiftAttributeIdPattern
        | types__root.StarGiftAttributeIdBackdrop
    )

    StarGiftAttributeRarity = (
        types__root.StarGiftAttributeRarity
        | types__root.StarGiftAttributeRarityUncommon
        | types__root.StarGiftAttributeRarityRare
        | types__root.StarGiftAttributeRarityEpic
        | types__root.StarGiftAttributeRarityLegendary
    )

    StarGiftAuctionAcquiredGift = types__root.StarGiftAuctionAcquiredGift

    StarGiftAuctionRound = (
        types__root.StarGiftAuctionRound
        | types__root.StarGiftAuctionRoundExtendable
    )

    StarGiftAuctionState = (
        types__root.StarGiftAuctionStateNotModified
        | types__root.StarGiftAuctionState
        | types__root.StarGiftAuctionStateFinished
    )

    StarGiftAuctionUserState = types__root.StarGiftAuctionUserState

    StarGiftBackground = types__root.StarGiftBackground

    StarGiftCollection = types__root.StarGiftCollection

    StarGiftUpgradePrice = types__root.StarGiftUpgradePrice

    StarRefProgram = types__root.StarRefProgram

    StarsAmount = (
        types__root.StarsAmount
        | types__root.StarsTonAmount
    )

    StarsGiftOption = types__root.StarsGiftOption

    StarsGiveawayOption = types__root.StarsGiveawayOption

    StarsGiveawayWinnersOption = types__root.StarsGiveawayWinnersOption

    StarsRating = types__root.StarsRating

    StarsRevenueStatus = types__root.StarsRevenueStatus

    StarsSubscription = types__root.StarsSubscription

    StarsSubscriptionPricing = types__root.StarsSubscriptionPricing

    StarsTopupOption = types__root.StarsTopupOption

    StarsTransaction = types__root.StarsTransaction

    StarsTransactionPeer = (
        types__root.StarsTransactionPeerUnsupported
        | types__root.StarsTransactionPeerAppStore
        | types__root.StarsTransactionPeerPlayMarket
        | types__root.StarsTransactionPeerPremiumBot
        | types__root.StarsTransactionPeerFragment
        | types__root.StarsTransactionPeer
        | types__root.StarsTransactionPeerAds
        | types__root.StarsTransactionPeerAPI
    )

    StatsAbsValueAndPrev = types__root.StatsAbsValueAndPrev

    StatsDateRangeDays = types__root.StatsDateRangeDays

    StatsGraph = (
        types__root.StatsGraphAsync
        | types__root.StatsGraphError
        | types__root.StatsGraph
    )

    StatsGroupTopAdmin = types__root.StatsGroupTopAdmin

    StatsGroupTopInviter = types__root.StatsGroupTopInviter

    StatsGroupTopPoster = types__root.StatsGroupTopPoster

    StatsPercentValue = types__root.StatsPercentValue

    StatsURL = types__root.StatsURL

    StickerKeyword = types__root.StickerKeyword

    StickerPack = types__root.StickerPack

    StickerSet = types__root.StickerSet

    StickerSetCovered = (
        types__root.StickerSetCovered
        | types__root.StickerSetMultiCovered
        | types__root.StickerSetFullCovered
        | types__root.StickerSetNoCovered
    )

    StoriesStealthMode = types__root.StoriesStealthMode

    StoryAlbum = types__root.StoryAlbum

    StoryFwdHeader = types__root.StoryFwdHeader

    StoryItem = (
        types__root.StoryItemDeleted
        | types__root.StoryItemSkipped
        | types__root.StoryItem
    )

    StoryReaction = (
        types__root.StoryReaction
        | types__root.StoryReactionPublicForward
        | types__root.StoryReactionPublicRepost
    )

    StoryView = (
        types__root.StoryView
        | types__root.StoryViewPublicForward
        | types__root.StoryViewPublicRepost
    )

    StoryViews = types__root.StoryViews

    SuggestedPost = types__root.SuggestedPost

    TextWithEntities = types__root.TextWithEntities

    Theme = types__root.Theme

    ThemeSettings = types__root.ThemeSettings

    Timezone = types__root.Timezone

    TodoCompletion = types__root.TodoCompletion

    TodoItem = types__root.TodoItem

    TodoList = types__root.TodoList

    TopPeer = types__root.TopPeer

    TopPeerCategory = (
        types__root.TopPeerCategoryBotsPM
        | types__root.TopPeerCategoryBotsInline
        | types__root.TopPeerCategoryCorrespondents
        | types__root.TopPeerCategoryGroups
        | types__root.TopPeerCategoryChannels
        | types__root.TopPeerCategoryPhoneCalls
        | types__root.TopPeerCategoryForwardUsers
        | types__root.TopPeerCategoryForwardChats
        | types__root.TopPeerCategoryBotsApp
        | types__root.TopPeerCategoryBotsGuestChat
    )

    TopPeerCategoryPeers = types__root.TopPeerCategoryPeers

    Update = (
        types__root.UpdateNewMessage
        | types__root.UpdateMessageID
        | types__root.UpdateDeleteMessages
        | types__root.UpdateUserTyping
        | types__root.UpdateChatUserTyping
        | types__root.UpdateChatParticipants
        | types__root.UpdateUserStatus
        | types__root.UpdateUserName
        | types__root.UpdateNewAuthorization
        | types__root.UpdateNewEncryptedMessage
        | types__root.UpdateEncryptedChatTyping
        | types__root.UpdateEncryption
        | types__root.UpdateEncryptedMessagesRead
        | types__root.UpdateChatParticipantAdd
        | types__root.UpdateChatParticipantDelete
        | types__root.UpdateDcOptions
        | types__root.UpdateNotifySettings
        | types__root.UpdateServiceNotification
        | types__root.UpdatePrivacy
        | types__root.UpdateUserPhone
        | types__root.UpdateReadHistoryInbox
        | types__root.UpdateReadHistoryOutbox
        | types__root.UpdateWebPage
        | types__root.UpdateReadMessagesContents
        | types__root.UpdateChannelTooLong
        | types__root.UpdateChannel
        | types__root.UpdateNewChannelMessage
        | types__root.UpdateReadChannelInbox
        | types__root.UpdateDeleteChannelMessages
        | types__root.UpdateChannelMessageViews
        | types__root.UpdateChatParticipantAdmin
        | types__root.UpdateNewStickerSet
        | types__root.UpdateStickerSetsOrder
        | types__root.UpdateStickerSets
        | types__root.UpdateSavedGifs
        | types__root.UpdateBotInlineQuery
        | types__root.UpdateBotInlineSend
        | types__root.UpdateEditChannelMessage
        | types__root.UpdateBotCallbackQuery
        | types__root.UpdateEditMessage
        | types__root.UpdateInlineBotCallbackQuery
        | types__root.UpdateReadChannelOutbox
        | types__root.UpdateDraftMessage
        | types__root.UpdateReadFeaturedStickers
        | types__root.UpdateRecentStickers
        | types__root.UpdateConfig
        | types__root.UpdatePtsChanged
        | types__root.UpdateChannelWebPage
        | types__root.UpdateDialogPinned
        | types__root.UpdatePinnedDialogs
        | types__root.UpdateBotWebhookJSON
        | types__root.UpdateBotWebhookJSONQuery
        | types__root.UpdateBotShippingQuery
        | types__root.UpdateBotPrecheckoutQuery
        | types__root.UpdatePhoneCall
        | types__root.UpdateLangPackTooLong
        | types__root.UpdateLangPack
        | types__root.UpdateFavedStickers
        | types__root.UpdateChannelReadMessagesContents
        | types__root.UpdateContactsReset
        | types__root.UpdateChannelAvailableMessages
        | types__root.UpdateDialogUnreadMark
        | types__root.UpdateMessagePoll
        | types__root.UpdateChatDefaultBannedRights
        | types__root.UpdateFolderPeers
        | types__root.UpdatePeerSettings
        | types__root.UpdatePeerLocated
        | types__root.UpdateNewScheduledMessage
        | types__root.UpdateDeleteScheduledMessages
        | types__root.UpdateTheme
        | types__root.UpdateGeoLiveViewed
        | types__root.UpdateLoginToken
        | types__root.UpdateMessagePollVote
        | types__root.UpdateDialogFilter
        | types__root.UpdateDialogFilterOrder
        | types__root.UpdateDialogFilters
        | types__root.UpdatePhoneCallSignalingData
        | types__root.UpdateChannelMessageForwards
        | types__root.UpdateReadChannelDiscussionInbox
        | types__root.UpdateReadChannelDiscussionOutbox
        | types__root.UpdatePeerBlocked
        | types__root.UpdateChannelUserTyping
        | types__root.UpdatePinnedMessages
        | types__root.UpdatePinnedChannelMessages
        | types__root.UpdateChat
        | types__root.UpdateGroupCallParticipants
        | types__root.UpdateGroupCall
        | types__root.UpdatePeerHistoryTTL
        | types__root.UpdateChatParticipant
        | types__root.UpdateChannelParticipant
        | types__root.UpdateBotStopped
        | types__root.UpdateGroupCallConnection
        | types__root.UpdateBotCommands
        | types__root.UpdatePendingJoinRequests
        | types__root.UpdateBotChatInviteRequester
        | types__root.UpdateMessageReactions
        | types__root.UpdateAttachMenuBots
        | types__root.UpdateWebViewResultSent
        | types__root.UpdateBotMenuButton
        | types__root.UpdateSavedRingtones
        | types__root.UpdateTranscribedAudio
        | types__root.UpdateReadFeaturedEmojiStickers
        | types__root.UpdateUserEmojiStatus
        | types__root.UpdateRecentEmojiStatuses
        | types__root.UpdateRecentReactions
        | types__root.UpdateMoveStickerSetToTop
        | types__root.UpdateMessageExtendedMedia
        | types__root.UpdateUser
        | types__root.UpdateAutoSaveSettings
        | types__root.UpdateStory
        | types__root.UpdateReadStories
        | types__root.UpdateStoryID
        | types__root.UpdateStoriesStealthMode
        | types__root.UpdateSentStoryReaction
        | types__root.UpdateBotChatBoost
        | types__root.UpdateChannelViewForumAsMessages
        | types__root.UpdatePeerWallpaper
        | types__root.UpdateBotMessageReaction
        | types__root.UpdateBotMessageReactions
        | types__root.UpdateSavedDialogPinned
        | types__root.UpdatePinnedSavedDialogs
        | types__root.UpdateSavedReactionTags
        | types__root.UpdateSmsJob
        | types__root.UpdateQuickReplies
        | types__root.UpdateNewQuickReply
        | types__root.UpdateDeleteQuickReply
        | types__root.UpdateQuickReplyMessage
        | types__root.UpdateDeleteQuickReplyMessages
        | types__root.UpdateBotBusinessConnect
        | types__root.UpdateBotNewBusinessMessage
        | types__root.UpdateBotEditBusinessMessage
        | types__root.UpdateBotDeleteBusinessMessage
        | types__root.UpdateNewStoryReaction
        | types__root.UpdateStarsBalance
        | types__root.UpdateBusinessBotCallbackQuery
        | types__root.UpdateStarsRevenueStatus
        | types__root.UpdateBotPurchasedPaidMedia
        | types__root.UpdatePaidReactionPrivacy
        | types__root.UpdateSentPhoneCode
        | types__root.UpdateGroupCallChainBlocks
        | types__root.UpdateReadMonoForumInbox
        | types__root.UpdateReadMonoForumOutbox
        | types__root.UpdateMonoForumNoPaidException
        | types__root.UpdateGroupCallMessage
        | types__root.UpdateGroupCallEncryptedMessage
        | types__root.UpdatePinnedForumTopic
        | types__root.UpdatePinnedForumTopics
        | types__root.UpdateDeleteGroupCallMessages
        | types__root.UpdateStarGiftAuctionState
        | types__root.UpdateStarGiftAuctionUserState
        | types__root.UpdateEmojiGameInfo
        | types__root.UpdateStarGiftCraftFail
        | types__root.UpdateChatParticipantRank
        | types__root.UpdateManagedBot
        | types__root.UpdateBotGuestChatQuery
        | types__root.UpdateAiComposeTones
        | types__root.UpdateJoinChatWebViewDecision
        | types__root.UpdateNewBotConnection
        | types__root.UpdateWebBrowserSettings
        | types__root.UpdateWebBrowserException
        | types__root.UpdateNewEphemeralMessage
        | types__root.UpdateDeleteEphemeralMessages
        | types__root.UpdateEditEphemeralMessage
        | types__root.UpdateBotStarsSubscription
    )

    Updates = (
        types__root.UpdatesTooLong
        | types__root.UpdateShortMessage
        | types__root.UpdateShortChatMessage
        | types__root.UpdateShort
        | types__root.UpdatesCombined
        | types__root.Updates
        | types__root.UpdateShortSentMessage
    )

    UrlAuthResult = (
        types__root.UrlAuthResultRequest
        | types__root.UrlAuthResultAccepted
        | types__root.UrlAuthResultDefault
    )

    User = (
        types__root.UserEmpty
        | types__root.User
    )

    UserFull = types__root.UserFull

    UserProfilePhoto = (
        types__root.UserProfilePhotoEmpty
        | types__root.UserProfilePhoto
    )

    UserStatus = (
        types__root.UserStatusEmpty
        | types__root.UserStatusOnline
        | types__root.UserStatusOffline
        | types__root.UserStatusRecently
        | types__root.UserStatusLastWeek
        | types__root.UserStatusLastMonth
    )

    Username = types__root.Username

    VideoSize = (
        types__root.VideoSize
        | types__root.VideoSizeEmojiMarkup
        | types__root.VideoSizeStickerMarkup
    )

    WallPaper = (
        types__root.WallPaper
        | types__root.WallPaperNoFile
    )

    WallPaperSettings = types__root.WallPaperSettings

    WebAuthorization = types__root.WebAuthorization

    WebDocument = (
        types__root.WebDocument
        | types__root.WebDocumentNoProxy
    )

    WebDomainException = types__root.WebDomainException

    WebPage = (
        types__root.WebPageEmpty
        | types__root.WebPagePending
        | types__root.WebPage
        | types__root.WebPageNotModified
    )

    WebPageAttribute = (
        types__root.WebPageAttributeTheme
        | types__root.WebPageAttributeStory
        | types__root.WebPageAttributeStickerSet
        | types__root.WebPageAttributeUniqueStarGift
        | types__root.WebPageAttributeStarGiftCollection
        | types__root.WebPageAttributeStarGiftAuction
        | types__root.WebPageAttributeAiComposeTone
    )

    WebViewMessageSent = types__root.WebViewMessageSent

    WebViewResult = types__root.WebViewResultUrl
