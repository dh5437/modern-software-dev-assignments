#!/usr/bin/env python3
import asyncio
import base64
import hashlib
import json
import logging
import os
import secrets
import time
import urllib.parse
from http import HTTPStatus
from typing import Any, AsyncIterator, Dict, Iterable, Mapping, Optional, Set

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from pydantic import BaseModel, RootModel, ValidationError
from dotenv import load_dotenv

import mcp_core

load_dotenv()

DEFAULT_HTTP_PATH = os.getenv("MCP_PATH", "/mcp")
DEFAULT_HTTP_HOST = os.getenv("MCP_HOST", "127.0.0.1")


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


MAX_BODY_BYTES = _int_env("MCP_MAX_BODY_BYTES", 1_000_000)
DEFAULT_HTTP_PORT = _int_env("MCP_PORT", 8000)
OAUTH_CODE_TTL = _int_env("MCP_OAUTH_CODE_TTL", 600)
OAUTH_TOKEN_TTL = _int_env("MCP_OAUTH_TOKEN_TTL", 3600)

BASE_URL = "http://127.0.0.1:8000"
RESOURCE_URL = f"{BASE_URL}{DEFAULT_HTTP_PATH}"

logger = logging.getLogger("mcp-oauth")
logging.basicConfig(level=logging.INFO)

app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)


class JsonRpcPayload(RootModel[dict[str, Any] | list[Any]]):
    pass


AUTH_CODES: Dict[str, Dict[str, Any]] = {}
ACCESS_TOKENS: Dict[str, Dict[str, Any]] = {}
CLIENTS: Dict[str, Dict[str, Any]] = {}


class RegisterRequest(BaseModel):
    redirect_uris: list[str]


class RegisterResponse(BaseModel):
    client_id: str
    redirect_uris: list[str]
    token_endpoint_auth_method: str
    grant_types: list[str]
    response_types: list[str]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


def _parse_allowed_origins() -> Optional[Set[str]]:
    raw = os.getenv("MCP_ALLOWED_ORIGINS", "")
    if not raw:
        return None
    return {origin.strip() for origin in raw.split(",") if origin.strip()}


def _origin_allowed(origin: Optional[str], allowed: Optional[Set[str]]) -> bool:
    if origin is None:
        return True
    if allowed is not None:
        return origin in allowed
    parsed = urllib.parse.urlparse(origin)
    return parsed.hostname in {"localhost", "127.0.0.1"}


def _extract_bearer(headers: Mapping[str, str]) -> Optional[str]:
    auth_header = headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[len("Bearer ") :].strip()
    return None


def _prune_expired(store: Dict[str, Dict[str, Any]]) -> None:
    now = time.time()
    expired = []
    for key, value in store.items():
        expires_at = value.get("expires_at", 0)
        if expires_at <= now:
            expired.append(key)
    for key in expired:
        del store[key]


def _resource_or_default(resource: Optional[str]) -> str:
    return resource if resource else RESOURCE_URL


def _resource_ok(resource: str) -> bool:
    return resource == RESOURCE_URL


