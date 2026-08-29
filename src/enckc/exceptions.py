"""`enckc` 예외 계층."""

from __future__ import annotations

from typing import Literal

FailureKind = Literal[
    "not_found",
    "auth",
    "server",
    "rate_limit",
    "request",
    "network",
    "parse",
]


class EnckcError(Exception):
    """모든 `enckc` 예외의 기본 클래스."""

    def __init__(
        self,
        message: str = "",
        *,
        provider: str = "encykorea",
        endpoint: str | None = None,
        status_code: int | None = None,
        failure_kind: FailureKind | None = None,
        retryable: bool | None = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.endpoint = endpoint
        self.status_code = status_code
        self.failure_kind = failure_kind
        self.retryable = retryable

    @property
    def metadata(self) -> dict[str, object]:
        """비어 있지 않은 구조화 오류 metadata를 반환합니다."""

        values: dict[str, object | None] = {
            "provider": self.provider,
            "endpoint": self.endpoint,
            "status_code": self.status_code,
            "failure_kind": self.failure_kind,
            "retryable": self.retryable,
        }
        return {key: value for key, value in values.items() if value is not None}


class EnckcAuthError(EnckcError):
    """인증키가 잘못되었거나 만료되었거나 권한이 없을 때 발생합니다 (HTTP 401/403)."""


class EnckcNotFoundError(EnckcError):
    """요청한 리소스를 찾을 수 없을 때 발생합니다 (HTTP 404)."""


class EnckcRequestError(EnckcError):
    """요청이 잘못되었거나 API가 요청을 거부했을 때 발생합니다."""


class EnckcServerError(EnckcError):
    """API가 일시적인 서버 측 실패를 반환했을 때 발생합니다 (HTTP 5xx)."""


class EnckcParseError(EnckcError):
    """API 응답을 기대한 구조로 파싱할 수 없을 때 발생합니다."""
