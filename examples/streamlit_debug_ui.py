"""Streamlit 기반 한국민족문화대백과사전(Encykorea) API 디버그 카탈로그 뷰어."""
# ruff: noqa: E402,I001

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
for module_name, module in list(sys.modules.items()):
    if module_name != "enckc" and not module_name.startswith("enckc."):
        continue
    module_file = getattr(module, "__file__", None)
    if module_file is not None and not Path(module_file).resolve().is_relative_to(SRC):
        del sys.modules[module_name]

try:
    import pandas as pd
    import streamlit as st
except ModuleNotFoundError as exc:  # pragma: no cover - 선택 실행 도구
    raise SystemExit('Streamlit UI를 쓰려면 `pip install -e ".[debug-ui]"`를 실행하세요.') from exc

from enckc import (
    ENCKC_ENV_NAMES,
    EnckcClient,
    first_env_value,
    get_api_catalog,
    jsonable,
    load_local_env,
    save_fixture,
)


def main() -> None:
    st.set_page_config(page_title="Encykorea API Debug", layout="wide")
    st.title("Encykorea OpenAPI Debug")

    # 1. Data source / API 선택 (카탈로그가 6개뿐이므로 API 단일 selectbox만 사용)
    rows = list(get_api_catalog())
    labels = [row["dataset_label"] for row in rows]
    selected_label = st.sidebar.selectbox("API", labels)
    selected = rows[labels.index(selected_label)]

    # 2. 설명 캡션 2줄 (무엇을 하는 API인지 + 어떤 데이터를 반환하는지)
    st.sidebar.caption(selected["description"])
    st.sidebar.caption(selected["returns_description"])

    # 3. Environment: 실제 서비스가 읽는 env var 이름을 그대로 사용
    st.sidebar.subheader("Environment")
    env_sources = _env_key_sources(ENCKC_ENV_NAMES)
    environment = "manual"
    if env_sources:
        environment = st.sidebar.radio(
            "Environment", ["env", "manual"], horizontal=True, key="environment"
        )
        if environment == "env":
            info = env_sources[0]
            st.sidebar.caption(f"{info['name']} 값을 사용합니다. Source: {info['source']}")
    else:
        st.sidebar.caption(
            f"{' / '.join(ENCKC_ENV_NAMES)} 값이 감지되지 않았습니다. 수동 입력을 사용하세요."
        )

    # 4. Auth: 이 API는 쿼리파라미터가 아니라 HTTP 요청 헤더 X-API-Key로 인증합니다.
    st.sidebar.subheader("Auth")
    st.sidebar.caption(
        "이 API는 `serviceKey` 쿼리파라미터가 아니라 HTTP 요청 헤더 `X-API-Key`로 인증합니다."
    )
    if environment == "manual":
        api_key = st.sidebar.text_input(
            "X-API-Key (header)",
            value="",
            type="password",
            placeholder="직접 입력",
            help=f"사용 가능한 env 이름: {', '.join(ENCKC_ENV_NAMES)}",
        )
    else:
        api_key = _first_env_value(ENCKC_ENV_NAMES)

    # 5. 서비스키 발급 링크 버튼
    st.sidebar.link_button("서비스키 발급/확인", selected["service_key_url"])

    # 6. Timeout
    timeout = st.sidebar.number_input(
        "Timeout",
        min_value=1.0,
        max_value=60.0,
        value=10.0,
        step=1.0,
        help="API 요청 timeout seconds입니다.",
    )

    # 7. Fixture 저장 기준 디렉터리
    fixture_base_dir = _fixture_base_dir_sidebar()

    tabs = st.tabs(
        [
            "Raw Response",
            "Pydantic Model",
            "Processed Result",
            "Validation Errors",
            "Debug Trace",
            "Fixture / Testcase",
        ]
    )

    with tabs[0]:
        _raw_response_tab(selected, api_key, timeout=float(timeout))
    with tabs[1]:
        _pydantic_model_tab(selected)
    with tabs[2]:
        _processed_result_tab(selected)
    with tabs[3]:
        _validation_errors_tab(selected)
    with tabs[4]:
        _debug_trace_tab(rows, selected)
    with tabs[5]:
        _fixture_tab(fixture_base_dir, selected)


def _raw_response_tab(selected: dict[str, Any], api_key: str, *, timeout: float) -> None:
    st.subheader(selected["dataset_name"])
    st.caption(f"{selected['method']} {selected['path']}")

    submitted, params, missing = _request_form(selected)

    st.subheader("Request params preview")
    st.json(params)

    if not submitted:
        return
    if missing:
        st.error("필수 파라미터를 입력하세요: " + ", ".join(missing))
        return
    if not api_key or not api_key.strip():
        st.error(
            "API 키가 설정되지 않았습니다. "
            "사이드바에서 X-API-Key를 입력하거나 환경변수를 사용하세요."
        )
        return

    client: EnckcClient | None = None
    try:
        client = EnckcClient(api_key=api_key, timeout=timeout, retries=0)
        run = client.debug_fetch(selected["service_key"], params=params)
    except Exception as exc:  # noqa: BLE001 - 클라이언트 생성 실패 등 사전 검증 단계 오류
        st.error(str(exc))
        return
    finally:
        if client is not None:
            client.close()

    _store_run(selected, run)
    if run.error:
        st.error(run.error["message"])
    st.json(jsonable(run.response))


