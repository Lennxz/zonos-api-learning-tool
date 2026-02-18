import json
import os
import urllib.request
import ssl
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse


ALLOWED_ORIGIN = 'https://zonos-api-demo.vercel.app'


class handler(BaseHTTPRequestHandler):
    def _cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
        self.send_header('Access-Control-Allow-Methods', 'DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def do_DELETE(self):
        supabase_url = os.environ.get('SUPABASE_URL', '')
        supabase_key = os.environ.get('SUPABASE_SERVICE_KEY', '')

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        session_id = params.get('session', [None])[0]

        if not session_id:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': 'Missing session ID'}).encode())
            return

        if supabase_url and supabase_key:
            req = urllib.request.Request(
                f'{supabase_url}/rest/v1/webhook_events?session_id=eq.{session_id}',
                method='DELETE',
            )
            req.add_header('apikey', supabase_key)
            req.add_header('Authorization', f'Bearer {supabase_key}')

            ctx = ssl.create_default_context()
            try:
                urllib.request.urlopen(req, context=ctx, timeout=5)
            except Exception:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self._cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': 'Failed to clear events'}).encode())
                return

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({'ok': True}).encode())
