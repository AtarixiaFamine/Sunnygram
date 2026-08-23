# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Generated from Telegram's error table at layer 227. Do not edit by
# hand; run codegen/gen_errors.py instead.
"""Every error Telegram documents, one class each.

The name is what to catch: except PeerIdInvalid says what went wrong far
better than reading a string out of an exception does. Each one hangs off
the class for its status code, so except BadRequest still catches the
hundreds of ways a call can be wrong, and except RPCError catches the lot.

An error whose name carries a number fills in value, and the classes that
make something of it, waiting or migrating, are hand-written in rpc.py.
"""

from __future__ import annotations

import re

from .rpc import (
    AuthTokenExpired,
    AuthTokenInvalid,
    BadRequest,
    FileMigrate,
    Flood,
    FloodWait,
    Forbidden,
    InternalError,
    NetworkMigrate,
    NotAcceptable,
    PasswordHashInvalid,
    PhoneCodeExpired,
    PhoneCodeInvalid,
    PhoneMigrate,
    PhoneNumberInvalid,
    RPCError,
    SessionPasswordNeeded,
    SlowmodeWait,
    StatsMigrate,
    TakeoutInitDelay,
    Timeout,
    Unauthorized,
    UserMigrate,
)


class AboutTooLong(BadRequest):
    """About string too long."""


class AccessDenied(Forbidden):
    """The account was deactivated, or is a bot/service account."""


class AccessTokenExpired(BadRequest):
    """Access token expired."""


class AccessTokenInvalid(BadRequest):
    """Access token invalid."""


class AdExpired(BadRequest):
    """The ad has expired (too old or not found)."""


class AddressInvalid(Flood):
    """The specified geopoint address is invalid."""


class AdminIdInvalid(BadRequest):
    """The specified admin ID is invalid."""


class AdminRankEmojiNotAllowed(BadRequest):
    """An admin rank cannot contain emojis."""


class AdminRankInvalid(BadRequest):
    """The specified admin rank is invalid."""


class AdminRightsEmpty(BadRequest):
    """The chatAdminRights constructor passed in
    keyboardButtonRequestPeer.peer_type.user_admin_rights has no rights set (i.e. flags
    is 0).
    """


class AdminsTooMuch(BadRequest):
    """There are too many admins."""


class AiComposeTaskMissing(BadRequest):
    """No AI task was specified. The caller must provide at least one of: proofread,
    translate (with a target language), tone, or emojify.
    """


class AicomposeFloodPremium(BadRequest):
    """You've reached the daily limit of AI text transformations, upgrade to Telegram
    Premium to get **50x** times more AI text transformations per day!
    """


class AicomposeTimeout(InternalError):
    """A timeout occurred while composing the message."""


class AicomposeToneInvalid(BadRequest):
    """The specified tone is invalid."""


class AicomposeToneTitleInvalid(BadRequest):
    """The specified tone title is invalid."""


class AlbumPhotosTooMany(BadRequest):
    """You have uploaded too many profile photos, delete some before retrying."""


class AllowPaymentRequired(Forbidden):
    """This peer only accepts paid messages »: this error is only emitted for older
    layers without paid messages support, so the client must be updated in order to use
    paid messages. This peer charges %d Telegram Stars per message, but the
    `allow_paid_stars` was not set or its value is smaller than %d.
    """


class ApiGiftRestrictedUpdateApp(NotAcceptable):
    """Please update the app to access the gift API."""


class ApiIdInvalid(BadRequest):
    """API ID invalid."""


class ApiIdPublishedFlood(BadRequest):
    """This API id was published somewhere, you can't use it now."""


class ArticleTitleEmpty(BadRequest):
    """The title of the article is empty."""


class AudioContentUrlEmpty(BadRequest):
    """The remote URL specified in the content field is empty."""


class AudioTitleEmpty(BadRequest):
    """An empty audio title was provided."""


class AuthBytesInvalid(BadRequest):
    """The provided authorization is invalid."""


class AuthKeyDuplicated(NotAcceptable):
    """Concurrent usage of the current session from multiple connections was detected,
    the current session was invalidated by the server for security reasons!
    """


class AuthKeyInvalid(Unauthorized):
    """The specified auth key is invalid."""


class AuthKeyPermEmpty(Unauthorized):
    """The method is unavailable for temporary authorization keys, not bound to a
    permanent authorization key.
    """


class AuthKeyUnregistered(Unauthorized):
    """The specified authorization key is not registered in the system (for example, a
    PFS temporary key has expired).
    """


class AuthKeyUnsynchronized(InternalError):
    """Internal error, please repeat the method call."""


class AuthRestart(InternalError):
    """Restart the authorization process. Internal error (debug info %d), please repeat
    the method call.
    """


class AuthTokenAlreadyAccepted(BadRequest):
    """The specified auth token was already accepted."""


class AuthTokenException(BadRequest):
    """An error occurred while importing the auth token."""


class AuthTokenInvalidx(BadRequest):
    """The specified auth token is invalid."""


class AutoarchiveNotAvailable(BadRequest):
    """The autoarchive setting is not available at this time: please check the value of
    the autoarchive_setting_available field in client config » before calling this
    method.
    """


class BalanceTooLow(BadRequest):
    """The transaction cannot be completed because the current Telegram Stars balance is
    too low.
    """


class BankCardNumberInvalid(BadRequest):
    """The specified card number is invalid."""


class BannedRightsInvalid(NotAcceptable):
    """You provided some invalid flags in the banned rights."""


class BirthdayAlready(BadRequest):
    """The target user already has a birthday set."""


class BirthdayInvalid(BadRequest):
    """An invalid age was specified, must be between 0 and 150 years."""


class BoostNotModified(BadRequest):
    """You're already boosting the specified channel."""


class BoostPeerInvalid(BadRequest):
    """The specified `boost_peer` is invalid."""


class BoostsEmpty(BadRequest):
    """No boost slots were specified."""


class BoostsRequired(BadRequest):
    """The specified channel must first be boosted by its users in order to perform this
    action.
    """


class BotAccessForbidden(Forbidden):
    """The specified method *can* be used over a business connection for some
    operations, but the specified query attempted an operation that is not allowed over
    a business connection.
    """


class BotAlreadyDisabled(BadRequest):
    """The connected business bot was already disabled for the specified peer."""


class BotAppBotInvalid(BadRequest):
    """The bot_id passed in the inputBotAppShortName constructor is invalid."""


class BotAppInvalid(BadRequest):
    """The specified bot app is invalid."""


class BotAppShortnameInvalid(BadRequest):
    """The specified bot app short name is invalid."""


class BotBusinessMissing(BadRequest):
    """The specified bot is not a business bot (the user.`bot_business` flag is not
    set).
    """


class BotChannelsNa(BadRequest):
    """Bots can't edit admin privileges."""


class BotCommandDescriptionInvalid(BadRequest):
    """The specified command description is invalid."""


class BotCommandInvalid(BadRequest):
    """The specified command is invalid."""


class BotCreateLimitExceeded(BadRequest):
    """The current user already owns the maximum allowed number of owned bots, as
    specified by `bots_create_limit_default` » and `bots_create_limit_premium` »; if the
    current user doesn't have Telegram Premium, upgrading to Premium will allow them to
    create more bots.
    """


class BotDomainInvalid(BadRequest):
    """Bot domain invalid."""


class BotFallbackUnsupported(BadRequest):
    """The fallback flag can't be set for bots."""


class BotForumCreateForbidden(Forbidden):
    """Since the bot's user.bot_forum_can_manage_topics flag is **not** set, the user
    cannot create or modify bot forum topics.
    """


class BotGamesDisabled(BadRequest):
    """Games can't be sent to channels."""


class BotGroupsBlocked(BadRequest):
    """This bot can't be added to groups."""


class BotGuardNotSupported(Forbidden):
    """This bot is not designated as a "join guard" bot. This method is only available
    to bots that mediate user joins to chats.
    """


class BotIdInvalid(BadRequest):
    """The specified bot ID is invalid."""


class BotInlineDisabled(BadRequest):
    """This bot can't be used in inline mode."""


class BotInvalid(BadRequest):
    """This is not a valid bot."""


class BotInvoiceInvalid(BadRequest):
    """The specified invoice is invalid."""


class BotMethodInvalid(BadRequest):
    """The specified method cannot be used by bots."""


class BotNotConnectedYet(BadRequest):
    """No business bot is connected to the currently logged in user."""


class BotOnesideNotAvail(BadRequest):
    """Bots can't pin messages in PM just for themselves."""


class BotPaymentsDisabled(BadRequest):
    """Please enable bot payments in botfather before calling this method."""


class BotResponseTimeout(BadRequest):
    """A timeout occurred while fetching data from the bot."""


class BotScoreNotModified(BadRequest):
    """The score wasn't modified."""


class BotVerifierForbidden(Forbidden):
    """This bot cannot assign verification icons."""


class BotWebviewDisabled(BadRequest):
    """A webview cannot be opened in the specified conditions: emitted for example if
    `from_bot_menu` or `url` are set and `peer` is not the chat with the bot.
    """


class BotsTooMuch(BadRequest):
    """There are too many bots in this chat/channel."""


class BroadcastForbidden(Forbidden):
    """Channel poll voters and reactions cannot be fetched to prevent deanonymization.
    """


class BroadcastIdInvalid(BadRequest):
    """Broadcast ID invalid."""


class BroadcastPublicVotersForbidden(BadRequest):
    """You can't forward polls with public voters."""


class BroadcastRequired(BadRequest):
    """This method can only be called on a channel, please use stats.getMegagroupStats
    for supergroups.
    """


class BusinessAddressActive(NotAcceptable):
    """The user is currently advertising a Business Location, the location may only be
    changed (or removed) using account.updateBusinessLocation ».
    """


class BusinessConnectionInvalid(BadRequest):
    """The `connection_id` passed to the wrapping invokeWithBusinessConnection call is
    invalid.
    """


class BusinessConnectionNotAllowed(BadRequest):
    """This method was invoked over a business connection using
    invokeWithBusinessConnection, but either (1) we're a user, and users cannot invoke
    methods over a business connection; (2) we're a bot, but business mode was disabled
    in @botfather or (3); we're a bot, but this method cannot be invoked over a business
    connection.
    """


class BusinessPeerInvalid(BadRequest):
    """Messages can't be set to the specified peer through the current business
    connection.
    """


class BusinessPeerUsageMissing(BadRequest):
    """You cannot send a message to a user through a business connection if the user
    hasn't recently contacted us.
    """


class BusinessRecipientsEmpty(BadRequest):
    """You didn't set any flag in inputBusinessBotRecipients, thus the bot cannot work
    with *any* peer.
    """


class BusinessWorkHoursEmpty(BadRequest):
    """No work hours were specified."""


class BusinessWorkHoursPeriodInvalid(BadRequest):
    """The specified work hours are invalid, see here » for the exact requirements."""


class ButtonCopyTextInvalid(BadRequest):
    """The specified keyboardButtonCopy.`copy_text` is invalid."""


class ButtonDataInvalid(BadRequest):
    """The data of one or more of the buttons you provided is invalid."""


class ButtonIdInvalid(BadRequest):
    """The specified button ID is invalid."""


class ButtonInvalid(BadRequest):
    """The specified button is invalid."""


class ButtonPosInvalid(BadRequest):
    """The position of one of the keyboard buttons is invalid (i.e. a Game or Pay button
    not in the first position, and so on...).
    """


class ButtonTextInvalid(BadRequest):
    """The specified button text is invalid."""


class ButtonTypeInvalid(BadRequest):
    """The type of one or more of the buttons you provided is invalid."""


class ButtonUrlInvalid(BadRequest):
    """Button URL invalid."""


class ButtonUserInvalid(BadRequest):
    """The `user_id` passed to inputKeyboardButtonUserProfile is invalid!"""


class ButtonUserPrivacyRestricted(BadRequest):
    """The privacy setting of the user specified in a inputKeyboardButtonUserProfile
    button do not allow creating such a button.
    """


class CallAlreadyAccepted(BadRequest):
    """The call was already accepted."""


class CallAlreadyDeclined(BadRequest):
    """The call was already declined."""


class CallNotActive(BadRequest):
    """The specified call is not active."""


class CallOccupyFailed(InternalError):
    """The call failed because the user is already making another call."""


class CallPeerInvalid(BadRequest):
    """The provided call peer object is invalid."""


class CallProtocolCompatLayerInvalid(NotAcceptable):
    """The other side of the call does not support any of the VoIP protocols supported
    by the local client, as specified by the `protocol.layer` and
    `protocol.library_versions` fields.
    """


class CallProtocolFlagsInvalid(BadRequest):
    """Call protocol flags invalid."""


class CallProtocolLayerInvalid(BadRequest):
    """The specified protocol layer version range is invalid."""


class CdnMethodInvalid(BadRequest):
    """You can't call this method in a CDN DC."""


class CdnUploadTimeout(InternalError):
    """A server-side timeout occurred while reuploading the file to the CDN DC."""


class ChannelForumMissing(BadRequest):
    """This supergroup is not a forum."""


class ChannelIdInvalid(BadRequest):
    """The specified supergroup ID is invalid."""


class ChannelInvalid(BadRequest):
    """The provided channel is invalid."""


class ChannelMonoforumUnsupported(BadRequest):
    """Monoforums do not support this feature."""


class ChannelParicipantMissing(BadRequest):
    """The current user is not in the channel."""


class ChannelPrivate(BadRequest):
    """You haven't joined this channel/supergroup."""


class ChannelPublicGroupNa(Forbidden):
    """channel/supergroup not available."""


class ChannelTooBig(BadRequest):
    """This channel has too many participants (>1000) to be deleted."""


class ChannelTooLarge(NotAcceptable):
    """Channel is too large to be deleted; this error is issued when trying to delete
    channels with more than 1000 members (subject to change).
    """


class ChannelsAdminLocatedTooMuch(BadRequest):
    """The user has reached the limit of public geogroups."""


class ChannelsAdminPublicTooMuch(BadRequest):
    """You're admin of too many public channels, make some channels private to change
    the username of this channel.
    """


class ChannelsTooMuch(BadRequest):
    """You have joined too many channels/supergroups."""


class ChargeAlreadyRefunded(BadRequest):
    """The transaction was already refunded."""


class ChargeIdEmpty(BadRequest):
    """The specified charge_id is empty."""


class ChargeIdInvalid(BadRequest):
    """The specified charge_id is invalid."""


class ChatAboutNotModified(BadRequest):
    """About text has not changed."""


class ChatAboutTooLong(BadRequest):
    """Chat about too long."""


class ChatActionForbidden(Forbidden):
    """You cannot execute this action."""


class ChatAdminInviteRequired(Forbidden):
    """You do not have the rights to do this."""


class ChatAdminRequired(BadRequest):
    """You must be an admin in this chat to do this."""


class ChatDiscussionUnallowed(BadRequest):
    """You can't enable forum topics in a discussion group linked to a channel."""


class ChatForbidden(Forbidden):
    """This chat is not available to the current user."""


class ChatForwardsRestricted(BadRequest):
    """You can't forward messages from a protected chat."""


class ChatGuestSendForbidden(Forbidden):
    """You join the discussion group before commenting, see here » for more info."""


class ChatIdEmpty(BadRequest):
    """The provided chat ID is empty."""


class ChatIdGenerateFailed(InternalError):
    """Failure while generating the chat ID."""


class ChatIdInvalid(BadRequest):
    """The provided chat id is invalid."""


class ChatInvalid(BadRequest):
    """Invalid chat."""


class ChatInvitePermanent(BadRequest):
    """You can't set an expiration date on permanent invite links."""


class ChatLinkExists(BadRequest):
    """The chat is public, you can't hide the history to new users."""


class ChatMemberAddFailed(BadRequest):
    """Could not add participants."""


class ChatNotModified(BadRequest):
    """No changes were made to chat information because the new information you passed
    is identical to the current information.
    """


class ChatPublicRequired(BadRequest):
    """You can only enable join requests in public groups."""


class ChatRestricted(BadRequest):
    """You can't send messages in this chat, you were restricted."""


class ChatRevokeDateUnsupported(BadRequest):
    """`min_date` and `max_date` are not available for using with non-user peers."""


class ChatSendAudiosForbidden(Forbidden):
    """You can't send audio messages in this chat."""


class ChatSendDocsForbidden(Forbidden):
    """You can't send documents in this chat."""


class ChatSendGameForbidden(Forbidden):
    """You can't send a game to this chat."""


class ChatSendGifsForbidden(Forbidden):
    """You can't send gifs in this chat."""


class ChatSendInlineForbidden(Forbidden):
    """You can't send inline messages in this group."""


class ChatSendMediaForbidden(Forbidden):
    """You can't send media in this chat."""


class ChatSendPhotosForbidden(Forbidden):
    """You can't send photos in this chat."""


class ChatSendPlainForbidden(Forbidden):
    """You can't send non-media (text) messages in this chat."""


class ChatSendPollForbidden(Forbidden):
    """You can't send polls in this chat."""


class ChatSendRoundvideosForbidden(Forbidden):
    """You can't send round videos to this chat."""


class ChatSendStickersForbidden(Forbidden):
    """You can't send stickers in this chat."""


class ChatSendVideosForbidden(Forbidden):
    """You can't send videos in this chat."""


class ChatSendVoicesForbidden(Forbidden):
    """You can't send voice recordings in this chat."""


class ChatSendWebpageForbidden(Forbidden):
    """You can't send webpage previews to this chat."""


class ChatTitleEmpty(BadRequest):
    """No chat title provided."""


class ChatTooBig(BadRequest):
    """This method is not available for groups with more than
    `chat_read_mark_size_threshold` members, see client configuration ».
    """


class ChatTypeInvalid(Forbidden):
    """The specified user type is invalid."""


class ChatWriteForbidden(Forbidden):
    """You can't write in this chat."""


class ChatlinkSlugEmpty(BadRequest):
    """The specified slug is empty."""


class ChatlinkSlugExpired(BadRequest):
    """The specified business chat link has expired."""


class ChatlinksTooMuch(BadRequest):
    """Too many business chat links were created, please delete some older links."""


class ChatlistExcludeInvalid(BadRequest):
    """The specified `exclude_peers` are invalid."""


class ChatlistsTooMuch(BadRequest):
    """You have created too many folder links, hitting the
    `chatlist_invites_limit_default`/`chatlist_invites_limit_premium` limits ».
    """


class CodeEmpty(BadRequest):
    """The provided code is empty."""


class CodeHashInvalid(BadRequest):
    """Code hash invalid."""


class CodeInvalid(BadRequest):
    """Code invalid."""


class CollectibleInvalid(BadRequest):
    """The specified collectible is invalid."""


class CollectibleNotFound(BadRequest):
    """The specified collectible could not be found."""


class CollectionIdInvalid(BadRequest):
    """The specified collection ID is invalid."""


class ColorInvalid(BadRequest):
    """The specified color palette ID was invalid."""


class ConnectionApiIdInvalid(BadRequest):
    """The provided API id is invalid."""


class ConnectionAppVersionEmpty(BadRequest):
    """App version is empty."""


class ConnectionDeviceModelEmpty(BadRequest):
    """The specified device model is empty."""


class ConnectionIdInvalid(BadRequest):
    """The specified connection ID is invalid."""


class ConnectionLangPackInvalid(BadRequest):
    """The specified language pack is empty."""


class ConnectionLayerInvalid(BadRequest):
    """Layer invalid."""


class ConnectionNotInited(BadRequest):
    """Please initialize the connection using initConnection before making queries."""


class ConnectionSystemEmpty(BadRequest):
    """The specified system version is empty."""


class ConnectionSystemLangCodeEmpty(BadRequest):
    """The specified system language code is empty."""


class ContactAddMissing(BadRequest):
    """Contact to add is missing."""


class ContactIdInvalid(BadRequest):
    """The provided contact ID is invalid."""


class ContactMissing(BadRequest):
    """The specified user is not a contact."""


class ContactNameEmpty(BadRequest):
    """Contact name empty."""


class ContactReqMissing(BadRequest):
    """Missing contact request."""


class CreateCallFailed(BadRequest):
    """An error occurred while creating the call."""


class CredentialInvalid(BadRequest):
    """The specified credential is invalid."""


class CurrencyTotalAmountInvalid(BadRequest):
    """The total amount of all prices is invalid."""


class CustomReactionsTooMany(BadRequest):
    """Too many custom reactions were specified."""


