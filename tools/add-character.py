#!/usr/bin/env python3
"""Convert character images and register one character in the directory."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillowが必要です: python -m pip install -r tools/requirements.txt")


REQUIRED_FIELDS = {
    "id",
    "name",
    "realName",
    "kicker",
    "summary",
    "quotes",
    "facts",
    "bio",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="画像2枚をWebPへ変換し、キャラクターを名鑑へ登録します。"
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
    with path.open(encoding="utf-8") as file:
        record = json.load(file)
    if not isinstance(record, dict):
        raise ValueError("キャラクター情報はJSONオブジェクトにしてください。")

    missing = sorted(REQUIRED_FIELDS - record.keys())
    if missing:
        raise ValueError(f"必須項目が不足しています: {', '.join(missing)}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(record["id"])):
        raise ValueError("idは半角英小文字・数字・ハイフンだけで入力してください。")
    if not isinstance(record["quotes"], list) or not record["quotes"]:
        raise ValueError("quotesは1件以上の配列にしてください。")
    if not isinstance(record["facts"], list) or not record["facts"]:
        raise ValueError("factsは1件以上の配列にしてください。")
    if not isinstance(record["bio"], list) or not record["bio"]:
        raise ValueError("bioは1件以上の配列にしてください。")
    return record


def convert_image(source: Path, destination: Path, max_size: tuple[int, int], quality: int) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"画像が見つかりません: {source}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "transparency" in image.info else "RGB")
        image.save(destination, "WEBP", quality=quality, method=6)


def write_json_atomic(path: Path, data: list[dict]) -> None:
    with NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp"
    ) as temporary:
        json.dump(data, temporary, ensure_ascii=False, indent=2)
        temporary.write("\n")
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)


def main() -> None:
    args = parse_args()
    repo = args.repo.resolve()
    data_path = repo / "data" / "characters.json"
    assets = repo / "assets"
    record = read_record(args.record)

    with data_path.open(encoding="utf-8") as file:
        characters = json.load(file)
    if any(character.get("id") == record["id"] for character in characters):
        raise ValueError(f"id「{record['id']}」はすでに登録されています。")

    portrait_name = f"{record['id']}-ai.webp"
    original_name = f"{record['id']}-original.webp"
    portrait_output = assets / portrait_name
    original_output = assets / original_name

    if portrait_output.exists() or original_output.exists():
        raise FileExistsError("同名の画像がすでにあります。idを確認してください。")

    try:
        convert_image(args.portrait, portrait_output, (1800, 2400), 88)
        convert_image(args.original, original_output, (2200, 2200), 84)
        record["images"] = {
            "portrait": f"assets/{portrait_name}",
            "original": f"assets/{original_name}",
        }
        characters.append(record)
        write_json_atomic(data_path, characters)
    except Exception:
        portrait_output.unlink(missing_ok=True)
        original_output.unlink(missing_ok=True)
        raise

    print(f"追加完了: {record['name']} ({record['id']})")
    print(f"立ち絵: {portrait_output.relative_to(repo)}")
    print(f"元資料: {original_output.relative_to(repo)}")
    print(f"名鑑データ: {data_path.relative_to(repo)}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        sys.exit(f"追加できませんでした: {error}")
