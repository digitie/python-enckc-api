# 비동기 사용과 TPS 제어

`EnckcClient`는 비동기 전용이다. 기존 `AsyncEnckcClient`, `aio()`, 동기 context
manager와 `close()`는 제거했다. `from_env()`와 생성자는 네트워크 I/O가 없는 일반
함수이며, 조회·`debug_fetch()`·`aclose()`는 await, 페이지·항목 순회는 async for를 쓴다.

```python
from enckc import AsyncTokenBucket, EnckcClient

async def collect():
    bucket = AsyncTokenBucket(max_rps=2, capacity=1)
    async with EnckcClient.from_env(rate_limiter=bucket) as client:
        result = await client.articles.search("세종", page_size=5)
        async for page in client.iter_pages(client.articles.list, page_size=5, max_pages=2):
            print(page.items)
        run = await client.debug_fetch("articles_search", {"q": "세종", "ps": 5})
        return result, run
```

`max_rps` 기본값은 5다. 유한한 양수만 허용하며 0, 음수, NaN, 무한대, bool은 거부한다.
버킷의 기본 capacity는 `max(1, max_rps)`이고 처음에는 가득 찬 상태다. 순간 burst를
1건으로 줄이려면 `capacity=1`을 지정한다. 예산은 토큰 버킷이며 고정 1초 구간별
최대 건수 제한과는 다르다. 0.5 TPS도 허용한다.

여러 클라이언트에 동일 `rate_limiter` 객체를 주입하면 호출 예산을 공유한다.
주입된 버킷이 `max_rps`보다 우선한다. 버킷은 하나의 이벤트 루프에서만 사용한다.
취소된 대기 요청은 토큰을 쓰지 않고 다음 대기 요청이 진행한다.

서비스·디버그·페이지 순회와 각 재시도가 같은 버킷을 사용한다. 기본 HTTPX 세션은
redirect를 따르지 않으며, `follow_redirects=True` 세션을 주입하면 각 후속 송신도
토큰을 소비한다. 사용자 정의 인증 흐름이나 transport 내부의 추가 송신은 제어하지
않는다. 외부 세션의 수명과 redirect 목적지·인증 정책은 호출자가 관리한다.

`async with`가 자체 생성 세션을 닫는다. 주입한 세션은 호출자가 별도로 닫고,
종료된 EnckcClient에서는 추가 요청을 받지 않는다. CLI/Streamlit은 실행 경계에서
`asyncio.run`을 한 번 호출하고 같은 이벤트 루프 안에서 생성·사용·종료한다.
