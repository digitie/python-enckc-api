"""페이지네이션 헬퍼 및 순회 테스트."""

from __future__ import annotations

import pytest

from enckc import EnckcClient
from enckc.models import ArticleListItem, PaginatedResponse
from enckc.pagination import async_iter_pages, has_next_page, iter_pages, next_page_no


def _mock_page(page_no: int, total_pages: int = 3) -> PaginatedResponse[ArticleListItem]:
    return PaginatedResponse[ArticleListItem](
        currentCount=2,
        totalCount=total_pages * 2,
        pageNo=page_no,
        pageSize=2,
        totalPage=total_pages,
        items=[
            ArticleListItem(eid=f"E{page_no}_1", headword=f"항목_{page_no}_1"),
            ArticleListItem(eid=f"E{page_no}_2", headword=f"항목_{page_no}_2"),
        ],
    )


def test_has_next_page_and_next_page_no():
    page1 = _mock_page(1, total_pages=3)
    assert has_next_page(page1) is True
    assert next_page_no(page1) == 2

    page3 = _mock_page(3, total_pages=3)
    assert has_next_page(page3) is False
    assert next_page_no(page3) is None


def test_iter_pages():
    pages = list(iter_pages(lambda p, ps: _mock_page(p, total_pages=3), page_size=2))
    assert len(pages) == 3
    assert pages[0].page_no == 1
    assert pages[1].page_no == 2
    assert pages[2].page_no == 3


def test_iter_pages_max_items():
    pages = list(iter_pages(lambda p, ps: _mock_page(p, total_pages=3), page_size=2, max_items=3))
    assert len(pages) == 2


@pytest.mark.asyncio
async def test_async_iter_pages():
    async def fetch(p: int, ps: int) -> PaginatedResponse[ArticleListItem]:
        return _mock_page(p, total_pages=2)

    pages = [p async for p in async_iter_pages(fetch, page_size=2)]
    assert len(pages) == 2
    assert pages[1].page_no == 2


def test_iter_all_exact_max_items():
    client = EnckcClient(api_key="test-key")

    # mock articles.list to return pages of 20 items
    def mock_list(page: int = 1, page_size: int = 20):
        return PaginatedResponse[ArticleListItem](
            currentCount=20,
            totalCount=100,
            pageNo=page,
            pageSize=page_size,
            totalPage=5,
            items=[
                ArticleListItem(eid=f"E{page}_{i}", headword=f"항목_{page}_{i}") for i in range(20)
            ],
        )

    client.articles.list = mock_list  # type: ignore[assignment]
    items = list(client.articles.iter_all(page_size=20, max_items=5))
    # Must yield exactly 5 items, not 20!
    assert len(items) == 5
    assert items[0].eid == "E1_0"
    assert items[4].eid == "E1_4"
