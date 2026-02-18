import json
import os
from http.server import BaseHTTPRequestHandler

ALLOWED_ORIGIN = 'https://zonos-api-demo.vercel.app'


class handler(BaseHTTPRequestHandler):
    def _cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store')
        self._cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({
            'supabaseUrl': os.environ.get('SUPABASE_URL', ''),
            'supabaseAnonKey': os.environ.get('SUPABASE_ANON_KEY', ''),
        }).encode())
