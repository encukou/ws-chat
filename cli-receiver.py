import asyncio
import sys

import aiohttp


URL = 'http://localhost:8080/CLI/ws/'

async def client():
    async with aiohttp.ClientSession().ws_connect(URL) as ws:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = msg.data.strip()
                print(data)
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break

asyncio.run(client())
