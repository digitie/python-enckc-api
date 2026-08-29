"""catalog.py / debug.py 및 EnckcClient.debug_fetch() 단위 테스트."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from enckc import EnckcClient, get_api_catalog, get_api_catalog_entry
from enckc.debug import DebugRun, debug_error, jsonable, redact_sensitive, save_fixture
from enckc.exceptions import EnckcAuthError

SAMPLE_ARTICLES_LIST = {
    "currentCount": 1,
    "totalCount": 100,
    "pageNo": 1,
    "pageSize": 20,
    "totalPage": 5,
    "items": [
        {
            "eid": "E0000002",
            "headword": "ㄱ",
            "articleAliases": [],
            "articleAttributes": [],
            "hashtags": [],
            "relatedArticles": [],
            "relatedMedias": [],
        }
    ],
}

SAMPLE_ARTICLE_DETAIL = {
    "eid": "E0029849",
    "headword": "세조",
    "articleAliases": [],
    "articleAttributes": [],
    "hashtags": [],
    "relatedArticles": [],
    "relatedMedias": [],
}


def test_get_api_catalog_has_all_six_endpoints():
    rows = get_api_catalog()
    keys = {row["service_key"] for row in rows}
    assert keys == {
        "articles_list",
        "articles_search",
        "article_detail",
        "medias_list",
        "medias_search",
        "media_detail",
    }
    for row in rows:
        assert row["data_source"] == "encykorea"
        assert "required_params" in row
        assert "optional_params" in row
        assert isinstance(row["required_params"], list)
        assert isinstance(row["optional_params"], list)


def test_get_api_catalog_entry_required_params():
    entry = get_api_catalog_entry("articles_search")
    required_names = {p["name"] for p in entry["required_params"]}
    assert required_names == {"q"}
    optional_names = {p["name"] for p in entry["optional_params"]}
    assert optional_names == {"p", "ps"}


def test_get_api_catalog_entry_unknown_key_raises():
    with pytest.raises(KeyError):
        get_api_catalog_entry("does_not_exist")


def test_debug_fetch_list_endpoint_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/articles"
        assert request.headers["x-api-key"] == "test-key"
        return httpx.Response(200, json=SAMPLE_ARTICLES_LIST)

    session = httpx.Client(transport=httpx.MockTransport(handler))
    with EnckcClient(api_key="test-key", session=session) as client:
        run = client.debug_fetch("articles_list", params={"p": 1, "ps": 20})

    assert isinstance(run, DebugRun)
    assert run.error is None
    assert run.response["status_code"] == 200
    assert run.processed is not None
    assert len(run.processed) == 1
    assert run.trace  # 비어있지 않아야 함
    # 인증 헤더는 request trace에서 마스킹되어야 함
    assert run.request["headers"]["X-API-Key"] == "***REDACTED***"


def test_debug_fetch_search_endpoint_routes_query_param():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/articles/search"
        assert request.url.params["q"] == "세종"
        return httpx.Response(200, json=SAMPLE_ARTICLES_LIST)

    session = httpx.Client(transport=httpx.MockTransport(handler))
    with EnckcClient(api_key="test-key", session=session) as client:
        run = client.debug_fetch("articles_search", params={"q": "세종", "p": 1, "ps": 20})

    assert run.error is None
    assert run.processed[0].eid == "E0000002"


def test_debug_fetch_detail_endpoint_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/articles/E0029849"
        return httpx.Response(200, json=SAMPLE_ARTICLE_DETAIL)

    session = httpx.Client(transport=httpx.MockTransport(handler))
    with EnckcClient(api_key="test-key", session=session) as client:
        run = client.debug_fetch("article_detail", params={"eid": "E0029849"})

    assert run.error is None
    assert run.processed["headword"] == "세조"


def test_debug_fetch_detail_endpoint_204_no_content():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(204, content=b"")

    session = httpx.Client(transport=httpx.MockTransport(handler))
    with EnckcClient(api_key="test-key", session=session) as client:
        run = client.debug_fetch("article_detail", params={"eid": "NONEXISTENT"})

    assert run.error is None
    assert run.parsed is None
    assert run.processed is None


def test_debug_fetch_missing_path_param_returns_structured_error():
    session = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200)))
    with EnckcClient(api_key="test-key", session=session) as client:
        run = client.debug_fetch("article_detail", params={})

    assert run.error is not None
    assert run.error["type"] == "ValueError"
    assert "traceback" in run.error


def test_debug_fetch_auth_error_becomes_structured_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"message": "invalid key"})

    session = httpx.Client(transport=httpx.MockTransport(handler))
    with EnckcClient(api_key="bad-key", session=session) as client:
        run = client.debug_fetch("articles_list", params={"p": 1, "ps": 20})

    assert run.error is not None
    assert run.error["type"] == "EnckcAuthError"
    assert run.error["status_code"] == 401
    assert run.error["failure_kind"] == "auth"
    assert "traceback" in run.error
    assert "message" in run.error


def test_jsonable_handles_pydantic_and_dataclass():
    run = DebugRun(
        function="x",
        input={"a": 1},
        request={},
        response={},
        parsed=None,
        processed=None,
        trace=["a"],
    )
    data = jsonable(run)
    assert data["function"] == "x"
    assert data["input"] == {"a": 1}


def test_redact_sensitive_masks_api_key_variants():
    payload = {
        "X-API-Key": "secret",
        "api_key": "secret2",
        "nested": {"ServiceKey": "secret3", "safe": "keep-me"},
        "list": [{"apikey": "secret4"}],
    }
    redacted = redact_sensitive(payload)
    assert redacted["X-API-Key"] == "***REDACTED***"
    assert redacted["api_key"] == "***REDACTED***"
    assert redacted["nested"]["ServiceKey"] == "***REDACTED***"
    assert redacted["nested"]["safe"] == "keep-me"
    assert redacted["list"][0]["apikey"] == "***REDACTED***"


def test_debug_error_generic_exception():
    payload = debug_error(ValueError("boom"))
    assert payload["type"] == "ValueError"
    assert payload["message"] == "boom"
    assert "traceback" in payload


def test_debug_error_enckc_error_includes_provider_fields():
    exc = EnckcAuthError(
        "invalid", endpoint="/articles", status_code=401, failure_kind="auth", retryable=False
    )
    payload = debug_error(exc)
    assert payload["type"] == "EnckcAuthError"
    assert payload["status_code"] == 401
    assert payload["failure_kind"] == "auth"
    assert payload["retryable"] is False
    assert payload["provider"] == "encykorea"


def test_save_fixture_round_trip(tmp_path: Path):
    path = save_fixture(
        base_dir=tmp_path,
        function_name="articles_list",
        case_name="Normal Case!",
        description="설명",
        input_data={"X-API-Key": "should-be-redacted"},
        request_data={"headers": {"X-API-Key": "should-be-redacted"}},
        response_data={"status_code": 200, "body": {"ok": True}},
        parsed_result=None,
        processed_result=[{"eid": "E0000002"}],
    )
    assert path.exists()
    saved: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    assert saved["input"]["X-API-Key"] == "***REDACTED***"
    assert saved["request"]["headers"]["X-API-Key"] == "***REDACTED***"
    assert saved["processed"] == [{"eid": "E0000002"}]
    assert saved["assertion"]["mode"] == "snapshot"


def test_save_fixture_refuses_overwrite_by_default(tmp_path: Path):
    kwargs = {
        "base_dir": tmp_path,
        "function_name": "articles_list",
        "case_name": "dup",
        "description": "d",
        "input_data": {},
        "request_data": {},
        "response_data": {},
        "parsed_result": None,
        "processed_result": None,
    }
    save_fixture(**kwargs)
    with pytest.raises(FileExistsError):
        save_fixture(**kwargs)
    # overwrite=True는 성공해야 함
    save_fixture(**kwargs, overwrite=True)
