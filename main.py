from flask import Flask, jsonify, request
import requests
import os
import time
from threading import Lock

app = Flask(__name__)

GITHUB_API_BASE = "https://api.github.com"
# Simple in-memory cache (username -> (timestamp, data))
CACHE = {}
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "30"))  # optional caching
CACHE_LOCK = Lock()

def fetch_gists_from_github(username):
    url = f"{GITHUB_API_BASE}/users/{username}/gists"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "gists-proxy/1.0"}
    # Respect optional GitHub token (for higher rate limits)
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()

def summarize_gist(gist):
    # Return a compact, safe representation of a gist
    files = list(gist.get("files", {}).keys())
    return {
        "id": gist.get("id"),
        "url": gist.get("html_url"),
        "description": gist.get("description"),
        "public": gist.get("public", True),
        "files": files,
        "created_at": gist.get("created_at"),
        "updated_at": gist.get("updated_at")
    }

@app.route("/<username>", methods=["GET"])
def get_user_gists(username):
    # Basic validation
    username = username.strip()
    if not username:
        return jsonify({"error": "username required"}), 400

    # Check cache
    now = time.time()
    with CACHE_LOCK:
        entry = CACHE.get(username)
        if entry:
            ts, data = entry
            if now - ts < CACHE_TTL_SECONDS:
                return jsonify({"source": "cache", "gists": data})

    try:
        raw = fetch_gists_from_github(username)
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else 500
        # If user not found, forward 404
        if status == 404:
            return jsonify({"error": "user not found"}), 404
        return jsonify({"error": "github api error", "detail": str(e)}), status
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "upstream request failed", "detail": str(e)}), 502

    summarized = [summarize_gist(g) for g in raw]

    with CACHE_LOCK:
        CACHE[username] = (now, summarized)

    return jsonify({"source": "github", "gists": summarized})

if __name__ == "__main__":
    # For local dev only. In container we'll use gunicorn.
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
