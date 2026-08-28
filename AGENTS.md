# AGENTS.md

## 문서 언어 정책

이 저장소의 모든 Markdown/RST 문서는 한글로 작성합니다. 공식 API 필드명, 코드 식별자, 명령어, URL, provider 원문처럼 그대로 보존해야 하는 값만 영어를 유지합니다. 새 문서나 기존 문서를 수정할 때도 이 규칙을 우선합니다.

## 역할

이 문서는 `python-enckc-api` 저장소에서 작업하는 에이전트를 위한 운영 가이드입니다. import package는 `enckc`이며, 세부 API 명세는 `enckc-api.md`, 구현 불변조건은 `SKILL.md`, 아키텍처 결정은 `docs/decisions.md`를 함께 확인합니다.

## 지시 우선순위

1. 사용자 요청
2. 이 `AGENTS.md`
3. `SKILL.md`
4. `enckc-api.md`, `docs/decisions.md`, `docs/api-coverage.md`
5. `README.md` 및 나머지 `docs/`
6. 기존 코드와 테스트
7. 최소한의 되돌릴 수 있는 가정

## 프로젝트 기준

- `python-enckc-api`는 한국학중앙연구원 한국민족문화대백과사전(Encykorea) OpenAPI용 Python 클라이언트이며 import package 이름은 `enckc`입니다.
- 기본 API 엔드포인트 URL은 `https://devin.aks.ac.kr:8080/api`입니다.
- 인증 방식은 HTTP Header `X-API-Key`입니다.
- Python 지원 기준은 3.10 이상입니다.
- 런타임 의존성은 `httpx`, `pydantic`입니다.
- 기본 단위 테스트는 실제 Encykorea 네트워크 호출 없이 mock/fixture 기반으로 동작해야 합니다.
- 실제 API 테스트는 `integration` pytest marker를 사용합니다.

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
- `src/enckc/debug.py`: `api_catalog`, `run_debug` 카탈로그 및 픽스처 도우미
- `src/enckc/metadata.py`: 민감 정보 마스킹 및 `ResponseMetadata`

## 작업 후 체크리스트

- [ ] `pytest -q` 단위 테스트 통과
- [ ] `ruff check .` 린트 통과
- [ ] `mypy src/enckc` 엄격한 타입 검사 통과
- [ ] `docs/journal.md`에 작업 항목 추가 (역시간순)
- [ ] `docs/resume.md`의 진척도 갱신
- [ ] 사용자 가시 변경 시 `CHANGELOG.md` 갱신

## 검증 명령어

```bash
# 기본 품질 게이트
python -m pytest -q
python -m ruff check .
python -m mypy src/enckc

# 실제 API E2E 통합 테스트
python -m pytest -m integration -v
```