def _client_for_id(client_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not client_id:
        return None
    return CLIENTS.get(client_id)


def _redirect_uri_registered(client: Dict[str, Any], redirect_uri: Optional[str]) -> bool:
    if not redirect_uri:
        return False
    return redirect_uri in client.get("redirect_uris", [])


def _auth_ok(headers: Mapping[str, str]) -> bool:
    token = _extract_bearer(headers)
    token_prefix = (token or "")[:6]
    logger.debug("auth: bearer_present=%s token_prefix=%s", bool(token), token_prefix)
    if not token:
        return False
    _prune_expired(ACCESS_TOKENS)
    entry = ACCESS_TOKENS.get(token)
    if entry is None:
        logger.debug("auth: token_invalid prefix=%s", token_prefix)
        return False
    if entry.get("resource") != RESOURCE_URL:
        logger.debug("auth: resource_mismatch prefix=%s", token_prefix)
        return False
    logger.debug("auth: ok prefix=%s", token_prefix)
    return True


def _accept_ok(accept: str, allow_event_stream: bool = False) -> bool:
    # Accept가 비어 있으면 관대하게 허용 (많은 클라이언트가 생략함)
    if not accept:
        return True
    # 범용 accept 허용
    if "*/*" in accept:
        return True
    if "application/json" in accept:
        return True
    if allow_event_stream and "text/event-stream" in accept:
        return True
    return False



def _json_error(status: int, code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content=mcp_core.json_rpc_error(code, message, None))


def _sse_stream(responses: Iterable[dict[str, Any]]) -> Iterable[bytes]:
    for response in responses:
        data = json.dumps(response)
        yield f"data: {data}\n\n".encode("utf-8")


async def _sse_keepalive(request: Request, interval_seconds: float = 15.0) -> AsyncIterator[bytes]:
    yield b": connected\n\n"
    while True:
        if await request.is_disconnected():
            break
        await asyncio.sleep(interval_seconds)
        yield b": keep-alive\n\n"


async def _read_json_body(request: Request) -> Dict[str, Any]:
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


async def _read_form_encoded(request: Request) -> Dict[str, Any]:
    body = await request.body()
    parsed = urllib.parse.parse_qs(body.decode("utf-8"))
    return {key: values[0] for key, values in parsed.items() if values}


def _is_local_redirect_uri(redirect_uri: Optional[str]) -> bool:
    if not redirect_uri:
        return False
    parsed = urllib.parse.urlparse(redirect_uri)
    if parsed.scheme != "http":
        return False
    if parsed.hostname not in {"localhost", "127.0.0.1"}:
        return False
    return True


def _pkce_s256(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    encoded = base64.urlsafe_b64encode(digest).decode("utf-8")
    return encoded.rstrip("=")


def _unauthorized_response() -> Response:
    headers = {"WWW-Authenticate": f'Bearer resource_metadata="{BASE_URL}/.well-known/oauth-protected-resource"'}
    return Response(status_code=HTTPStatus.UNAUTHORIZED, headers=headers)


@app.post(DEFAULT_HTTP_PATH, response_model=None)
async def mcp_post(request: Request) -> Response:
    auth_header = request.headers.get("Authorization")
    logger.debug("mcp POST Authorization present=%s", bool(auth_header))
    auth_ok = _auth_ok(request.headers)
    logger.debug("mcp POST auth_ok=%s", auth_ok)
    if not auth_ok:
        return _unauthorized_response()
    if not _origin_allowed(request.headers.get("Origin"), _parse_allowed_origins()):
        return Response(status_code=HTTPStatus.FORBIDDEN)

    accept = request.headers.get("Accept", "")
    if not _accept_ok(accept, allow_event_stream=True):
        return Response(status_code=HTTPStatus.NOT_ACCEPTABLE)

    # length_header = request.headers.get("Content-Length")
    # if length_header is None:
    #     return _json_error(HTTPStatus.LENGTH_REQUIRED, -32600, "Missing Content-Length")
    # try:
    #     length = int(length_header)
    # except ValueError:
    #     return _json_error(HTTPStatus.BAD_REQUEST, -32600, "Invalid Content-Length")
    # if length > MAX_BODY_BYTES:
    #     return _json_error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, -32600, "Payload too large")

    body = await request.body()
    if len(body) > MAX_BODY_BYTES:
        return _json_error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, -32600, "Payload too large")
    try:
        payload = json.loads(body.decode("utf-8")) if body else {}
    except json.JSONDecodeError:
        return _json_error(HTTPStatus.BAD_REQUEST, -32700, "Parse error")

    try:
        payload = JsonRpcPayload.model_validate(payload).root
    except ValidationError:
        return _json_error(HTTPStatus.BAD_REQUEST, -32600, "Invalid Request")

    responses = mcp_core.collect_responses(payload)
    if not responses:
        if mcp_core.payload_has_requests(payload):
            return Response(status_code=HTTPStatus.ACCEPTED)
        return Response(status_code=HTTPStatus.ACCEPTED)

    if "text/event-stream" in accept:
        return StreamingResponse(_sse_stream(responses), media_type="text/event-stream")

    if len(responses) == 1:
        return JSONResponse(status_code=HTTPStatus.OK, content=responses[0])
    return JSONResponse(status_code=HTTPStatus.OK, content=responses)


@app.get(DEFAULT_HTTP_PATH, response_model=None)
async def mcp_get(request: Request) -> Response:
    auth_header = request.headers.get("Authorization")
    logger.debug("mcp GET Authorization present=%s", bool(auth_header))
    auth_ok = _auth_ok(request.headers)
    logger.debug("mcp GET auth_ok=%s", auth_ok)
    if not auth_ok:
        return _unauthorized_response()
    if not _origin_allowed(request.headers.get("Origin"), _parse_allowed_origins()):
        return Response(status_code=HTTPStatus.FORBIDDEN)

    accept = request.headers.get("Accept", "")
    if not _accept_ok(accept, allow_event_stream=True):
        return Response(status_code=HTTPStatus.NOT_ACCEPTABLE)

    headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    return StreamingResponse(
        _sse_keepalive(request),
        media_type="text/event-stream",
        headers=headers,
    )
    
@app.get("/.well-known/oauth-authorization-server", response_model=None)
async def oauth_metadata() -> Response:
    return JSONResponse(
        {
            "issuer": BASE_URL,
            "authorization_endpoint": f"{BASE_URL}/oauth/authorize",
            "token_endpoint": f"{BASE_URL}/oauth/token",
            "registration_endpoint": f"{BASE_URL}/register",
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code"],
            "code_challenge_methods_supported": ["S256"],
            "token_endpoint_auth_methods_supported": ["none"],
        }
    )


@app.get("/.well-known/oauth-protected-resource", response_model=None)
async def oauth_protected_resource() -> Response:
    return JSONResponse(
        {
            "resource": RESOURCE_URL,
            "authorization_servers": [BASE_URL],
        }
    )


@app.post("/register", response_model=None)
async def oauth_register(request: Request) -> Response:
    content_type = request.headers.get("Content-Type", "")
    if "application/json" not in content_type:
        logger.info("register failed: invalid_content_type")
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "invalid_request"})
    data = await _read_json_body(request)
    try:
        payload = RegisterRequest.model_validate(data)
    except ValidationError:
        logger.info("register failed: invalid_redirect_uris")
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "invalid_redirect_uri"})
    if not payload.redirect_uris or not all(_is_local_redirect_uri(uri) for uri in payload.redirect_uris):
        logger.info("register failed: redirect_uri_not_local")
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "invalid_redirect_uri"})

    logger.info("register redirect_uris=%s", payload.redirect_uris)
    client_id = secrets.token_urlsafe(16)
    CLIENTS[client_id] = {
        "redirect_uris": payload.redirect_uris,
        "created_at": time.time(),
        "token_endpoint_auth_method": "none",
    }
    response = RegisterResponse(
        client_id=client_id,
        redirect_uris=payload.redirect_uris,
        token_endpoint_auth_method="none",
        grant_types=["authorization_code"],
        response_types=["code"],
    )
    return JSONResponse(response.model_dump())


