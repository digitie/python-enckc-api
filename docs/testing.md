# 테스트 가이드 (Testing Guide)

`python-enckc-api`의 테스트 원칙과 실행 가이드입니다.

## 테스트 구조

- `tests/test_client.py`: 동기 클라이언트 단위 테스트 (Mock 기반)
- `tests/test_async_client.py`: 비동기 클라이언트 단위 테스트 (Mock 기반)
- `tests/test_pydantic_models.py`: Pydantic 응답 모델 검증
- `tests/test_http.py`: HTTP 재시도, 지수 백오프, 에러 상태 코드 매핑 검증
- `tests/test_pagination.py`: 페이지네이션 순회 검증
- `tests/test_exceptions.py`: 예외 메타데이터 및 계층 검증
- `tests/test_cli.py`: CLI 인자 파싱 및 실행 검증
- `tests/test_credentials.py`: 인증키 로더 및 공백 정규화 검증
- `tests/test_public_api.py`: public export 심볼 및 타입 검증
- `tests/test_live_services.py`: 실제 발급된 API 키로 실서버를 호출하는 E2E 통합 테스트

## 테스트 실행

### 1. 기본 단위 테스트 (네트워크 호출 없음)
```bash
python -m pytest -q
```

### 2. 실제 API E2E 통합 테스트
`.env.local` 파일 또는 환경변수에 `ENCKC_API_KEY`가 설정되어 있어야 합니다:
```bash
python -m pytest -m integration -v
```
