import json
import os
import urllib.request
import urllib.error
import ssl
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def do_GET(self):
        env_api_key = os.environ.get('ZONOS_API_KEY', '')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        result = {'hasKey': True} if env_api_key else {'hasKey': False}
        self.wfile.write(json.dumps(result).encode())

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            request_data = json.loads(body)

            target_url = request_data.get('url')
            method = request_data.get('method', 'GET')
            headers = request_data.get('headers', {})
            payload = request_data.get('body')

            if not target_url:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': True, 'message': 'Missing URL'}).encode())
                return

            req_body = None
            if payload:
                if isinstance(payload, dict):
                    req_body = json.dumps(payload).encode('utf-8')
                else:
                    req_body = payload.encode('utf-8')

            # Use server-side API key if not provided by the client
            env_api_key = os.environ.get('ZONOS_API_KEY', '')
            if env_api_key and not headers.get('credentialToken'):
                headers['credentialToken'] = env_api_key

            req = urllib.request.Request(target_url, data=req_body, method=method)
            for key, value in headers.items():
                req.add_header(key, value)

            ctx = ssl.create_default_context()

            try:
                with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
                    response_body = response.read().decode('utf-8')
                    status_code = response.status

                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()

                    result = {
                        'status': status_code,
                        'statusText': response.reason,
                        'headers': dict(response.headers),
                        'body': response_body
                    }
                    self.wfile.write(json.dumps(result).encode())

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
                self.wfile.write(json.dumps(result).encode())

        except urllib.error.URLError as e:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            result = {'error': True, 'message': f'Connection failed: {str(e.reason)}'}
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            result = {'error': True, 'message': str(e)}
            self.wfile.write(json.dumps(result).encode())
