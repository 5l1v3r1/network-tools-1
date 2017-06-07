#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import json
from http.server import BaseHTTPRequestHandler
from urllib.request import urlopen
from urllib.parse import urlencode


APP_ID = "6036474"


class VKAuth(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress logging
        pass


    def do_GET(self):
        # Correctly answer
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        # Get token from code
        code = self.path.split('=')[1]
        VKAuth.access_token = self._get_token(code)


    def _get_token(self, code):
        params = [
            ("client_id", APP_ID),
            ("client_secret", "BcERuYfHHwLekLSXm3Dh"),
            ("redirect_uri", "http://localhost:31337/"),
            ("code", code)
        ]
        url = 'https://oauth.vk.com/access_token?' + urlencode(params)
        response = urlopen(url).read()
        return json.loads(response.decode())['access_token']
