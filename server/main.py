import os
import mimetypes

async def app(scope, receive, send):
    path = scope["path"].lstrip("/") or "index.html"
    filepath = os.path.join("client/dist", path)

    if not os.path.exists(filepath):
        filepath = "/Users/moaesaycto/Desktop/Code Dump/OpenAir/client/dist/index.html"

    with open(filepath, "rb") as f:
        content = f.read()

    mime, _ = mimetypes.guess_type(filepath)
    await send({"type": "http.response.start", "status": 200, "headers": [
        [b"content-type", (mime or "application/octet-stream").encode()],
    ]})
    await send({"type": "http.response.body", "body": content})