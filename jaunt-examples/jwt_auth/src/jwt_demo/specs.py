"""
JWT Authentication — Jaunt Example

A minimal JWT (JSON Web Token) implementation for
issuing and verifying HS256-signed bearer tokens.
"""

from __future__ import annotations

from datetime import timedelta

import jaunt
from pydantic import BaseModel


class Claims(BaseModel):
    """Decoded token payload."""

    sub: str  # subject (user id)
    iat: float  # issued-at (unix timestamp)
    exp: float  # expiry (unix timestamp)


@jaunt.magic()
def create_token(
    user_id: str,
    secret: str,
    *,
    ttl: timedelta = timedelta(hours=1),
) -> str:
    """
    Create an HS256-signed JWT.

    Structure: base64url(header) . base64url(payload) . base64url(signature)

    Header:  {"alg": "HS256", "typ": "JWT"}
    Payload: {"sub": user_id, "iat": <now>, "exp": <now + ttl>}

    - Use HMAC-SHA256 with `secret` as the key.
    - base64url encoding must omit padding ("=" characters).
    - Raise ValueError if user_id is empty or ttl is not positive.
    """
    raise RuntimeError("spec stub (generated at build time)")


@jaunt.magic(deps=[create_token, Claims])
def verify_token(token: str, secret: str) -> Claims:
    """
    Verify an HS256-signed JWT and return its claims.

    Contract:
    - Token must be exactly 3 base64url segments (no "=" padding): header.payload.signature
    - Signature must be HS256: HMAC-SHA256(secret, f"{header_b64}.{payload_b64}")
    - Validate structure strictly (JSON shape, required fields, types)

    Steps:
    1. Split token on "." — must have exactly 3 parts.
    2. Recompute HMAC-SHA256 over header.payload; compare to signature.
    3. Decode payload JSON into Claims.
    4. Check exp > current time.

    Errors:
    - Raise ValueError("malformed") if structure is wrong.
    - Raise ValueError("invalid signature") if HMAC doesn't match.
    - Raise ValueError("expired") if token has expired.
    """
    raise RuntimeError("spec stub (generated at build time)")


@jaunt.magic(deps=[create_token, verify_token])
def rotate_token(token: str, secret: str, *, ttl: timedelta = timedelta(hours=1)) -> str:
    """
    Verify an existing token and issue a fresh one for the same subject.

    - Verify the old token (propagate any errors).
    - Create a new token with the same user_id and a fresh ttl.
    - Return the new token string.
    """
    raise RuntimeError("spec stub (generated at build time)")
