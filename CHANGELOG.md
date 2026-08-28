# CHANGELOG.md

모든 주목할 만한 변경 사항은 이 파일에 기록됩니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)을 따르며,
이 프로젝트는 [Semantic Versioning](https://semver.org/lang/ko/)을 준수합니다.

## [0.1.0] - 2026-08-29

### 추가
- 한국학중앙연구원 한국민족문화대백과사전(Encykorea) OpenAPI 클라이언트 초기 릴리스
- 전체 6개 엔드포인트 구현:
  - `articles.list()`: 전체 항목 목록 조회
  - `articles.search()`: 항목 키워드 검색
  - `articles.get()`: 항목 상세 본문/각주/속성 조회 (EID)
  - `medias.list()`: 미디어 전체 목록 조회
  - `medias.search()`: 미디어 키워드 검색
  - `medias.get()`: 미디어 상세 정보 조회 (MID)
- `httpx` 기반 동기(`EnckcClient`) 및 비동기(`AsyncEnckcClient`) 클라이언트
- Pydantic v2 불변 응답 모델 (`ConfigDict(frozen=True, extra="forbid")`)
- `iter_pages`, `async_iter_pages`, `iter_all` 자동 페이지네이션 순회자
- 204 No Content 안전 처리 (`get()` 호출 시 `None` 반환)
- `enckc` CLI 명령행 도구 지원
- `tools/debug_streamlit.py` 실시간 디버그 카탈로그 UI
- 계층적 예외(`EnckcError`, `EnckcAuthError`, `EnckcNotFoundError` 등)
- 인증키 자동 정규화 및 보안 마스킹
