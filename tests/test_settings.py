"""
QA tests for settings.py
"""

import pytest
from pydantic import ValidationError

from src.settings import (
    DatabaseSettings,
    EmailSettings,
    GPTSettings,
    ServerSettings,
)


def test_server_settings_defaults():
    s = ServerSettings()
    assert s.PORT == 8000
    assert str(s.IP_ADDRESS) == "localhost"
    assert s.DEBUG is False


def test_server_settings_env_overrides(monkeypatch):
    monkeypatch.setenv("PORT", "9999")
    monkeypatch.setenv("IP_ADDRESS", "0.0.0.0")
    monkeypatch.setenv("DEBUG", "True")
    s = ServerSettings()
    assert s.PORT == 9999
    assert str(s.IP_ADDRESS) == "0.0.0.0"
    assert s.DEBUG is True


def test_gpt_settings_defaults():
    s = GPTSettings()
    assert s.API_KEY == ""
    assert s.GPT_MODEL == "gpt-3.5-turbo"
    assert len(s.GPT_PROMPT) > 0


def test_database_settings_defaults():
    s = DatabaseSettings()
    assert s.DB_URI == ""


def test_database_settings_custom_uri(monkeypatch):
    monkeypatch.setenv("DB_URI", "mongodb://localhost:27017/test")
    s = DatabaseSettings()
    assert s.DB_URI == "mongodb://localhost:27017/test"


def test_email_settings_missing_required_raises():
    with pytest.raises(ValidationError):
        EmailSettings()


def test_email_settings_with_required_fields(monkeypatch):
    monkeypatch.setenv("EMAIL", "test@example.com")
    monkeypatch.setenv("EMAIL_PW", "secret")
    monkeypatch.setenv("EMAIL_RECEIVER", "recv@example.com")
    s = EmailSettings()
    assert str(s.EMAIL) == "test@example.com"
    assert s.EMAIL_PW == "secret"
    assert str(s.EMAIL_RECEIVER) == "recv@example.com"
    assert s.SMTP_SERVER == "smtp.gmail.com"
    assert s.SMTP_PORT == 587
    assert s.SUBJECT == "Surf Report"


def test_email_settings_invalid_email_raises(monkeypatch):
    monkeypatch.setenv("EMAIL", "not-an-email")
    monkeypatch.setenv("EMAIL_PW", "secret")
    monkeypatch.setenv("EMAIL_RECEIVER", "recv@example.com")
    with pytest.raises(ValidationError):
        EmailSettings()
