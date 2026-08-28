# 반복하기 쉬운 실수 및 주의사항 (Repeated Mistakes)

## 1. 204 No Content를 파싱 에러로 처리
Encykorea API는 존재하지 않는 리소스에 대해 404가 아닌 204 No Content를 반환합니다. 빈 문자열 본문에 `response.json()`을 호출하면 `JSONDecodeError`가 발생하므로 반드시 상태 코드 204 및 빈 본문 검사를 먼저 수행해야 합니다.

## 2. API 키 평문 노출
로그, 예외 메시지, metadata에 `X-API-Key`를 평문으로 노출하면 보안상 위험합니다. 항상 `metadata.py`의 마스킹 도우미를 거쳐 출력해야 합니다.

## 3. Pydantic v2 frozen 모델 수정 시도
모든 응답 모델은 불변이므로 인스턴스 속성을 직접 변경할 수 없습니다. 변경이 필요하면 `model_copy(update={...})`를 사용해야 합니다.

## 4. 페이지 번호 0 전달
Encykorea API의 `pageNo`(`p`)는 1-indexed입니다. 0 이하의 값을 넘기지 않도록 방어 로직을 유지합니다.
