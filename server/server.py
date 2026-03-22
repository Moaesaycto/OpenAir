import mimetypes
import os
import sys

from sockets import dump1090_handler, gps_stream_handler

BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get("APP_PORT", 8000))

WEBSOCKETS_MAP = {
    "/adsb": dump1090_handler,
    "/gps-stream": gps_stream_handler,
}


async def app(scope, receive, send):
    if scope["type"] == "websocket":
        path = scope["path"]
        if path in WEBSOCKETS_MAP:
            ws_run = WEBSOCKETS_MAP[path]
            await ws_run(scope, receive, send)
        return

    filepath = os.path.join(BASE_DIR, "static/index.html")
    with open(filepath, "r") as f:
        content = f.read()

    # We inject this through the window for dynamic ports accessible in the client
    content = content.replace(
        "</head>", f"<script>window.API_PORT={PORT}</script></head>"
    )

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
    await send({"type": "http.response.body", "body": content.encode("utf-8")})
