#!/usr/bin/env python3
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

SLACK_API_BASE = "https://slack.com/api"
SLACK_AUTH_BASE = "https://slack.com/oauth/v2"
USER_AGENT = "week3-mcp-server"
DEFAULT_TIMEOUT = 10
SLACK_DEFAULT_SCOPES = [
    "channels:read",
    "groups:read",
    "im:read",
    "mpim:read",
    "channels:history",
    "groups:history",
    "im:history",
    "mpim:history",
    "chat:write",
]

def json_rpc_error(code: int, message: str, req_id: Optional[Any]) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": code, "message": message},
    }


def json_rpc_result(result: Dict[str, Any], req_id: Optional[Any]) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _tool_error(message: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": message}], "isError": True}


def _tool_result(text: str) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def _slack_request(
    path: str,
    method: str,
    token: Optional[str],
    params: Optional[Dict[str, Any]] = None,
    body: Optional[Dict[str, Any]] = None,
    form_encoded: bool = False,
) -> Any:
    url = f"{SLACK_API_BASE}{path}"
    data = None
    headers = {"User-Agent": USER_AGENT}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if params:
        query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        url = f"{url}?{query}"
    if body is not None:
        if form_encoded:
            data = urllib.parse.urlencode(body).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload) if payload else {}
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8") if exc.fp else ""
        detail = body_text.strip() or exc.reason
        raise RuntimeError(f"Slack API error ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Slack API request failed: {exc.reason}") from exc


def _slack_bot_token() -> Optional[str]:
    return os.getenv("SLACK_BOT_TOKEN")


def _slack_oauth_env() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    return (
        os.getenv("SLACK_CLIENT_ID"),
        os.getenv("SLACK_CLIENT_SECRET"),
        os.getenv("SLACK_REDIRECT_URI"),
    )


def tool_slack_get_authorize_url(args: Dict[str, Any]) -> Dict[str, Any]:
    client_id, _, redirect_uri_env = _slack_oauth_env()
    if not client_id:
        return _tool_error("Missing SLACK_CLIENT_ID for OAuth")

    redirect_uri = args.get("redirect_uri") or redirect_uri_env
    if not redirect_uri:
        return _tool_error("Missing redirect_uri (pass argument or set SLACK_REDIRECT_URI)")

    scopes = args.get("scopes", SLACK_DEFAULT_SCOPES)
    if isinstance(scopes, list):
        scope_value = ",".join(scopes)
    elif isinstance(scopes, str):
        scope_value = scopes
    else:
        return _tool_error("scopes must be a list or string")

    params = {
        "client_id": client_id,
        "scope": scope_value,
        "redirect_uri": redirect_uri,
        "state": args.get("state"),
    }
    query = urllib.parse.urlencode({k: v for k, v in params.items() if v})
    return _tool_result(f"{SLACK_AUTH_BASE}/authorize?{query}")


def tool_slack_exchange_code(args: Dict[str, Any]) -> Dict[str, Any]:
    code = args.get("code")
    if not code or not isinstance(code, str):
        return _tool_error("Missing required string field: code")

    client_id, client_secret, redirect_uri_env = _slack_oauth_env()
    if not client_id or not client_secret:
        return _tool_error("Missing SLACK_CLIENT_ID or SLACK_CLIENT_SECRET for OAuth")

    redirect_uri = args.get("redirect_uri") or redirect_uri_env
    body = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
    }
    try:
        data = _slack_request("/oauth.v2.access", "POST", None, body=body, form_encoded=True)
    except RuntimeError as exc:
        return _tool_error(str(exc))

    if not data.get("ok", False):
        return _tool_error(f"Slack OAuth failed: {data.get('error', 'unknown_error')}")
    return _tool_result(json.dumps(data, indent=2, sort_keys=True))


def tool_slack_read_channel_messages(args: Dict[str, Any]) -> Dict[str, Any]:
    channel = args.get("channel")
    if not channel or not isinstance(channel, str):
        return _tool_error("Missing required string field: channel")

    token = _slack_bot_token()
    if not token:
        return _tool_error("Missing SLACK_BOT_TOKEN")

    limit = args.get("limit", 100)
    try:
        limit = min(max(int(limit), 1), 200)
    except (TypeError, ValueError):
        return _tool_error("limit must be an integer between 1 and 200")

    params = {
        "channel": channel,
        "limit": limit,
        "cursor": args.get("cursor"),
        "latest": args.get("latest"),
        "oldest": args.get("oldest"),
        "inclusive": args.get("inclusive"),
    }
    try:
        data = _slack_request("/conversations.history", "GET", token, params=params)
    except RuntimeError as exc:
        return _tool_error(str(exc))

    if not data.get("ok", False):
        return _tool_error(f"Slack API error: {data.get('error', 'unknown_error')}")

    response_metadata = data.get("response_metadata") or {}
    result = {
        "messages": data.get("messages", []),
        "has_more": data.get("has_more", False),
        "next_cursor": response_metadata.get("next_cursor"),
    }
    return _tool_result(json.dumps(result, indent=2, sort_keys=True))


