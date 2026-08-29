# decisions.md — 의사결정 기록

이 문서는 이 프로젝트의 구조적 결정을 결정 시점 순서로 누적한다.
결정이 뒤집힐 때는 새 항목을 추가하고, 옛 항목은 지우지 않은 채
(supersedes: 위 항목)으로 표시한다.

## D-001: `requests` 대신 `httpx` 기반 동기/비동기 통합 전송 계층을 사용한다

- 상태: accepted
- 날짜: 2026-08-29

### 컨텍스트

동기 클라이언트(`EnckcClient`)와 비동기 클라이언트(`AsyncEnckcClient`)를 동일한 파사드 구조(`client.articles.*`, `client.medias.*`)로 함께 제공해야 했다. `requests`는 네이티브 비동기를 지원하지 않아 별도의 비동기 HTTP 라이브러리를 추가로 들여와야 하는 문제가 있었다.

### 결정

전송 계층을 `httpx` 하나로 통일하고, 동기/비동기 클라이언트가 `src/enckc/_http.py`의 공통 로직(세션 생성, 지수 백오프 재시도, 상태 코드 매핑)을 공유하도록 한다.

### 근거

- `async`/`await` 네이티브 지원으로 별도의 비동기 HTTP 의존성이 불필요하다.
- 커넥션 풀 재사용 등 동기/비동기 공통 최적화를 단일 코드 경로로 유지할 수 있다.
- 모던 파이썬 비동기 생태계와의 호환성이 좋다.

### 결과

- `src/enckc/_http.py`가 동기/비동기 세션 생성과 재시도 로직을 함께 담당한다.
- 런타임 의존성이 `httpx`, `pydantic` 두 가지로 최소화되었다.

## D-002: 모든 공개 응답 모델에 Pydantic v2 frozen 설정을 적용한다

- 상태: accepted
- 날짜: 2026-08-29

### 컨텍스트

API 응답을 그대로 노출하는 모델이 호출부에서 변경 가능하면, 캐싱이나 재사용 시 예기치 않은 데이터 오염이 발생할 수 있다. 또한 Encykorea API 스키마가 예고 없이 필드를 추가/변경할 가능성에 대비해 계약 위반을 조기에 감지할 수단이 필요했다.

### 결정

`src/enckc/models.py`의 모든 공개 응답 모델에 `ConfigDict(frozen=True, extra="forbid", populate_by_name=True)`를 적용한다.

### 근거

- 불변 모델은 캐싱 안전성과 예측 가능성을 보장한다.
- `extra="forbid"`는 API 스키마 변경(필드 추가 등)을 파싱 시점에 즉시 드러낸다.

### 결과

- `ArticleListItem`, `ArticleDetail`, `MediaItem`, `PaginatedResponse` 등 모든 응답 모델이 불변이며 `model_dump(mode="json")`으로 안전하게 직렬화된다.
- 스키마 변경으로 인한 `pydantic.ValidationError`는 `EnckcParseError`로 통일해 노출한다(D-003과 연동).

## D-003: 204 No Content는 예외가 아닌 `None`으로 안전하게 처리한다

- 상태: accepted
- 날짜: 2026-08-29

### 컨텍스트

존재하지 않는 `eid`/`mid`로 상세 조회를 하면 Encykorea 서버는 404가 아닌 HTTP 204 No Content를 반환한다. 이를 파싱 에러나 예외로 처리하면 "항목이 없다"는 정상적인 경우를 오류로 오인하게 된다.

### 결정

`articles.get()` / `medias.get()` 호출 시 204 No Content 응답을 예외로 던지지 않고 `None`을 반환한다.

### 근거

- 백과사전 항목 조회의 특성상 "결과 없음"은 예외적 상황이 아니라 흔한 정상 흐름이다.
- Python 관용구상 `None` 반환이 호출부에서 가장 직관적으로 다루기 쉽다.

### 결과

- `AGENTS.md`의 절대 하지 말 것 목록에 "204 No Content를 파싱 에러로 처리 금지"가 명시되어 있다.
- 관련 동작은 mock 기반 단위 테스트로 검증되며, 실서버 회귀는 `integration` 마커 테스트로 확인한다.

## D-004: `client.articles.*` / `client.medias.*` 파사드 패턴으로 API 서비스를 분리한다

- 상태: accepted
- 날짜: 2026-08-29

### 컨텍스트

공식 API는 항목(article) 6종 중 3종, 미디어(media) 3종으로 도메인이 명확히 구분된다. 이를 클라이언트 최상위에 평면적으로 나열하면 메서드가 늘어날수록 가독성이 떨어진다.

### 결정

`EnckcClient`/`AsyncEnckcClient` 아래에 `articles`, `medias` 두 서비스 파사드를 두어 도메인별로 메서드를 그룹화한다. 자주 쓰이는 메서드는 필요 시 최상위 클라이언트에도 편의 alias로 제공할 수 있다.

### 근거

- 6개 엔드포인트를 의미 단위로 그룹화해 API 탐색성과 가독성을 높인다.
- 단순 전달용 wrapper/adapter 계층을 추가하지 않고도(AGENTS.md DO NOT 5번) 일관된 구조를 유지할 수 있다.

### 결과

- `src/enckc/client.py`에 `ArticlesService`, `MediasService`가 정의되어 있고, CLI(`enckc search-articles`, `enckc article` 등)도 동일한 도메인 구분을 따른다.