class DataHashSizeInvalid(BadRequest):
    """The size of the specified secureValueErrorData.data_hash is invalid."""


class DataInvalid(BadRequest):
    """Encrypted data invalid."""


class DataJsonInvalid(BadRequest):
    """The provided JSON data is invalid."""


class DataTooLong(BadRequest):
    """Data too long."""


class DateEmpty(BadRequest):
    """Date empty."""


class DcIdInvalid(BadRequest):
    """The provided DC ID is invalid."""


class DhGAInvalid(BadRequest):
    """g_a invalid."""


class DocumentInvalid(BadRequest):
    """The specified document is invalid."""


class EditBotInviteForbidden(Forbidden):
    """Normal users can't edit invites that were created by bots."""


class EditMessageTempRestricted(NotAcceptable):
    """Message editing is temporarily forbidden for this user due to regulatory
    restrictions.
    """


class EffectChatInvalid(BadRequest):
    """Message effects can only be used in private 1-on-1 chats, but the caller tried to
    send a message with an effect to a group or channel.
    """


class EffectIdInvalid(BadRequest):
    """The specified effect ID is invalid."""


class EmailHashExpired(BadRequest):
    """Email hash expired."""


class EmailInstallMissing(BadRequest):
    """Attempting to send a code to the recovery email, but no email is configured."""


class EmailInvalid(BadRequest):
    """The specified email is invalid."""


class EmailNotAllowed(BadRequest):
    """The specified email cannot be used to complete the operation."""


class EmailNotSetup(BadRequest):
    """In order to change the login email with emailVerifyPurposeLoginChange, an
    existing login email must already be set using emailVerifyPurposeLoginSetup.
    """


class EmailUnconfirmed(BadRequest):
    """Email unconfirmed. The provided email isn't confirmed, %d is the length of the
    verification code that was just sent to the email: use account.verifyEmail to enter
    the received verification code and enable the recovery email.
    """


class EmailVerifyExpired(BadRequest):
    """The verification email has expired."""


class EmojiInvalid(BadRequest):
    """The specified theme emoji is valid."""


class EmojiMarkupInvalid(BadRequest):
    """The specified `video_emoji_markup` was invalid."""


class EmojiNotModified(BadRequest):
    """The theme wasn't changed."""


class EmoticonEmpty(BadRequest):
    """The emoji is empty."""


class EmoticonInvalid(BadRequest):
    """The specified emoji is invalid."""


class EmoticonStickerpackMissing(BadRequest):
    """inputStickerSetDice.emoji cannot be empty."""


class EncryptedMessageInvalid(BadRequest):
    """Encrypted message invalid."""


class EncryptionAlreadyAccepted(BadRequest):
    """Secret chat already accepted."""


class EncryptionAlreadyDeclined(BadRequest):
    """The secret chat was already declined."""


class EncryptionDeclined(BadRequest):
    """The secret chat was declined."""


class EncryptionIdInvalid(BadRequest):
    """The provided secret chat ID is invalid."""


class EntitiesTooLong(BadRequest):
    """You provided too many styled message entities."""


class EntityBoundsInvalid(BadRequest):
    """A specified entity offset or length is invalid, see here » for info on how to
    properly compute the entity offset/length.
    """


class EntityDateFormatInvalid(BadRequest):
    """One of the passed messageEntityFormattedDate objects has an invalid format (i.e.
    an invalid combination of the format flags).
    """


class EntityDateInvalid(BadRequest):
    """One of the passed messageEntityFormattedDate objects has an invalid date: the
    allowed value ranges from `0` to the current date plus 1098 days
    (`time()+1098*86400`).
    """


class EntityDateTooLong(BadRequest):
    """The maximum text span that can be covered by a date entity is 31 UTF-16 code
    units if any of the date formatting flags is set, or 127 UTF-16 code units without.
    """


class EntityMentionUserInvalid(BadRequest):
    """You mentioned an invalid user."""


class ErrorTextEmpty(BadRequest):
    """The provided error message is empty."""


class ExpireDateInvalid(BadRequest):
    """The specified expiration date is invalid."""


class ExpiresAtInvalid(BadRequest):
    """The specified `expires_at` timestamp is invalid."""


class ExportCardInvalid(BadRequest):
    """Provided card is invalid."""


class ExtendedMediaAmountInvalid(BadRequest):
    """The specified `stars_amount` of the passed inputMediaPaidMedia is invalid."""


class ExtendedMediaEmpty(BadRequest):
    """The specified extended media is empty."""


class ExtendedMediaInvalid(BadRequest):
    """The specified paid media is invalid."""


class ExtendedMediaPeerInvalid(BadRequest):
    """Paid media is not allowed for the target peer."""


class ExternalUrlInvalid(BadRequest):
    """External URL invalid."""


class FileContentTypeInvalid(BadRequest):
    """File content-type is invalid."""


class FileEmtpy(BadRequest):
    """An empty file was provided."""


class FileIdInvalid(BadRequest):
    """The provided file id is invalid."""


class FilePartEmpty(BadRequest):
    """The provided file part is empty."""


class FilePartInvalid(BadRequest):
    """The file part number is invalid."""


class FilePartLengthInvalid(BadRequest):
    """The length of a file part is invalid."""


class FilePartMissing(BadRequest):
    """Part %d of the file is missing from storage. Try repeating the method call to
    resave the part.
    """


class FilePartSizeChanged(BadRequest):
    """Provided file part size has changed."""


class FilePartSizeInvalid(BadRequest):
    """The provided file part size is invalid."""


class FilePartTooBig(BadRequest):
    """The uploaded file part is too big."""


class FilePartTooSmall(BadRequest):
    """The size of the uploaded file part is too small, please see the documentation for
    the allowed sizes.
    """


class FilePartsInvalid(BadRequest):
    """The number of file parts is invalid."""


class FileReferenceEmpty(BadRequest):
    """The file reference of the media file at offset %d in the multi_media array is
    invalid. An empty file reference was specified.
    """


class FileReferenceExpired(BadRequest):
    """The file reference of the media file at index %d in the passed media array
    expired, it must be refreshed as specified in the documentation. File reference
    expired, it must be refetched as described in the documentation.
    """


class FileReferenceInvalid(BadRequest):
    """The file reference of the media file at index %d in the passed media array is
    invalid. The specified file reference is invalid.
    """


class FileTitleEmpty(BadRequest):
    """An empty file title was specified."""


class FileTokenInvalid(BadRequest):
    """The master DC did not accept the `file_token` (e.g., the token has expired).
    Continue downloading the file from the master DC using upload.getFile.
    """


class FilerefUpgradeNeeded(NotAcceptable):
    """The client has to be updated in order to support file references."""


class FilterIdInvalid(BadRequest):
    """The specified filter ID is invalid."""


class FilterIncludeEmpty(BadRequest):
    """The include_peers vector of the filter is empty."""


class FilterNotSupported(BadRequest):
    """The specified filter cannot be used in this context."""


class FilterTitleEmpty(BadRequest):
    """The title field of the filter is empty."""


class FirstnameInvalid(BadRequest):
    """The first name is invalid."""


class FloodPremiumWait(FloodWait):
    """Please wait %d seconds before repeating the action, or purchase a Telegram
    Premium subscription to remove this rate limit.
    """


class FolderIdEmpty(BadRequest):
    """An empty folder ID was specified."""


class FolderIdInvalid(BadRequest):
    """Invalid folder ID."""


class FormExpired(BadRequest):
    """The form was generated more than 10 minutes ago and has expired, please re-
    generate it using payments.getPaymentForm and pass the new `form_id`.
    """


class FormIdEmpty(BadRequest):
    """The specified form ID is empty."""


class FormSubmitDuplicate(BadRequest):
    """The same payment form was already submitted."""


class FormUnsupported(BadRequest):
    """Please update your client."""


class ForumEnabled(BadRequest):
    """You can't execute the specified action because the group is a forum, disable
    forum functionality to continue.
    """


class FreshChangeAdminsForbidden(NotAcceptable):
    """You were just elected admin, you can't add or modify other admins yet."""


class FreshChangePhoneForbidden(NotAcceptable):
    """You can't change phone number right after logging in, please wait at least 24
    hours.
    """


class FreshResetAuthorisationForbidden(NotAcceptable):
    """You can't logout other sessions if less than 24 hours have passed since you
    logged on the current session.
    """


class FromMessageBotDisabled(BadRequest):
    """Bots can't use fromMessage min constructors."""


class FromPeerInvalid(BadRequest):
    """The specified from_id is invalid."""


class FrozenMethodInvalid(Flood):
    """The current account is frozen, and thus cannot execute the specified action."""


class FrozenParticipantMissing(BadRequest):
    """The current account is frozen, and cannot access the specified peer."""


class GameBotInvalid(BadRequest):
    """Bots can't send another bot's game."""


class GeneralModifyIconForbidden(BadRequest):
    """You can't modify the icon of the "General" topic."""


class GeoPointInvalid(BadRequest):
    """Invalid geoposition provided."""


class GifContentTypeInvalid(BadRequest):
    """GIF content-type invalid."""


class GifIdInvalid(BadRequest):
    """The provided GIF ID is invalid."""


class GiftMonthsInvalid(BadRequest):
    """The value passed in invoice.inputInvoicePremiumGiftStars.months is invalid."""


class GiftSlugExpired(BadRequest):
    """The specified gift slug has expired."""


class GiftSlugInvalid(BadRequest):
    """The specified slug is invalid."""


class GiftStarsInvalid(BadRequest):
    """The specified amount of stars is invalid."""


class GraphExpiredReload(BadRequest):
    """This graph has expired, please obtain a new graph token."""


class GraphInvalidReload(BadRequest):
    """Invalid graph token provided, please reload the stats and provide the updated
    token.
    """


class GraphOutdatedReload(BadRequest):
    """The graph is outdated, please get a new async token using
    stats.getBroadcastStats.
    """


class GroupcallAlreadyDiscarded(BadRequest):
    """The group call was already discarded."""


class GroupcallAlreadyStarted(Forbidden):
    """The groupcall has already started, you can join directly using
    phone.joinGroupCall.
    """


class GroupcallChangeForbidden(Forbidden):
    """You cannot change this group call setting."""


class GroupcallForbidden(Forbidden):
    """The specified group call cannot be used in this context."""


class GroupcallInvalid(BadRequest):
    """The specified group call is invalid."""


class GroupcallJoinMissing(BadRequest):
    """You haven't joined this group call."""


class GroupcallNotModified(BadRequest):
    """Group call settings weren't modified."""


class GroupcallSsrcDuplicateMuch(BadRequest):
    """The app needs to retry joining the group call with a new SSRC value."""


class GroupedMediaInvalid(BadRequest):
    """Invalid grouped media."""


class HashInvalid(BadRequest):
    """The provided hash is invalid."""


class HashSizeInvalid(BadRequest):
    """The size of the specified secureValueError.hash is invalid."""


class HashtagInvalid(BadRequest):
    """The specified hashtag is invalid."""


class HideRequesterMissing(BadRequest):
    """The join request was missing or was already handled."""


class IdExpired(BadRequest):
    """The passed prepared inline message ID has expired."""


class IdInvalid(BadRequest):
    """The passed ID is invalid."""


class ImageProcessFailed(BadRequest):
    """Failure while processing image."""


class ImportFileInvalid(BadRequest):
    """The specified chat export file is invalid."""


class ImportFormatDateInvalid(BadRequest):
    """The date specified in the import file is invalid."""


class ImportFormatUnrecognized(BadRequest):
    """The specified chat export file was exported from an unsupported chat app."""


class ImportIdInvalid(BadRequest):
    """The specified import ID is invalid."""


class ImportTokenInvalid(BadRequest):
    """The specified token is invalid."""


class InlineBotRequired(Forbidden):
    """Only the inline bot can edit message."""


class InlineResultExpired(BadRequest):
    """The inline query expired."""


class InputChatlistInvalid(BadRequest):
    """The specified folder is invalid."""


class InputConstructorInvalid(BadRequest):
    """The specified TL constructor is invalid."""


class InputFetchError(BadRequest):
    """An error occurred while parsing the provided TL constructor."""


class InputFetchFail(BadRequest):
    """An error occurred while parsing the provided TL constructor."""


class InputFileInvalid(BadRequest):
    """The specified InputFile is invalid."""


class InputFilterInvalid(BadRequest):
    """The specified filter is invalid."""


class InputLayerInvalid(BadRequest):
    """The specified layer is invalid."""


class InputMethodInvalid(BadRequest):
    """The specified method is invalid."""


class InputPeersEmpty(BadRequest):
    """The specified peer array is empty."""


class InputPurposeInvalid(BadRequest):
    """The specified payment purpose is invalid."""


class InputRequestTooLong(BadRequest):
    """The request payload is too long."""


class InputStarsAmountInvalid(BadRequest):
    """The specified offer amount in stars is invalid, see here » for the allowed range.
    """


class InputStarsNanosInvalid(BadRequest):
    """The specified offer amount in nanotons is invalid, see here » for the allowed
    range.
    """


class InputTextEmpty(BadRequest):
    """The specified text is empty."""


class InputTextTooLong(BadRequest):
    """The specified text is too long."""


class InputUserDeactivated(BadRequest):
    """The specified user was deleted."""


class InviteForbiddenWithJoinas(BadRequest):
    """If the user has anonymously joined a group call as a channel, they can't invite
    other users to the group call because that would cause deanonymization, because the
    invite would be sent using the original user ID, not the anonymized channel ID.
    """


class InviteHashEmpty(BadRequest):
    """The invite hash is empty."""


class InviteHashExpired(BadRequest):
    """The invite link has expired."""


class InviteHashInvalid(BadRequest):
    """The invite hash is invalid."""


class InviteRequestSent(BadRequest):
    """You have successfully requested to join this chat or channel."""


class InviteRevokedMissing(BadRequest):
    """The specified invite link was already revoked or is invalid."""


class InviteSlugEmpty(BadRequest):
    """The specified invite slug is empty."""


class InviteSlugExpired(BadRequest):
    """The specified chat folder link has expired."""


class InviteSlugInvalid(BadRequest):
    """The specified invitation slug is invalid."""


class InvitesTooMuch(BadRequest):
    """The maximum number of per-folder invites specified by the
    `chatlist_invites_limit_default`/`chatlist_invites_limit_premium` client
    configuration parameters » was reached.
    """


class InvoiceInvalid(BadRequest):
    """The specified invoice is invalid."""


class InvoicePayloadInvalid(BadRequest):
    """The specified invoice payload is invalid."""


class JoinAsPeerInvalid(BadRequest):
    """The specified peer cannot be used to join a group call."""


class LangCodeInvalid(BadRequest):
    """The specified language code is invalid."""


class LangCodeNotSupported(BadRequest):
    """The specified language code is not supported."""


class LangPackInvalid(BadRequest):
    """The provided language pack is invalid."""


class LanguageInvalid(BadRequest):
    """The specified lang_code is invalid."""


class LastnameInvalid(BadRequest):
    """The last name is invalid."""


class LimitInvalid(BadRequest):
    """The provided limit is invalid."""


class LimitPerPostInvalid(BadRequest):
    """The specified reactions_limit value is invalid."""


class LinkNotModified(BadRequest):
    """Discussion link not modified."""


class LocationInvalid(BadRequest):
    """The provided location is invalid."""


class ManagerInvalid(BadRequest):
    """The specified manager bot is invalid."""


class ManagerPermissionMissing(BadRequest):
    """The specified manager bot does not have the user.`bot_can_manage_bots` flag set.
    """


class MaxDateInvalid(BadRequest):
    """The specified maximum date is invalid."""


class MaxIdInvalid(BadRequest):
    """The provided max ID is invalid."""


class MaxQtsInvalid(BadRequest):
    """The specified max_qts is invalid."""


class Md5ChecksumInvalid(BadRequest):
    """The MD5 checksums do not match."""


class MediaAlreadyPaid(BadRequest):
    """You already paid for the specified media."""


class MediaCaptionTooLong(BadRequest):
    """The caption is too long."""


class MediaEmpty(BadRequest):
    """The provided media object is invalid."""


class MediaFileInvalid(BadRequest):
    """The specified media file is invalid."""


class MediaGroupedInvalid(BadRequest):
    """You tried to send media of different types in an album."""


class MediaInvalid(BadRequest):
    """Media invalid."""


class MediaNewInvalid(BadRequest):
    """The new media is invalid."""


class MediaPrevInvalid(BadRequest):
    """Previous media invalid."""


class MediaTtlInvalid(BadRequest):
    """The specified media TTL is invalid."""


class MediaTypeInvalid(BadRequest):
    """The specified media type cannot be used in stories."""


class MediaVideoStoryMissing(BadRequest):
    """A non-story video cannot be repubblished as a story (emitted when trying to
    resend a non-story video as a story using inputDocument).
    """


class MegagroupGeoRequired(BadRequest):
    """This method can only be invoked on a geogroup."""


class MegagroupIdInvalid(BadRequest):
    """Invalid supergroup ID."""


class MegagroupPrehistoryHidden(BadRequest):
    """Group with hidden history for new members can't be set as discussion groups."""


class MegagroupRequired(BadRequest):
    """You can only use this method on a supergroup."""


class MessageAuthorRequired(Forbidden):
    """Message author required."""


class MessageDeleteForbidden(Forbidden):
    """You can't delete one of the messages you tried to delete, most likely because it
    is a service message.
    """


class MessageEditTimeExpired(BadRequest):
    """You can't edit this message anymore, too much time has passed since its creation.
    """


class MessageEmpty(BadRequest):
    """The provided message is empty."""


class MessageIdInvalid(BadRequest):
    """The provided message id is invalid."""


class MessageIdsEmpty(BadRequest):
    """No message ids were provided."""


class MessageNotModified(BadRequest):
    """The provided message data is identical to the previous message data, the message
    wasn't modified.
    """


class MessageNotReadYet(BadRequest):
    """The specified message wasn't read yet."""


class MessagePollClosed(BadRequest):
    """Poll closed."""


class MessageRequired(BadRequest):
    """A non-empty list of IDs must be passed to `id`."""


class MessageTooLong(BadRequest):
    """The provided message is too long."""


class MessageTooOld(BadRequest):
    """The message is too old, the requested information is not available."""


class MethodInvalid(BadRequest):
    """The specified method is invalid."""


class MinDateInvalid(BadRequest):
    """The specified minimum date is invalid."""


class MonthInvalid(BadRequest):
    """The number of months specified in inputInvoicePremiumGiftStars.months is invalid.
    """


class MsgIdInvalid(BadRequest):
    """Invalid message ID provided."""


class MsgTooOld(BadRequest):
    """`chat_read_mark_expire_period` seconds have passed since the message was sent,
    read receipts were deleted.
    """


class MsgVoiceMissing(BadRequest):
    """The specified message is not a voice message."""


class MsgVoiceTooLong(BadRequest):
    """The specified voice message is too long to be transcribed."""


class MsgWaitFailed(InternalError):
    """A waiting call returned an error."""


class MsgWaitTimeout(Timeout):
    """Spent too much time waiting for a previous query in the invokeAfterMsg request
    queue, aborting!
    """


class MultiMediaTooLong(BadRequest):
    """Too many media files for album."""


class NameInvalid(BadRequest):
    """The specified bot name is invalid."""


class NeedActionMissing(BadRequest):
    """The caller didn't specify a valid action (either save or suggest) for the contact
    profile photo upload.
    """


class NewSaltInvalid(BadRequest):
    """The new salt is invalid."""


class NewSettingsEmpty(BadRequest):
    """No password is set on the current account, and no new password was specified in
    `new_settings`.
    """


class NewSettingsInvalid(BadRequest):
    """The new password settings are invalid."""


class NextOffsetInvalid(BadRequest):
    """The specified offset is longer than 64 bytes."""


class NoPaymentNeeded(BadRequest):
    """The upgrade/transfer of the specified gift was already paid for or is free."""


class NogeneralHideForbidden(BadRequest):
    """Only the "General" topic with `id=1` can be hidden."""


class NotEligible(Forbidden):
    """The current user is not eligible to join the Peer-to-Peer Login Program."""


class NotJoined(BadRequest):
    """The current user hasn't joined the Peer-to-Peer Login Program."""


class OauthRequestInvalid(InternalError):
    """The specified OAuth request is invalid."""


class OffsetInvalid(BadRequest):
    """The provided offset is invalid."""


