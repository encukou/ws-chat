import asyncio
import json

import aiohttp
from aiohttp import web

queues = []
history = []


async def hello(request):
    form_data = await request.post()
    if 'name' in form_data:
        return web.HTTPFound(app.router['chat_page'].url_for(**form_data))

    with open('home.html', 'rb') as f:
        return web.Response(
            body=f.read().decode('utf8'),
            content_type='text/html')


async def chat_page(request):
    with open('chat.html', 'rb') as f:
        return web.Response(
            body=f.read().decode('utf8'),
            content_type='text/html')


async def new_msg(request):
    name = request.match_info['name']
    read_task = asyncio.Task(request.content.read())
    message = (await read_task).decode('utf-8')
    await send_message(name, message)
    return web.Response(body=b'OK')


async def send_message(name, message):
    print('{}: {}'.format(name, message).strip())
    history.append('{}: {}'.format(name, message))
    if len(history) > 20:
        del history[:-10]
    for queue in queues:
        await queue.put((name, message))


async def websocket_handler(request):
    name = request.match_info['name']
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    await send_message('system', '{} joined!'.format(name))

    for message in list(history):
        await ws.send_str(message)

    echo_task = asyncio.Task(echo_loop(ws))

    async for msg in ws:

        if msg.type == aiohttp.WSMsgType.close:
            print('websocket connection closed')
            break
        elif msg.type == aiohttp.WSMsgType.error:
            print('ws connection closed with exception %s' % ws.exception())
            break
        elif msg.type == aiohttp.WSMsgType.text:
            message = msg.data
            await send_message(name, message)
        else:
            print('ws connection received unknown message type %s' % msg.tp)

    await send_message('system', '{} left!'.format(name))
    echo_task.cancel()
    await echo_task
    return ws

async def echo_loop(ws):
    queue = asyncio.Queue()
    queues.append(queue)
    try:
        while True:
            name, message = await queue.get()
            await ws.send_str('{}: {}'.format(name, message))
    finally:
        queues.remove(queue)


app = web.Application()
app.router.add_route('GET', '/', hello)
app.router.add_route('POST', '/', hello)
app.router.add_route('GET', '/{name}/', chat_page, name='chat_page')
app.router.add_route('POST', '/{name}/', new_msg)
app.router.add_route('GET', '/{name}/ws/', websocket_handler)

def main():
    loop = asyncio.get_event_loop()
    handler = app.make_handler()
    f = loop.create_server(handler, '0.0.0.0', 8080)
    srv = loop.run_until_complete(f)

    async def end():
        await handler.finish_connections(1.0)
        srv.close()
        await srv.wait_closed()
        await app.finish()

    print('serving on', srv.sockets[0].getsockname())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(end())
    loop.close()

if __name__ == '__main__':
    main()
