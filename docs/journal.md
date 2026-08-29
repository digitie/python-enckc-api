# 개발 일지 (Journal)

## 2026-08-29 (2)
- **작업 내용**:
  - `tools/debug_streamlit.py`(엔드포인트별 하드코딩 분기, 탭 1개, 세션 상태 없음, fixture 저장
    불가)를 khoa 참고 구현 패턴에 맞춰 `examples/streamlit_debug_ui.py`로 재작성 및 이동
  - 선행 작업으로 `src/enckc/catalog.py` 신설: `ApiDefinition`/`ParamSpec` 및
    `get_api_catalog()`/`get_api_catalog_entry()`로 6개 엔드포인트의 `required_params`/
    `optional_params` 메타데이터를 데이터로 표현 (폼 위젯 자동 생성의 근거)
  - `src/enckc/debug.py`의 `DebugRun`을 input/request/response/parsed/processed/trace/error/
    catalog로 확장, `jsonable`/`redact_sensitive`/`debug_error`/`save_fixture` 추가
  - `EnckcClient.debug_fetch()` 신설: 카탈로그의 facade/operation/kind/item_model/detail_model
    메타데이터로 요청을 라우팅하는 제네릭 메서드(엔드포인트별 if 분기 없음)
  - 표준 6탭(Raw Response/Pydantic Model/Processed Result/Validation Errors/Debug Trace/
    Fixture) 구성, 데이터소스:API로 스코프한 `st.session_state` 저장, X-API-Key 헤더 인증에
    맞춘 Auth 섹션 라벨 조정
  - `tests/test_debug.py` 신규 (catalog/debug_fetch/jsonable/redact_sensitive/debug_error/
    save_fixture 15개 단위 테스트), `pyproject.toml`의 `debug-ui` extra에 `pandas>=2` 추가
- **관련 파일**:
  - `src/enckc/catalog.py`, `src/enckc/debug.py`, `src/enckc/client.py`, `src/enckc/__init__.py`
  - `examples/streamlit_debug_ui.py` (구 `tools/debug_streamlit.py`)
  - `tests/test_debug.py`, `pyproject.toml`
  - `README.md`, `AGENTS.md`, `CHANGELOG.md`, `docs/resume.md`

## 2026-08-29
- **작업 내용**:
  - `python-enckc-api` 신규 저장소 구축 및 전체 6개 OpenAPI 엔드포인트 구현 완료
  - `httpx` 기반 동기(`EnckcClient`) 및 비동기(`AsyncEnckcClient`) 클라이언트 구현
  - Pydantic v2 불변 모델(`ConfigDict(frozen=True, extra="forbid", populate_by_name=True)`), `to_dict()`, `to_json()`, 컬렉션 프로토콜 구현
  - `iter_pages`, `async_iter_pages`, `iter_all` 자동 페이지네이션 및 `max_items` 정밀 제어
  - 204 No Content 미존재 리소스 안전 처리 (`None` 반환)
  - `enckc` CLI 명령행 도구 및 Streamlit 실시간 디버그 카탈로그 UI 구현
  - 2명의 적대적 서브에이전트(아키텍처/타입 전문가, 보안/E2E 전문가) 코드 감사 및 11개 지적사항 전원 수정
  - `feat/enckc-core-api` 브랜치에서 `main` 브랜치로 검증 후 PR 머지 완료
- **관련 파일**:
  - `src/enckc/*`
  - `tests/*`
  - `tools/debug_streamlit.py`
  - `README.md`, `enckc-api.md`, `AGENTS.md`, `SKILL.md`, `docs/*`
