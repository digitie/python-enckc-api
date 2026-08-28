"""HTTP 클라이언트 전송 및 재시도 테스트."""

from __future__ import annotations

import httpx
import pytest

from enckc._http import (
    build_client,
    get_with_retries,
    raise_for_enckc_http_error,
    raise_for_enckc_network_error,
)
from enckc.exceptions import (
    EnckcAuthError,
    EnckcNotFoundError,
    EnckcRequestError,
    EnckcServerError,
)


def test_build_client():
    client = build_client(headers={"X-Custom": "val"})
    assert "User-Agent" in client.headers
    assert client.headers["X-Custom"] == "val"
    client.close()


def test_raise_for_http_error_mappings():
    req = httpx.Request("GET", "https://devin.aks.ac.kr:8080/api/articles")

    # 404
    resp_404 = httpx.Response(404, request=req)
    with pytest.raises(EnckcNotFoundError):
        raise_for_enckc_http_error(httpx.HTTPStatusError("404", request=req, response=resp_404))

    # 401
    resp_401 = httpx.Response(401, request=req)
    with pytest.raises(EnckcAuthError):
        raise_for_enckc_http_error(httpx.HTTPStatusError("401", request=req, response=resp_401))

    # 500
    resp_500 = httpx.Response(500, request=req)
    with pytest.raises(EnckcServerError):
        raise_for_enckc_http_error(httpx.HTTPStatusError("500", request=req, response=resp_500))

    # 429
    resp_429 = httpx.Response(429, request=req)
    with pytest.raises(EnckcRequestError) as exc_info:
        raise_for_enckc_http_error(httpx.HTTPStatusError("429", request=req, response=resp_429))
    assert exc_info.value.failure_kind == "rate_limit"


def test_raise_for_network_error():
    with pytest.raises(EnckcRequestError) as exc_info:
        raise_for_enckc_network_error(endpoint="/api/articles")
    assert exc_info.value.failure_kind == "network"
    assert exc_info.value.retryable is True


def test_get_with_retries_recovers():
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(500, request=request)
        return httpx.Response(200, json={"success": True}, request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    resp = get_with_retries(
        client, "https://devin.aks.ac.kr:8080/api/articles", retries=2, backoff_factor=0.01
    )
    assert resp.status_code == 200
    assert calls == 2
