import asyncio
import json
from pathlib import Path
from itertools import cycle

from summoner.client import SummonerClient

# Load questions once
qa_path = Path(__file__).parent / "qa.json"
with qa_path.open("r", encoding="utf-8") as f:
    QUESTIONS = list(json.load(f).keys())

if __name__ == "__main__":
    myagent = SummonerClient(name="QuestionBot")

    # Create a simple cycling iterator
    question_cycle = cycle(QUESTIONS)

    @myagent.receive(route="")
    async def receive_response(msg):
        content = msg["content"] if isinstance(msg, dict) else msg
        print(f"\033[91mReceived:\033[0m {content}")

    @myagent.send(route="")
    async def send_question():
        # Grab the next question
        next_q = next(question_cycle)
        # Small pause if you want a pacing delay
        await asyncio.sleep(1)
        print(f"\033[90m(Asked: {next_q})\033[0m")
        return next_q

    myagent.run(host="127.0.0.1", port=8888)
