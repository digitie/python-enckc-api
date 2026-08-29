# python-enckc-api

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![GPL-3.0-or-later 라이선스](https://img.shields.io/badge/License-GPL--3.0--or--later-blue.svg)
![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)

한국학중앙연구원(AKS) **한국민족문화대백과사전**(Encyclopedia of Korean Culture, Encykorea) OpenAPI를 Python에서 쉽고 안전하게 활용하기 위한 공식 규격 기반의 비공식 클라이언트 라이브러리입니다. `enckc`라는 import 패키지를 통해 전체 항목 조회, 키워드 검색, 항목 본문 상세(EID), 미디어 목록/검색/상세(MID) 등 6개 핵심 API 엔드포인트를 동기/비동기로 완전하게 지원합니다.

최근 변경 사항은 [CHANGELOG.md](CHANGELOG.md)를 참고하세요.

---

## 제공 표면

| 표면 | 진입점 | 설명 |
|---|---|---|
| 동기 클라이언트 | `enckc.EnckcClient` | `httpx` 기반 동기 클라이언트. `client.articles.*`, `client.medias.*` |
| 비동기 클라이언트 | `enckc.EnckcClient.aio()` / `AsyncEnckcClient` | 동일한 파사드 구조의 비동기 클라이언트 |
| CLI | `enckc` 명령행 도구 | 터미널에서 즉시 검색/조회 (`enckc search-articles`, `enckc article` 등) |
| 디버그 UI | `examples/streamlit_debug_ui.py` | Streamlit 기반 실시간 카탈로그 탐색 도구 (`debug-ui` extra 필요) |

## 먼저 읽을 문서

| 필요한 정보 | 문서 |
|---|---|
| API 규격 상세 (엔드포인트/파라미터/응답 스키마) | [enckc-api.md](enckc-api.md) |
| 에이전트 구현 불변조건 요약 | [SKILL.md](SKILL.md) |
| 에이전트 운영 가이드 (지시 우선순위, DO NOT) | [AGENTS.md](AGENTS.md) |
| 코드 탐색 시 참고할 핵심 규칙 요약 | [docs/agent-guide.md](docs/agent-guide.md) |
| 전체 엔드포인트 지원 현황 | [docs/api-coverage.md](docs/api-coverage.md) |
| 구조적 의사결정 기록 | [docs/decisions.md](docs/decisions.md) |
| 테스트 구조 및 실행법 | [docs/testing.md](docs/testing.md) |
| 문제 해결 가이드 (401, 204, 인코딩 등) | [docs/troubleshooting.md](docs/troubleshooting.md) |
| 반복된 실수와 회고 | [docs/repeated-mistakes.md](docs/repeated-mistakes.md) |
| 진행 상황 재개 메모 | [docs/resume.md](docs/resume.md) |
| 작업 목록 | [docs/tasks.md](docs/tasks.md) |
| 작업 일지 (역시간순) | [docs/journal.md](docs/journal.md) |
| 기여 방법 | [CONTRIBUTING.md](CONTRIBUTING.md) |
| AI 에이전트 협업 지침 (코딩 표준/보안/검증) | [AI_AGENT_GUIDE.md](AI_AGENT_GUIDE.md) |

---

## 설치 및 인증키 설정

### 1. 인증키 발급

[한국민족문화대백과사전 OpenAPI 안내 페이지](https://encykorea.aks.ac.kr/Guide/OpenApiUse)에서 OpenAPI 인증키를 발급받습니다. 이 인증키는 HTTP 요청 헤더 `X-API-Key`로 전송됩니다 (`serviceKey` 쿼리파라미터 방식이 아닙니다).

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

### 2. 설치

```bash
pip install python-enckc-api
```

개발 환경 로컬 설치:
```bash
pip install -e ".[dev,debug-ui]"
```

---

## 사용 예제

```python
from enckc import EnckcClient

# .env.local 또는 환경변수에서 ENCKC_API_KEY 자동 로드
with EnckcClient.from_env() as client:
    # 항목 검색 (예: '세종')
    search_result = client.articles.search(query="세종", page=1, page_size=5)
    print(f"총 검색 건수: {search_result.total_count}건")
    for item in search_result.items:
        print(f"[{item.eid}] {item.headword} ({item.origin or ''}) - {item.definition}")

    # 항목 상세 본문 조회 (예: 세조 E0029849) — 존재하지 않으면 None 반환
    article = client.articles.get(eid="E0029849")
    if article:
        print(f"\n=== {article.headword} 상세 ===")
        print(f"시대: {article.era}")
        print(f"본문 길이: {len(article.body or '')}자")
```

위 예제는 동기 클라이언트의 핵심 흐름만 다룹니다. 비동기 클라이언트(`AsyncEnckcClient`), 대용량 스트리밍 순회(`iter_all`), 미디어 API, CLI 사용법은 [enckc-api.md](enckc-api.md)와 아래 CLI/응답 모델 절을 참고하세요.

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
| `era` | `str \| None` | 시대 구분 (예: `조선/조선 전기`) |
| `definition` | `str \| None` | 항목 정의문 |
| `body` | `str \| None` | 상세 본문 (Markdown 포맷) |
| `related_articles` | `list[RelatedArticle]` | 본문 연관 백과사전 항목 목록 |
| `related_medias` | `list[MediaItem]` | 연관 미디어 목록 |

전체 필드 목록은 [enckc-api.md](enckc-api.md)를 참고하세요.

### `MediaItem` / `MediaDetail`

| 필드명 | 타입 | 설명 |
|---|---|---|
| `mid` | `str` | 미디어 고유 UUID 식별자 |
| `media_type` | `str \| None` | 미디어 구분 (`사진`, `도면`, `음원` 등) |
| `kogl_type` | `str \| None` | 공공누리 라이선스 유형 (`KOGL1` ~ `KOGL4`) |
| `url` | `str \| None` | 원본 이미지/미디어 다운로드 URL |
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

카탈로그(`enckc.get_api_catalog()`)의 `required_params`/`optional_params` 메타데이터로 입력
폼을 자동 생성하고, `EnckcClient.debug_fetch()`로 요청을 실행해 Raw Response/Pydantic
Model/Processed Result/Validation Errors/Debug Trace/Fixture 저장까지 6개 탭에서 확인할 수
있습니다.

```bash
pip install -e ".[debug-ui]"
streamlit run examples/streamlit_debug_ui.py
```

---

## 검증

```bash
# 기본 품질 게이트 (네트워크 호출 없음)
python -m pytest -q
python -m ruff check .
python -m mypy src/enckc

# 실제 API E2E 통합 테스트 (ENCKC_API_KEY 필요)
python -m pytest -m integration -v
```

---

## 데이터 및 API 출처

이 라이브러리가 감싸는 데이터와 API는 한국학중앙연구원(The Academy of Korean Studies)이 제공하는 [한국민족문화대백과사전 OpenAPI](https://encykorea.aks.ac.kr/Guide/OpenApiUse)이며, 기본 엔드포인트는 `https://devin.aks.ac.kr:8080/api`입니다.

---

## 디렉터리 개요

| 경로 | 설명 |
|---|---|
| `src/enckc/` | 패키지 소스 코드 (`client.py`, `models.py`, `_http.py`, `_credentials.py`, `exceptions.py`, `pagination.py`, `cli.py`, `catalog.py`, `debug.py`, `metadata.py`) |
| `tests/` | 단위 및 통합 테스트 스위트 |
| `examples/` | Streamlit 디버그 UI (`streamlit_debug_ui.py`) |
| `docs/` | 설계 결정, 테스트/문제해결 가이드, 작업 일지 |

---

## 문서/기여 규칙

- 모든 문서는 한글로 작성합니다. 코드 식별자, API 필드명, 명령어, URL, provider 원문 용어만 예외입니다.
- 문서의 파일 위치 정보는 항상 프로젝트 루트 기준 상대 경로로 작성합니다 (로컬 절대 경로 금지).
- 사용자 가시 변경 시 `CHANGELOG.md`를 갱신합니다.
- 브랜치/PR 규칙과 개발 환경 설정은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.

---

## 라이선스 및 법적 고지

이 저장소의 코드는 GNU General Public License v3.0 or later (GPL-3.0-or-later) 라이선스를 따릅니다. 이 라이선스는 **이 저장소의 코드에만** 적용되며, 이 라이브러리가 감싸는 한국민족문화대백과사전 데이터 및 API의 이용은 한국학중앙연구원(The Academy of Korean Studies)이 정한 [OpenAPI 이용약관](https://encykorea.aks.ac.kr/Guide/OpenApiUse)을 따릅니다. 해당 데이터의 저작권은 한국학중앙연구원에 있으며, 이 프로젝트는 정부/공공기관 API에 대한 비공식 래퍼로서 원본 API의 가용성, 정확성, 지속성에 대해 어떠한 보증도 하지 않고 법적 효력을 보장하지 않습니다.
