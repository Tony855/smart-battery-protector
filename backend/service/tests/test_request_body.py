import asyncio

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.request_body import read_limited_body


def make_request(chunks, headers=None, receive_override=None):
    messages = [
        {"type": "http.request", "body": chunk, "more_body": index < len(chunks) - 1}
        for index, chunk in enumerate(chunks)
    ]
    if not messages:
        messages = [{"type": "http.request", "body": b"", "more_body": False}]

    async def receive():
        if receive_override is not None:
            return await receive_override()
        return messages.pop(0)

    scope = {
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
        "method": "POST", "scheme": "http", "path": "/upload",
        "raw_path": b"/upload", "query_string": b"",
        "headers": [(key.lower().encode("latin-1"), value.encode("latin-1"))
                    for key, value in (headers or {}).items()],
        "client": ("test", 1234), "server": ("test", 80),
    }
    return Request(scope, receive)


def test_streaming_body_accepts_exact_limit_across_chunks():
    request = make_request([b"abc", b"de"])
    body = asyncio.run(read_limited_body(request, max_bytes=5, too_large_detail="too_large"))
    assert body == b"abcde"


def test_streaming_body_rejects_limit_plus_one():
    request = make_request([b"abc", b"def"])
    with pytest.raises(HTTPException) as error:
        asyncio.run(read_limited_body(request, max_bytes=5, too_large_detail="too_large"))
    assert error.value.status_code == 413
    assert error.value.detail == "too_large"


def test_content_length_rejects_before_consuming_body():
    async def unexpected_receive():
        raise AssertionError("body should not be read after oversized Content-Length")

    request = make_request([], headers={"content-length": "6"}, receive_override=unexpected_receive)
    with pytest.raises(HTTPException) as error:
        asyncio.run(read_limited_body(request, max_bytes=5, too_large_detail="too_large"))
    assert error.value.status_code == 413
