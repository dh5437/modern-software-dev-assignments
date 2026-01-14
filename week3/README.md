# Week 3 MCP Server: Slack Tools (STDIO + Streamable HTTP)

This MCP server exposes tools backed by the Slack API:
- `slack_get_authorize_url`
- `slack_exchange_code`
- `slack_read_channel_messages`
- `slack_send_channel_message`
- `slack_list_accessible_channels`

## Prerequisites
- Python 3.10+

## Setup

```bash
cd week3
```

Optional environment variables:

```bash
export SLACK_BOT_TOKEN="your_bot_token_here"
export SLACK_CLIENT_ID="your_client_id"
export SLACK_CLIENT_SECRET="your_client_secret"
export SLACK_REDIRECT_URI="https://your.app/slack/callback"
```

## Run (local STDIO server)

```bash
python server/stdio_server.py
```

## Run (Streamable HTTP server)

```bash
python server/main.py
```

Environment variables for HTTP:

- `MCP_HOST` (default: `127.0.0.1`)
- `MCP_PORT` (default: `8000`)
- `MCP_PATH` (default: `/mcp`)
- `MCP_MAX_BODY_BYTES` (default: `1000000`)
- `MCP_ALLOWED_ORIGINS` (comma-separated origin allowlist)
- `MCP_API_KEY` (optional; require `Authorization: Bearer <key>` or `X-API-Key`)

Example POST request:

```bash
curl -sS -X POST "http://127.0.0.1:8000/mcp" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

Notes:
- POST supports `Accept: application/json` or `Accept: text/event-stream` (SSE response).
- GET supports SSE (`Accept: text/event-stream`) for server-initiated messages (no messages are pushed yet).

## MCP client configuration (example)

Example Claude Desktop configuration entry:

```json
{
  "mcpServers": {
    "week3-slack": {
      "command": "python",
      "args": ["/absolute/path/to/week3/server/stdio_server.py"],
      "env": {
        "SLACK_BOT_TOKEN": "your_bot_token_here"
      }
    }
  }
}
```

## MCP Authorization (OAuth 2.1 + PKCE + Dynamic Registration)
This server implements MCP Authorization (Protocol Revision 2025-06-18) with:
- Protected resource metadata: `/.well-known/oauth-protected-resource`
- Authorization server metadata: `/.well-known/oauth-authorization-server`
- Dynamic client registration: `POST /register`
- Authorization Code + PKCE (S256)

Codex flow (high level):
1) Codex discovers `/.well-known/oauth-protected-resource` from `WWW-Authenticate`.
2) Codex fetches `/.well-known/oauth-authorization-server` for endpoints.
3) Codex registers a client via `POST /register`.
4) Codex redirects to `/oauth/authorize` for a code.
5) Codex exchanges code at `/oauth/token` for a Bearer token.
6) Codex calls `/mcp` with `Authorization: Bearer <access_token>`.

Notes:
- Tokens are in-memory only (server restart clears them).
- `resource` is `http://127.0.0.1:8000/mcp`.
- Access tokens are accepted only via the Authorization header (no query string).

## Tools
### Slack OAuth and scopes
Required scopes for the Slack tools:
- `channels:read`, `groups:read`, `im:read`, `mpim:read`
- `channels:history`, `groups:history`, `im:history`, `mpim:history`
- `chat:write`

Example OAuth flow:
1) Call `slack_get_authorize_url` and direct a user to the URL.
2) Receive a `code` on your redirect URL.
3) Call `slack_exchange_code` to obtain tokens.

### slack_get_authorize_url
Generate a Slack OAuth authorize URL.

Input:
- `redirect_uri` (string, optional; defaults to `SLACK_REDIRECT_URI`)
- `scopes` (string or array of strings, optional)
- `state` (string, optional)

Example:

```json
{
  "name": "slack_get_authorize_url",
  "arguments": {
    "scopes": ["channels:read", "chat:write"],
    "state": "request-123"
  }
}
```

### slack_exchange_code
Exchange a Slack OAuth code for tokens.

Input:
- `code` (string, required)
- `redirect_uri` (string, optional; defaults to `SLACK_REDIRECT_URI`)

Example:

```json
{
  "name": "slack_exchange_code",
  "arguments": {
    "code": "your_oauth_code"
  }
}
```

### slack_read_channel_messages
Read messages from a channel.

Input:
- `channel` (string, required)
- `limit` (int, 1-200)
- `cursor` (string, optional)
- `latest` (string, optional)
- `oldest` (string, optional)
- `inclusive` (boolean, optional)

Example:

```json
{
  "name": "slack_read_channel_messages",
  "arguments": {
    "channel": "C123",
    "limit": 50
  }
}
```

### slack_send_channel_message
Send a message to a channel.

Input:
- `channel` (string, required)
- `text` (string, required)
- `thread_ts` (string, optional)

Example:

```json
{
  "name": "slack_send_channel_message",
  "arguments": {
    "channel": "C123",
    "text": "Hello from MCP!"
  }
}
```

### slack_list_accessible_channels
List channels the bot is a member of.

Input:
- `limit` (int, 1-200)
- `cursor` (string, optional)
- `exclude_archived` (boolean, optional)
- `types` (string, optional)

Example:

```json
{
  "name": "slack_list_accessible_channels",
  "arguments": {
    "exclude_archived": true
  }
}
```

## Error handling and rate limits
- HTTP failures, timeouts, and unexpected responses are returned as tool errors.
- If the GitHub rate limit is low, the tool appends a warning to the output.

## Notes
- Logging is sent to stderr to keep STDIO output clean for MCP clients.
