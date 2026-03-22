import sys
import os
import mimetypes
import asyncio
import json
import serial
import threading

from util import try_get_gps

BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get("APP_PORT", 8000))

GPS_BAUD = 9600
GPS_PORT = "/dev/cu.usbmodem1101"


async def app(scope, receive, send):
    if scope["type"] == "websocket" and scope["path"] == "/adsb":
        await dump1090_handler(scope, receive, send)
        return

    if scope["type"] == "websocket" and scope["path"] == "/gps-stream":
        await gps_stream_handler(scope, receive, send)
        return

    path = scope.get("path", "/")
    CORS_HEADERS = [
        [b"access-control-allow-origin", b"*"],
        [b"content-type", b"application/json"],
    ]

    if path == "/gps":
        query = dict(
            p.split("=")
            for p in scope.get("query_string", b"").decode().split("&")
            if "=" in p
        )
        manual_port = query.get(
            "port"
        )  # None if not provided, e.g. "/gps?port=/dev/ttyUSB0"
        result = await asyncio.to_thread(try_get_gps, manual_port)
        body = json.dumps(result).encode()
        await send(
            {"type": "http.response.start", "status": 200, "headers": CORS_HEADERS}
        )
        await send({"type": "http.response.body", "body": body})
        return

    if path == "/ports":
        ports = [
            {"device": p.device, "name": p.description}
            for p in serial.tools.list_ports.comports()
        ]
        body = json.dumps(ports).encode()
        await send(
            {"type": "http.response.start", "status": 200, "headers": CORS_HEADERS}
        )
        await send({"type": "http.response.body", "body": body})
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


async def gps_stream_handler(scope, receive, send):
    await send({"type": "websocket.accept"})
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()
    stop_event = threading.Event()

    def read_serial():
        try:
            with serial.Serial(GPS_PORT, GPS_BAUD, timeout=1) as ser:
                while not stop_event.is_set():
                    line = ser.readline().decode("ascii", errors="replace").strip()
                    if line:
                        loop.call_soon_threadsafe(queue.put_nowait, line)
        except serial.SerialException:
            loop.call_soon_threadsafe(queue.put_nowait, None)

    threading.Thread(target=read_serial, daemon=True).start()

    try:
        while True:
            line = await queue.get()
            if line is None:
                break
            await send({"type": "websocket.send", "text": line})
    finally:
        stop_event.set()  # signals the thread to stop
        await send({"type": "websocket.close"})
