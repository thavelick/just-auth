#!/usr/bin/python3
import argparse
import hashlib
import http.server

from http.client import HTTPConnection, HTTPSConnection
from urllib.request import Request, urlopen
from urllib.parse import parse_qs, urlparse


PASSWORD = "super secret password"
SALT = "pretty secret salt"
PROXY_TO_URL = "http://localhost:8000"


class JustAuthHandler(http.server.BaseHTTPRequestHandler):
    # pylint: disable=invalid-name
    def do_GET(self):
        path = self.path

        if self.has_correct_auth_cookie():
            self.proxy_request("GET")
        elif path == "/login":
            self.show_file("login.html", "text/html")
        else:
            self.redirect("/login")

    # pylint: disable=invalid-name
    def do_POST(self):
        path = self.path

        if self.has_correct_auth_cookie():
            self.proxy_request("POST")
        elif path == "/login":
            self.process_login()
        else:
            self.redirect("/login")

    # pylint: disable=invalid-name
    def do_PUT(self):
        if self.has_correct_auth_cookie():
            self.proxy_request("PUT")
        else:
            self.redirect("/login")

    # pylint: disable=invalid-name
    def do_PATCH(self):
        if self.has_correct_auth_cookie():
            self.proxy_request("PATCH")
        else:
            self.redirect("/login")

    # pylint: disable=invalid-name
    def do_DELETE(self):
        if self.has_correct_auth_cookie():
            self.proxy_request("DELETE")
        else:
            self.redirect("/login")

    def proxy_request(self, method):
        parsed_url = urlparse(PROXY_TO_URL)

        conn = HTTPConnection(parsed_url.netloc)

        path = self.path
        headers = dict(self.headers)
        body = None

        if method in ("POST", "PUT", "PATCH"):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length else None

        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()

        self.send_response(response.status)
        for header, value in response.getheaders():
            self.send_header(header, value)
        self.end_headers()
        if method != "HEAD":
            self.wfile.write(response.read())

        conn.close()

    def show_file(self, path, content_type):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.show_text(content, content_type)

    def process_login(self):
        if self.headers["Content-Type"] != "application/x-www-form-urlencoded":
            self.show_text("Invalid content type", status_code=400)
            return

        content_length = int(self.headers["Content-Length"])
        post_data = parse_qs(self.rfile.read(content_length).decode("utf-8"))

        if "password" not in post_data:
            self.show_text("Missing password", status_code=400)
            return

        if post_data["password"][0] != PASSWORD:
            print("wrong password", PASSWORD, "!=", post_data["password"][0])
            self.redirect("/login")
            return

        token = hashlib.sha256((PASSWORD + SALT).encode("utf-8")).hexdigest()

        redirect_url = "/"
        if "redirect_url" in post_data:
            redirect_url = post_data["redirect_url"][0]

        self.send_response(302)
        self.send_header("Set-Cookie", f"just-auth-token={token}")
        self.send_header("Location", redirect_url)
        self.end_headers()

    def redirect(self, url):
        self.send_response(302)
        self.send_header("Location", url)
        self.end_headers()

    def show_text(self, text, content_type="text/plain", status_code=200):
        text = str.encode(text)
        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.send_header("Content-length", len(text))
        self.end_headers()
        self.wfile.write(text)

    def has_correct_auth_cookie(self):
        if "Cookie" not in self.headers:
            return False

        cookies = self.headers["Cookie"].split(";")
        for cookie in cookies:
            cookie = cookie.strip()
            if cookie.startswith("just-auth-token="):
                token = cookie[len("just-auth-token=") :]
                return (
                    token
                    == hashlib.sha256((PASSWORD + SALT).encode("utf-8")).hexdigest()
                )
        return False


parser = argparse.ArgumentParser()
parser.add_argument(
    "--port", help="port to listen on", type=int, default=8486, required=False
)
args = parser.parse_args()

with http.server.HTTPServer(("", args.port), JustAuthHandler) as httpd:
    print("serving at port", args.port)
    httpd.serve_forever()
