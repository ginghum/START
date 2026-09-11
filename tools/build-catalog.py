#!/usr/bin/env python3
"""Generate the browser-facing catalog from one folder per character."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from catalog_lib import compile_catalog, write_json_atomic


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="名鑑用characters.jsonを自動生成します。")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data" / "characters.json",
        help="生成先（通常は省略）",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    catalog = compile_catalog(ROOT)
    write_json_atomic(args.output, catalog)
    print(f"名鑑データ生成完了: {len(catalog)}名")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        sys.exit(f"名鑑データを生成できませんでした: {error}")
