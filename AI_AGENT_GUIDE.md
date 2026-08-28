# AI 에이전트 개발 및 운영 가이드

본 문서는 ChatGPT Codex, Claude Code, Google Antigravity 등 다양한 AI 에이전트가 `python-enckc-api` 저장소에서 협업할 때 준수해야 하는 운영 지침입니다.

## 1. 아키텍처 및 코딩 표준

- **타입 안전성**: 모든 public 인터페이스와 내부 함수는 엄격한 타입 힌팅을 적용하며, `mypy --strict`를 통과해야 합니다.
- **불변성**: Pydantic v2 frozen 모델을 기반으로 하며 `model_dump()`, `model_dump_json()`을 제공합니다.
- **동기/비동기 대칭성**: `EnckcClient`와 `AsyncEnckcClient`는 동일한 메서드 시그니처와 파사드 구조(`articles`, `medias`)를 유지합니다.
- **에러 핸들링**: HTTP 상태 코드 및 예외 상황은 명확한 `EnckcError` 서브클래스로 변환하여 전달합니다.

## 2. 보안 정책

- 커밋, 로그, 테스트 파일, fixture에 실제 API 키를 절대 노출하지 않습니다.
- 로컬 개발 시에는 `.env.local`을 사용하며, git 추적에서 제외됩니다.
- `metadata.py`의 `sanitize_request_params` 함수를 통해 모든 메타데이터에서 인증 파라미터를 마스킹합니다.

## 3. 품질 검증 절차

작업 완료 후 반드시 다음 3단계 검증을 순차적으로 통과해야 합니다:
1. `pytest -q`: 전체 단위 테스트
2. `ruff check .`: 코드 스타일 및 린트
3. `mypy src/enckc`: 정적 타입 검사