class OffsetPeerIdInvalid(BadRequest):
    """The provided offset peer is invalid."""


class OptionInvalid(BadRequest):
    """Invalid option selected."""


class OptionsTooMuch(BadRequest):
    """Too many options provided."""


class OrderInvalid(BadRequest):
    """The specified username order is invalid."""


class PackShortNameInvalid(BadRequest):
    """Short pack name invalid."""


class PackShortNameOccupied(BadRequest):
    """A stickerpack with this name already exists."""


class PackTitleInvalid(BadRequest):
    """The stickerpack title is invalid."""


class PackTypeInvalid(BadRequest):
    """The masks and emojis flags are mutually exclusive."""


class ParentPeerInvalid(BadRequest):
    """The specified `parent_peer` is invalid."""


class ParticipantIdInvalid(BadRequest):
    """The specified participant ID is invalid."""


class ParticipantJoinMissing(BadRequest):
    """Trying to enable a presentation, when the user hasn't joined the Video Chat with
    phone.joinGroupCall.
    """


class ParticipantVersionOutdated(BadRequest):
    """The other participant does not use an up to date telegram client with support for
    calls.
    """


class ParticipantsTooFew(BadRequest):
    """Not enough participants."""


class PasskeyOriginMismatch(BadRequest):
    """Third-party clients currently don't support passkeys even when changing the
    origin.
    """


class PasswordEmpty(BadRequest):
    """The provided password is empty."""


class PasswordMissing(BadRequest):
    """You must enable 2FA before executing this operation."""


class PasswordRecoveryExpired(BadRequest):
    """The recovery code has expired."""


class PasswordRecoveryNa(BadRequest):
    """No email was set, can't recover password via email."""


class PasswordRequired(BadRequest):
    """A 2FA password must be configured to use Telegram Passport."""


class PasswordTooFresh(BadRequest):
    """The password was modified less than 24 hours ago, try again in %d seconds."""


class PaymentCredentialsInvalid(BadRequest):
    """The specified payment credentials are invalid."""


class PaymentProviderInvalid(BadRequest):
    """The specified payment provider is invalid."""


class PaymentRequired(BadRequest):
    """Payment is required for this action, see here » for more info."""


class PaymentUnsupported(NotAcceptable):
    """A detailed description of the error will be received separately as described here
    ».
    """


class PeerFlood(BadRequest):
    """The current account is spamreported, you cannot execute this action, check
    @spambot for more info.
    """


class PeerHistoryEmpty(BadRequest):
    """You can't pin an empty chat with a user."""


class PeerIdInvalid(BadRequest):
    """The provided peer id is invalid."""


class PeerIdNotSupported(BadRequest):
    """The provided peer ID is not supported."""


class PeerTypesInvalid(BadRequest):
    """The passed keyboardButtonSwitchInline.`peer_types` field is invalid."""


class PeersListEmpty(BadRequest):
    """The specified list of peers is empty."""


class PersistentTimestampEmpty(BadRequest):
    """Persistent timestamp empty."""


class PersistentTimestampInvalid(BadRequest):
    """Persistent timestamp invalid."""


class PersistentTimestampOutdated(InternalError):
    """Channel internal replication issues, try again later (treat this like an
    RPC_CALL_FAIL).
    """


class PhoneCodeEmpty(BadRequest):
    """phone_code is missing."""


class PhoneCodeHashEmpty(BadRequest):
    """phone_code_hash is missing."""


class PhoneHashExpired(BadRequest):
    """An invalid or expired `phone_code_hash` was provided."""


class PhoneNotOccupied(BadRequest):
    """No user is associated to the specified phone number."""


class PhoneNumberAppSignupForbidden(BadRequest):
    """You can't sign up using this app."""


class PhoneNumberBanned(BadRequest):
    """The provided phone number is banned from telegram."""


class PhoneNumberFlood(BadRequest):
    """You asked for the code too many times."""


class PhoneNumberOccupied(BadRequest):
    """The phone number is already in use."""


class PhoneNumberUnoccupied(BadRequest):
    """The phone number is not yet being used."""


class PhonePasswordFlood(NotAcceptable):
    """You have tried logging in too many times."""


class PhonePasswordProtected(BadRequest):
    """This phone is password protected."""


class PhotoContentTypeInvalid(BadRequest):
    """Photo mime-type invalid."""


class PhotoContentUrlEmpty(BadRequest):
    """Photo URL invalid."""


class PhotoCropFileMissing(BadRequest):
    """Photo crop file missing."""


class PhotoCropSizeSmall(BadRequest):
    """Photo is too small."""


class PhotoExtInvalid(BadRequest):
    """The extension of the photo is invalid."""


class PhotoFileMissing(BadRequest):
    """Profile photo file missing."""


class PhotoIdInvalid(BadRequest):
    """Photo ID invalid."""


class PhotoInvalid(BadRequest):
    """Photo invalid."""


class PhotoInvalidDimensions(BadRequest):
    """The photo dimensions are invalid."""


class PhotoSaveFileInvalid(BadRequest):
    """Internal issues, try again later."""


class PhotoThumbUrlEmpty(BadRequest):
    """Photo thumbnail URL is empty."""


class PinRestricted(BadRequest):
    """You can't pin messages."""


class PinnedDialogsTooMuch(BadRequest):
    """Too many pinned dialogs."""


class PinnedTooMuch(BadRequest):
    """There are too many pinned topics, unpin some first."""


class PinnedTopicNotModified(BadRequest):
    """The specified topic is already pinned."""


class PollAnswerInvalid(BadRequest):
    """One of the poll answers is not acceptable."""


class PollAnswersInvalid(BadRequest):
    """Invalid poll answers were provided."""


class PollCountryRestricted(NotAcceptable):
    """Users from the current user's country cannot vote in this country-restricted poll
    ».
    """


class PollMemberRestricted(NotAcceptable):
    """Only channel subscribers can vote in this poll."""


class PollOptionDuplicate(BadRequest):
    """Duplicate poll options provided."""


class PollOptionInvalid(BadRequest):
    """Invalid poll option provided."""


class PollQuestionInvalid(BadRequest):
    """One of the poll questions is not acceptable."""


class PollVoteRequired(Forbidden):
    """Cast a vote in the poll before calling this method."""


class PrecheckoutFailed(NotAcceptable):
    """Precheckout failed, a detailed and localized description for the error will be
    emitted via an updateServiceNotification as specified here ».
    """


class PremiumAccountRequired(Forbidden):
    """A premium account is required to execute this action."""


class PremiumCurrentlyUnavailable(NotAcceptable):
    """You cannot currently purchase a Premium subscription."""


class PremiumPurposeInvalid(BadRequest):
    """The specified InputStorePaymentPurpose is invalid."""


class PremiumSubActiveUntil(Flood):
    """You already have a premium subscription active until unixtime %d."""


class PreviousChatImportActiveWaitMin(NotAcceptable):
    """Import for this chat is already in progress, wait %d minutes before starting a
    new one.
    """


class PricingChatInvalid(BadRequest):
    """The pricing for the subscription is invalid, the maximum price is specified in
    the `stars_subscription_amount_max` config key ».
    """


class PrivacyKeyInvalid(BadRequest):
    """The privacy key is invalid."""


class PrivacyPremiumRequired(Forbidden):
    """You need a Telegram Premium subscription to send a message to this user."""


class PrivacyTooLong(BadRequest):
    """Too many privacy rules were specified, the current limit is 1000."""


class PrivacyValueInvalid(BadRequest):
    """The specified privacy rule combination is invalid."""


class PublicBroadcastExpected(BadRequest):
    """`channel` only accepts a channel, but a supergroup was passed."""


class PublicChannelMissing(Forbidden):
    """You can only export group call invite links for public chats or channels."""


class PublicKeyInvalid(BadRequest):
    """The specified e2e public key is invalid."""


class PublicKeyRequired(BadRequest):
    """A public key is required."""


class PurposeInvalid(BadRequest):
    """The specified payment purpose is invalid."""


class QueryIdEmpty(BadRequest):
    """The query ID is empty."""


class QueryIdInvalid(BadRequest):
    """The query ID is invalid."""


class QueryTooShort(BadRequest):
    """The query string is too short."""


class QuickRepliesBotNotAllowed(BadRequest):
    """Quick replies cannot be used by bots."""


class QuickRepliesTooMuch(BadRequest):
    """A maximum of appConfig.`quick_replies_limit` shortcuts may be created, the limit
    was reached.
    """


class QuizAnswerMissing(BadRequest):
    """You can forward a quiz while hiding the original author only after choosing an
    option in the quiz.
    """


class QuizCorrectAnswerInvalid(BadRequest):
    """An invalid value was provided to the correct_answers field."""


class QuizCorrectAnswersEmpty(BadRequest):
    """No correct quiz answer was specified."""


class QuizCorrectAnswersTooMuch(BadRequest):
    """You specified too many correct answers in a quiz, quizzes can only have one right
    answer!
    """


class QuizMultipleInvalid(BadRequest):
    """Quizzes can't have the multiple_choice flag set!"""


class QuoteTextInvalid(BadRequest):
    """The specified `reply_to`.`quote_text` field is invalid."""


class RaiseHandForbidden(BadRequest):
    """You cannot raise your hand."""


class RandomIdDuplicate(InternalError):
    """You provided a random ID that was already used."""


class RandomIdEmpty(BadRequest):
    """Random ID empty."""


class RandomIdExpired(BadRequest):
    """The specified `random_id` was expired (most likely it didn't follow the required
    `uint64_t random_id = (time() << 32) | ((uint64_t)random_uint32_t())` format, or the
    specified time is too far in the past).
    """


class RandomIdInvalid(BadRequest):
    """A provided random ID is invalid."""


class RandomLengthInvalid(BadRequest):
    """Random length invalid."""


class RangesInvalid(BadRequest):
    """Invalid range provided."""


class ReactionEmpty(BadRequest):
    """Empty reaction provided."""


class ReactionInvalid(BadRequest):
    """The specified reaction is invalid."""


class ReactionsCountInvalid(BadRequest):
    """The specified number of reactions is invalid."""


class ReactionsTooMany(BadRequest):
    """The message already has exactly `reactions_uniq_max` reaction emojis, you can't
    react with a new emoji, see the docs for more info ».
    """


class ReceiptEmpty(BadRequest):
    """The specified receipt is empty."""


class ReplyMarkupBuyEmpty(BadRequest):
    """Reply markup for buy button empty."""


class ReplyMarkupGameEmpty(BadRequest):
    """A game message is being edited, but the newly provided keyboard doesn't have a
    keyboardButtonGame button.
    """


class ReplyMarkupInvalid(BadRequest):
    """The provided reply markup is invalid."""


class ReplyMarkupTooLong(BadRequest):
    """The specified reply_markup is too long."""


class ReplyMessageIdInvalid(BadRequest):
    """The specified reply-to message ID is invalid."""


class ReplyMessagesTooMuch(BadRequest):
    """Each shortcut can contain a maximum of appConfig.`quick_reply_messages_limit`
    messages, the limit was reached.
    """


class ReplyToInvalid(BadRequest):
    """The specified `reply_to` field is invalid."""


class ReplyToMonoforumPeerInvalid(BadRequest):
    """The specified inputReplyToMonoForum.monoforum_peer_id is invalid."""


class ReplyToUserInvalid(BadRequest):
    """The replied-to user is invalid."""


class RequestMsgExpired(BadRequest):
    """The request specified in request_msg_id has already expired."""


class RequestTokenInvalid(BadRequest):
    """The master DC did not accept the `request_token` from the CDN DC. Continue
    downloading the file from the master DC using upload.getFile.
    """


class ResellStarsTooFew(BadRequest):
    """The offered price is too low."""


class ResellStarsTooMuch(BadRequest):
    """The offered price is too high."""


class ResetRequestMissing(BadRequest):
    """No password reset is in progress."""


class ResultIdDuplicate(BadRequest):
    """You provided a duplicate result ID."""


class ResultIdEmpty(BadRequest):
    """Result ID empty."""


class ResultIdInvalid(BadRequest):
    """One of the specified result IDs is invalid."""


class ResultTypeInvalid(BadRequest):
    """Result type invalid."""


class ResultsTooMuch(BadRequest):
    """Too many results were provided."""


class RevoteNotAllowed(BadRequest):
    """You cannot change your vote."""


class RightForbidden(Forbidden):
    """Your admin rights do not allow you to do this."""


class RightsNotModified(BadRequest):
    """The new admin rights are equal to the old rights, no change was made."""


class RingtoneInvalid(BadRequest):
    """The specified ringtone is invalid."""


class RingtoneMimeInvalid(BadRequest):
    """The MIME type for the ringtone is invalid."""


class RsaDecryptFailed(BadRequest):
    """Internal RSA decryption failed."""


class SavedIdEmpty(BadRequest):
    """The passed inputSavedStarGiftChat.saved_id is empty."""


class ScheduleBotNotAllowed(BadRequest):
    """Bots cannot schedule messages."""


class ScheduleDateInvalid(BadRequest):
    """Invalid schedule date provided."""


class ScheduleDateTooLate(BadRequest):
    """You can't schedule a message this far in the future."""


class ScheduleStatusPrivate(BadRequest):
    """Can't schedule until user is online, if the user's last seen timestamp is hidden
    by their privacy settings.
    """


class ScheduleTooMuch(BadRequest):
    """There are too many scheduled messages."""


class ScoreInvalid(BadRequest):
    """The specified game score is invalid."""


class SearchQueryEmpty(BadRequest):
    """The search query is empty."""


class SearchWithLinkNotSupported(BadRequest):
    """You cannot provide a search query and an invite link at the same time."""


class SecondsInvalid(BadRequest):
    """Invalid duration provided."""


class SecureSecretRequired(BadRequest):
    """A secure secret is required."""


class SelfDeleteRestricted(BadRequest):
    """Business bots can't delete messages just for the user, `revoke` **must** be set.
    """


class SendAsPeerInvalid(BadRequest):
    """You can't send messages as the specified peer."""


class SendCodeUnavailable(NotAcceptable):
    """Returned when all available options for this type of number were already used
    (e.g. flash-call, then SMS, then this error might be returned to trigger a second
    resend).
    """


class SendMediaInvalid(InternalError):
    """The specified media is invalid."""


class SendMessageGameInvalid(BadRequest):
    """An inputBotInlineMessageGame can only be contained in an
    inputBotInlineResultGame, not in an
    inputBotInlineResult/inputBotInlineResultPhoto/etc.
    """


class SendMessageMediaInvalid(BadRequest):
    """Invalid media provided."""


class SendMessageTypeInvalid(BadRequest):
    """The message type is invalid."""


class SensitiveChangeForbidden(Forbidden):
    """You can't change your sensitive content settings."""


class SessionExpired(Unauthorized):
    """The session has expired."""


class SessionRevoked(Unauthorized):
    """The session was revoked by the user."""


class SessionTooFresh(BadRequest):
    """This session was created less than 24 hours ago, try again in %d seconds."""


class SettingsInvalid(BadRequest):
    """Invalid settings were provided."""


class Sha256HashInvalid(BadRequest):
    """The provided SHA256 hash is invalid."""


class ShortNameInvalid(BadRequest):
    """The specified short name is invalid."""


class ShortNameOccupied(BadRequest):
    """The specified short name is already in use."""


class ShortcutInvalid(BadRequest):
    """The specified shortcut is invalid."""


class SignInFailed(InternalError):
    """Failure while signing in."""


class SlotsEmpty(BadRequest):
    """The specified slot list is empty."""


class SlowmodeMultiMsgsDisabled(BadRequest):
    """Slowmode is enabled, you cannot forward multiple messages to this group."""


class SlugInvalid(BadRequest):
    """The specified invoice slug is invalid."""


class SmsCodeCreateFailed(BadRequest):
    """An error occurred while creating the SMS code."""


class SmsjobIdInvalid(BadRequest):
    """The specified job ID is invalid."""


class SrpAInvalid(BadRequest):
    """The specified inputCheckPasswordSRP.A value is invalid."""


class SrpIdInvalid(BadRequest):
    """Invalid SRP ID provided."""


class SrpPasswordChanged(BadRequest):
    """Password has changed."""


class StargiftAlreadyConverted(BadRequest):
    """The specified star gift was already converted to Stars."""


class StargiftAlreadyRefunded(BadRequest):
    """The specified star gift was already refunded."""


class StargiftAlreadyUpgraded(BadRequest):
    """The specified gift was already upgraded to a collectible gift."""


class StargiftAttributeInvalid(BadRequest):
    """One of the specified star gift attributes is invalid."""


class StargiftExportInProgress(NotAcceptable):
    """A gift export is in progress, a detailed and localized description for the error
    will be emitted via an updateServiceNotification as specified here ».
    """


class StargiftInvalid(BadRequest):
    """The passed gift is invalid."""


class StargiftMessageInvalid(BadRequest):
    """The specified inputInvoiceStarGift.message is invalid."""


class StargiftNotFound(BadRequest):
    """The specified gift was not found."""


class StargiftNotOwner(BadRequest):
    """You're not the owner of the gift you trying to transfer."""


class StargiftNotUnique(BadRequest):
    """You can't transfer a non-collectible gift."""


class StargiftObjectInvalid(BadRequest):
    """The specified star gift object is invalid."""


class StargiftOfferInvalid(BadRequest):
    """The specified offer amount is invalid."""


class StargiftOfferNotAllowed(BadRequest):
    """You can't send a purchase offer for this gift."""


class StargiftOwnerInvalid(BadRequest):
    """You cannot transfer or sell a gift owned by another user."""


class StargiftPeerInvalid(BadRequest):
    """The specified inputSavedStarGiftChat.peer is invalid."""


class StargiftResellCurrencyNotAllowed(BadRequest):
    """You can't buy the gift using the specified currency (i.e. trying to pay in Stars
    for TON gifts).
    """


class StargiftResellTooEarly(BadRequest):
    """You will be able to resell this gift in %d seconds."""


class StargiftSlugInvalid(BadRequest):
    """The specified gift slug is invalid."""


class StargiftTransferTooEarly(BadRequest):
    """You cannot transfer this gift yet, wait %d seconds."""


class StargiftUpgradeUnavailable(BadRequest):
    """A received gift can only be upgraded to a collectible gift if the
    messageActionStarGift/savedStarGift.`can_upgrade` flag is set.
    """


class StargiftUsageLimited(BadRequest):
    """The gift is sold out."""


class StargiftUserUsageLimited(BadRequest):
    """You've reached the starGift.limited_per_user limit, you can't buy any more gifts
    of this type.
    """


class StarrefAwaitingEnd(BadRequest):
    """The previous referral program was terminated less than 24 hours ago: further
    changes can be made after the date specified in userFull.starref_program.end_date.
    """


class StarrefExpired(BadRequest):
    """The specified referral link is invalid."""


class StarrefHashRevoked(BadRequest):
    """The specified affiliate link was already revoked."""


class StarrefPermilleInvalid(BadRequest):
    """The specified commission_permille is invalid: the minimum and maximum values for
    this parameter are contained in the starref_min_commission_permille and
    starref_max_commission_permille client configuration parameters.
    """


class StarrefPermilleTooLow(BadRequest):
    """The specified commission_permille is too low: the minimum and maximum values for
    this parameter are contained in the starref_min_commission_permille and
    starref_max_commission_permille client configuration parameters.
    """


class StarsAmountInvalid(BadRequest):
    """The specified amount in stars is invalid."""


class StarsFormAmountMismatch(NotAcceptable):
    """The form amount has changed, please fetch the new form using
    payments.getPaymentForm and restart the process.
    """


class StarsInvoiceInvalid(BadRequest):
    """The specified Telegram Star invoice is invalid."""


class StarsPaymentRequired(BadRequest):
    """To import this chat invite link, you must first pay for the associated Telegram
    Star subscription ».
    """


class StartParamEmpty(BadRequest):
    """The start parameter is empty."""


class StartParamInvalid(BadRequest):
    """Start parameter invalid."""


class StartParamTooLong(BadRequest):
    """Start parameter is too long."""


class StickerDocumentInvalid(BadRequest):
    """The specified sticker document is invalid."""


class StickerEmojiInvalid(BadRequest):
    """Sticker emoji invalid."""


class StickerFileInvalid(BadRequest):
    """Sticker file invalid."""


class StickerGifDimensions(BadRequest):
    """The specified video sticker has invalid dimensions."""


