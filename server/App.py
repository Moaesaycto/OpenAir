import threading
import webview
import uvicorn
import os
import sys
import subprocess
import signal
import socket
import time

HOST = "127.0.0.1"
PORT = 8000
BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
DUMPS1090_PATH = os.path.join(BASE_DIR, "dump1090")

BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

dump1090_process = None


def start_server():
    uvicorn.run("server:app", host=HOST, port=PORT)


def start_dump1090():
    global dump1090_process
    dump1090_process = subprocess.Popen(
        [DUMPS1090_PATH, "--net"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


def read_dump1090():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("localhost", 30003))
                print("Connected to dump1090", flush=True)
                while True:
                    data = s.recv(1024).decode("utf-8", errors="ignore")
                    if not data:
                        break
                    print(data, end="", flush=True)
        except ConnectionRefusedError:
            print("Waiting for dump1090...", flush=True)
            time.sleep(1)


def on_closing():
    if dump1090_process:
        dump1090_process.terminate()
        dump1090_process.wait()
    os.kill(os.getpid(), signal.SIGTERM)


if __name__ == "__main__":
    dump1090_thread = threading.Thread(target=start_dump1090, daemon=True)
    dump1090_thread.start()

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    t3 = threading.Thread(target=read_dump1090, daemon=True)
    t3.start()

    window = webview.create_window("Open Air", f"http://{HOST}:{PORT}")
    window.events.closing += on_closing
    webview.start()
