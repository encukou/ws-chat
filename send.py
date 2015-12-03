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


async def send_one(msg):
    ws = await aiohttp.ws_connect('http://localhost:8080/CLI/ws/')
    ws.send_str(msg)
    await ws.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(send_one(' '.join(sys.argv[1:])))