@app.get("/oauth/authorize", response_model=None)
async def oauth_authorize(request: Request) -> Response:
    params = request.query_params
    client_id = params.get("client_id")
    redirect_uri = params.get("redirect_uri")
    response_type = params.get("response_type")
    code_challenge = params.get("code_challenge")
    code_challenge_method = params.get("code_challenge_method")
    resource = params.get("resource")
    state = params.get("state")

    logger.info("oauth/authorize client_id=%s redirect_uri=%s resource=%s", client_id, redirect_uri, resource)

    client = _client_for_id(client_id)
    if client is None:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "invalid_client"})
    if response_type != "code":
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "unsupported_response_type"})
    if not _redirect_uri_registered(client, redirect_uri):
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "invalid_redirect_uri"})
    if code_challenge_method != "S256" or not code_challenge:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "invalid_request"})
    if resource is None:
        resource = RESOURCE_URL
    resource = _resource_or_default(resource)
    if not _resource_ok(resource):
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "invalid_resource"})

    code = secrets.token_urlsafe(24)
    AUTH_CODES[code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_challenge": code_challenge,
        "resource": resource,
        "expires_at": time.time() + OAUTH_CODE_TTL,
    }
    _prune_expired(AUTH_CODES)

    query = {"code": code}
    if state:
        query["state"] = state
    location = f"{redirect_uri}?{urllib.parse.urlencode(query)}"
    return RedirectResponse(url=location, status_code=HTTPStatus.FOUND)


