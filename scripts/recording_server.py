"""Loopback-only display for CleanShot recording of actual Python execution."""

import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENTS = []
LOCK = threading.Lock()
RUNNING = False


def run():
    global RUNNING
    output = ROOT / "output/recording"
    output.mkdir(parents=True, exist_ok=True)
    with (output / "live_run.jsonl").open("w") as log:
        process = subprocess.Popen([sys.executable, "-m", "scripts.recording_run"], cwd=ROOT,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            log.write(line)
            log.flush()
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                event = {"event": "message", "text": line.rstrip()}
            with LOCK:
                EVENTS.append(event)
        code = process.wait()
        with LOCK:
            EVENTS.append({"event": "message", "text": f"Process exited with code {code}"})
            EVENTS.append({"event": "exit", "code": code})
            RUNNING = False


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/events":
            with LOCK:
                payload = json.dumps(EVENTS).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
        elif self.path == "/":
            payload = (ROOT / "scripts/recording_view.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
        else:
            self.send_error(404)
            return
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        global RUNNING
        if self.path != "/start" or self.headers.get("Host") != "127.0.0.1:55410":
            self.send_error(403)
            return
        with LOCK:
            if RUNNING:
                self.send_error(409)
                return
            EVENTS.clear()
            RUNNING = True
        threading.Thread(target=run, daemon=True).start()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"started")


if __name__ == "__main__":
    print("Recording view: http://127.0.0.1:55410", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 55410), Handler).serve_forever()
