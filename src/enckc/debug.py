"""디버그 런, 카탈로그 및 픽스처 생성 도우미."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .client import EnckcClient
from .metadata import make_response_metadata
from .models import ArticleDetail, ArticleListItem, MediaDetail, MediaItem, PaginatedResponse


@dataclass(frozen=True)
class ApiCatalogEntry:
    """OpenAPI 엔드포인트 카탈로그 항목."""

    endpoint_id: str
    label: str
    method: str
    path: str
    description: str
    sample_param: str
    guide_url: str = "https://encykorea.aks.ac.kr/Guide/OpenApiUse"


ENCKC_CATALOG: list[ApiCatalogEntry] = [
    ApiCatalogEntry(
        endpoint_id="articles_list",
        label="전체 항목 리스트",
        method="GET",
        path="/api/articles",
        description="한국민족문화대백과사전 전체 항목 리스트를 페이지 단위로 조회합니다.",
        sample_param="p=1&ps=20",
    ),
    ApiCatalogEntry(
        endpoint_id="articles_search",
        label="항목 검색",
        method="GET",
        path="/api/articles/search",
        description="키워드로 한국민족문화대백과사전 표제어 및 항목을 검색합니다.",
        sample_param="q=세종&p=1&ps=20",
    ),
    ApiCatalogEntry(
        endpoint_id="article_detail",
        label="항목 내용 상세",
        method="GET",
        path="/api/articles/{eid}",
        description=(
            "항목 EID(예: E0029849)로 본문, 해설, 각주, 속성, "
            "연관항목/미디어 상세 내용을 조회합니다."
        ),
        sample_param="eid=E0029849",
    ),
    ApiCatalogEntry(
        endpoint_id="medias_list",
        label="미디어 목록",
        method="GET",
        path="/api/medias",
        description=(
            "한국민족문화대백과사전 미디어(사진, 도면, 음원 등) "
            "전체 목록을 페이지 단위로 조회합니다."
        ),
        sample_param="p=1&ps=20",
    ),
    ApiCatalogEntry(
        endpoint_id="medias_search",
        label="미디어 검색",
        method="GET",
        path="/api/medias/search",
        description="키워드로 미디어를 검색합니다.",
        sample_param="q=훈민정음&p=1&ps=20",
    ),
    ApiCatalogEntry(
        endpoint_id="media_detail",
        label="미디어 내용 상세",
        method="GET",
        path="/api/medias/{mid}",
        description="미디어 MID로 미디어 상세 정보(URL, 캡션, 저작권, 설명 등)를 조회합니다.",
        sample_param="mid=0bad737c-471b-4fd5-86cf-10774faeaaa7",
    ),
]


def api_catalog(filter_query: str | None = None) -> list[ApiCatalogEntry]:
    """지원하는 한국민족문화대백과사전 API 카탈로그를 반환합니다."""

    if not filter_query:
        return list(ENCKC_CATALOG)
    query_norm = filter_query.strip().lower()
    return [
        entry
        for entry in ENCKC_CATALOG
        if query_norm in entry.endpoint_id.lower()
        or query_norm in entry.label.lower()
        or query_norm in entry.path.lower()
        or query_norm in entry.description.lower()
    ]


@dataclass(frozen=True)
class DebugRun:
    """디버그 및 픽스처 생성용 실행 결과 래퍼."""

    endpoint: str
    params: dict[str, Any]
    status_code: int
    raw_response: Any
    processed: Any


def run_debug(
    client: EnckcClient,
    endpoint_id: str,
    **kwargs: Any,
) -> DebugRun:
    """지정한 엔드포인트를 1회 요청으로 실행하고 디버그 정보를 반환합니다."""

    if endpoint_id == "articles_list":
        p = kwargs.get("p", 1)
        ps = kwargs.get("ps", 20)
        params = {"p": p, "ps": ps}
        raw, status = client._request_raw("/articles", params=params)
        model_data = raw or {
            "currentCount": 0,
            "totalCount": 0,
            "pageNo": p,
            "pageSize": ps,
            "totalPage": 0,
            "items": [],
        }
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint="/articles",
            request_params=params,
        )
        res = PaginatedResponse[ArticleListItem].model_validate(
            {**model_data, "metadata": metadata}
        )
        return DebugRun("/articles", params, status, raw, res.to_dict())

    if endpoint_id == "articles_search":
        q = kwargs.get("q", "세종")
        p = kwargs.get("p", 1)
        ps = kwargs.get("ps", 20)
        params = {"q": q, "p": p, "ps": ps}
        raw, status = client._request_raw("/articles/search", params=params)
        model_data = raw or {
            "currentCount": 0,
            "totalCount": 0,
            "pageNo": p,
            "pageSize": ps,
            "totalPage": 0,
            "items": [],
        }
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint="/articles/search",
            request_params=params,
        )
        res = PaginatedResponse[ArticleListItem].model_validate(
            {**model_data, "metadata": metadata}
        )
        return DebugRun("/articles/search", params, status, raw, res.to_dict())

    if endpoint_id == "article_detail":
        eid = kwargs.get("eid", "E0029849")
        path = f"/articles/{eid}"
        raw, status = client._request_raw(path)
        if raw is None or status == 204:
            return DebugRun(path, {"eid": eid}, status, raw, None)
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint=path,
            request_params={"eid": eid},
        )
        res_detail = ArticleDetail.model_validate({**raw, "raw": raw, "metadata": metadata})
        return DebugRun(path, {"eid": eid}, status, raw, res_detail.to_dict())

    if endpoint_id == "medias_list":
        p = kwargs.get("p", 1)
        ps = kwargs.get("ps", 20)
        params = {"p": p, "ps": ps}
        raw, status = client._request_raw("/medias", params=params)
        model_data = raw or {
            "currentCount": 0,
            "totalCount": 0,
            "pageNo": p,
            "pageSize": ps,
            "totalPage": 0,
            "items": [],
        }
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint="/medias",
            request_params=params,
        )
        res_list = PaginatedResponse[MediaItem].model_validate({**model_data, "metadata": metadata})
        return DebugRun("/medias", params, status, raw, res_list.to_dict())

    if endpoint_id == "medias_search":
        q = kwargs.get("q", "훈민정음")
        p = kwargs.get("p", 1)
        ps = kwargs.get("ps", 20)
        params = {"q": q, "p": p, "ps": ps}
        raw, status = client._request_raw("/medias/search", params=params)
        model_data = raw or {
            "currentCount": 0,
            "totalCount": 0,
            "pageNo": p,
            "pageSize": ps,
            "totalPage": 0,
            "items": [],
        }
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint="/medias/search",
            request_params=params,
        )
        res_search = PaginatedResponse[MediaItem].model_validate(
            {**model_data, "metadata": metadata}
        )
        return DebugRun("/medias/search", params, status, raw, res_search.to_dict())

    if endpoint_id == "media_detail":
        mid = kwargs.get("mid", "0bad737c-471b-4fd5-86cf-10774faeaaa7")
        path = f"/medias/{mid}"
        raw, status = client._request_raw(path)
        if raw is None or status == 204:
            return DebugRun(path, {"mid": mid}, status, raw, None)
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint=path,
            request_params={"mid": mid},
        )
        res_media = MediaDetail.model_validate({**raw, "raw": raw, "metadata": metadata})
        return DebugRun(path, {"mid": mid}, status, raw, res_media.to_dict())

    raise ValueError(f"Unknown endpoint_id: {endpoint_id}")
