"""Run: python server.py (Python 3.11+). No pip install required."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from planner import ROOT, load_data, graph, route, plan

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            url = urlparse(self.path)
            if url.path in ('/', '/style.css', '/app.js'):
                name = 'index.html' if url.path == '/' else url.path[1:]
                body = (ROOT / 'static' / name).read_bytes()
                mime = {'html':'text/html', 'css':'text/css', 'js':'text/javascript'}[name.rsplit('.',1)[1]]
            elif url.path in ('/api/data', '/api/route', '/api/plan'):
                data = load_data(); q = {k:v[0] for k,v in parse_qs(url.query).items()}
                if url.path == '/api/data': result = data
                else:
                    g = graph(data, q.get('accessible','1') == '1', float(q.get('speed','0.8')), float(q.get('wait','1')))
                    if url.path == '/api/route':
                        result = route(g, q['source'], q['target'], q.get('metric','seconds'))
                    else: result = plan(data, g, q.get('metric','seconds'), int(q.get('cart','2')), float(q.get('handling','120')))
                body = json.dumps(result, ensure_ascii=False).encode(); mime = 'application/json'
            else:
                self.send_error(404); return
            self.send_response(200); self.send_header('Content-Type', mime+'; charset=utf-8')
            self.send_header('Cache-Control','no-store'); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
        except (ValueError, KeyError, OSError) as e:
            body = json.dumps({'error':str(e)}, ensure_ascii=False).encode()
            self.send_response(400); self.send_header('Content-Type','application/json; charset=utf-8'); self.end_headers(); self.wfile.write(body)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--port', type=int, default=8000); args = parser.parse_args()
    load_data()
    print(f'Evergreen demo: http://localhost:{args.port}', flush=True)
    ThreadingHTTPServer(('0.0.0.0', args.port), Handler).serve_forever()
