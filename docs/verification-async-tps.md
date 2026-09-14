# 비동기/TPS 전환 검증

- 독립 적대적 리뷰 2인 최종 승인. 문서 예제와 func/fetch_page 키워드 회귀를 수정했다.
- 오프라인 72개 및 14개 subtest 통과, Ruff/mypy/compileall 통과.
- live E2E 7개는 모두 서버 연결/timeout 단계에서 실패했다. HTTP 응답이나 실제 데이터는
  검증하지 못했고, HTTP 403이 관측된 것은 아니다.
- Windows와 WSL의 별도 curl 요청도 devin.aks.ac.kr:8080 연결에 실패했다.
- 2026-09-14 [공식 안내](https://encykorea.aks.ac.kr/Guide/OpenApiUse)에서도 같은 서버
  주소와 X-API-Key 인증 헤더를 확인했다. 기본 URL은 변경하지 않는다.
- 사용자의 403이 없는 저장소는 머지하라는 지시에 따라 위 live 제한을 공개하고 머지한다.
  네트워크 실패를 성공으로 집계하지 않으며, 서버 연결 복구 후 실제 데이터 재검증이 필요하다.
