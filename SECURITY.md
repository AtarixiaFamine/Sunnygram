# Security Policy

## Supported Versions

Sunnygram is pre-1.0. Security fixes are released against the latest version only.

| Version    | Supported |
| ---------- | --------- |
| latest 0.x | ✅        |
| older      | ❌        |

## Reporting a Vulnerability

Please **do not open a public issue** for security vulnerabilities.

Report privately through GitHub's [private vulnerability reporting](https://github.com/AtarixiaFamine/Sunnygram/security/advisories/new)
(the repository's **Security → Report a vulnerability** button). Include:

- a description of the issue and its impact,
- steps to reproduce, with a minimal proof of concept if you have one,
- the affected version(s).

Expect an acknowledgement within a few days. Once confirmed, I will prepare and release a
fix and credit you in the advisory unless you would rather stay anonymous. Please allow a
reasonable window before public disclosure.

## What is in scope

Sunnygram implements MTProto itself rather than wrapping a library that does, so the
protocol is this project's responsibility and not somebody else's. Things worth reporting:

- Anything that would let a party in the middle read, forge, or replay messages: a flaw in
  the authorization-key handshake, the message-key derivation, AES-IGE, or the checks on
  incoming messages (session id, sequence parity, the clock window, the replay history).
- A parameter check that Telegram's
  [security guidelines](https://core.telegram.org/mtproto/security_guidelines) require and
  Sunnygram skips or gets wrong.
- Server data that can make the TL deserializer allocate without bound, loop, or read out
  of range. Server data is untrusted here by design (rule S3).
- A path where an auth key or session material reaches a log, a `repr`, or an exception
  message (rule S2).
- Anything in the SRP implementation that would leak a password or accept a wrong one.

## What is not

**Your session file is the account.** Anyone holding one is signed in as you, with no
password, no code, and nothing you would notice. The same goes for a string session,
which is that in one line of plain text. Keeping them out of source control, logs, images
and screenshots is your side of the bargain, and a leak of your own is outside this
project's scope.

Your `api_id` and `api_hash` identify your application. They are not as dangerous as a
session, and they are still not something to publish.