class StickerIdInvalid(BadRequest):
    """The provided sticker ID is invalid."""


class StickerInvalid(BadRequest):
    """The provided sticker is invalid."""


class StickerMimeInvalid(BadRequest):
    """The specified sticker MIME type is invalid."""


class StickerPngDimensions(BadRequest):
    """Sticker png dimensions invalid."""


class StickerPngNopng(BadRequest):
    """One of the specified stickers is not a valid PNG file."""


class StickerTgsNodoc(BadRequest):
    """You must send the animated sticker as a document."""


class StickerTgsNotgs(BadRequest):
    """Invalid TGS sticker provided."""


class StickerThumbPngNopng(BadRequest):
    """Incorrect stickerset thumb file provided, PNG / WEBP expected."""


class StickerThumbTgsNotgs(BadRequest):
    """Incorrect stickerset TGS thumb file provided."""


class StickerVideoBig(BadRequest):
    """The specified video sticker is too big."""


class StickerVideoNodoc(BadRequest):
    """You must send the video sticker as a document."""


class StickerVideoNowebm(BadRequest):
    """The specified video sticker is not in webm format."""


class StickerpackStickersTooMuch(BadRequest):
    """There are too many stickers in this stickerpack, you can't add any more."""


class StickersEmpty(BadRequest):
    """No sticker provided."""


class StickersTooMuch(BadRequest):
    """There are too many stickers in this stickerpack, you can't add any more."""


class StickersetInvalid(BadRequest):
    """The provided sticker set is invalid."""


class StickersetNotModified(BadRequest):
    """The passed stickerset information is equal to the current information."""


class StickersetOwnerAnonymous(NotAcceptable):
    """Provided stickerset can't be installed as group stickerset to prevent admin
    deanonymization.
    """


class StoriesNeverCreated(BadRequest):
    """This peer hasn't ever posted any stories."""


class StoriesTooMuch(BadRequest):
    """You have hit the maximum active stories limit as specified by the
    `story_expiring_limit_*` client configuration parameters: you should buy a Premium
    subscription, delete an active story, or wait for the oldest story to expire.
    """


class StoryIdEmpty(BadRequest):
    """You specified no story IDs."""


class StoryIdInvalid(BadRequest):
    """The specified story ID is invalid."""


class StoryLiveAlready(BadRequest):
    """This peer already has an active live story, and its ID is equal to %d."""


class StoryNotModified(BadRequest):
    """The new story information you passed is equal to the previous story information,
    thus it wasn't modified.
    """


class StoryPeriodInvalid(BadRequest):
    """The specified story period is invalid for this account."""


class StorySendFloodMonthly(BadRequest):
    """You've hit the monthly story limit as specified by the
    `stories_sent_monthly_limit_*` client configuration parameters: wait %d seconds
    before posting a new story.
    """


class StorySendFloodWeekly(BadRequest):
    """You've hit the weekly story limit as specified by the
    `stories_sent_weekly_limit_*` client configuration parameters: wait for %d seconds
    before posting a new story.
    """


class SubscriptionExportMissing(BadRequest):
    """You cannot send a bot subscription invoice directly, you may only create invoice
    links using payments.exportInvoice.
    """


class SubscriptionIdInvalid(BadRequest):
    """The specified subscription_id is invalid."""


class SubscriptionPeriodInvalid(BadRequest):
    """The specified subscription_pricing.period is invalid."""


class SuggestedPostAmountInvalid(BadRequest):
    """The specified price for the suggested post is invalid."""


class SuggestedPostPeerInvalid(BadRequest):
    """You cannot send suggested posts to non-monoforum peers."""


class SwitchPmTextEmpty(BadRequest):
    """The switch_pm.text field was empty."""


class SwitchWebviewUrlInvalid(BadRequest):
    """The URL specified in switch_webview.url is invalid!"""


class TakeoutInvalid(BadRequest):
    """The specified takeout ID is invalid."""


class TakeoutRequired(Forbidden):
    """A takeout session needs to be initialized first, see here » for more info."""


class TaskAlreadyExists(BadRequest):
    """An email reset was already requested."""


class TempAuthKeyAlreadyBound(BadRequest):
    """The passed temporary key is already bound to another **perm_auth_key_id**."""


class TempAuthKeyEmpty(BadRequest):
    """No temporary auth key provided."""


class TermsUrlInvalid(BadRequest):
    """The specified invoice.`terms_url` is invalid."""


class TextdraftPeerInvalid(BadRequest):
    """sendMessageTextDraftAction can only be used in private 1-on-1 chats."""


class ThemeFileInvalid(BadRequest):
    """Invalid theme file provided."""


class ThemeFormatInvalid(BadRequest):
    """Invalid theme format provided."""


class ThemeInvalid(BadRequest):
    """Invalid theme provided."""


class ThemeMimeInvalid(BadRequest):
    """The theme's MIME type is invalid."""


class ThemeParamsInvalid(BadRequest):
    """The specified `theme_params` field is invalid."""


class ThemeSlugInvalid(BadRequest):
    """The specified theme slug is invalid."""


class ThemeTitleInvalid(BadRequest):
    """The specified theme title is invalid."""


class TimezoneInvalid(BadRequest):
    """The specified timezone does not exist."""


class TitleInvalid(BadRequest):
    """The specified stickerpack title is invalid."""


class TmpPasswordDisabled(BadRequest):
    """The temporary password is disabled."""


class TmpPasswordInvalid(BadRequest):
    """The passed tmp_password is invalid."""


class ToIdInvalid(BadRequest):
    """The specified `to_id` of the passed inputInvoiceStarGiftResale or
    inputInvoiceStarGiftTransfer is invalid.
    """


class ToLangInvalid(BadRequest):
    """The specified destination language is invalid."""


class TodoItemDuplicate(BadRequest):
    """Duplicate checklist items detected."""


class TodoItemsEmpty(BadRequest):
    """A checklist was specified, but no checklist items were passed."""


class TodoItemsTooMuch(BadRequest):
    """You specified too many todo list items."""


class TodoNotModified(BadRequest):
    """No todo items were specified, so no changes were made to the todo list."""


class TokenEmpty(BadRequest):
    """The specified token is empty."""


class TokenInvalid(BadRequest):
    """The provided token is invalid."""


class TokenTypeInvalid(BadRequest):
    """The specified token type is invalid."""


class TopicCloseSeparately(BadRequest):
    """The `close` flag cannot be provided together with any of the other flags."""


class TopicClosed(BadRequest):
    """This topic was closed, you can't send messages to it anymore."""


class TopicDeleted(BadRequest):
    """The specified topic was deleted."""


class TopicHideSeparately(BadRequest):
    """The `hide` flag cannot be provided together with any of the other flags."""


class TopicIdInvalid(BadRequest):
    """The specified topic ID is invalid."""


class TopicNotModified(BadRequest):
    """The updated topic info is equal to the current topic info, nothing was changed.
    """


class TopicTitleEmpty(BadRequest):
    """The specified topic title is empty."""


class TopicsEmpty(BadRequest):
    """You specified no topic IDs."""


class TransactionIdInvalid(BadRequest):
    """The specified transaction ID is invalid."""


class TranscriptionFailed(BadRequest):
    """Audio transcription failed."""


class TranslateReqFailed(InternalError):
    """Translation failed, please try again later."""


class TranslateReqQuotaExceeded(BadRequest):
    """Translation is currently unavailable due to a temporary server-side lack of
    resources.
    """


class TranslationTimeout(InternalError):
    """A timeout occurred while translating the specified text."""


class TranslationsDisabled(NotAcceptable):
    """Translations are unavailable, a detailed and localized description for the error
    will be emitted via an updateServiceNotification as specified here ».
    """


class TtlDaysInvalid(BadRequest):
    """The provided TTL is invalid."""


class TtlMediaInvalid(BadRequest):
    """Invalid media Time To Live was provided."""


class TtlPeriodInvalid(BadRequest):
    """The specified TTL period is invalid."""


class TwoFactorConfirmWait(Flood):
    """Since this account is active and protected by a 2FA password, we will delete it
    in 1 week for security purposes. You can cancel this process at any time, you'll be
    able to reset your account in %d seconds.
    """


class TypesEmpty(BadRequest):
    """No top peer type was provided."""


class Unsupported(BadRequest):
    """`require_payment` cannot be *set* by users, only by monoforums: users must
    instead use the inputPrivacyKeyNoPaidMessages privacy setting to remove a previously
    added exemption.
    """


class UntilDateInvalid(BadRequest):
    """Invalid until date provided."""


class UpdateAppToLogin(NotAcceptable):
    """Please update your client to login."""


class UrlExpired(BadRequest):
    """The specified OAuth request has expired."""


class UrlInvalid(BadRequest):
    """Invalid URL provided."""


class UsageLimitInvalid(BadRequest):
    """The specified usage limit is invalid."""


class UserAdminInvalid(BadRequest):
    """You're not an admin."""


class UserAlreadyInvited(BadRequest):
    """You have already invited this user."""


class UserAlreadyParticipant(BadRequest):
    """The user is already in the group."""


class UserBannedInChannel(BadRequest):
    """You're banned from sending messages in supergroups/channels."""


class UserBlocked(BadRequest):
    """User blocked."""


class UserBot(BadRequest):
    """Bots can only be admins in channels."""


class UserBotInvalid(Forbidden):
    """User accounts must provide the `bot` method parameter when calling this method.
    If there is no such method parameter, this method can only be invoked by bot
    accounts.
    """


class UserBotRequired(BadRequest):
    """This method can only be called by a bot."""


class UserBotToBotDisabled(BadRequest):
    """Bot-to-bot messaging is disabled because one of the two bots hasn't enabled the
    Bot to Bot setting in @BotFather.
    """


class UserChannelsTooMuch(Forbidden):
    """One of the users you tried to add is already in too many channels/supergroups."""


class UserCreator(BadRequest):
    """For channels.editAdmin: you've tried to edit the admin rights of the owner, but
    you're not the owner; for channels.leaveChannel: you can't leave this channel,
    because you're its creator.
    """


class UserDeactivated(Unauthorized):
    """The current account was deleted by the user."""


class UserDeactivatedBan(Unauthorized):
    """The current account was deleted and banned by Telegram's antispam system."""


class UserDeleted(Forbidden):
    """You can't send this secret message because the other participant deleted their
    account.
    """


class UserDisallowedStargifts(Forbidden):
    """The recipient user has configured restrictions on which categories of star gifts
    they're willing to accept (unique, limited, or unlimited): the sender attempted to
    get a payment form for a gift that falls into a category the recipient has blocked.
    """


class UserGiftUnavailable(BadRequest):
    """Gifts are not available in the current region (stars_gifts_enabled is equal to
    false).
    """


class UserIdInvalid(BadRequest):
    """The provided user ID is invalid."""


class UserInvalid(Forbidden):
    """Invalid user provided."""


class UserIsBlocked(Forbidden):
    """You were blocked by this user."""


class UserIsBot(BadRequest):
    """Bots can't send messages to other bots."""


class UserKicked(BadRequest):
    """This user was kicked from this supergroup/channel."""


class UserNotMutualContact(BadRequest):
    """The provided user is not a mutual contact."""


class UserNotParticipant(BadRequest):
    """You're not a member of this supergroup/channel."""


class UserPermissionDenied(Forbidden):
    """The user hasn't granted or has revoked the bot's access to change their emoji
    status using bots.toggleUserEmojiStatusPermission.
    """


class UserPrivacyRestricted(Forbidden):
    """The user's privacy settings do not allow you to do this."""


class UserPublicMissing(BadRequest):
    """Cannot generate a link to stories posted by a peer without a username."""


class UserRestricted(Forbidden):
    """You're spamreported, you can't create channels or chats."""


class UserVolumeInvalid(BadRequest):
    """The specified user volume is invalid."""


class UsernameInvalid(BadRequest):
    """The provided username is not valid."""


class UsernameNotModified(BadRequest):
    """The username was not modified."""


class UsernameNotOccupied(BadRequest):
    """The provided username is not occupied."""


class UsernameOccupied(BadRequest):
    """The provided username is already occupied."""


class UsernamePurchaseAvailable(BadRequest):
    """The specified username can be purchased on https://fragment.com."""


class UsernameSuffixMissing(BadRequest):
    """The required `bot` suffix is missing from the passed username."""


class UsernamesActiveTooMuch(BadRequest):
    """The maximum number of active usernames was reached."""


class UserpicPrivacyRequired(NotAcceptable):
    """You need to disable privacy settings for your profile picture in order to make
    your geolocation public.
    """


class UserpicUploadRequired(NotAcceptable):
    """You must have a profile picture to publish your geolocation."""


class UsersTooFew(BadRequest):
    """Not enough users (to create a chat, for example)."""


class UsersTooMuch(BadRequest):
    """The maximum number of users has been exceeded (to create a chat, for example)."""


class VenueIdInvalid(BadRequest):
    """The specified venue ID is invalid."""


class VideoContentTypeInvalid(BadRequest):
    """The video's content type is invalid."""


class VideoDurationInvalid(BadRequest):
    """The duration of the specified video is invalid."""


class VideoFileInvalid(BadRequest):
    """The specified video file is invalid."""


class VideoPauseForbidden(BadRequest):
    """You cannot pause the video stream."""


class VideoStopForbidden(BadRequest):
    """You cannot stop the video stream."""


class VideoTitleEmpty(BadRequest):
    """The specified video title is empty."""


class VoiceMessagesForbidden(BadRequest):
    """This user's privacy settings forbid you from sending voice messages."""


class WallpaperFileInvalid(BadRequest):
    """The specified wallpaper file is invalid."""


class WallpaperInvalid(BadRequest):
    """The specified wallpaper is invalid."""


class WallpaperMimeInvalid(BadRequest):
    """The specified wallpaper MIME type is invalid."""


class WallpaperNotFound(BadRequest):
    """The specified wallpaper could not be found."""


class WcConvertUrlInvalid(BadRequest):
    """WC convert URL invalid."""


class WebappReqIdInvalid(BadRequest):
    """The specified webapp_req_id is invalid."""


class WebauthTokenExpired(BadRequest):
    """The specified auth token has expired."""


class WebdocumentInvalid(BadRequest):
    """Invalid webdocument URL provided."""


class WebdocumentMimeInvalid(BadRequest):
    """Invalid webdocument mime type provided."""


class WebdocumentSizeTooBig(BadRequest):
    """Webdocument is too big!"""


class WebdocumentUrlEmpty(BadRequest):
    """The passed web document URL is empty."""


class WebdocumentUrlInvalid(BadRequest):
    """The specified webdocument URL is invalid."""


class WebpageCurlFailed(BadRequest):
    """Failure while fetching the webpage with cURL."""


class WebpageMediaEmpty(BadRequest):
    """Webpage media empty."""


class WebpageNotFound(BadRequest):
    """A preview for the specified webpage `url` could not be generated."""


class WebpageUrlInvalid(BadRequest):
    """The specified webpage `url` is invalid."""


class WebpushAuthInvalid(BadRequest):
    """The specified web push authentication secret is invalid."""


class WebpushKeyInvalid(BadRequest):
    """The specified web push elliptic curve Diffie-Hellman public key is invalid."""


class WebpushTokenInvalid(BadRequest):
    """The specified web push token is invalid."""


class YouBlockedUser(BadRequest):
    """You blocked this user."""


class YourPrivacyRestricted(Forbidden):
    """You cannot fetch the read date of this message because you have disallowed other
    users to do so for *your* messages; to fix, allow other users to see *your* exact
    last online date OR purchase a Telegram Premium subscription.
    """


