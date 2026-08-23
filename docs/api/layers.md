# Layers

Everything under the client, for a program that wants one piece of it. `ARCHITECTURE.md`
in the repository explains how they fit together; this is the reference for reaching them
directly.

## Sessions

::: sunnygram.storage.base.Storage
::: sunnygram.storage.base.SessionState
::: sunnygram.storage.sqlite.SQLiteStorage
::: sunnygram.storage.string.StringStorage
::: sunnygram.storage.memory.MemoryStorage
::: sunnygram.storage.string.encode_session
::: sunnygram.storage.string.decode_session

## Logging in

::: sunnygram.auth.login.log_in
::: sunnygram.auth.login.send_code
::: sunnygram.auth.login.sign_in
::: sunnygram.auth.login.check_password
::: sunnygram.auth.login.sign_in_qr
::: sunnygram.auth.login.sign_in_bot
::: sunnygram.auth.login.resend_code
::: sunnygram.auth.login.log_out
::: sunnygram.auth.login.get_me
::: sunnygram.auth.login.SentCode
::: sunnygram.auth.login.LoginToken

## Peers

::: sunnygram.peers.resolver.resolve
::: sunnygram.peers.resolver.resolve_username
::: sunnygram.peers.resolver.resolve_phone
::: sunnygram.peers.resolver.mark_id
::: sunnygram.peers.resolver.mark_peer
::: sunnygram.peers.resolver.unmark_id

## Files

::: sunnygram.files.download.download_file
::: sunnygram.files.upload.upload_file
::: sunnygram.files.cdn.CdnSession
::: sunnygram.files.ref.file_ref
::: sunnygram.files.ref.decode_ref
::: sunnygram.files.ref.parse_ref
::: sunnygram.files.ref.FileRef

## Topics

::: sunnygram.methods.forum.iter_topic_pages
::: sunnygram.methods.forum.topics_by_id
::: sunnygram.methods.forum.create_topic
::: sunnygram.methods.forum.edit_topic
::: sunnygram.methods.forum.pin_topic
::: sunnygram.methods.forum.reorder_topics
::: sunnygram.methods.forum.delete_topic
::: sunnygram.methods.forum.toggle_forum
::: sunnygram.methods.messages.reply_header

## Crypto

Written from scratch and validated against official vectors. Not something to call
directly, and worth reading before trusting.

::: sunnygram.crypto.describe

## The wire

::: sunnygram.network.connection.Connection
::: sunnygram.session.session.Session
::: sunnygram.transport.tcp.TCPTransport
::: sunnygram.tl.core.TLObject
