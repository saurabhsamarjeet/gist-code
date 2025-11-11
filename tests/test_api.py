import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json
import responses
import pytest
from main import app

# sample GitHub gists payload (simplified)
SAMPLE_GISTS = [
    {
        "id": "1",
        "html_url": "https://gist.github.com/1",
        "description": "Example gist 1",
        "public": True,
        "files": {"file1.txt": {"filename": "file1.txt"}},
        "created_at": "2020-01-01T00:00:00Z",
        "updated_at": "2020-01-01T00:00:00Z"
    },
    {
        "id": "2",
        "html_url": "https://gist.github.com/2",
        "description": "Example gist 2",
        "public": True,
        "files": {"hello.py": {"filename": "hello.py"}},
        "created_at": "2020-02-01T00:00:00Z",
        "updated_at": "2020-02-01T00:00:00Z"
    }
]

GITHUB_URL = "https://api.github.com/users/octocat/gists"

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as c:
        yield c

@responses.activate
def test_get_octocat_gists(client):
    # Mock GitHub API response
    responses.add(
        responses.GET,
        GITHUB_URL,
        json=SAMPLE_GISTS,
        status=200
    )

    resp = client.get("/octocat")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["source"] == "github"
    gists = data["gists"]
    assert isinstance(gists, list)
    assert len(gists) == 2
    # check fields we expect
    assert gists[0]["id"] == "1"
    assert "file1.txt" in gists[0]["files"]
