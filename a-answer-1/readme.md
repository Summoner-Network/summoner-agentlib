# AnswerBot

This agent listens for plain-text questions and replies with pre-configured answers loaded from `qa.json`. It demonstrates:

- Loading static Q&A data at startup  
- Asynchronously buffering incoming requests  
- Sending back responses in a batched, ordered fashion  


## 📦 What It Does

1. **Loads** answers from `a-answer-1/qa.json` into a Python dict.  
2. **Receives** each incoming question (with an optional `addr` field) on the default route.  
3. **Buffers** matching answers in an `asyncio.Queue`.  
4. **Sends** out all buffered responses every time the send handler runs, preserving order and tagging each reply with its original sender’s address.


## 🔧 How It Works

- At startup, `qa.json` is read into the global `ANSWERS` dict.  
- **Receive handler** (`@myagent.receive(route="")`):  
  - Prints the raw payload for debugging.  
  - Extracts `msg["content"]` and `msg["addr"]`.  
  - If the question text exists in `ANSWERS`, enqueues a tuple `(addr, answer)`.  
- **Send handler** (`@myagent.send(route="")`):  
  - Blocks until at least one `(addr, answer)` is available.  
  - Sleeps 0.1 s to allow additional requests to queue up.  
  - Drains the queue into a list of lines formatted as  
    ```
    Response to <addr>: <answer>
    ```  
  - Returns them joined by `\n` (so the SDK frames them as one batch).

If no questions arrive, the send handler never fires and the agent remains idle.


## ▶️ Quick Demo

You will need three terminals:

1. **Terminal 1: Start the server** 
  ```bash
  python server.py
  ```

2. **Terminal 2: Run ChatAgent and ask questions**

  ```bash
  python a-chat-1/agent.py
  ```

  ```
  2025-05-20 16:58:35,360 - ChatAgent - INFO - Connected to server.
  s> How old are you?
  [Received] I do not age like humans do.
  r> What time is it?
  [Received] I suggest checking your device's clock.
  r> How are you?
  [Received] I am operating smoothly, thank you.
  r>
  ```

3. **Terminal 3: Run AnswerBot**

  ```bash
  python a-answer-1/agent.py
  ```

  ```
  2025-05-20 16:58:32,091 - AnswerBot - INFO - Connected to server.
  Received: {'addr': '127.0.0.1:58211', 'content': 'How old are you?'}
  Received: {'addr': '127.0.0.1:58211', 'content': 'What time is it?'}
  Received: {'addr': '127.0.0.1:58211', 'content': 'How are you?'}
  ```

  AnswerBot logs each raw request and replies in the same order as the chat agent sees them.


## 🚦 Behavior Summary

| Event                          | Behavior                                                        |
| ------------------------------ | --------------------------------------------------------------- |
| Incoming question in `ANSWERS` | Enqueue `(addr, answer)`                                        |
| Send handler triggered         | Wait 0.1 s → batch all queued replies → send one framed message |
| Question not in `ANSWERS`      | Ignored (no reply)                                              |
| No questions received          | Agent remains idle                                              |


## 💡 Tips

* **Add your own Q\&A** by editing `qa.json` (key = question text, value = answer).
* **Change the debounce window** by adjusting `await asyncio.sleep(0.1)` to a longer delay.
* **Customize the route** names by replacing the empty strings in `@receive(route="…")` and `@send(route="…")` if you need multiple channels.

Use AnswerBot as a template for any static Q\&A or lookup-based agent. Just swap out `qa.json` for your own data store and route names as needed.