# Every error whose name is fixed, which is nearly all of them. This is the
# first thing a refused call is looked up in and it answers in one step.
BY_NAME: dict[str, type[RPCError]] = {
    "ABOUT_TOO_LONG": AboutTooLong,
    "ACCESS_DENIED": AccessDenied,
    "ACCESS_TOKEN_EXPIRED": AccessTokenExpired,
    "ACCESS_TOKEN_INVALID": AccessTokenInvalid,
    "ADDRESS_INVALID": AddressInvalid,
    "ADMINS_TOO_MUCH": AdminsTooMuch,
    "ADMIN_ID_INVALID": AdminIdInvalid,
    "ADMIN_RANK_EMOJI_NOT_ALLOWED": AdminRankEmojiNotAllowed,
    "ADMIN_RANK_INVALID": AdminRankInvalid,
    "ADMIN_RIGHTS_EMPTY": AdminRightsEmpty,
    "AD_EXPIRED": AdExpired,
    "AICOMPOSE_FLOOD_PREMIUM": AicomposeFloodPremium,
    "AICOMPOSE_TIMEOUT": AicomposeTimeout,
    "AICOMPOSE_TONE_INVALID": AicomposeToneInvalid,
    "AICOMPOSE_TONE_TITLE_INVALID": AicomposeToneTitleInvalid,
    "AI_COMPOSE_TASK_MISSING": AiComposeTaskMissing,
    "ALBUM_PHOTOS_TOO_MANY": AlbumPhotosTooMany,
    "ALLOW_PAYMENT_REQUIRED": AllowPaymentRequired,
    "API_GIFT_RESTRICTED_UPDATE_APP": ApiGiftRestrictedUpdateApp,
    "API_ID_INVALID": ApiIdInvalid,
    "API_ID_PUBLISHED_FLOOD": ApiIdPublishedFlood,
    "ARTICLE_TITLE_EMPTY": ArticleTitleEmpty,
    "AUDIO_CONTENT_URL_EMPTY": AudioContentUrlEmpty,
    "AUDIO_TITLE_EMPTY": AudioTitleEmpty,
    "AUTH_BYTES_INVALID": AuthBytesInvalid,
    "AUTH_KEY_DUPLICATED": AuthKeyDuplicated,
    "AUTH_KEY_INVALID": AuthKeyInvalid,
    "AUTH_KEY_PERM_EMPTY": AuthKeyPermEmpty,
    "AUTH_KEY_UNREGISTERED": AuthKeyUnregistered,
    "AUTH_KEY_UNSYNCHRONIZED": AuthKeyUnsynchronized,
    "AUTH_RESTART": AuthRestart,
    "AUTH_TOKEN_ALREADY_ACCEPTED": AuthTokenAlreadyAccepted,
    "AUTH_TOKEN_EXCEPTION": AuthTokenException,
    "AUTH_TOKEN_EXPIRED": AuthTokenExpired,
    "AUTH_TOKEN_INVALID": AuthTokenInvalid,
    "AUTH_TOKEN_INVALIDX": AuthTokenInvalidx,
    "AUTOARCHIVE_NOT_AVAILABLE": AutoarchiveNotAvailable,
    "BALANCE_TOO_LOW": BalanceTooLow,
    "BANK_CARD_NUMBER_INVALID": BankCardNumberInvalid,
    "BANNED_RIGHTS_INVALID": BannedRightsInvalid,
    "BIRTHDAY_ALREADY": BirthdayAlready,
    "BIRTHDAY_INVALID": BirthdayInvalid,
    "BOOSTS_EMPTY": BoostsEmpty,
    "BOOSTS_REQUIRED": BoostsRequired,
    "BOOST_NOT_MODIFIED": BoostNotModified,
    "BOOST_PEER_INVALID": BoostPeerInvalid,
    "BOTS_TOO_MUCH": BotsTooMuch,
    "BOT_ACCESS_FORBIDDEN": BotAccessForbidden,
    "BOT_ALREADY_DISABLED": BotAlreadyDisabled,
    "BOT_APP_BOT_INVALID": BotAppBotInvalid,
    "BOT_APP_INVALID": BotAppInvalid,
    "BOT_APP_SHORTNAME_INVALID": BotAppShortnameInvalid,
    "BOT_BUSINESS_MISSING": BotBusinessMissing,
    "BOT_CHANNELS_NA": BotChannelsNa,
    "BOT_COMMAND_DESCRIPTION_INVALID": BotCommandDescriptionInvalid,
    "BOT_COMMAND_INVALID": BotCommandInvalid,
    "BOT_CREATE_LIMIT_EXCEEDED": BotCreateLimitExceeded,
    "BOT_DOMAIN_INVALID": BotDomainInvalid,
    "BOT_FALLBACK_UNSUPPORTED": BotFallbackUnsupported,
    "BOT_FORUM_CREATE_FORBIDDEN": BotForumCreateForbidden,
    "BOT_GAMES_DISABLED": BotGamesDisabled,
    "BOT_GROUPS_BLOCKED": BotGroupsBlocked,
    "BOT_GUARD_NOT_SUPPORTED": BotGuardNotSupported,
    "BOT_ID_INVALID": BotIdInvalid,
    "BOT_INLINE_DISABLED": BotInlineDisabled,
    "BOT_INVALID": BotInvalid,
    "BOT_INVOICE_INVALID": BotInvoiceInvalid,
    "BOT_METHOD_INVALID": BotMethodInvalid,
    "BOT_NOT_CONNECTED_YET": BotNotConnectedYet,
    "BOT_ONESIDE_NOT_AVAIL": BotOnesideNotAvail,
    "BOT_PAYMENTS_DISABLED": BotPaymentsDisabled,
    "BOT_RESPONSE_TIMEOUT": BotResponseTimeout,
    "BOT_SCORE_NOT_MODIFIED": BotScoreNotModified,
    "BOT_VERIFIER_FORBIDDEN": BotVerifierForbidden,
    "BOT_WEBVIEW_DISABLED": BotWebviewDisabled,
    "BROADCAST_FORBIDDEN": BroadcastForbidden,
    "BROADCAST_ID_INVALID": BroadcastIdInvalid,
    "BROADCAST_PUBLIC_VOTERS_FORBIDDEN": BroadcastPublicVotersForbidden,
    "BROADCAST_REQUIRED": BroadcastRequired,
    "BUSINESS_ADDRESS_ACTIVE": BusinessAddressActive,
    "BUSINESS_CONNECTION_INVALID": BusinessConnectionInvalid,
    "BUSINESS_CONNECTION_NOT_ALLOWED": BusinessConnectionNotAllowed,
    "BUSINESS_PEER_INVALID": BusinessPeerInvalid,
    "BUSINESS_PEER_USAGE_MISSING": BusinessPeerUsageMissing,
    "BUSINESS_RECIPIENTS_EMPTY": BusinessRecipientsEmpty,
    "BUSINESS_WORK_HOURS_EMPTY": BusinessWorkHoursEmpty,
    "BUSINESS_WORK_HOURS_PERIOD_INVALID": BusinessWorkHoursPeriodInvalid,
    "BUTTON_COPY_TEXT_INVALID": ButtonCopyTextInvalid,
    "BUTTON_DATA_INVALID": ButtonDataInvalid,
    "BUTTON_ID_INVALID": ButtonIdInvalid,
    "BUTTON_INVALID": ButtonInvalid,
    "BUTTON_POS_INVALID": ButtonPosInvalid,
    "BUTTON_TEXT_INVALID": ButtonTextInvalid,
    "BUTTON_TYPE_INVALID": ButtonTypeInvalid,
    "BUTTON_URL_INVALID": ButtonUrlInvalid,
    "BUTTON_USER_INVALID": ButtonUserInvalid,
    "BUTTON_USER_PRIVACY_RESTRICTED": ButtonUserPrivacyRestricted,
    "CALL_ALREADY_ACCEPTED": CallAlreadyAccepted,
    "CALL_ALREADY_DECLINED": CallAlreadyDeclined,
    "CALL_NOT_ACTIVE": CallNotActive,
    "CALL_OCCUPY_FAILED": CallOccupyFailed,
    "CALL_PEER_INVALID": CallPeerInvalid,
    "CALL_PROTOCOL_COMPAT_LAYER_INVALID": CallProtocolCompatLayerInvalid,
    "CALL_PROTOCOL_FLAGS_INVALID": CallProtocolFlagsInvalid,
    "CALL_PROTOCOL_LAYER_INVALID": CallProtocolLayerInvalid,
    "CDN_METHOD_INVALID": CdnMethodInvalid,
    "CDN_UPLOAD_TIMEOUT": CdnUploadTimeout,
    "CHANNELS_ADMIN_LOCATED_TOO_MUCH": ChannelsAdminLocatedTooMuch,
    "CHANNELS_ADMIN_PUBLIC_TOO_MUCH": ChannelsAdminPublicTooMuch,
    "CHANNELS_TOO_MUCH": ChannelsTooMuch,
    "CHANNEL_FORUM_MISSING": ChannelForumMissing,
    "CHANNEL_ID_INVALID": ChannelIdInvalid,
    "CHANNEL_INVALID": ChannelInvalid,
    "CHANNEL_MONOFORUM_UNSUPPORTED": ChannelMonoforumUnsupported,
    "CHANNEL_PARICIPANT_MISSING": ChannelParicipantMissing,
    "CHANNEL_PRIVATE": ChannelPrivate,
    "CHANNEL_PUBLIC_GROUP_NA": ChannelPublicGroupNa,
    "CHANNEL_TOO_BIG": ChannelTooBig,
    "CHANNEL_TOO_LARGE": ChannelTooLarge,
    "CHARGE_ALREADY_REFUNDED": ChargeAlreadyRefunded,
    "CHARGE_ID_EMPTY": ChargeIdEmpty,
    "CHARGE_ID_INVALID": ChargeIdInvalid,
    "CHATLINKS_TOO_MUCH": ChatlinksTooMuch,
    "CHATLINK_SLUG_EMPTY": ChatlinkSlugEmpty,
    "CHATLINK_SLUG_EXPIRED": ChatlinkSlugExpired,
    "CHATLISTS_TOO_MUCH": ChatlistsTooMuch,
    "CHATLIST_EXCLUDE_INVALID": ChatlistExcludeInvalid,
    "CHAT_ABOUT_NOT_MODIFIED": ChatAboutNotModified,
    "CHAT_ABOUT_TOO_LONG": ChatAboutTooLong,
    "CHAT_ACTION_FORBIDDEN": ChatActionForbidden,
    "CHAT_ADMIN_INVITE_REQUIRED": ChatAdminInviteRequired,
    "CHAT_ADMIN_REQUIRED": ChatAdminRequired,
    "CHAT_DISCUSSION_UNALLOWED": ChatDiscussionUnallowed,
    "CHAT_FORBIDDEN": ChatForbidden,
    "CHAT_FORWARDS_RESTRICTED": ChatForwardsRestricted,
    "CHAT_GUEST_SEND_FORBIDDEN": ChatGuestSendForbidden,
    "CHAT_ID_EMPTY": ChatIdEmpty,
    "CHAT_ID_GENERATE_FAILED": ChatIdGenerateFailed,
    "CHAT_ID_INVALID": ChatIdInvalid,
    "CHAT_INVALID": ChatInvalid,
    "CHAT_INVITE_PERMANENT": ChatInvitePermanent,
    "CHAT_LINK_EXISTS": ChatLinkExists,
    "CHAT_MEMBER_ADD_FAILED": ChatMemberAddFailed,
    "CHAT_NOT_MODIFIED": ChatNotModified,
    "CHAT_PUBLIC_REQUIRED": ChatPublicRequired,
    "CHAT_RESTRICTED": ChatRestricted,
    "CHAT_REVOKE_DATE_UNSUPPORTED": ChatRevokeDateUnsupported,
    "CHAT_SEND_AUDIOS_FORBIDDEN": ChatSendAudiosForbidden,
    "CHAT_SEND_DOCS_FORBIDDEN": ChatSendDocsForbidden,
    "CHAT_SEND_GAME_FORBIDDEN": ChatSendGameForbidden,
    "CHAT_SEND_GIFS_FORBIDDEN": ChatSendGifsForbidden,
    "CHAT_SEND_INLINE_FORBIDDEN": ChatSendInlineForbidden,
    "CHAT_SEND_MEDIA_FORBIDDEN": ChatSendMediaForbidden,
    "CHAT_SEND_PHOTOS_FORBIDDEN": ChatSendPhotosForbidden,
    "CHAT_SEND_PLAIN_FORBIDDEN": ChatSendPlainForbidden,
    "CHAT_SEND_POLL_FORBIDDEN": ChatSendPollForbidden,
    "CHAT_SEND_ROUNDVIDEOS_FORBIDDEN": ChatSendRoundvideosForbidden,
    "CHAT_SEND_STICKERS_FORBIDDEN": ChatSendStickersForbidden,
    "CHAT_SEND_VIDEOS_FORBIDDEN": ChatSendVideosForbidden,
    "CHAT_SEND_VOICES_FORBIDDEN": ChatSendVoicesForbidden,
    "CHAT_SEND_WEBPAGE_FORBIDDEN": ChatSendWebpageForbidden,
    "CHAT_TITLE_EMPTY": ChatTitleEmpty,
    "CHAT_TOO_BIG": ChatTooBig,
    "CHAT_TYPE_INVALID": ChatTypeInvalid,
    "CHAT_WRITE_FORBIDDEN": ChatWriteForbidden,
    "CODE_EMPTY": CodeEmpty,
    "CODE_HASH_INVALID": CodeHashInvalid,
    "CODE_INVALID": CodeInvalid,
    "COLLECTIBLE_INVALID": CollectibleInvalid,
    "COLLECTIBLE_NOT_FOUND": CollectibleNotFound,
    "COLLECTION_ID_INVALID": CollectionIdInvalid,
    "COLOR_INVALID": ColorInvalid,
    "CONNECTION_API_ID_INVALID": ConnectionApiIdInvalid,
    "CONNECTION_APP_VERSION_EMPTY": ConnectionAppVersionEmpty,
    "CONNECTION_DEVICE_MODEL_EMPTY": ConnectionDeviceModelEmpty,
    "CONNECTION_ID_INVALID": ConnectionIdInvalid,
    "CONNECTION_LANG_PACK_INVALID": ConnectionLangPackInvalid,
    "CONNECTION_LAYER_INVALID": ConnectionLayerInvalid,
    "CONNECTION_NOT_INITED": ConnectionNotInited,
    "CONNECTION_SYSTEM_EMPTY": ConnectionSystemEmpty,
    "CONNECTION_SYSTEM_LANG_CODE_EMPTY": ConnectionSystemLangCodeEmpty,
    "CONTACT_ADD_MISSING": ContactAddMissing,
    "CONTACT_ID_INVALID": ContactIdInvalid,
    "CONTACT_MISSING": ContactMissing,
    "CONTACT_NAME_EMPTY": ContactNameEmpty,
    "CONTACT_REQ_MISSING": ContactReqMissing,
    "CREATE_CALL_FAILED": CreateCallFailed,
    "CREDENTIAL_INVALID": CredentialInvalid,
    "CURRENCY_TOTAL_AMOUNT_INVALID": CurrencyTotalAmountInvalid,
    "CUSTOM_REACTIONS_TOO_MANY": CustomReactionsTooMany,
    "DATA_HASH_SIZE_INVALID": DataHashSizeInvalid,
    "DATA_INVALID": DataInvalid,
    "DATA_JSON_INVALID": DataJsonInvalid,
    "DATA_TOO_LONG": DataTooLong,
    "DATE_EMPTY": DateEmpty,
    "DC_ID_INVALID": DcIdInvalid,
    "DH_G_A_INVALID": DhGAInvalid,
    "DOCUMENT_INVALID": DocumentInvalid,
    "EDIT_BOT_INVITE_FORBIDDEN": EditBotInviteForbidden,
    "EDIT_MESSAGE_TEMP_RESTRICTED": EditMessageTempRestricted,
    "EFFECT_CHAT_INVALID": EffectChatInvalid,
    "EFFECT_ID_INVALID": EffectIdInvalid,
    "EMAIL_HASH_EXPIRED": EmailHashExpired,
    "EMAIL_INSTALL_MISSING": EmailInstallMissing,
    "EMAIL_INVALID": EmailInvalid,
    "EMAIL_NOT_ALLOWED": EmailNotAllowed,
    "EMAIL_NOT_SETUP": EmailNotSetup,
    "EMAIL_UNCONFIRMED": EmailUnconfirmed,
    "EMAIL_VERIFY_EXPIRED": EmailVerifyExpired,
    "EMOJI_INVALID": EmojiInvalid,
    "EMOJI_MARKUP_INVALID": EmojiMarkupInvalid,
    "EMOJI_NOT_MODIFIED": EmojiNotModified,
    "EMOTICON_EMPTY": EmoticonEmpty,
    "EMOTICON_INVALID": EmoticonInvalid,
    "EMOTICON_STICKERPACK_MISSING": EmoticonStickerpackMissing,
    "ENCRYPTED_MESSAGE_INVALID": EncryptedMessageInvalid,
    "ENCRYPTION_ALREADY_ACCEPTED": EncryptionAlreadyAccepted,
    "ENCRYPTION_ALREADY_DECLINED": EncryptionAlreadyDeclined,
    "ENCRYPTION_DECLINED": EncryptionDeclined,
    "ENCRYPTION_ID_INVALID": EncryptionIdInvalid,
    "ENTITIES_TOO_LONG": EntitiesTooLong,
    "ENTITY_BOUNDS_INVALID": EntityBoundsInvalid,
    "ENTITY_DATE_FORMAT_INVALID": EntityDateFormatInvalid,
    "ENTITY_DATE_INVALID": EntityDateInvalid,
    "ENTITY_DATE_TOO_LONG": EntityDateTooLong,
    "ENTITY_MENTION_USER_INVALID": EntityMentionUserInvalid,
    "ERROR_TEXT_EMPTY": ErrorTextEmpty,
    "EXPIRES_AT_INVALID": ExpiresAtInvalid,
    "EXPIRE_DATE_INVALID": ExpireDateInvalid,
    "EXPORT_CARD_INVALID": ExportCardInvalid,
    "EXTENDED_MEDIA_AMOUNT_INVALID": ExtendedMediaAmountInvalid,
    "EXTENDED_MEDIA_EMPTY": ExtendedMediaEmpty,
    "EXTENDED_MEDIA_INVALID": ExtendedMediaInvalid,
    "EXTENDED_MEDIA_PEER_INVALID": ExtendedMediaPeerInvalid,
    "EXTERNAL_URL_INVALID": ExternalUrlInvalid,
    "FILEREF_UPGRADE_NEEDED": FilerefUpgradeNeeded,
    "FILE_CONTENT_TYPE_INVALID": FileContentTypeInvalid,
    "FILE_EMTPY": FileEmtpy,
    "FILE_ID_INVALID": FileIdInvalid,
    "FILE_PARTS_INVALID": FilePartsInvalid,
    "FILE_PART_EMPTY": FilePartEmpty,
    "FILE_PART_INVALID": FilePartInvalid,
    "FILE_PART_LENGTH_INVALID": FilePartLengthInvalid,
    "FILE_PART_SIZE_CHANGED": FilePartSizeChanged,
    "FILE_PART_SIZE_INVALID": FilePartSizeInvalid,
    "FILE_PART_TOO_BIG": FilePartTooBig,
    "FILE_PART_TOO_SMALL": FilePartTooSmall,
    "FILE_REFERENCE_EMPTY": FileReferenceEmpty,
    "FILE_REFERENCE_EXPIRED": FileReferenceExpired,
    "FILE_REFERENCE_INVALID": FileReferenceInvalid,
    "FILE_TITLE_EMPTY": FileTitleEmpty,
    "FILE_TOKEN_INVALID": FileTokenInvalid,
    "FILTER_ID_INVALID": FilterIdInvalid,
    "FILTER_INCLUDE_EMPTY": FilterIncludeEmpty,
    "FILTER_NOT_SUPPORTED": FilterNotSupported,
    "FILTER_TITLE_EMPTY": FilterTitleEmpty,
    "FIRSTNAME_INVALID": FirstnameInvalid,
    "FOLDER_ID_EMPTY": FolderIdEmpty,
    "FOLDER_ID_INVALID": FolderIdInvalid,
    "FORM_EXPIRED": FormExpired,
    "FORM_ID_EMPTY": FormIdEmpty,
    "FORM_SUBMIT_DUPLICATE": FormSubmitDuplicate,
    "FORM_UNSUPPORTED": FormUnsupported,
    "FORUM_ENABLED": ForumEnabled,
    "FRESH_CHANGE_ADMINS_FORBIDDEN": FreshChangeAdminsForbidden,
    "FRESH_CHANGE_PHONE_FORBIDDEN": FreshChangePhoneForbidden,
    "FRESH_RESET_AUTHORISATION_FORBIDDEN": FreshResetAuthorisationForbidden,
    "FROM_MESSAGE_BOT_DISABLED": FromMessageBotDisabled,
    "FROM_PEER_INVALID": FromPeerInvalid,
    "FROZEN_METHOD_INVALID": FrozenMethodInvalid,
    "FROZEN_PARTICIPANT_MISSING": FrozenParticipantMissing,
    "GAME_BOT_INVALID": GameBotInvalid,
    "GENERAL_MODIFY_ICON_FORBIDDEN": GeneralModifyIconForbidden,
    "GEO_POINT_INVALID": GeoPointInvalid,
    "GIFT_MONTHS_INVALID": GiftMonthsInvalid,
    "GIFT_SLUG_EXPIRED": GiftSlugExpired,
    "GIFT_SLUG_INVALID": GiftSlugInvalid,
    "GIFT_STARS_INVALID": GiftStarsInvalid,
    "GIF_CONTENT_TYPE_INVALID": GifContentTypeInvalid,
    "GIF_ID_INVALID": GifIdInvalid,
    "GRAPH_EXPIRED_RELOAD": GraphExpiredReload,
    "GRAPH_INVALID_RELOAD": GraphInvalidReload,
    "GRAPH_OUTDATED_RELOAD": GraphOutdatedReload,
    "GROUPCALL_ALREADY_DISCARDED": GroupcallAlreadyDiscarded,
    "GROUPCALL_ALREADY_STARTED": GroupcallAlreadyStarted,
    "GROUPCALL_CHANGE_FORBIDDEN": GroupcallChangeForbidden,
    "GROUPCALL_FORBIDDEN": GroupcallForbidden,
    "GROUPCALL_INVALID": GroupcallInvalid,
    "GROUPCALL_JOIN_MISSING": GroupcallJoinMissing,
    "GROUPCALL_NOT_MODIFIED": GroupcallNotModified,
    "GROUPCALL_SSRC_DUPLICATE_MUCH": GroupcallSsrcDuplicateMuch,
    "GROUPED_MEDIA_INVALID": GroupedMediaInvalid,
    "HASHTAG_INVALID": HashtagInvalid,
    "HASH_INVALID": HashInvalid,
    "HASH_SIZE_INVALID": HashSizeInvalid,
    "HIDE_REQUESTER_MISSING": HideRequesterMissing,
    "ID_EXPIRED": IdExpired,
    "ID_INVALID": IdInvalid,
    "IMAGE_PROCESS_FAILED": ImageProcessFailed,
    "IMPORT_FILE_INVALID": ImportFileInvalid,
    "IMPORT_FORMAT_DATE_INVALID": ImportFormatDateInvalid,
    "IMPORT_FORMAT_UNRECOGNIZED": ImportFormatUnrecognized,
    "IMPORT_ID_INVALID": ImportIdInvalid,
    "IMPORT_TOKEN_INVALID": ImportTokenInvalid,
    "INLINE_BOT_REQUIRED": InlineBotRequired,
    "INLINE_RESULT_EXPIRED": InlineResultExpired,
    "INPUT_CHATLIST_INVALID": InputChatlistInvalid,
    "INPUT_CONSTRUCTOR_INVALID": InputConstructorInvalid,
    "INPUT_FETCH_ERROR": InputFetchError,
    "INPUT_FETCH_FAIL": InputFetchFail,
    "INPUT_FILE_INVALID": InputFileInvalid,
    "INPUT_FILTER_INVALID": InputFilterInvalid,
    "INPUT_LAYER_INVALID": InputLayerInvalid,
    "INPUT_METHOD_INVALID": InputMethodInvalid,
    "INPUT_PEERS_EMPTY": InputPeersEmpty,
    "INPUT_PURPOSE_INVALID": InputPurposeInvalid,
    "INPUT_REQUEST_TOO_LONG": InputRequestTooLong,
    "INPUT_STARS_AMOUNT_INVALID": InputStarsAmountInvalid,
    "INPUT_STARS_NANOS_INVALID": InputStarsNanosInvalid,
    "INPUT_TEXT_EMPTY": InputTextEmpty,
    "INPUT_TEXT_TOO_LONG": InputTextTooLong,
    "INPUT_USER_DEACTIVATED": InputUserDeactivated,
    "INVITES_TOO_MUCH": InvitesTooMuch,
    "INVITE_FORBIDDEN_WITH_JOINAS": InviteForbiddenWithJoinas,
    "INVITE_HASH_EMPTY": InviteHashEmpty,
    "INVITE_HASH_EXPIRED": InviteHashExpired,
    "INVITE_HASH_INVALID": InviteHashInvalid,
    "INVITE_REQUEST_SENT": InviteRequestSent,
    "INVITE_REVOKED_MISSING": InviteRevokedMissing,
    "INVITE_SLUG_EMPTY": InviteSlugEmpty,
    "INVITE_SLUG_EXPIRED": InviteSlugExpired,
    "INVITE_SLUG_INVALID": InviteSlugInvalid,
    "INVOICE_INVALID": InvoiceInvalid,
    "INVOICE_PAYLOAD_INVALID": InvoicePayloadInvalid,
    "JOIN_AS_PEER_INVALID": JoinAsPeerInvalid,
    "LANGUAGE_INVALID": LanguageInvalid,
    "LANG_CODE_INVALID": LangCodeInvalid,
    "LANG_CODE_NOT_SUPPORTED": LangCodeNotSupported,
    "LANG_PACK_INVALID": LangPackInvalid,
    "LASTNAME_INVALID": LastnameInvalid,
    "LIMIT_INVALID": LimitInvalid,
    "LIMIT_PER_POST_INVALID": LimitPerPostInvalid,
    "LINK_NOT_MODIFIED": LinkNotModified,
    "LOCATION_INVALID": LocationInvalid,
    "MANAGER_INVALID": ManagerInvalid,
    "MANAGER_PERMISSION_MISSING": ManagerPermissionMissing,
    "MAX_DATE_INVALID": MaxDateInvalid,
    "MAX_ID_INVALID": MaxIdInvalid,
    "MAX_QTS_INVALID": MaxQtsInvalid,
    "MD5_CHECKSUM_INVALID": Md5ChecksumInvalid,
    "MEDIA_ALREADY_PAID": MediaAlreadyPaid,
    "MEDIA_CAPTION_TOO_LONG": MediaCaptionTooLong,
    "MEDIA_EMPTY": MediaEmpty,
    "MEDIA_FILE_INVALID": MediaFileInvalid,
    "MEDIA_GROUPED_INVALID": MediaGroupedInvalid,
    "MEDIA_INVALID": MediaInvalid,
    "MEDIA_NEW_INVALID": MediaNewInvalid,
    "MEDIA_PREV_INVALID": MediaPrevInvalid,
    "MEDIA_TTL_INVALID": MediaTtlInvalid,
    "MEDIA_TYPE_INVALID": MediaTypeInvalid,
    "MEDIA_VIDEO_STORY_MISSING": MediaVideoStoryMissing,
    "MEGAGROUP_GEO_REQUIRED": MegagroupGeoRequired,
    "MEGAGROUP_ID_INVALID": MegagroupIdInvalid,
    "MEGAGROUP_PREHISTORY_HIDDEN": MegagroupPrehistoryHidden,
    "MEGAGROUP_REQUIRED": MegagroupRequired,
    "MESSAGE_AUTHOR_REQUIRED": MessageAuthorRequired,
    "MESSAGE_DELETE_FORBIDDEN": MessageDeleteForbidden,
    "MESSAGE_EDIT_TIME_EXPIRED": MessageEditTimeExpired,
    "MESSAGE_EMPTY": MessageEmpty,
    "MESSAGE_IDS_EMPTY": MessageIdsEmpty,
    "MESSAGE_ID_INVALID": MessageIdInvalid,
    "MESSAGE_NOT_MODIFIED": MessageNotModified,
    "MESSAGE_NOT_READ_YET": MessageNotReadYet,
    "MESSAGE_POLL_CLOSED": MessagePollClosed,
    "MESSAGE_REQUIRED": MessageRequired,
    "MESSAGE_TOO_LONG": MessageTooLong,
    "MESSAGE_TOO_OLD": MessageTooOld,
    "METHOD_INVALID": MethodInvalid,
    "MIN_DATE_INVALID": MinDateInvalid,
    "MONTH_INVALID": MonthInvalid,
    "MSG_ID_INVALID": MsgIdInvalid,
    "MSG_TOO_OLD": MsgTooOld,
    "MSG_VOICE_MISSING": MsgVoiceMissing,
    "MSG_VOICE_TOO_LONG": MsgVoiceTooLong,
    "MSG_WAIT_FAILED": MsgWaitFailed,
    "MSG_WAIT_TIMEOUT": MsgWaitTimeout,
    "MULTI_MEDIA_TOO_LONG": MultiMediaTooLong,
    "NAME_INVALID": NameInvalid,
    "NEED_ACTION_MISSING": NeedActionMissing,
    "NEW_SALT_INVALID": NewSaltInvalid,
    "NEW_SETTINGS_EMPTY": NewSettingsEmpty,
    "NEW_SETTINGS_INVALID": NewSettingsInvalid,
    "NEXT_OFFSET_INVALID": NextOffsetInvalid,
    "NOGENERAL_HIDE_FORBIDDEN": NogeneralHideForbidden,
    "NOT_ELIGIBLE": NotEligible,
    "NOT_JOINED": NotJoined,
    "NO_PAYMENT_NEEDED": NoPaymentNeeded,
    "OAUTH_REQUEST_INVALID": OauthRequestInvalid,
    "OFFSET_INVALID": OffsetInvalid,
    "OFFSET_PEER_ID_INVALID": OffsetPeerIdInvalid,
    "OPTIONS_TOO_MUCH": OptionsTooMuch,
    "OPTION_INVALID": OptionInvalid,
    "ORDER_INVALID": OrderInvalid,
    "PACK_SHORT_NAME_INVALID": PackShortNameInvalid,
    "PACK_SHORT_NAME_OCCUPIED": PackShortNameOccupied,
    "PACK_TITLE_INVALID": PackTitleInvalid,
    "PACK_TYPE_INVALID": PackTypeInvalid,
    "PARENT_PEER_INVALID": ParentPeerInvalid,
    "PARTICIPANTS_TOO_FEW": ParticipantsTooFew,
    "PARTICIPANT_ID_INVALID": ParticipantIdInvalid,
    "PARTICIPANT_JOIN_MISSING": ParticipantJoinMissing,
    "PARTICIPANT_VERSION_OUTDATED": ParticipantVersionOutdated,
    "PASSKEY_ORIGIN_MISMATCH": PasskeyOriginMismatch,
    "PASSWORD_EMPTY": PasswordEmpty,
    "PASSWORD_HASH_INVALID": PasswordHashInvalid,
    "PASSWORD_MISSING": PasswordMissing,
    "PASSWORD_RECOVERY_EXPIRED": PasswordRecoveryExpired,
    "PASSWORD_RECOVERY_NA": PasswordRecoveryNa,
    "PASSWORD_REQUIRED": PasswordRequired,
    "PAYMENT_CREDENTIALS_INVALID": PaymentCredentialsInvalid,
    "PAYMENT_PROVIDER_INVALID": PaymentProviderInvalid,
    "PAYMENT_REQUIRED": PaymentRequired,
    "PAYMENT_UNSUPPORTED": PaymentUnsupported,
    "PEERS_LIST_EMPTY": PeersListEmpty,
    "PEER_FLOOD": PeerFlood,
    "PEER_HISTORY_EMPTY": PeerHistoryEmpty,
    "PEER_ID_INVALID": PeerIdInvalid,
    "PEER_ID_NOT_SUPPORTED": PeerIdNotSupported,
    "PEER_TYPES_INVALID": PeerTypesInvalid,
    "PERSISTENT_TIMESTAMP_EMPTY": PersistentTimestampEmpty,
    "PERSISTENT_TIMESTAMP_INVALID": PersistentTimestampInvalid,
    "PERSISTENT_TIMESTAMP_OUTDATED": PersistentTimestampOutdated,
    "PHONE_CODE_EMPTY": PhoneCodeEmpty,
    "PHONE_CODE_EXPIRED": PhoneCodeExpired,
    "PHONE_CODE_HASH_EMPTY": PhoneCodeHashEmpty,
    "PHONE_CODE_INVALID": PhoneCodeInvalid,
    "PHONE_HASH_EXPIRED": PhoneHashExpired,
    "PHONE_NOT_OCCUPIED": PhoneNotOccupied,
    "PHONE_NUMBER_APP_SIGNUP_FORBIDDEN": PhoneNumberAppSignupForbidden,
    "PHONE_NUMBER_BANNED": PhoneNumberBanned,
    "PHONE_NUMBER_FLOOD": PhoneNumberFlood,
    "PHONE_NUMBER_INVALID": PhoneNumberInvalid,
    "PHONE_NUMBER_OCCUPIED": PhoneNumberOccupied,
    "PHONE_NUMBER_UNOCCUPIED": PhoneNumberUnoccupied,
    "PHONE_PASSWORD_FLOOD": PhonePasswordFlood,
    "PHONE_PASSWORD_PROTECTED": PhonePasswordProtected,
    "PHOTO_CONTENT_TYPE_INVALID": PhotoContentTypeInvalid,
    "PHOTO_CONTENT_URL_EMPTY": PhotoContentUrlEmpty,
    "PHOTO_CROP_FILE_MISSING": PhotoCropFileMissing,
    "PHOTO_CROP_SIZE_SMALL": PhotoCropSizeSmall,
    "PHOTO_EXT_INVALID": PhotoExtInvalid,
    "PHOTO_FILE_MISSING": PhotoFileMissing,
    "PHOTO_ID_INVALID": PhotoIdInvalid,
    "PHOTO_INVALID": PhotoInvalid,
    "PHOTO_INVALID_DIMENSIONS": PhotoInvalidDimensions,
    "PHOTO_SAVE_FILE_INVALID": PhotoSaveFileInvalid,
    "PHOTO_THUMB_URL_EMPTY": PhotoThumbUrlEmpty,
    "PINNED_DIALOGS_TOO_MUCH": PinnedDialogsTooMuch,
    "PINNED_TOO_MUCH": PinnedTooMuch,
    "PINNED_TOPIC_NOT_MODIFIED": PinnedTopicNotModified,
    "PIN_RESTRICTED": PinRestricted,
    "POLL_ANSWERS_INVALID": PollAnswersInvalid,
    "POLL_ANSWER_INVALID": PollAnswerInvalid,
    "POLL_COUNTRY_RESTRICTED": PollCountryRestricted,
    "POLL_MEMBER_RESTRICTED": PollMemberRestricted,
    "POLL_OPTION_DUPLICATE": PollOptionDuplicate,
    "POLL_OPTION_INVALID": PollOptionInvalid,
    "POLL_QUESTION_INVALID": PollQuestionInvalid,
    "POLL_VOTE_REQUIRED": PollVoteRequired,
    "PRECHECKOUT_FAILED": PrecheckoutFailed,
    "PREMIUM_ACCOUNT_REQUIRED": PremiumAccountRequired,
    "PREMIUM_CURRENTLY_UNAVAILABLE": PremiumCurrentlyUnavailable,
    "PREMIUM_PURPOSE_INVALID": PremiumPurposeInvalid,
    "PRICING_CHAT_INVALID": PricingChatInvalid,
    "PRIVACY_KEY_INVALID": PrivacyKeyInvalid,
    "PRIVACY_PREMIUM_REQUIRED": PrivacyPremiumRequired,
    "PRIVACY_TOO_LONG": PrivacyTooLong,
    "PRIVACY_VALUE_INVALID": PrivacyValueInvalid,
    "PUBLIC_BROADCAST_EXPECTED": PublicBroadcastExpected,
    "PUBLIC_CHANNEL_MISSING": PublicChannelMissing,
    "PUBLIC_KEY_INVALID": PublicKeyInvalid,
    "PUBLIC_KEY_REQUIRED": PublicKeyRequired,
    "PURPOSE_INVALID": PurposeInvalid,
    "QUERY_ID_EMPTY": QueryIdEmpty,
    "QUERY_ID_INVALID": QueryIdInvalid,
    "QUERY_TOO_SHORT": QueryTooShort,
    "QUICK_REPLIES_BOT_NOT_ALLOWED": QuickRepliesBotNotAllowed,
    "QUICK_REPLIES_TOO_MUCH": QuickRepliesTooMuch,
    "QUIZ_ANSWER_MISSING": QuizAnswerMissing,
    "QUIZ_CORRECT_ANSWERS_EMPTY": QuizCorrectAnswersEmpty,
    "QUIZ_CORRECT_ANSWERS_TOO_MUCH": QuizCorrectAnswersTooMuch,
    "QUIZ_CORRECT_ANSWER_INVALID": QuizCorrectAnswerInvalid,
    "QUIZ_MULTIPLE_INVALID": QuizMultipleInvalid,
    "QUOTE_TEXT_INVALID": QuoteTextInvalid,
    "RAISE_HAND_FORBIDDEN": RaiseHandForbidden,
    "RANDOM_ID_DUPLICATE": RandomIdDuplicate,
    "RANDOM_ID_EMPTY": RandomIdEmpty,
    "RANDOM_ID_EXPIRED": RandomIdExpired,
    "RANDOM_ID_INVALID": RandomIdInvalid,
    "RANDOM_LENGTH_INVALID": RandomLengthInvalid,
    "RANGES_INVALID": RangesInvalid,
    "REACTIONS_COUNT_INVALID": ReactionsCountInvalid,
    "REACTIONS_TOO_MANY": ReactionsTooMany,
    "REACTION_EMPTY": ReactionEmpty,
    "REACTION_INVALID": ReactionInvalid,
    "RECEIPT_EMPTY": ReceiptEmpty,
    "REPLY_MARKUP_BUY_EMPTY": ReplyMarkupBuyEmpty,
    "REPLY_MARKUP_GAME_EMPTY": ReplyMarkupGameEmpty,
    "REPLY_MARKUP_INVALID": ReplyMarkupInvalid,
    "REPLY_MARKUP_TOO_LONG": ReplyMarkupTooLong,
    "REPLY_MESSAGES_TOO_MUCH": ReplyMessagesTooMuch,
    "REPLY_MESSAGE_ID_INVALID": ReplyMessageIdInvalid,
    "REPLY_TO_INVALID": ReplyToInvalid,
    "REPLY_TO_MONOFORUM_PEER_INVALID": ReplyToMonoforumPeerInvalid,
    "REPLY_TO_USER_INVALID": ReplyToUserInvalid,
    "REQUEST_MSG_EXPIRED": RequestMsgExpired,
    "REQUEST_TOKEN_INVALID": RequestTokenInvalid,
    "RESELL_STARS_TOO_FEW": ResellStarsTooFew,
    "RESELL_STARS_TOO_MUCH": ResellStarsTooMuch,
    "RESET_REQUEST_MISSING": ResetRequestMissing,
    "RESULTS_TOO_MUCH": ResultsTooMuch,
    "RESULT_ID_DUPLICATE": ResultIdDuplicate,
    "RESULT_ID_EMPTY": ResultIdEmpty,
    "RESULT_ID_INVALID": ResultIdInvalid,
    "RESULT_TYPE_INVALID": ResultTypeInvalid,
    "REVOTE_NOT_ALLOWED": RevoteNotAllowed,
    "RIGHTS_NOT_MODIFIED": RightsNotModified,
    "RIGHT_FORBIDDEN": RightForbidden,
    "RINGTONE_INVALID": RingtoneInvalid,
    "RINGTONE_MIME_INVALID": RingtoneMimeInvalid,
    "RSA_DECRYPT_FAILED": RsaDecryptFailed,
    "SAVED_ID_EMPTY": SavedIdEmpty,
    "SCHEDULE_BOT_NOT_ALLOWED": ScheduleBotNotAllowed,
    "SCHEDULE_DATE_INVALID": ScheduleDateInvalid,
    "SCHEDULE_DATE_TOO_LATE": ScheduleDateTooLate,
    "SCHEDULE_STATUS_PRIVATE": ScheduleStatusPrivate,
    "SCHEDULE_TOO_MUCH": ScheduleTooMuch,
    "SCORE_INVALID": ScoreInvalid,
    "SEARCH_QUERY_EMPTY": SearchQueryEmpty,
    "SEARCH_WITH_LINK_NOT_SUPPORTED": SearchWithLinkNotSupported,
    "SECONDS_INVALID": SecondsInvalid,
    "SECURE_SECRET_REQUIRED": SecureSecretRequired,
    "SELF_DELETE_RESTRICTED": SelfDeleteRestricted,
    "SEND_AS_PEER_INVALID": SendAsPeerInvalid,
    "SEND_CODE_UNAVAILABLE": SendCodeUnavailable,
    "SEND_MEDIA_INVALID": SendMediaInvalid,
    "SEND_MESSAGE_GAME_INVALID": SendMessageGameInvalid,
    "SEND_MESSAGE_MEDIA_INVALID": SendMessageMediaInvalid,
    "SEND_MESSAGE_TYPE_INVALID": SendMessageTypeInvalid,
    "SENSITIVE_CHANGE_FORBIDDEN": SensitiveChangeForbidden,
    "SESSION_EXPIRED": SessionExpired,
    "SESSION_PASSWORD_NEEDED": SessionPasswordNeeded,
    "SESSION_REVOKED": SessionRevoked,
    "SETTINGS_INVALID": SettingsInvalid,
    "SHA256_HASH_INVALID": Sha256HashInvalid,
    "SHORTCUT_INVALID": ShortcutInvalid,
    "SHORT_NAME_INVALID": ShortNameInvalid,
    "SHORT_NAME_OCCUPIED": ShortNameOccupied,
    "SIGN_IN_FAILED": SignInFailed,
    "SLOTS_EMPTY": SlotsEmpty,
    "SLOWMODE_MULTI_MSGS_DISABLED": SlowmodeMultiMsgsDisabled,
    "SLUG_INVALID": SlugInvalid,
    "SMSJOB_ID_INVALID": SmsjobIdInvalid,
    "SMS_CODE_CREATE_FAILED": SmsCodeCreateFailed,
    "SRP_A_INVALID": SrpAInvalid,
    "SRP_ID_INVALID": SrpIdInvalid,
    "SRP_PASSWORD_CHANGED": SrpPasswordChanged,
    "STARGIFT_ALREADY_CONVERTED": StargiftAlreadyConverted,
    "STARGIFT_ALREADY_REFUNDED": StargiftAlreadyRefunded,
    "STARGIFT_ALREADY_UPGRADED": StargiftAlreadyUpgraded,
    "STARGIFT_ATTRIBUTE_INVALID": StargiftAttributeInvalid,
    "STARGIFT_EXPORT_IN_PROGRESS": StargiftExportInProgress,
    "STARGIFT_INVALID": StargiftInvalid,
    "STARGIFT_MESSAGE_INVALID": StargiftMessageInvalid,
    "STARGIFT_NOT_FOUND": StargiftNotFound,
    "STARGIFT_NOT_OWNER": StargiftNotOwner,
    "STARGIFT_NOT_UNIQUE": StargiftNotUnique,
    "STARGIFT_OBJECT_INVALID": StargiftObjectInvalid,
    "STARGIFT_OFFER_INVALID": StargiftOfferInvalid,
    "STARGIFT_OFFER_NOT_ALLOWED": StargiftOfferNotAllowed,
    "STARGIFT_OWNER_INVALID": StargiftOwnerInvalid,
    "STARGIFT_PEER_INVALID": StargiftPeerInvalid,
    "STARGIFT_RESELL_CURRENCY_NOT_ALLOWED": StargiftResellCurrencyNotAllowed,
    "STARGIFT_SLUG_INVALID": StargiftSlugInvalid,
    "STARGIFT_UPGRADE_UNAVAILABLE": StargiftUpgradeUnavailable,
    "STARGIFT_USAGE_LIMITED": StargiftUsageLimited,
    "STARGIFT_USER_USAGE_LIMITED": StargiftUserUsageLimited,
    "STARREF_AWAITING_END": StarrefAwaitingEnd,
    "STARREF_EXPIRED": StarrefExpired,
    "STARREF_HASH_REVOKED": StarrefHashRevoked,
    "STARREF_PERMILLE_INVALID": StarrefPermilleInvalid,
    "STARREF_PERMILLE_TOO_LOW": StarrefPermilleTooLow,
    "STARS_AMOUNT_INVALID": StarsAmountInvalid,
    "STARS_FORM_AMOUNT_MISMATCH": StarsFormAmountMismatch,
    "STARS_INVOICE_INVALID": StarsInvoiceInvalid,
    "STARS_PAYMENT_REQUIRED": StarsPaymentRequired,
    "START_PARAM_EMPTY": StartParamEmpty,
    "START_PARAM_INVALID": StartParamInvalid,
    "START_PARAM_TOO_LONG": StartParamTooLong,
    "STICKERPACK_STICKERS_TOO_MUCH": StickerpackStickersTooMuch,
    "STICKERSET_INVALID": StickersetInvalid,
    "STICKERSET_NOT_MODIFIED": StickersetNotModified,
    "STICKERSET_OWNER_ANONYMOUS": StickersetOwnerAnonymous,
    "STICKERS_EMPTY": StickersEmpty,
    "STICKERS_TOO_MUCH": StickersTooMuch,
    "STICKER_DOCUMENT_INVALID": StickerDocumentInvalid,
    "STICKER_EMOJI_INVALID": StickerEmojiInvalid,
    "STICKER_FILE_INVALID": StickerFileInvalid,
    "STICKER_GIF_DIMENSIONS": StickerGifDimensions,
    "STICKER_ID_INVALID": StickerIdInvalid,
    "STICKER_INVALID": StickerInvalid,
    "STICKER_MIME_INVALID": StickerMimeInvalid,
    "STICKER_PNG_DIMENSIONS": StickerPngDimensions,
    "STICKER_PNG_NOPNG": StickerPngNopng,
    "STICKER_TGS_NODOC": StickerTgsNodoc,
    "STICKER_TGS_NOTGS": StickerTgsNotgs,
    "STICKER_THUMB_PNG_NOPNG": StickerThumbPngNopng,
    "STICKER_THUMB_TGS_NOTGS": StickerThumbTgsNotgs,
    "STICKER_VIDEO_BIG": StickerVideoBig,
    "STICKER_VIDEO_NODOC": StickerVideoNodoc,
    "STICKER_VIDEO_NOWEBM": StickerVideoNowebm,
    "STORIES_NEVER_CREATED": StoriesNeverCreated,
    "STORIES_TOO_MUCH": StoriesTooMuch,
    "STORY_ID_EMPTY": StoryIdEmpty,
    "STORY_ID_INVALID": StoryIdInvalid,
    "STORY_NOT_MODIFIED": StoryNotModified,
    "STORY_PERIOD_INVALID": StoryPeriodInvalid,
    "SUBSCRIPTION_EXPORT_MISSING": SubscriptionExportMissing,
    "SUBSCRIPTION_ID_INVALID": SubscriptionIdInvalid,
    "SUBSCRIPTION_PERIOD_INVALID": SubscriptionPeriodInvalid,
    "SUGGESTED_POST_AMOUNT_INVALID": SuggestedPostAmountInvalid,
    "SUGGESTED_POST_PEER_INVALID": SuggestedPostPeerInvalid,
    "SWITCH_PM_TEXT_EMPTY": SwitchPmTextEmpty,
    "SWITCH_WEBVIEW_URL_INVALID": SwitchWebviewUrlInvalid,
    "TAKEOUT_INVALID": TakeoutInvalid,
    "TAKEOUT_REQUIRED": TakeoutRequired,
    "TASK_ALREADY_EXISTS": TaskAlreadyExists,
    "TEMP_AUTH_KEY_ALREADY_BOUND": TempAuthKeyAlreadyBound,
    "TEMP_AUTH_KEY_EMPTY": TempAuthKeyEmpty,
    "TERMS_URL_INVALID": TermsUrlInvalid,
    "TEXTDRAFT_PEER_INVALID": TextdraftPeerInvalid,
    "THEME_FILE_INVALID": ThemeFileInvalid,
    "THEME_FORMAT_INVALID": ThemeFormatInvalid,
    "THEME_INVALID": ThemeInvalid,
    "THEME_MIME_INVALID": ThemeMimeInvalid,
    "THEME_PARAMS_INVALID": ThemeParamsInvalid,
    "THEME_SLUG_INVALID": ThemeSlugInvalid,
    "THEME_TITLE_INVALID": ThemeTitleInvalid,
    "TIMEZONE_INVALID": TimezoneInvalid,
    "TITLE_INVALID": TitleInvalid,
    "TMP_PASSWORD_DISABLED": TmpPasswordDisabled,
    "TMP_PASSWORD_INVALID": TmpPasswordInvalid,
    "TODO_ITEMS_EMPTY": TodoItemsEmpty,
    "TODO_ITEMS_TOO_MUCH": TodoItemsTooMuch,
    "TODO_ITEM_DUPLICATE": TodoItemDuplicate,
    "TODO_NOT_MODIFIED": TodoNotModified,
    "TOKEN_EMPTY": TokenEmpty,
    "TOKEN_INVALID": TokenInvalid,
    "TOKEN_TYPE_INVALID": TokenTypeInvalid,
    "TOPICS_EMPTY": TopicsEmpty,
    "TOPIC_CLOSED": TopicClosed,
    "TOPIC_CLOSE_SEPARATELY": TopicCloseSeparately,
    "TOPIC_DELETED": TopicDeleted,
    "TOPIC_HIDE_SEPARATELY": TopicHideSeparately,
    "TOPIC_ID_INVALID": TopicIdInvalid,
    "TOPIC_NOT_MODIFIED": TopicNotModified,
    "TOPIC_TITLE_EMPTY": TopicTitleEmpty,
    "TO_ID_INVALID": ToIdInvalid,
    "TO_LANG_INVALID": ToLangInvalid,
    "TRANSACTION_ID_INVALID": TransactionIdInvalid,
    "TRANSCRIPTION_FAILED": TranscriptionFailed,
    "TRANSLATE_REQ_FAILED": TranslateReqFailed,
    "TRANSLATE_REQ_QUOTA_EXCEEDED": TranslateReqQuotaExceeded,
    "TRANSLATIONS_DISABLED": TranslationsDisabled,
    "TRANSLATION_TIMEOUT": TranslationTimeout,
    "TTL_DAYS_INVALID": TtlDaysInvalid,
    "TTL_MEDIA_INVALID": TtlMediaInvalid,
    "TTL_PERIOD_INVALID": TtlPeriodInvalid,
    "TYPES_EMPTY": TypesEmpty,
    "Timeout": Timeout,
    "UNSUPPORTED": Unsupported,
    "UNTIL_DATE_INVALID": UntilDateInvalid,
    "UPDATE_APP_TO_LOGIN": UpdateAppToLogin,
    "URL_EXPIRED": UrlExpired,
    "URL_INVALID": UrlInvalid,
    "USAGE_LIMIT_INVALID": UsageLimitInvalid,
    "USERNAMES_ACTIVE_TOO_MUCH": UsernamesActiveTooMuch,
    "USERNAME_INVALID": UsernameInvalid,
    "USERNAME_NOT_MODIFIED": UsernameNotModified,
    "USERNAME_NOT_OCCUPIED": UsernameNotOccupied,
    "USERNAME_OCCUPIED": UsernameOccupied,
    "USERNAME_PURCHASE_AVAILABLE": UsernamePurchaseAvailable,
    "USERNAME_SUFFIX_MISSING": UsernameSuffixMissing,
    "USERPIC_PRIVACY_REQUIRED": UserpicPrivacyRequired,
    "USERPIC_UPLOAD_REQUIRED": UserpicUploadRequired,
    "USERS_TOO_FEW": UsersTooFew,
    "USERS_TOO_MUCH": UsersTooMuch,
    "USER_ADMIN_INVALID": UserAdminInvalid,
    "USER_ALREADY_INVITED": UserAlreadyInvited,
    "USER_ALREADY_PARTICIPANT": UserAlreadyParticipant,
    "USER_BANNED_IN_CHANNEL": UserBannedInChannel,
    "USER_BLOCKED": UserBlocked,
    "USER_BOT": UserBot,
    "USER_BOT_INVALID": UserBotInvalid,
    "USER_BOT_REQUIRED": UserBotRequired,
    "USER_BOT_TO_BOT_DISABLED": UserBotToBotDisabled,
    "USER_CHANNELS_TOO_MUCH": UserChannelsTooMuch,
    "USER_CREATOR": UserCreator,
    "USER_DEACTIVATED": UserDeactivated,
    "USER_DEACTIVATED_BAN": UserDeactivatedBan,
    "USER_DELETED": UserDeleted,
    "USER_DISALLOWED_STARGIFTS": UserDisallowedStargifts,
    "USER_GIFT_UNAVAILABLE": UserGiftUnavailable,
    "USER_ID_INVALID": UserIdInvalid,
    "USER_INVALID": UserInvalid,
    "USER_IS_BLOCKED": UserIsBlocked,
    "USER_IS_BOT": UserIsBot,
    "USER_KICKED": UserKicked,
    "USER_NOT_MUTUAL_CONTACT": UserNotMutualContact,
    "USER_NOT_PARTICIPANT": UserNotParticipant,
    "USER_PERMISSION_DENIED": UserPermissionDenied,
    "USER_PRIVACY_RESTRICTED": UserPrivacyRestricted,
    "USER_PUBLIC_MISSING": UserPublicMissing,
    "USER_RESTRICTED": UserRestricted,
    "USER_VOLUME_INVALID": UserVolumeInvalid,
    "VENUE_ID_INVALID": VenueIdInvalid,
    "VIDEO_CONTENT_TYPE_INVALID": VideoContentTypeInvalid,
    "VIDEO_DURATION_INVALID": VideoDurationInvalid,
    "VIDEO_FILE_INVALID": VideoFileInvalid,
    "VIDEO_PAUSE_FORBIDDEN": VideoPauseForbidden,
    "VIDEO_STOP_FORBIDDEN": VideoStopForbidden,
    "VIDEO_TITLE_EMPTY": VideoTitleEmpty,
    "VOICE_MESSAGES_FORBIDDEN": VoiceMessagesForbidden,
    "WALLPAPER_FILE_INVALID": WallpaperFileInvalid,
    "WALLPAPER_INVALID": WallpaperInvalid,
    "WALLPAPER_MIME_INVALID": WallpaperMimeInvalid,
    "WALLPAPER_NOT_FOUND": WallpaperNotFound,
    "WC_CONVERT_URL_INVALID": WcConvertUrlInvalid,
    "WEBAPP_REQ_ID_INVALID": WebappReqIdInvalid,
    "WEBAUTH_TOKEN_EXPIRED": WebauthTokenExpired,
    "WEBDOCUMENT_INVALID": WebdocumentInvalid,
    "WEBDOCUMENT_MIME_INVALID": WebdocumentMimeInvalid,
    "WEBDOCUMENT_SIZE_TOO_BIG": WebdocumentSizeTooBig,
    "WEBDOCUMENT_URL_EMPTY": WebdocumentUrlEmpty,
    "WEBDOCUMENT_URL_INVALID": WebdocumentUrlInvalid,
    "WEBPAGE_CURL_FAILED": WebpageCurlFailed,
    "WEBPAGE_MEDIA_EMPTY": WebpageMediaEmpty,
    "WEBPAGE_NOT_FOUND": WebpageNotFound,
    "WEBPAGE_URL_INVALID": WebpageUrlInvalid,
    "WEBPUSH_AUTH_INVALID": WebpushAuthInvalid,
    "WEBPUSH_KEY_INVALID": WebpushKeyInvalid,
    "WEBPUSH_TOKEN_INVALID": WebpushTokenInvalid,
    "YOUR_PRIVACY_RESTRICTED": YourPrivacyRestricted,
    "YOU_BLOCKED_USER": YouBlockedUser,
}

