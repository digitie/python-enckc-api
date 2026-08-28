"""EnckcClient 동기 클라이언트 단위 테스트."""

from __future__ import annotations

import httpx
import pytest

from enckc import EnckcClient
from enckc.exceptions import EnckcAuthError

SAMPLE_ARTICLES_LIST = {
    "currentCount": 1,
    "totalCount": 100,
    "pageNo": 1,
    "pageSize": 20,
    "totalPage": 5,
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
            "writerInfo": "강신항(성균관대학교, 국어학)",
            "lastModifiedTime": "2026-05-31T22:42:47.22",
            "headMID": "5d2519e3-878b-47e6-bfd5-58e3c6cc0c8d",
            "headMedia": {
                "mid": "5d2519e3-878b-47e6-bfd5-58e3c6cc0c8d",
                "mediaType": "사진",
                "koglType": "KOGL1",
                "url": "https://devin.aks.ac.kr/image/5d2519e3-878b-47e6-bfd5-58e3c6cc0c8d?preset=orig",
                "caption": "훈민정음언해 / ㄱ",
                "description": "한글 자모의 첫째 글자.",
                "copyrightDisplay": "한국학중앙연구원",
            },
            "articleAliases": [{"word": "기역", "aliasType": "일반ː이칭"}],
            "articleAttributes": [{"groupName": "물품", "attrName": "재질", "attrValue": "나무"}],
            "hashtags": ["한글"],
            "relatedArticles": [],
            "relatedMedias": [],
        }
    ],
    "requestUrl": "/api/articles",
    "queryString": "?p=1&ps=20",
}

SAMPLE_ARTICLE_DETAIL = {
    "eid": "E0029849",
    "url": "https://encykorea.aks.ac.kr/Article/E0029849",
    "headword": "세조",
    "origin": "世祖",
    "headwordOrigin": "세조(世祖)",
    "field": "역사/조선시대사",
    "primaryTypePartA": "인물",
    "primaryTypePartB": "전통 인물",
    "primaryType": "인물/전통 인물",
    "secondaryType": "NONE",
    "contentsType": "인물/전통 인물",
    "era": "조선/조선 전기",
    "definition": "조선의 제7대(재위: 1455년~1468년) 왕.",
    "summary": "세조는 조선의 제7대 왕이다.",
    "body": "# 개설\n세조 실록 내용...",
    "footNote": "[^1]: 각주 내용",
    "reference": "- 『세종실록』",
    "writerInfo": "이재호",
    "lastModifiedTime": "2022-09-29T18:07:41.363",
    "headMID": "00000000-0000-0000-0000-000000000000",
    "headMedia": None,
    "articleAliases": [{"word": "수지(粹之)", "aliasType": "인물ː자"}],
    "articleAttributes": [
        {"groupName": "인물/전통 인물", "attrName": "출생 연도", "attrValue": "1417년"}
    ],
    "hashtags": [],
    "relatedArticles": [
        {
            "targetEID": "E0019665",
            "targetUrl": "https://encykorea.aks.ac.kr/Article/E0019665",
            "headword": "문종",
            "origin": "文宗",
            "headwordOrigin": "문종(文宗)",
            "field": "역사/조선시대사",
            "primaryTypePartA": "인물",
            "primaryTypePartB": "전통 인물",
            "primaryType": "인물/전통 인물",
            "secondaryType": "NONE",
            "contentsType": "인물/전통 인물",
            "era": "조선/조선 전기",
            "definition": "조선의 제5대 왕.",
            "writerProfile": "최승희",
            "headMID": "00000000-0000-0000-0000-000000000000",
            "headMedia": None,
        }
    ],
    "relatedMedias": [],
}

SAMPLE_MEDIA_ITEM = {
    "mid": "0bad737c-471b-4fd5-86cf-10774faeaaa7",
    "mediaType": "사진",
    "koglType": "KOGL1",
    "url": "https://devin.aks.ac.kr/image/0bad737c?preset=orig",
    "caption": "사례편람 / 자최관",
    "description": "설명",
    "copyrightDisplay": "한국학중앙연구원",
}

