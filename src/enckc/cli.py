"""`enckc` 명령행 인터페이스 (CLI)."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict, is_dataclass
from typing import Any

from .client import EnckcClient
from .exceptions import EnckcError


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="enckc",
        description="한국민족문화대백과사전(Encykorea) OpenAPI 명령행 도구",
    )
    parser.add_argument(
        "--api-key",
        help=(
            "한국민족문화대백과사전 OpenAPI 인증키. "
            "미지정 시 ENCKC_API_KEY 환경변수 또는 .env/.env.local 사용."
        ),
    )
    parser.add_argument(
        "--base-url",
        help="API Base URL (기본값: https://devin.aks.ac.kr:8080/api)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. articles (목록)
    articles_parser = subparsers.add_parser("articles", help="전체 항목 리스트 조회")
    articles_parser.add_argument(
        "-p", "--page", type=int, default=1, help="페이지 번호 (기본값: 1)"
    )
    articles_parser.add_argument(
        "-s", "--page-size", type=int, default=20, help="페이지 크기 (기본값: 20)"
    )

    # 2. search-articles (검색)
    search_art_parser = subparsers.add_parser("search-articles", help="항목 키워드 검색")
    search_art_parser.add_argument("-q", "--query", required=True, help="검색 키워드")
    search_art_parser.add_argument(
        "-p", "--page", type=int, default=1, help="페이지 번호 (기본값: 1)"
    )
    search_art_parser.add_argument(
        "-s", "--page-size", type=int, default=20, help="페이지 크기 (기본값: 20)"
    )

    # 3. article (상세)
    article_parser = subparsers.add_parser("article", help="항목 EID로 상세 조회")
    article_parser.add_argument("eid", help="항목 EID (예: E0029849)")

    # 4. medias (미디어 목록)
    medias_parser = subparsers.add_parser("medias", help="미디어 전체 목록 조회")
    medias_parser.add_argument("-p", "--page", type=int, default=1, help="페이지 번호 (기본값: 1)")
    medias_parser.add_argument(
        "-s", "--page-size", type=int, default=20, help="페이지 크기 (기본값: 20)"
    )

    # 5. search-medias (미디어 검색)
    search_med_parser = subparsers.add_parser("search-medias", help="미디어 키워드 검색")
    search_med_parser.add_argument("-q", "--query", required=True, help="검색 키워드")
    search_med_parser.add_argument(
        "-p", "--page", type=int, default=1, help="페이지 번호 (기본값: 1)"
    )
    search_med_parser.add_argument(
        "-s", "--page-size", type=int, default=20, help="페이지 크기 (기본값: 20)"
    )

    # 6. media (미디어 상세)
    media_parser = subparsers.add_parser("media", help="미디어 MID로 상세 조회")
    media_parser.add_argument("mid", help="미디어 MID (UUID 형식)")

    args = parser.parse_args(argv)

    if args.api_key:
        print(
            "Warning: --api-key exposes your API key in shell history and process "
            "listings; prefer the ENCKC_API_KEY environment variable or .env file.",
            file=sys.stderr,
        )

    client = (
        EnckcClient(api_key=args.api_key, base_url=args.base_url)
        if args.api_key
        else EnckcClient.from_env(base_url=args.base_url)
    )

    try:
        if args.command == "articles":
            res_arts = client.articles.list(page=args.page, page_size=args.page_size)
            _print_json(res_arts)
            return 0

        if args.command == "search-articles":
            res_search_art = client.articles.search(
                args.query, page=args.page, page_size=args.page_size
            )
            _print_json(res_search_art)
            return 0

        if args.command == "article":
            article = client.articles.get(args.eid)
            if article is None:
                print(
                    json.dumps(
                        {"error": f"Article not found: {args.eid}"}, ensure_ascii=False, indent=2
                    )
                )
                return 1
            _print_json(article)
            return 0

        if args.command == "medias":
            res_meds = client.medias.list(page=args.page, page_size=args.page_size)
            _print_json(res_meds)
            return 0

        if args.command == "search-medias":
            res_search_med = client.medias.search(
                args.query, page=args.page, page_size=args.page_size
            )
            _print_json(res_search_med)
            return 0

        if args.command == "media":
            media = client.medias.get(args.mid)
            if media is None:
                print(
                    json.dumps(
                        {"error": f"Media not found: {args.mid}"}, ensure_ascii=False, indent=2
                    )
                )
                return 1
            _print_json(media)
            return 0

        return 0
    except EnckcError as exc:
        print(json.dumps({"error": str(exc), **exc.metadata}, ensure_ascii=False, indent=2))
        return 1
    finally:
        client.close()


def _print_json(value: Any) -> None:
    data = _jsonable(value)
    # 표준 출력이 유니코드를 올바르게 처리하도록 보장
    json_str = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    try:
        print(json_str)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(json_str.encode("utf-8") + b"\n")


def _jsonable(value: Any) -> Any:
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", by_alias=True)
    if is_dataclass(value):
        return asdict(value)  # type: ignore[arg-type]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
