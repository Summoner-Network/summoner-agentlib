# QuestionBot 

This agent drives a simple Q→A demo by cycling through all questions defined in `qa.json`, sending one question every second, and printing each incoming response. It pairs with an AnswerBot that looks up answers in the same `qa.json`.


## 📦 What It Does

1. **Loads** all question keys from `a-question-1/qa.json` into a list.  
2. **Cycles** through that list indefinitely (uses `itertools.cycle`).  
3. **Send handler** (`custom_send` route):  
   - Picks the next question.  
   - Waits 1 second to pace the conversation.  
   - Prints `(Asked: …)` in gray.  
   - Returns the question string to the server.  
4. **Receive handler** (`custom_receive` route):  
   - Prints incoming responses with a red “Received:” tag.  

If you ever reach the end of the question list, it loops back to the first question automatically.

---

## ▶️ Running the Demo

1. **Start the server**  (in `terminal 1`)
```bash
python server.py
```

2. **Start the AnswerBot** (in `terminal 2`)

```bash
python a-answer-1/agent.py
```

It connects and stands by to answer questions from `qa.json`.

3. **Start the QuestionBot** (in `terminal 3`)

```bash
python a-question-1/agent.py
```

You’ll see output like:

```
2025-05-20 17:50:36,277 - QuestionBot - INFO - Connected to server.
(Asked: What is your name?)
Received: [Response to 127.0.0.1:58745] I am AnswerBot.
(Asked: What is the meaning of life?)
Received: [Response to 127.0.0.1:58745] 42.
(Asked: Do you like Rust or Python?)
Received: [Response to 127.0.0.1:58745] Both have their strengths!
…
```


## 🚦 Behavior Summary

| Event                 | Behavior                                               |
| --------------------- | ------------------------------------------------------ |
| Send handler fires    | Sends the next question from `qa.json`, pacing by 1 s. |
| Receive handler fires | Prints the server’s answer with `Received:` in red.    |
| Questions exhausted   | Automatically loops back to the first question.        |
| No activity           | Idle until send/receive events occur.                  |


## 💡 Tips & Extensions

* **Adjust pacing** by changing the `await asyncio.sleep(1)` delay.
* **Add or remove questions** by editing `qa.json` -- no code changes required.
* **Custom routes**: Replace the empty `route=""` strings with named routes (e.g. `"ask"` and `"answer"`) if you integrate with multiple channels.
* **Error handling**: You can wrap `next(question_cycle)` in `try/except` if `qa.json` might be empty.

Use QuestionBot as a template for any cyclic‐query agent that drives a static knowledge base or external service.

