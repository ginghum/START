#!/usr/bin/env python3
"""Validate catalog data and every referenced image before deployment."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "characters.json"
REQUIRED_FIELDS = {
    "id",
    "name",
    "realName",
    "kicker",
    "summary",
    "quotes",
    "facts",
    "bio",
    "images",
}


def main() -> None:
    characters = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    if not isinstance(characters, list):
        raise ValueError("characters.jsonの最上位は配列にしてください。")

    seen_ids: set[str] = set()
    for index, character in enumerate(characters, start=1):
        if not isinstance(character, dict):
            raise ValueError(f"{index}件目がオブジェクトではありません。")
        missing = REQUIRED_FIELDS - character.keys()
        if missing:
            raise ValueError(f"{index}件目の必須項目が不足: {', '.join(sorted(missing))}")

        character_id = character["id"]
        if not isinstance(character_id, str) or not re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*", character_id
        ):
            raise ValueError(f"不正なid: {character_id}")
        if character_id in seen_ids:
            raise ValueError(f"idが重複しています: {character_id}")
        seen_ids.add(character_id)

        images = character["images"]
        for image_type in ("portrait", "original"):
            relative_path = images.get(image_type)
            if not isinstance(relative_path, str) or not relative_path.startswith("assets/"):
                raise ValueError(f"{character_id}の{image_type}画像パスが不正です。")
            if not (ROOT / relative_path).is_file():
                raise FileNotFoundError(f"{character_id}の画像がありません: {relative_path}")

    print(f"名鑑データ検証完了: {len(characters)}名")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        sys.exit(f"名鑑データ検証エラー: {error}")
