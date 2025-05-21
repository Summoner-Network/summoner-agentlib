# ChatAgent (List‐Aware)

This agent builds on the ChatAgent introduced in `a-chat-1/` by handling batched messages (lists) sent by reporter-style agents (see folders `a-reporter-*/`). It connects to a Summoner server, receives both single strings and lists of strings, and displays each item in the correct order before prompting you to respond.

Use this version when you expect to receive timed or grouped reports (lists) rather than only individual chat lines.


## 📦 What It Does

* Waits for incoming payloads on the `custom_receive` route.
  * Detects whether the payload is:
    * A `list[str]` (batched report)
    * A `str` (individual message)
  * Prints each string in sequence, tagging lines that start with `Warning:` as server warnings.
* Lets you type responses, which are sent on the `custom_send` route.


## 💡 How It Differs from `a-chat-1/`

|                      | a-chat-1 (Basic)           | a-chat-2 (List-Aware)                          |
| -------------------- | -------------------------- | ---------------------------------------------- |
| **Payload type**     | Always a single `str`      | May be a `str` **or** a `list[str]`            |
| **Display behavior** | One line per message       | Unpacks lists and prints each element in order |
| **Typical use case** | Simple back-and-forth chat | Works with agents that batch multiple messages |


## ✏️ How It Works

1. **Receive** on `custom_receive`:

   * If the payload is a **list**, loop over its items and print each one.
   * If it’s a **string**, print it directly.
2. **Prompt** you at `s> ` and send whatever you type on the `custom_send` route.


## ▶️ Running the Agent

```bash
python a-chat-2/agent.py
```

You’ll see:

```
2025-05-20 10:00:00 - ChatAgent - INFO - Connected to server.
s>
```

**Example – incoming batched report**:

  ```
  [Received] Hi
  [Received] How are you?
  [Received] Bye
  r> Got it, thanks!
  ```

**Example – incoming single message**:

  ```
  [Received] Are you there?
  r> Yes, I’m here!
  ```

**Server warning example**:

  If a message starts with `"Warning:"`, it is specially tagged as:

  ```
  [From server] Warning: Something went wrong
  ```

## 🚦 Summary of Behavior

| Event                        | Behavior                               |
| ---------------------------- | -------------------------------------- |
| Payload is a `list[str]`     | Unpack and print each element in order |
| Payload is a single `str`    | Print that string                      |
| Line starts with `Warning:`  | Tag as `[From server] …`               |
| You type at the `s> ` prompt | Sent immediately on `custom_send`      |
