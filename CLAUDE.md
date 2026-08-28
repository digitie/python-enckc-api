# CLAUDE.md — 프로젝트 컨텍스트

이 파일은 Claude Code, Antigravity 등의 에이전트들이 매 세션 시작 시 자동으로 로드하여 읽는 진입점 파일입니다.

## 프로젝트 현황

한국학중앙연구원 한국민족문화대백과사전(Encykorea) OpenAPI용 Python 클라이언트 라이브러리(`enckc`).
전체 6개 엔드포인트(전체 항목, 항목 검색, 항목 상세, 미디어 목록, 미디어 검색, 미디어 상세)에 대한 동기/비동기 통합 지원, Pydantic v2 불변 응답 모델, 스트리밍 페이지네이션, CLI 명령행 도구, 디버그 카탈로그 UI가 완비되어 있습니다.

## 로컬 개발 환경

```text
python-enckc-api/
├── src/enckc/        # 패키지 소스 코드
│   ├── client.py     # EnckcClient / AsyncEnckcClient
│   ├── models.py     # Pydantic v2 frozen 모델
│   ├── _http.py      # httpx 기반 전송 계층
│   └── ...
├── tests/            # 단위 및 통합 테스트 스위트
├── tools/            # Streamlit 디버그 UI
└── docs/             # 설계 결정, 일지, 커버리지 문서
```

## 빠른 검증 명령

```bash
# 기본 품질 게이트
python -m pytest -q
python -m ruff check .
python -m mypy src/enckc

# 실제 API E2E 검증
python -m pytest -m integration -v
```

## 주요 결정 사항

- **ADR-001**: `httpx` 기반 동기/비동기 통합 전송 계층
- **ADR-002**: Pydantic v2 frozen 모델 (`extra="forbid"`)
- **ADR-003**: 204 No Content 안전 처리 (항목/미디어 미존재 시 `None` 반환)
- **ADR-004**: 인증키 자동 마스킹 및 보안 격리
