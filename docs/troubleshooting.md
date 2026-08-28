# 문제 해결 가이드 (Troubleshooting)

## 1. 401 Unauthorized 오류

- **원인**: `X-API-Key` 헤더 누락 또는 유효하지 않은 API 키.
- **해결책**:
  - 발급받은 키가 올바른지 확인합니다 (`.env.local`의 `ENCKC_API_KEY`).
  - 신규 발급된 키는 Encykorea 시스템 등록 후 약 30분의 활성화 대기 시간이 필요할 수 있습니다.

## 2. 항목/미디어 조회 시 `None` 반환

- **원인**: 전달한 `eid` 또는 `mid`가 데이터베이스에 존재하지 않음 (서버 HTTP 204 No Content).
- **해결책**:
  - `eid` 형식(`E0029849`) 또는 `mid` UUID 형식을 확인합니다.
  - `search_articles()`를 통해 정확한 `eid`를 먼저 검색해 봅니다.

## 3. Windows 환경에서 인코딩 깨짐

- **원인**: Windows 기본 콘솔 인코딩(CP949) 문제.
- **해결책**:
  - `PYTHONIOENCODING=utf-8` 환경변수를 설정하거나, CLI 및 클라이언트 내부의 UTF-8 버퍼 출력을 활용합니다.
