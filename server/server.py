import sys
import os
import mimetypes

BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


async def app(scope, receive, send):
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
