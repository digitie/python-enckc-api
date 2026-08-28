"""Streamlit 기반 한국민족문화대백과사전 API 디버그 카탈로그 뷰어."""
# ruff: noqa: E402,I001

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    import streamlit as st
except ModuleNotFoundError as exc:
    raise SystemExit(
        'Streamlit UI를 사용하려면 `pip install -e ".[debug-ui]"`를 실행하세요.'
    ) from exc

from enckc import (
    EnckcClient,
    api_catalog,
    load_local_env,
)


def main() -> None:
    st.set_page_config(page_title="Encykorea OpenAPI Debug", layout="wide")
    st.title("한국민족문화대백과사전 OpenAPI Debugger")

    entries = api_catalog()
    entry_labels = [f"[{e.method}] {e.label} ({e.path})" for e in entries]
    selected_idx = st.sidebar.selectbox(
        "API 엔드포인트 선택", range(len(entries)), format_func=lambda i: entry_labels[i]
    )
    selected = entries[selected_idx]

    st.sidebar.caption(selected.description)
    st.sidebar.markdown(f"[공식 가이드 바로가기]({selected.guide_url})")

    # API Key resolution
    local_env = load_local_env()
    default_key = local_env.get("ENCKC_API_KEY", "")
    api_key = st.sidebar.text_input("X-API-Key", value=default_key, type="password")

    st.subheader(f"{selected.label} ({selected.path})")

    # Parameter inputs
    col1, col2, col3 = st.columns([1, 1, 2])
    params: dict[str, Any] = {}

    if selected.endpoint_id in {"articles_list", "medias_list"}:
        with col1:
            params["p"] = st.number_input("페이지 번호 (p)", min_value=1, value=1, step=1)
        with col2:
            params["ps"] = st.number_input(
                "페이지 크기 (ps)", min_value=1, max_value=100, value=20, step=1
            )

    elif selected.endpoint_id == "articles_search":
        with col1:
            params["q"] = st.text_input("검색어 (q)", value="세종")
        with col2:
            params["p"] = st.number_input("페이지 번호 (p)", min_value=1, value=1, step=1)
        with col3:
            params["ps"] = st.number_input(
                "페이지 크기 (ps)", min_value=1, max_value=100, value=20, step=1
            )

    elif selected.endpoint_id == "medias_search":
        with col1:
            params["q"] = st.text_input("검색어 (q)", value="훈민정음")
        with col2:
            params["p"] = st.number_input("페이지 번호 (p)", min_value=1, value=1, step=1)
        with col3:
            params["ps"] = st.number_input(
                "페이지 크기 (ps)", min_value=1, max_value=100, value=20, step=1
            )

    elif selected.endpoint_id == "article_detail":
        with col1:
            params["eid"] = st.text_input("항목 EID (eid)", value="E0029849")

    elif selected.endpoint_id == "media_detail":
        with col1:
            params["mid"] = st.text_input(
                "미디어 MID (mid)", value="0bad737c-471b-4fd5-86cf-10774faeaaa7"
            )

    if st.button("API 요청 실행", type="primary"):
        if not api_key:
            st.error(
                "API 키가 설정되지 않았습니다. 사이드바에 키를 입력하거나 .env.local에 설정하세요."
            )
            return

        client = EnckcClient(api_key=api_key)
        try:
            with st.spinner("요청 중..."):
                if selected.endpoint_id == "articles_list":
                    res = client.articles.list(page=params["p"], page_size=params["ps"])
                    st.success(
                        f"조회 성공 (현재 {res.current_count}건 / "
                        f"총 {res.total_count}건, {res.page_no}/{res.total_page} 페이지)"
                    )
                    st.json(res.model_dump(mode="json"))

                elif selected.endpoint_id == "articles_search":
                    res = client.articles.search(
                        params["q"], page=params["p"], page_size=params["ps"]
                    )
                    st.success(f"검색 성공 (검색어: '{params['q']}', {res.total_count}건 발견)")
                    st.json(res.model_dump(mode="json"))

                elif selected.endpoint_id == "article_detail":
                    article = client.articles.get(params["eid"])
                    if article is None:
                        st.warning(
                            f"해당 EID({params['eid']})의 항목을 찾을 수 없습니다 (204 No Content)."
                        )
                    else:
                        st.success(f"항목 조회 성공: {article.headword} ({article.origin or ''})")
                        tab1, tab2, tab3 = st.tabs(["본문 미리보기", "구조화 데이터", "Raw JSON"])
                        with tab1:
                            st.markdown(f"### {article.headword} ({article.origin or ''})")
                            st.caption(
                                f"분야: {article.field} | 시대: {article.era} | "
                                f"집필: {article.writer_info}"
                            )
                            if article.summary:
                                st.info(article.summary)
                            if article.body:
                                st.markdown(article.body)
                        with tab2:
                            st.write("**이칭/별칭:**", [a.word for a in article.article_aliases])
                            st.write(
                                "**속성 정보:**",
                                [
                                    f"{attr.group_name}/{attr.attr_name}: {attr.attr_value}"
                                    for attr in article.article_attributes
                                ],
                            )
                            st.write(
                                "**연관 항목:**",
                                [
                                    f"{ra.headword} ({ra.target_eid})"
                                    for ra in article.related_articles
                                ],
                            )
                        with tab3:
                            st.json(article.model_dump(mode="json"))

                elif selected.endpoint_id == "medias_list":
                    res_m = client.medias.list(page=params["p"], page_size=params["ps"])
                    st.success(f"미디어 목록 조회 성공 (총 {res_m.total_count}건)")
                    st.json(res_m.model_dump(mode="json"))

                elif selected.endpoint_id == "medias_search":
                    res_m = client.medias.search(
                        params["q"], page=params["p"], page_size=params["ps"]
                    )
                    st.success(f"미디어 검색 성공 (총 {res_m.total_count}건)")
                    st.json(res_m.model_dump(mode="json"))

                elif selected.endpoint_id == "media_detail":
                    media = client.medias.get(params["mid"])
                    if media is None:
                        st.warning(f"해당 MID({params['mid']})의 미디어를 찾을 수 없습니다.")
                    else:
                        st.success(f"미디어 조회 성공: {media.caption}")
                        if media.url:
                            st.image(media.url, caption=media.caption)
                        st.json(media.model_dump(mode="json"))

        except Exception as e:
            st.error(f"오류 발생: {e}")
        finally:
            client.close()


if __name__ == "__main__":
    main()
