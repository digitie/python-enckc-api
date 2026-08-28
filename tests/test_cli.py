"""CLI 명령행 도구 테스트."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from enckc.cli import main
from enckc.models import ArticleDetail, ArticleListItem, PaginatedResponse


@patch("enckc.cli.EnckcClient")
def test_cli_articles_list(mock_client_cls, capsys):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.articles.list.return_value = PaginatedResponse[ArticleListItem](
        currentCount=1,
        totalCount=1,
        pageNo=1,
        pageSize=20,
        totalPage=1,
        items=[ArticleListItem(eid="E0000002", headword="ㄱ")],
    )

    exit_code = main(["--api-key", "test-key", "articles", "-p", "1", "-s", "20"])
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["totalCount"] == 1
    assert data["items"][0]["eid"] == "E0000002"


@patch("enckc.cli.EnckcClient")
def test_cli_article_get(mock_client_cls, capsys):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.articles.get.return_value = ArticleDetail(
        eid="E0029849",
        headword="세조",
        summary="세조 요약",
    )

    exit_code = main(["--api-key", "test-key", "article", "E0029849"])
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["eid"] == "E0029849"
    assert data["headword"] == "세조"