# The rest carry a number in the middle of the name, so they are matched
# rather than looked up. There are only a few dozen and nothing reaches
# them until a call has already failed, so a scan is fast enough.
BY_PATTERN: tuple[tuple[re.Pattern[str], type[RPCError]], ...] = (
    (re.compile(r"^2FA_CONFIRM_WAIT_(-?\d+)$"), TwoFactorConfirmWait),
    (re.compile(r"^ALLOW_PAYMENT_REQUIRED_(-?\d+)$"), AllowPaymentRequired),
    (re.compile(r"^AUTH_RESTART_(-?\d+)$"), AuthRestart),
    (re.compile(r"^EMAIL_UNCONFIRMED_(-?\d+)$"), EmailUnconfirmed),
    (re.compile(r"^FILE_MIGRATE_(-?\d+)$"), FileMigrate),
    (re.compile(r"^FILE_PART_(-?\d+)_MISSING$"), FilePartMissing),
    (re.compile(r"^FILE_REFERENCE_(-?\d+)_EMPTY$"), FileReferenceEmpty),
    (re.compile(r"^FILE_REFERENCE_(-?\d+)_EXPIRED$"), FileReferenceExpired),
    (re.compile(r"^FILE_REFERENCE_(-?\d+)_INVALID$"), FileReferenceInvalid),
    (re.compile(r"^FLOOD_PREMIUM_WAIT_(-?\d+)$"), FloodPremiumWait),
    (re.compile(r"^FLOOD_WAIT_(-?\d+)$"), FloodWait),
    (re.compile(r"^NETWORK_MIGRATE_(-?\d+)$"), NetworkMigrate),
    (re.compile(r"^PASSWORD_TOO_FRESH_(-?\d+)$"), PasswordTooFresh),
    (re.compile(r"^PHONE_MIGRATE_(-?\d+)$"), PhoneMigrate),
    (re.compile(r"^PREMIUM_SUB_ACTIVE_UNTIL_(-?\d+)$"), PremiumSubActiveUntil),
    (
        re.compile(r"^PREVIOUS_CHAT_IMPORT_ACTIVE_WAIT_(-?\d+)MIN$"),
        PreviousChatImportActiveWaitMin,
    ),
    (re.compile(r"^SESSION_TOO_FRESH_(-?\d+)$"), SessionTooFresh),
    (re.compile(r"^SLOWMODE_WAIT_(-?\d+)$"), SlowmodeWait),
    (re.compile(r"^STARGIFT_RESELL_TOO_EARLY_(-?\d+)$"), StargiftResellTooEarly),
    (re.compile(r"^STARGIFT_TRANSFER_TOO_EARLY_(-?\d+)$"), StargiftTransferTooEarly),
    (re.compile(r"^STATS_MIGRATE_(-?\d+)$"), StatsMigrate),
    (re.compile(r"^STORY_LIVE_ALREADY_(-?\d+)$"), StoryLiveAlready),
    (re.compile(r"^STORY_SEND_FLOOD_MONTHLY_(-?\d+)$"), StorySendFloodMonthly),
    (re.compile(r"^STORY_SEND_FLOOD_WEEKLY_(-?\d+)$"), StorySendFloodWeekly),
    (re.compile(r"^TAKEOUT_INIT_DELAY_(-?\d+)$"), TakeoutInitDelay),
    (re.compile(r"^USER_MIGRATE_(-?\d+)$"), UserMigrate),
)

