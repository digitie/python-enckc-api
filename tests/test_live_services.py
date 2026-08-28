"""실제 Encykorea OpenAPI 서버 호출 E2E 라이브 통합 테스트."""

from __future__ import annotations

import pytest

from enckc import AsyncEnckcClient, EnckcClient

# integration marker
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def live_client():
    client = EnckcClient.from_env()
    yield client
    client.close()


def test_live_articles_list(live_client: EnckcClient):
    resp = live_client.articles.list(page=1, page_size=20)
    assert resp.current_count > 0
    assert resp.total_count > 70000
    assert resp.page_no == 1
    assert len(resp.items) > 0
    assert resp.items[0].eid.startswith("E")


def test_live_articles_search(live_client: EnckcClient):
    resp = live_client.articles.search(query="세종", page=1, page_size=20)
    assert resp.total_count > 0
    assert len(resp.items) > 0
    assert any("세종" in item.headword for item in resp.items)


def test_live_article_detail_and_non_existent(live_client: EnckcClient):
    # 세조 (E0029849)
    article = live_client.articles.get("E0029849")
    assert article is not None
    assert article.eid == "E0029849"
    assert article.headword == "세조"
    assert "조선" in (article.era or "")
    assert article.body is not None and len(article.body) > 100

    # 존재하지 않는 EID (204 No Content -> None)
    missing = live_client.articles.get("E99999999")
    assert missing is None


def test_live_medias_list(live_client: EnckcClient):
    resp = live_client.medias.list(page=1, page_size=20)
    assert resp.current_count > 0
    assert resp.total_count > 70000
    assert len(resp.items) > 0
    assert resp.items[0].mid is not None


def test_live_medias_search(live_client: EnckcClient):
    resp = live_client.medias.search(query="훈민정음", page=1, page_size=20)
    assert resp.total_count > 0
    assert len(resp.items) > 0


def test_live_media_detail(live_client: EnckcClient):
    # First get a valid mid from list
    m_list = live_client.medias.list(page=1, page_size=20)
    assert len(m_list.items) > 0
    mid = m_list.items[0].mid

    media = live_client.medias.get(mid)
    assert media is not None
    assert media.mid == mid
    assert media.url is not None


@pytest.mark.asyncio
async def test_live_async_client():
    async with AsyncEnckcClient.from_env() as aclient:
        resp = await aclient.articles.search("한글", page=1, page_size=2)
        assert resp.total_count > 0
        assert len(resp.items) == 2

        article = await aclient.articles.get(resp.items[0].eid)
        assert article is not None
