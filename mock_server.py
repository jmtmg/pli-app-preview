#!/usr/bin/env python3
import http.server
import socketserver
import urllib.parse
import json
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
# Serve from this script's directory (dist)
root = os.path.dirname(os.path.abspath(__file__))
os.chdir(root)

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # CORS for convenience
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == '/conversations':
            q = urllib.parse.parse_qs(parsed.query)
            if q.get('filter') == ['humans']:
                sample = {
                    "conversations": [
                        {
                            "id": "1",
                            "title": "Conversation humaine 1",
                            "messages": [
                                {"from": "Alice", "text": "Bonjour — ceci est une démo."},
                                {"from": "Bob", "text": "Salut — test PLI demo."}
                            ]
                        }
                    ]
                }
                body = json.dumps(sample, ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
        # Otherwise, serve static files
        return super().do_GET()

if __name__ == '__main__':
    with socketserver.ThreadingTCPServer(("", PORT), Handler) as httpd:
        print(f"Serving dist at http://127.0.0.1:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
