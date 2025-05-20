# ChatAgent

This is the simplest interactive agent in the Summoner ecosystem. It connects to a Summoner server, receives messages, and lets you type replies directly into the terminal.

It’s ideal for getting started with agent development and understanding how send/receive routes work.

## 📦 What It Does

* Waits for incoming messages on the `custom_receive` route.
* Prints those messages to the terminal.
* Lets you type responses, which are sent on the `custom_send` route.

You can think of it as a command-line chat interface to the Summoner network.

## ✏️ How It Works

When the agent runs:

* It connects to the server (e.g., on localhost:8888).

* It listens for messages from other agents or the server.

* It prompts you to type messages with a prefix like:

  ```
  s> Hello!
  ```

* Messages received from others are printed like:

  ```
  [Received] Hello!
  r>
  ```

If a message starts with `"Warning:"`, it is specially tagged as:

```
[From server] Warning: Something went wrong
```


## ▶️ Running the Agent

To start the agent:

```bash
python a-chat-1/agent.py
```

You’ll see something like:

```
2025-05-20 10:00:00 - ChatAgent - INFO - Connected to server.
s>
```

Type your message at the prompt and press Enter to send.


## 🚦 Summary of Behavior

| Event                          | Behavior                             |
| ------------------------------ | ------------------------------------ |
| Message received               | Printed in the terminal with a tag   |
| You type a message             | Sent to the server immediately       |
| Message starts with "Warning:" | Displayed with \[From server] tag    |
| Idle                           | Waits quietly until input or message |

