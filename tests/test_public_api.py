"""공개 API 심볼 노출 및 일관성 테스트."""

from __future__ import annotations

import enckc


def test_public_api_all_exported():
    for name in enckc.__all__:
        assert hasattr(enckc, name), f"Symbol {name} listed in __all__ but not exported"


def test_public_classes():
    assert issubclass(enckc.ArticleDetail, enckc.ArticleListItem)
    assert issubclass(enckc.ArticleListItem, enckc.EnckcModel)
    assert issubclass(enckc.EnckcAuthError, enckc.EnckcError)
