# Errors

The roots. Every error Telegram documents is also reachable by name from
`sunnygram.errors`, generated from Telegram's own table with the published explanation as
its docstring, and not listed here because there are 780 of them. See
[Errors](../errors.md) for the shape of the tree and how to catch things.

## Refusals

::: sunnygram.errors.rpc.RPCError
::: sunnygram.errors.rpc.BadRequest
::: sunnygram.errors.rpc.Unauthorized
::: sunnygram.errors.rpc.Forbidden
::: sunnygram.errors.rpc.NotFound
::: sunnygram.errors.rpc.NotAcceptable
::: sunnygram.errors.rpc.InternalError
::: sunnygram.errors.rpc.Timeout

## Waiting

::: sunnygram.errors.rpc.Flood
::: sunnygram.errors.rpc.FloodWait
::: sunnygram.errors.rpc.SlowmodeWait
::: sunnygram.errors.rpc.TakeoutInitDelay

## Migrations

::: sunnygram.errors.rpc.Migrate

## Signing in

::: sunnygram.errors.rpc.SessionPasswordNeeded
::: sunnygram.errors.rpc.PhoneCodeInvalid
::: sunnygram.errors.rpc.PhoneCodeExpired
::: sunnygram.errors.rpc.PhoneNumberInvalid
::: sunnygram.errors.rpc.PasswordHashInvalid
::: sunnygram.errors.rpc.AuthTokenExpired
::: sunnygram.errors.rpc.AuthTokenInvalid

## Everything else

::: sunnygram.errors.base.SunnygramError
::: sunnygram.errors.base.TLError
::: sunnygram.errors.base.TransportError
::: sunnygram.errors.base.SecurityError
::: sunnygram.errors.base.PeerNotFound
::: sunnygram.errors.base.FileTooLarge

## Building one

::: sunnygram.errors.rpc.rpc_error
