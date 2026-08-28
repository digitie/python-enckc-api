"""예외 계층 및 메타데이터 테스트."""

from __future__ import annotations

from enckc.exceptions import (
    EnckcAuthError,
    EnckcError,
    EnckcNotFoundError,
    EnckcParseError,
    EnckcRequestError,
    EnckcServerError,
)


def test_exception_metadata():
    err = EnckcError(
        "오류 메시지",
        provider="encykorea",
        endpoint="/api/articles",
        status_code=401,
        failure_kind="auth",
        retryable=False,
    )
    meta = err.metadata
    assert meta["provider"] == "encykorea"
    assert meta["endpoint"] == "/api/articles"
    assert meta["status_code"] == 401
    assert meta["failure_kind"] == "auth"
    assert meta["retryable"] is False


def test_exception_hierarchy():
    assert issubclass(EnckcAuthError, EnckcError)
    assert issubclass(EnckcNotFoundError, EnckcError)
    assert issubclass(EnckcRequestError, EnckcError)
    assert issubclass(EnckcServerError, EnckcError)
    assert issubclass(EnckcParseError, EnckcError)
