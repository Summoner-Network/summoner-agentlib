# Summoner Agent Library

This repository is based on the `starter-template`, but unlike SDK components, it doesn’t include any integration tooling. Its sole purpose is to provide example agents for the Summoner protocol.


##  Using `setup()` in your agents

Some agent examples in this repository include a function called `setup()`, which is awaited before the agent starts. If you're new to asyncio or to the Summoner protocol, it may not be immediately clear why this pattern is used or when it’s necessary.

This section explains the role of `setup()` and helps you understand when it’s needed  --  and when it isn’t.

### Core principle: Summoner agents run on an async event loop

When you launch an agent using:

```python
myagent.run(host="127.0.0.1", port=8888)
```

Summoner internally creates and manages an asyncio event loop. Any asynchronous component you use  --  such as receiving and sending messages, connecting to databases, or creating locks and queues  --  must be attached to this event loop.

This is important because many common async tools in Python (like `asyncio.Queue` or `aiosqlite`) are bound to the specific loop they were created in. If they're created outside that loop  --  for example, at the top of your script  --  you may encounter errors like:

```sh
RuntimeError: Task ... got Future ... attached to a different loop
```


### When to use a `setup()` coroutine

You should use a setup coroutine when you need to:

* Initialize an `asyncio.Queue` (e.g. for message buffering)
* Connect to an async database like `aiosqlite`
* Start background tasks using `loop.create_task`
* Perform any other asynchronous initialization before the agent starts

Note: You do not need setup() just to create an `asyncio.Lock`. Locks can safely be created at the top level before `myagent.run()`.

Here’s the typical pattern:

```python
message_buffer = None  # defined globally but initialized later

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

This ensures that message\_buffer is created inside the same event loop that the agent will use  --  avoiding loop mismatches and shutdown issues.


### When you don't need `setup()`

If your agent only defines routes (e.g. using @myagent.receive or @myagent.send) and all your logic is local to those handlers, you don’t need a setup coroutine. You can define everything inline and run the agent directly.

Example:

```python
myagent = SummonerClient(name="SimpleAgent", option="python")

@myagent.receive(route="ping")
async def handle_ping(msg):
    print("Got:", msg)

@myagent.send(route="pong")
async def respond():
    return "pong"

myagent.run(host="127.0.0.1", port=8888)
```

This is ideal for simple agents without internal state or external dependencies.

### 📂 Examples that use `setup()`

To see this pattern in context, look at the following agents in this repository:

* `a-reporter-*/`: uses setup() to initialize an async message queue for ordering and batching.
* `a-seller-*/` and `a-buyer-*/`: use setup() to initialize shared state, aiosqlite databases, and background negotiation logic with locks.

These examples show how `setup()` gives you a controlled place to initialize anything async or stateful before the agent starts running. If your agent grows in complexity, especially if it uses shared state or persistent storage, setup() is your friend.
