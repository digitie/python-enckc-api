# API 지원 범위 (API Coverage)

한국학중앙연구원 한국민족문화대백과사전(Encykorea) OpenAPI의 전체 지원 엔드포인트 목록입니다.

## 엔드포인트 커버리지 (100% 지원)

| 엔드포인트 ID | 공식 경로 | 메서드 | 클라이언트 메서드 | 모델 | 상태 |
|---|---|---|---|---|---|
| `articles_list` | `/api/articles` | `GET` | `client.articles.list()` | `PaginatedResponse[ArticleListItem]` | 지원 완료 |
| `articles_search` | `/api/articles/search` | `GET` | `client.articles.search()` | `PaginatedResponse[ArticleListItem]` | 지원 완료 |
| `article_detail` | `/api/articles/{eid}` | `GET` | `client.articles.get()` | `ArticleDetail \| None` | 지원 완료 |
| `medias_list` | `/api/medias` | `GET` | `client.medias.list()` | `PaginatedResponse[MediaItem]` | 지원 완료 |
| `medias_search` | `/api/medias/search` | `GET` | `client.medias.search()` | `PaginatedResponse[MediaItem]` | 지원 완료 |
| `media_detail` | `/api/medias/{mid}` | `GET` | `client.medias.get()` | `MediaDetail \| None` | 지원 완료 |

## 기능별 지원 현황

- **동기 클라이언트 (`EnckcClient`)**: 6/6 완료
- **비동기 클라이언트 (`AsyncEnckcClient`)**: 6/6 완료
- **CLI 도구 (`enckc`)**: 6/6 완료
- **Streamlit 디버그 UI**: 6/6 완료
- **자동 페이지네이션 순회자 (`iter_all`)**: 항목 및 미디어 전체 지원
- **204 No Content 미존재 항목 처리**: 지원 완료
- **인증키 보안 마스킹**: 전 영역 적용 완료
