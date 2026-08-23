# Client

The one object most programs hold. See [Quickstart](../quickstart.md) for what to do with
it and [Handling updates](../updates.md) for the handler side.

::: sunnygram.client.Client

## Dispatcher

::: sunnygram.dispatcher.Dispatcher
::: sunnygram.dispatcher.Handler
::: sunnygram.dispatcher.AlbumCollector
::: sunnygram.dispatcher.StopPropagation

## Invoker

The layer below the client: one session, a connection per datacenter, and the retries that
make a call survive a dropped socket.

::: sunnygram.network.invoker.Invoker
::: sunnygram.network.ClientInfo





## Pacing

::: sunnygram.network.limiter.RateLimiter
::: sunnygram.network.limiter.TokenBucket

## Getting out

::: sunnygram.transport.proxy.Proxy
::: sunnygram.transport.obfuscation.Obfuscation
