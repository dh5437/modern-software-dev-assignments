import json
import urllib.parse
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "server"))
import mcp_core  # noqa: E402


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload
        self.headers = {}

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _decode_tool_payload(tool_result):
    payload = tool_result["content"][0]["text"]
    return json.loads(payload)


def test_slack_get_authorize_url(monkeypatch):
    monkeypatch.setenv("SLACK_CLIENT_ID", "client-123")
    monkeypatch.setenv("SLACK_REDIRECT_URI", "https://example.com/callback")

    result = mcp_core.tool_slack_get_authorize_url(
        {"scopes": ["channels:read", "chat:write"], "state": "abc"}
    )
    url = result["content"][0]["text"]
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)

    assert parsed.netloc == "slack.com"
    assert query["client_id"] == ["client-123"]
    assert query["redirect_uri"] == ["https://example.com/callback"]
    assert query["scope"] == ["channels:read,chat:write"]
    assert query["state"] == ["abc"]


def test_slack_exchange_code(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["data"] = request.data.decode("utf-8")
        return FakeResponse({"ok": True, "access_token": "xoxb-test"})

    monkeypatch.setenv("SLACK_CLIENT_ID", "client-123")
    monkeypatch.setenv("SLACK_CLIENT_SECRET", "secret-456")
    monkeypatch.setattr(mcp_core.urllib.request, "urlopen", fake_urlopen)

    result = mcp_core.tool_slack_exchange_code({"code": "auth-code"})
    payload = _decode_tool_payload(result)

    assert captured["url"].endswith("/oauth.v2.access")
    assert payload["access_token"] == "xoxb-test"
    body = urllib.parse.parse_qs(captured["data"])
    assert body["code"] == ["auth-code"]
    assert body["client_id"] == ["client-123"]
    assert body["client_secret"] == ["secret-456"]


def test_slack_read_channel_messages(monkeypatch):
    def fake_urlopen(request, timeout):
        assert "conversations.history" in request.full_url
        return FakeResponse(
            {
                "ok": True,
                "messages": [{"text": "hi"}],
                "has_more": True,
                "response_metadata": {"next_cursor": "cursor-1"},
            }
        )

    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-token")
    monkeypatch.setattr(mcp_core.urllib.request, "urlopen", fake_urlopen)

    result = mcp_core.tool_slack_read_channel_messages({"channel": "C123", "limit": 2})
    payload = _decode_tool_payload(result)

    assert payload["messages"] == [{"text": "hi"}]
    assert payload["has_more"] is True
    assert payload["next_cursor"] == "cursor-1"


def test_slack_list_accessible_channels(monkeypatch):
    def fake_urlopen(request, timeout):
        assert "conversations.list" in request.full_url
        return FakeResponse(
            {
                "ok": True,
                "channels": [
                    {"id": "C1", "is_member": True},
                    {"id": "C2", "is_member": False},
                ],
                "response_metadata": {"next_cursor": "cursor-2"},
            }
        )

    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-token")
    monkeypatch.setattr(mcp_core.urllib.request, "urlopen", fake_urlopen)

    result = mcp_core.tool_slack_list_accessible_channels({})
    payload = _decode_tool_payload(result)

    assert payload["channels"] == [{"id": "C1", "is_member": True}]
    assert payload["next_cursor"] == "cursor-2"
