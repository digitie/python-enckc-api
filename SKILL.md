---
name: enckc-api-python-builder
description: 한국학중앙연구원 한국민족문화대백과사전(Encykorea) OpenAPI용 Python 클라이언트를 구현, 확장, 디버그, 테스트할 때 사용한다. Encykorea, enckc, 민족문화대백과, 한국학중앙연구원, 백과사전, EID, MID, X-API-Key 관련 작업에 적용한다.
---

# 한국민족문화대백과사전 Python 라이브러리 빌더

`python-enckc-api`는 한국학중앙연구원 한국민족문화대백과사전 OpenAPI를 위한 Python 클라이언트이며 import package 이름은 `enckc`입니다.

## 프로젝트 불변조건

1. Base URL은 `https://devin.aks.ac.kr:8080/api`입니다.
2. 인증 헤더는 `X-API-Key: {API_KEY}`입니다.
3. 지원 대상 엔드포인트 6종:
   - `GET /api/articles` (전체 항목 리스트)
   - `GET /api/articles/search` (항목 검색)
   - `GET /api/articles/{eid}` (항목 내용 상세)
   - `GET /api/medias` (미디어 목록)
   - `GET /api/medias/search` (미디어 검색)
   - `GET /api/medias/{mid}` (미디어 내용 상세)
4. 모든 public 응답 모델은 `pydantic.BaseModel`에 `ConfigDict(frozen=True, extra="forbid", populate_by_name=True)`를 적용합니다.
5. 존재하지 않는 항목/미디어 조회 시 서버는 `204 No Content`를 반환하며, 클라이언트는 파싱 에러 없이 `None`을 반환합니다.
6. 검색 결과가 없으면 `items: []`, `totalCount: 0`, `currentCount: 0`으로 정상 반환됩니다.
7. 인증키는 `ENCKC_API_KEY` 환경변수 또는 `.env`/`.env.local`에서 읽어오며, 공백을 자동 제거하고 로그/메타데이터에 평문으로 남기지 않습니다.
8. 기본 테스트는 외부 네트워크 호출 없이 mock/fixture로 검증하며, 실서버 호출은 `@pytest.mark.integration`으로 분리합니다.
9. 문서의 파일 위치 정보는 항상 프로젝트 루트 기준 상대 경로로 작성합니다.
10. Python docstring과 주석은 한글로 작성합니다.
