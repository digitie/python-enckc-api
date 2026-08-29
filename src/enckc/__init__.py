"""한국민족문화대백과사전(Encykorea) OpenAPI Python 클라이언트 라이브러리."""

from __future__ import annotations

from ._credentials import (
    ENCKC_ENV_NAMES,
    api_key_for_gateway,
    env_names_for_gateway,
    first_env_value,
    load_local_env,
    normalize_api_key,
)
from .catalog import (
    API_DEFINITIONS,
    ApiDefinition,
    ParamSpec,
    get_api_catalog,
    get_api_catalog_entry,
    get_api_definition,
)
from .client import (
    ArticlesService,
    AsyncArticlesService,
    AsyncEnckcClient,
    AsyncMediasService,
    EnckcClient,
    MediasService,
)
from .debug import (
    DebugRun,
    debug_error,
    jsonable,
    redact_sensitive,
    save_fixture,
)
from .enums import (
    EnckcEndpoint,
    KoglType,
    MediaType,
)
from .exceptions import (
    EnckcAuthError,
    EnckcError,
    EnckcNotFoundError,
    EnckcParseError,
    EnckcRequestError,
    EnckcServerError,
)
from .metadata import (
    ResponseMetadata,
    make_response_metadata,
    redact_credentials_in_text,
    redact_url_credentials,
    sanitize_request_params,
)
from .models import (
    ArticleAlias,
    ArticleAttribute,
    ArticleDetail,
    ArticleListItem,
    EnckcModel,
    MediaDetail,
    MediaItem,
    PaginatedResponse,
    RelatedArticle,
)
from .pagination import (
    async_iter_pages,
    has_next_page,
    iter_pages,
    next_page_no,
)

__all__ = [
    # Clients
    "EnckcClient",
    "AsyncEnckcClient",
    "ArticlesService",
    "MediasService",
    "AsyncArticlesService",
    "AsyncMediasService",
    # Models
    "EnckcModel",
    "ArticleListItem",
    "ArticleDetail",
    "ArticleAlias",
    "ArticleAttribute",
    "RelatedArticle",
    "MediaItem",
    "MediaDetail",
    "PaginatedResponse",
    "ResponseMetadata",
    # Enums
    "EnckcEndpoint",
    "MediaType",
    "KoglType",
    # Exceptions
    "EnckcError",
    "EnckcAuthError",
    "EnckcNotFoundError",
    "EnckcRequestError",
    "EnckcServerError",
    "EnckcParseError",
    # Pagination
    "has_next_page",
    "next_page_no",
    "iter_pages",
    "async_iter_pages",
    # Credentials & Config
    "ENCKC_ENV_NAMES",
    "normalize_api_key",
    "api_key_for_gateway",
    "env_names_for_gateway",
    "first_env_value",
    "load_local_env",
    # Metadata & Security
    "make_response_metadata",
    "sanitize_request_params",
    "redact_credentials_in_text",
    "redact_url_credentials",
    # Debug & Catalog
    "API_DEFINITIONS",
    "ApiDefinition",
    "ParamSpec",
    "get_api_catalog",
    "get_api_catalog_entry",
    "get_api_definition",
    "DebugRun",
    "debug_error",
    "jsonable",
    "redact_sensitive",
    "save_fixture",
]
