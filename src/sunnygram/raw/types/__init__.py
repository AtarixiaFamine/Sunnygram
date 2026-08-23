# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from the TL schema at layer 228. Do not edit by hand;
# run codegen/gen_tl.py instead.
"""The generated TL constructors.

A name in the root namespace is reachable straight from here, and a
namespace is reachable as an attribute, so raw.types.Message and
raw.types.messages.Messages both work. Either one imports only the
module it needs.

The mtproto attribute is not a TL namespace but the service schema,
which is kept apart so that speaking the protocol does not mean loading
the API.
"""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

__all__ = [
    "account",
    "aicompose",
    "auth",
    "bots",
    "channels",
    "chatlists",
    "communities",
    "contacts",
    "fragment",
    "help",
    "messages",
    "mtproto",
    "payments",
    "phone",
    "photos",
    "premium",
    "smsjobs",
    "stats",
    "stickers",
    "storage",
    "stories",
    "updates",
    "upload",
    "users",
    "AccountDaysTTL",
    "AiComposeTone",
    "AiComposeToneDefault",
    "AiComposeToneExample",
    "AttachMenuBot",
    "AttachMenuBotIcon",
    "AttachMenuBotIconColor",
    "AttachMenuBots",
    "AttachMenuBotsBot",
    "AttachMenuBotsNotModified",
    "AttachMenuPeerTypeBotPM",
    "AttachMenuPeerTypeBroadcast",
    "AttachMenuPeerTypeChat",
    "AttachMenuPeerTypePM",
    "AttachMenuPeerTypeSameBotPM",
    "AuctionBidLevel",
    "Authorization",
    "AutoDownloadSettings",
    "AutoSaveException",
    "AutoSaveSettings",
    "AvailableEffect",
    "AvailableReaction",
    "BankCardOpenUrl",
    "BaseThemeArctic",
    "BaseThemeClassic",
    "BaseThemeDay",
    "BaseThemeNight",
    "BaseThemeTinted",
    "Birthday",
    "Boost",
    "BotApp",
    "BotAppNotModified",
    "BotAppSettings",
    "BotBusinessConnection",
    "BotCommand",
    "BotCommandScopeChatAdmins",
    "BotCommandScopeChats",
    "BotCommandScopeDefault",
    "BotCommandScopePeer",
    "BotCommandScopePeerAdmins",
    "BotCommandScopePeerUser",
    "BotCommandScopeUsers",
    "BotInfo",
    "BotInlineMediaResult",
    "BotInlineMessageMediaAuto",
    "BotInlineMessageMediaContact",
    "BotInlineMessageMediaGeo",
    "BotInlineMessageMediaInvoice",
    "BotInlineMessageMediaVenue",
    "BotInlineMessageMediaWebPage",
    "BotInlineMessageRichMessage",
    "BotInlineMessageText",
    "BotInlineResult",
    "BotMenuButton",
    "BotMenuButtonCommands",
    "BotMenuButtonDefault",
    "BotPreviewMedia",
    "BotVerification",
    "BotVerifierSettings",
    "BusinessAwayMessage",
    "BusinessAwayMessageScheduleAlways",
    "BusinessAwayMessageScheduleCustom",
    "BusinessAwayMessageScheduleOutsideWorkHours",
    "BusinessBotRecipients",
    "BusinessBotRights",
    "BusinessChatLink",
    "BusinessGreetingMessage",
    "BusinessIntro",
    "BusinessLocation",
    "BusinessRecipients",
    "BusinessWeeklyOpen",
    "BusinessWorkHours",
    "CdnConfig",
    "CdnPublicKey",
    "Channel",
    "ChannelAdminLogEvent",
    "ChannelAdminLogEventActionChangeAbout",
    "ChannelAdminLogEventActionChangeAvailableReactions",
    "ChannelAdminLogEventActionChangeEmojiStatus",
    "ChannelAdminLogEventActionChangeEmojiStickerSet",
    "ChannelAdminLogEventActionChangeHistoryTTL",
    "ChannelAdminLogEventActionChangeLinkedChat",
    "ChannelAdminLogEventActionChangeLocation",
    "ChannelAdminLogEventActionChangePeerColor",
    "ChannelAdminLogEventActionChangePhoto",
    "ChannelAdminLogEventActionChangeProfilePeerColor",
    "ChannelAdminLogEventActionChangeStickerSet",
    "ChannelAdminLogEventActionChangeTitle",
    "ChannelAdminLogEventActionChangeUsername",
    "ChannelAdminLogEventActionChangeUsernames",
    "ChannelAdminLogEventActionChangeWallpaper",
    "ChannelAdminLogEventActionCreateTopic",
    "ChannelAdminLogEventActionDefaultBannedRights",
    "ChannelAdminLogEventActionDeleteMessage",
    "ChannelAdminLogEventActionDeleteTopic",
    "ChannelAdminLogEventActionDiscardGroupCall",
    "ChannelAdminLogEventActionEditMessage",
    "ChannelAdminLogEventActionEditTopic",
    "ChannelAdminLogEventActionExportedInviteDelete",
    "ChannelAdminLogEventActionExportedInviteEdit",
    "ChannelAdminLogEventActionExportedInviteRevoke",
    "ChannelAdminLogEventActionParticipantEditRank",
    "ChannelAdminLogEventActionParticipantInvite",
    "ChannelAdminLogEventActionParticipantJoin",
    "ChannelAdminLogEventActionParticipantJoinByInvite",
    "ChannelAdminLogEventActionParticipantJoinByRequest",
    "ChannelAdminLogEventActionParticipantLeave",
    "ChannelAdminLogEventActionParticipantMute",
    "ChannelAdminLogEventActionParticipantSubExtend",
    "ChannelAdminLogEventActionParticipantToggleAdmin",
    "ChannelAdminLogEventActionParticipantToggleBan",
    "ChannelAdminLogEventActionParticipantUnmute",
    "ChannelAdminLogEventActionParticipantVolume",
    "ChannelAdminLogEventActionPinTopic",
    "ChannelAdminLogEventActionSendMessage",
    "ChannelAdminLogEventActionStartGroupCall",
    "ChannelAdminLogEventActionStopPoll",
    "ChannelAdminLogEventActionToggleAntiSpam",
    "ChannelAdminLogEventActionToggleAutotranslation",
    "ChannelAdminLogEventActionToggleForum",
    "ChannelAdminLogEventActionToggleGroupCallSetting",
    "ChannelAdminLogEventActionToggleInvites",
    "ChannelAdminLogEventActionToggleNoForwards",
    "ChannelAdminLogEventActionTogglePreHistoryHidden",
    "ChannelAdminLogEventActionToggleSignatureProfiles",
    "ChannelAdminLogEventActionToggleSignatures",
    "ChannelAdminLogEventActionToggleSlowMode",
    "ChannelAdminLogEventActionUpdatePinned",
    "ChannelAdminLogEventsFilter",
    "ChannelForbidden",
    "ChannelFull",
    "ChannelLocation",
    "ChannelLocationEmpty",
    "ChannelMessagesFilter",
    "ChannelMessagesFilterEmpty",
    "ChannelParticipant",
    "ChannelParticipantAdmin",
    "ChannelParticipantBanned",
    "ChannelParticipantCreator",
    "ChannelParticipantLeft",
    "ChannelParticipantSelf",
    "ChannelParticipantsAdmins",
    "ChannelParticipantsBanned",
    "ChannelParticipantsBots",
    "ChannelParticipantsContacts",
    "ChannelParticipantsKicked",
    "ChannelParticipantsMentions",
    "ChannelParticipantsRecent",
    "ChannelParticipantsSearch",
    "Chat",
    "ChatAdminRights",
    "ChatAdminWithInvites",
    "ChatBannedRights",
    "ChatEmpty",
    "ChatForbidden",
    "ChatFull",
    "ChatInvite",
    "ChatInviteAlready",
    "ChatInviteExported",
    "ChatInviteImporter",
    "ChatInvitePeek",
    "ChatInvitePublicJoinRequests",
    "ChatOnlines",
    "ChatParticipant",
    "ChatParticipantAdmin",
    "ChatParticipantCreator",
    "ChatParticipants",
    "ChatParticipantsForbidden",
    "ChatPhoto",
    "ChatPhotoEmpty",
    "ChatReactionsAll",
    "ChatReactionsNone",
    "ChatReactionsSome",
    "ChatTheme",
    "ChatThemeUniqueGift",
    "CodeSettings",
    "Community",
    "CommunityForbidden",
    "CommunityFull",
    "CommunityPeer",
    "CommunityPeerRequest",
    "Config",
    "ConnectedBot",
    "ConnectedBotStarRef",
    "Contact",
    "ContactBirthday",
    "ContactStatus",
    "DataJSON",
    "DcOption",
    "DefaultHistoryTTL",
    "Dialog",
    "DialogCommunity",
    "DialogFilter",
    "DialogFilterChatlist",
    "DialogFilterDefault",
    "DialogFilterSuggested",
    "DialogFolder",
    "DialogPeer",
    "DialogPeerCommunity",
    "DialogPeerFolder",
    "DisallowedGiftsSettings",
    "Document",
    "DocumentAttributeAnimated",
    "DocumentAttributeAudio",
    "DocumentAttributeCustomEmoji",
    "DocumentAttributeFilename",
    "DocumentAttributeHasStickers",
    "DocumentAttributeImageSize",
    "DocumentAttributeSticker",
    "DocumentAttributeVideo",
    "DocumentEmpty",
    "DraftMessage",
    "DraftMessageEmpty",
    "EmailVerificationApple",
    "EmailVerificationCode",
    "EmailVerificationGoogle",
    "EmailVerifyPurposeLoginChange",
    "EmailVerifyPurposeLoginSetup",
    "EmailVerifyPurposePassport",
    "EmojiGroup",
    "EmojiGroupGreeting",
    "EmojiGroupPremium",
    "EmojiKeyword",
    "EmojiKeywordDeleted",
    "EmojiKeywordsDifference",
    "EmojiLanguage",
    "EmojiList",
    "EmojiListNotModified",
    "EmojiStatus",
    "EmojiStatusCollectible",
    "EmojiStatusEmpty",
    "EmojiURL",
    "EncryptedChat",
    "EncryptedChatDiscarded",
    "EncryptedChatEmpty",
    "EncryptedChatRequested",
    "EncryptedChatWaiting",
    "EncryptedFile",
    "EncryptedFileEmpty",
    "EncryptedMessage",
    "EncryptedMessageService",
    "EphemeralMessage",
    "Error",
    "ExportedChatlistInvite",
    "ExportedContactToken",
    "ExportedMessageLink",
    "ExportedStoryLink",
    "FactCheck",
    "FileHash",
    "Folder",
    "FolderPeer",
    "ForumTopic",
    "ForumTopicDeleted",
    "FoundStory",
    "Game",
    "GeoPoint",
    "GeoPointAddress",
    "GeoPointEmpty",
    "GlobalPrivacySettings",
    "GroupCall",
    "GroupCallDiscarded",
    "GroupCallDonor",
    "GroupCallMessage",
    "GroupCallParticipant",
    "GroupCallParticipantVideo",
    "GroupCallParticipantVideoSourceGroup",
    "GroupCallStreamChannel",
    "HighScore",
    "ImportedContact",
    "InlineBotSwitchPM",
    "InlineBotWebView",
    "InlineQueryPeerTypeBotPM",
    "InlineQueryPeerTypeBroadcast",
    "InlineQueryPeerTypeChat",
    "InlineQueryPeerTypeMegagroup",
    "InlineQueryPeerTypePM",
    "InlineQueryPeerTypeSameBotPM",
    "InputAiComposeToneDefault",
    "InputAiComposeToneID",
    "InputAiComposeToneSingleUse",
    "InputAiComposeToneSlug",
    "InputAppEvent",
    "InputBotAppID",
    "InputBotAppShortName",
    "InputBotInlineMessageGame",
    "InputBotInlineMessageID",
    "InputBotInlineMessageID64",
    "InputBotInlineMessageMediaAuto",
    "InputBotInlineMessageMediaContact",
    "InputBotInlineMessageMediaGeo",
    "InputBotInlineMessageMediaInvoice",
    "InputBotInlineMessageMediaVenue",
    "InputBotInlineMessageMediaWebPage",
    "InputBotInlineMessageRichMessage",
    "InputBotInlineMessageText",
    "InputBotInlineResult",
    "InputBotInlineResultDocument",
    "InputBotInlineResultGame",
    "InputBotInlineResultPhoto",
    "InputBusinessAwayMessage",
    "InputBusinessBotRecipients",
    "InputBusinessChatLink",
    "InputBusinessGreetingMessage",
    "InputBusinessIntro",
    "InputBusinessRecipients",
    "InputChannel",
    "InputChannelEmpty",
    "InputChannelFromMessage",
    "InputChatPhoto",
    "InputChatPhotoEmpty",
    "InputChatTheme",
    "InputChatThemeEmpty",
    "InputChatThemeUniqueGift",
    "InputChatUploadedPhoto",
    "InputChatlistDialogFilter",
    "InputCheckPasswordEmpty",
    "InputCheckPasswordSRP",
    "InputClientProxy",
    "InputCollectiblePhone",
    "InputCollectibleUsername",
    "InputDialogPeer",
    "InputDialogPeerCommunity",
    "InputDialogPeerFolder",
    "InputDocument",
    "InputDocumentEmpty",
    "InputDocumentFileLocation",
    "InputEmojiStatusCollectible",
    "InputEncryptedChat",
    "InputEncryptedFile",
    "InputEncryptedFileBigUploaded",
    "InputEncryptedFileEmpty",
    "InputEncryptedFileLocation",
    "InputEncryptedFileUploaded",
    "InputFile",
    "InputFileBig",
    "InputFileLocation",
    "InputFileStoryDocument",
    "InputFolderPeer",
    "InputGameID",
    "InputGameShortName",
    "InputGeoPoint",
    "InputGeoPointEmpty",
    "InputGroupCall",
    "InputGroupCallInviteMessage",
    "InputGroupCallSlug",
    "InputGroupCallStream",
    "InputInvoiceBusinessBotTransferStars",
    "InputInvoiceChatInviteSubscription",
    "InputInvoiceMessage",
    "InputInvoicePremiumAuthCode",
    "InputInvoicePremiumGiftCode",
    "InputInvoicePremiumGiftStars",
    "InputInvoiceSlug",
    "InputInvoiceStarGift",
    "InputInvoiceStarGiftAuctionBid",
    "InputInvoiceStarGiftDropOriginalDetails",
    "InputInvoiceStarGiftPrepaidUpgrade",
    "InputInvoiceStarGiftResale",
    "InputInvoiceStarGiftTransfer",
    "InputInvoiceStarGiftUpgrade",
    "InputInvoiceStars",
    "InputKeyboardButtonRequestPeer",
    "InputKeyboardButtonUrlAuth",
    "InputKeyboardButtonUserProfile",
    "InputMediaAreaChannelPost",
    "InputMediaAreaVenue",
    "InputMediaContact",
    "InputMediaDice",
    "InputMediaDocument",
    "InputMediaDocumentExternal",
    "InputMediaEmpty",
    "InputMediaGame",
    "InputMediaGeoLive",
    "InputMediaGeoPoint",
    "InputMediaInvoice",
    "InputMediaPaidMedia",
    "InputMediaPhoto",
    "InputMediaPhotoExternal",
    "InputMediaPoll",
    "InputMediaStakeDice",
    "InputMediaStory",
    "InputMediaTodo",
    "InputMediaUploadedDocument",
    "InputMediaUploadedPhoto",
    "InputMediaVenue",
    "InputMediaWebPage",
    "InputMessageCallbackQuery",
    "InputMessageEntityMentionName",
    "InputMessageID",
    "InputMessagePinned",
    "InputMessageReadMetric",
    "InputMessageReplyTo",
    "InputMessagesFilterChatPhotos",
    "InputMessagesFilterContacts",
    "InputMessagesFilterDocument",
    "InputMessagesFilterEmpty",
    "InputMessagesFilterGeo",
    "InputMessagesFilterGif",
    "InputMessagesFilterMusic",
    "InputMessagesFilterMyMentions",
    "InputMessagesFilterPhoneCalls",
    "InputMessagesFilterPhotoVideo",
    "InputMessagesFilterPhotos",
    "InputMessagesFilterPinned",
    "InputMessagesFilterPoll",
    "InputMessagesFilterRoundVideo",
    "InputMessagesFilterRoundVoice",
    "InputMessagesFilterUrl",
    "InputMessagesFilterVideo",
    "InputMessagesFilterVoice",
    "InputNotifyBroadcasts",
    "InputNotifyChats",
    "InputNotifyCommunity",
    "InputNotifyForumTopic",
    "InputNotifyPeer",
    "InputNotifyUsers",
    "InputPageBlockMap",
    "InputPasskeyCredentialFirebasePNV",
    "InputPasskeyCredentialPublicKey",
    "InputPasskeyResponseLogin",
    "InputPasskeyResponseRegister",
    "InputPaymentCredentials",
    "InputPaymentCredentialsApplePay",
    "InputPaymentCredentialsGooglePay",
    "InputPaymentCredentialsSaved",
    "InputPeerChannel",
    "InputPeerChannelFromMessage",
    "InputPeerChat",
    "InputPeerColorCollectible",
    "InputPeerEmpty",
    "InputPeerNotifySettings",
    "InputPeerPhotoFileLocation",
    "InputPeerSelf",
    "InputPeerUser",
    "InputPeerUserFromMessage",
    "InputPhoneCall",
    "InputPhoneContact",
    "InputPhoto",
    "InputPhotoEmpty",
    "InputPhotoFileLocation",
    "InputPhotoLegacyFileLocation",
    "InputPollAnswer",
    "InputPrivacyKeyAbout",
    "InputPrivacyKeyAddedByPhone",
    "InputPrivacyKeyBirthday",
    "InputPrivacyKeyChatInvite",
    "InputPrivacyKeyForwards",
    "InputPrivacyKeyNoPaidMessages",
    "InputPrivacyKeyPhoneCall",
    "InputPrivacyKeyPhoneNumber",
    "InputPrivacyKeyPhoneP2P",
    "InputPrivacyKeyProfilePhoto",
    "InputPrivacyKeySavedMusic",
    "InputPrivacyKeyStarGiftsAutoSave",
    "InputPrivacyKeyStatusTimestamp",
    "InputPrivacyKeyVoiceMessages",
    "InputPrivacyValueAllowAll",
    "InputPrivacyValueAllowBots",
    "InputPrivacyValueAllowChatParticipants",
    "InputPrivacyValueAllowCloseFriends",
    "InputPrivacyValueAllowContacts",
    "InputPrivacyValueAllowPremium",
    "InputPrivacyValueAllowUsers",
    "InputPrivacyValueDisallowAll",
    "InputPrivacyValueDisallowBots",
    "InputPrivacyValueDisallowChatParticipants",
    "InputPrivacyValueDisallowContacts",
    "InputPrivacyValueDisallowUsers",
    "InputQuickReplyShortcut",
    "InputQuickReplyShortcutId",
    "InputReplyToEphemeralMessage",
    "InputReplyToMessage",
    "InputReplyToMonoForum",
    "InputReplyToStory",
    "InputReportReasonChildAbuse",
    "InputReportReasonCopyright",
    "InputReportReasonFake",
    "InputReportReasonGeoIrrelevant",
    "InputReportReasonIllegalDrugs",
    "InputReportReasonOther",
    "InputReportReasonPersonalDetails",
    "InputReportReasonPornography",
    "InputReportReasonSpam",
    "InputReportReasonViolence",
    "InputRichFileDocument",
    "InputRichFilePhoto",
    "InputRichMessage",
    "InputRichMessageHTML",
    "InputRichMessageMarkdown",
    "InputSavedStarGiftChat",
    "InputSavedStarGiftSlug",
    "InputSavedStarGiftUser",
    "InputSecureFile",
    "InputSecureFileLocation",
    "InputSecureFileUploaded",
    "InputSecureValue",
    "InputSendMessageRichMessageDraftAction",
    "InputSingleMedia",
    "InputStarGiftAuction",
    "InputStarGiftAuctionSlug",
    "InputStarsTransaction",
    "InputStickerSetAnimatedEmoji",
    "InputStickerSetAnimatedEmojiAnimations",
    "InputStickerSetDice",
    "InputStickerSetEmojiChannelDefaultStatuses",
    "InputStickerSetEmojiDefaultStatuses",
    "InputStickerSetEmojiDefaultTopicIcons",
    "InputStickerSetEmojiGenericAnimations",
    "InputStickerSetEmpty",
    "InputStickerSetID",
    "InputStickerSetItem",
    "InputStickerSetPremiumGifts",
    "InputStickerSetShortName",
    "InputStickerSetThumb",
    "InputStickerSetTonGifts",
    "InputStickeredMediaDocument",
    "InputStickeredMediaPhoto",
    "InputStorePaymentAuthCode",
    "InputStorePaymentGiftPremium",
    "InputStorePaymentPremiumGiftCode",
    "InputStorePaymentPremiumGiveaway",
    "InputStorePaymentPremiumSubscription",
    "InputStorePaymentStarsGift",
    "InputStorePaymentStarsGiveaway",
    "InputStorePaymentStarsTopup",
    "InputTakeoutFileLocation",
    "InputTheme",
    "InputThemeSettings",
    "InputThemeSlug",
    "InputUser",
    "InputUserEmpty",
    "InputUserFromMessage",
    "InputUserSelf",
    "InputWallPaper",
    "InputWallPaperNoFile",
    "InputWallPaperSlug",
    "InputWebDocument",
    "InputWebFileAudioAlbumThumbLocation",
    "InputWebFileGeoPointLocation",
    "InputWebFileLocation",
    "Invoice",
    "JoinChatBotResultApproved",
    "JoinChatBotResultDeclined",
    "JoinChatBotResultQueued",
    "JoinChatBotResultWebView",
    "JsonArray",
    "JsonBool",
    "JsonNull",
    "JsonNumber",
    "JsonObject",
    "JsonObjectValue",
    "JsonString",
    "KeyboardButton",
    "KeyboardButtonBuy",
    "KeyboardButtonCallback",
    "KeyboardButtonCopy",
    "KeyboardButtonGame",
    "KeyboardButtonRequestGeoLocation",
    "KeyboardButtonRequestPeer",
    "KeyboardButtonRequestPhone",
    "KeyboardButtonRequestPoll",
    "KeyboardButtonRow",
    "KeyboardButtonSimpleWebView",
    "KeyboardButtonStyle",
    "KeyboardButtonSwitchInline",
    "KeyboardButtonUrl",
    "KeyboardButtonUrlAuth",
    "KeyboardButtonUserProfile",
    "KeyboardButtonWebView",
    "LabeledPrice",
    "LangPackDifference",
    "LangPackLanguage",
    "LangPackString",
    "LangPackStringDeleted",
    "LangPackStringPluralized",
    "MaskCoords",
    "MediaAreaChannelPost",
    "MediaAreaCoordinates",
    "MediaAreaGeoPoint",
    "MediaAreaStarGift",
    "MediaAreaSuggestedReaction",
    "MediaAreaUrl",
    "MediaAreaVenue",
    "MediaAreaWeather",
    "Message",
    "MessageActionBoostApply",
    "MessageActionBotAllowed",
    "MessageActionChangeCommunity",
    "MessageActionChangeCreator",
    "MessageActionChannelCreate",
    "MessageActionChannelMigrateFrom",
    "MessageActionChatAddUser",
    "MessageActionChatCreate",
    "MessageActionChatDeletePhoto",
    "MessageActionChatDeleteUser",
    "MessageActionChatEditPhoto",
    "MessageActionChatEditTitle",
    "MessageActionChatJoinedByLink",
    "MessageActionChatJoinedByRequest",
    "MessageActionChatMigrateTo",
    "MessageActionConferenceCall",
    "MessageActionContactSignUp",
    "MessageActionCustomAction",
    "MessageActionEmpty",
    "MessageActionGameScore",
    "MessageActionGeoProximityReached",
    "MessageActionGiftCode",
    "MessageActionGiftPremium",
    "MessageActionGiftStars",
    "MessageActionGiftTon",
    "MessageActionGiveawayLaunch",
    "MessageActionGiveawayResults",
    "MessageActionGroupCall",
    "MessageActionGroupCallScheduled",
    "MessageActionHistoryClear",
    "MessageActionInviteToGroupCall",
    "MessageActionManagedBotCreated",
    "MessageActionNewCreatorPending",
    "MessageActionNoForwardsRequest",
    "MessageActionNoForwardsToggle",
    "MessageActionPaidMessagesPrice",
    "MessageActionPaidMessagesRefunded",
    "MessageActionPaymentRefunded",
    "MessageActionPaymentSent",
    "MessageActionPaymentSentMe",
    "MessageActionPhoneCall",
    "MessageActionPinMessage",
    "MessageActionPollAppendAnswer",
    "MessageActionPollDeleteAnswer",
    "MessageActionPrizeStars",
    "MessageActionRequestedPeer",
    "MessageActionRequestedPeerSentMe",
    "MessageActionScreenshotTaken",
    "MessageActionSecureValuesSent",
    "MessageActionSecureValuesSentMe",
    "MessageActionSetChatTheme",
    "MessageActionSetChatWallPaper",
    "MessageActionSetMessagesTTL",
    "MessageActionStarGift",
    "MessageActionStarGiftPurchaseOffer",
    "MessageActionStarGiftPurchaseOfferDeclined",
    "MessageActionStarGiftUnique",
    "MessageActionSuggestBirthday",
    "MessageActionSuggestProfilePhoto",
    "MessageActionSuggestedPostApproval",
    "MessageActionSuggestedPostRefund",
    "MessageActionSuggestedPostSuccess",
    "MessageActionTodoAppendTasks",
    "MessageActionTodoCompletions",
    "MessageActionTopicCreate",
    "MessageActionTopicEdit",
    "MessageActionWebViewDataSent",
    "MessageActionWebViewDataSentMe",
    "MessageEmpty",
    "MessageEntityBankCard",
    "MessageEntityBlockquote",
    "MessageEntityBold",
    "MessageEntityBotCommand",
    "MessageEntityCashtag",
    "MessageEntityCode",
    "MessageEntityCustomEmoji",
    "MessageEntityDiffDelete",
    "MessageEntityDiffInsert",
    "MessageEntityDiffReplace",
    "MessageEntityEmail",
    "MessageEntityFormattedDate",
    "MessageEntityHashtag",
    "MessageEntityItalic",
    "MessageEntityMention",
    "MessageEntityMentionName",
    "MessageEntityPhone",
    "MessageEntityPre",
    "MessageEntitySpoiler",
    "MessageEntityStrike",
    "MessageEntityTextUrl",
    "MessageEntityUnderline",
    "MessageEntityUnknown",
    "MessageEntityUrl",
    "MessageExtendedMedia",
    "MessageExtendedMediaPreview",
    "MessageFwdHeader",
    "MessageMediaContact",
    "MessageMediaDice",
    "MessageMediaDocument",
    "MessageMediaEmpty",
    "MessageMediaGame",
    "MessageMediaGeo",
    "MessageMediaGeoLive",
    "MessageMediaGiveaway",
    "MessageMediaGiveawayResults",
    "MessageMediaInvoice",
    "MessageMediaPaidMedia",
    "MessageMediaPhoto",
    "MessageMediaPoll",
    "MessageMediaStory",
    "MessageMediaToDo",
    "MessageMediaUnsupported",
    "MessageMediaVenue",
    "MessageMediaVideoStream",
    "MessageMediaWebPage",
    "MessagePeerReaction",
    "MessagePeerVote",
    "MessagePeerVoteInputOption",
    "MessagePeerVoteMultiple",
    "MessageRange",
    "MessageReactions",
    "MessageReactor",
    "MessageReplies",
    "MessageReplyHeader",
    "MessageReplyStoryHeader",
    "MessageReportOption",
    "MessageService",
    "MessageViews",
    "MissingInvitee",
    "MonoForumDialog",
    "MyBoost",
    "NearestDc",
    "NotificationSoundDefault",
    "NotificationSoundLocal",
    "NotificationSoundNone",
    "NotificationSoundRingtone",
    "NotifyBroadcasts",
    "NotifyChats",
    "NotifyCommunity",
    "NotifyForumTopic",
    "NotifyPeer",
    "NotifyUsers",
    "Null",
    "OutboxReadDate",
    "Page",
    "PageBlockAnchor",
    "PageBlockAudio",
    "PageBlockAuthorDate",
    "PageBlockBlockquote",
    "PageBlockBlockquoteBlocks",
    "PageBlockChannel",
    "PageBlockCollage",
    "PageBlockCover",
    "PageBlockDetails",
    "PageBlockDivider",
    "PageBlockEmbed",
    "PageBlockEmbedPost",
    "PageBlockFooter",
    "PageBlockHeader",
    "PageBlockHeading1",
    "PageBlockHeading2",
    "PageBlockHeading3",
    "PageBlockHeading4",
    "PageBlockHeading5",
    "PageBlockHeading6",
    "PageBlockKicker",
    "PageBlockList",
    "PageBlockMap",
    "PageBlockMath",
    "PageBlockOrderedList",
    "PageBlockParagraph",
    "PageBlockPhoto",
    "PageBlockPreformatted",
    "PageBlockPullquote",
    "PageBlockRelatedArticles",
    "PageBlockSlideshow",
    "PageBlockSubheader",
    "PageBlockSubtitle",
    "PageBlockTable",
    "PageBlockThinking",
    "PageBlockTitle",
    "PageBlockUnsupported",
    "PageBlockVideo",
    "PageCaption",
    "PageListItemBlocks",
    "PageListItemText",
    "PageListOrderedItemBlocks",
    "PageListOrderedItemText",
    "PageRelatedArticle",
    "PageTableCell",
    "PageTableRow",
    "PaidReactionPrivacyAnonymous",
    "PaidReactionPrivacyDefault",
    "PaidReactionPrivacyPeer",
    "Passkey",
    "PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow",
    "PasswordKdfAlgoUnknown",
    "PaymentCharge",
    "PaymentFormMethod",
    "PaymentRequestedInfo",
    "PaymentSavedCredentialsCard",
    "PeerBlocked",
    "PeerChannel",
    "PeerChat",
    "PeerColor",
    "PeerColorCollectible",
    "PeerLocated",
    "PeerNotifySettings",
    "PeerSelfLocated",
    "PeerSettings",
    "PeerStories",
    "PeerUser",
    "PendingSuggestion",
    "PhoneCall",
    "PhoneCallAccepted",
    "PhoneCallDiscardReasonBusy",
    "PhoneCallDiscardReasonDisconnect",
    "PhoneCallDiscardReasonHangup",
    "PhoneCallDiscardReasonMigrateConferenceCall",
    "PhoneCallDiscardReasonMissed",
    "PhoneCallDiscarded",
    "PhoneCallEmpty",
    "PhoneCallProtocol",
    "PhoneCallRequested",
    "PhoneCallWaiting",
    "PhoneConnection",
    "PhoneConnectionWebrtc",
    "Photo",
    "PhotoCachedSize",
    "PhotoEmpty",
    "PhotoPathSize",
    "PhotoSize",
    "PhotoSizeEmpty",
    "PhotoSizeProgressive",
    "PhotoStrippedSize",
    "Poll",
    "PollAnswer",
    "PollAnswerVoters",
    "PollResults",
    "PopularContact",
    "PostAddress",
    "PostInteractionCountersMessage",
    "PostInteractionCountersStory",
    "PremiumGiftCodeOption",
    "PremiumSubscriptionOption",
    "PrepaidGiveaway",
    "PrepaidStarsGiveaway",
    "PrivacyKeyAbout",
    "PrivacyKeyAddedByPhone",
    "PrivacyKeyBirthday",
    "PrivacyKeyChatInvite",
    "PrivacyKeyForwards",
    "PrivacyKeyNoPaidMessages",
    "PrivacyKeyPhoneCall",
    "PrivacyKeyPhoneNumber",
    "PrivacyKeyPhoneP2P",
    "PrivacyKeyProfilePhoto",
    "PrivacyKeySavedMusic",
    "PrivacyKeyStarGiftsAutoSave",
    "PrivacyKeyStatusTimestamp",
    "PrivacyKeyVoiceMessages",
    "PrivacyValueAllowAll",
    "PrivacyValueAllowBots",
    "PrivacyValueAllowChatParticipants",
    "PrivacyValueAllowCloseFriends",
    "PrivacyValueAllowContacts",
    "PrivacyValueAllowPremium",
    "PrivacyValueAllowUsers",
    "PrivacyValueDisallowAll",
    "PrivacyValueDisallowBots",
    "PrivacyValueDisallowChatParticipants",
    "PrivacyValueDisallowContacts",
    "PrivacyValueDisallowUsers",
    "ProfileTabFiles",
    "ProfileTabGifs",
    "ProfileTabGifts",
    "ProfileTabLinks",
    "ProfileTabMedia",
    "ProfileTabMusic",
    "ProfileTabPosts",
    "ProfileTabVoice",
    "PublicForwardMessage",
    "PublicForwardStory",
    "QuickReply",
    "ReactionCount",
    "ReactionCustomEmoji",
    "ReactionEmoji",
    "ReactionEmpty",
    "ReactionNotificationsFromAll",
    "ReactionNotificationsFromContacts",
    "ReactionPaid",
    "ReactionsNotifySettings",
    "ReadParticipantDate",
    "ReceivedNotifyMessage",
    "RecentMeUrlChat",
    "RecentMeUrlChatInvite",
    "RecentMeUrlStickerSet",
    "RecentMeUrlUnknown",
    "RecentMeUrlUser",
    "RecentStory",
    "ReplyInlineMarkup",
    "ReplyKeyboardForceReply",
    "ReplyKeyboardHide",
    "ReplyKeyboardMarkup",
    "ReportResultAddComment",
    "ReportResultChooseOption",
    "ReportResultReported",
    "RequestPeerTypeBroadcast",
    "RequestPeerTypeChat",
    "RequestPeerTypeCreateBot",
    "RequestPeerTypeUser",
    "RequestedPeerChannel",
    "RequestedPeerChat",
    "RequestedPeerUser",
    "RequirementToContactEmpty",
    "RequirementToContactPaidMessages",
    "RequirementToContactPremium",
    "RestrictionReason",
    "RichMessage",
    "SavedDialog",
    "SavedPhoneContact",
    "SavedReactionTag",
    "SavedStarGift",
    "SearchPostsFlood",
    "SearchResultPosition",
    "SearchResultsCalendarPeriod",
    "SecureCredentialsEncrypted",
    "SecureData",
    "SecureFile",
    "SecureFileEmpty",
    "SecurePasswordKdfAlgoPBKDF2HMACSHA512iter100000",
    "SecurePasswordKdfAlgoSHA512",
    "SecurePasswordKdfAlgoUnknown",
    "SecurePlainEmail",
    "SecurePlainPhone",
    "SecureRequiredType",
    "SecureRequiredTypeOneOf",
    "SecureSecretSettings",
    "SecureValue",
    "SecureValueError",
    "SecureValueErrorData",
    "SecureValueErrorFile",
    "SecureValueErrorFiles",
    "SecureValueErrorFrontSide",
    "SecureValueErrorReverseSide",
    "SecureValueErrorSelfie",
    "SecureValueErrorTranslationFile",
    "SecureValueErrorTranslationFiles",
    "SecureValueHash",
    "SecureValueTypeAddress",
    "SecureValueTypeBankStatement",
    "SecureValueTypeDriverLicense",
    "SecureValueTypeEmail",
    "SecureValueTypeIdentityCard",
    "SecureValueTypeInternalPassport",
    "SecureValueTypePassport",
    "SecureValueTypePassportRegistration",
    "SecureValueTypePersonalDetails",
    "SecureValueTypePhone",
    "SecureValueTypeRentalAgreement",
    "SecureValueTypeTemporaryRegistration",
    "SecureValueTypeUtilityBill",
    "SendAsPeer",
    "SendMessageCancelAction",
    "SendMessageChooseContactAction",
    "SendMessageChooseStickerAction",
    "SendMessageEmojiInteraction",
    "SendMessageEmojiInteractionSeen",
    "SendMessageGamePlayAction",
    "SendMessageGeoLocationAction",
    "SendMessageHistoryImportAction",
    "SendMessageRecordAudioAction",
    "SendMessageRecordRoundAction",
    "SendMessageRecordVideoAction",
    "SendMessageRichMessageDraftAction",
    "SendMessageTextDraftAction",
    "SendMessageTypingAction",
    "SendMessageUploadAudioAction",
    "SendMessageUploadDocumentAction",
    "SendMessageUploadPhotoAction",
    "SendMessageUploadRoundAction",
    "SendMessageUploadVideoAction",
    "ShippingOption",
    "SmsJob",
    "SpeakingInGroupCallAction",
    "SponsoredMessage",
    "SponsoredMessageReportOption",
    "SponsoredPeer",
    "StarGift",
    "StarGiftActiveAuctionState",
    "StarGiftAttributeBackdrop",
    "StarGiftAttributeCounter",
    "StarGiftAttributeIdBackdrop",
    "StarGiftAttributeIdModel",
    "StarGiftAttributeIdPattern",
    "StarGiftAttributeModel",
    "StarGiftAttributeOriginalDetails",
    "StarGiftAttributePattern",
    "StarGiftAttributeRarity",
    "StarGiftAttributeRarityEpic",
    "StarGiftAttributeRarityLegendary",
    "StarGiftAttributeRarityRare",
    "StarGiftAttributeRarityUncommon",
    "StarGiftAuctionAcquiredGift",
    "StarGiftAuctionRound",
    "StarGiftAuctionRoundExtendable",
    "StarGiftAuctionState",
    "StarGiftAuctionStateFinished",
    "StarGiftAuctionStateNotModified",
    "StarGiftAuctionUserState",
    "StarGiftBackground",
    "StarGiftCollection",
    "StarGiftUnique",
    "StarGiftUpgradePrice",
    "StarRefProgram",
    "StarsAmount",
    "StarsGiftOption",
    "StarsGiveawayOption",
    "StarsGiveawayWinnersOption",
    "StarsRating",
    "StarsRevenueStatus",
    "StarsSubscription",
    "StarsSubscriptionPricing",
    "StarsTonAmount",
    "StarsTopupOption",
    "StarsTransaction",
    "StarsTransactionPeer",
    "StarsTransactionPeerAPI",
    "StarsTransactionPeerAds",
    "StarsTransactionPeerAppStore",
    "StarsTransactionPeerFragment",
    "StarsTransactionPeerPlayMarket",
    "StarsTransactionPeerPremiumBot",
    "StarsTransactionPeerUnsupported",
    "StatsAbsValueAndPrev",
    "StatsDateRangeDays",
    "StatsGraph",
    "StatsGraphAsync",
    "StatsGraphError",
    "StatsGroupTopAdmin",
    "StatsGroupTopInviter",
    "StatsGroupTopPoster",
    "StatsPercentValue",
    "StatsURL",
    "StickerKeyword",
    "StickerPack",
    "StickerSet",
    "StickerSetCovered",
    "StickerSetFullCovered",
    "StickerSetMultiCovered",
    "StickerSetNoCovered",
    "StoriesStealthMode",
    "StoryAlbum",
    "StoryFwdHeader",
    "StoryItem",
    "StoryItemDeleted",
    "StoryItemSkipped",
    "StoryReaction",
    "StoryReactionPublicForward",
    "StoryReactionPublicRepost",
    "StoryView",
    "StoryViewPublicForward",
    "StoryViewPublicRepost",
    "StoryViews",
    "SuggestedPost",
    "TextAnchor",
    "TextAutoEmail",
    "TextAutoPhone",
    "TextAutoUrl",
    "TextBankCard",
    "TextBold",
    "TextBotCommand",
    "TextCashtag",
    "TextConcat",
    "TextCustomEmoji",
    "TextDate",
    "TextDiff",
    "TextEmail",
    "TextEmpty",
    "TextFixed",
    "TextHashtag",
    "TextImage",
    "TextItalic",
    "TextMarked",
    "TextMath",
    "TextMention",
    "TextMentionName",
    "TextPhone",
    "TextPlain",
    "TextSpoiler",
    "TextStrike",
    "TextSubscript",
    "TextSuperscript",
    "TextUnderline",
    "TextUrl",
    "TextWithEntities",
    "Theme",
    "ThemeSettings",
    "Timezone",
    "TodoCompletion",
    "TodoItem",
    "TodoList",
    "TopPeer",
    "TopPeerCategoryBotsApp",
    "TopPeerCategoryBotsGuestChat",
    "TopPeerCategoryBotsInline",
    "TopPeerCategoryBotsPM",
    "TopPeerCategoryChannels",
    "TopPeerCategoryCorrespondents",
    "TopPeerCategoryForwardChats",
    "TopPeerCategoryForwardUsers",
    "TopPeerCategoryGroups",
    "TopPeerCategoryPeers",
    "TopPeerCategoryPhoneCalls",
    "UpdateAiComposeTones",
    "UpdateAttachMenuBots",
    "UpdateAutoSaveSettings",
    "UpdateBotBusinessConnect",
    "UpdateBotCallbackQuery",
    "UpdateBotChatBoost",
    "UpdateBotChatInviteRequester",
    "UpdateBotCommands",
    "UpdateBotDeleteBusinessMessage",
    "UpdateBotEditBusinessMessage",
    "UpdateBotGuestChatQuery",
    "UpdateBotInlineQuery",
    "UpdateBotInlineSend",
    "UpdateBotMenuButton",
    "UpdateBotMessageReaction",
    "UpdateBotMessageReactions",
    "UpdateBotNewBusinessMessage",
    "UpdateBotPrecheckoutQuery",
    "UpdateBotPurchasedPaidMedia",
    "UpdateBotShippingQuery",
    "UpdateBotStarsSubscription",
    "UpdateBotStopped",
    "UpdateBotWebhookJSON",
    "UpdateBotWebhookJSONQuery",
    "UpdateBusinessBotCallbackQuery",
    "UpdateChannel",
    "UpdateChannelAvailableMessages",
    "UpdateChannelMessageForwards",
    "UpdateChannelMessageViews",
    "UpdateChannelParticipant",
    "UpdateChannelReadMessagesContents",
    "UpdateChannelTooLong",
    "UpdateChannelUserTyping",
    "UpdateChannelViewForumAsMessages",
    "UpdateChannelWebPage",
    "UpdateChat",
    "UpdateChatDefaultBannedRights",
    "UpdateChatParticipant",
    "UpdateChatParticipantAdd",
    "UpdateChatParticipantAdmin",
    "UpdateChatParticipantDelete",
    "UpdateChatParticipantRank",
    "UpdateChatParticipants",
    "UpdateChatUserTyping",
    "UpdateConfig",
    "UpdateContactsReset",
    "UpdateDcOptions",
    "UpdateDeleteChannelMessages",
    "UpdateDeleteEphemeralMessages",
    "UpdateDeleteGroupCallMessages",
    "UpdateDeleteMessages",
    "UpdateDeleteQuickReply",
    "UpdateDeleteQuickReplyMessages",
    "UpdateDeleteScheduledMessages",
    "UpdateDialogFilter",
    "UpdateDialogFilterOrder",
    "UpdateDialogFilters",
    "UpdateDialogPinned",
    "UpdateDialogUnreadMark",
    "UpdateDraftMessage",
    "UpdateEditChannelMessage",
    "UpdateEditEphemeralMessage",
    "UpdateEditMessage",
    "UpdateEmojiGameInfo",
    "UpdateEncryptedChatTyping",
    "UpdateEncryptedMessagesRead",
    "UpdateEncryption",
    "UpdateFavedStickers",
    "UpdateFolderPeers",
    "UpdateGeoLiveViewed",
    "UpdateGroupCall",
    "UpdateGroupCallChainBlocks",
    "UpdateGroupCallConnection",
    "UpdateGroupCallEncryptedMessage",
    "UpdateGroupCallMessage",
    "UpdateGroupCallParticipants",
    "UpdateInlineBotCallbackQuery",
    "UpdateJoinChatWebViewDecision",
    "UpdateLangPack",
    "UpdateLangPackTooLong",
    "UpdateLoginToken",
    "UpdateManagedBot",
    "UpdateMessageExtendedMedia",
    "UpdateMessageID",
    "UpdateMessagePoll",
    "UpdateMessagePollVote",
    "UpdateMessageReactions",
    "UpdateMonoForumNoPaidException",
    "UpdateMoveStickerSetToTop",
    "UpdateNewAuthorization",
    "UpdateNewBotConnection",
    "UpdateNewChannelMessage",
    "UpdateNewEncryptedMessage",
    "UpdateNewEphemeralMessage",
    "UpdateNewMessage",
    "UpdateNewQuickReply",
    "UpdateNewScheduledMessage",
    "UpdateNewStickerSet",
    "UpdateNewStoryReaction",
    "UpdateNotifySettings",
    "UpdatePaidReactionPrivacy",
    "UpdatePeerBlocked",
    "UpdatePeerHistoryTTL",
    "UpdatePeerLocated",
    "UpdatePeerSettings",
    "UpdatePeerWallpaper",
    "UpdatePendingJoinRequests",
    "UpdatePhoneCall",
    "UpdatePhoneCallSignalingData",
    "UpdatePinnedChannelMessages",
    "UpdatePinnedDialogs",
    "UpdatePinnedForumTopic",
    "UpdatePinnedForumTopics",
    "UpdatePinnedMessages",
    "UpdatePinnedSavedDialogs",
    "UpdatePrivacy",
    "UpdatePtsChanged",
    "UpdateQuickReplies",
    "UpdateQuickReplyMessage",
    "UpdateReadChannelDiscussionInbox",
    "UpdateReadChannelDiscussionOutbox",
    "UpdateReadChannelInbox",
    "UpdateReadChannelOutbox",
    "UpdateReadFeaturedEmojiStickers",
    "UpdateReadFeaturedStickers",
    "UpdateReadHistoryInbox",
    "UpdateReadHistoryOutbox",
    "UpdateReadMessagesContents",
    "UpdateReadMonoForumInbox",
    "UpdateReadMonoForumOutbox",
    "UpdateReadStories",
    "UpdateRecentEmojiStatuses",
    "UpdateRecentReactions",
    "UpdateRecentStickers",
    "UpdateSavedDialogPinned",
    "UpdateSavedGifs",
    "UpdateSavedReactionTags",
    "UpdateSavedRingtones",
    "UpdateSentPhoneCode",
    "UpdateSentStoryReaction",
    "UpdateServiceNotification",
    "UpdateShort",
    "UpdateShortChatMessage",
    "UpdateShortMessage",
    "UpdateShortSentMessage",
    "UpdateSmsJob",
    "UpdateStarGiftAuctionState",
    "UpdateStarGiftAuctionUserState",
    "UpdateStarGiftCraftFail",
    "UpdateStarsBalance",
    "UpdateStarsRevenueStatus",
    "UpdateStickerSets",
    "UpdateStickerSetsOrder",
    "UpdateStoriesStealthMode",
    "UpdateStory",
    "UpdateStoryID",
    "UpdateTheme",
    "UpdateTranscribedAudio",
    "UpdateUser",
    "UpdateUserEmojiStatus",
    "UpdateUserName",
    "UpdateUserPhone",
    "UpdateUserStatus",
    "UpdateUserTyping",
    "UpdateWebBrowserException",
    "UpdateWebBrowserSettings",
    "UpdateWebPage",
    "UpdateWebViewResultSent",
    "Updates",
    "UpdatesCombined",
    "UpdatesTooLong",
    "UrlAuthResultAccepted",
    "UrlAuthResultDefault",
    "UrlAuthResultRequest",
    "User",
    "UserEmpty",
    "UserFull",
    "UserProfilePhoto",
    "UserProfilePhotoEmpty",
    "UserStatusEmpty",
    "UserStatusLastMonth",
    "UserStatusLastWeek",
    "UserStatusOffline",
    "UserStatusOnline",
    "UserStatusRecently",
    "Username",
    "VideoSize",
    "VideoSizeEmojiMarkup",
    "VideoSizeStickerMarkup",
    "WallPaper",
    "WallPaperNoFile",
    "WallPaperSettings",
    "WebAuthorization",
    "WebDocument",
    "WebDocumentNoProxy",
    "WebDomainException",
    "WebPage",
    "WebPageAttributeAiComposeTone",
    "WebPageAttributeStarGiftAuction",
    "WebPageAttributeStarGiftCollection",
    "WebPageAttributeStickerSet",
    "WebPageAttributeStory",
    "WebPageAttributeTheme",
    "WebPageAttributeUniqueStarGift",
    "WebPageEmpty",
    "WebPageNotModified",
    "WebPagePending",
    "WebViewMessageSent",
    "WebViewResultUrl",
]

