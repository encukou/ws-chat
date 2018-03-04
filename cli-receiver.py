import asyncio
import re
import json
import sys
import blessings

import aiohttp

NUM_STRIPS = 6

T = blessings.Terminal(stream=sys.stderr)

def clamp(n, minimum, maximum):
    if n < minimum:
        return minimum
    if n > maximum:
        return maximum
    return n


async def client():
    ws = await aiohttp.ClientSession().ws_connect('http://localhost:8080/CLI/ws/')

    try:
        while True:
            msg = await ws.receive()

            if msg.type == aiohttp.WSMsgType.text:
                data = msg.data.strip()
                print(data)
            elif msg.type == aiohttp.WSMsgType.closed:
                break
            elif msg.type == aiohttp.WSMsgType.error:
                break
    finally:
        await ws.close()

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(client())
except KeyboardInterrupt:
    pass