def _request_form(selected: dict[str, Any]) -> tuple[bool, dict[str, Any], list[str]]:
    required_specs: list[dict[str, Any]] = selected["required_params"]
    optional_specs: list[dict[str, Any]] = selected["optional_params"]
    key_prefix = f"{selected['data_source']}:{selected['service_key']}"

    with st.form(f"request-form:{key_prefix}"):
        st.subheader("Required parameters")
        if required_specs:
            required_values = _render_param_grid(required_specs, key_prefix=key_prefix)
        else:
            st.caption("이 API에는 필수 파라미터가 없습니다.")
            required_values = {}

        st.subheader("Optional parameters")
        if optional_specs:
            optional_values = _render_param_grid(optional_specs, key_prefix=key_prefix)
        else:
            st.caption("이 API에는 선택 파라미터가 없습니다.")
            optional_values = {}

        submitted = st.form_submit_button("Run selected API")

    params = {**required_values, **optional_values}
    missing = [
        spec["name"] for spec in required_specs if not str(params.get(spec["name"], "")).strip()
    ]
    return submitted, params, missing


def _render_param_grid(specs: list[dict[str, Any]], *, key_prefix: str) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for index in range(0, len(specs), 2):
        columns = st.columns(2)
        for column, spec in zip(columns, specs[index : index + 2], strict=False):
            with column:
                values[spec["name"]] = _render_param_widget(spec, key_prefix=key_prefix)
    return values


def _render_param_widget(spec: dict[str, Any], *, key_prefix: str) -> Any:
    """카탈로그의 파라미터 메타데이터(kind/enum_choices)만으로 위젯을 자동 생성합니다.

    함수명/엔드포인트별 하드코딩 분기가 없습니다: enum 파라미터가 있으면 selectbox,
    정수형이면 number_input, 그 외에는 text_input을 사용합니다.
    """

    widget_key = f"{key_prefix}:param:{spec['name']}"
    label = f"{spec['name']}{'*' if spec['required'] else ''}"
    help_text = spec["help"] or None

    if spec["enum_choices"]:
        choices: list[str] = spec["enum_choices"]
        default_index = choices.index(spec["default"]) if spec["default"] in choices else 0
        return st.selectbox(label, choices, index=default_index, help=help_text, key=widget_key)

    if spec["kind"] == "int":
        default_value = int(spec["default"]) if spec["default"] is not None else 1
        return int(
            st.number_input(
                label, min_value=1, value=default_value, step=1, help=help_text, key=widget_key
            )
        )

    default_text = str(spec["default"]) if spec["default"] is not None else ""
    return st.text_input(label, value=default_text, help=help_text, key=widget_key)


def _pydantic_model_tab(selected: dict[str, Any]) -> None:
    run = _current_run(selected)
    if run is None:
        st.info("Raw Response 탭에서 선택한 API를 실행하면 여기에서 Pydantic 모델을 확인합니다.")
        return
    if run.error:
        st.warning("실행 중 오류가 있습니다. Validation Errors 탭을 확인하세요.")
    st.json(jsonable(run.parsed))


def _processed_result_tab(selected: dict[str, Any]) -> None:
    run = _current_run(selected)
    if run is None:
        st.info("Raw Response 탭에서 API를 실행하면 처리된 결과를 표시합니다.")
        return
    data = jsonable(run.processed)
    if data is None:
        st.info("결과가 없습니다 (204 No Content 또는 미조회 상태).")
    elif isinstance(data, list):
        if data:
            st.dataframe(pd.json_normalize(data, sep="."), width="stretch", hide_index=True)
        else:
            st.info("결과가 없습니다 (0건).")
    else:
        st.json(data)


def _validation_errors_tab(selected: dict[str, Any]) -> None:
    run = _current_run(selected)
    if run is None:
        st.info("아직 실행된 API가 없습니다.")
        return
    if not run.error:
        st.success("현재 실행 결과에서 validation error 또는 exception이 없습니다.")
        return
    st.error(run.error["message"])
    st.json(run.error)


