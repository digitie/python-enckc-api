"""공통 파싱 및 데이터 변환 도우미."""

from __future__ import annotations

from typing import Any


def str_or_none(value: Any) -> str | None:
    """빈 문자열이 아니면 문자열로 변환하고, None 또는 빈 문자열이면 None을 반환합니다."""

    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def int_or_none(value: Any) -> int | None:
    """정수로 변환하고, 변환 불가능하면 None을 반환합니다."""

    if value is None:
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def float_or_none(value: Any) -> float | None:
    """부동소수점 숫자로 변환하고, 변환 불가능하면 None을 반환합니다."""

    if value is None:
        return None
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None
