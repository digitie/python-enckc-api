"""httpx 기반 HTTP 클라이언트 및 재시도 헬퍼."""

from __future__ import annotations

import asyncio
import random
import time
from typing import Any, NoReturn

import httpx

from .exceptions import (
    EnckcAuthError,
    EnckcNotFoundError,
    EnckcRequestError,
    EnckcServerError,
)

RETRY_STATUS_CODES = frozenset({429, 500, 502, 503, 504})
DEFAULT_USER_AGENT = "python-enckc-api/0.1.0 (https://github.com/digitie/python-enckc-api)"


def _backoff_with_jitter(backoff_factor: float, attempt: int, max_backoff: float = 30.0) -> float:
    """동등 지터를 적용한 지수 백오프 대기 시간을 계산합니다."""
    base = min(backoff_factor * (2**attempt), max_backoff)
    half = base / 2
    return float(half + random.uniform(0, half))


def _retry_after_seconds(response: httpx.Response | None) -> float | None:
    if response is None:
        return None
    value = response.headers.get("Retry-After")
    if value is None:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        return None


def raise_for_enckc_http_error(
    exc: httpx.HTTPStatusError,
    *,
    endpoint: str | None = None,
    label: str = "Encykorea",
    detail: str = "",
) -> NoReturn:
    """HTTPStatusError를 매칭되는 Enckc 예외로 변환합니다."""

    status = exc.response.status_code if exc.response is not None else None
    suffix = f": {detail}" if detail else ""

    if status == 404:
        raise EnckcNotFoundError(
            f"{label} resource not found (HTTP 404){suffix}",
            endpoint=endpoint,
            status_code=status,
            failure_kind="not_found",
            retryable=False,
        ) from None

    if status in {401, 403}:
        raise EnckcAuthError(
            f"{label} authentication failed with HTTP {status}{suffix}",
            endpoint=endpoint,
            status_code=status,
            failure_kind="auth",
            retryable=False,
        ) from None

    if status and status >= 500:
        raise EnckcServerError(
            f"{label} server returned HTTP {status}{suffix}",
            endpoint=endpoint,
            status_code=status,
            failure_kind="server",
            retryable=True,
        ) from None

    if status == 429:
        raise EnckcRequestError(
            f"{label} request rate limited with HTTP {status}{suffix}",
            endpoint=endpoint,
            status_code=status,
            failure_kind="rate_limit",
            retryable=True,
        ) from None

    raise EnckcRequestError(
        f"{label} request failed with HTTP {status}{suffix}",
        endpoint=endpoint,
        status_code=status,
        failure_kind="request",
        retryable=False,
    ) from None


def raise_for_enckc_network_error(
    *,
    endpoint: str | None = None,
    label: str = "Encykorea",
) -> NoReturn:
    """httpx RequestError (타임아웃/연결 실패)를 EnckcRequestError로 변환합니다."""

    raise EnckcRequestError(
        f"{label} request failed due to network/timeout error",
        endpoint=endpoint,
        failure_kind="network",
        retryable=True,
    ) from None


def build_client(*, headers: dict[str, str] | None = None) -> httpx.Client:
    """기본 동기 httpx 클라이언트를 생성합니다."""
    default_headers = {"User-Agent": DEFAULT_USER_AGENT}
    if headers:
        default_headers.update(headers)
    return httpx.Client(follow_redirects=False, headers=default_headers)


def build_async_client(*, headers: dict[str, str] | None = None) -> httpx.AsyncClient:
    """기본 비동기 httpx 클라이언트를 생성합니다."""
    default_headers = {"User-Agent": DEFAULT_USER_AGENT}
    if headers:
        default_headers.update(headers)
    return httpx.AsyncClient(follow_redirects=False, headers=default_headers)


def get_with_retries(
    client: httpx.Client,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 10.0,
    retries: int = 3,
    backoff_factor: float = 0.3,
) -> httpx.Response:
    """재시도 로직이 적용된 동기 GET 요청을 수행합니다."""

    attempts = max(1, retries + 1)
    last_exc: httpx.HTTPError | None = None
    for attempt in range(attempts):
        retry_after: float | None = None
        try:
            response = client.get(url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            if not _should_retry_status(exc) or attempt >= attempts - 1:
                raise
            last_exc = exc
            retry_after = _retry_after_seconds(exc.response)
        except httpx.RequestError as exc:
            if attempt >= attempts - 1:
                raise
            last_exc = exc
        if retry_after is None:
            retry_after = _backoff_with_jitter(backoff_factor, attempt)
        time.sleep(retry_after)

    if last_exc is not None:  # pragma: no cover
        raise last_exc
    raise RuntimeError("HTTP request failed before it could be attempted")


async def async_get_with_retries(
    client: httpx.AsyncClient,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 10.0,
    retries: int = 3,
    backoff_factor: float = 0.3,
) -> httpx.Response:
    """재시도 로직이 적용된 비동기 GET 요청을 수행합니다."""

    attempts = max(1, retries + 1)
    last_exc: httpx.HTTPError | None = None
    for attempt in range(attempts):
        retry_after: float | None = None
        try:
            response = await client.get(url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            if not _should_retry_status(exc) or attempt >= attempts - 1:
                raise
            last_exc = exc
            retry_after = _retry_after_seconds(exc.response)
        except httpx.RequestError as exc:
            if attempt >= attempts - 1:
                raise
            last_exc = exc
        if retry_after is None:
            retry_after = _backoff_with_jitter(backoff_factor, attempt)
        await asyncio.sleep(retry_after)

    if last_exc is not None:  # pragma: no cover
        raise last_exc
    raise RuntimeError("HTTP request failed before it could be attempted")


def _should_retry_status(exc: httpx.HTTPStatusError) -> bool:
    return exc.response.status_code in RETRY_STATUS_CODES
