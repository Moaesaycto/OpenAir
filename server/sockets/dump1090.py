import asyncio


async def dump1090_handler(scope, receive, send):
    await send({"type": "websocket.accept"})

    reader, writer = None, None
    for _ in range(10):
        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", 30003)
            break
        except OSError:
            await asyncio.sleep(1)

    if reader is None:
        await send({"type": "websocket.close"})
        return

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            await send(
                {
                    "type": "websocket.send",
                    "text": data.decode("utf-8", errors="ignore"),
                }
            )
    finally:
        writer.close()
        await send({"type": "websocket.close"})
