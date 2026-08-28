"""AsyncEnckcClient 비동기 클라이언트 단위 테스트."""

from __future__ import annotations

import httpx
import pytest

from enckc import AsyncEnckcClient
from enckc.exceptions import EnckcServerError

SAMPLE_ARTICLES = {
    "currentCount": 1,
    "totalCount": 1,
    "pageNo": 1,
    "pageSize": 20,
    "totalPage": 1,
    "items": [
        {
            "eid": "E0000002",
            "url": "https://encykorea.aks.ac.kr/Article/E0000002",
            "headword": "ㄱ",
            "origin": "",
            "headwordOrigin": "ㄱ",
            "field": "언어/문자",
            "primaryTypePartA": "개념",
            "primaryTypePartB": "",
            "primaryType": "개념",
            "secondaryType": "NONE",
            "contentsType": "개념",
            "era": "조선/조선 전기",
            "definition": "한글 자음에서 첫 번째로 등장하는 글자.",
            "summary": "",
            "body": "",
            "footNote": "",
            "reference": "",
            "writerInfo": "강신항",
            "lastModifiedTime": "2026-05-31T22:42:47.22",
            "headMID": "00000000-0000-0000-0000-000000000000",
            "headMedia": None,
            "articleAliases": [],
            "articleAttributes": [],
            "hashtags": [],
            "relatedArticles": [],
            "relatedMedias": [],
        }
    ],
}

SAMPLE_MEDIA = {
    "mid": "0bad737c-471b-4fd5-86cf-10774faeaaa7",
    "mediaType": "사진",
    "koglType": "KOGL1",
    "url": "https://devin.aks.ac.kr/image/0bad737c",
    "caption": "자최관",
    "description": "",
    "copyrightDisplay": "한국학중앙연구원",
}


@pytest.mark.asyncio
async def test_async_articles_and_search():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-api-key"] == "test-key"
        if request.url.path in {"/api/articles", "/api/articles/search"}:
            return httpx.Response(200, json=SAMPLE_ARTICLES)
        if request.url.path.startswith("/api/articles/"):
            return httpx.Response(200, json=SAMPLE_ARTICLES["items"][0])
        return httpx.Response(200, json=SAMPLE_ARTICLES)

    transport = httpx.MockTransport(handler)
    session = httpx.AsyncClient(transport=transport)

    async with AsyncEnckcClient(api_key="test-key", async_session=session) as client:
        res = await client.articles.list()
        assert res.total_count == 1
        assert res.items[0].headword == "ㄱ"

        res_s = await client.articles.search("한글")
        assert len(res_s.items) == 1

        detail = await client.articles.get("E0000002")
        assert detail is not None
        assert detail.headword == "ㄱ"


@pytest.mark.asyncio
async def test_async_medias():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/medias":
            return httpx.Response(
                200,
                json={
                    "currentCount": 1,
                    "totalCount": 1,
                    "pageNo": 1,
                    "pageSize": 20,
                    "totalPage": 1,
                    "items": [SAMPLE_MEDIA],
                },
            )
        if request.url.path == "/api/medias/0bad737c-471b-4fd5-86cf-10774faeaaa7":
            return httpx.Response(200, json=SAMPLE_MEDIA)
        return httpx.Response(204, content=b"")

    transport = httpx.MockTransport(handler)
    session = httpx.AsyncClient(transport=transport)

    async with AsyncEnckcClient(api_key="test-key", async_session=session) as client:
        medias = await client.medias.list()
        assert len(medias.items) == 1

        media = await client.medias.get("0bad737c-471b-4fd5-86cf-10774faeaaa7")
        assert media is not None
        assert media.caption == "자최관"
        assert media.metadata is not None
        assert media.metadata.provider == "encykorea"
        assert media.raw is not None

        not_found = await client.medias.get("NONE")
        assert not_found is None


@pytest.mark.asyncio
async def test_async_server_error_500():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, content=b"Internal Error")

    transport = httpx.MockTransport(handler)
    session = httpx.AsyncClient(transport=transport)

    async with AsyncEnckcClient(api_key="test-key", async_session=session) as client:
        with pytest.raises(EnckcServerError) as exc_info:
            await client.articles.list()
        assert exc_info.value.status_code == 500
        assert exc_info.value.retryable is True
