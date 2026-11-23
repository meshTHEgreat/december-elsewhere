"""Serve the exact Pages files with the production path prefix for browser checks."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PREFIX = "/december-elsewhere"
DOCS = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else ROOT / "docs"


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith(PREFIX + "/"):
            self.path = self.path[len(PREFIX):]
        super().do_GET()

    def log_message(self, *_):
        pass


class Preview(ThreadingHTTPServer):
    request_queue_size = 128


with Preview(("127.0.0.1", int(sys.argv[1])), partial(Handler, directory=DOCS)) as server:
    server.serve_forever()