SAMPLE_MEDIAS_LIST = {
    "currentCount": 1,
    "totalCount": 50,
    "pageNo": 1,
    "pageSize": 20,
    "totalPage": 3,
    "items": [SAMPLE_MEDIA_ITEM],
    "requestUrl": "/api/medias",
    "queryString": "?p=1&ps=20",
}


def test_articles_list_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-api-key"] == "test-key"
        assert request.url.path == "/api/articles"
        assert request.url.params["p"] == "1"
        assert request.url.params["ps"] == "20"
        return httpx.Response(200, json=SAMPLE_ARTICLES_LIST)

    transport = httpx.MockTransport(handler)
    session = httpx.Client(transport=transport)

    with EnckcClient(api_key="test-key", session=session) as client:
        resp = client.articles.list(page=1, page_size=20)
        assert resp.total_count == 100
        assert len(resp.items) == 1
        assert resp.items[0].headword == "ㄱ"
        assert resp.items[0].head_media is not None
        assert resp.items[0].head_media.caption == "훈민정음언해 / ㄱ"


def test_articles_search_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/articles/search"
        assert request.url.params["q"] == "세종"
        return httpx.Response(200, json=SAMPLE_ARTICLES_LIST)

    transport = httpx.MockTransport(handler)
    session = httpx.Client(transport=transport)

    with EnckcClient(api_key="test-key", session=session) as client:
        resp = client.articles.search(query="세종")
        assert len(resp.items) == 1
        assert resp.items[0].eid == "E0000002"


def test_article_detail_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/articles/E0029849"
        return httpx.Response(200, json=SAMPLE_ARTICLE_DETAIL)

    transport = httpx.MockTransport(handler)
    session = httpx.Client(transport=transport)

    with EnckcClient(api_key="test-key", session=session) as client:
        article = client.articles.get("E0029849")
        assert article is not None
        assert article.headword == "세조"
        assert article.summary == "세조는 조선의 제7대 왕이다."
        assert len(article.related_articles) == 1
        assert article.related_articles[0].headword == "문종"


def test_article_detail_not_found_204():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(204, content=b"")

    transport = httpx.MockTransport(handler)
    session = httpx.Client(transport=transport)

    with EnckcClient(api_key="test-key", session=session) as client:
        article = client.articles.get("NONEXISTENT")
        assert article is None


def test_medias_list_and_search():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=SAMPLE_MEDIAS_LIST)

    transport = httpx.MockTransport(handler)
    session = httpx.Client(transport=transport)

    with EnckcClient(api_key="test-key", session=session) as client:
        resp_list = client.medias.list()
        assert resp_list.total_count == 50
        assert len(resp_list.items) == 1
        assert resp_list.items[0].caption == "사례편람 / 자최관"

        resp_search = client.medias.search("사례편람")
        assert len(resp_search.items) == 1


def test_media_detail_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/medias/0bad737c-471b-4fd5-86cf-10774faeaaa7"
        return httpx.Response(200, json=SAMPLE_MEDIA_ITEM)

    transport = httpx.MockTransport(handler)
    session = httpx.Client(transport=transport)

    with EnckcClient(api_key="test-key", session=session) as client:
        media = client.medias.get("0bad737c-471b-4fd5-86cf-10774faeaaa7")
        assert media is not None
        assert media.mid == "0bad737c-471b-4fd5-86cf-10774faeaaa7"
        assert media.media_type == "사진"
        assert media.metadata is not None
        assert media.metadata.provider == "encykorea"
        assert media.raw is not None


def test_auth_error_401():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"title": "Unauthorized", "status": 401})

    transport = httpx.MockTransport(handler)
    session = httpx.Client(transport=transport)

    with EnckcClient(api_key="bad-key", session=session) as client:
        with pytest.raises(EnckcAuthError) as exc_info:
            client.articles.list()
        assert exc_info.value.status_code == 401
        assert exc_info.value.failure_kind == "auth"
