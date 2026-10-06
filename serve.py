#!/usr/bin/env python3
"""Static server for the article, plus a save endpoint for the in-page editor.

    python3 serve.py            # serves this folder on http://localhost:8765
    python3 serve.py 3000       # pick a port

PUT /article.md with the new markdown in the body overwrites article.md.
Only files inside this folder are served or written.
"""
import os, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
EDITABLE = {"article.md"}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_PUT(self):
        name = self.path.lstrip("/").split("?")[0]
        if name not in EDITABLE:
            self.send_error(403, "not editable")
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        tmp = os.path.join(ROOT, name + ".tmp")
        with open(tmp, "wb") as f:
            f.write(body)
        os.replace(tmp, os.path.join(ROOT, name))
        self.send_response(204)
        self.end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.command, self.path))

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print("serving %s on http://localhost:%d" % (ROOT, port))
    ThreadingHTTPServer(("", port), Handler).serve_forever()
