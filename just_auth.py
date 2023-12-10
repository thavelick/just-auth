#!/usr/bin/python3
import hashlib
import http.server
import os

from http.client import HTTPConnection
from urllib.parse import quote, parse_qs, urlparse

PASSWORD = os.environ.get("JUST_AUTH_PASSWORD", "super secret password")
SALT = os.environ.get("JUST_AUTH_SALT", "pretty secret salt")
PROXY_TO_URL = os.environ.get("JUST_AUTH_PROXY_TO_URL", "http://localhost:8000")
PORT = int(os.environ.get("JUST_AUTH_PORT", 8486))


class JustAuthHandler(http.server.BaseHTTPRequestHandler):
    # pylint: disable=invalid-name
    def do_GET(self):
        if self.has_correct_auth_cookie():
            self.proxy_request("GET")
            return

        path = self.path
        query_string_dict = {}
        if "?" in path:
            path, query_string = path.split("?", 1)
            query_string_dict = parse_qs(query_string)

        if path == "/login":
            self.show_login_form(query_string_dict.get("redirect_path", "")[0])
        else:
            self.redirect_to_login()

    # pylint: disable=invalid-name
    def do_POST(self):
        if self.has_correct_auth_cookie():
            self.proxy_request("POST")
            return

        if self.path == "/login":
            self.process_login()
            return

        self.redirect_to_login()

    # pylint: disable=invalid-name
    def do_PUT(self):
        self.proxy_or_redirect_to_login("PUT")

    # pylint: disable=invalid-name
    def do_PATCH(self):
        self.proxy_or_redirect_to_login("PATCH")

    # pylint: disable=invalid-name
    def do_DELETE(self):
        self.proxy_or_redirect_to_login("DELETE")

    def proxy_or_redirect_to_login(self, method):
        if self.has_correct_auth_cookie():
            self.proxy_request(method)
            return

        self.redirect_to_login()

    def redirect_to_login(self):
        self.redirect(f"/login?redirect_path={quote(self.path)}")

    def proxy_request(self, method):
        parsed_url = urlparse(PROXY_TO_URL)

        conn = HTTPConnection(parsed_url.netloc)

        path = self.path
        headers = dict(self.headers)
        body = None

        if method in ("POST", "PUT", "PATCH"):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length else None

        try:
            conn.request(method, path, body=body, headers=headers)
        except ConnectionError:
            self.show_text("Gateway Connection error", status_code=502)
            return

        response = conn.getresponse()

        self.send_response(response.status)
        for header, value in response.getheaders():
            self.send_header(header, value)
        self.end_headers()
        if method != "HEAD":
            self.wfile.write(response.read())

        conn.close()

    def show_login_form(self, redirect_path):
        with open("login.html", "r", encoding="utf-8") as f:
            content = f.read()

        content = content.replace("{redirect_path}", redirect_path)
        self.show_text(content, "text/html")

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
            self.show_text("Incorrect password", status_code=400)
            return

        token = hashlib.sha256((PASSWORD + SALT).encode("utf-8")).hexdigest()
        redirect_path = "/"
        if "redirect_path" in post_data:
            redirect_path = post_data["redirect_path"][0]
        if not redirect_path.startswith("/"):
            redirect_path = "/"

        self.send_response(302)

        self.send_header("Set-Cookie", f"just-auth-token={token}; Max-Age={7*24*60*60}")
        self.send_header("Location", redirect_path)
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


with http.server.HTTPServer(("", PORT), JustAuthHandler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