def _debug_trace_tab(rows: list[dict[str, Any]], selected: dict[str, Any]) -> None:
    run = _current_run(selected)

    st.subheader("Catalog")
    st.dataframe(rows, width="stretch", hide_index=True)

    st.subheader("Selected API")
    st.json(selected)
    st.link_button("서비스키 발급/확인", selected["service_key_url"])
    st.caption(f"credential env: {', '.join(selected['service_key_env_names'])}")

    if run is not None:
        st.subheader("Trace")
        st.write(run.trace)
        st.subheader("Request")
        st.json(jsonable(run.request))
        st.subheader("Response")
        st.json(jsonable({k: v for k, v in run.response.items() if k != "body"}))
        if run.catalog is not None:
            st.dataframe(
                pd.json_normalize([run.catalog], sep="."), width="stretch", hide_index=True
            )


def _fixture_tab(fixture_base_dir: str, selected: dict[str, Any]) -> None:
    run = _current_run(selected)
    if run is None:
        st.info("Raw Response 탭에서 API를 실행한 뒤 fixture를 저장할 수 있습니다.")
        st.caption("Fixture base dir")
        st.code(fixture_base_dir, language=None)
        return

    with st.expander("Save as fixture", expanded=True):
        case_name = st.text_input("Case name", value=f"{selected['service_key']}_normal")
        description = st.text_area("Description", value=f"{selected['dataset_name']} 정상 케이스")
        assertion_mode = st.selectbox(
            "Assertion mode",
            ["snapshot", "schema_only", "required_fields", "count"],
        )
        exclude_fields_raw = st.text_input(
            "Exclude fields",
            value="fetched_at, request_id, updated_at",
        )
        required_fields_raw = st.text_input("Required fields", value="")
        overwrite = st.checkbox("Overwrite existing fixture", value=False)

        assertion = {
            "mode": assertion_mode,
            "exclude_fields": [
                value.strip() for value in exclude_fields_raw.split(",") if value.strip()
            ],
            "required_fields": [
                value.strip() for value in required_fields_raw.split(",") if value.strip()
            ],
        }

        st.subheader("Fixture preview")
        st.json(
            {
                "function": selected["service_key"],
                "input": jsonable(run.input),
                "request": jsonable(run.request),
                "response": jsonable(run.response),
                "processed": jsonable(run.processed),
                "assertion": assertion,
            }
        )

        if st.button("Save as fixture"):
            try:
                path = save_fixture(
                    base_dir=fixture_base_dir,
                    function_name=selected["service_key"],
                    case_name=case_name,
                    description=description,
                    input_data=run.input,
                    request_data=run.request,
                    response_data=run.response,
                    parsed_result=run.parsed,
                    processed_result=run.processed,
                    assertion=assertion,
                    overwrite=overwrite,
                )
            except Exception as exc:  # noqa: BLE001 - 저장 실패 사유를 그대로 노출
                st.error(str(exc))
            else:
                st.success(f"Saved: {path}")


def _env_key_sources(env_names: tuple[str, ...]) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    for name in env_names:
        value = os.getenv(name)
        if value is not None and value.strip():
            sources.append({"name": name, "source": "process env"})
            return sources

    local_env = load_local_env(start=ROOT)
    for name in env_names:
        value = local_env.get(name)
        if value is not None and value.strip():
            sources.append({"name": name, "source": ".env/.env.local"})
            return sources
    return sources


def _first_env_value(env_names: tuple[str, ...]) -> str:
    try:
        return first_env_value(env_names)
    except ValueError:
        return ""


def _fixture_base_dir_sidebar() -> str:
    st.sidebar.subheader("Fixtures")
    candidates = _fixture_dir_candidates()
    options = [str(path) for path in candidates]
    custom_label = "Custom..."
    selected = st.sidebar.selectbox("Fixture base dir", [*options, custom_label])
    if selected == custom_label:
        selected = st.sidebar.text_input(
            "Custom fixture base dir",
            value=str((ROOT / "tests" / "fixtures").resolve()),
        )
    st.sidebar.caption(selected)
    return selected


def _fixture_dir_candidates() -> list[Path]:
    preferred = [
        ROOT / "tests" / "fixtures",
        ROOT / "tests",
        ROOT / "examples",
        ROOT,
    ]
    candidates: list[Path] = []
    for path in preferred:
        resolved = path.resolve()
        if resolved not in candidates:
            candidates.append(resolved)
    return candidates


def _store_run(selected: dict[str, Any], run: Any) -> None:
    st.session_state["last_run"] = {
        "selection_key": _selection_key(selected),
        "run": run,
    }


def _current_run(selected: dict[str, Any]) -> Any | None:
    stored = st.session_state.get("last_run")
    if not isinstance(stored, dict):
        return None
    if stored.get("selection_key") != _selection_key(selected):
        return None
    return stored.get("run")


def _selection_key(selected: dict[str, Any]) -> str:
    return f"{selected['data_source']}:{selected['service_key']}"


if __name__ == "__main__":
    main()
