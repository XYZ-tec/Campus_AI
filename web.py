"""
web.py
======
Basic web frontend for the Smart Campus AI system.

Start it with:   python web.py
Then open:       http://localhost:8000

It uses only the Python standard library (no Flask needed). The page sends
the form to /api/request, which calls the same process_request() as the CLI,
so the web page and the CLI always give the same answer.
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from pipeline import process_request
from core.constants import (
    ROLES, REQUEST_TYPES, CATEGORIES, LOCATIONS, REQUIRED_FIELDS, OPTIONAL_FIELDS,
)

PORT = 8000
PAGE = Path(__file__).parent / "web" / "index.html"


class Handler(BaseHTTPRequestHandler):
    """Answers the browser: the page, the form options, and form submissions."""

    def send_json(self, data, status=200):
        """Send a Python dictionary to the browser as JSON."""
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        """GET /             -> the web page
           GET /api/options  -> the choices and fields for the form"""
        if self.path == "/":
            body = PAGE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/options":
            self.send_json({
                "roles": ROLES,
                "request_types": REQUEST_TYPES,
                "categories": CATEGORIES,
                "locations": LOCATIONS,
                "required_fields": REQUIRED_FIELDS,
                "optional_fields": OPTIONAL_FIELDS,
            })
        else:
            self.send_json({"message": "Page not found."}, 404)

    def do_POST(self):
        """POST /api/request -> run the request through the pipeline."""
        if self.path != "/api/request":
            self.send_json({"message": "Page not found."}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw_request = json.loads(self.rfile.read(length))
            if not isinstance(raw_request, dict):
                raise ValueError("request must be a JSON object")
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"decision": "rejected",
                            "message": "Invalid request data: " + str(error)}, 400)
            return
        try:
            self.send_json(process_request(raw_request))
        except Exception as error:      # never let one bad request stop the server
            self.send_json({"decision": "rejected",
                            "message": "Server error: " + str(error)}, 500)

    def log_message(self, format, *args):
        """Keep the terminal quiet (do not print every browser request)."""
        return


def main():
    """Start the web server and keep it running until Ctrl + C."""
    server = HTTPServer(("localhost", PORT), Handler)
    print("Smart Campus AI web page: http://localhost:" + str(PORT))
    print("Press Ctrl + C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
