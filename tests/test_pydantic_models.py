"""Pydantic 응답 모델 및 유효성 검증 테스트."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from enckc.models import (
    ArticleListItem,
    MediaDetail,
    PaginatedResponse,
)


def test_article_list_item_frozen():
    item = ArticleListItem(
        eid="E0000001",
        headword="테스트",
    )
    with pytest.raises(ValidationError):
        # 불변 모델은 속성 직접 수정을 허용하지 않음
        item.headword = "수정"  # type: ignore[misc]


def test_article_extra_field_forbidden():
    with pytest.raises(ValidationError):
        # 정의되지 않은 추가 필드는 금지됨
        ArticleListItem(
            eid="E0000001",
            headword="테스트",
            unknown_field="unexpected",  # type: ignore[call-arg]
        )


def test_paginated_response_serialization_and_collection():
    item = ArticleListItem(
        eid="E0000001",
        headword="표제어",
        origin="漢字",
    )
    resp = PaginatedResponse[ArticleListItem](
        currentCount=1,
        totalCount=10,
        pageNo=1,
        pageSize=20,
        totalPage=1,
        items=[item],
    )
    # to_dict / to_json 검증
    dumped = resp.to_dict()
    assert dumped["currentCount"] == 1
    assert dumped["totalCount"] == 10
    assert dumped["items"][0]["eid"] == "E0000001"
    assert dumped["items"][0]["headword"] == "표제어"

    json_str = resp.to_json()
    parsed = json.loads(json_str)
    assert parsed["currentCount"] == 1

    # 컬렉션 프로토콜 (__len__, __iter__) 검증
    assert len(resp) == 1
    items_list = list(resp)
    assert len(items_list) == 1
    assert items_list[0].eid == "E0000001"


def test_media_detail_model():
    detail = MediaDetail.model_validate(
        {
            "mid": "0bad737c-471b-4fd5-86cf-10774faeaaa7",
            "mediaType": "사진",
            "koglType": "KOGL1",
            "caption": "테스트 캡션",
            "raw": {"mid": "0bad737c"},
        }
    )
    assert detail.mid == "0bad737c-471b-4fd5-86cf-10774faeaaa7"
    assert detail.media_type == "사진"
    assert detail.caption == "테스트 캡션"
    assert detail.raw == {"mid": "0bad737c"}
    assert detail.to_dict()["mediaType"] == "사진"
