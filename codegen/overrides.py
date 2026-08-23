"""The manual adjustments to code generation.

Everything here is a deliberate exception, kept in one file so the generator
itself stays a plain reading of the schema. An entry that stops being needed
after a schema refresh should be deleted rather than left to rot.
"""

from __future__ import annotations

# Definitions whose declared constructor id does not reproduce from hashing
# their declaration text. All three are MTProxy shapes that reach a client
# through a DNS or HTTP blob rather than over MTProto, and Telegram appears to
# have computed their ids from an older wording. The declared id is authoritative
# either way, so this set only exists to keep the parser's self-check honest: a
# new name appearing here after a refresh deserves a look before it is added.
ID_EXCEPTIONS = frozenset(
    {
        "ipPortSecret",
        "accessPointRule",
        "help.configSimple",
    }
)

# Definitions to leave out of the generated package entirely. The fake-TLS
# blocks describe how to dress up a connection for MTProxy, are not MTProto
# objects, and are the only definitions in either schema with no declared id.
EXCLUDED = frozenset(
    {
        "tlsClientHello",
        "tlsBlockString",
        "tlsBlockRandom",
        "tlsBlockZero",
        "tlsBlockDomain",
        "tlsBlockGrease",
        "tlsBlockPublicKey",
        "tlsBlockScope",
        "tlsBlockPermutation",
        "tlsBlockM",
        "tlsBlockE",
        "tlsBlockPadding",
    }
)

# Field names to spell differently in Python. A name that collides with a
# keyword is mangled automatically with a trailing underscore; this is for
# cases where a better name exists.
RENAMED_FIELDS: dict[str, str] = {}

# mtproto.tl predates the bytes spelling, so it says string for binary blobs:
# resPQ.pq is the product of two primes, not text. Decoding one of those as
# utf-8 would raise on the first byte that is not valid, so in that schema
# string means bytes unless the field really is text. Naming the text is the
# safe direction to be explicit in: guessing bytes costs a caller an encode,
# guessing text costs them a crash.
MTPROTO_TEXT_FIELDS = frozenset(
    {
        "rpc_error.error_message",
    }
)

# The same correction for api.tl, which spells binary bytes and needs no
# blanket rule. An entry here is a field that turned out to be binary anyway.
BYTES_FIELDS: frozenset[str] = frozenset()

# Errors that already exist by hand in errors/rpc.py, mapped to the class that
# stands for them. Those are the ones carrying behavior a table cannot express:
# seconds to wait, a datacenter to go to, a second factor to ask for. The
# generator imports these rather than emitting them, so there is exactly one
# class per error however it came to exist.
ERROR_HAND_WRITTEN: dict[str, str] = {
    "FLOOD_WAIT_%d": "FloodWait",
    "SLOWMODE_WAIT_%d": "SlowmodeWait",
    "TAKEOUT_INIT_DELAY_%d": "TakeoutInitDelay",
    "PHONE_MIGRATE_%d": "PhoneMigrate",
    "NETWORK_MIGRATE_%d": "NetworkMigrate",
    "USER_MIGRATE_%d": "UserMigrate",
    "FILE_MIGRATE_%d": "FileMigrate",
    "STATS_MIGRATE_%d": "StatsMigrate",
    "SESSION_PASSWORD_NEEDED": "SessionPasswordNeeded",
    "PHONE_CODE_INVALID": "PhoneCodeInvalid",
    "PHONE_CODE_EXPIRED": "PhoneCodeExpired",
    "PHONE_NUMBER_INVALID": "PhoneNumberInvalid",
    "PASSWORD_HASH_INVALID": "PasswordHashInvalid",
    "AUTH_TOKEN_EXPIRED": "AuthTokenExpired",
    "AUTH_TOKEN_INVALID": "AuthTokenInvalid",
    "Timeout": "Timeout",
}

# Errors to spell differently. Telegram's names are shouted words joined by
# underscores, which turns into a class name on its own; this is for the ones
# that do not, and a name starting with a digit is not a Python name at all.
ERROR_CLASS_NAMES: dict[str, str] = {
    "2FA_CONFIRM_WAIT_%d": "TwoFactorConfirmWait",
}

# Errors to hang off a different class than their status code implies. The
# status code is the usual answer, so an entry here is a case where the name
# says more than the number does: a premium flood is still a flood, and code
# that waits on one wants to catch both the same way.
ERROR_BASES: dict[str, str] = {
    "FLOOD_PREMIUM_WAIT_%d": "FloodWait",
}
