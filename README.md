# Summoner Agent Library

This repository is based on `starter-template`, but instead of providing integration tooling intended for merging with Summoner's core SDK, it offers example agents for the Summoner protocol.

## Using `setup()` in Your Agents

Some agent examples define a `setup()` coroutine, which is awaited before the agent starts. This section explains why this pattern exists and when it is necessary.

### Core Principle: Summoner Agents Use an Async Event Loop

Launching an agent with:

```python
myagent.run(host="127.0.0.1", port=8888)
```

creates and manages an `asyncio` event loop internally. Any asynchronous components -- such as message handling, database connections, or task scheduling -- must be created within this loop.

Asynchronous tools like `asyncio.Queue` or `aiosqlite` are bound to the event loop that created them. If they are created outside the Summoner loop (e.g. at the top level of your script), you may encounter errors such as:

```sh
RuntimeError: Task ... got Future ... attached to a different loop
```

### When to Use a `setup()` Coroutine

Use `setup()` when asynchronous initialization is required, such as:

* Initializing an `asyncio.Queue` for buffering messages
* Connecting to an async database (e.g. `aiosqlite`)
* Creating background tasks using `loop.create_task`
* Performing other async setup tasks

Note: `asyncio.Lock` can be safely created before `myagent.run()`, without requiring `setup()`.

Example pattern:

```python
message_buffer = None

async def setup():
    global message_buffer
    message_buffer = asyncio.Queue()

    @myagent.receive(route="...")
    async def receive(msg):
        await message_buffer.put(msg)

    @myagent.send(route="...")
    async def send():
        return await message_buffer.get()

myagent.loop.run_until_complete(setup())
myagent.run(host="127.0.0.1", port=8888)
```

This ensures all async objects are bound to the correct event loop.

### When `setup()` Is Not Needed

If your agent only defines handlers using `@myagent.receive` and `@myagent.send`, and all logic is local to those handlers, `setup()` is unnecessary.

Example:

```python
myagent = SummonerClient(name="SimpleAgent")

@myagent.receive(route="ping")
async def handle_ping(msg):
    print("Got:", msg)

@myagent.send(route="pong")
async def respond():
    return "pong"

myagent.run(host="127.0.0.1", port=8888)
```

This approach is suitable for simple agents with no shared state or external dependencies.

### Examples That Use `setup()`

Relevant examples in this repository:

* `a-reporter-*`: uses `setup()` to initialize a message queue for ordering and batching
* `a-seller-*` and `a-buyer-*`: use `setup()` for shared state, `aiosqlite` initialization, and background negotiation logic

These examples show how `setup()` provides a structured way to initialize asynchronous or stateful components before the agent starts.
