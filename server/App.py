import os
import signal
import socket
import subprocess
import sys
import uvicorn
import threading
import webview


def find_free_port() -> str:
    """Dynamic port to avoid collision"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


HOST: str = "127.0.0.1"
PORT: str = find_free_port()
os.environ["APP_PORT"] = str(PORT)

BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
DUMPS1090_PATH = os.path.join(BASE_DIR, "dump1090")

dump1090_process = None
stop_event = threading.Event()


def start_server() -> None:
    uvicorn.run("server:app", host=HOST, port=PORT)


def start_dump1090() -> None:
    global dump1090_process
    dump1090_process = subprocess.Popen(
        [DUMPS1090_PATH, "--net"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


def on_closing() -> None:
    stop_event.set()
    if dump1090_process:
        dump1090_process.terminate()
        try:
            dump1090_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            dump1090_process.kill()
    os.kill(os.getpid(), signal.SIGTERM)


if __name__ == "__main__":
    dump1090_thread = threading.Thread(target=start_dump1090, daemon=True)
    dump1090_thread.start()

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    window = webview.create_window("Open Air", f"http://{HOST}:{PORT}")
    window.events.closing += on_closing
    webview.start()
