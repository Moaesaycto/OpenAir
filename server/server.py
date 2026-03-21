import sys
import os
import mimetypes
import asyncio

BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


async def app(scope, receive, send):
    if scope["type"] == "websocket" and scope["path"] == "/adsb":
        await websocket_handler(scope, receive, send)
        return

    filepath = os.path.join(BASE_DIR, "static/index.html")

    with open(filepath, "rb") as f:
        content = f.read()

    mime, _ = mimetypes.guess_type(filepath)
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", (mime or "application/octet-stream").encode()],
            ],
        }
    )
    await send({"type": "http.response.body", "body": content})


async def websocket_handler(scope, receive, send):
    await send({"type": "websocket.accept"})
    reader, writer = await asyncio.open_connection("localhost", 30003)
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            await send(
                {"type": "websocket.send", "text": data.decode("utf-8", errors="ignore")}
            )
    finally:
        writer.close()
        await send({"type": "websocket.close"})
