"""한국민족문화대백과사전(Encykorea) OpenAPI 클라이언트."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import Any, TypeVar

import httpx

from ._credentials import ENCKC_ENV_NAMES, first_env_value, normalize_api_key
from ._http import (
    async_get_with_retries,
    build_async_client,
    build_client,
    get_with_retries,
    raise_for_enckc_http_error,
    raise_for_enckc_network_error,
)
from .exceptions import EnckcParseError
from .metadata import make_response_metadata
from .models import (
    ArticleDetail,
    ArticleListItem,
    MediaDetail,
    MediaItem,
    PaginatedResponse,
)
from .pagination import async_iter_pages, iter_pages

DEFAULT_BASE_URL = "https://devin.aks.ac.kr:8080/api"
T = TypeVar("T")


class EnckcClient:
    """한국민족문화대백과사전 OpenAPI 동기 클라이언트."""

    def __init__(
        self,
        api_key: str,
        *,
        timeout: float = 10.0,
        retries: int = 3,
        base_url: str | None = None,
        session: httpx.Client | None = None,
    ) -> None:
        self.api_key = normalize_api_key(api_key, field_name="api_key")
        self.timeout = timeout
        self.retries = retries
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.headers = {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
        }
        self.session = session or build_client(headers=self.headers)
        self._owns_session = session is None
        self.articles: ArticlesService = ArticlesService(self)
        self.medias: MediasService = MediasService(self)
        self.closed = False

    @classmethod
    def from_env(cls, name: str = "ENCKC_API_KEY", **kwargs: Any) -> EnckcClient:
        """환경변수 또는 `.env`/`.env.local`에서 인증키를 읽어 클라이언트를 생성합니다."""
        names = ENCKC_ENV_NAMES if name == "ENCKC_API_KEY" else (name, *ENCKC_ENV_NAMES)
        api_key = first_env_value(names)
        return cls(api_key=api_key, **kwargs)

    @classmethod
    def aio(cls, api_key: str, **kwargs: Any) -> AsyncEnckcClient:
        """비동기 사용을 위한 `AsyncEnckcClient`를 생성합니다."""
        return AsyncEnckcClient(api_key=api_key, **kwargs)

    @classmethod
    def aio_from_env(cls, name: str = "ENCKC_API_KEY", **kwargs: Any) -> AsyncEnckcClient:
        """환경변수에서 인증키를 읽어 `AsyncEnckcClient`를 생성합니다."""
        names = ENCKC_ENV_NAMES if name == "ENCKC_API_KEY" else (name, *ENCKC_ENV_NAMES)
        api_key = first_env_value(names)
        return AsyncEnckcClient(api_key=api_key, **kwargs)

    def close(self) -> None:
        """동기 HTTP 세션을 닫습니다."""
        if self._owns_session and hasattr(self.session, "close"):
            self.session.close()
        self.closed = True

    def __enter__(self) -> EnckcClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    # 편의 직접 접근 동기 메서드
    def list_articles(
        self, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[ArticleListItem]:
        """전체 항목 리스트를 조회합니다."""
        return self.articles.list(page=page, page_size=page_size)

    def search_articles(
        self, query: str, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[ArticleListItem]:
        """항목을 키워드로 검색합니다."""
        return self.articles.search(query=query, page=page, page_size=page_size)

    def get_article(self, eid: str) -> ArticleDetail | None:
        """EID로 항목 상세 내용을 조회합니다."""
        return self.articles.get(eid=eid)

    def list_medias(self, page: int = 1, page_size: int = 20) -> PaginatedResponse[MediaItem]:
        """전체 미디어 목록을 조회합니다."""
        return self.medias.list(page=page, page_size=page_size)

    def search_medias(
        self, query: str, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[MediaItem]:
        """미디어를 키워드로 검색합니다."""
        return self.medias.search(query=query, page=page, page_size=page_size)

    def get_media(self, mid: str) -> MediaDetail | None:
        """MID로 미디어 상세 내용을 조회합니다."""
        return self.medias.get(mid=mid)

    def iter_pages(
        self,
        func: Callable[..., PaginatedResponse[T]],
        *args: Any,
        page_size: int = 20,
        start_page: int = 1,
        max_pages: int = 100,
        max_items: int | None = None,
        **kwargs: Any,
    ) -> Iterator[PaginatedResponse[T]]:
        """페이지네이션 함수를 순회합니다."""

        def _fetch(p: int, ps: int) -> PaginatedResponse[T]:
            return func(*args, page=p, page_size=ps, **kwargs)

        return iter_pages(
            _fetch,
            page_size=page_size,
            start_page=start_page,
            max_pages=max_pages,
            max_items=max_items,
        )

    def _request_raw(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any] | None, int]:
        """내부 동기 요청 실행 및 JSON 파싱."""
        url = f"{self.base_url}{path}"
        try:
            resp = get_with_retries(
                self.session,
                url,
                params=params,
                headers=self.headers,
                timeout=self.timeout,
                retries=self.retries,
            )
            # 204 No Content 대응
            if resp.status_code == 204 or not resp.content.strip():
                return None, 204
            return resp.json(), resp.status_code
        except httpx.HTTPStatusError as exc:
            raise_for_enckc_http_error(exc, endpoint=path, label="Encykorea")
        except httpx.RequestError:
            raise_for_enckc_network_error(endpoint=path, label="Encykorea")
        except Exception as exc:
            raise EnckcParseError(
                f"Failed to parse Encykorea response as JSON: {exc}",
                endpoint=path,
                failure_kind="parse",
                retryable=False,
            ) from exc


class ArticlesService:
    """백과사전 항목(Article) 서비스 파사드."""

    def __init__(self, client: EnckcClient) -> None:
        self._client = client

    def list(self, *, page: int = 1, page_size: int = 20) -> PaginatedResponse[ArticleListItem]:
        """전체 항목 리스트를 조회합니다.

        `GET /articles?p={pageNo}&ps={pageSize}`
        """
        params = {"p": page, "ps": page_size}
        raw, _ = self._client._request_raw("/articles", params=params)
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
        return PaginatedResponse[ArticleListItem].model_validate({**raw, "metadata": metadata})

    def search(
        self, query: str, *, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[ArticleListItem]:
        """항목을 검색어로 검색합니다.

        `GET /articles/search?q={keyword}&p={pageNo}&ps={pageSize}`
        """
        params = {"q": query, "p": page, "ps": page_size}
        raw, _ = self._client._request_raw("/articles/search", params=params)
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
        return PaginatedResponse[ArticleListItem].model_validate({**raw, "metadata": metadata})

    def get(self, eid: str) -> ArticleDetail | None:
        """항목 EID(예: 'E0029849')로 상세 내용을 조회합니다. 존재하지 않으면 None을 반환합니다.

        `GET /articles/{eid}`
        """
        cleaned_eid = eid.strip()
        path = f"/articles/{cleaned_eid}"
        raw, status = self._client._request_raw(path)
        if raw is None or status == 204:
            return None
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint=path,
            request_params={"eid": cleaned_eid},
        )
        return ArticleDetail.model_validate({**raw, "raw": raw, "metadata": metadata})

    def iter_all(
        self,
        query: str | None = None,
        *,
        page_size: int = 20,
        start_page: int = 1,
        max_pages: int = 100,
        max_items: int | None = None,
    ) -> Iterator[ArticleListItem]:
        """페이지를 순회하며 개별 ArticleListItem 객체를 스트리밍합니다."""
        fetch_func = (
            (lambda p, ps: self.search(query, page=p, page_size=ps))
            if query
            else (lambda p, ps: self.list(page=p, page_size=ps))
        )
        yielded = 0
        for page_resp in iter_pages(
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
    """백과사전 미디어(Media) 서비스 파사드."""

    def __init__(self, client: EnckcClient) -> None:
        self._client = client

    def list(self, *, page: int = 1, page_size: int = 20) -> PaginatedResponse[MediaItem]:
        """미디어 전체 목록을 조회합니다.

        `GET /medias?p={pageNo}&ps={pageSize}`
        """
        params = {"p": page, "ps": page_size}
        raw, _ = self._client._request_raw("/medias", params=params)
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
        return PaginatedResponse[MediaItem].model_validate({**raw, "metadata": metadata})

    def search(
        self, query: str, *, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[MediaItem]:
        """미디어를 검색어로 검색합니다.

        `GET /medias/search?q={keyword}&p={pageNo}&ps={pageSize}`
        """
        params = {"q": query, "p": page, "ps": page_size}
        raw, _ = self._client._request_raw("/medias/search", params=params)
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
        return PaginatedResponse[MediaItem].model_validate({**raw, "metadata": metadata})

    def get(self, mid: str) -> MediaDetail | None:
        """미디어 MID로 상세 내용을 조회합니다. 존재하지 않으면 None을 반환합니다.

        `GET /medias/{mid}`
        """
        cleaned_mid = mid.strip()
        path = f"/medias/{cleaned_mid}"
        raw, status = self._client._request_raw(path)
        if raw is None or status == 204:
            return None
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint=path,
            request_params={"mid": cleaned_mid},
        )
        return MediaDetail.model_validate({**raw, "raw": raw, "metadata": metadata})

    def iter_all(
        self,
        query: str | None = None,
        *,
        page_size: int = 20,
        start_page: int = 1,
        max_pages: int = 100,
        max_items: int | None = None,
    ) -> Iterator[MediaItem]:
        """페이지를 순회하며 개별 MediaItem 객체를 스트리밍합니다."""
        fetch_func = (
            (lambda p, ps: self.search(query, page=p, page_size=ps))
            if query
            else (lambda p, ps: self.list(page=p, page_size=ps))
        )
        yielded = 0
        for page_resp in iter_pages(
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


class AsyncArticlesService:
    """백과사전 항목(Article) 비동기 서비스 파사드."""

    def __init__(self, client: AsyncEnckcClient) -> None:
        self._client = client

    async def list(
        self, *, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[ArticleListItem]:
        """비동기로 전체 항목 리스트를 조회합니다."""
        params = {"p": page, "ps": page_size}
        raw, _ = await self._client._arequest_raw("/articles", params=params)
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
        return PaginatedResponse[ArticleListItem].model_validate({**raw, "metadata": metadata})

    async def search(
        self, query: str, *, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[ArticleListItem]:
        """비동기로 항목을 키워드 검색합니다."""
        params = {"q": query, "p": page, "ps": page_size}
        raw, _ = await self._client._arequest_raw("/articles/search", params=params)
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
        return PaginatedResponse[ArticleListItem].model_validate({**raw, "metadata": metadata})

    async def get(self, eid: str) -> ArticleDetail | None:
        """비동기로 항목 상세 내용을 조회합니다."""
        cleaned_eid = eid.strip()
        path = f"/articles/{cleaned_eid}"
        raw, status = await self._client._arequest_raw(path)
        if raw is None or status == 204:
            return None
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint=path,
            request_params={"eid": cleaned_eid},
        )
        return ArticleDetail.model_validate({**raw, "raw": raw, "metadata": metadata})

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
        async for page_resp in async_iter_pages(
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


class AsyncMediasService:
    """백과사전 미디어(Media) 비동기 서비스 파사드."""

    def __init__(self, client: AsyncEnckcClient) -> None:
        self._client = client

    async def list(self, *, page: int = 1, page_size: int = 20) -> PaginatedResponse[MediaItem]:
        """비동기로 전체 미디어 목록을 조회합니다."""
        params = {"p": page, "ps": page_size}
        raw, _ = await self._client._arequest_raw("/medias", params=params)
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
        return PaginatedResponse[MediaItem].model_validate({**raw, "metadata": metadata})

    async def search(
        self, query: str, *, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[MediaItem]:
        """비동기로 미디어를 키워드 검색합니다."""
        params = {"q": query, "p": page, "ps": page_size}
        raw, _ = await self._client._arequest_raw("/medias/search", params=params)
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
        return PaginatedResponse[MediaItem].model_validate({**raw, "metadata": metadata})

    async def get(self, mid: str) -> MediaDetail | None:
        """비동기로 미디어 상세 내용을 조회합니다."""
        cleaned_mid = mid.strip()
        path = f"/medias/{cleaned_mid}"
        raw, status = await self._client._arequest_raw(path)
        if raw is None or status == 204:
            return None
        metadata = make_response_metadata(
            provider="encykorea",
            endpoint=path,
            request_params={"mid": cleaned_mid},
        )
        return MediaDetail.model_validate({**raw, "raw": raw, "metadata": metadata})

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
        async for page_resp in async_iter_pages(
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


class AsyncEnckcClient:
    """한국민족문화대백과사전 OpenAPI 비동기 클라이언트."""

    def __init__(
        self,
        api_key: str,
        *,
        timeout: float = 10.0,
        retries: int = 3,
        base_url: str | None = None,
        async_session: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = normalize_api_key(api_key, field_name="api_key")
        self.timeout = timeout
        self.retries = retries
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.headers = {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
        }
        self.session = async_session or build_async_client(headers=self.headers)
        self._owns_session = async_session is None
        self.articles: AsyncArticlesService = AsyncArticlesService(self)
        self.medias: AsyncMediasService = AsyncMediasService(self)
        self.closed = False

    @classmethod
    def from_env(cls, name: str = "ENCKC_API_KEY", **kwargs: Any) -> AsyncEnckcClient:
        names = ENCKC_ENV_NAMES if name == "ENCKC_API_KEY" else (name, *ENCKC_ENV_NAMES)
        api_key = first_env_value(names)
        return cls(api_key=api_key, **kwargs)

    async def aclose(self) -> None:
        """비동기 HTTP 세션을 닫습니다."""
        if self._owns_session and hasattr(self.session, "aclose"):
            await self.session.aclose()
        self.closed = True

    async def close(self) -> None:
        """`aclose()`의 별칭입니다."""
        await self.aclose()

    async def __aenter__(self) -> AsyncEnckcClient:
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

    def async_iter_pages(
        self,
        afunc: Callable[..., Awaitable[PaginatedResponse[T]]],
        *args: Any,
        page_size: int = 20,
        start_page: int = 1,
        max_pages: int = 100,
        max_items: int | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[PaginatedResponse[T]]:
        """비동기 페이지네이션 함수를 순회합니다."""

        async def _fetch(p: int, ps: int) -> PaginatedResponse[T]:
            return await afunc(*args, page=p, page_size=ps, **kwargs)

        return async_iter_pages(
            _fetch,
            page_size=page_size,
            start_page=start_page,
            max_pages=max_pages,
            max_items=max_items,
        )

    async def _arequest_raw(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any] | None, int]:
        """내부 비동기 요청 실행 및 JSON 파싱."""
        url = f"{self.base_url}{path}"
        try:
            resp = await async_get_with_retries(
                self.session,
                url,
                params=params,
                headers=self.headers,
                timeout=self.timeout,
                retries=self.retries,
            )
            if resp.status_code == 204 or not resp.content.strip():
                return None, 204
            return resp.json(), resp.status_code
        except httpx.HTTPStatusError as exc:
            raise_for_enckc_http_error(exc, endpoint=path, label="Encykorea")
        except httpx.RequestError:
            raise_for_enckc_network_error(endpoint=path, label="Encykorea")
        except Exception as exc:
            raise EnckcParseError(
                f"Failed to parse Encykorea response as JSON: {exc}",
                endpoint=path,
                failure_kind="parse",
                retryable=False,
            ) from exc