if TYPE_CHECKING:
    from . import account as account
    from . import aicompose as aicompose
    from . import auth as auth
    from . import bots as bots
    from . import channels as channels
    from . import chatlists as chatlists
    from . import communities as communities
    from . import contacts as contacts
    from . import fragment as fragment
    from . import help as help
    from . import messages as messages
    from . import mtproto as mtproto
    from . import payments as payments
    from . import phone as phone
    from . import photos as photos
    from . import premium as premium
    from . import smsjobs as smsjobs
    from . import stats as stats
    from . import stickers as stickers
    from . import storage as storage
    from . import stories as stories
    from . import updates as updates
    from . import upload as upload
    from . import users as users
    from ._root import AccountDaysTTL as AccountDaysTTL
    from ._root import AiComposeTone as AiComposeTone
    from ._root import AiComposeToneDefault as AiComposeToneDefault
    from ._root import AiComposeToneExample as AiComposeToneExample
    from ._root import AttachMenuBot as AttachMenuBot
    from ._root import AttachMenuBotIcon as AttachMenuBotIcon
    from ._root import AttachMenuBotIconColor as AttachMenuBotIconColor
    from ._root import AttachMenuBots as AttachMenuBots
    from ._root import AttachMenuBotsBot as AttachMenuBotsBot
    from ._root import AttachMenuBotsNotModified as AttachMenuBotsNotModified
    from ._root import AttachMenuPeerTypeBotPM as AttachMenuPeerTypeBotPM
    from ._root import AttachMenuPeerTypeBroadcast as AttachMenuPeerTypeBroadcast
    from ._root import AttachMenuPeerTypeChat as AttachMenuPeerTypeChat
    from ._root import AttachMenuPeerTypePM as AttachMenuPeerTypePM
    from ._root import AttachMenuPeerTypeSameBotPM as AttachMenuPeerTypeSameBotPM
    from ._root import AuctionBidLevel as AuctionBidLevel
    from ._root import Authorization as Authorization
    from ._root import AutoDownloadSettings as AutoDownloadSettings
    from ._root import AutoSaveException as AutoSaveException
    from ._root import AutoSaveSettings as AutoSaveSettings
    from ._root import AvailableEffect as AvailableEffect
    from ._root import AvailableReaction as AvailableReaction
    from ._root import BankCardOpenUrl as BankCardOpenUrl
    from ._root import BaseThemeArctic as BaseThemeArctic
    from ._root import BaseThemeClassic as BaseThemeClassic
    from ._root import BaseThemeDay as BaseThemeDay
    from ._root import BaseThemeNight as BaseThemeNight
    from ._root import BaseThemeTinted as BaseThemeTinted
    from ._root import Birthday as Birthday
    from ._root import Boost as Boost
    from ._root import BotApp as BotApp
    from ._root import BotAppNotModified as BotAppNotModified
    from ._root import BotAppSettings as BotAppSettings
    from ._root import BotBusinessConnection as BotBusinessConnection
    from ._root import BotCommand as BotCommand
    from ._root import BotCommandScopeChatAdmins as BotCommandScopeChatAdmins
    from ._root import BotCommandScopeChats as BotCommandScopeChats
    from ._root import BotCommandScopeDefault as BotCommandScopeDefault
    from ._root import BotCommandScopePeer as BotCommandScopePeer
    from ._root import BotCommandScopePeerAdmins as BotCommandScopePeerAdmins
    from ._root import BotCommandScopePeerUser as BotCommandScopePeerUser
    from ._root import BotCommandScopeUsers as BotCommandScopeUsers
    from ._root import BotInfo as BotInfo
    from ._root import BotInlineMediaResult as BotInlineMediaResult
    from ._root import BotInlineMessageMediaAuto as BotInlineMessageMediaAuto
    from ._root import BotInlineMessageMediaContact as BotInlineMessageMediaContact
    from ._root import BotInlineMessageMediaGeo as BotInlineMessageMediaGeo
    from ._root import BotInlineMessageMediaInvoice as BotInlineMessageMediaInvoice
    from ._root import BotInlineMessageMediaVenue as BotInlineMessageMediaVenue
    from ._root import BotInlineMessageMediaWebPage as BotInlineMessageMediaWebPage
    from ._root import BotInlineMessageRichMessage as BotInlineMessageRichMessage
    from ._root import BotInlineMessageText as BotInlineMessageText
    from ._root import BotInlineResult as BotInlineResult
    from ._root import BotMenuButton as BotMenuButton
    from ._root import BotMenuButtonCommands as BotMenuButtonCommands
    from ._root import BotMenuButtonDefault as BotMenuButtonDefault
    from ._root import BotPreviewMedia as BotPreviewMedia
    from ._root import BotVerification as BotVerification
    from ._root import BotVerifierSettings as BotVerifierSettings
    from ._root import BusinessAwayMessage as BusinessAwayMessage
    from ._root import BusinessAwayMessageScheduleAlways as BusinessAwayMessageScheduleAlways
    from ._root import BusinessAwayMessageScheduleCustom as BusinessAwayMessageScheduleCustom
    from ._root import BusinessAwayMessageScheduleOutsideWorkHours as BusinessAwayMessageScheduleOutsideWorkHours
    from ._root import BusinessBotRecipients as BusinessBotRecipients
    from ._root import BusinessBotRights as BusinessBotRights
    from ._root import BusinessChatLink as BusinessChatLink
    from ._root import BusinessGreetingMessage as BusinessGreetingMessage
    from ._root import BusinessIntro as BusinessIntro
    from ._root import BusinessLocation as BusinessLocation
    from ._root import BusinessRecipients as BusinessRecipients
    from ._root import BusinessWeeklyOpen as BusinessWeeklyOpen
    from ._root import BusinessWorkHours as BusinessWorkHours
    from ._root import CdnConfig as CdnConfig
    from ._root import CdnPublicKey as CdnPublicKey
    from ._root import Channel as Channel
    from ._root import ChannelAdminLogEvent as ChannelAdminLogEvent
    from ._root import ChannelAdminLogEventActionChangeAbout as ChannelAdminLogEventActionChangeAbout
    from ._root import ChannelAdminLogEventActionChangeAvailableReactions as ChannelAdminLogEventActionChangeAvailableReactions
    from ._root import ChannelAdminLogEventActionChangeEmojiStatus as ChannelAdminLogEventActionChangeEmojiStatus
    from ._root import ChannelAdminLogEventActionChangeEmojiStickerSet as ChannelAdminLogEventActionChangeEmojiStickerSet
    from ._root import ChannelAdminLogEventActionChangeHistoryTTL as ChannelAdminLogEventActionChangeHistoryTTL
    from ._root import ChannelAdminLogEventActionChangeLinkedChat as ChannelAdminLogEventActionChangeLinkedChat
    from ._root import ChannelAdminLogEventActionChangeLocation as ChannelAdminLogEventActionChangeLocation
    from ._root import ChannelAdminLogEventActionChangePeerColor as ChannelAdminLogEventActionChangePeerColor
    from ._root import ChannelAdminLogEventActionChangePhoto as ChannelAdminLogEventActionChangePhoto
    from ._root import ChannelAdminLogEventActionChangeProfilePeerColor as ChannelAdminLogEventActionChangeProfilePeerColor
    from ._root import ChannelAdminLogEventActionChangeStickerSet as ChannelAdminLogEventActionChangeStickerSet
    from ._root import ChannelAdminLogEventActionChangeTitle as ChannelAdminLogEventActionChangeTitle
    from ._root import ChannelAdminLogEventActionChangeUsername as ChannelAdminLogEventActionChangeUsername
    from ._root import ChannelAdminLogEventActionChangeUsernames as ChannelAdminLogEventActionChangeUsernames
    from ._root import ChannelAdminLogEventActionChangeWallpaper as ChannelAdminLogEventActionChangeWallpaper
    from ._root import ChannelAdminLogEventActionCreateTopic as ChannelAdminLogEventActionCreateTopic
    from ._root import ChannelAdminLogEventActionDefaultBannedRights as ChannelAdminLogEventActionDefaultBannedRights
    from ._root import ChannelAdminLogEventActionDeleteMessage as ChannelAdminLogEventActionDeleteMessage
    from ._root import ChannelAdminLogEventActionDeleteTopic as ChannelAdminLogEventActionDeleteTopic
    from ._root import ChannelAdminLogEventActionDiscardGroupCall as ChannelAdminLogEventActionDiscardGroupCall
    from ._root import ChannelAdminLogEventActionEditMessage as ChannelAdminLogEventActionEditMessage
    from ._root import ChannelAdminLogEventActionEditTopic as ChannelAdminLogEventActionEditTopic
    from ._root import ChannelAdminLogEventActionExportedInviteDelete as ChannelAdminLogEventActionExportedInviteDelete
    from ._root import ChannelAdminLogEventActionExportedInviteEdit as ChannelAdminLogEventActionExportedInviteEdit
    from ._root import ChannelAdminLogEventActionExportedInviteRevoke as ChannelAdminLogEventActionExportedInviteRevoke
    from ._root import ChannelAdminLogEventActionParticipantEditRank as ChannelAdminLogEventActionParticipantEditRank
    from ._root import ChannelAdminLogEventActionParticipantInvite as ChannelAdminLogEventActionParticipantInvite
    from ._root import ChannelAdminLogEventActionParticipantJoin as ChannelAdminLogEventActionParticipantJoin
    from ._root import ChannelAdminLogEventActionParticipantJoinByInvite as ChannelAdminLogEventActionParticipantJoinByInvite
    from ._root import ChannelAdminLogEventActionParticipantJoinByRequest as ChannelAdminLogEventActionParticipantJoinByRequest
    from ._root import ChannelAdminLogEventActionParticipantLeave as ChannelAdminLogEventActionParticipantLeave
    from ._root import ChannelAdminLogEventActionParticipantMute as ChannelAdminLogEventActionParticipantMute
    from ._root import ChannelAdminLogEventActionParticipantSubExtend as ChannelAdminLogEventActionParticipantSubExtend
    from ._root import ChannelAdminLogEventActionParticipantToggleAdmin as ChannelAdminLogEventActionParticipantToggleAdmin
    from ._root import ChannelAdminLogEventActionParticipantToggleBan as ChannelAdminLogEventActionParticipantToggleBan
    from ._root import ChannelAdminLogEventActionParticipantUnmute as ChannelAdminLogEventActionParticipantUnmute
    from ._root import ChannelAdminLogEventActionParticipantVolume as ChannelAdminLogEventActionParticipantVolume
    from ._root import ChannelAdminLogEventActionPinTopic as ChannelAdminLogEventActionPinTopic
    from ._root import ChannelAdminLogEventActionSendMessage as ChannelAdminLogEventActionSendMessage
    from ._root import ChannelAdminLogEventActionStartGroupCall as ChannelAdminLogEventActionStartGroupCall
    from ._root import ChannelAdminLogEventActionStopPoll as ChannelAdminLogEventActionStopPoll
    from ._root import ChannelAdminLogEventActionToggleAntiSpam as ChannelAdminLogEventActionToggleAntiSpam
    from ._root import ChannelAdminLogEventActionToggleAutotranslation as ChannelAdminLogEventActionToggleAutotranslation
    from ._root import ChannelAdminLogEventActionToggleForum as ChannelAdminLogEventActionToggleForum
    from ._root import ChannelAdminLogEventActionToggleGroupCallSetting as ChannelAdminLogEventActionToggleGroupCallSetting
    from ._root import ChannelAdminLogEventActionToggleInvites as ChannelAdminLogEventActionToggleInvites
    from ._root import ChannelAdminLogEventActionToggleNoForwards as ChannelAdminLogEventActionToggleNoForwards
    from ._root import ChannelAdminLogEventActionTogglePreHistoryHidden as ChannelAdminLogEventActionTogglePreHistoryHidden
    from ._root import ChannelAdminLogEventActionToggleSignatureProfiles as ChannelAdminLogEventActionToggleSignatureProfiles
    from ._root import ChannelAdminLogEventActionToggleSignatures as ChannelAdminLogEventActionToggleSignatures
    from ._root import ChannelAdminLogEventActionToggleSlowMode as ChannelAdminLogEventActionToggleSlowMode
    from ._root import ChannelAdminLogEventActionUpdatePinned as ChannelAdminLogEventActionUpdatePinned
    from ._root import ChannelAdminLogEventsFilter as ChannelAdminLogEventsFilter
    from ._root import ChannelForbidden as ChannelForbidden
    from ._root import ChannelFull as ChannelFull
    from ._root import ChannelLocation as ChannelLocation
    from ._root import ChannelLocationEmpty as ChannelLocationEmpty
    from ._root import ChannelMessagesFilter as ChannelMessagesFilter
    from ._root import ChannelMessagesFilterEmpty as ChannelMessagesFilterEmpty
    from ._root import ChannelParticipant as ChannelParticipant
    from ._root import ChannelParticipantAdmin as ChannelParticipantAdmin
    from ._root import ChannelParticipantBanned as ChannelParticipantBanned
    from ._root import ChannelParticipantCreator as ChannelParticipantCreator
    from ._root import ChannelParticipantLeft as ChannelParticipantLeft
    from ._root import ChannelParticipantSelf as ChannelParticipantSelf
    from ._root import ChannelParticipantsAdmins as ChannelParticipantsAdmins
    from ._root import ChannelParticipantsBanned as ChannelParticipantsBanned
    from ._root import ChannelParticipantsBots as ChannelParticipantsBots
    from ._root import ChannelParticipantsContacts as ChannelParticipantsContacts
    from ._root import ChannelParticipantsKicked as ChannelParticipantsKicked
    from ._root import ChannelParticipantsMentions as ChannelParticipantsMentions
    from ._root import ChannelParticipantsRecent as ChannelParticipantsRecent
    from ._root import ChannelParticipantsSearch as ChannelParticipantsSearch
    from ._root import Chat as Chat
    from ._root import ChatAdminRights as ChatAdminRights
    from ._root import ChatAdminWithInvites as ChatAdminWithInvites
    from ._root import ChatBannedRights as ChatBannedRights
    from ._root import ChatEmpty as ChatEmpty
    from ._root import ChatForbidden as ChatForbidden
    from ._root import ChatFull as ChatFull
    from ._root import ChatInvite as ChatInvite
    from ._root import ChatInviteAlready as ChatInviteAlready
    from ._root import ChatInviteExported as ChatInviteExported
    from ._root import ChatInviteImporter as ChatInviteImporter
    from ._root import ChatInvitePeek as ChatInvitePeek
    from ._root import ChatInvitePublicJoinRequests as ChatInvitePublicJoinRequests
    from ._root import ChatOnlines as ChatOnlines
    from ._root import ChatParticipant as ChatParticipant
    from ._root import ChatParticipantAdmin as ChatParticipantAdmin
    from ._root import ChatParticipantCreator as ChatParticipantCreator
    from ._root import ChatParticipants as ChatParticipants
    from ._root import ChatParticipantsForbidden as ChatParticipantsForbidden
    from ._root import ChatPhoto as ChatPhoto
    from ._root import ChatPhotoEmpty as ChatPhotoEmpty
    from ._root import ChatReactionsAll as ChatReactionsAll
    from ._root import ChatReactionsNone as ChatReactionsNone
    from ._root import ChatReactionsSome as ChatReactionsSome
    from ._root import ChatTheme as ChatTheme
    from ._root import ChatThemeUniqueGift as ChatThemeUniqueGift
    from ._root import CodeSettings as CodeSettings
    from ._root import Community as Community
    from ._root import CommunityForbidden as CommunityForbidden
    from ._root import CommunityFull as CommunityFull
    from ._root import CommunityPeer as CommunityPeer
    from ._root import CommunityPeerRequest as CommunityPeerRequest
    from ._root import Config as Config
    from ._root import ConnectedBot as ConnectedBot
    from ._root import ConnectedBotStarRef as ConnectedBotStarRef
    from ._root import Contact as Contact
    from ._root import ContactBirthday as ContactBirthday
    from ._root import ContactStatus as ContactStatus
    from ._root import DataJSON as DataJSON
    from ._root import DcOption as DcOption
    from ._root import DefaultHistoryTTL as DefaultHistoryTTL
    from ._root import Dialog as Dialog
    from ._root import DialogCommunity as DialogCommunity
    from ._root import DialogFilter as DialogFilter
    from ._root import DialogFilterChatlist as DialogFilterChatlist
    from ._root import DialogFilterDefault as DialogFilterDefault
    from ._root import DialogFilterSuggested as DialogFilterSuggested
    from ._root import DialogFolder as DialogFolder
    from ._root import DialogPeer as DialogPeer
    from ._root import DialogPeerCommunity as DialogPeerCommunity
    from ._root import DialogPeerFolder as DialogPeerFolder
    from ._root import DisallowedGiftsSettings as DisallowedGiftsSettings
    from ._root import Document as Document
    from ._root import DocumentAttributeAnimated as DocumentAttributeAnimated
    from ._root import DocumentAttributeAudio as DocumentAttributeAudio
    from ._root import DocumentAttributeCustomEmoji as DocumentAttributeCustomEmoji
    from ._root import DocumentAttributeFilename as DocumentAttributeFilename
    from ._root import DocumentAttributeHasStickers as DocumentAttributeHasStickers
    from ._root import DocumentAttributeImageSize as DocumentAttributeImageSize
    from ._root import DocumentAttributeSticker as DocumentAttributeSticker
    from ._root import DocumentAttributeVideo as DocumentAttributeVideo
    from ._root import DocumentEmpty as DocumentEmpty
    from ._root import DraftMessage as DraftMessage
    from ._root import DraftMessageEmpty as DraftMessageEmpty
    from ._root import EmailVerificationApple as EmailVerificationApple
    from ._root import EmailVerificationCode as EmailVerificationCode
    from ._root import EmailVerificationGoogle as EmailVerificationGoogle
    from ._root import EmailVerifyPurposeLoginChange as EmailVerifyPurposeLoginChange
    from ._root import EmailVerifyPurposeLoginSetup as EmailVerifyPurposeLoginSetup
    from ._root import EmailVerifyPurposePassport as EmailVerifyPurposePassport
    from ._root import EmojiGroup as EmojiGroup
    from ._root import EmojiGroupGreeting as EmojiGroupGreeting
    from ._root import EmojiGroupPremium as EmojiGroupPremium
    from ._root import EmojiKeyword as EmojiKeyword
    from ._root import EmojiKeywordDeleted as EmojiKeywordDeleted
    from ._root import EmojiKeywordsDifference as EmojiKeywordsDifference
    from ._root import EmojiLanguage as EmojiLanguage
    from ._root import EmojiList as EmojiList
    from ._root import EmojiListNotModified as EmojiListNotModified
    from ._root import EmojiStatus as EmojiStatus
    from ._root import EmojiStatusCollectible as EmojiStatusCollectible
    from ._root import EmojiStatusEmpty as EmojiStatusEmpty
    from ._root import EmojiURL as EmojiURL
    from ._root import EncryptedChat as EncryptedChat
    from ._root import EncryptedChatDiscarded as EncryptedChatDiscarded
    from ._root import EncryptedChatEmpty as EncryptedChatEmpty
    from ._root import EncryptedChatRequested as EncryptedChatRequested
    from ._root import EncryptedChatWaiting as EncryptedChatWaiting
    from ._root import EncryptedFile as EncryptedFile
    from ._root import EncryptedFileEmpty as EncryptedFileEmpty
    from ._root import EncryptedMessage as EncryptedMessage
    from ._root import EncryptedMessageService as EncryptedMessageService
    from ._root import EphemeralMessage as EphemeralMessage
    from ._root import Error as Error
    from ._root import ExportedChatlistInvite as ExportedChatlistInvite
    from ._root import ExportedContactToken as ExportedContactToken
    from ._root import ExportedMessageLink as ExportedMessageLink
    from ._root import ExportedStoryLink as ExportedStoryLink
    from ._root import FactCheck as FactCheck
    from ._root import FileHash as FileHash
    from ._root import Folder as Folder
    from ._root import FolderPeer as FolderPeer
    from ._root import ForumTopic as ForumTopic
    from ._root import ForumTopicDeleted as ForumTopicDeleted
    from ._root import FoundStory as FoundStory
    from ._root import Game as Game
    from ._root import GeoPoint as GeoPoint
    from ._root import GeoPointAddress as GeoPointAddress
    from ._root import GeoPointEmpty as GeoPointEmpty
    from ._root import GlobalPrivacySettings as GlobalPrivacySettings
    from ._root import GroupCall as GroupCall
    from ._root import GroupCallDiscarded as GroupCallDiscarded
    from ._root import GroupCallDonor as GroupCallDonor
    from ._root import GroupCallMessage as GroupCallMessage
    from ._root import GroupCallParticipant as GroupCallParticipant
    from ._root import GroupCallParticipantVideo as GroupCallParticipantVideo
    from ._root import GroupCallParticipantVideoSourceGroup as GroupCallParticipantVideoSourceGroup
    from ._root import GroupCallStreamChannel as GroupCallStreamChannel
    from ._root import HighScore as HighScore
    from ._root import ImportedContact as ImportedContact
    from ._root import InlineBotSwitchPM as InlineBotSwitchPM
    from ._root import InlineBotWebView as InlineBotWebView
    from ._root import InlineQueryPeerTypeBotPM as InlineQueryPeerTypeBotPM
    from ._root import InlineQueryPeerTypeBroadcast as InlineQueryPeerTypeBroadcast
    from ._root import InlineQueryPeerTypeChat as InlineQueryPeerTypeChat
    from ._root import InlineQueryPeerTypeMegagroup as InlineQueryPeerTypeMegagroup
    from ._root import InlineQueryPeerTypePM as InlineQueryPeerTypePM
    from ._root import InlineQueryPeerTypeSameBotPM as InlineQueryPeerTypeSameBotPM
    from ._root import InputAiComposeToneDefault as InputAiComposeToneDefault
    from ._root import InputAiComposeToneID as InputAiComposeToneID
    from ._root import InputAiComposeToneSingleUse as InputAiComposeToneSingleUse
    from ._root import InputAiComposeToneSlug as InputAiComposeToneSlug
    from ._root import InputAppEvent as InputAppEvent
    from ._root import InputBotAppID as InputBotAppID
    from ._root import InputBotAppShortName as InputBotAppShortName
    from ._root import InputBotInlineMessageGame as InputBotInlineMessageGame
    from ._root import InputBotInlineMessageID as InputBotInlineMessageID
    from ._root import InputBotInlineMessageID64 as InputBotInlineMessageID64
    from ._root import InputBotInlineMessageMediaAuto as InputBotInlineMessageMediaAuto
    from ._root import InputBotInlineMessageMediaContact as InputBotInlineMessageMediaContact
    from ._root import InputBotInlineMessageMediaGeo as InputBotInlineMessageMediaGeo
    from ._root import InputBotInlineMessageMediaInvoice as InputBotInlineMessageMediaInvoice
    from ._root import InputBotInlineMessageMediaVenue as InputBotInlineMessageMediaVenue
    from ._root import InputBotInlineMessageMediaWebPage as InputBotInlineMessageMediaWebPage
    from ._root import InputBotInlineMessageRichMessage as InputBotInlineMessageRichMessage
    from ._root import InputBotInlineMessageText as InputBotInlineMessageText
    from ._root import InputBotInlineResult as InputBotInlineResult
    from ._root import InputBotInlineResultDocument as InputBotInlineResultDocument
    from ._root import InputBotInlineResultGame as InputBotInlineResultGame
    from ._root import InputBotInlineResultPhoto as InputBotInlineResultPhoto
    from ._root import InputBusinessAwayMessage as InputBusinessAwayMessage
    from ._root import InputBusinessBotRecipients as InputBusinessBotRecipients
    from ._root import InputBusinessChatLink as InputBusinessChatLink
    from ._root import InputBusinessGreetingMessage as InputBusinessGreetingMessage
    from ._root import InputBusinessIntro as InputBusinessIntro
    from ._root import InputBusinessRecipients as InputBusinessRecipients
    from ._root import InputChannel as InputChannel
    from ._root import InputChannelEmpty as InputChannelEmpty
    from ._root import InputChannelFromMessage as InputChannelFromMessage
    from ._root import InputChatPhoto as InputChatPhoto
    from ._root import InputChatPhotoEmpty as InputChatPhotoEmpty
    from ._root import InputChatTheme as InputChatTheme
    from ._root import InputChatThemeEmpty as InputChatThemeEmpty
    from ._root import InputChatThemeUniqueGift as InputChatThemeUniqueGift
    from ._root import InputChatUploadedPhoto as InputChatUploadedPhoto
    from ._root import InputChatlistDialogFilter as InputChatlistDialogFilter
    from ._root import InputCheckPasswordEmpty as InputCheckPasswordEmpty
    from ._root import InputCheckPasswordSRP as InputCheckPasswordSRP
    from ._root import InputClientProxy as InputClientProxy
    from ._root import InputCollectiblePhone as InputCollectiblePhone
    from ._root import InputCollectibleUsername as InputCollectibleUsername
    from ._root import InputDialogPeer as InputDialogPeer
    from ._root import InputDialogPeerCommunity as InputDialogPeerCommunity
    from ._root import InputDialogPeerFolder as InputDialogPeerFolder
    from ._root import InputDocument as InputDocument
    from ._root import InputDocumentEmpty as InputDocumentEmpty
    from ._root import InputDocumentFileLocation as InputDocumentFileLocation
    from ._root import InputEmojiStatusCollectible as InputEmojiStatusCollectible
    from ._root import InputEncryptedChat as InputEncryptedChat
    from ._root import InputEncryptedFile as InputEncryptedFile
    from ._root import InputEncryptedFileBigUploaded as InputEncryptedFileBigUploaded
    from ._root import InputEncryptedFileEmpty as InputEncryptedFileEmpty
    from ._root import InputEncryptedFileLocation as InputEncryptedFileLocation
    from ._root import InputEncryptedFileUploaded as InputEncryptedFileUploaded
    from ._root import InputFile as InputFile
    from ._root import InputFileBig as InputFileBig
    from ._root import InputFileLocation as InputFileLocation
    from ._root import InputFileStoryDocument as InputFileStoryDocument
    from ._root import InputFolderPeer as InputFolderPeer
    from ._root import InputGameID as InputGameID
    from ._root import InputGameShortName as InputGameShortName
    from ._root import InputGeoPoint as InputGeoPoint
    from ._root import InputGeoPointEmpty as InputGeoPointEmpty
    from ._root import InputGroupCall as InputGroupCall
    from ._root import InputGroupCallInviteMessage as InputGroupCallInviteMessage
    from ._root import InputGroupCallSlug as InputGroupCallSlug
    from ._root import InputGroupCallStream as InputGroupCallStream
    from ._root import InputInvoiceBusinessBotTransferStars as InputInvoiceBusinessBotTransferStars
    from ._root import InputInvoiceChatInviteSubscription as InputInvoiceChatInviteSubscription
    from ._root import InputInvoiceMessage as InputInvoiceMessage
    from ._root import InputInvoicePremiumAuthCode as InputInvoicePremiumAuthCode
    from ._root import InputInvoicePremiumGiftCode as InputInvoicePremiumGiftCode
    from ._root import InputInvoicePremiumGiftStars as InputInvoicePremiumGiftStars
    from ._root import InputInvoiceSlug as InputInvoiceSlug
    from ._root import InputInvoiceStarGift as InputInvoiceStarGift
    from ._root import InputInvoiceStarGiftAuctionBid as InputInvoiceStarGiftAuctionBid
    from ._root import InputInvoiceStarGiftDropOriginalDetails as InputInvoiceStarGiftDropOriginalDetails
    from ._root import InputInvoiceStarGiftPrepaidUpgrade as InputInvoiceStarGiftPrepaidUpgrade
    from ._root import InputInvoiceStarGiftResale as InputInvoiceStarGiftResale
    from ._root import InputInvoiceStarGiftTransfer as InputInvoiceStarGiftTransfer
    from ._root import InputInvoiceStarGiftUpgrade as InputInvoiceStarGiftUpgrade
    from ._root import InputInvoiceStars as InputInvoiceStars
    from ._root import InputKeyboardButtonRequestPeer as InputKeyboardButtonRequestPeer
    from ._root import InputKeyboardButtonUrlAuth as InputKeyboardButtonUrlAuth
    from ._root import InputKeyboardButtonUserProfile as InputKeyboardButtonUserProfile
    from ._root import InputMediaAreaChannelPost as InputMediaAreaChannelPost
    from ._root import InputMediaAreaVenue as InputMediaAreaVenue
    from ._root import InputMediaContact as InputMediaContact
    from ._root import InputMediaDice as InputMediaDice
    from ._root import InputMediaDocument as InputMediaDocument
    from ._root import InputMediaDocumentExternal as InputMediaDocumentExternal
    from ._root import InputMediaEmpty as InputMediaEmpty
    from ._root import InputMediaGame as InputMediaGame
    from ._root import InputMediaGeoLive as InputMediaGeoLive
    from ._root import InputMediaGeoPoint as InputMediaGeoPoint
    from ._root import InputMediaInvoice as InputMediaInvoice
    from ._root import InputMediaPaidMedia as InputMediaPaidMedia
    from ._root import InputMediaPhoto as InputMediaPhoto
    from ._root import InputMediaPhotoExternal as InputMediaPhotoExternal
    from ._root import InputMediaPoll as InputMediaPoll
    from ._root import InputMediaStakeDice as InputMediaStakeDice
    from ._root import InputMediaStory as InputMediaStory
    from ._root import InputMediaTodo as InputMediaTodo
    from ._root import InputMediaUploadedDocument as InputMediaUploadedDocument
    from ._root import InputMediaUploadedPhoto as InputMediaUploadedPhoto
    from ._root import InputMediaVenue as InputMediaVenue
    from ._root import InputMediaWebPage as InputMediaWebPage
    from ._root import InputMessageCallbackQuery as InputMessageCallbackQuery
    from ._root import InputMessageEntityMentionName as InputMessageEntityMentionName
    from ._root import InputMessageID as InputMessageID
    from ._root import InputMessagePinned as InputMessagePinned
    from ._root import InputMessageReadMetric as InputMessageReadMetric
    from ._root import InputMessageReplyTo as InputMessageReplyTo
    from ._root import InputMessagesFilterChatPhotos as InputMessagesFilterChatPhotos
    from ._root import InputMessagesFilterContacts as InputMessagesFilterContacts
    from ._root import InputMessagesFilterDocument as InputMessagesFilterDocument
    from ._root import InputMessagesFilterEmpty as InputMessagesFilterEmpty
    from ._root import InputMessagesFilterGeo as InputMessagesFilterGeo
    from ._root import InputMessagesFilterGif as InputMessagesFilterGif
    from ._root import InputMessagesFilterMusic as InputMessagesFilterMusic
    from ._root import InputMessagesFilterMyMentions as InputMessagesFilterMyMentions
    from ._root import InputMessagesFilterPhoneCalls as InputMessagesFilterPhoneCalls
    from ._root import InputMessagesFilterPhotoVideo as InputMessagesFilterPhotoVideo
    from ._root import InputMessagesFilterPhotos as InputMessagesFilterPhotos
    from ._root import InputMessagesFilterPinned as InputMessagesFilterPinned
    from ._root import InputMessagesFilterPoll as InputMessagesFilterPoll
    from ._root import InputMessagesFilterRoundVideo as InputMessagesFilterRoundVideo
    from ._root import InputMessagesFilterRoundVoice as InputMessagesFilterRoundVoice
    from ._root import InputMessagesFilterUrl as InputMessagesFilterUrl
    from ._root import InputMessagesFilterVideo as InputMessagesFilterVideo
    from ._root import InputMessagesFilterVoice as InputMessagesFilterVoice
    from ._root import InputNotifyBroadcasts as InputNotifyBroadcasts
    from ._root import InputNotifyChats as InputNotifyChats
    from ._root import InputNotifyCommunity as InputNotifyCommunity
    from ._root import InputNotifyForumTopic as InputNotifyForumTopic
    from ._root import InputNotifyPeer as InputNotifyPeer
    from ._root import InputNotifyUsers as InputNotifyUsers
    from ._root import InputPageBlockMap as InputPageBlockMap
    from ._root import InputPasskeyCredentialFirebasePNV as InputPasskeyCredentialFirebasePNV
    from ._root import InputPasskeyCredentialPublicKey as InputPasskeyCredentialPublicKey
    from ._root import InputPasskeyResponseLogin as InputPasskeyResponseLogin
    from ._root import InputPasskeyResponseRegister as InputPasskeyResponseRegister
    from ._root import InputPaymentCredentials as InputPaymentCredentials
    from ._root import InputPaymentCredentialsApplePay as InputPaymentCredentialsApplePay
    from ._root import InputPaymentCredentialsGooglePay as InputPaymentCredentialsGooglePay
    from ._root import InputPaymentCredentialsSaved as InputPaymentCredentialsSaved
    from ._root import InputPeerChannel as InputPeerChannel
    from ._root import InputPeerChannelFromMessage as InputPeerChannelFromMessage
    from ._root import InputPeerChat as InputPeerChat
    from ._root import InputPeerColorCollectible as InputPeerColorCollectible
    from ._root import InputPeerEmpty as InputPeerEmpty
    from ._root import InputPeerNotifySettings as InputPeerNotifySettings
    from ._root import InputPeerPhotoFileLocation as InputPeerPhotoFileLocation
    from ._root import InputPeerSelf as InputPeerSelf
    from ._root import InputPeerUser as InputPeerUser
    from ._root import InputPeerUserFromMessage as InputPeerUserFromMessage
    from ._root import InputPhoneCall as InputPhoneCall
    from ._root import InputPhoneContact as InputPhoneContact
    from ._root import InputPhoto as InputPhoto
    from ._root import InputPhotoEmpty as InputPhotoEmpty
    from ._root import InputPhotoFileLocation as InputPhotoFileLocation
    from ._root import InputPhotoLegacyFileLocation as InputPhotoLegacyFileLocation
    from ._root import InputPollAnswer as InputPollAnswer
    from ._root import InputPrivacyKeyAbout as InputPrivacyKeyAbout
    from ._root import InputPrivacyKeyAddedByPhone as InputPrivacyKeyAddedByPhone
    from ._root import InputPrivacyKeyBirthday as InputPrivacyKeyBirthday
    from ._root import InputPrivacyKeyChatInvite as InputPrivacyKeyChatInvite
    from ._root import InputPrivacyKeyForwards as InputPrivacyKeyForwards
    from ._root import InputPrivacyKeyNoPaidMessages as InputPrivacyKeyNoPaidMessages
    from ._root import InputPrivacyKeyPhoneCall as InputPrivacyKeyPhoneCall
    from ._root import InputPrivacyKeyPhoneNumber as InputPrivacyKeyPhoneNumber
    from ._root import InputPrivacyKeyPhoneP2P as InputPrivacyKeyPhoneP2P
    from ._root import InputPrivacyKeyProfilePhoto as InputPrivacyKeyProfilePhoto
    from ._root import InputPrivacyKeySavedMusic as InputPrivacyKeySavedMusic
    from ._root import InputPrivacyKeyStarGiftsAutoSave as InputPrivacyKeyStarGiftsAutoSave
    from ._root import InputPrivacyKeyStatusTimestamp as InputPrivacyKeyStatusTimestamp
    from ._root import InputPrivacyKeyVoiceMessages as InputPrivacyKeyVoiceMessages
    from ._root import InputPrivacyValueAllowAll as InputPrivacyValueAllowAll
    from ._root import InputPrivacyValueAllowBots as InputPrivacyValueAllowBots
    from ._root import InputPrivacyValueAllowChatParticipants as InputPrivacyValueAllowChatParticipants
    from ._root import InputPrivacyValueAllowCloseFriends as InputPrivacyValueAllowCloseFriends
    from ._root import InputPrivacyValueAllowContacts as InputPrivacyValueAllowContacts
    from ._root import InputPrivacyValueAllowPremium as InputPrivacyValueAllowPremium
    from ._root import InputPrivacyValueAllowUsers as InputPrivacyValueAllowUsers
    from ._root import InputPrivacyValueDisallowAll as InputPrivacyValueDisallowAll
    from ._root import InputPrivacyValueDisallowBots as InputPrivacyValueDisallowBots
    from ._root import InputPrivacyValueDisallowChatParticipants as InputPrivacyValueDisallowChatParticipants
    from ._root import InputPrivacyValueDisallowContacts as InputPrivacyValueDisallowContacts
    from ._root import InputPrivacyValueDisallowUsers as InputPrivacyValueDisallowUsers
    from ._root import InputQuickReplyShortcut as InputQuickReplyShortcut
    from ._root import InputQuickReplyShortcutId as InputQuickReplyShortcutId
    from ._root import InputReplyToEphemeralMessage as InputReplyToEphemeralMessage
    from ._root import InputReplyToMessage as InputReplyToMessage
    from ._root import InputReplyToMonoForum as InputReplyToMonoForum
    from ._root import InputReplyToStory as InputReplyToStory
    from ._root import InputReportReasonChildAbuse as InputReportReasonChildAbuse
    from ._root import InputReportReasonCopyright as InputReportReasonCopyright
    from ._root import InputReportReasonFake as InputReportReasonFake
    from ._root import InputReportReasonGeoIrrelevant as InputReportReasonGeoIrrelevant
    from ._root import InputReportReasonIllegalDrugs as InputReportReasonIllegalDrugs
    from ._root import InputReportReasonOther as InputReportReasonOther
    from ._root import InputReportReasonPersonalDetails as InputReportReasonPersonalDetails
    from ._root import InputReportReasonPornography as InputReportReasonPornography
    from ._root import InputReportReasonSpam as InputReportReasonSpam
    from ._root import InputReportReasonViolence as InputReportReasonViolence
    from ._root import InputRichFileDocument as InputRichFileDocument
    from ._root import InputRichFilePhoto as InputRichFilePhoto
    from ._root import InputRichMessage as InputRichMessage
    from ._root import InputRichMessageHTML as InputRichMessageHTML
    from ._root import InputRichMessageMarkdown as InputRichMessageMarkdown
    from ._root import InputSavedStarGiftChat as InputSavedStarGiftChat
    from ._root import InputSavedStarGiftSlug as InputSavedStarGiftSlug
    from ._root import InputSavedStarGiftUser as InputSavedStarGiftUser
    from ._root import InputSecureFile as InputSecureFile
    from ._root import InputSecureFileLocation as InputSecureFileLocation
    from ._root import InputSecureFileUploaded as InputSecureFileUploaded
    from ._root import InputSecureValue as InputSecureValue
    from ._root import InputSendMessageRichMessageDraftAction as InputSendMessageRichMessageDraftAction
    from ._root import InputSingleMedia as InputSingleMedia
    from ._root import InputStarGiftAuction as InputStarGiftAuction
    from ._root import InputStarGiftAuctionSlug as InputStarGiftAuctionSlug
    from ._root import InputStarsTransaction as InputStarsTransaction
    from ._root import InputStickerSetAnimatedEmoji as InputStickerSetAnimatedEmoji
    from ._root import InputStickerSetAnimatedEmojiAnimations as InputStickerSetAnimatedEmojiAnimations
    from ._root import InputStickerSetDice as InputStickerSetDice
    from ._root import InputStickerSetEmojiChannelDefaultStatuses as InputStickerSetEmojiChannelDefaultStatuses
    from ._root import InputStickerSetEmojiDefaultStatuses as InputStickerSetEmojiDefaultStatuses
    from ._root import InputStickerSetEmojiDefaultTopicIcons as InputStickerSetEmojiDefaultTopicIcons
    from ._root import InputStickerSetEmojiGenericAnimations as InputStickerSetEmojiGenericAnimations
    from ._root import InputStickerSetEmpty as InputStickerSetEmpty
    from ._root import InputStickerSetID as InputStickerSetID
    from ._root import InputStickerSetItem as InputStickerSetItem
    from ._root import InputStickerSetPremiumGifts as InputStickerSetPremiumGifts
    from ._root import InputStickerSetShortName as InputStickerSetShortName
    from ._root import InputStickerSetThumb as InputStickerSetThumb
    from ._root import InputStickerSetTonGifts as InputStickerSetTonGifts
    from ._root import InputStickeredMediaDocument as InputStickeredMediaDocument
    from ._root import InputStickeredMediaPhoto as InputStickeredMediaPhoto
    from ._root import InputStorePaymentAuthCode as InputStorePaymentAuthCode
    from ._root import InputStorePaymentGiftPremium as InputStorePaymentGiftPremium
    from ._root import InputStorePaymentPremiumGiftCode as InputStorePaymentPremiumGiftCode
    from ._root import InputStorePaymentPremiumGiveaway as InputStorePaymentPremiumGiveaway
    from ._root import InputStorePaymentPremiumSubscription as InputStorePaymentPremiumSubscription
    from ._root import InputStorePaymentStarsGift as InputStorePaymentStarsGift
    from ._root import InputStorePaymentStarsGiveaway as InputStorePaymentStarsGiveaway
    from ._root import InputStorePaymentStarsTopup as InputStorePaymentStarsTopup
    from ._root import InputTakeoutFileLocation as InputTakeoutFileLocation
    from ._root import InputTheme as InputTheme
    from ._root import InputThemeSettings as InputThemeSettings
    from ._root import InputThemeSlug as InputThemeSlug
    from ._root import InputUser as InputUser
    from ._root import InputUserEmpty as InputUserEmpty
    from ._root import InputUserFromMessage as InputUserFromMessage
    from ._root import InputUserSelf as InputUserSelf
    from ._root import InputWallPaper as InputWallPaper
    from ._root import InputWallPaperNoFile as InputWallPaperNoFile
    from ._root import InputWallPaperSlug as InputWallPaperSlug
    from ._root import InputWebDocument as InputWebDocument
    from ._root import InputWebFileAudioAlbumThumbLocation as InputWebFileAudioAlbumThumbLocation
    from ._root import InputWebFileGeoPointLocation as InputWebFileGeoPointLocation
    from ._root import InputWebFileLocation as InputWebFileLocation
    from ._root import Invoice as Invoice
    from ._root import JoinChatBotResultApproved as JoinChatBotResultApproved
    from ._root import JoinChatBotResultDeclined as JoinChatBotResultDeclined
    from ._root import JoinChatBotResultQueued as JoinChatBotResultQueued
    from ._root import JoinChatBotResultWebView as JoinChatBotResultWebView
    from ._root import JsonArray as JsonArray
    from ._root import JsonBool as JsonBool
    from ._root import JsonNull as JsonNull
    from ._root import JsonNumber as JsonNumber
    from ._root import JsonObject as JsonObject
    from ._root import JsonObjectValue as JsonObjectValue
    from ._root import JsonString as JsonString
    from ._root import KeyboardButton as KeyboardButton
    from ._root import KeyboardButtonBuy as KeyboardButtonBuy
    from ._root import KeyboardButtonCallback as KeyboardButtonCallback
    from ._root import KeyboardButtonCopy as KeyboardButtonCopy
    from ._root import KeyboardButtonGame as KeyboardButtonGame
    from ._root import KeyboardButtonRequestGeoLocation as KeyboardButtonRequestGeoLocation
    from ._root import KeyboardButtonRequestPeer as KeyboardButtonRequestPeer
    from ._root import KeyboardButtonRequestPhone as KeyboardButtonRequestPhone
    from ._root import KeyboardButtonRequestPoll as KeyboardButtonRequestPoll
    from ._root import KeyboardButtonRow as KeyboardButtonRow
    from ._root import KeyboardButtonSimpleWebView as KeyboardButtonSimpleWebView
    from ._root import KeyboardButtonStyle as KeyboardButtonStyle
    from ._root import KeyboardButtonSwitchInline as KeyboardButtonSwitchInline
    from ._root import KeyboardButtonUrl as KeyboardButtonUrl
    from ._root import KeyboardButtonUrlAuth as KeyboardButtonUrlAuth
    from ._root import KeyboardButtonUserProfile as KeyboardButtonUserProfile
    from ._root import KeyboardButtonWebView as KeyboardButtonWebView
    from ._root import LabeledPrice as LabeledPrice
    from ._root import LangPackDifference as LangPackDifference
    from ._root import LangPackLanguage as LangPackLanguage
    from ._root import LangPackString as LangPackString
    from ._root import LangPackStringDeleted as LangPackStringDeleted
    from ._root import LangPackStringPluralized as LangPackStringPluralized
    from ._root import MaskCoords as MaskCoords
    from ._root import MediaAreaChannelPost as MediaAreaChannelPost
    from ._root import MediaAreaCoordinates as MediaAreaCoordinates
    from ._root import MediaAreaGeoPoint as MediaAreaGeoPoint
    from ._root import MediaAreaStarGift as MediaAreaStarGift
    from ._root import MediaAreaSuggestedReaction as MediaAreaSuggestedReaction
    from ._root import MediaAreaUrl as MediaAreaUrl
    from ._root import MediaAreaVenue as MediaAreaVenue
    from ._root import MediaAreaWeather as MediaAreaWeather
    from ._root import Message as Message
    from ._root import MessageActionBoostApply as MessageActionBoostApply
    from ._root import MessageActionBotAllowed as MessageActionBotAllowed
    from ._root import MessageActionChangeCommunity as MessageActionChangeCommunity
    from ._root import MessageActionChangeCreator as MessageActionChangeCreator
    from ._root import MessageActionChannelCreate as MessageActionChannelCreate
    from ._root import MessageActionChannelMigrateFrom as MessageActionChannelMigrateFrom
    from ._root import MessageActionChatAddUser as MessageActionChatAddUser
    from ._root import MessageActionChatCreate as MessageActionChatCreate
    from ._root import MessageActionChatDeletePhoto as MessageActionChatDeletePhoto
    from ._root import MessageActionChatDeleteUser as MessageActionChatDeleteUser
    from ._root import MessageActionChatEditPhoto as MessageActionChatEditPhoto
    from ._root import MessageActionChatEditTitle as MessageActionChatEditTitle
    from ._root import MessageActionChatJoinedByLink as MessageActionChatJoinedByLink
    from ._root import MessageActionChatJoinedByRequest as MessageActionChatJoinedByRequest
    from ._root import MessageActionChatMigrateTo as MessageActionChatMigrateTo
    from ._root import MessageActionConferenceCall as MessageActionConferenceCall
    from ._root import MessageActionContactSignUp as MessageActionContactSignUp
    from ._root import MessageActionCustomAction as MessageActionCustomAction
    from ._root import MessageActionEmpty as MessageActionEmpty
    from ._root import MessageActionGameScore as MessageActionGameScore
    from ._root import MessageActionGeoProximityReached as MessageActionGeoProximityReached
    from ._root import MessageActionGiftCode as MessageActionGiftCode
    from ._root import MessageActionGiftPremium as MessageActionGiftPremium
    from ._root import MessageActionGiftStars as MessageActionGiftStars
    from ._root import MessageActionGiftTon as MessageActionGiftTon
    from ._root import MessageActionGiveawayLaunch as MessageActionGiveawayLaunch
    from ._root import MessageActionGiveawayResults as MessageActionGiveawayResults
    from ._root import MessageActionGroupCall as MessageActionGroupCall
    from ._root import MessageActionGroupCallScheduled as MessageActionGroupCallScheduled
    from ._root import MessageActionHistoryClear as MessageActionHistoryClear
    from ._root import MessageActionInviteToGroupCall as MessageActionInviteToGroupCall
    from ._root import MessageActionManagedBotCreated as MessageActionManagedBotCreated
    from ._root import MessageActionNewCreatorPending as MessageActionNewCreatorPending
    from ._root import MessageActionNoForwardsRequest as MessageActionNoForwardsRequest
    from ._root import MessageActionNoForwardsToggle as MessageActionNoForwardsToggle
    from ._root import MessageActionPaidMessagesPrice as MessageActionPaidMessagesPrice
    from ._root import MessageActionPaidMessagesRefunded as MessageActionPaidMessagesRefunded
    from ._root import MessageActionPaymentRefunded as MessageActionPaymentRefunded
    from ._root import MessageActionPaymentSent as MessageActionPaymentSent
    from ._root import MessageActionPaymentSentMe as MessageActionPaymentSentMe
    from ._root import MessageActionPhoneCall as MessageActionPhoneCall
    from ._root import MessageActionPinMessage as MessageActionPinMessage
    from ._root import MessageActionPollAppendAnswer as MessageActionPollAppendAnswer
    from ._root import MessageActionPollDeleteAnswer as MessageActionPollDeleteAnswer
    from ._root import MessageActionPrizeStars as MessageActionPrizeStars
    from ._root import MessageActionRequestedPeer as MessageActionRequestedPeer
    from ._root import MessageActionRequestedPeerSentMe as MessageActionRequestedPeerSentMe
    from ._root import MessageActionScreenshotTaken as MessageActionScreenshotTaken
    from ._root import MessageActionSecureValuesSent as MessageActionSecureValuesSent
    from ._root import MessageActionSecureValuesSentMe as MessageActionSecureValuesSentMe
    from ._root import MessageActionSetChatTheme as MessageActionSetChatTheme
    from ._root import MessageActionSetChatWallPaper as MessageActionSetChatWallPaper
    from ._root import MessageActionSetMessagesTTL as MessageActionSetMessagesTTL
    from ._root import MessageActionStarGift as MessageActionStarGift
    from ._root import MessageActionStarGiftPurchaseOffer as MessageActionStarGiftPurchaseOffer
    from ._root import MessageActionStarGiftPurchaseOfferDeclined as MessageActionStarGiftPurchaseOfferDeclined
    from ._root import MessageActionStarGiftUnique as MessageActionStarGiftUnique
    from ._root import MessageActionSuggestBirthday as MessageActionSuggestBirthday
    from ._root import MessageActionSuggestProfilePhoto as MessageActionSuggestProfilePhoto
    from ._root import MessageActionSuggestedPostApproval as MessageActionSuggestedPostApproval
    from ._root import MessageActionSuggestedPostRefund as MessageActionSuggestedPostRefund
    from ._root import MessageActionSuggestedPostSuccess as MessageActionSuggestedPostSuccess
    from ._root import MessageActionTodoAppendTasks as MessageActionTodoAppendTasks
    from ._root import MessageActionTodoCompletions as MessageActionTodoCompletions
    from ._root import MessageActionTopicCreate as MessageActionTopicCreate
    from ._root import MessageActionTopicEdit as MessageActionTopicEdit
    from ._root import MessageActionWebViewDataSent as MessageActionWebViewDataSent
    from ._root import MessageActionWebViewDataSentMe as MessageActionWebViewDataSentMe
    from ._root import MessageEmpty as MessageEmpty
    from ._root import MessageEntityBankCard as MessageEntityBankCard
    from ._root import MessageEntityBlockquote as MessageEntityBlockquote
    from ._root import MessageEntityBold as MessageEntityBold
    from ._root import MessageEntityBotCommand as MessageEntityBotCommand
    from ._root import MessageEntityCashtag as MessageEntityCashtag
    from ._root import MessageEntityCode as MessageEntityCode
    from ._root import MessageEntityCustomEmoji as MessageEntityCustomEmoji
    from ._root import MessageEntityDiffDelete as MessageEntityDiffDelete
    from ._root import MessageEntityDiffInsert as MessageEntityDiffInsert
    from ._root import MessageEntityDiffReplace as MessageEntityDiffReplace
    from ._root import MessageEntityEmail as MessageEntityEmail
    from ._root import MessageEntityFormattedDate as MessageEntityFormattedDate
    from ._root import MessageEntityHashtag as MessageEntityHashtag
    from ._root import MessageEntityItalic as MessageEntityItalic
    from ._root import MessageEntityMention as MessageEntityMention
    from ._root import MessageEntityMentionName as MessageEntityMentionName
    from ._root import MessageEntityPhone as MessageEntityPhone
    from ._root import MessageEntityPre as MessageEntityPre
    from ._root import MessageEntitySpoiler as MessageEntitySpoiler
    from ._root import MessageEntityStrike as MessageEntityStrike
    from ._root import MessageEntityTextUrl as MessageEntityTextUrl
    from ._root import MessageEntityUnderline as MessageEntityUnderline
    from ._root import MessageEntityUnknown as MessageEntityUnknown
    from ._root import MessageEntityUrl as MessageEntityUrl
    from ._root import MessageExtendedMedia as MessageExtendedMedia
    from ._root import MessageExtendedMediaPreview as MessageExtendedMediaPreview
    from ._root import MessageFwdHeader as MessageFwdHeader
    from ._root import MessageMediaContact as MessageMediaContact
    from ._root import MessageMediaDice as MessageMediaDice
    from ._root import MessageMediaDocument as MessageMediaDocument
    from ._root import MessageMediaEmpty as MessageMediaEmpty
    from ._root import MessageMediaGame as MessageMediaGame
    from ._root import MessageMediaGeo as MessageMediaGeo
    from ._root import MessageMediaGeoLive as MessageMediaGeoLive
    from ._root import MessageMediaGiveaway as MessageMediaGiveaway
    from ._root import MessageMediaGiveawayResults as MessageMediaGiveawayResults
    from ._root import MessageMediaInvoice as MessageMediaInvoice
    from ._root import MessageMediaPaidMedia as MessageMediaPaidMedia
    from ._root import MessageMediaPhoto as MessageMediaPhoto
    from ._root import MessageMediaPoll as MessageMediaPoll
    from ._root import MessageMediaStory as MessageMediaStory
    from ._root import MessageMediaToDo as MessageMediaToDo
    from ._root import MessageMediaUnsupported as MessageMediaUnsupported
    from ._root import MessageMediaVenue as MessageMediaVenue
    from ._root import MessageMediaVideoStream as MessageMediaVideoStream
    from ._root import MessageMediaWebPage as MessageMediaWebPage
    from ._root import MessagePeerReaction as MessagePeerReaction
    from ._root import MessagePeerVote as MessagePeerVote
    from ._root import MessagePeerVoteInputOption as MessagePeerVoteInputOption
    from ._root import MessagePeerVoteMultiple as MessagePeerVoteMultiple
    from ._root import MessageRange as MessageRange
    from ._root import MessageReactions as MessageReactions
    from ._root import MessageReactor as MessageReactor
    from ._root import MessageReplies as MessageReplies
    from ._root import MessageReplyHeader as MessageReplyHeader
    from ._root import MessageReplyStoryHeader as MessageReplyStoryHeader
    from ._root import MessageReportOption as MessageReportOption
    from ._root import MessageService as MessageService
    from ._root import MessageViews as MessageViews
    from ._root import MissingInvitee as MissingInvitee
    from ._root import MonoForumDialog as MonoForumDialog
    from ._root import MyBoost as MyBoost
    from ._root import NearestDc as NearestDc
    from ._root import NotificationSoundDefault as NotificationSoundDefault
    from ._root import NotificationSoundLocal as NotificationSoundLocal
    from ._root import NotificationSoundNone as NotificationSoundNone
    from ._root import NotificationSoundRingtone as NotificationSoundRingtone
    from ._root import NotifyBroadcasts as NotifyBroadcasts
    from ._root import NotifyChats as NotifyChats
    from ._root import NotifyCommunity as NotifyCommunity
    from ._root import NotifyForumTopic as NotifyForumTopic
    from ._root import NotifyPeer as NotifyPeer
    from ._root import NotifyUsers as NotifyUsers
    from ._root import Null as Null
    from ._root import OutboxReadDate as OutboxReadDate
    from ._root import Page as Page
    from ._root import PageBlockAnchor as PageBlockAnchor
    from ._root import PageBlockAudio as PageBlockAudio
    from ._root import PageBlockAuthorDate as PageBlockAuthorDate
    from ._root import PageBlockBlockquote as PageBlockBlockquote
    from ._root import PageBlockBlockquoteBlocks as PageBlockBlockquoteBlocks
    from ._root import PageBlockChannel as PageBlockChannel
    from ._root import PageBlockCollage as PageBlockCollage
    from ._root import PageBlockCover as PageBlockCover
    from ._root import PageBlockDetails as PageBlockDetails
    from ._root import PageBlockDivider as PageBlockDivider
    from ._root import PageBlockEmbed as PageBlockEmbed
    from ._root import PageBlockEmbedPost as PageBlockEmbedPost
    from ._root import PageBlockFooter as PageBlockFooter
    from ._root import PageBlockHeader as PageBlockHeader
    from ._root import PageBlockHeading1 as PageBlockHeading1
    from ._root import PageBlockHeading2 as PageBlockHeading2
    from ._root import PageBlockHeading3 as PageBlockHeading3
    from ._root import PageBlockHeading4 as PageBlockHeading4
    from ._root import PageBlockHeading5 as PageBlockHeading5
    from ._root import PageBlockHeading6 as PageBlockHeading6
    from ._root import PageBlockKicker as PageBlockKicker
    from ._root import PageBlockList as PageBlockList
    from ._root import PageBlockMap as PageBlockMap
    from ._root import PageBlockMath as PageBlockMath
    from ._root import PageBlockOrderedList as PageBlockOrderedList
    from ._root import PageBlockParagraph as PageBlockParagraph
    from ._root import PageBlockPhoto as PageBlockPhoto
    from ._root import PageBlockPreformatted as PageBlockPreformatted
    from ._root import PageBlockPullquote as PageBlockPullquote
    from ._root import PageBlockRelatedArticles as PageBlockRelatedArticles
    from ._root import PageBlockSlideshow as PageBlockSlideshow
    from ._root import PageBlockSubheader as PageBlockSubheader
    from ._root import PageBlockSubtitle as PageBlockSubtitle
    from ._root import PageBlockTable as PageBlockTable
    from ._root import PageBlockThinking as PageBlockThinking
    from ._root import PageBlockTitle as PageBlockTitle
    from ._root import PageBlockUnsupported as PageBlockUnsupported
    from ._root import PageBlockVideo as PageBlockVideo
    from ._root import PageCaption as PageCaption
    from ._root import PageListItemBlocks as PageListItemBlocks
    from ._root import PageListItemText as PageListItemText
    from ._root import PageListOrderedItemBlocks as PageListOrderedItemBlocks
    from ._root import PageListOrderedItemText as PageListOrderedItemText
    from ._root import PageRelatedArticle as PageRelatedArticle
    from ._root import PageTableCell as PageTableCell
    from ._root import PageTableRow as PageTableRow
    from ._root import PaidReactionPrivacyAnonymous as PaidReactionPrivacyAnonymous
    from ._root import PaidReactionPrivacyDefault as PaidReactionPrivacyDefault
    from ._root import PaidReactionPrivacyPeer as PaidReactionPrivacyPeer
    from ._root import Passkey as Passkey
    from ._root import PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow as PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow
    from ._root import PasswordKdfAlgoUnknown as PasswordKdfAlgoUnknown
    from ._root import PaymentCharge as PaymentCharge
    from ._root import PaymentFormMethod as PaymentFormMethod
    from ._root import PaymentRequestedInfo as PaymentRequestedInfo
    from ._root import PaymentSavedCredentialsCard as PaymentSavedCredentialsCard
    from ._root import PeerBlocked as PeerBlocked
    from ._root import PeerChannel as PeerChannel
    from ._root import PeerChat as PeerChat
    from ._root import PeerColor as PeerColor
    from ._root import PeerColorCollectible as PeerColorCollectible
    from ._root import PeerLocated as PeerLocated
    from ._root import PeerNotifySettings as PeerNotifySettings
    from ._root import PeerSelfLocated as PeerSelfLocated
    from ._root import PeerSettings as PeerSettings
    from ._root import PeerStories as PeerStories
    from ._root import PeerUser as PeerUser
    from ._root import PendingSuggestion as PendingSuggestion
    from ._root import PhoneCall as PhoneCall
    from ._root import PhoneCallAccepted as PhoneCallAccepted
    from ._root import PhoneCallDiscardReasonBusy as PhoneCallDiscardReasonBusy
    from ._root import PhoneCallDiscardReasonDisconnect as PhoneCallDiscardReasonDisconnect
    from ._root import PhoneCallDiscardReasonHangup as PhoneCallDiscardReasonHangup
    from ._root import PhoneCallDiscardReasonMigrateConferenceCall as PhoneCallDiscardReasonMigrateConferenceCall
    from ._root import PhoneCallDiscardReasonMissed as PhoneCallDiscardReasonMissed
    from ._root import PhoneCallDiscarded as PhoneCallDiscarded
    from ._root import PhoneCallEmpty as PhoneCallEmpty
    from ._root import PhoneCallProtocol as PhoneCallProtocol
    from ._root import PhoneCallRequested as PhoneCallRequested
    from ._root import PhoneCallWaiting as PhoneCallWaiting
    from ._root import PhoneConnection as PhoneConnection
    from ._root import PhoneConnectionWebrtc as PhoneConnectionWebrtc
    from ._root import Photo as Photo
    from ._root import PhotoCachedSize as PhotoCachedSize
    from ._root import PhotoEmpty as PhotoEmpty
    from ._root import PhotoPathSize as PhotoPathSize
    from ._root import PhotoSize as PhotoSize
    from ._root import PhotoSizeEmpty as PhotoSizeEmpty
    from ._root import PhotoSizeProgressive as PhotoSizeProgressive
    from ._root import PhotoStrippedSize as PhotoStrippedSize
    from ._root import Poll as Poll
    from ._root import PollAnswer as PollAnswer
    from ._root import PollAnswerVoters as PollAnswerVoters
    from ._root import PollResults as PollResults
    from ._root import PopularContact as PopularContact
    from ._root import PostAddress as PostAddress
    from ._root import PostInteractionCountersMessage as PostInteractionCountersMessage
    from ._root import PostInteractionCountersStory as PostInteractionCountersStory
    from ._root import PremiumGiftCodeOption as PremiumGiftCodeOption
    from ._root import PremiumSubscriptionOption as PremiumSubscriptionOption
    from ._root import PrepaidGiveaway as PrepaidGiveaway
    from ._root import PrepaidStarsGiveaway as PrepaidStarsGiveaway
    from ._root import PrivacyKeyAbout as PrivacyKeyAbout
    from ._root import PrivacyKeyAddedByPhone as PrivacyKeyAddedByPhone
    from ._root import PrivacyKeyBirthday as PrivacyKeyBirthday
    from ._root import PrivacyKeyChatInvite as PrivacyKeyChatInvite
    from ._root import PrivacyKeyForwards as PrivacyKeyForwards
    from ._root import PrivacyKeyNoPaidMessages as PrivacyKeyNoPaidMessages
    from ._root import PrivacyKeyPhoneCall as PrivacyKeyPhoneCall
    from ._root import PrivacyKeyPhoneNumber as PrivacyKeyPhoneNumber
    from ._root import PrivacyKeyPhoneP2P as PrivacyKeyPhoneP2P
    from ._root import PrivacyKeyProfilePhoto as PrivacyKeyProfilePhoto
    from ._root import PrivacyKeySavedMusic as PrivacyKeySavedMusic
    from ._root import PrivacyKeyStarGiftsAutoSave as PrivacyKeyStarGiftsAutoSave
    from ._root import PrivacyKeyStatusTimestamp as PrivacyKeyStatusTimestamp
    from ._root import PrivacyKeyVoiceMessages as PrivacyKeyVoiceMessages
    from ._root import PrivacyValueAllowAll as PrivacyValueAllowAll
    from ._root import PrivacyValueAllowBots as PrivacyValueAllowBots
    from ._root import PrivacyValueAllowChatParticipants as PrivacyValueAllowChatParticipants
    from ._root import PrivacyValueAllowCloseFriends as PrivacyValueAllowCloseFriends
    from ._root import PrivacyValueAllowContacts as PrivacyValueAllowContacts
    from ._root import PrivacyValueAllowPremium as PrivacyValueAllowPremium
    from ._root import PrivacyValueAllowUsers as PrivacyValueAllowUsers
    from ._root import PrivacyValueDisallowAll as PrivacyValueDisallowAll
    from ._root import PrivacyValueDisallowBots as PrivacyValueDisallowBots
    from ._root import PrivacyValueDisallowChatParticipants as PrivacyValueDisallowChatParticipants
    from ._root import PrivacyValueDisallowContacts as PrivacyValueDisallowContacts
    from ._root import PrivacyValueDisallowUsers as PrivacyValueDisallowUsers
    from ._root import ProfileTabFiles as ProfileTabFiles
    from ._root import ProfileTabGifs as ProfileTabGifs
    from ._root import ProfileTabGifts as ProfileTabGifts
    from ._root import ProfileTabLinks as ProfileTabLinks
    from ._root import ProfileTabMedia as ProfileTabMedia
    from ._root import ProfileTabMusic as ProfileTabMusic
    from ._root import ProfileTabPosts as ProfileTabPosts
    from ._root import ProfileTabVoice as ProfileTabVoice
    from ._root import PublicForwardMessage as PublicForwardMessage
    from ._root import PublicForwardStory as PublicForwardStory
    from ._root import QuickReply as QuickReply
    from ._root import ReactionCount as ReactionCount
    from ._root import ReactionCustomEmoji as ReactionCustomEmoji
    from ._root import ReactionEmoji as ReactionEmoji
    from ._root import ReactionEmpty as ReactionEmpty
    from ._root import ReactionNotificationsFromAll as ReactionNotificationsFromAll
    from ._root import ReactionNotificationsFromContacts as ReactionNotificationsFromContacts
    from ._root import ReactionPaid as ReactionPaid
    from ._root import ReactionsNotifySettings as ReactionsNotifySettings
    from ._root import ReadParticipantDate as ReadParticipantDate
    from ._root import ReceivedNotifyMessage as ReceivedNotifyMessage
    from ._root import RecentMeUrlChat as RecentMeUrlChat
    from ._root import RecentMeUrlChatInvite as RecentMeUrlChatInvite
    from ._root import RecentMeUrlStickerSet as RecentMeUrlStickerSet
    from ._root import RecentMeUrlUnknown as RecentMeUrlUnknown
    from ._root import RecentMeUrlUser as RecentMeUrlUser
    from ._root import RecentStory as RecentStory
    from ._root import ReplyInlineMarkup as ReplyInlineMarkup
    from ._root import ReplyKeyboardForceReply as ReplyKeyboardForceReply
    from ._root import ReplyKeyboardHide as ReplyKeyboardHide
    from ._root import ReplyKeyboardMarkup as ReplyKeyboardMarkup
    from ._root import ReportResultAddComment as ReportResultAddComment
    from ._root import ReportResultChooseOption as ReportResultChooseOption
    from ._root import ReportResultReported as ReportResultReported
    from ._root import RequestPeerTypeBroadcast as RequestPeerTypeBroadcast
    from ._root import RequestPeerTypeChat as RequestPeerTypeChat
    from ._root import RequestPeerTypeCreateBot as RequestPeerTypeCreateBot
    from ._root import RequestPeerTypeUser as RequestPeerTypeUser
    from ._root import RequestedPeerChannel as RequestedPeerChannel
    from ._root import RequestedPeerChat as RequestedPeerChat
    from ._root import RequestedPeerUser as RequestedPeerUser
    from ._root import RequirementToContactEmpty as RequirementToContactEmpty
    from ._root import RequirementToContactPaidMessages as RequirementToContactPaidMessages
    from ._root import RequirementToContactPremium as RequirementToContactPremium
    from ._root import RestrictionReason as RestrictionReason
    from ._root import RichMessage as RichMessage
    from ._root import SavedDialog as SavedDialog
    from ._root import SavedPhoneContact as SavedPhoneContact
    from ._root import SavedReactionTag as SavedReactionTag
    from ._root import SavedStarGift as SavedStarGift
    from ._root import SearchPostsFlood as SearchPostsFlood
    from ._root import SearchResultPosition as SearchResultPosition
    from ._root import SearchResultsCalendarPeriod as SearchResultsCalendarPeriod
    from ._root import SecureCredentialsEncrypted as SecureCredentialsEncrypted
    from ._root import SecureData as SecureData
    from ._root import SecureFile as SecureFile
    from ._root import SecureFileEmpty as SecureFileEmpty
    from ._root import SecurePasswordKdfAlgoPBKDF2HMACSHA512iter100000 as SecurePasswordKdfAlgoPBKDF2HMACSHA512iter100000
    from ._root import SecurePasswordKdfAlgoSHA512 as SecurePasswordKdfAlgoSHA512
    from ._root import SecurePasswordKdfAlgoUnknown as SecurePasswordKdfAlgoUnknown
    from ._root import SecurePlainEmail as SecurePlainEmail
    from ._root import SecurePlainPhone as SecurePlainPhone
    from ._root import SecureRequiredType as SecureRequiredType
    from ._root import SecureRequiredTypeOneOf as SecureRequiredTypeOneOf
    from ._root import SecureSecretSettings as SecureSecretSettings
    from ._root import SecureValue as SecureValue
    from ._root import SecureValueError as SecureValueError
    from ._root import SecureValueErrorData as SecureValueErrorData
    from ._root import SecureValueErrorFile as SecureValueErrorFile
    from ._root import SecureValueErrorFiles as SecureValueErrorFiles
    from ._root import SecureValueErrorFrontSide as SecureValueErrorFrontSide
    from ._root import SecureValueErrorReverseSide as SecureValueErrorReverseSide
    from ._root import SecureValueErrorSelfie as SecureValueErrorSelfie
    from ._root import SecureValueErrorTranslationFile as SecureValueErrorTranslationFile
    from ._root import SecureValueErrorTranslationFiles as SecureValueErrorTranslationFiles
    from ._root import SecureValueHash as SecureValueHash
    from ._root import SecureValueTypeAddress as SecureValueTypeAddress
    from ._root import SecureValueTypeBankStatement as SecureValueTypeBankStatement
    from ._root import SecureValueTypeDriverLicense as SecureValueTypeDriverLicense
    from ._root import SecureValueTypeEmail as SecureValueTypeEmail
    from ._root import SecureValueTypeIdentityCard as SecureValueTypeIdentityCard
    from ._root import SecureValueTypeInternalPassport as SecureValueTypeInternalPassport
    from ._root import SecureValueTypePassport as SecureValueTypePassport
    from ._root import SecureValueTypePassportRegistration as SecureValueTypePassportRegistration
    from ._root import SecureValueTypePersonalDetails as SecureValueTypePersonalDetails
    from ._root import SecureValueTypePhone as SecureValueTypePhone
    from ._root import SecureValueTypeRentalAgreement as SecureValueTypeRentalAgreement
    from ._root import SecureValueTypeTemporaryRegistration as SecureValueTypeTemporaryRegistration
    from ._root import SecureValueTypeUtilityBill as SecureValueTypeUtilityBill
    from ._root import SendAsPeer as SendAsPeer
    from ._root import SendMessageCancelAction as SendMessageCancelAction
    from ._root import SendMessageChooseContactAction as SendMessageChooseContactAction
    from ._root import SendMessageChooseStickerAction as SendMessageChooseStickerAction
    from ._root import SendMessageEmojiInteraction as SendMessageEmojiInteraction
    from ._root import SendMessageEmojiInteractionSeen as SendMessageEmojiInteractionSeen
    from ._root import SendMessageGamePlayAction as SendMessageGamePlayAction
    from ._root import SendMessageGeoLocationAction as SendMessageGeoLocationAction
    from ._root import SendMessageHistoryImportAction as SendMessageHistoryImportAction
    from ._root import SendMessageRecordAudioAction as SendMessageRecordAudioAction
    from ._root import SendMessageRecordRoundAction as SendMessageRecordRoundAction
    from ._root import SendMessageRecordVideoAction as SendMessageRecordVideoAction
    from ._root import SendMessageRichMessageDraftAction as SendMessageRichMessageDraftAction
    from ._root import SendMessageTextDraftAction as SendMessageTextDraftAction
    from ._root import SendMessageTypingAction as SendMessageTypingAction
    from ._root import SendMessageUploadAudioAction as SendMessageUploadAudioAction
    from ._root import SendMessageUploadDocumentAction as SendMessageUploadDocumentAction
    from ._root import SendMessageUploadPhotoAction as SendMessageUploadPhotoAction
    from ._root import SendMessageUploadRoundAction as SendMessageUploadRoundAction
    from ._root import SendMessageUploadVideoAction as SendMessageUploadVideoAction
    from ._root import ShippingOption as ShippingOption
    from ._root import SmsJob as SmsJob
    from ._root import SpeakingInGroupCallAction as SpeakingInGroupCallAction
    from ._root import SponsoredMessage as SponsoredMessage
    from ._root import SponsoredMessageReportOption as SponsoredMessageReportOption
    from ._root import SponsoredPeer as SponsoredPeer
    from ._root import StarGift as StarGift
    from ._root import StarGiftActiveAuctionState as StarGiftActiveAuctionState
    from ._root import StarGiftAttributeBackdrop as StarGiftAttributeBackdrop
    from ._root import StarGiftAttributeCounter as StarGiftAttributeCounter
    from ._root import StarGiftAttributeIdBackdrop as StarGiftAttributeIdBackdrop
    from ._root import StarGiftAttributeIdModel as StarGiftAttributeIdModel
    from ._root import StarGiftAttributeIdPattern as StarGiftAttributeIdPattern
    from ._root import StarGiftAttributeModel as StarGiftAttributeModel
    from ._root import StarGiftAttributeOriginalDetails as StarGiftAttributeOriginalDetails
    from ._root import StarGiftAttributePattern as StarGiftAttributePattern
    from ._root import StarGiftAttributeRarity as StarGiftAttributeRarity
    from ._root import StarGiftAttributeRarityEpic as StarGiftAttributeRarityEpic
    from ._root import StarGiftAttributeRarityLegendary as StarGiftAttributeRarityLegendary
    from ._root import StarGiftAttributeRarityRare as StarGiftAttributeRarityRare
    from ._root import StarGiftAttributeRarityUncommon as StarGiftAttributeRarityUncommon
    from ._root import StarGiftAuctionAcquiredGift as StarGiftAuctionAcquiredGift
    from ._root import StarGiftAuctionRound as StarGiftAuctionRound
    from ._root import StarGiftAuctionRoundExtendable as StarGiftAuctionRoundExtendable
    from ._root import StarGiftAuctionState as StarGiftAuctionState
    from ._root import StarGiftAuctionStateFinished as StarGiftAuctionStateFinished
    from ._root import StarGiftAuctionStateNotModified as StarGiftAuctionStateNotModified
    from ._root import StarGiftAuctionUserState as StarGiftAuctionUserState
    from ._root import StarGiftBackground as StarGiftBackground
    from ._root import StarGiftCollection as StarGiftCollection
    from ._root import StarGiftUnique as StarGiftUnique
    from ._root import StarGiftUpgradePrice as StarGiftUpgradePrice
    from ._root import StarRefProgram as StarRefProgram
    from ._root import StarsAmount as StarsAmount
    from ._root import StarsGiftOption as StarsGiftOption
    from ._root import StarsGiveawayOption as StarsGiveawayOption
    from ._root import StarsGiveawayWinnersOption as StarsGiveawayWinnersOption
    from ._root import StarsRating as StarsRating
    from ._root import StarsRevenueStatus as StarsRevenueStatus
    from ._root import StarsSubscription as StarsSubscription
    from ._root import StarsSubscriptionPricing as StarsSubscriptionPricing
    from ._root import StarsTonAmount as StarsTonAmount
    from ._root import StarsTopupOption as StarsTopupOption
    from ._root import StarsTransaction as StarsTransaction
    from ._root import StarsTransactionPeer as StarsTransactionPeer
    from ._root import StarsTransactionPeerAPI as StarsTransactionPeerAPI
    from ._root import StarsTransactionPeerAds as StarsTransactionPeerAds
    from ._root import StarsTransactionPeerAppStore as StarsTransactionPeerAppStore
    from ._root import StarsTransactionPeerFragment as StarsTransactionPeerFragment
    from ._root import StarsTransactionPeerPlayMarket as StarsTransactionPeerPlayMarket
    from ._root import StarsTransactionPeerPremiumBot as StarsTransactionPeerPremiumBot
    from ._root import StarsTransactionPeerUnsupported as StarsTransactionPeerUnsupported
    from ._root import StatsAbsValueAndPrev as StatsAbsValueAndPrev
    from ._root import StatsDateRangeDays as StatsDateRangeDays
    from ._root import StatsGraph as StatsGraph
    from ._root import StatsGraphAsync as StatsGraphAsync
    from ._root import StatsGraphError as StatsGraphError
    from ._root import StatsGroupTopAdmin as StatsGroupTopAdmin
    from ._root import StatsGroupTopInviter as StatsGroupTopInviter
    from ._root import StatsGroupTopPoster as StatsGroupTopPoster
    from ._root import StatsPercentValue as StatsPercentValue
    from ._root import StatsURL as StatsURL
    from ._root import StickerKeyword as StickerKeyword
    from ._root import StickerPack as StickerPack
    from ._root import StickerSet as StickerSet
    from ._root import StickerSetCovered as StickerSetCovered
    from ._root import StickerSetFullCovered as StickerSetFullCovered
    from ._root import StickerSetMultiCovered as StickerSetMultiCovered
    from ._root import StickerSetNoCovered as StickerSetNoCovered
    from ._root import StoriesStealthMode as StoriesStealthMode
    from ._root import StoryAlbum as StoryAlbum
    from ._root import StoryFwdHeader as StoryFwdHeader
    from ._root import StoryItem as StoryItem
    from ._root import StoryItemDeleted as StoryItemDeleted
    from ._root import StoryItemSkipped as StoryItemSkipped
    from ._root import StoryReaction as StoryReaction
    from ._root import StoryReactionPublicForward as StoryReactionPublicForward
    from ._root import StoryReactionPublicRepost as StoryReactionPublicRepost
    from ._root import StoryView as StoryView
    from ._root import StoryViewPublicForward as StoryViewPublicForward
    from ._root import StoryViewPublicRepost as StoryViewPublicRepost
    from ._root import StoryViews as StoryViews
    from ._root import SuggestedPost as SuggestedPost
    from ._root import TextAnchor as TextAnchor
    from ._root import TextAutoEmail as TextAutoEmail
    from ._root import TextAutoPhone as TextAutoPhone
    from ._root import TextAutoUrl as TextAutoUrl
    from ._root import TextBankCard as TextBankCard
    from ._root import TextBold as TextBold
    from ._root import TextBotCommand as TextBotCommand
    from ._root import TextCashtag as TextCashtag
    from ._root import TextConcat as TextConcat
    from ._root import TextCustomEmoji as TextCustomEmoji
    from ._root import TextDate as TextDate
    from ._root import TextDiff as TextDiff
    from ._root import TextEmail as TextEmail
    from ._root import TextEmpty as TextEmpty
    from ._root import TextFixed as TextFixed
    from ._root import TextHashtag as TextHashtag
    from ._root import TextImage as TextImage
    from ._root import TextItalic as TextItalic
    from ._root import TextMarked as TextMarked
    from ._root import TextMath as TextMath
    from ._root import TextMention as TextMention
    from ._root import TextMentionName as TextMentionName
    from ._root import TextPhone as TextPhone
    from ._root import TextPlain as TextPlain
    from ._root import TextSpoiler as TextSpoiler
    from ._root import TextStrike as TextStrike
    from ._root import TextSubscript as TextSubscript
    from ._root import TextSuperscript as TextSuperscript
    from ._root import TextUnderline as TextUnderline
    from ._root import TextUrl as TextUrl
    from ._root import TextWithEntities as TextWithEntities
    from ._root import Theme as Theme
    from ._root import ThemeSettings as ThemeSettings
    from ._root import Timezone as Timezone
    from ._root import TodoCompletion as TodoCompletion
    from ._root import TodoItem as TodoItem
    from ._root import TodoList as TodoList
    from ._root import TopPeer as TopPeer
    from ._root import TopPeerCategoryBotsApp as TopPeerCategoryBotsApp
    from ._root import TopPeerCategoryBotsGuestChat as TopPeerCategoryBotsGuestChat
    from ._root import TopPeerCategoryBotsInline as TopPeerCategoryBotsInline
    from ._root import TopPeerCategoryBotsPM as TopPeerCategoryBotsPM
    from ._root import TopPeerCategoryChannels as TopPeerCategoryChannels
    from ._root import TopPeerCategoryCorrespondents as TopPeerCategoryCorrespondents
    from ._root import TopPeerCategoryForwardChats as TopPeerCategoryForwardChats
    from ._root import TopPeerCategoryForwardUsers as TopPeerCategoryForwardUsers
    from ._root import TopPeerCategoryGroups as TopPeerCategoryGroups
    from ._root import TopPeerCategoryPeers as TopPeerCategoryPeers
    from ._root import TopPeerCategoryPhoneCalls as TopPeerCategoryPhoneCalls
    from ._root import UpdateAiComposeTones as UpdateAiComposeTones
    from ._root import UpdateAttachMenuBots as UpdateAttachMenuBots
    from ._root import UpdateAutoSaveSettings as UpdateAutoSaveSettings
    from ._root import UpdateBotBusinessConnect as UpdateBotBusinessConnect
    from ._root import UpdateBotCallbackQuery as UpdateBotCallbackQuery
    from ._root import UpdateBotChatBoost as UpdateBotChatBoost
    from ._root import UpdateBotChatInviteRequester as UpdateBotChatInviteRequester
    from ._root import UpdateBotCommands as UpdateBotCommands
    from ._root import UpdateBotDeleteBusinessMessage as UpdateBotDeleteBusinessMessage
    from ._root import UpdateBotEditBusinessMessage as UpdateBotEditBusinessMessage
    from ._root import UpdateBotGuestChatQuery as UpdateBotGuestChatQuery
    from ._root import UpdateBotInlineQuery as UpdateBotInlineQuery
    from ._root import UpdateBotInlineSend as UpdateBotInlineSend
    from ._root import UpdateBotMenuButton as UpdateBotMenuButton
    from ._root import UpdateBotMessageReaction as UpdateBotMessageReaction
    from ._root import UpdateBotMessageReactions as UpdateBotMessageReactions
    from ._root import UpdateBotNewBusinessMessage as UpdateBotNewBusinessMessage
    from ._root import UpdateBotPrecheckoutQuery as UpdateBotPrecheckoutQuery
    from ._root import UpdateBotPurchasedPaidMedia as UpdateBotPurchasedPaidMedia
    from ._root import UpdateBotShippingQuery as UpdateBotShippingQuery
    from ._root import UpdateBotStarsSubscription as UpdateBotStarsSubscription
    from ._root import UpdateBotStopped as UpdateBotStopped
    from ._root import UpdateBotWebhookJSON as UpdateBotWebhookJSON
    from ._root import UpdateBotWebhookJSONQuery as UpdateBotWebhookJSONQuery
    from ._root import UpdateBusinessBotCallbackQuery as UpdateBusinessBotCallbackQuery
    from ._root import UpdateChannel as UpdateChannel
    from ._root import UpdateChannelAvailableMessages as UpdateChannelAvailableMessages
    from ._root import UpdateChannelMessageForwards as UpdateChannelMessageForwards
    from ._root import UpdateChannelMessageViews as UpdateChannelMessageViews
    from ._root import UpdateChannelParticipant as UpdateChannelParticipant
    from ._root import UpdateChannelReadMessagesContents as UpdateChannelReadMessagesContents
    from ._root import UpdateChannelTooLong as UpdateChannelTooLong
    from ._root import UpdateChannelUserTyping as UpdateChannelUserTyping
    from ._root import UpdateChannelViewForumAsMessages as UpdateChannelViewForumAsMessages
    from ._root import UpdateChannelWebPage as UpdateChannelWebPage
    from ._root import UpdateChat as UpdateChat
    from ._root import UpdateChatDefaultBannedRights as UpdateChatDefaultBannedRights
    from ._root import UpdateChatParticipant as UpdateChatParticipant
    from ._root import UpdateChatParticipantAdd as UpdateChatParticipantAdd
    from ._root import UpdateChatParticipantAdmin as UpdateChatParticipantAdmin
    from ._root import UpdateChatParticipantDelete as UpdateChatParticipantDelete
    from ._root import UpdateChatParticipantRank as UpdateChatParticipantRank
    from ._root import UpdateChatParticipants as UpdateChatParticipants
    from ._root import UpdateChatUserTyping as UpdateChatUserTyping
    from ._root import UpdateConfig as UpdateConfig
    from ._root import UpdateContactsReset as UpdateContactsReset
    from ._root import UpdateDcOptions as UpdateDcOptions
    from ._root import UpdateDeleteChannelMessages as UpdateDeleteChannelMessages
    from ._root import UpdateDeleteEphemeralMessages as UpdateDeleteEphemeralMessages
    from ._root import UpdateDeleteGroupCallMessages as UpdateDeleteGroupCallMessages
    from ._root import UpdateDeleteMessages as UpdateDeleteMessages
    from ._root import UpdateDeleteQuickReply as UpdateDeleteQuickReply
    from ._root import UpdateDeleteQuickReplyMessages as UpdateDeleteQuickReplyMessages
    from ._root import UpdateDeleteScheduledMessages as UpdateDeleteScheduledMessages
    from ._root import UpdateDialogFilter as UpdateDialogFilter
    from ._root import UpdateDialogFilterOrder as UpdateDialogFilterOrder
    from ._root import UpdateDialogFilters as UpdateDialogFilters
    from ._root import UpdateDialogPinned as UpdateDialogPinned
    from ._root import UpdateDialogUnreadMark as UpdateDialogUnreadMark
    from ._root import UpdateDraftMessage as UpdateDraftMessage
    from ._root import UpdateEditChannelMessage as UpdateEditChannelMessage
    from ._root import UpdateEditEphemeralMessage as UpdateEditEphemeralMessage
    from ._root import UpdateEditMessage as UpdateEditMessage
    from ._root import UpdateEmojiGameInfo as UpdateEmojiGameInfo
    from ._root import UpdateEncryptedChatTyping as UpdateEncryptedChatTyping
    from ._root import UpdateEncryptedMessagesRead as UpdateEncryptedMessagesRead
    from ._root import UpdateEncryption as UpdateEncryption
    from ._root import UpdateFavedStickers as UpdateFavedStickers
    from ._root import UpdateFolderPeers as UpdateFolderPeers
    from ._root import UpdateGeoLiveViewed as UpdateGeoLiveViewed
    from ._root import UpdateGroupCall as UpdateGroupCall
    from ._root import UpdateGroupCallChainBlocks as UpdateGroupCallChainBlocks
    from ._root import UpdateGroupCallConnection as UpdateGroupCallConnection
    from ._root import UpdateGroupCallEncryptedMessage as UpdateGroupCallEncryptedMessage
    from ._root import UpdateGroupCallMessage as UpdateGroupCallMessage
    from ._root import UpdateGroupCallParticipants as UpdateGroupCallParticipants
    from ._root import UpdateInlineBotCallbackQuery as UpdateInlineBotCallbackQuery
    from ._root import UpdateJoinChatWebViewDecision as UpdateJoinChatWebViewDecision
    from ._root import UpdateLangPack as UpdateLangPack
    from ._root import UpdateLangPackTooLong as UpdateLangPackTooLong
    from ._root import UpdateLoginToken as UpdateLoginToken
    from ._root import UpdateManagedBot as UpdateManagedBot
    from ._root import UpdateMessageExtendedMedia as UpdateMessageExtendedMedia
    from ._root import UpdateMessageID as UpdateMessageID
    from ._root import UpdateMessagePoll as UpdateMessagePoll
    from ._root import UpdateMessagePollVote as UpdateMessagePollVote
    from ._root import UpdateMessageReactions as UpdateMessageReactions
    from ._root import UpdateMonoForumNoPaidException as UpdateMonoForumNoPaidException
    from ._root import UpdateMoveStickerSetToTop as UpdateMoveStickerSetToTop
    from ._root import UpdateNewAuthorization as UpdateNewAuthorization
    from ._root import UpdateNewBotConnection as UpdateNewBotConnection
    from ._root import UpdateNewChannelMessage as UpdateNewChannelMessage
    from ._root import UpdateNewEncryptedMessage as UpdateNewEncryptedMessage
    from ._root import UpdateNewEphemeralMessage as UpdateNewEphemeralMessage
    from ._root import UpdateNewMessage as UpdateNewMessage
    from ._root import UpdateNewQuickReply as UpdateNewQuickReply
    from ._root import UpdateNewScheduledMessage as UpdateNewScheduledMessage
    from ._root import UpdateNewStickerSet as UpdateNewStickerSet
    from ._root import UpdateNewStoryReaction as UpdateNewStoryReaction
    from ._root import UpdateNotifySettings as UpdateNotifySettings
    from ._root import UpdatePaidReactionPrivacy as UpdatePaidReactionPrivacy
    from ._root import UpdatePeerBlocked as UpdatePeerBlocked
    from ._root import UpdatePeerHistoryTTL as UpdatePeerHistoryTTL
    from ._root import UpdatePeerLocated as UpdatePeerLocated
    from ._root import UpdatePeerSettings as UpdatePeerSettings
    from ._root import UpdatePeerWallpaper as UpdatePeerWallpaper
    from ._root import UpdatePendingJoinRequests as UpdatePendingJoinRequests
    from ._root import UpdatePhoneCall as UpdatePhoneCall
    from ._root import UpdatePhoneCallSignalingData as UpdatePhoneCallSignalingData
    from ._root import UpdatePinnedChannelMessages as UpdatePinnedChannelMessages
    from ._root import UpdatePinnedDialogs as UpdatePinnedDialogs
    from ._root import UpdatePinnedForumTopic as UpdatePinnedForumTopic
    from ._root import UpdatePinnedForumTopics as UpdatePinnedForumTopics
    from ._root import UpdatePinnedMessages as UpdatePinnedMessages
    from ._root import UpdatePinnedSavedDialogs as UpdatePinnedSavedDialogs
    from ._root import UpdatePrivacy as UpdatePrivacy
    from ._root import UpdatePtsChanged as UpdatePtsChanged
    from ._root import UpdateQuickReplies as UpdateQuickReplies
    from ._root import UpdateQuickReplyMessage as UpdateQuickReplyMessage
    from ._root import UpdateReadChannelDiscussionInbox as UpdateReadChannelDiscussionInbox
    from ._root import UpdateReadChannelDiscussionOutbox as UpdateReadChannelDiscussionOutbox
    from ._root import UpdateReadChannelInbox as UpdateReadChannelInbox
    from ._root import UpdateReadChannelOutbox as UpdateReadChannelOutbox
    from ._root import UpdateReadFeaturedEmojiStickers as UpdateReadFeaturedEmojiStickers
    from ._root import UpdateReadFeaturedStickers as UpdateReadFeaturedStickers
    from ._root import UpdateReadHistoryInbox as UpdateReadHistoryInbox
    from ._root import UpdateReadHistoryOutbox as UpdateReadHistoryOutbox
    from ._root import UpdateReadMessagesContents as UpdateReadMessagesContents
    from ._root import UpdateReadMonoForumInbox as UpdateReadMonoForumInbox
    from ._root import UpdateReadMonoForumOutbox as UpdateReadMonoForumOutbox
    from ._root import UpdateReadStories as UpdateReadStories
    from ._root import UpdateRecentEmojiStatuses as UpdateRecentEmojiStatuses
    from ._root import UpdateRecentReactions as UpdateRecentReactions
    from ._root import UpdateRecentStickers as UpdateRecentStickers
    from ._root import UpdateSavedDialogPinned as UpdateSavedDialogPinned
    from ._root import UpdateSavedGifs as UpdateSavedGifs
    from ._root import UpdateSavedReactionTags as UpdateSavedReactionTags
    from ._root import UpdateSavedRingtones as UpdateSavedRingtones
    from ._root import UpdateSentPhoneCode as UpdateSentPhoneCode
    from ._root import UpdateSentStoryReaction as UpdateSentStoryReaction
    from ._root import UpdateServiceNotification as UpdateServiceNotification
    from ._root import UpdateShort as UpdateShort
    from ._root import UpdateShortChatMessage as UpdateShortChatMessage
    from ._root import UpdateShortMessage as UpdateShortMessage
    from ._root import UpdateShortSentMessage as UpdateShortSentMessage
    from ._root import UpdateSmsJob as UpdateSmsJob
    from ._root import UpdateStarGiftAuctionState as UpdateStarGiftAuctionState
    from ._root import UpdateStarGiftAuctionUserState as UpdateStarGiftAuctionUserState
    from ._root import UpdateStarGiftCraftFail as UpdateStarGiftCraftFail
    from ._root import UpdateStarsBalance as UpdateStarsBalance
    from ._root import UpdateStarsRevenueStatus as UpdateStarsRevenueStatus
    from ._root import UpdateStickerSets as UpdateStickerSets
    from ._root import UpdateStickerSetsOrder as UpdateStickerSetsOrder
    from ._root import UpdateStoriesStealthMode as UpdateStoriesStealthMode
    from ._root import UpdateStory as UpdateStory
    from ._root import UpdateStoryID as UpdateStoryID
    from ._root import UpdateTheme as UpdateTheme
    from ._root import UpdateTranscribedAudio as UpdateTranscribedAudio
    from ._root import UpdateUser as UpdateUser
    from ._root import UpdateUserEmojiStatus as UpdateUserEmojiStatus
    from ._root import UpdateUserName as UpdateUserName
    from ._root import UpdateUserPhone as UpdateUserPhone
    from ._root import UpdateUserStatus as UpdateUserStatus
    from ._root import UpdateUserTyping as UpdateUserTyping
    from ._root import UpdateWebBrowserException as UpdateWebBrowserException
    from ._root import UpdateWebBrowserSettings as UpdateWebBrowserSettings
    from ._root import UpdateWebPage as UpdateWebPage
    from ._root import UpdateWebViewResultSent as UpdateWebViewResultSent
    from ._root import Updates as Updates
    from ._root import UpdatesCombined as UpdatesCombined
    from ._root import UpdatesTooLong as UpdatesTooLong
    from ._root import UrlAuthResultAccepted as UrlAuthResultAccepted
    from ._root import UrlAuthResultDefault as UrlAuthResultDefault
    from ._root import UrlAuthResultRequest as UrlAuthResultRequest
    from ._root import User as User
    from ._root import UserEmpty as UserEmpty
    from ._root import UserFull as UserFull
    from ._root import UserProfilePhoto as UserProfilePhoto
    from ._root import UserProfilePhotoEmpty as UserProfilePhotoEmpty
    from ._root import UserStatusEmpty as UserStatusEmpty
    from ._root import UserStatusLastMonth as UserStatusLastMonth
    from ._root import UserStatusLastWeek as UserStatusLastWeek
    from ._root import UserStatusOffline as UserStatusOffline
    from ._root import UserStatusOnline as UserStatusOnline
    from ._root import UserStatusRecently as UserStatusRecently
    from ._root import Username as Username
    from ._root import VideoSize as VideoSize
    from ._root import VideoSizeEmojiMarkup as VideoSizeEmojiMarkup
    from ._root import VideoSizeStickerMarkup as VideoSizeStickerMarkup
    from ._root import WallPaper as WallPaper
    from ._root import WallPaperNoFile as WallPaperNoFile
    from ._root import WallPaperSettings as WallPaperSettings
    from ._root import WebAuthorization as WebAuthorization
    from ._root import WebDocument as WebDocument
    from ._root import WebDocumentNoProxy as WebDocumentNoProxy
    from ._root import WebDomainException as WebDomainException
    from ._root import WebPage as WebPage
    from ._root import WebPageAttributeAiComposeTone as WebPageAttributeAiComposeTone
    from ._root import WebPageAttributeStarGiftAuction as WebPageAttributeStarGiftAuction
    from ._root import WebPageAttributeStarGiftCollection as WebPageAttributeStarGiftCollection
    from ._root import WebPageAttributeStickerSet as WebPageAttributeStickerSet
    from ._root import WebPageAttributeStory as WebPageAttributeStory
    from ._root import WebPageAttributeTheme as WebPageAttributeTheme
    from ._root import WebPageAttributeUniqueStarGift as WebPageAttributeUniqueStarGift
    from ._root import WebPageEmpty as WebPageEmpty
    from ._root import WebPageNotModified as WebPageNotModified
    from ._root import WebPagePending as WebPagePending
    from ._root import WebViewMessageSent as WebViewMessageSent
    from ._root import WebViewResultUrl as WebViewResultUrl
else:
    _NAMESPACES = frozenset({'account', 'aicompose', 'auth', 'bots', 'channels', 'chatlists', 'communities', 'contacts', 'fragment', 'help', 'messages', 'mtproto', 'payments', 'phone', 'photos', 'premium', 'smsjobs', 'stats', 'stickers', 'storage', 'stories', 'updates', 'upload', 'users'})
    _EXPORTED = frozenset(__all__)

    def __getattr__(name: str) -> Any:
        if name in _NAMESPACES:
            value: Any = import_module(f".{name}", __name__)
        elif name in _EXPORTED:
            value = getattr(import_module("._root", __name__), name)
        else:
            raise AttributeError(
                f"module {__name__!r} has no attribute {name!r}"
            )
        globals()[name] = value
        return value

    def __dir__() -> list[str]:
        # PEP 562 pairs __getattr__ with a __dir__. Without one, dir()
        # and a REPL's tab completion see only what has already been
        # imported, which on a fresh interpreter is nothing, and this
        # is the layer docs/raw-api.md sends people to. Naming the
        # names imports none of them, so rule P7 is untouched.
        return sorted(set(globals()) | _EXPORTED | _NAMESPACES)
