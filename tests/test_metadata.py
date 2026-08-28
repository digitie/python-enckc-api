"""메타데이터 및 인증값 마스킹 보안 테스트."""

from __future__ import annotations

from enckc.metadata import (
    make_response_metadata,
    redact_credentials_in_text,
    redact_url_credentials,
    sanitize_request_params,
)


def test_sanitize_request_params_x_api_key():
    params = {
        "X-API-Key": "secret123",
        "x-api-key": "secret456",
        "x_api_key": "secret789",
        "xapikey": "secret000",
        "serviceKey": "secretAAA",
        "q": "검색어",
        "p": 1,
    }
    sanitized = sanitize_request_params(params)
    assert sanitized["X-API-Key"] == "***REDACTED***"
    assert sanitized["x-api-key"] == "***REDACTED***"
    assert sanitized["x_api_key"] == "***REDACTED***"
    assert sanitized["xapikey"] == "***REDACTED***"
    assert sanitized["serviceKey"] == "***REDACTED***"
    assert sanitized["q"] == "검색어"
    assert sanitized["p"] == 1


def test_redact_credentials_in_text():
    text = "Error calling API with X-API-Key: my-secret-key and service_key=secret-value"
    redacted = redact_credentials_in_text(text)
    assert "my-secret-key" not in redacted
    assert "secret-value" not in redacted
    assert "***REDACTED***" in redacted


def test_redact_url_credentials():
    url = "https://devin.aks.ac.kr:8080/api/articles?q=test&x-api-key=mykey&serviceKey=servkey"
    redacted = redact_url_credentials(url)
    assert "mykey" not in redacted
    assert "servkey" not in redacted
    assert (
        "x-api-key=%2A%2A%2AREDACTED%2A%2A%2A" in redacted or "x-api-key=***REDACTED***" in redacted
    )


def test_response_metadata_immutability():
    meta = make_response_metadata(
        provider="encykorea",
        endpoint="/articles",
        request_params={"X-API-Key": "mykey", "p": 1},
    )
    assert meta.request_params["X-API-Key"] == "***REDACTED***"
    assert meta.request_params["p"] == 1
    assert meta.provider == "encykorea"
