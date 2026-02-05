#!/usr/bin/env python3
"""
Simple API Explorer Server
Run this, then open http://localhost:8000 in your browser
"""

import http.server
import json
import urllib.request
import urllib.error
import ssl
from urllib.parse import urlparse, parse_qs

PORT = 8000

class APIProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def do_POST(self):
        if self.path == '/proxy':
            self.handle_proxy()
        else:
            super().do_POST()

    def handle_proxy(self):
        """Proxy requests to external APIs"""
        try:
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            request_data = json.loads(body)

            # Extract proxy parameters
            target_url = request_data.get('url')
            method = request_data.get('method', 'GET')
            headers = request_data.get('headers', {})
            payload = request_data.get('body')

            if not target_url:
                self.send_error(400, 'Missing URL')
                return

            # Prepare the request
            req_body = None
            if payload:
                if isinstance(payload, dict):
                    req_body = json.dumps(payload).encode('utf-8')
                else:
                    req_body = payload.encode('utf-8')

            # Create request
            req = urllib.request.Request(target_url, data=req_body, method=method)

            # Add headers
            for key, value in headers.items():
                req.add_header(key, value)

            # Make the request (with SSL context that accepts all certs for testing)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            try:
                with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
                    response_body = response.read().decode('utf-8')
                    response_headers = dict(response.headers)
                    status_code = response.status

                    # Send response back
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()

                    result = {
                        'status': status_code,
                        'statusText': response.reason,
                        'headers': response_headers,
                        'body': response_body
                    }
                    self.wfile.write(json.dumps(result).encode('utf-8'))

            except urllib.error.HTTPError as e:
                response_body = e.read().decode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                result = {
                    'status': e.code,
                    'statusText': e.reason,
                    'headers': dict(e.headers),
                    'body': response_body
                }
                self.wfile.write(json.dumps(result).encode('utf-8'))

        except urllib.error.URLError as e:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            result = {
                'error': True,
                'message': f'Connection failed: {str(e.reason)}'
            }
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except Exception as e:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            result = {
                'error': True,
                'message': str(e)
            }
            self.wfile.write(json.dumps(result).encode('utf-8'))

    def log_message(self, format, *args):
        """Custom log format"""
        try:
            msg = str(args[0]) if args else ''
            if '/proxy' in msg:
                print(f"[Proxy] {msg}")
            elif msg.startswith('GET /'):
                pass  # Don't log static file requests
            else:
                print(f"[Server] {msg}")
        except Exception:
            pass  # Ignore logging errors


def main():
    handler = APIProxyHandler

    with http.server.HTTPServer(('', PORT), handler) as httpd:
        print(f"""
╔════════════════════════════════════════════════════════════╗
║                    API Explorer Server                      ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║   Server running at: http://localhost:{PORT}                 ║
║                                                            ║
║   Open this URL in your browser to use the API Explorer    ║
║                                                            ║
║   Press Ctrl+C to stop the server                          ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == '__main__':
    main()
