from summoner.client import SummonerClient
import asyncio

message_buffer = None  # initialized in setup()

if __name__ == "__main__":
    myagent = SummonerClient(name="ReporterAgent")

    async def setup():
        global message_buffer
        message_buffer = asyncio.Queue()

        @myagent.receive(route="custom_receive")
        async def custom_receive(msg):
            content = msg["content"] if isinstance(msg, dict) else msg
            await message_buffer.put(content)

            tag = "\r[From server]" if content.startswith("Warning:") else "\r[Received]"
            print(tag, content, flush=True)
            print("r> ", end="", flush=True)

        @myagent.send(route="custom_send")
        async def custom_send():
            # Wait for the first message (blocks indefinitely if nothing arrives)
            first = await message_buffer.get()
            batch = [first]

            # After first message, wait 5 seconds to collect more
            await asyncio.sleep(5)

            while True:
                try:
                    msg = message_buffer.get_nowait()
                    batch.append(msg)
                except asyncio.QueueEmpty:
                    break

            return batch

    myagent.loop.run_until_complete(setup())
    myagent.run(host="127.0.0.1", port=8888)
