# AGENTS.md

## 목표

`python-enckc-api`는 한국학중앙연구원(AKS) 한국민족문화대백과사전(Encykorea) OpenAPI를 위한 Python 클라이언트입니다. import package 이름은 `enckc`이며, `httpx` 기반 동기(`EnckcClient`)/비동기(`AsyncEnckcClient`) 클라이언트, 불변 Pydantic v2 응답 모델, 자동 페이지네이션 순회자, `enckc` CLI를 제공합니다. 세부 API 명세는 `enckc-api.md`, 구현 불변조건은 `SKILL.md`, 아키텍처 결정은 `docs/decisions.md`를 함께 확인합니다.

## Think Before Coding

- 변경 전 `enckc-api.md`(API 규격)와 `docs/decisions.md`(ADR)를 확인해 기존 계약을 깨지 않는지 확인할 것.
- 동기/비동기 두 클라이언트에 동시에 영향을 주는 변경인지 `client.py`의 대칭 구조를 기준으로 먼저 파악할 것.
- 204 No Content, 빈 검색 결과, 스키마 검증 실패 등 이미 합의된 엣지케이스 처리 방식을 재확인 없이 바꾸지 말 것.

## Simplicity First

- `client.articles.*` / `client.medias.*` 파사드 구조를 유지하고, 단순 전달용 wrapper/adapter 계층을 추가하지 말 것.
- `httpx`, `pydantic`의 역할을 대체하지 않는 새 런타임 의존성은 추가하지 말 것.
- 응답 모델은 frozen Pydantic v2 모델을 그대로 확장하고, 별도 직렬화 레이어를 만들지 말 것.

## Surgical Changes

- 한 PR/커밋은 하나의 엔드포인트 또는 하나의 관심사(동기 vs 비동기, 클라이언트 vs CLI)에 집중할 것.
- `src/enckc/metadata.py`의 인증키 마스킹처럼 보안에 관련된 코드는 최소한으로, 의도가 드러나게 수정할 것.
- 관련 없는 포맷팅/리네이밍을 실제 기능 변경과 같은 커밋에 섞지 말 것.

## Goal-Driven Execution

- 작업 완료 기준은 "테스트가 통과한다"가 아니라 "요청된 동작이 mock 기반 테스트로 검증됨"으로 정의할 것.
- 6개 엔드포인트 중 일부만 변경하더라도 동기/비동기/CLI 3면의 대칭성이 깨지지 않았는지 확인할 것.
- 사용자가 명시적으로 요청하지 않은 범위(예: `examples/` Streamlit 디버그 UI)까지 손대지 말 것.

## Practical Bias

- API 응답 스키마가 예고 없이 바뀔 수 있다는 전제로, 파싱 실패는 `EnckcParseError`로 통일해 노출하고 원본 예외를 삼키지 말 것.
- 확신이 서지 않는 실제 API 동작은 `integration` 마커 테스트로 실서버 검증하되, 기본 테스트 스위트에는 포함하지 말 것.
- 현재 6개 엔드포인트 범위를 넘는 이론적 추상화(플러그인 시스템 등)는 만들지 말 것.

## 문서 언어 정책

이 저장소의 모든 Markdown/RST 문서는 한글로 작성합니다. 공식 API 필드명, 코드 식별자, 명령어, URL, provider 원문처럼 그대로 보존해야 하는 값만 영어를 유지합니다. 새 문서나 기존 문서를 수정할 때도 이 규칙을 우선합니다.

## 식별자 표

이름이 여러 개 혼재하므로 참고합니다.

| 이름 종류 | 값 |
|---|---|
| PyPI 배포명 | `python-enckc-api` |
| import 패키지명 | `enckc` |
| GitHub 저장소 | `digitie/python-enckc-api` |
| 환경변수 prefix | `ENCKC_` (예: `ENCKC_API_KEY`) |

## 프로젝트 기준

- 기본 API 엔드포인트 URL은 `https://devin.aks.ac.kr:8080/api`입니다.
- 인증 방식은 HTTP 요청 헤더 `X-API-Key`이며, 쿼리파라미터(`serviceKey`) 방식이 아닙니다.
- Python 지원 기준은 3.10 이상입니다.
- 기본 단위 테스트는 실제 Encykorea 네트워크 호출 없이 mock/fixture 기반으로 동작해야 합니다. 실제 API 테스트는 `integration` pytest marker를 사용합니다.

## 지시 우선순위

사용자 요청 > `AGENTS.md` > `README.md`/기존 테스트

## 절대 하지 말 것 (DO NOT)

1. **`main` 직접 푸시 금지** — 반드시 feature 브랜치 + PR 생성 후 검증을 거쳐 머지합니다.
2. **실제 `api_key` 평문 노출 금지** — 출력, 로그, 커밋, fixture에 절대로 남기지 않습니다. `.env.local`을 활용하고 `metadata.py`에서 항상 마스킹합니다.
3. **기본 테스트에서 실제 API 호출 금지** — 네트워크 호출 없는 mock/fixture 기반으로 검증해야 합니다.
4. **204 No Content를 파싱 에러로 처리 금지** — 미존재 항목/미디어에 대해 204 No Content가 오면 정상적인 `None`으로 처리합니다.
5. **불필요한 wrapper/adapter 계층 추가 금지** — 단순 전달용 wrapper를 지양하고, 일관된 public client 구조를 유지합니다.
6. **문서에 로컬 절대 경로 기재 금지** — 문서의 파일 위치 정보는 항상 프로젝트 루트 기준 상대 경로(예: `src/enckc/client.py`)로 작성합니다.

## 모듈 지도

- `src/enckc/client.py`: `EnckcClient`, `AsyncEnckcClient`, `ArticlesService`, `MediasService`
- `src/enckc/models.py`: frozen Pydantic v2 모델 (`ArticleListItem`, `ArticleDetail`, `MediaItem`, `PaginatedResponse`)
- `src/enckc/_http.py`: `httpx` 동기/비동기 세션 생성, 지수 백오프 재시도, 상태 코드 매핑
- `src/enckc/_credentials.py`: 인증키 정규화와 `.env`/`.env.local` 로딩
- `src/enckc/exceptions.py`: 계층적 `EnckcError` 예외 클래스
- `src/enckc/pagination.py`: `iter_pages`, `async_iter_pages`, `has_next_page`, `next_page_no`
- `src/enckc/cli.py`: `enckc` 명령행 도구
- `src/enckc/catalog.py`: `get_api_catalog`/`get_api_catalog_entry` API 카탈로그 및 파라미터 메타데이터
  (`required_params`/`optional_params`), `EnckcClient.debug_fetch()`가 라우팅에 사용
- `src/enckc/debug.py`: `DebugRun`, `jsonable`, `redact_sensitive`, `debug_error`, `save_fixture`
  디버그 UI/픽스처 도우미
- `src/enckc/metadata.py`: 민감 정보 마스킹 및 `ResponseMetadata`

## 작업 후 체크리스트

- [ ] `pytest -q` 단위 테스트 통과
- [ ] `ruff check .` 린트 통과
- [ ] `mypy src/enckc` 엄격한 타입 검사 통과
- [ ] `docs/journal.md`에 작업 항목 추가 (역시간순)
- [ ] `docs/resume.md`의 진척도 갱신
- [ ] 사용자 가시 변경 시 `CHANGELOG.md` 갱신

## 검증

```bash
# 기본 품질 게이트
python -m pytest -q
python -m ruff check .
python -m mypy src/enckc

# 실제 API E2E 통합 테스트
python -m pytest -m integration -v
```
