"""한국민족문화대백과사전 OpenAPI Pydantic 응답 모델."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from .metadata import ResponseMetadata

ItemT = TypeVar("ItemT")


class EnckcModel(BaseModel):
    """불변 공개 `enckc` 응답 모델의 기본 클래스."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    def to_dict(self) -> dict[str, Any]:
        """Pydantic v2 직렬화로 JSON 호환 dict를 반환합니다."""
        return self.model_dump(mode="json", by_alias=True)

    def to_json(self) -> str:
        """Pydantic v2 직렬화로 JSON 문자열을 반환합니다."""
        return self.model_dump_json(by_alias=True)


class MediaItem(EnckcModel):
    """미디어 항목 정보 모델."""

    mid: str
    media_type: str | None = Field(default=None, alias="mediaType")
    kogl_type: str | None = Field(default=None, alias="koglType")
    url: str | None = None
    caption: str | None = None
    description: str | None = None
    copyright_display: str | None = Field(default=None, alias="copyrightDisplay")


class MediaDetail(MediaItem):
    """미디어 상세 정보 및 메타데이터 모델."""

    raw: dict[str, Any] = Field(default_factory=dict)
    metadata: ResponseMetadata | None = None


class ArticleAlias(EnckcModel):
    """항목 이칭/별칭 모델."""

    word: str
    alias_type: str | None = Field(default=None, alias="aliasType")


class ArticleAttribute(EnckcModel):
    """항목 속성 정보 모델."""

    group_name: str | None = Field(default=None, alias="groupName")
    attr_name: str | None = Field(default=None, alias="attrName")
    attr_value: str | None = Field(default=None, alias="attrValue")


class RelatedArticle(EnckcModel):
    """연관 항목 요약 모델."""

    target_eid: str = Field(alias="targetEID")
    target_url: str | None = Field(default=None, alias="targetUrl")
    headword: str
    origin: str | None = None
    headword_origin: str | None = Field(default=None, alias="headwordOrigin")
    field: str | None = None
    primary_type_part_a: str | None = Field(default=None, alias="primaryTypePartA")
    primary_type_part_b: str | None = Field(default=None, alias="primaryTypePartB")
    primary_type: str | None = Field(default=None, alias="primaryType")
    secondary_type: str | None = Field(default=None, alias="secondaryType")
    contents_type: str | None = Field(default=None, alias="contentsType")
    era: str | None = None
    definition: str | None = None
    writer_profile: str | None = Field(default=None, alias="writerProfile")
    head_mid: str | None = Field(default=None, alias="headMID")
    head_media: MediaItem | None = Field(default=None, alias="headMedia")


class ArticleListItem(EnckcModel):
    """항목 목록 및 검색 결과 항목 모델."""

    eid: str
    url: str | None = None
    headword: str
    origin: str | None = None
    headword_origin: str | None = Field(default=None, alias="headwordOrigin")
    field: str | None = None
    primary_type_part_a: str | None = Field(default=None, alias="primaryTypePartA")
    primary_type_part_b: str | None = Field(default=None, alias="primaryTypePartB")
    primary_type: str | None = Field(default=None, alias="primaryType")
    secondary_type: str | None = Field(default=None, alias="secondaryType")
    contents_type: str | None = Field(default=None, alias="contentsType")
    era: str | None = None
    definition: str | None = None
    summary: str | None = None
    body: str | None = None
    foot_note: str | None = Field(default=None, alias="footNote")
    reference: str | None = None
    writer_info: str | None = Field(default=None, alias="writerInfo")
    last_modified_time: str | None = Field(default=None, alias="lastModifiedTime")
    head_mid: str | None = Field(default=None, alias="headMID")
    head_media: MediaItem | None = Field(default=None, alias="headMedia")
    article_aliases: list[ArticleAlias] = Field(default_factory=list, alias="articleAliases")
    article_attributes: list[ArticleAttribute] = Field(
        default_factory=list, alias="articleAttributes"
    )
    hashtags: list[str] = Field(default_factory=list)
    related_articles: list[RelatedArticle] = Field(default_factory=list, alias="relatedArticles")
    related_medias: list[MediaItem] = Field(default_factory=list, alias="relatedMedias")


class ArticleDetail(ArticleListItem):
    """항목 상세 본문 및 메타데이터 모델."""

    raw: dict[str, Any] = Field(default_factory=dict)
    metadata: ResponseMetadata | None = None


class PaginatedResponse(EnckcModel, Generic[ItemT]):
    """페이지네이션 응답 래퍼 모델."""

    current_count: int = Field(alias="currentCount")
    total_count: int = Field(alias="totalCount")
    page_no: int = Field(alias="pageNo")
    page_size: int = Field(alias="pageSize")
    total_page: int = Field(alias="totalPage")
    items: list[ItemT] = Field(default_factory=list)
    request_url: str | None = Field(default=None, alias="requestUrl")
    query_string: str | None = Field(default=None, alias="queryString")
    metadata: ResponseMetadata | None = None

    def __iter__(self) -> Iterator[ItemT]:  # type: ignore[override]
        """응답 항목 리스트를 직접 순회합니다."""
        return iter(self.items)

    def __len__(self) -> int:
        """현재 페이지에 포함된 항목 개수를 반환합니다."""
        return len(self.items)
