#!/usr/bin/env python3
"""Validate character folders and the generated browser catalog."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from catalog_lib import compile_catalog


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "characters.json"


def main() -> None:
    expected = compile_catalog(ROOT)
    if not DATA_PATH.is_file():
        raise FileNotFoundError("data/characters.jsonが生成されていません。")
    actual = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    if actual != expected:
        raise ValueError("生成済み名鑑データがキャラクターフォルダと一致しません。")
    print(f"名鑑データ検証完了: {len(actual)}名")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        sys.exit(f"名鑑データ検証エラー: {error}")
