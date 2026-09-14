"""한국민족문화대백과사전(Encykorea) OpenAPI 클라이언트."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable, Mapping
from typing import Any, TypeVar, cast
from urllib.parse import quote

import httpx
from pydantic import BaseModel, ValidationError

from ._credentials import ENCKC_ENV_NAMES, first_env_value, normalize_api_key
from ._http import (
    build_client,
    get_with_retries,
    raise_for_enckc_http_error,
    raise_for_enckc_network_error,
)
from ._ratelimit import AsyncTokenBucket
from .catalog import ApiDefinition, get_api_catalog_entry, get_api_definition
from .debug import DebugRun, debug_error, redact_sensitive
from .exceptions import EnckcNotFoundError, EnckcParseError
from .metadata import make_response_metadata, sanitize_request_params
from .models import (
    ArticleDetail,
    ArticleListItem,
    MediaDetail,
    MediaItem,
    PaginatedResponse,
)
from .pagination import iter_pages

DEFAULT_BASE_URL = "https://devin.aks.ac.kr:8080/api"
T = TypeVar("T")
ModelT = TypeVar("ModelT", bound=BaseModel)


def _validate_or_raise(model: type[ModelT], payload: dict[str, Any], *, endpoint: str) -> ModelT:
    """응답 페이로드를 모델로 검증하고, 실패 시 EnckcParseError로 변환합니다."""
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise EnckcParseError(
            str(exc),
            endpoint=endpoint,
            failure_kind="parse",
            retryable=False,
        ) from exc








class ArticlesService:
    """백과사전 항목(Article) 비동기 서비스 파사드."""

    def __init__(self, client: EnckcClient) -> None:
        self._client = client

    async def list(
        self, *, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[ArticleListItem]:
        """비동기로 전체 항목 리스트를 조회합니다."""
        params = {"p": page, "ps": page_size}
        raw, _ = await self._client._request_raw("/articles", params=params)
        if raw is None:
            raw = {
                "currentCount": 0,
                "totalCount": 0,
                "pageNo": page,
                "pageSize": page_size,
                "totalPage": 0,
                "items": [],
            }
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint="/articles",
            request_params=params,
        )
        return _validate_or_raise(
            PaginatedResponse[ArticleListItem], {**raw, "metadata": metadata}, endpoint="/articles"
        )

    async def search(
        self, query: str, *, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[ArticleListItem]:
        """비동기로 항목을 키워드 검색합니다."""
        params = {"q": query, "p": page, "ps": page_size}
        raw, _ = await self._client._request_raw("/articles/search", params=params)
        if raw is None:
            raw = {
                "currentCount": 0,
                "totalCount": 0,
                "pageNo": page,
                "pageSize": page_size,
                "totalPage": 0,
                "items": [],
            }
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint="/articles/search",
            request_params=params,
        )
        return _validate_or_raise(
            PaginatedResponse[ArticleListItem],
            {**raw, "metadata": metadata},
            endpoint="/articles/search",
        )

    async def get(self, eid: str) -> ArticleDetail | None:
        """비동기로 항목 상세 내용을 조회합니다."""
        cleaned_eid = eid.strip()
        path = f"/articles/{quote(cleaned_eid, safe='')}"
        try:
            raw, status = await self._client._request_raw(path)
        except EnckcNotFoundError:
            return None
        if raw is None or status == 204:
            return None
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint=path,
            request_params={"eid": cleaned_eid},
        )
        return _validate_or_raise(
            ArticleDetail, {**raw, "raw": raw, "metadata": metadata}, endpoint=path
        )

    async def iter_all(
        self,
        query: str | None = None,
        *,
        page_size: int = 20,
        start_page: int = 1,
        max_pages: int = 100,
        max_items: int | None = None,
    ) -> AsyncIterator[ArticleListItem]:
        """비동기로 페이지를 순회하며 개별 ArticleListItem 객체를 스트리밍합니다."""
        fetch_func = (
            (lambda p, ps: self.search(query, page=p, page_size=ps))
            if query
            else (lambda p, ps: self.list(page=p, page_size=ps))
        )
        yielded = 0
        async for page_resp in iter_pages(
            fetch_func,
            page_size=page_size,
            start_page=start_page,
            max_pages=max_pages,
            max_items=max_items,
        ):
            for item in page_resp.items:
                yield item
                yielded += 1
                if max_items is not None and yielded >= max_items:
                    return


class MediasService:
    """백과사전 미디어(Media) 비동기 서비스 파사드."""

    def __init__(self, client: EnckcClient) -> None:
        self._client = client

    async def list(self, *, page: int = 1, page_size: int = 20) -> PaginatedResponse[MediaItem]:
        """비동기로 전체 미디어 목록을 조회합니다."""
        params = {"p": page, "ps": page_size}
        raw, _ = await self._client._request_raw("/medias", params=params)
        if raw is None:
            raw = {
                "currentCount": 0,
                "totalCount": 0,
                "pageNo": page,
                "pageSize": page_size,
                "totalPage": 0,
                "items": [],
            }
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint="/medias",
            request_params=params,
        )
        return _validate_or_raise(
            PaginatedResponse[MediaItem], {**raw, "metadata": metadata}, endpoint="/medias"
        )

    async def search(
        self, query: str, *, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[MediaItem]:
        """비동기로 미디어를 키워드 검색합니다."""
        params = {"q": query, "p": page, "ps": page_size}
        raw, _ = await self._client._request_raw("/medias/search", params=params)
        if raw is None:
            raw = {
                "currentCount": 0,
                "totalCount": 0,
                "pageNo": page,
                "pageSize": page_size,
                "totalPage": 0,
                "items": [],
            }
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint="/medias/search",
            request_params=params,
        )
        return _validate_or_raise(
            PaginatedResponse[MediaItem],
            {**raw, "metadata": metadata},
            endpoint="/medias/search",
        )

    async def get(self, mid: str) -> MediaDetail | None:
        """비동기로 미디어 상세 내용을 조회합니다."""
        cleaned_mid = mid.strip()
        path = f"/medias/{quote(cleaned_mid, safe='')}"
        try:
            raw, status = await self._client._request_raw(path)
        except EnckcNotFoundError:
            return None
        if raw is None or status == 204:
            return None
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint=path,
            request_params={"mid": cleaned_mid},
        )
        return _validate_or_raise(
            MediaDetail, {**raw, "raw": raw, "metadata": metadata}, endpoint=path
        )

    async def iter_all(
        self,
        query: str | None = None,
        *,
        page_size: int = 20,
        start_page: int = 1,
        max_pages: int = 100,
        max_items: int | None = None,
    ) -> AsyncIterator[MediaItem]:
        """비동기로 페이지를 순회하며 개별 MediaItem 객체를 스트리밍합니다."""
        fetch_func = (
            (lambda p, ps: self.search(query, page=p, page_size=ps))
            if query
            else (lambda p, ps: self.list(page=p, page_size=ps))
        )
        yielded = 0
        async for page_resp in iter_pages(
            fetch_func,
            page_size=page_size,
            start_page=start_page,
            max_pages=max_pages,
            max_items=max_items,
        ):
            for item in page_resp.items:
                yield item
                yielded += 1
                if max_items is not None and yielded >= max_items:
                    return


class EnckcClient:
    """한국민족문화대백과사전 OpenAPI 비동기 클라이언트."""

    def __init__(
        self,
        api_key: str,
        *,
        timeout: float = 10.0,
        retries: int = 3,
        max_rps: float = 5.0,
        rate_limiter: AsyncTokenBucket | None = None,
        base_url: str | None = None,
        session: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = normalize_api_key(api_key, field_name="api_key")
        self.rate_limiter = rate_limiter if rate_limiter is not None else AsyncTokenBucket(max_rps)
        if session is not None and not isinstance(session, httpx.AsyncClient):
            raise TypeError("session must be an httpx.AsyncClient")
        self.timeout = timeout
        self.retries = retries
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.headers = {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
        }
        self.session = session if session is not None else build_client(headers=self.headers)
        self._owns_session = session is None
        self.articles: ArticlesService = ArticlesService(self)
        self.medias: MediasService = MediasService(self)
        self.closed = False

    @classmethod
    def from_env(cls, name: str | None = None, **kwargs: Any) -> EnckcClient:
        names = ENCKC_ENV_NAMES if name is None else (name,)
        api_key = first_env_value(names)
        return cls(api_key=api_key, **kwargs)

    async def aclose(self) -> None:
        """비동기 HTTP 세션을 닫습니다."""
        if self._owns_session and hasattr(self.session, "aclose"):
            await self.session.aclose()
        self.closed = True

    async def __aenter__(self) -> EnckcClient:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    # 편의 직접 접근 비동기 메서드
    async def list_articles(
        self, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[ArticleListItem]:
        return await self.articles.list(page=page, page_size=page_size)

    async def search_articles(
        self, query: str, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[ArticleListItem]:
        return await self.articles.search(query=query, page=page, page_size=page_size)

    async def get_article(self, eid: str) -> ArticleDetail | None:
        return await self.articles.get(eid=eid)

    async def list_medias(self, page: int = 1, page_size: int = 20) -> PaginatedResponse[MediaItem]:
        return await self.medias.list(page=page, page_size=page_size)

    async def search_medias(
        self, query: str, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[MediaItem]:
        return await self.medias.search(query=query, page=page, page_size=page_size)

    async def get_media(self, mid: str) -> MediaDetail | None:
        return await self.medias.get(mid=mid)

    def iter_pages(
        self,
        func: Callable[..., Awaitable[PaginatedResponse[T]]],
        *args: Any,
        page_size: int = 20,
        start_page: int = 1,
        max_pages: int = 100,
        max_items: int | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[PaginatedResponse[T]]:
        """비동기 페이지네이션 함수를 순회합니다."""

        async def _fetch(p: int, ps: int) -> PaginatedResponse[T]:
            return await func(*args, page=p, page_size=ps, **kwargs)

        return iter_pages(
            _fetch,
            page_size=page_size,
            start_page=start_page,
            max_pages=max_pages,
            max_items=max_items,
        )

    async def _request_raw(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any] | None, int]:
        """내부 비동기 요청 실행 및 JSON 파싱."""
        if self.closed:
            raise RuntimeError("EnckcClient is closed")
        url = f"{self.base_url}{path}"
        try:
            resp = await get_with_retries(
                self.session,
                url,
                params=params,
                headers=self.headers,
                timeout=self.timeout,
                retries=self.retries,
                rate_limiter=self.rate_limiter,
            )
        except httpx.HTTPStatusError as exc:
            raise_for_enckc_http_error(exc, endpoint=path, label="Encykorea")
        except httpx.RequestError:
            raise_for_enckc_network_error(endpoint=path, label="Encykorea")
        if resp.status_code == 204 or not resp.content.strip():
            return None, 204
        try:
            return resp.json(), resp.status_code
        except Exception as exc:
            raise EnckcParseError(
                f"Failed to parse Encykorea response as JSON: {exc}",
                endpoint=path,
                failure_kind="parse",
                retryable=False,
            ) from exc


    async def debug_fetch(
        self,
        key: str | ApiDefinition,
        params: Mapping[str, Any] | None = None,
    ) -> DebugRun:
        """디버그 UI/fixture 생성을 위한 카탈로그 기반 제네릭 fetch 실행 정보를 반환합니다.

        `catalog.py`의 `ApiDefinition` 메타데이터(경로 템플릿, path/query 파라미터,
        응답 모델)로 요청을 라우팅하며, 엔드포인트별 `if key == ...` 하드코딩 분기는
        두지 않습니다.
        """

        definition = get_api_definition(key)
        catalog_entry = get_api_catalog_entry(definition)
        values = dict(params or {})
        path_params = {
            name: values[name] for name in definition.path_param_names if name in values
        }
        query_params = {
            name: value
            for name, value in values.items()
            if name not in definition.path_param_names
            and value is not None
            and str(value).strip() != ""
        }

        input_data = redact_sensitive({"key": definition.key, "params": values})
        trace: list[str] = [
            f"카탈로그 조회: {definition.key}",
            f"엔드포인트: {definition.method} {definition.path_template}",
            f"동급 client 호출: client.{definition.facade}.{definition.operation}(...)",
        ]

        try:
            path = definition.path_template.format(
                **{name: quote(str(value), safe="") for name, value in path_params.items()}
            )
        except KeyError as key_exc:
            missing_exc = ValueError(f"missing path parameter: {key_exc}")
            trace.append(f"경로 파라미터 누락: {key_exc}")
            return DebugRun(
                function=definition.key,
                input=input_data,
                request={},
                response={},
                parsed=None,
                processed=None,
                trace=trace,
                error=debug_error(missing_exc),
                catalog=catalog_entry,
            )

        request_info: dict[str, Any] = {
            "method": definition.method,
            "url": f"{self.base_url}{path}",
            "query": sanitize_request_params(query_params),
            "headers": redact_sensitive(self.headers),
        }

        try:
            raw, status = await self._request_raw(path, params=query_params or None)
        except Exception as exc:  # noqa: BLE001 - 구조화된 디버그 오류로 변환하기 위해 폭넓게 수집
            trace.append(f"요청 실패: {exc.__class__.__name__}")
            return DebugRun(
                function=definition.key,
                input=input_data,
                request=request_info,
                response={},
                parsed=None,
                processed=None,
                trace=trace,
                error=debug_error(exc),
                catalog=catalog_entry,
            )

        trace.append(f"응답 status_code={status}")
        response_info: dict[str, Any] = {"status_code": status, "body": raw}
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint=path,
            request_params=query_params,
        )

        try:
            parsed: Any
            processed: Any
            if definition.kind == "list":
                item_model = definition.item_model
                if item_model is None:  # pragma: no cover - 카탈로그 정의 오류 방지용
                    raise ValueError(f"{definition.key}: item_model is not configured")
                model_data = raw or {
                    "currentCount": 0,
                    "totalCount": 0,
                    "pageNo": query_params.get("p", 1),
                    "pageSize": query_params.get("ps", 20),
                    "totalPage": 0,
                    "items": [],
                }
                paginated_model = cast(
                    "type[PaginatedResponse[Any]]", PaginatedResponse[item_model]  # type: ignore[valid-type]
                )
                parsed = _validate_or_raise(
                    paginated_model, {**model_data, "metadata": metadata}, endpoint=path
                )
                processed = list(parsed.items)
                trace.append(f"파싱: PaginatedResponse[{item_model.__name__}] ({len(processed)}건)")
            else:
                detail_model = definition.detail_model
                if detail_model is None:  # pragma: no cover - 카탈로그 정의 오류 방지용
                    raise ValueError(f"{definition.key}: detail_model is not configured")
                if raw is None or status == 204:
                    parsed = None
                    processed = None
                    trace.append("204 No Content -> None")
                else:
                    parsed = _validate_or_raise(
                        detail_model, {**raw, "raw": raw, "metadata": metadata}, endpoint=path
                    )
                    processed = parsed.to_dict()
                    trace.append(f"파싱: {detail_model.__name__}")
        except EnckcParseError as exc:
            trace.append("응답 검증 실패")
            return DebugRun(
                function=definition.key,
                input=input_data,
                request=request_info,
                response=response_info,
                parsed=None,
                processed=None,
                trace=trace,
                error=debug_error(exc),
                catalog=catalog_entry,
            )

        return DebugRun(
            function=definition.key,
            input=input_data,
            request=request_info,
            response=response_info,
            parsed=parsed,
            processed=processed,
            trace=trace,
            catalog=catalog_entry,
        )

