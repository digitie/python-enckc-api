"""요청 메타데이터 및 인증값 보안 보호 도우미."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import BaseModel, ConfigDict, Field

SENSITIVE_KEY_NAMES = frozenset(
    {
        "apikey",
        "api_key",
        "servicekey",
        "service_key",
        "authkey",
        "auth_key",
        "xapikey",
        "x-api-key",
        "x_api_key",
    }
)


def sanitize_request_params(params: dict[str, Any] | None) -> dict[str, Any]:
    """로그/메타데이터에 남길 수 있도록 인증 파라미터를 안전하게 마스킹합니다."""

    if not params:
        return {}
    sanitized: dict[str, Any] = {}
    for key, value in params.items():
        key_str = str(key)
        key_normalized = key_str.lower().replace("-", "").replace("_", "")
        if key_normalized in SENSITIVE_KEY_NAMES or key_str.lower() in SENSITIVE_KEY_NAMES:
            sanitized[key_str] = "***REDACTED***"
        else:
            sanitized[key_str] = value
    return sanitized


def redact_credentials_in_text(text: str) -> str:
    """텍스트 내의 인증키 패턴을 마스킹합니다."""

    if not text:
        return text
    # X-API-Key: ... 또는 x-api-key=... 형태 마스킹
    redacted = re.sub(
        r"(?i)(x-?api-?key\s*[:=]\s*)([^\s&,;]+)",
        r"\1***REDACTED***",
        text,
    )
    # service_key=, auth_key=, api_key= 형태 마스킹
    redacted = re.sub(
        r"(?i)(service_?key|auth_?key|api_?key)=([^&\s]+)",
        r"\1=***REDACTED***",
        redacted,
    )
    return redacted


def redact_url_credentials(url: str) -> str:
    """URL의 쿼리 파라미터에서 민감한 인증키를 마스킹합니다."""

    if not url:
        return url
    split = urlsplit(url)
    if not split.query:
        return url
    pairs = parse_qsl(split.query, keep_blank_values=True)
    sanitized_pairs = []
    for k, v in pairs:
        norm = k.lower().replace("-", "").replace("_", "")
        if norm in SENSITIVE_KEY_NAMES or k.lower() in SENSITIVE_KEY_NAMES:
            sanitized_pairs.append((k, "***REDACTED***"))
        else:
            sanitized_pairs.append((k, v))
    new_query = urlencode(sanitized_pairs)
    return urlunsplit((split.scheme, split.netloc, split.path, new_query, split.fragment))


class ResponseMetadata(BaseModel):
    """불변 응답 메타데이터 모델."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    provider: str = "encykorea"
    endpoint: str | None = None
    request_params: dict[str, Any] = Field(default_factory=dict)
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def make_response_metadata(
    *,
    provider: str = "encykorea",
    endpoint: str | None = None,
    request_params: dict[str, Any] | None = None,
) -> ResponseMetadata:
    """인증 파라미터가 마스킹된 ResponseMetadata 인스턴스를 생성합니다."""

    return ResponseMetadata(
        provider=provider,
        endpoint=endpoint,
        request_params=sanitize_request_params(request_params),
        fetched_at=datetime.now(timezone.utc),
    )