@app.post("/oauth/token", response_model=None)
async def oauth_token(request: Request) -> Response:
    content_type = request.headers.get("Content-Type", "")
    if "application/x-www-form-urlencoded" not in content_type:
        logger.info("oauth/token failed: invalid_content_type")
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "invalid_request"})
    data = await _read_form_encoded(request)
    grant_type = data.get("grant_type")
    code = data.get("code")
    client_id = data.get("client_id")
    redirect_uri = data.get("redirect_uri")
    code_verifier = data.get("code_verifier")
    resource = _resource_or_default(data.get("resource"))

    if grant_type != "authorization_code":
        logger.info("oauth/token failed: unsupported_grant_type")
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "unsupported_grant_type"})
    client = _client_for_id(client_id)
    if client is None:
        logger.info("oauth/token failed: invalid_client")
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "invalid_client"})
    if not _redirect_uri_registered(client, redirect_uri):
        logger.info("oauth/token failed: invalid_redirect_uri")
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "invalid_redirect_uri"})
    if not isinstance(code, str) or not code or not isinstance(code_verifier, str) or not code_verifier:
        logger.info("oauth/token failed: invalid_request")
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "invalid_request"})

    _prune_expired(AUTH_CODES)
    entry = AUTH_CODES.pop(code, None)
    if entry is None or entry["client_id"] != client_id or entry["redirect_uri"] != redirect_uri:
        logger.info("oauth/token failed: invalid_grant")
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "invalid_grant"})
    if entry["resource"] != resource:
        logger.info("oauth/token failed: invalid_resource")
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "invalid_resource"})
    if not _resource_ok(resource):
        logger.info("oauth/token failed: invalid_resource")
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "invalid_resource"})
    if _pkce_s256(code_verifier) != entry["code_challenge"]:
        logger.info("oauth/token failed: invalid_grant (pkce)")
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": "invalid_grant"})

    access_token = secrets.token_urlsafe(32)
    ACCESS_TOKENS[access_token] = {
        "client_id": client_id,
        "resource": resource,
        "expires_at": time.time() + OAUTH_TOKEN_TTL,
    }

    logger.info("oauth/token success client_id=%s resource=%s", client_id, resource)
    response = TokenResponse(
        access_token=access_token,
        expires_in=OAUTH_TOKEN_TTL,
    )
    return JSONResponse(response.model_dump())


@app.get("/callback", response_model=None)
async def oauth_callback(request: Request) -> Response:
    params = request.query_params
    code = params.get("code", "")
    state = params.get("state", "")
    body = {
        "message": "Authorization complete. You can close this window.",
        "code": code,
        "state": state,
    }
    return JSONResponse(body)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=DEFAULT_HTTP_HOST,
        port=DEFAULT_HTTP_PORT,
        log_level="info",
        access_log=True,
    )
