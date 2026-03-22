import asyncio
import pynmea2
import serial
import serial.tools.list_ports
import threading


GPS_BAUD = 9600


def _is_gps_port(device: str) -> bool:
    """Given a port, check if it is returning valid GPS signals"""
    try:
        with serial.Serial(device, GPS_BAUD, timeout=2) as ser:
            for _ in range(10):
                line = ser.readline().decode("ascii", errors="replace").strip()
                if line.startswith("$GP") or line.startswith("$GN"):
                    try:
                        pynmea2.parse(line)
                        return True
                    except pynmea2.ParseError:
                        continue
    except (serial.SerialException, OSError):
        pass
    return False


def _find_gps_port() -> str | None:
    """Finds any USB port that provides NMEA 0183"""
    for port in serial.tools.list_ports.comports():
        if port.vid and port.pid:
            if _is_gps_port(port.device):
                return port.device
    return None


GPS_PORT = _find_gps_port()


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
        stop_event.set()
        await send({"type": "websocket.close"})
