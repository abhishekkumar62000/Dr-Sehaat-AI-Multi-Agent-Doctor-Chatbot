from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import re
import uuid

HOST = '0.0.0.0'
PORT = 5000

DOCTORS = [
    {"key": "general_physician", "label": "General Physician", "description": "General health and wellness"},
    {"key": "cardiologist", "label": "Cardiologist", "description": "Heart-related concerns"},
    {"key": "dermatologist", "label": "Dermatologist", "description": "Skin-related concerns"}
]

SESSIONS = {}

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        data = json.dumps(obj).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == '/api/health' or path == '/api/health/':
            self._send_json({'success': True, 'status': 'ok'})
            return
        if path == '/api/doctors':
            self._send_json({'success': True, 'data': {'doctors': DOCTORS, 'default': 'general_physician'}})
            return
        # Unknown
        self._send_json({'success': False, 'error': 'Not found'}, status=404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length).decode('utf-8') if length else ''
        data = {}
        try:
            if body:
                data = json.loads(body)
        except Exception:
            pass

        if path == '/api/chat/new-session':
            session_id = str(uuid.uuid4())
            SESSIONS[session_id] = {'messages': []}
            initial = 'Hello, I am Dr. Sehaat. How can I assist you today? (This is a mock response)'
            resp = {'success': True, 'data': {'session_id': session_id, 'initial_message': initial}}
            self._send_json(resp)
            return

        if path == '/api/chat/send':
            session_id = data.get('session_id')
            message = data.get('message', '')
            doctor_role = data.get('doctor_role', 'general_physician')
            if not session_id or session_id not in SESSIONS:
                self._send_json({'success': False, 'error': 'Invalid session_id'}, status=400)
                return
            # Very simple echo-like response
            assistant = f"(Mock {doctor_role}) I received: {message}"
            is_emergency = False
            # crude emergency detection
            low = message.lower()
            if any(k in low for k in ['chest pain', 'shortness of breath', 'severe bleeding']):
                is_emergency = True
                assistant = "⚠️ This sounds like an emergency. Please contact local emergency services immediately."
            SESSIONS[session_id]['messages'].append({'role': 'patient', 'content': message})
            SESSIONS[session_id]['messages'].append({'role': 'assistant', 'content': assistant, 'is_emergency': is_emergency})
            resp = {'success': True, 'data': {'assistant_response': assistant, 'is_emergency': is_emergency}}
            self._send_json(resp)
            return

        m = re.match(r'^/api/chat/close-session/([0-9a-fA-F\-]+)$', path)
        if m:
            sid = m.group(1)
            SESSIONS.pop(sid, None)
            self._send_json({'success': True})
            return

        self._send_json({'success': False, 'error': 'Not found'}, status=404)

if __name__ == '__main__':
    print(f"Starting mock backend on http://{HOST}:{PORT} ...")
    server = HTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down mock backend')
        server.server_close()
