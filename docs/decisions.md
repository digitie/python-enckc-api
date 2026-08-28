# Architecture Decision Records (ADR)

## ADR-001: httpx 기반 전송 계층

- **상태**: 확정
- **결정**: `requests` 대신 `httpx`를 사용하여 동기/비동기 클라이언트를 단일 인터페이스 구조로 일관되게 제공한다.
- **이유**: `async/await` 네이티브 지원, 커넥션 풀 재사용, 모던 파이썬 비동기 생태계 완벽 호환.

## ADR-002: Pydantic v2 frozen 불변 모델

- **상태**: 확정
- **결정**: 모든 공개 응답 모델에 `ConfigDict(frozen=True, extra="forbid", populate_by_name=True)`를 적용한다.
- **이유**: 모델 불변성을 통한 캐싱 안전성, 예측 가능성, API 스키마 변경 시 조기 감지.

## ADR-003: 204 No Content 안전 처리

- **상태**: 확정
- **결정**: 미존재 `eid` 또는 `mid` 요청 시 204 No Content가 오면 예외를 던지지 않고 `None`을 반환한다.
- **이유**: 백과사전 항목 조회의 특성상 조회가 없을 때 `None` 반환이 가장 직관적이고 Pythonic함.

## ADR-004: 파사드 패턴 기반 API 서비스 분리

- **상태**: 확정
- **결정**: `client.articles.*`와 `client.medias.*`로 도메인을 분리하고, 자주 쓰이는 메서드는 최상위 클라이언트에도 편의 alias를 제공한다.
- **이유**: 6개 엔드포인트의 의미적 그룹화 및 가독성 극대화.
