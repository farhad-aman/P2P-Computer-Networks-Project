import json
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import redis

redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_client = redis.Redis(host=redis_host, port=6379)


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        if self.path == '/get-all':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            keys = redis_client.keys('*')
            response_data = {'keys': [key.decode('utf-8') for key in keys]}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        elif self.path.split('?')[0] == '/get':
            username = query_components.get('username', [''])[0]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            value = redis_client.get(username)
            response_data = {'value': value.decode('utf-8') if value else None}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self.send_error(404, 'Path not found', self.path)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        with self.rfile as file:
            body = file.read(content_length)
        if self.path == '/register':
            try:
                input_data = json.loads(body.decode())
                if 'username' not in input_data or 'ip' not in input_data:
                    raise ValueError('Missing username or IP')
                username = input_data['username']
                ip = input_data['ip']
                if not username or not ip:
                    raise ValueError('Empty username or IP')
                if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                    raise ValueError('Invalid IP address format.')
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                redis_client.set(username, ip)
                response_data = {'message': 'Registration successful'}
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
            except (json.JSONDecodeError, KeyError) as e:
                self.send_error(400, str(e))
            except ValueError as e:
                self.send_error(400, str(e))
        else:
            self.send_error(404, 'Path not found', self.path)


# Start the HTTP server
if __name__ == '__main__':
    port = 80
    host = ('', port)
    httpd = HTTPServer(host, RequestHandler)
    print("Server Started on Port:", port)
    httpd.serve_forever()

