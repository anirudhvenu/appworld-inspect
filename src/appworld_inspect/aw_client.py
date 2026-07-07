"""Minimal HTTP client for the AppWorld environment server.

Runs inside the sandbox container (stdlib only). Reads a JSON request from
stdin ({"path": ..., "method": ..., "payload": ...}), forwards it to the
AppWorld environment server on localhost, and writes the JSON response to
stdout.
"""

import json
import sys
import urllib.error
import urllib.request

SERVER_URL = "http://localhost:9000"
TIMEOUT_SECONDS = 600


def main() -> None:
    """Forward one JSON request from stdin to the environment server."""
    request = json.load(sys.stdin)
    url = SERVER_URL + request["path"]
    method = request.get("method", "POST")
    if method == "GET":
        http_request = urllib.request.Request(url)
    else:
        http_request = urllib.request.Request(
            url,
            data=json.dumps(request.get("payload", {})).encode(),
            headers={"Content-Type": "application/json"},
        )
    try:
        with urllib.request.urlopen(http_request, timeout=TIMEOUT_SECONDS) as response:
            sys.stdout.write(response.read().decode())
    except urllib.error.HTTPError as error:
        sys.stdout.write(
            json.dumps({"error": f"HTTP {error.code}", "detail": error.read().decode()})
        )
        sys.exit(1)
    except urllib.error.URLError as error:
        sys.stdout.write(
            json.dumps({"error": "unreachable", "detail": str(error.reason)})
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
