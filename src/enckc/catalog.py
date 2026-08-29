"""API 카탈로그와 디버그 UI/폼 자동 생성을 위한 파라미터 메타데이터.

디버그 UI(예: `examples/streamlit_debug_ui.py`)가 엔드포인트별 `if endpoint_id ==
...` 분기 없이 폼 위젯을 자동 생성하고 요청을 라우팅할 수 있도록, 각 API의
실제 요청/응답 형태(파라미터, path 템플릿, 응답 모델)를 데이터로 표현합니다.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, Literal

from pydantic import BaseModel

from ._credentials import ENCKC_ENV_NAMES
from .models import ArticleDetail, ArticleListItem, MediaDetail, MediaItem

SERVICE_KEY_URL: Final = "https://encykorea.aks.ac.kr/Guide/OpenApiUse"
ParamKind = Literal["str", "int"]
ResponseKind = Literal["list", "detail"]
Facade = Literal["articles", "medias"]
Operation = Literal["list", "search", "get"]


@dataclass(frozen=True, slots=True)
class ParamSpec:
    """요청 파라미터 위젯 하나를 자동 생성하기 위한 최소 명세."""

    name: str
    kind: ParamKind = "str"
    required: bool = False
    default: Any = None
    help: str = ""
    enum: type[Enum] | None = None

    def enum_choices(self) -> list[str] | None:
        """Enum이 지정된 경우 selectbox choice 목록을 반환합니다."""

        if self.enum is None:
            return None
        return [str(member.value) for member in self.enum]


@dataclass(frozen=True, slots=True)
class ApiDefinition:
    """Encykorea OpenAPI 엔드포인트 하나의 카탈로그 정의."""

    key: str
    label: str
    method: str
    path_template: str
    description: str
    returns_description: str
    kind: ResponseKind
    facade: Facade
    operation: Operation
    required_params: tuple[ParamSpec, ...] = ()
    optional_params: tuple[ParamSpec, ...] = ()
    path_param_names: tuple[str, ...] = ()
    query_param: str | None = None
    item_model: type[BaseModel] | None = None
    detail_model: type[BaseModel] | None = None
    service_key_url: str = SERVICE_KEY_URL

    @property
    def all_params(self) -> tuple[ParamSpec, ...]:
        return self.required_params + self.optional_params


_PAGE_PARAMS: Final[tuple[ParamSpec, ...]] = (
    ParamSpec("p", kind="int", default=1, help="페이지 번호 (1부터 시작합니다)."),
    ParamSpec("ps", kind="int", default=20, help="페이지 크기 (한 페이지당 결과 수)."),
)

API_DEFINITIONS: Final[tuple[ApiDefinition, ...]] = (
    ApiDefinition(
        key="articles_list",
        label="전체 항목 리스트",
        method="GET",
        path_template="/articles",
        description="한국민족문화대백과사전 전체 항목 리스트를 페이지 단위로 조회합니다.",
        returns_description=(
            "표제어/분야/시대 등 요약 필드를 담은 ArticleListItem 목록과 페이지 정보를 반환합니다."
        ),
        kind="list",
        facade="articles",
        operation="list",
        optional_params=_PAGE_PARAMS,
        item_model=ArticleListItem,
    ),
    ApiDefinition(
        key="articles_search",
        label="항목 검색",
        method="GET",
        path_template="/articles/search",
        description="키워드로 한국민족문화대백과사전 표제어 및 항목을 검색합니다.",
        returns_description="검색어와 일치하는 ArticleListItem 목록과 총 검색 건수를 반환합니다.",
        kind="list",
        facade="articles",
        operation="search",
        query_param="q",
        required_params=(
            ParamSpec("q", kind="str", required=True, help="검색 키워드 (예: 세종)."),
        ),
        optional_params=_PAGE_PARAMS,
        item_model=ArticleListItem,
    ),
    ApiDefinition(
        key="article_detail",
        label="항목 내용 상세",
        method="GET",
        path_template="/articles/{eid}",
        description=(
            "항목 EID(예: E0029849)로 본문, 해설, 각주, 속성, "
            "연관항목/미디어 상세 내용을 조회합니다."
        ),
        returns_description=(
            "ArticleDetail(본문/속성/연관 항목·미디어 포함) 단일 객체를 반환하며, "
            "존재하지 않는 EID는 204 No Content -> None으로 처리됩니다."
        ),
        kind="detail",
        facade="articles",
        operation="get",
        required_params=(
            ParamSpec(
                "eid",
                kind="str",
                required=True,
                default="E0029849",
                help="항목 EID (예: E0029849).",
            ),
        ),
        path_param_names=("eid",),
        detail_model=ArticleDetail,
    ),
    ApiDefinition(
        key="medias_list",
        label="미디어 목록",
        method="GET",
        path_template="/medias",
        description=(
            "한국민족문화대백과사전 미디어(사진, 도면, 음원 등) "
            "전체 목록을 페이지 단위로 조회합니다."
        ),
        returns_description=(
            "MediaItem 목록(mid/media_type/url/caption 등)과 페이지 정보를 반환합니다."
        ),
        kind="list",
        facade="medias",
        operation="list",
        optional_params=_PAGE_PARAMS,
        item_model=MediaItem,
    ),
    ApiDefinition(
        key="medias_search",
        label="미디어 검색",
        method="GET",
        path_template="/medias/search",
        description="키워드로 미디어를 검색합니다.",
        returns_description="검색어와 일치하는 MediaItem 목록과 총 검색 건수를 반환합니다.",
        kind="list",
        facade="medias",
        operation="search",
        query_param="q",
        required_params=(
            ParamSpec("q", kind="str", required=True, help="검색 키워드 (예: 훈민정음)."),
        ),
        optional_params=_PAGE_PARAMS,
        item_model=MediaItem,
    ),
    ApiDefinition(
        key="media_detail",
        label="미디어 내용 상세",
        method="GET",
        path_template="/medias/{mid}",
        description="미디어 MID로 미디어 상세 정보(URL, 캡션, 저작권, 설명 등)를 조회합니다.",
        returns_description=(
            "MediaDetail(원본 URL/캡션/저작권 정보 포함) 단일 객체를 반환하며, "
            "존재하지 않는 MID는 204 No Content -> None으로 처리됩니다."
        ),
        kind="detail",
        facade="medias",
        operation="get",
        required_params=(
            ParamSpec(
                "mid",
                kind="str",
                required=True,
                default="0bad737c-471b-4fd5-86cf-10774faeaaa7",
                help="미디어 MID (UUID).",
            ),
        ),
        path_param_names=("mid",),
        detail_model=MediaDetail,
    ),
)

CATALOG_BY_KEY: Final[dict[str, ApiDefinition]] = {
    definition.key: definition for definition in API_DEFINITIONS
}


def get_api_definition(key: str | ApiDefinition) -> ApiDefinition:
    """key(또는 이미 ApiDefinition인 값)로 카탈로그 정의를 반환합니다."""

    if isinstance(key, ApiDefinition):
        return key
    try:
        return CATALOG_BY_KEY[key]
    except KeyError as exc:
        known = ", ".join(CATALOG_BY_KEY)
        raise KeyError(f"unknown enckc API catalog key {key!r}; known keys: {known}") from exc


def get_api_catalog() -> tuple[dict[str, Any], ...]:
    """Streamlit 등 UI에서 표로 보여주기 쉬운 API 카탈로그를 반환합니다."""

    return tuple(_catalog_entry(definition) for definition in API_DEFINITIONS)


def get_api_catalog_entry(key: str | ApiDefinition) -> dict[str, Any]:
    """엔드포인트 하나의 API 카탈로그 항목을 dict로 반환합니다."""

    return _catalog_entry(get_api_definition(key))


def _param_dict(spec: ParamSpec) -> dict[str, Any]:
    return {
        "name": spec.name,
        "required": spec.required,
        "kind": spec.kind,
        "default": spec.default,
        "help": spec.help,
        "enum_choices": spec.enum_choices(),
    }


def _catalog_entry(definition: ApiDefinition) -> dict[str, Any]:
    return {
        "service_key": definition.key,
        "dataset_name": definition.label,
        "dataset_label": f"{definition.label} ({definition.key})",
        "method": definition.method,
        "path": definition.path_template,
        "endpoint": definition.path_template,
        "description": definition.description,
        "returns_description": definition.returns_description,
        "kind": definition.kind,
        "data_source": "encykorea",
        "service_key_env_names": list(ENCKC_ENV_NAMES),
        "service_key_url": definition.service_key_url,
        "required_params": [_param_dict(spec) for spec in definition.required_params],
        "optional_params": [_param_dict(spec) for spec in definition.optional_params],
    }


__all__ = [
    "API_DEFINITIONS",
    "CATALOG_BY_KEY",
    "SERVICE_KEY_URL",
    "ApiDefinition",
    "ParamSpec",
    "get_api_catalog",
    "get_api_catalog_entry",
    "get_api_definition",
]
