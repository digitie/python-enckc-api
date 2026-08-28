# 한국민족문화대백과사전(Encykorea) OpenAPI 상세 명세

한국학중앙연구원(The Academy of Korean Studies)에서 제공하는 한국민족문화대백과사전 OpenAPI의 기술 규격 및 응답 형식 문서입니다.

공식 안내 사이트: [https://encykorea.aks.ac.kr/Guide/OpenApiUse](https://encykorea.aks.ac.kr/Guide/OpenApiUse)

---

## 1. 기본 통신 규격

- **기본 엔드포인트 URL**: `https://devin.aks.ac.kr:8080/api`
- **프로토콜**: HTTPS / RESTful JSON
- **인증 방식**: HTTP 요청 헤더에 발급받은 API 키를 `X-API-Key`로 전송
  - `X-API-Key: YOUR_ENCKC_API_KEY_HERE`
- **응답 인코딩**: UTF-8

---

## 2. API 엔드포인트 목록

| 번호 | 명칭 | HTTP 메서드 및 경로 | 주요 파라미터 |
|---|---|---|---|
| 1 | 전체 항목 리스트 | `GET /api/articles` | `p`(페이지번호), `ps`(페이지크기) |
| 2 | 항목 검색 | `GET /api/articles/search` | `q`(검색어), `p`(페이지번호), `ps`(페이지크기) |
| 3 | 항목 내용 상세 | `GET /api/articles/{eid}` | `eid`(항목 식별자) |
| 4 | 미디어 목록 | `GET /api/medias` | `p`(페이지번호), `ps`(페이지크기) |
| 5 | 미디어 검색 | `GET /api/medias/search` | `q`(검색어), `p`(페이지번호), `ps`(페이지크기) |
| 6 | 미디어 내용 상세 | `GET /api/medias/{mid}` | `mid`(미디어 UUID) |

---

## 3. 엔드포인트별 상세 규격

### 3.1. 전체 항목 리스트 (`GET /api/articles`)

한국민족문화대백과사전에 등재된 75,000건 이상의 전체 표제어 항목 목록을 페이지 단위로 조회합니다.

#### 요청 파라미터
- `p` (선택, 기본값 1): 요청 페이지 번호
- `ps` (선택, 기본값 20): 페이지당 항목 수

#### 응답 예시 (200 OK)
```json
{
  "currentCount": 20,
  "totalCount": 75835,
  "pageNo": 1,
  "pageSize": 20,
  "totalPage": 3792,
  "items": [
    {
      "eid": "E0000002",
      "url": "https://encykorea.aks.ac.kr/Article/E0000002",
      "headword": "ㄱ",
      "origin": "",
      "headwordOrigin": "ㄱ",
      "field": "언어/문자",
      "primaryTypePartA": "개념",
      "primaryTypePartB": "",
      "primaryType": "개념",
      "secondaryType": "NONE",
      "contentsType": "개념",
      "era": "조선/조선 전기",
      "definition": "한글 자음에서 첫 번째로 등장하는 글자.",
      "summary": "",
      "body": "",
      "footNote": "",
      "reference": "",
      "writerInfo": "강신항(성균관대학교, 국어학)",
      "lastModifiedTime": "2026-05-31T22:42:47.22",
      "headMID": "5d2519e3-878b-47e6-bfd5-58e3c6cc0c8d",
      "headMedia": {
        "mid": "5d2519e3-878b-47e6-bfd5-58e3c6cc0c8d",
        "mediaType": "사진",
        "koglType": "KOGL1",
        "url": "https://devin.aks.ac.kr/image/5d2519e3-878b-47e6-bfd5-58e3c6cc0c8d?preset=orig",
        "caption": "훈민정음언해 / ㄱ",
        "description": "한글 자모의 첫째 글자. &apos;기역&apos;이라 읽는다.",
        "copyrightDisplay": "한국학중앙연구원"
      },
      "articleAliases": [
        {
          "word": "기역",
          "aliasType": "일반ː이칭"
        }
      ],
      "articleAttributes": [],
      "hashtags": [],
      "relatedArticles": [],
      "relatedMedias": []
    }
  ],
  "requestUrl": "/api/articles",
  "queryString": "?p=1&ps=20"
}
```

---

### 3.2. 항목 검색 (`GET /api/articles/search`)

지정한 키워드로 표제어, 본문, 속성을 검색합니다.

#### 요청 파라미터
- `q` (필수): 검색 키워드 (URL 인코딩)
- `p` (선택, 기본값 1): 페이지 번호
- `ps` (선택, 기본값 20): 페이지당 항목 수

#### 응답 예시
```json
{
  "currentCount": 2,
  "totalCount": 27,
  "pageNo": 1,
  "pageSize": 20,
  "totalPage": 2,
  "items": [
    {
      "eid": "E0075386",
      "url": "https://encykorea.aks.ac.kr/Article/E0075386",
      "headword": "세종 비암사 소조 아미타여래 좌상",
      "origin": "世宗 碑岩寺 塑造 阿彌陀如來 坐像",
      "headwordOrigin": "세종 비암사 소조 아미타여래 좌상(世宗 碑岩寺 塑造 阿彌陀如來 坐像)",
      "field": "예술·체육/조각 | 종교·철학/불교",
      "primaryTypePartA": "작품",
      "primaryTypePartB": "불상",
      "primaryType": "작품/불상",
      "secondaryType": "시도문화유산",
      "contentsType": "작품/불상, 시도문화유산",
      "era": "조선/조선 전기",
      "definition": "세종특별자치시 전의면 비암사 극락보전에 봉안되어 있는 조선 전기의 소조아미타여래좌상."
    }
  ],
  "requestUrl": "/api/articles/search",
  "queryString": "?q=세종&p=1&ps=20"
}
```

---

### 3.3. 항목 내용 상세 (`GET /api/articles/{eid}`)

항목 고유 EID(예: `E0029849`)를 전달하여 본문(Markdown), 각주, 참고문헌, 속성, 연관 항목 및 연관 미디어를 포함한 전체 상세 정보를 조회합니다.

#### 응답 예시
```json
{
  "eid": "E0029849",
  "url": "https://encykorea.aks.ac.kr/Article/E0029849",
  "headword": "세조",
  "origin": "世祖",
  "headwordOrigin": "세조(世祖)",
  "field": "역사/조선시대사",
  "primaryTypePartA": "인물",
  "primaryTypePartB": "전통 인물",
  "primaryType": "인물/전통 인물",
  "secondaryType": "NONE",
  "contentsType": "인물/전통 인물",
  "era": "조선/조선 전기",
  "definition": "조선의 제7대(재위: 1455년~1468년) 왕.",
  "summary": "세조는 조선의 제7대 왕이다. 재위 기간은 1455~1468년으로...",
  "body": "# 개설\r\n재위 1455년(세조 1)∼1468년(세조 14)...",
  "footNote": "[^1]: 임금의 자리를 물려받음...",
  "reference": "- 『세종실록(世宗實錄)』\n- 『문종실록(文宗實錄)』...",
  "writerInfo": "이재호",
  "lastModifiedTime": "2022-09-29T18:07:41.363",
  "headMID": "00000000-0000-0000-0000-000000000000",
  "headMedia": null,
  "articleAliases": [
    {
      "word": "수지(粹之)",
      "aliasType": "인물ː자"
    }
  ],
  "articleAttributes": [
    {
      "groupName": "인물/전통 인물",
      "attrName": "출생 연도",
      "attrValue": "1417년(태종 17)"
    }
  ],
  "relatedArticles": [
    {
      "targetEID": "E0019665",
      "headword": "문종",
      "origin": "文宗",
      "headwordOrigin": "문종(文宗)"
    }
  ],
  "relatedMedias": []
}
```

---

### 3.4. 미디어 목록 (`GET /api/medias`)

대백과사전에 등록된 79,000건 이상의 전체 미디어 목록을 페이지 단위로 조회합니다.

#### 요청 파라미터
- `p` (선택, 기본값 1): 페이지 번호
- `ps` (선택, 기본값 20): 페이지당 미디어 수

#### 응답 예시
```json
{
  "currentCount": 20,
  "totalCount": 79725,
  "pageNo": 1,
  "pageSize": 20,
  "totalPage": 3987,
  "items": [
    {
      "mid": "0bad737c-471b-4fd5-86cf-10774faeaaa7",
      "mediaType": "사진",
      "koglType": "KOGL1",
      "url": "https://devin.aks.ac.kr/image/0bad737c-471b-4fd5-86cf-10774faeaaa7?preset=orig",
      "caption": "사례편람 / 자최관",
      "description": "",
      "copyrightDisplay": "한국학중앙연구원"
    }
  ],
  "requestUrl": "/api/medias",
  "queryString": "?p=1&ps=20"
}
```

---

### 3.5. 미디어 검색 (`GET /api/medias/search`)

키워드로 미디어를 검색합니다.

#### 요청 파라미터
- `q` (필수): 검색 키워드
- `p` (선택, 기본값 1): 페이지 번호
- `ps` (선택, 기본값 20): 페이지당 미디어 수

---

### 3.6. 미디어 내용 상세 (`GET /api/medias/{mid}`)

미디어 고유 식별자 MID(UUID 형식)를 전달하여 미디어의 원본 URL, 캡션, 라이선스, 저작권자 상세 정보를 조회합니다.

#### 응답 예시
```json
{
  "mid": "0bad737c-471b-4fd5-86cf-10774faeaaa7",
  "mediaType": "사진",
  "koglType": "KOGL1",
  "url": "https://devin.aks.ac.kr/image/0bad737c-471b-4fd5-86cf-10774faeaaa7?preset=orig",
  "caption": "사례편람 / 자최관",
  "description": "",
  "copyrightDisplay": "한국학중앙연구원"
}
```

---

## 4. HTTP 상태 코드 및 특이사항

- **200 OK**: 요청 성공 및 결과 반환
- **204 No Content**: 요청한 `eid` 또는 `mid`가 데이터베이스에 존재하지 않음 (본문 빈 문자열)
- **401 Unauthorized**: `X-API-Key` 헤더 누락 또는 유효하지 않은 인증키
- **429 Too Many Requests**: 요청 한도 초과 (Rate Limiting)
- **500 Internal Server Error**: 서버 측 내부 오류
