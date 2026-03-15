import threading
import webview
import uvicorn

HOST = "127.0.0.1"
PORT = 8000


def start_server():
    uvicorn.run("server:app", host=HOST, port=PORT)


if __name__ == "__main__":
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    webview.create_window("Open Air", f"http://{HOST}:{PORT}")
    webview.start()
