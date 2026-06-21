from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse

from router import route_get, route_post


class Handler(BaseHTTPRequestHandler):
    def _json(self, payload: dict, code: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        code, payload = route_get(parsed.path, parsed.query)
        self._json(payload, code)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        code, payload = route_post(parsed.path, parsed.query)
        self._json(payload, code)


def run() -> None:
    server = HTTPServer(("127.0.0.1", 7890), Handler)
    print("uHomeNest API listening on http://127.0.0.1:7890")
    server.serve_forever()


if __name__ == "__main__":
    run()
