import re
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

import httpx

PORT = 8000
REDIRECT_URI = f"http://localhost:{PORT}"
SCOPES = ["read", "trade", "openid"]

authorize_url = "https://my.tastytrade.com/auth.html"
token_url = "https://api.tastyworks.com/oauth/token"
client_id = ""
client_secret = ""


root_page = """
<!DOCTYPE html>
<html lang="en-us">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OAuth Setup</title>
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
          rel="stylesheet"
          integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH"
          crossorigin="anonymous">
  </head>
  <body>
    <div class="container position-absolute top-50 start-50 translate-middle"
         style="width: 400px">
      <form method="POST">
        <div class="row mb-3">
          <input type="text"
                 required
                 placeholder="Client ID"
                 name="client_id"
                 class="form-control">
        </div>
        <div class="row mb-3">
          <input type="password"
                 required
                 placeholder="Client Secret"
                 name="client_secret"
                 class="form-control">
        </div>
        <div class="row mb-3">
          <button type="submit" class="btn btn-success">Connect</button>
        </div>
      </form>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
            integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
            crossorigin="anonymous"></script>
  </body>
</html>
""".encode()


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        global client_id, client_secret
        content_length = int(self.headers["Content-Length"])
        raw = self.rfile.read(content_length)
        data = parse_qs(raw.decode("utf-8"))
        client_id = data["client_id"][0]
        client_secret = data["client_secret"][0]

        # Redirect to login page using API key submitted by user
        self.send_response(302)
        query_string = "&".join(
            [
                "response_type=code",
                f"redirect_uri={REDIRECT_URI}",
                f"client_id={data['client_id'][0]}",
                f"scope={' '.join(SCOPES)}",
            ]
        )
        url = f"{authorize_url}?{query_string}"
        self.send_header("Location", url)
        self.end_headers()

    def do_GET(self) -> None:
        global client_id, client_secret
        # Serve root page with sign in link
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(root_page)
        else:
            # Check if query path contains case insensitive "code="
            code_match = re.search(r"code=(.+)", self.path, re.I)
            if code_match and client_id and client_secret:
                user_auth_code = code_match[1]
                post_data = {
                    "grant_type": "authorization_code",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": REDIRECT_URI,
                    "code": user_auth_code,
                }
                response = httpx.post(token_url, data=post_data)
                token_access = response.json()
                refresh_token: str = token_access["refresh_token"]
                print(refresh_token)

                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(refresh_token.encode())


def login(is_test: bool = False) -> None:
    """
    Starts a local HTTP server and opens the browser to OAuth login.
    Designed for one-time use to get a refresh token.
    """
    global authorize_url, token_url
    if is_test:
        authorize_url = "https://cert-my.staging-tasty.works/auth.html"
        token_url = "https://api.cert.tastyworks.com/oauth/token"
    httpd = HTTPServer(("", PORT), RequestHandler)
    print(f"Opening url: {REDIRECT_URI}")
    webbrowser.open(REDIRECT_URI)
    httpd.serve_forever()
