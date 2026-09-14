"""공개 비동기 요청의 공유 예산과 생명주기를 검증합니다."""
import asyncio
import time

import httpx
import pytest

import enckc
from enckc import AsyncTokenBucket, EnckcClient


class CountingBucket(AsyncTokenBucket):
    def __init__(self):
        super().__init__(100)
        self.calls = 0

    async def acquire(self):
        self.calls += 1
        await super().acquire()


async def test_retry_redirect_debug_and_multiple_clients_share_budget():
    bucket = CountingBucket()
    seen = []

    def respond(request):
        seen.append(request.url.path)
        assert request.headers["X-API-Key"] == "test-key"
        if len(seen) == 1:
            return httpx.Response(503, headers={"Retry-After": "0"})
        if len(seen) == 2:
            return httpx.Response(307, headers={"Location": "/api/articles/end"})
        return httpx.Response(204)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(respond), follow_redirects=True
    ) as session:
        async with EnckcClient("test-key", session=session, rate_limiter=bucket) as first:
            async with EnckcClient("test-key", session=session, rate_limiter=bucket) as second:
                assert await first.articles.get("missing") is None
                run = await second.debug_fetch("media_detail", {"mid": "missing"})
                assert run.error is None
                assert run.response["status_code"] == 204
        assert not session.is_closed
        assert bucket.calls == len(seen) == 4
        with pytest.raises(RuntimeError, match="closed"):
            await first.medias.get("missing")
        assert len(seen) == 4


async def test_concurrent_public_requests_obey_capacity_one_budget():
    sent = []

    def respond(request):
        sent.append(time.monotonic())
        return httpx.Response(204)

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as session:
        async with EnckcClient(
            "test-key", session=session, rate_limiter=AsyncTokenBucket(20, capacity=1)
        ) as client:
            results = await asyncio.gather(*(client.get_article(str(i)) for i in range(5)))
    assert results == [None] * 5
    assert sent[-1] - sent[0] >= 0.195


@pytest.mark.parametrize("rate", [0, -1, float("inf"), float("nan"), True])
def test_invalid_rate_rejected_before_client_creation(rate):
    with pytest.raises(ValueError):
        EnckcClient("test-key", max_rps=rate)


def test_sync_surface_and_sync_injection_removed():
    assert not hasattr(enckc, "AsyncEnckcClient")
    assert not hasattr(EnckcClient, "aio")
    assert not hasattr(EnckcClient, "__enter__")
    with httpx.Client() as session:
        with pytest.raises(TypeError, match="AsyncClient"):
            EnckcClient("test-key", session=session)


async def test_pagination_preserves_public_callback_keywords():
    async def fetch_page(page_no, page_size):
        return enckc.PaginatedResponse(
            items=[], page_no=page_no, page_size=page_size, total_count=0,
            current_count=0, total_page=0,
        )

    pages = [page async for page in enckc.iter_pages(fetch_page=fetch_page)]
    assert len(pages) == 1
    async with EnckcClient("test-key") as client:
        async def func(*, page, page_size):
            return await fetch_page(page, page_size)

        pages = [page async for page in client.iter_pages(func=func)]
    assert len(pages) == 1
