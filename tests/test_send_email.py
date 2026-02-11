"""
QA tests for send_email.py

send_email.py runs EmailSettings() at import time, which fails with the
default .env (invalid email addresses). We must set valid env vars before
importing the module, then reload it for each test to get a clean state.
"""

import importlib
import subprocess
from unittest.mock import Mock, patch

import pytest

# Valid email env vars needed for EmailSettings() at import time
_EMAIL_ENV = {
    "EMAIL": "test@example.com",
    "EMAIL_PW": "secret",
    "EMAIL_RECEIVER": "recv@example.com",
    "SMTP_SERVER": "smtp.gmail.com",
    "SMTP_PORT": "587",
    "COMMAND": "localhost:8000",
    "SUBJECT": "Surf Report",
}


@pytest.fixture(autouse=True)
def _set_email_env(monkeypatch):
    """Set valid email env vars so EmailSettings() succeeds on import."""
    for key, val in _EMAIL_ENV.items():
        monkeypatch.setenv(key, val)


def _reload_send_email():
    """Force-(re)import src.send_email with current env vars."""
    import src.send_email
    importlib.reload(src.send_email)
    return src.send_email


def test_send_email_success():
    """Success path: curl succeeds, SMTP sends."""
    mod = _reload_send_email()

    mock_smtp_instance = Mock()
    mock_smtp_context = Mock()
    mock_smtp_context.__enter__ = Mock(return_value=mock_smtp_instance)
    mock_smtp_context.__exit__ = Mock(return_value=False)

    curl_result = Mock()
    curl_result.returncode = 0
    curl_result.stdout = "Wave Height: 4ft"

    with (
        patch.object(mod, "subprocess") as mock_subproc,
        patch("smtplib.SMTP", return_value=mock_smtp_context),
    ):
        mock_subproc.run.return_value = curl_result
        mod.send_user_email()

        mock_subproc.run.assert_called_once()
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(
            "test@example.com", "secret"
        )
        mock_smtp_instance.sendmail.assert_called_once()


def test_send_email_curl_failure():
    """Curl failure raises CalledProcessError."""
    mod = _reload_send_email()

    with patch.object(mod, "subprocess") as mock_subproc:
        mock_subproc.run.side_effect = subprocess.CalledProcessError(
            1, "curl", stderr="fail"
        )
        mock_subproc.CalledProcessError = subprocess.CalledProcessError
        with pytest.raises(subprocess.CalledProcessError):
            mod.send_user_email()


def test_send_email_smtp_failure():
    """SMTP auth failure raises."""
    mod = _reload_send_email()

    curl_result = Mock()
    curl_result.returncode = 0
    curl_result.stdout = "Wave Height: 4ft"

    mock_smtp_instance = Mock()
    mock_smtp_instance.starttls.return_value = None
    mock_smtp_instance.login.side_effect = Exception("Auth failed")
    mock_smtp_context = Mock()
    mock_smtp_context.__enter__ = Mock(return_value=mock_smtp_instance)
    mock_smtp_context.__exit__ = Mock(return_value=False)

    with (
        patch.object(mod, "subprocess") as mock_subproc,
        patch("smtplib.SMTP", return_value=mock_smtp_context),
    ):
        mock_subproc.run.return_value = curl_result
        with pytest.raises(Exception, match="Auth failed"):
            mod.send_user_email()
