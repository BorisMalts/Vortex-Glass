#!/usr/bin/env python3
"""
run.py — Vortex-Glass dev server
Place next to liquid-glass.js and demo.html, then:  python3 run.py
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

PORT = 3000
HOST = "localhost"

# ── Serve from the directory this script lives in ────────────────────────────
ROOT = Path(__file__).parent.resolve()
os.chdir(ROOT)

# ── Custom handler: correct MIME for .js ES modules ──────────────────────────
class Handler(http.server.SimpleHTTPRequestHandler):

    # Map extensions → MIME types (SimpleHTTPRequestHandler misses some)
    EXTRA_TYPES = {
        ".js":   "application/javascript",
        ".mjs":  "application/javascript",
        ".css":  "text/css",
        ".html": "text/html",
        ".json": "application/json",
        ".svg":  "image/svg+xml",
        ".png":  "image/png",
        ".jpg":  "image/jpeg",
        ".woff2":"font/woff2",
    }

    def guess_type(self, path):
        ext = Path(path).suffix.lower()
        return self.EXTRA_TYPES.get(ext, super().guess_type(path))

    # Add CORS + cache-busting headers so ES module imports always work
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    # Silence request logs — set to True if you want them
    VERBOSE = False

    def log_message(self, fmt, *args):
        if self.VERBOSE:
            super().log_message(fmt, *args)


# ── Sanity checks ─────────────────────────────────────────────────────────────
def check_files():
    missing = []
    for name in ("demo.html", "liquid-glass.js"):
        if not (ROOT / name).exists():
            missing.append(name)
    if missing:
        print(f"\n⚠  Missing files in {ROOT}:")
        for m in missing:
            print(f"   · {m}")
        print("\nMake sure demo.html and liquid-glass.js are in the same folder as run.py.\n")
        sys.exit(1)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    check_files()

    url = f"http://{HOST}:{PORT}/demo.html"

    # Allow address reuse so restarting immediately after Ctrl-C works
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
        print(f"\n  🫧  Vortex-Glass dev server")
        print(f"  ──────────────────────────────")
        print(f"  Serving : {ROOT}")
        print(f"  URL     : {url}")
        print(f"  Stop    : Ctrl-C\n")

        # Open browser after server is ready
        webbrowser.open(url)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n  Server stopped.\n")


if __name__ == "__main__":
    main()