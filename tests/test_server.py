"""
QA tests for server.py
Make sure pytest is installed: pip install pytest
Run pytest: pytest
"""

import subprocess
from http import HTTPStatus

from src import settings
from src.server import create_app


def test_routes():
    """
    Test that the routes are able to be retrieved
    /home, /help, /
    When a page is requested (GET)
    THEN check if the response is valid (200)
    """
    env = settings.ServerSettings()
    flask_app = create_app(env)
    OK = 200

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        response_help = test_client.get("/help")
        assert response_help.status_code == OK

        response_home = test_client.get("/home")
        assert response_home.status_code == OK

        response_root = test_client.get("/")
        assert response_root.status_code == OK


# ---- New tests below ----


def test_script_js_route(flask_test_client):
    """/script.js returns 200."""
    resp = flask_test_client.get("/script.js")
    assert resp.status_code == HTTPStatus.OK


def test_root_with_query_params(monkeypatch, flask_test_client):
    """Query params are parsed and passed to subprocess."""
    class DummyResult:
        stdout = "mocked output"
        stderr = ""

    def fake_run(*args, **kwargs):
        return DummyResult()

    monkeypatch.setattr(subprocess, "run", fake_run)
    resp = flask_test_client.get("/?location=santa_cruz&hide_wave")
    assert resp.status_code == HTTPStatus.OK
    assert b"mocked output" in resp.data


def test_root_subprocess_failure(monkeypatch):
    """Subprocess failure returns 500."""
    env = settings.ServerSettings()
    flask_app = create_app(env)

    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "cli.py", stderr="boom")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with flask_app.test_client() as client:
        resp = client.get("/")
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
