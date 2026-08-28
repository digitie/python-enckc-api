"""인증키 정규화 및 .env 로더 테스트."""

from __future__ import annotations

from pathlib import Path

import pytest

from enckc._credentials import (
    env_names_for_gateway,
    load_local_env,
    normalize_api_key,
)


def test_normalize_api_key():
    assert normalize_api_key("  abc\n def \t ") == "abcdef"
    with pytest.raises(ValueError):
        normalize_api_key("   ")


def test_env_names_for_gateway():
    assert "ENCKC_API_KEY" in env_names_for_gateway("enckc")
    assert "ENCKC_API_KEY" in env_names_for_gateway("encykorea")
    with pytest.raises(ValueError):
        env_names_for_gateway("invalid")


def test_load_local_env(tmp_path: Path):
    env_file = tmp_path / ".env.local"
    env_file.write_text("ENCKC_API_KEY=test-secret-key\n# Comment\nFOO=bar", encoding="utf-8")

    loaded = load_local_env(start=tmp_path)
    assert loaded["ENCKC_API_KEY"] == "test-secret-key"
    assert loaded["FOO"] == "bar"
