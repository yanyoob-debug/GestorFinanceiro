from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import mimetypes, json, time
root = Path(__file__).resolve().parents[2] / 'frontend/dist/fintrack-frontend/browser'
control = Path(__file__).with_name('dre-ui-control.json')
class Handler(BaseHTTPRequestHandler):
    def do_GET(self): self.handle_request()
    def do_POST(self): self.handle_request()
    def do_PUT(self): self.handle_request()
    def do_DELETE(self): self.handle_request()
    def handle_request(self):
        if self.path.startswith('/api/'):
            config = json.loads(control.read_text()) if control.exists() else {}
            dre = self.path.startswith('/api/relatorios/dre')
            if dre and config.get('fail'):
                self.send_response(500); self.end_headers(); self.wfile.write(b'{}'); return
            body = self.rfile.read(int(self.headers.get('Content-Length',0))) or None
            headers = {k:v for k,v in self.headers.items() if k.lower() in ['authorization','content-type']}
            req = Request('http://localhost:8082' + self.path, data=body, headers=headers, method=self.command)
            try:
                with urlopen(req) as response: status=response.status; data=response.read(); content=response.headers.get('Content-Type','application/json')
            except HTTPError as error: status=error.code; data=error.read(); content='application/json'
            if dre and config.get('delay'): time.sleep(config['delay'])
        else:
            path=root / self.path.split('?')[0].lstrip('/')
            if not path.is_file(): path=root/'index.html'
            if root not in path.resolve().parents: self.send_error(404); return
            data=path.read_bytes(); content=mimetypes.guess_type(path.name)[0] or 'application/octet-stream'; status=200
            if path.suffix=='.js': data=data.replace(b'http://localhost:8080/api',b'/api')
        self.send_response(status); self.send_header('Content-Type',content); self.send_header('Content-Length',str(len(data))); self.end_headers()
        try: self.wfile.write(data)
        except (BrokenPipeError,ConnectionResetError): pass
    def log_message(self,*args): pass
print('DRE UI test server: http://localhost:4300',flush=True)
ThreadingHTTPServer(('localhost',4300),Handler).serve_forever()
