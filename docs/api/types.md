# Types

The hand-written wrappers a handler actually receives. Each keeps the TL object it was
built from on `.raw`, so nothing is lost by taking the friendly one.

::: sunnygram.types.message.Message
::: sunnygram.types.callback.CallbackQuery
::: sunnygram.types.user.User
::: sunnygram.types.chat.Chat
::: sunnygram.types.dialog.Dialog
::: sunnygram.types.topic.Topic

## Inline mode

Both halves of it: the query that arrived, the result that goes back, and what was picked.
See [Inline mode](../inline.md).

::: sunnygram.types.inline.InlineQuery
::: sunnygram.types.inline.InlineResult
::: sunnygram.types.inline.ChosenResult

## Members

::: sunnygram.types.member.Member
::: sunnygram.types.member.MemberStatus
::: sunnygram.types.member.MemberUpdate
::: sunnygram.types.join.JoinRequest

## Reactions and polls

::: sunnygram.types.reaction.ReactionUpdate
::: sunnygram.types.poll.Poll
::: sunnygram.types.poll.PollAnswer
::: sunnygram.types.poll.PollVote

## The small events

Records with nothing to do about them, which is why they share a file.

::: sunnygram.types.events.DeletedMessages
::: sunnygram.types.events.Status
::: sunnygram.types.events.Typing
::: sunnygram.types.events.Blocked
::: sunnygram.types.events.Stopped

## Buttons

A keyboard is a shape with no call attached, which is why it is here, not among the
methods. See [Buttons](../buttons.md).

::: sunnygram.types.buttons.Button
::: sunnygram.types.buttons.keyboard
::: sunnygram.types.buttons.force_reply
::: sunnygram.types.buttons.remove_keyboard
::: sunnygram.types.buttons.buttons_of

## Rights

Both of these say what someone may do, in the readable direction: `True` is allowed. See
[Running a chat](../admin.md) for why that is worth stating.

::: sunnygram.types.rights.AdminRights
::: sunnygram.types.rights.Permissions

## Updates

::: sunnygram.updates.manager.Event
::: sunnygram.updates.manager.UpdateManager
::: sunnygram.recent.RecentMessages

## Text

::: sunnygram.parser.parse
::: sunnygram.parser.unparse
