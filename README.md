# python-enckc-api

한국학중앙연구원(AKS) **한국민족문화대백과사전**(Encyclopedia of Korean Culture, Encykorea) OpenAPI를 Python에서 쉽고 안전하게 활용하기 위한 공식 규격 기반의 비공식 클라이언트 라이브러리입니다.

`python-enckc-api`는 `enckc`라는 직관적인 import 패키지를 제공합니다. 특정 웹 프레임워크나 DB 스키마에 종속되지 않고, 한국민족문화대백과사전의 전체 항목 조회, 키워드 검색, 항목 본문 상세(EID), 미디어 목록/검색/상세(MID) 등 6개 핵심 API 엔드포인트를 완전하게 지원합니다.

> 세부 API 규격은 [enckc-api.md](enckc-api.md), 에이전트 개발 규칙은 [SKILL.md](SKILL.md) 및 [AGENTS.md](AGENTS.md)를 참고하세요.

---

## 핵심 특징

- **공식 OpenAPI 6종 전체 지원**:
  1. `articles.list()`: 전체 항목 리스트 (`GET /api/articles`)
  2. `articles.search()`: 항목 키워드 검색 (`GET /api/articles/search`)
  3. `articles.get()`: 항목 상세 본문/각주/속성/연관자료 (`GET /api/articles/{eid}`)
  4. `medias.list()`: 미디어 전체 목록 (`GET /api/medias`)
  5. `medias.search()`: 미디어 키워드 검색 (`GET /api/medias/search`)
  6. `medias.get()`: 미디어 상세 정보 (`GET /api/medias/{mid}`)
- **동기/비동기 통합 클라이언트**: `httpx` 기반의 동기 `EnckcClient` 및 비동기 `AsyncEnckcClient` 제공 (`async with EnckcClient.aio(...)`)
- **Pydantic v2 불변 모델**: 모든 응답 모델은 `ConfigDict(frozen=True, extra="forbid")`가 적용되어 데이터 오염을 방지하고 빠른 직렬화(`model_dump(mode="json")`) 및 역직렬화를 보장합니다.
- **204 No Content 및 빈 결과 완벽 대응**: 존재하지 않는 항목/미디어 조회 시 204 No Content를 안전하게 `None`으로 반환하며, 빈 검색 결과도 안전하게 빈 리스트로 래핑합니다.
- **자동 페이지네이션 순회자**: `iter_pages()`, `async_iter_pages()`, `articles.iter_all()`, `medias.iter_all()`을 통해 수만 건의 데이터를 Generator/AsyncGenerator로 손쉽게 스트리밍할 수 있습니다.
- **인증키 보안 마스킹**: 로그, 메타데이터, 예외 객체, repr 출력 등에서 API 인증키(`X-API-Key`)를 자동으로 마스킹(`***REDACTED***`)하여 유출을 원천 방지합니다.
- **CLI 명령행 도구**: 터미널에서 즉시 검색 및 조회가 가능한 `enckc` CLI 도구를 번들 제공합니다.
- **Streamlit 디버그 UI**: 웹 브라우저에서 실시간으로 대백과사전을 검색하고 JSON 응답을 탐색할 수 있는 디버그 UI 도구 지원 (`tools/debug_streamlit.py`).

---

## 시작하기

### 1단계: 인증키 발급 및 설정

