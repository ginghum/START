#!/usr/bin/env python3
"""Create one self-contained character folder from a record and two images."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillowが必要です: python -m pip install -r tools/requirements.txt")

from catalog_lib import compile_catalog, load_profiles, validate_record, write_json_atomic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="設定と画像2枚から、追加用キャラクターフォルダを作成します。"
    )
    parser.add_argument("--record", required=True, type=Path, help="キャラクター情報JSON")
    parser.add_argument("--portrait", required=True, type=Path, help="AI立ち絵")
    parser.add_argument("--original", required=True, type=Path, help="元手書き資料")
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="リポジトリの場所（通常は省略）",
    )
    return parser.parse_args()


def read_record(path: Path) -> dict:
    record = json.loads(path.read_text(encoding="utf-8"))
    return validate_record(record)


def convert_image(source: Path, destination: Path, max_size: tuple[int, int], quality: int) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"画像が見つかりません: {source}")
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "transparency" in image.info else "RGB")
        image.save(destination, "WEBP", quality=quality, method=6)


def main() -> None:
    args = parse_args()
    repo = args.repo.resolve()
    record = read_record(args.record)
    character_id = record["id"]
    target = repo / "characters-data" / character_id
    if target.exists():
        raise FileExistsError(f"id「{character_id}」はすでに登録されています。")

    existing = load_profiles(repo)
    record["order"] = max((item.get("order", 0) for item in existing), default=0) + 10
    target.mkdir(parents=True)
    profile_path = target / "profile.json"
    portrait_path = target / "portrait.webp"
    original_path = target / "original.webp"

    try:
        write_json_atomic(profile_path, record)
        convert_image(args.portrait, portrait_path, (1800, 2400), 88)
        convert_image(args.original, original_path, (2200, 2200), 84)
        catalog = compile_catalog(repo)
        write_json_atomic(repo / "data" / "characters.json", catalog)
    except Exception:
        for path in (profile_path, portrait_path, original_path):
            path.unlink(missing_ok=True)
        target.rmdir()
        raise

    print(f"追加完了: {record['name']} ({character_id})")
    print(f"追加対象: characters-data/{character_id}/ の3ファイルだけ")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        sys.exit(f"追加できませんでした: {error}")
