import json
import os
import urllib.request
import urllib.error
import ssl
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse


class handler(BaseHTTPRequestHandler):
    def _cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def do_POST(self):
        """Receive webhook events from Zonos and store in Supabase."""
        supabase_url = os.environ.get('SUPABASE_URL', '')
        supabase_key = os.environ.get('SUPABASE_SERVICE_KEY', '')

        # Parse session ID from query string
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        session_id = params.get('session', [None])[0]

        if not session_id:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': 'Missing session ID'}).encode())
            return

        # Read the POST body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b'{}'

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {'raw': body.decode('utf-8', errors='replace')}

        # Extract event type from common webhook formats
        event_type = (
            payload.get('event')
            or payload.get('type')
            or payload.get('event_type')
            or 'unknown'
        )

        # Capture useful headers
        headers_dict = {}
        for key in ['content-type', 'user-agent', 'x-zonos-signature',
                     'x-webhook-id', 'x-forwarded-for']:
            val = self.headers.get(key)
            if val:
                headers_dict[key] = val

        # Get source IP
        source_ip = (
            self.headers.get('x-forwarded-for', '').split(',')[0].strip()
            or self.headers.get('x-real-ip', '')
            or ''
        )

        # Insert into Supabase
        if supabase_url and supabase_key:
            row = {
                'session_id': session_id,
                'event_type': event_type,
                'payload': payload,
                'headers': headers_dict,
                'source_ip': source_ip,
            }

            req = urllib.request.Request(
                f'{supabase_url}/rest/v1/webhook_events',
                data=json.dumps(row).encode('utf-8'),
                method='POST',
            )
            req.add_header('apikey', supabase_key)
            req.add_header('Authorization', f'Bearer {supabase_key}')
            req.add_header('Content-Type', 'application/json')
            req.add_header('Prefer', 'return=minimal')

            ctx = ssl.create_default_context()
            try:
                urllib.request.urlopen(req, context=ctx, timeout=5)
            except Exception:
                pass  # Always return 200 to prevent Zonos retries

        # Always return 200
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({'ok': True, 'session': session_id}).encode())
