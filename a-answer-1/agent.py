from summoner.client import SummonerClient
import asyncio
import json
from pathlib import Path

def format_reply(addr, ans):
    prefix = f"[Response to {addr}] " if addr else ""
    return f"{prefix}{ans}"

qa_path = Path(__file__).parent / "qa.json"
with qa_path.open("r", encoding="utf-8") as f:
    ANSWERS = json.load(f)

message_buffer = None  # initialized in setup()

if __name__ == "__main__":
    myagent = SummonerClient(name="AnswerBot", option="python")

    async def setup():
        global message_buffer
        message_buffer = asyncio.Queue()
        
        @myagent.receive(route="")
        async def handle_question(msg):
            print(f"Received: {msg}")
            content = (msg["content"] if isinstance(msg, dict) else msg)
            addr = (msg["addr"] if isinstance(msg, dict) else "")
            if content in ANSWERS:
                await message_buffer.put((addr, ANSWERS[content]))

        @myagent.send(route="")
        async def respond_to_question():
            first = await message_buffer.get()
            batch = [format_reply(*first)]
            await asyncio.sleep(0.05)

            while True:
                try:
                    payload = message_buffer.get_nowait()
                    batch.append(format_reply(*payload))
                except asyncio.QueueEmpty:
                    break

            return "\n".join(batch)

    myagent.loop.run_until_complete(setup())
    myagent.run(host="127.0.0.1", port=8888)