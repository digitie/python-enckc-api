# 에이전트 안내서 (Agent Guide)

AI 에이전트가 `python-enckc-api` 코드베이스를 탐색하고 수정할 때 참고하는 요약 가이드입니다.

## 핵심 규칙
1. `src/enckc` 내부의 모든 코드는 타입 힌트를 필수로 작성합니다.
2. API 응답 모델은 `models.py`에 정의하며, `EnckcModel`을 상속합니다.
3. 테스트 코드는 `tests/`에 작성하며, 외부 네트워크를 호출하지 않는 단위 테스트를 기본으로 합니다.
4. 실제 네트워크 테스트는 `@pytest.mark.integration` 데코레이터를 붙여 격리합니다.