__all__ = [
    "AboutTooLong",
    "AccessDenied",
    "AccessTokenExpired",
    "AccessTokenInvalid",
    "AdExpired",
    "AddressInvalid",
    "AdminIdInvalid",
    "AdminRankEmojiNotAllowed",
    "AdminRankInvalid",
    "AdminRightsEmpty",
    "AdminsTooMuch",
    "AiComposeTaskMissing",
    "AicomposeFloodPremium",
    "AicomposeTimeout",
    "AicomposeToneInvalid",
    "AicomposeToneTitleInvalid",
    "AlbumPhotosTooMany",
    "AllowPaymentRequired",
    "ApiGiftRestrictedUpdateApp",
    "ApiIdInvalid",
    "ApiIdPublishedFlood",
    "ArticleTitleEmpty",
    "AudioContentUrlEmpty",
    "AudioTitleEmpty",
    "AuthBytesInvalid",
    "AuthKeyDuplicated",
    "AuthKeyInvalid",
    "AuthKeyPermEmpty",
    "AuthKeyUnregistered",
    "AuthKeyUnsynchronized",
    "AuthRestart",
    "AuthTokenAlreadyAccepted",
    "AuthTokenException",
    "AuthTokenInvalidx",
    "AutoarchiveNotAvailable",
    "BalanceTooLow",
    "BankCardNumberInvalid",
    "BannedRightsInvalid",
    "BirthdayAlready",
    "BirthdayInvalid",
    "BoostNotModified",
    "BoostPeerInvalid",
    "BoostsEmpty",
    "BoostsRequired",
    "BotAccessForbidden",
    "BotAlreadyDisabled",
    "BotAppBotInvalid",
    "BotAppInvalid",
    "BotAppShortnameInvalid",
    "BotBusinessMissing",
    "BotChannelsNa",
    "BotCommandDescriptionInvalid",
    "BotCommandInvalid",
    "BotCreateLimitExceeded",
    "BotDomainInvalid",
    "BotFallbackUnsupported",
    "BotForumCreateForbidden",
    "BotGamesDisabled",
    "BotGroupsBlocked",
    "BotGuardNotSupported",
    "BotIdInvalid",
    "BotInlineDisabled",
    "BotInvalid",
    "BotInvoiceInvalid",
    "BotMethodInvalid",
    "BotNotConnectedYet",
    "BotOnesideNotAvail",
    "BotPaymentsDisabled",
    "BotResponseTimeout",
    "BotScoreNotModified",
    "BotVerifierForbidden",
    "BotWebviewDisabled",
    "BotsTooMuch",
    "BroadcastForbidden",
    "BroadcastIdInvalid",
    "BroadcastPublicVotersForbidden",
    "BroadcastRequired",
    "BusinessAddressActive",
    "BusinessConnectionInvalid",
    "BusinessConnectionNotAllowed",
    "BusinessPeerInvalid",
    "BusinessPeerUsageMissing",
    "BusinessRecipientsEmpty",
    "BusinessWorkHoursEmpty",
    "BusinessWorkHoursPeriodInvalid",
    "ButtonCopyTextInvalid",
    "ButtonDataInvalid",
    "ButtonIdInvalid",
    "ButtonInvalid",
    "ButtonPosInvalid",
    "ButtonTextInvalid",
    "ButtonTypeInvalid",
    "ButtonUrlInvalid",
    "ButtonUserInvalid",
    "ButtonUserPrivacyRestricted",
    "CallAlreadyAccepted",
    "CallAlreadyDeclined",
    "CallNotActive",
    "CallOccupyFailed",
    "CallPeerInvalid",
    "CallProtocolCompatLayerInvalid",
    "CallProtocolFlagsInvalid",
    "CallProtocolLayerInvalid",
    "CdnMethodInvalid",
    "CdnUploadTimeout",
    "ChannelForumMissing",
    "ChannelIdInvalid",
    "ChannelInvalid",
    "ChannelMonoforumUnsupported",
    "ChannelParicipantMissing",
    "ChannelPrivate",
    "ChannelPublicGroupNa",
    "ChannelTooBig",
    "ChannelTooLarge",
    "ChannelsAdminLocatedTooMuch",
    "ChannelsAdminPublicTooMuch",
    "ChannelsTooMuch",
    "ChargeAlreadyRefunded",
    "ChargeIdEmpty",
    "ChargeIdInvalid",
    "ChatAboutNotModified",
    "ChatAboutTooLong",
    "ChatActionForbidden",
    "ChatAdminInviteRequired",
    "ChatAdminRequired",
    "ChatDiscussionUnallowed",
    "ChatForbidden",
    "ChatForwardsRestricted",
    "ChatGuestSendForbidden",
    "ChatIdEmpty",
    "ChatIdGenerateFailed",
    "ChatIdInvalid",
    "ChatInvalid",
    "ChatInvitePermanent",
    "ChatLinkExists",
    "ChatMemberAddFailed",
    "ChatNotModified",
    "ChatPublicRequired",
    "ChatRestricted",
    "ChatRevokeDateUnsupported",
    "ChatSendAudiosForbidden",
    "ChatSendDocsForbidden",
    "ChatSendGameForbidden",
    "ChatSendGifsForbidden",
    "ChatSendInlineForbidden",
    "ChatSendMediaForbidden",
    "ChatSendPhotosForbidden",
    "ChatSendPlainForbidden",
    "ChatSendPollForbidden",
    "ChatSendRoundvideosForbidden",
    "ChatSendStickersForbidden",
    "ChatSendVideosForbidden",
    "ChatSendVoicesForbidden",
    "ChatSendWebpageForbidden",
    "ChatTitleEmpty",
    "ChatTooBig",
    "ChatTypeInvalid",
    "ChatWriteForbidden",
    "ChatlinkSlugEmpty",
    "ChatlinkSlugExpired",
    "ChatlinksTooMuch",
    "ChatlistExcludeInvalid",
    "ChatlistsTooMuch",
    "CodeEmpty",
    "CodeHashInvalid",
    "CodeInvalid",
    "CollectibleInvalid",
    "CollectibleNotFound",
    "CollectionIdInvalid",
    "ColorInvalid",
    "ConnectionApiIdInvalid",
    "ConnectionAppVersionEmpty",
    "ConnectionDeviceModelEmpty",
    "ConnectionIdInvalid",
    "ConnectionLangPackInvalid",
    "ConnectionLayerInvalid",
    "ConnectionNotInited",
    "ConnectionSystemEmpty",
    "ConnectionSystemLangCodeEmpty",
    "ContactAddMissing",
    "ContactIdInvalid",
    "ContactMissing",
    "ContactNameEmpty",
    "ContactReqMissing",
    "CreateCallFailed",
    "CredentialInvalid",
    "CurrencyTotalAmountInvalid",
    "CustomReactionsTooMany",
    "DataHashSizeInvalid",
    "DataInvalid",
    "DataJsonInvalid",
    "DataTooLong",
    "DateEmpty",
    "DcIdInvalid",
    "DhGAInvalid",
    "DocumentInvalid",
    "EditBotInviteForbidden",
    "EditMessageTempRestricted",
    "EffectChatInvalid",
    "EffectIdInvalid",
    "EmailHashExpired",
    "EmailInstallMissing",
    "EmailInvalid",
    "EmailNotAllowed",
    "EmailNotSetup",
    "EmailUnconfirmed",
    "EmailVerifyExpired",
    "EmojiInvalid",
    "EmojiMarkupInvalid",
    "EmojiNotModified",
    "EmoticonEmpty",
    "EmoticonInvalid",
    "EmoticonStickerpackMissing",
    "EncryptedMessageInvalid",
    "EncryptionAlreadyAccepted",
    "EncryptionAlreadyDeclined",
    "EncryptionDeclined",
    "EncryptionIdInvalid",
    "EntitiesTooLong",
    "EntityBoundsInvalid",
    "EntityDateFormatInvalid",
    "EntityDateInvalid",
    "EntityDateTooLong",
    "EntityMentionUserInvalid",
    "ErrorTextEmpty",
    "ExpireDateInvalid",
    "ExpiresAtInvalid",
    "ExportCardInvalid",
    "ExtendedMediaAmountInvalid",
    "ExtendedMediaEmpty",
    "ExtendedMediaInvalid",
    "ExtendedMediaPeerInvalid",
    "ExternalUrlInvalid",
    "FileContentTypeInvalid",
    "FileEmtpy",
    "FileIdInvalid",
    "FilePartEmpty",
    "FilePartInvalid",
    "FilePartLengthInvalid",
    "FilePartMissing",
    "FilePartSizeChanged",
    "FilePartSizeInvalid",
    "FilePartTooBig",
    "FilePartTooSmall",
    "FilePartsInvalid",
    "FileReferenceEmpty",
    "FileReferenceExpired",
    "FileReferenceInvalid",
    "FileTitleEmpty",
    "FileTokenInvalid",
    "FilerefUpgradeNeeded",
    "FilterIdInvalid",
    "FilterIncludeEmpty",
    "FilterNotSupported",
    "FilterTitleEmpty",
    "FirstnameInvalid",
    "FloodPremiumWait",
    "FolderIdEmpty",
    "FolderIdInvalid",
    "FormExpired",
    "FormIdEmpty",
    "FormSubmitDuplicate",
    "FormUnsupported",
    "ForumEnabled",
    "FreshChangeAdminsForbidden",
    "FreshChangePhoneForbidden",
    "FreshResetAuthorisationForbidden",
    "FromMessageBotDisabled",
    "FromPeerInvalid",
    "FrozenMethodInvalid",
    "FrozenParticipantMissing",
    "GameBotInvalid",
    "GeneralModifyIconForbidden",
    "GeoPointInvalid",
    "GifContentTypeInvalid",
    "GifIdInvalid",
    "GiftMonthsInvalid",
    "GiftSlugExpired",
    "GiftSlugInvalid",
    "GiftStarsInvalid",
    "GraphExpiredReload",
    "GraphInvalidReload",
    "GraphOutdatedReload",
    "GroupcallAlreadyDiscarded",
    "GroupcallAlreadyStarted",
    "GroupcallChangeForbidden",
    "GroupcallForbidden",
    "GroupcallInvalid",
    "GroupcallJoinMissing",
    "GroupcallNotModified",
    "GroupcallSsrcDuplicateMuch",
    "GroupedMediaInvalid",
    "HashInvalid",
    "HashSizeInvalid",
    "HashtagInvalid",
    "HideRequesterMissing",
    "IdExpired",
    "IdInvalid",
    "ImageProcessFailed",
    "ImportFileInvalid",
    "ImportFormatDateInvalid",
    "ImportFormatUnrecognized",
    "ImportIdInvalid",
    "ImportTokenInvalid",
    "InlineBotRequired",
    "InlineResultExpired",
    "InputChatlistInvalid",
    "InputConstructorInvalid",
    "InputFetchError",
    "InputFetchFail",
    "InputFileInvalid",
    "InputFilterInvalid",
    "InputLayerInvalid",
    "InputMethodInvalid",
    "InputPeersEmpty",
    "InputPurposeInvalid",
    "InputRequestTooLong",
    "InputStarsAmountInvalid",
    "InputStarsNanosInvalid",
    "InputTextEmpty",
    "InputTextTooLong",
    "InputUserDeactivated",
    "InviteForbiddenWithJoinas",
    "InviteHashEmpty",
    "InviteHashExpired",
    "InviteHashInvalid",
    "InviteRequestSent",
    "InviteRevokedMissing",
    "InviteSlugEmpty",
    "InviteSlugExpired",
    "InviteSlugInvalid",
    "InvitesTooMuch",
    "InvoiceInvalid",
    "InvoicePayloadInvalid",
    "JoinAsPeerInvalid",
    "LangCodeInvalid",
    "LangCodeNotSupported",
    "LangPackInvalid",
    "LanguageInvalid",
    "LastnameInvalid",
    "LimitInvalid",
    "LimitPerPostInvalid",
    "LinkNotModified",
    "LocationInvalid",
    "ManagerInvalid",
    "ManagerPermissionMissing",
    "MaxDateInvalid",
    "MaxIdInvalid",
    "MaxQtsInvalid",
    "Md5ChecksumInvalid",
    "MediaAlreadyPaid",
    "MediaCaptionTooLong",
    "MediaEmpty",
    "MediaFileInvalid",
    "MediaGroupedInvalid",
    "MediaInvalid",
    "MediaNewInvalid",
    "MediaPrevInvalid",
    "MediaTtlInvalid",
    "MediaTypeInvalid",
    "MediaVideoStoryMissing",
    "MegagroupGeoRequired",
    "MegagroupIdInvalid",
    "MegagroupPrehistoryHidden",
    "MegagroupRequired",
    "MessageAuthorRequired",
    "MessageDeleteForbidden",
    "MessageEditTimeExpired",
    "MessageEmpty",
    "MessageIdInvalid",
    "MessageIdsEmpty",
    "MessageNotModified",
    "MessageNotReadYet",
    "MessagePollClosed",
    "MessageRequired",
    "MessageTooLong",
    "MessageTooOld",
    "MethodInvalid",
    "MinDateInvalid",
    "MonthInvalid",
    "MsgIdInvalid",
    "MsgTooOld",
    "MsgVoiceMissing",
    "MsgVoiceTooLong",
    "MsgWaitFailed",
    "MsgWaitTimeout",
    "MultiMediaTooLong",
    "NameInvalid",
    "NeedActionMissing",
    "NewSaltInvalid",
    "NewSettingsEmpty",
    "NewSettingsInvalid",
    "NextOffsetInvalid",
    "NoPaymentNeeded",
    "NogeneralHideForbidden",
    "NotEligible",
    "NotJoined",
    "OauthRequestInvalid",
    "OffsetInvalid",
    "OffsetPeerIdInvalid",
    "OptionInvalid",
    "OptionsTooMuch",
    "OrderInvalid",
    "PackShortNameInvalid",
    "PackShortNameOccupied",
    "PackTitleInvalid",
    "PackTypeInvalid",
    "ParentPeerInvalid",
    "ParticipantIdInvalid",
    "ParticipantJoinMissing",
    "ParticipantVersionOutdated",
    "ParticipantsTooFew",
    "PasskeyOriginMismatch",
    "PasswordEmpty",
    "PasswordMissing",
    "PasswordRecoveryExpired",
    "PasswordRecoveryNa",
    "PasswordRequired",
    "PasswordTooFresh",
    "PaymentCredentialsInvalid",
    "PaymentProviderInvalid",
    "PaymentRequired",
    "PaymentUnsupported",
    "PeerFlood",
    "PeerHistoryEmpty",
    "PeerIdInvalid",
    "PeerIdNotSupported",
    "PeerTypesInvalid",
    "PeersListEmpty",
    "PersistentTimestampEmpty",
    "PersistentTimestampInvalid",
    "PersistentTimestampOutdated",
    "PhoneCodeEmpty",
    "PhoneCodeHashEmpty",
    "PhoneHashExpired",
    "PhoneNotOccupied",
    "PhoneNumberAppSignupForbidden",
    "PhoneNumberBanned",
    "PhoneNumberFlood",
    "PhoneNumberOccupied",
    "PhoneNumberUnoccupied",
    "PhonePasswordFlood",
    "PhonePasswordProtected",
    "PhotoContentTypeInvalid",
    "PhotoContentUrlEmpty",
    "PhotoCropFileMissing",
    "PhotoCropSizeSmall",
    "PhotoExtInvalid",
    "PhotoFileMissing",
    "PhotoIdInvalid",
    "PhotoInvalid",
    "PhotoInvalidDimensions",
    "PhotoSaveFileInvalid",
    "PhotoThumbUrlEmpty",
    "PinRestricted",
    "PinnedDialogsTooMuch",
    "PinnedTooMuch",
    "PinnedTopicNotModified",
    "PollAnswerInvalid",
    "PollAnswersInvalid",
    "PollCountryRestricted",
    "PollMemberRestricted",
    "PollOptionDuplicate",
    "PollOptionInvalid",
    "PollQuestionInvalid",
    "PollVoteRequired",
    "PrecheckoutFailed",
    "PremiumAccountRequired",
    "PremiumCurrentlyUnavailable",
    "PremiumPurposeInvalid",
    "PremiumSubActiveUntil",
    "PreviousChatImportActiveWaitMin",
    "PricingChatInvalid",
    "PrivacyKeyInvalid",
    "PrivacyPremiumRequired",
    "PrivacyTooLong",
    "PrivacyValueInvalid",
    "PublicBroadcastExpected",
    "PublicChannelMissing",
    "PublicKeyInvalid",
    "PublicKeyRequired",
    "PurposeInvalid",
    "QueryIdEmpty",
    "QueryIdInvalid",
    "QueryTooShort",
    "QuickRepliesBotNotAllowed",
    "QuickRepliesTooMuch",
    "QuizAnswerMissing",
    "QuizCorrectAnswerInvalid",
    "QuizCorrectAnswersEmpty",
    "QuizCorrectAnswersTooMuch",
    "QuizMultipleInvalid",
    "QuoteTextInvalid",
    "RaiseHandForbidden",
    "RandomIdDuplicate",
    "RandomIdEmpty",
    "RandomIdExpired",
    "RandomIdInvalid",
    "RandomLengthInvalid",
    "RangesInvalid",
    "ReactionEmpty",
    "ReactionInvalid",
    "ReactionsCountInvalid",
    "ReactionsTooMany",
    "ReceiptEmpty",
    "ReplyMarkupBuyEmpty",
    "ReplyMarkupGameEmpty",
    "ReplyMarkupInvalid",
    "ReplyMarkupTooLong",
    "ReplyMessageIdInvalid",
    "ReplyMessagesTooMuch",
    "ReplyToInvalid",
    "ReplyToMonoforumPeerInvalid",
    "ReplyToUserInvalid",
    "RequestMsgExpired",
    "RequestTokenInvalid",
    "ResellStarsTooFew",
    "ResellStarsTooMuch",
    "ResetRequestMissing",
    "ResultIdDuplicate",
    "ResultIdEmpty",
    "ResultIdInvalid",
    "ResultTypeInvalid",
    "ResultsTooMuch",
    "RevoteNotAllowed",
    "RightForbidden",
    "RightsNotModified",
    "RingtoneInvalid",
    "RingtoneMimeInvalid",
    "RsaDecryptFailed",
    "SavedIdEmpty",
    "ScheduleBotNotAllowed",
    "ScheduleDateInvalid",
    "ScheduleDateTooLate",
    "ScheduleStatusPrivate",
    "ScheduleTooMuch",
    "ScoreInvalid",
    "SearchQueryEmpty",
    "SearchWithLinkNotSupported",
    "SecondsInvalid",
    "SecureSecretRequired",
    "SelfDeleteRestricted",
    "SendAsPeerInvalid",
    "SendCodeUnavailable",
    "SendMediaInvalid",
    "SendMessageGameInvalid",
    "SendMessageMediaInvalid",
    "SendMessageTypeInvalid",
    "SensitiveChangeForbidden",
    "SessionExpired",
    "SessionRevoked",
    "SessionTooFresh",
    "SettingsInvalid",
    "Sha256HashInvalid",
    "ShortNameInvalid",
    "ShortNameOccupied",
    "ShortcutInvalid",
    "SignInFailed",
    "SlotsEmpty",
    "SlowmodeMultiMsgsDisabled",
    "SlugInvalid",
    "SmsCodeCreateFailed",
    "SmsjobIdInvalid",
    "SrpAInvalid",
    "SrpIdInvalid",
    "SrpPasswordChanged",
    "StargiftAlreadyConverted",
    "StargiftAlreadyRefunded",
    "StargiftAlreadyUpgraded",
    "StargiftAttributeInvalid",
    "StargiftExportInProgress",
    "StargiftInvalid",
    "StargiftMessageInvalid",
    "StargiftNotFound",
    "StargiftNotOwner",
    "StargiftNotUnique",
    "StargiftObjectInvalid",
    "StargiftOfferInvalid",
    "StargiftOfferNotAllowed",
    "StargiftOwnerInvalid",
    "StargiftPeerInvalid",
    "StargiftResellCurrencyNotAllowed",
    "StargiftResellTooEarly",
    "StargiftSlugInvalid",
    "StargiftTransferTooEarly",
    "StargiftUpgradeUnavailable",
    "StargiftUsageLimited",
    "StargiftUserUsageLimited",
    "StarrefAwaitingEnd",
    "StarrefExpired",
    "StarrefHashRevoked",
    "StarrefPermilleInvalid",
    "StarrefPermilleTooLow",
    "StarsAmountInvalid",
    "StarsFormAmountMismatch",
    "StarsInvoiceInvalid",
    "StarsPaymentRequired",
    "StartParamEmpty",
    "StartParamInvalid",
    "StartParamTooLong",
    "StickerDocumentInvalid",
    "StickerEmojiInvalid",
    "StickerFileInvalid",
    "StickerGifDimensions",
    "StickerIdInvalid",
    "StickerInvalid",
    "StickerMimeInvalid",
    "StickerPngDimensions",
    "StickerPngNopng",
    "StickerTgsNodoc",
    "StickerTgsNotgs",
    "StickerThumbPngNopng",
    "StickerThumbTgsNotgs",
    "StickerVideoBig",
    "StickerVideoNodoc",
    "StickerVideoNowebm",
    "StickerpackStickersTooMuch",
    "StickersEmpty",
    "StickersTooMuch",
    "StickersetInvalid",
    "StickersetNotModified",
    "StickersetOwnerAnonymous",
    "StoriesNeverCreated",
    "StoriesTooMuch",
    "StoryIdEmpty",
    "StoryIdInvalid",
    "StoryLiveAlready",
    "StoryNotModified",
    "StoryPeriodInvalid",
    "StorySendFloodMonthly",
    "StorySendFloodWeekly",
    "SubscriptionExportMissing",
    "SubscriptionIdInvalid",
    "SubscriptionPeriodInvalid",
    "SuggestedPostAmountInvalid",
    "SuggestedPostPeerInvalid",
    "SwitchPmTextEmpty",
    "SwitchWebviewUrlInvalid",
    "TakeoutInvalid",
    "TakeoutRequired",
    "TaskAlreadyExists",
    "TempAuthKeyAlreadyBound",
    "TempAuthKeyEmpty",
    "TermsUrlInvalid",
    "TextdraftPeerInvalid",
    "ThemeFileInvalid",
    "ThemeFormatInvalid",
    "ThemeInvalid",
    "ThemeMimeInvalid",
    "ThemeParamsInvalid",
    "ThemeSlugInvalid",
    "ThemeTitleInvalid",
    "TimezoneInvalid",
    "TitleInvalid",
    "TmpPasswordDisabled",
    "TmpPasswordInvalid",
    "ToIdInvalid",
    "ToLangInvalid",
    "TodoItemDuplicate",
    "TodoItemsEmpty",
    "TodoItemsTooMuch",
    "TodoNotModified",
    "TokenEmpty",
    "TokenInvalid",
    "TokenTypeInvalid",
    "TopicCloseSeparately",
    "TopicClosed",
    "TopicDeleted",
    "TopicHideSeparately",
    "TopicIdInvalid",
    "TopicNotModified",
    "TopicTitleEmpty",
    "TopicsEmpty",
    "TransactionIdInvalid",
    "TranscriptionFailed",
    "TranslateReqFailed",
    "TranslateReqQuotaExceeded",
    "TranslationTimeout",
    "TranslationsDisabled",
    "TtlDaysInvalid",
    "TtlMediaInvalid",
    "TtlPeriodInvalid",
    "TwoFactorConfirmWait",
    "TypesEmpty",
    "Unsupported",
    "UntilDateInvalid",
    "UpdateAppToLogin",
    "UrlExpired",
    "UrlInvalid",
    "UsageLimitInvalid",
    "UserAdminInvalid",
    "UserAlreadyInvited",
    "UserAlreadyParticipant",
    "UserBannedInChannel",
    "UserBlocked",
    "UserBot",
    "UserBotInvalid",
    "UserBotRequired",
    "UserBotToBotDisabled",
    "UserChannelsTooMuch",
    "UserCreator",
    "UserDeactivated",
    "UserDeactivatedBan",
    "UserDeleted",
    "UserDisallowedStargifts",
    "UserGiftUnavailable",
    "UserIdInvalid",
    "UserInvalid",
    "UserIsBlocked",
    "UserIsBot",
    "UserKicked",
    "UserNotMutualContact",
    "UserNotParticipant",
    "UserPermissionDenied",
    "UserPrivacyRestricted",
    "UserPublicMissing",
    "UserRestricted",
    "UserVolumeInvalid",
    "UsernameInvalid",
    "UsernameNotModified",
    "UsernameNotOccupied",
    "UsernameOccupied",
    "UsernamePurchaseAvailable",
    "UsernameSuffixMissing",
    "UsernamesActiveTooMuch",
    "UserpicPrivacyRequired",
    "UserpicUploadRequired",
    "UsersTooFew",
    "UsersTooMuch",
    "VenueIdInvalid",
    "VideoContentTypeInvalid",
    "VideoDurationInvalid",
    "VideoFileInvalid",
    "VideoPauseForbidden",
    "VideoStopForbidden",
    "VideoTitleEmpty",
    "VoiceMessagesForbidden",
    "WallpaperFileInvalid",
    "WallpaperInvalid",
    "WallpaperMimeInvalid",
    "WallpaperNotFound",
    "WcConvertUrlInvalid",
    "WebappReqIdInvalid",
    "WebauthTokenExpired",
    "WebdocumentInvalid",
    "WebdocumentMimeInvalid",
    "WebdocumentSizeTooBig",
    "WebdocumentUrlEmpty",
    "WebdocumentUrlInvalid",
    "WebpageCurlFailed",
    "WebpageMediaEmpty",
    "WebpageNotFound",
    "WebpageUrlInvalid",
    "WebpushAuthInvalid",
    "WebpushKeyInvalid",
    "WebpushTokenInvalid",
    "YouBlockedUser",
    "YourPrivacyRestricted",
]
