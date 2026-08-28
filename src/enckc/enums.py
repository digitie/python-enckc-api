"""한국민족문화대백과사전 OpenAPI 열거형 및 상수."""

from __future__ import annotations

from enum import Enum


class EnckcEndpoint(str, Enum):
    """한국민족문화대백과사전 OpenAPI 엔드포인트."""

    ARTICLES = "/articles"
    ARTICLES_SEARCH = "/articles/search"
    ARTICLE_DETAIL = "/articles/{eid}"
    MEDIAS = "/medias"
    MEDIAS_SEARCH = "/medias/search"
    MEDIA_DETAIL = "/medias/{mid}"


class MediaType(str, Enum):
    """미디어 유형."""

    PHOTO = "사진"
    DRAWING = "도면"
    AUDIO = "음원"
    VIDEO = "동영상"
    DOCUMENT = "문서"


class KoglType(str, Enum):
    """공공누리(KOGL) 유형."""

    KOGL1 = "KOGL1"  # 제1유형: 출처표시
    KOGL2 = "KOGL2"  # 제2유형: 출처표시 + 상업적이용금지
    KOGL3 = "KOGL3"  # 제3유형: 출처표시 + 변경금지
    KOGL4 = "KOGL4"  # 제4유형: 출처표시 + 상업적이용금지 + 변경금지