def tool_slack_send_channel_message(args: Dict[str, Any]) -> Dict[str, Any]:
    channel = args.get("channel")
    text = args.get("text")
    if not channel or not isinstance(channel, str):
        return _tool_error("Missing required string field: channel")
    if not text or not isinstance(text, str):
        return _tool_error("Missing required string field: text")

    token = _slack_bot_token()
    if not token:
        return _tool_error("Missing SLACK_BOT_TOKEN")

    body = {
        "channel": channel,
        "text": text,
        "thread_ts": args.get("thread_ts"),
    }
    try:
        data = _slack_request("/chat.postMessage", "POST", token, body=body)
    except RuntimeError as exc:
        return _tool_error(str(exc))

    if not data.get("ok", False):
        return _tool_error(f"Slack API error: {data.get('error', 'unknown_error')}")

    result = {
        "channel": data.get("channel"),
        "ts": data.get("ts"),
        "message": data.get("message"),
    }
    return _tool_result(json.dumps(result, indent=2, sort_keys=True))


def tool_slack_list_accessible_channels(args: Dict[str, Any]) -> Dict[str, Any]:
    token = _slack_bot_token()
    if not token:
        return _tool_error("Missing SLACK_BOT_TOKEN")

    limit = args.get("limit", 100)
    try:
        limit = min(max(int(limit), 1), 200)
    except (TypeError, ValueError):
        return _tool_error("limit must be an integer between 1 and 200")

    params = {
        "limit": limit,
        "cursor": args.get("cursor"),
        "exclude_archived": args.get("exclude_archived", True),
        "types": args.get("types", "public_channel,private_channel"),
    }
    try:
        data = _slack_request("/conversations.list", "GET", token, params=params)
    except RuntimeError as exc:
        return _tool_error(str(exc))

    if not data.get("ok", False):
        return _tool_error(f"Slack API error: {data.get('error', 'unknown_error')}")

    channels = [channel for channel in data.get("channels", []) if channel.get("is_member")]
    response_metadata = data.get("response_metadata") or {}
    result = {
        "channels": channels,
        "next_cursor": response_metadata.get("next_cursor"),
    }
    return _tool_result(json.dumps(result, indent=2, sort_keys=True))


TOOLS = [
    {
        "name": "slack_get_authorize_url",
        "description": "Generate a Slack OAuth authorize URL for installing the app.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "redirect_uri": {"type": "string"},
                "scopes": {
                    "oneOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}]
                },
                "state": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "slack_exchange_code",
        "description": "Exchange a Slack OAuth code for tokens.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string"},
                "redirect_uri": {"type": "string"},
            },
            "required": ["code"],
            "additionalProperties": False,
        },
    },
    {
        "name": "slack_read_channel_messages",
        "description": "Read messages from a Slack channel using conversations.history.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "channel": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 200},
                "cursor": {"type": "string"},
                "latest": {"type": "string"},
                "oldest": {"type": "string"},
                "inclusive": {"type": "boolean"},
            },
            "required": ["channel"],
            "additionalProperties": False,
        },
    },
    {
        "name": "slack_send_channel_message",
        "description": "Send a message to a Slack channel using chat.postMessage.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "channel": {"type": "string"},
                "text": {"type": "string"},
                "thread_ts": {"type": "string"},
            },
            "required": ["channel", "text"],
            "additionalProperties": False,
        },
    },
    {
        "name": "slack_list_accessible_channels",
        "description": "List Slack channels the bot is a member of using conversations.list.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "minimum": 1, "maximum": 200},
                "cursor": {"type": "string"},
                "exclude_archived": {"type": "boolean"},
                "types": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
]


TOOL_HANDLERS = {
    "slack_get_authorize_url": tool_slack_get_authorize_url,
    "slack_exchange_code": tool_slack_exchange_code,
    "slack_read_channel_messages": tool_slack_read_channel_messages,
    "slack_send_channel_message": tool_slack_send_channel_message,
    "slack_list_accessible_channels": tool_slack_list_accessible_channels,
}


def _handle_initialize() -> Dict[str, Any]:
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {"listChanged": False}},
        "serverInfo": {"name": "week3-github-mcp", "version": "0.1.0"},
    }


def _handle_tools_list() -> Dict[str, Any]:
    return {"tools": TOOLS}


def _handle_tools_call(params: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(params, dict):
        return _tool_error("tools/call params must be an object")
    name = params.get("name")
    arguments = params.get("arguments") or {}
    if name not in TOOL_HANDLERS:
        return _tool_error(f"Unknown tool: {name}")
    if not isinstance(arguments, dict):
        return _tool_error("arguments must be an object")
    return TOOL_HANDLERS[name](arguments)


def process_request(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params")

    if method == "initialize":
        return json_rpc_result(_handle_initialize(), req_id)
    if method in {"initialized", "notifications/initialized"}:
        return None
    if method == "tools/list":
        return json_rpc_result(_handle_tools_list(), req_id)
    if method == "tools/call":
        return json_rpc_result(_handle_tools_call(params or {}), req_id)
    if method == "shutdown":
        return json_rpc_result({}, req_id)
    if method == "exit":
        return None

    return json_rpc_error(-32601, f"Method not found: {method}", req_id)


def collect_responses(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, dict):
        response = process_request(payload)
        if response:
            if response.get("id") is not None or "error" in response:
                return [response]
        return []
    if isinstance(payload, list):
        responses: List[Dict[str, Any]] = []
        for item in payload:
            if not isinstance(item, dict):
                responses.append(json_rpc_error(-32600, "Invalid Request", None))
                continue
            response = process_request(item)
            if response and (response.get("id") is not None or "error" in response):
                responses.append(response)
        return responses
    return [json_rpc_error(-32600, "Invalid Request", None)]


def payload_has_requests(payload: Any) -> bool:
    if isinstance(payload, dict):
        return "method" in payload
    if isinstance(payload, list):
        return any(isinstance(item, dict) and "method" in item for item in payload)
    return False
