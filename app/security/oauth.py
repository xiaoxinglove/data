from __future__ import annotations

import os
import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated, cast
from urllib.parse import parse_qs

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
    SecurityScopes,
)

ALLOWED_SCOPES = {
    "health:read",
    "chat:use",
    "documents:write",
    "enterprise:write",
}
ISSUER = "forestry-mvp"
AUDIENCE = "forestry-api"

basic = HTTPBasic(auto_error=False)
bearer = HTTPBearer(auto_error=False)


def _configuration() -> tuple[str, str, str]:
    client_id = os.environ.get("OAUTH_CLIENT_ID", "")
    client_secret = os.environ.get("OAUTH_CLIENT_SECRET", "")
    jwt_secret = os.environ.get("OAUTH_JWT_SECRET", "")
    if not client_id or not client_secret or len(jwt_secret) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OAuth 服务未配置",
        )
    return client_id, client_secret, jwt_secret


async def token_endpoint(
    request: Request,
    credentials: Annotated[HTTPBasicCredentials | None, Depends(basic)],
) -> dict[str, str | int]:
    client_id, client_secret, jwt_secret = _configuration()
    if credentials is None or not (
        secrets.compare_digest(credentials.username, client_id)
        and secrets.compare_digest(credentials.password, client_secret)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="客户端认证失败",
            headers={"WWW-Authenticate": "Basic"},
        )

    parameters = parse_qs((await request.body()).decode("utf-8"))
    if parameters.get("grant_type") != ["client_credentials"]:
        raise HTTPException(status_code=400, detail="unsupported_grant_type")
    requested = set(parameters.get("scope", [""])[0].split())
    if not requested <= ALLOWED_SCOPES:
        raise HTTPException(status_code=400, detail="invalid_scope")

    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "iss": ISSUER,
            "aud": AUDIENCE,
            "sub": client_id,
            "iat": now,
            "exp": now + timedelta(minutes=15),
            "scope": " ".join(sorted(requested)),
        },
        jwt_secret,
        algorithm="HS256",
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 900,
        "scope": " ".join(sorted(requested)),
    }


def require_token(
    security_scopes: SecurityScopes,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> str:
    if credentials is None:
        raise _unauthorized(security_scopes.scope_str)
    _, _, jwt_secret = _configuration()
    try:
        payload = cast(
            dict[str, object],
            jwt.decode(
                credentials.credentials,
                jwt_secret,
                algorithms=["HS256"],
                issuer=ISSUER,
                audience=AUDIENCE,
            ),
        )
    except jwt.PyJWTError as error:
        raise _unauthorized(security_scopes.scope_str) from error

    subject = payload.get("sub")
    granted_value = payload.get("scope", "")
    if not isinstance(subject, str) or not isinstance(granted_value, str):
        raise _unauthorized(security_scopes.scope_str)
    granted = set(granted_value.split())
    if not set(security_scopes.scopes) <= granted:
        raise HTTPException(status_code=403, detail="权限不足")
    return subject


def _unauthorized(scope: str) -> HTTPException:
    challenge = "Bearer" if not scope else f'Bearer scope="{scope}"'
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效或缺失的访问令牌",
        headers={"WWW-Authenticate": challenge},
    )
