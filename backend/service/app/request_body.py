"""Bounded streaming reads for untrusted HTTP request bodies."""
from __future__ import annotations

from fastapi import HTTPException, Request


async def read_limited_body(
    request: Request,
    *,
    max_bytes: int,
    too_large_detail: str,
) -> bytes:
    """Read at most max_bytes and reject oversized bodies before buffering them whole."""
    if max_bytes < 0:
        raise ValueError("max_bytes must be non-negative")

    declared_length = request.headers.get("content-length")
    if declared_length is not None:
        try:
            if int(declared_length) > max_bytes:
                raise HTTPException(status_code=413, detail=too_large_detail)
        except ValueError:
            # Continue with the streaming limit if a malformed value reaches the app.
            pass

    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > max_bytes:
            raise HTTPException(status_code=413, detail=too_large_detail)
        body.extend(chunk)
    return bytes(body)
