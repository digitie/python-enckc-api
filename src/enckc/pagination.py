"""한국민족문화대백과사전 OpenAPI 페이지네이션 도우미."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable, Iterator, Mapping
from typing import Any, TypeVar

from ._parsing import int_or_none
from .models import PaginatedResponse

T = TypeVar("T")


def has_next_page(response: PaginatedResponse[Any] | Mapping[str, Any]) -> bool:
    """응답에 다음 페이지가 있는지 확인합니다."""

    if isinstance(response, PaginatedResponse):
        page_no = response.page_no
        page_size = response.page_size
        total_count = response.total_count
    else:
        page_no = _int_from_dict(response, "pageNo", default=1)
        page_size = _int_from_dict(response, "pageSize", default=0)
        total_count = _int_from_dict(response, "totalCount", default=0)

    if page_no < 1 or page_size < 1 or total_count < 1:
        return False
    return page_no * page_size < total_count


def next_page_no(response: PaginatedResponse[Any] | Mapping[str, Any]) -> int | None:
    """다음 페이지 번호를 반환하고, 마지막 페이지이면 `None`을 반환합니다."""

    if not has_next_page(response):
        return None
    if isinstance(response, PaginatedResponse):
        return response.page_no + 1
    return _int_from_dict(response, "pageNo", default=1) + 1


def iter_pages(
    fetch_page: Callable[[int, int], PaginatedResponse[T]],
    *,
    page_size: int = 20,
    start_page: int = 1,
    max_pages: int = 100,
    max_items: int | None = None,
) -> Iterator[PaginatedResponse[T]]:
    """페이지를 순회하며 `PaginatedResponse[T]`를 생성합니다."""

    if start_page < 1:
        raise ValueError("start_page must be >= 1")
    if page_size < 1:
        raise ValueError("page_size must be >= 1")
    if max_pages < 1:
        raise ValueError("max_pages must be >= 1")
    if max_items is not None and max_items < 1:
        raise ValueError("max_items must be >= 1")

    page_no = start_page
    pages_seen = 0
    items_seen = 0

    while pages_seen < max_pages:
        page_resp = fetch_page(page_no, page_size)
        yield page_resp

        pages_seen += 1
        items_seen += len(page_resp.items)
        if max_items is not None and items_seen >= max_items:
            return

        next_page = next_page_no(page_resp)
        if next_page is None:
            return
        page_no = next_page


async def async_iter_pages(
    afetch_page: Callable[[int, int], Awaitable[PaginatedResponse[T]]],
    *,
    page_size: int = 20,
    start_page: int = 1,
    max_pages: int = 100,
    max_items: int | None = None,
) -> AsyncIterator[PaginatedResponse[T]]:
    """비동기로 페이지를 순회하며 `PaginatedResponse[T]`를 생성합니다."""

    if start_page < 1:
        raise ValueError("start_page must be >= 1")
    if page_size < 1:
        raise ValueError("page_size must be >= 1")
    if max_pages < 1:
        raise ValueError("max_pages must be >= 1")
    if max_items is not None and max_items < 1:
        raise ValueError("max_items must be >= 1")

    page_no = start_page
    pages_seen = 0
    items_seen = 0

    while pages_seen < max_pages:
        page_resp = await afetch_page(page_no, page_size)
        yield page_resp

        pages_seen += 1
        items_seen += len(page_resp.items)
        if max_items is not None and items_seen >= max_items:
            return

        next_page = next_page_no(page_resp)
        if next_page is None:
            return
        page_no = next_page


def _int_from_dict(body: Mapping[str, Any], key: str, *, default: int) -> int:
    val = int_or_none(body.get(key))
    return val if val is not None else default