1. [한국민족문화대백과사전 OpenAPI 안내 페이지](https://encykorea.aks.ac.kr/Guide/OpenApiUse)에서 OpenAPI 인증키 발급을 신청합니다.
2. 발급받은 인증키를 환경변수 또는 `.env`/`.env.local` 파일에 저장합니다.

```bash
export ENCKC_API_KEY="발급받은_인증키"
```

Windows PowerShell:
```powershell
$env:ENCKC_API_KEY="발급받은_인증키"
```

로컬 프로젝트 루트의 `.env.local` 파일:
```text
ENCKC_API_KEY=YOUR_ENCKC_API_KEY_HERE
```

### 2단계: 설치

```bash
pip install python-enckc-api
```

개발 환경 로컬 설치:
```bash
pip install -e ".[dev,debug-ui]"
```

---

## 사용 예제

### 1. 동기 클라이언트 (`EnckcClient`)

```python
from enckc import EnckcClient

# .env.local 또는 환경변수에서 ENCKC_API_KEY 자동 로드
with EnckcClient.from_env() as client:
    # 1. 항목 검색 (예: '세종')
    search_result = client.articles.search(query="세종", page=1, page_size=5)
    print(f"총 검색 건수: {search_result.total_count}건")
    for item in search_result.items:
        print(f"[{item.eid}] {item.headword} ({item.origin or ''}) - {item.definition}")

    # 2. 항목 상세 본문 조회 (예: 세조 E0029849)
    article = client.articles.get(eid="E0029849")
    if article:
        print(f"\n=== {article.headword} 상세 ===")
        print(f"시대: {article.era}")
        print(f"분야: {article.field}")
        print(f"요약: {article.summary}")
        print(f"본문 길이: {len(article.body or '')}자")
        print(f"연관 항목 수: {len(article.related_articles)}개")

    # 3. 미디어 검색 (예: '훈민정음')
    media_result = client.medias.search(query="훈민정음", page=1, page_size=3)
    for media in media_result.items:
        print(f"미디어: {media.caption} ({media.media_type}) -> {media.url}")
```

### 2. 비동기 클라이언트 (`AsyncEnckcClient`)

```python
import asyncio
from enckc import EnckcClient


async def main():
    async with EnckcClient.aio_from_env() as client:
        # 비동기 항목 검색
        resp = await client.articles.search("한글", page=1, page_size=5)
        print(f"한글 검색 결과: {resp.total_count}건")

        # 비동기 상세 조회
        detail = await client.articles.get("E0000002")  # 'ㄱ'
        if detail:
            print(f"표제어: {detail.headword}, 집필자: {detail.writer_info}")


asyncio.run(main())
```

### 3. 대용량 데이터 스트리밍 순회 (`iter_all`)

```python
from enckc import EnckcClient

with EnckcClient.from_env() as client:
    # 검색된 모든 항목을 페이지네이션을 거쳐 하나씩 순회 (최대 50건)
    for item in client.articles.iter_all(query="조선", page_size=20, max_items=50):
        print(item.eid, item.headword)
```

---

## CLI 사용법

터미널에서 `enckc` 명령어를 통해 대백과사전 데이터를 즉시 조회할 수 있습니다:

```bash
# 항목 검색
enckc search-articles -q "세종대왕" -p 1 -s 5

# 항목 상세 조회 (JSON 출력)
enckc article E0029849

# 미디어 검색
enckc search-medias -q "첨성대" -p 1 -s 3

# 미디어 상세 조회
enckc media 0bad737c-471b-4fd5-86cf-10774faeaaa7
```

---

## 응답 모델 구조

모든 모델은 불변 Pydantic v2 모델이며 속성 접근 및 딕셔너리 변환(`model_dump()`)을 지원합니다.

### `ArticleListItem` / `ArticleDetail`

| 필드명 | 타입 | 설명 |
|---|---|---|
| `eid` | `str` | 항목 고유 식별자 (예: `E0029849`) |
| `headword` | `str` | 표제어 한글 표기 (예: `세조`) |
| `origin` | `str \| None` | 표제어 한자/원어 표기 (예: `世祖`) |
| `field` | `str \| None` | 주제 분야 (예: `역사/조선시대사`) |
| `primary_type` | `str \| None` | 1차 분류 유형 (예: `인물/전통 인물`) |
| `era` | `str \| None` | 시대 구분 (예: `조선/조선 전기`) |
| `definition` | `str \| None` | 항목 정의문 |
| `summary` | `str \| None` | 요약 해설 |
| `body` | `str \| None` | 상세 본문 (Markdown 포맷) |
| `foot_note` | `str \| None` | 각주 설명 |
| `reference` | `str \| None` | 참고문헌 |
| `writer_info` | `str \| None` | 집필자 정보 (소속, 전공 등) |
| `article_aliases` | `list[ArticleAlias]` | 이칭/자/호/시호 등 별칭 목록 |
| `article_attributes` | `list[ArticleAttribute]` | 구조화 속성 목록 (출생/사망, 본관 등) |
| `related_articles` | `list[RelatedArticle]` | 본문 연관 백과사전 항목 목록 |
| `related_medias` | `list[MediaItem]` | 연관 미디어 목록 |

### `MediaItem` / `MediaDetail`

| 필드명 | 타입 | 설명 |
|---|---|---|
| `mid` | `str` | 미디어 고유 UUID 식별자 |
| `media_type` | `str \| None` | 미디어 구분 (`사진`, `도면`, `음원` 등) |
| `kogl_type` | `str \| None` | 공공누리 라이선스 유형 (`KOGL1` ~ `KOGL4`) |
| `url` | `str \| None` | 원본 이미지/미디어 다운로드 URL |
| `caption` | `str \| None` | 캡션 / 제목 |
| `description` | `str \| None` | 미디어 상세 설명 |
| `copyright_display` | `str \| None` | 저작권 표기 정보 |

---

## 예외 계층

```text
EnckcError (기본 예외)
├── EnckcAuthError (401/403 인증 실패)
├── EnckcNotFoundError (404 리소스 없음)
├── EnckcRequestError (400 잘못된 요청 / 429 Rate Limit)
├── EnckcServerError (5xx 서버 오류)
└── EnckcParseError (JSON 파싱 실패)
```

---

## 디버그 UI 실행

```bash
streamlit run tools/debug_streamlit.py
```

---

## 라이선스

이 프로젝트는 GNU General Public License v3.0 or later (GPL-3.0-or-later) 라이선스를 따릅니다.
제공되는 한국민족문화대백과사전 데이터의 저작권은 한국학중앙연구원(The Academy of Korean Studies)에 있습니다.
