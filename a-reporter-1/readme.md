# ReporterAgent

This agent listens for incoming messages and reports them back to the server in timed batches. It is built using [summoner-core](https://github.com/Summoner-Network/summoner-core) and demonstrates how to:

* Receive and process messages from the server
* Temporarily buffer messages
* Report the buffered messages every 5 seconds (only if new messages have arrived)
* Write clean, coroutine-safe logic using asyncio and the SummonerClient SDK


## 🔧 How It Works

This agent does nothing until it receives a message from the server. When a message is received:

1. It is printed in the terminal for inspection.
2. It is pushed into a queue for later reporting.

The agent then waits until the send route is triggered. The send route behaves as follows:

* It blocks until at least one message is available in the buffer.
* Once a message is received, it waits 5 seconds.
* During those 5 seconds, any additional messages are added to the batch.
* After 5 seconds, the entire batch is sent as a single message (joined with newline characters).

If no messages were ever received, nothing is sent  --  the agent stays idle.

## 🚀 Demo: How the Agent Behaves

This agent listens for messages, waits 5 seconds after receiving the first one, then sends all buffered messages as a single report. Here is how it works in action (you will need three terminals):


1. **Terminal 1: Start the server**

    ```bash
    python server.py
    ```

2. **Terminal 2: Start a chat agent and send a few messages quickly**

    ```bash
    python a-chat-1/agent.py
    ```

    Example interaction:

    ```
    2025-05-20 10:33:30,969 - ChatAgent - INFO - Connected to server.
    s> Hi
    s> How are you?
    s> Bye
    [Received] Hi
    How are you?
    Bye
    r>
    ```

    Note: All messages are sent within a few seconds.

3. **Terminal 3: Start the reporting agent**

    ```bash
    python a-reporter-1/agent.py
    ```

    Output:

    ```
    2025-05-20 10:33:34,662 - ReporterAgent - INFO - Connected to server.
    [Received] Hi
    [Received] How are you?
    [Received] Bye
    r>
    ```

    After the first message is received, the agent waits 5 seconds, gathers additional messages during that window, and then sends the entire batch back to the server (or other agents listening).


## 🚦 Behavior Summary

| Scenario                   | Behavior                           |
| -------------------------- | ---------------------------------- |
| No messages received       | Agent remains idle                 |
| One message received       | Sends after 5 seconds              |
| Multiple messages received | Batches them, sends after 5 sec    |
| Messages trickling in      | All messages within 5 sec are sent |


## 💡 Tips

* You can customize the batching window by changing the sleep duration in `custom_send()`.
* If you want to flush messages more frequently or based on a threshold (e.g. every 10 messages), this pattern is easy to extend.
* This agent is a good starting point for building "monitoring" or "reporting" agents that accumulate events and send them on a delay.
