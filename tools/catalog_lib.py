"""Shared character-catalog loading, validation, and generation helpers."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from tempfile import NamedTemporaryFile


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
ID_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def file_version(path: Path) -> str:
    """Return a short content hash used to invalidate stale browser/CDN caches."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:12]


def validate_record(record: object, expected_id: str | None = None) -> dict:
    if not isinstance(record, dict):
        raise ValueError("profile.jsonはJSONオブジェクトにしてください。")

    missing = sorted(REQUIRED_FIELDS - record.keys())
    if missing:
        raise ValueError(f"必須項目が不足しています: {', '.join(missing)}")

    character_id = record["id"]
    if not isinstance(character_id, str) or not ID_PATTERN.fullmatch(character_id):
        raise ValueError("idは半角英小文字・数字・ハイフンだけで入力してください。")
    if expected_id is not None and character_id != expected_id:
        raise ValueError(f"フォルダ名「{expected_id}」とid「{character_id}」が一致しません。")

    for field in ("name", "realName", "kicker", "summary"):
        if not isinstance(record[field], str) or not record[field].strip():
            raise ValueError(f"{field}は空でない文字列にしてください。")

    for field in ("quotes", "bio"):
        value = record[field]
        if not isinstance(value, list) or not value or not all(
            isinstance(item, str) and item.strip() for item in value
        ):
            raise ValueError(f"{field}は1件以上の文字列配列にしてください。")

    facts = record["facts"]
    if not isinstance(facts, list) or not facts:
        raise ValueError("factsは1件以上の配列にしてください。")
    for fact in facts:
        if not isinstance(fact, dict) or set(fact) != {"label", "value"}:
            raise ValueError("factsの各項目にはlabelとvalueだけを指定してください。")
        if not all(isinstance(fact[key], str) and fact[key].strip() for key in fact):
            raise ValueError("factsのlabelとvalueは空でない文字列にしてください。")

    order = record.get("order")
    if order is not None and (not isinstance(order, int) or isinstance(order, bool)):
        raise ValueError("orderは整数にしてください。")

    return record


def load_profiles(root: Path) -> list[dict]:
    characters_root = root / "characters-data"
    if not characters_root.is_dir():
        raise FileNotFoundError("characters-dataフォルダがありません。")

    profiles: list[dict] = []
    seen_ids: set[str] = set()
    for directory in sorted(path for path in characters_root.iterdir() if path.is_dir()):
        profile_path = directory / "profile.json"
        if not profile_path.is_file():
            raise FileNotFoundError(f"{directory.name}/profile.jsonがありません。")

        record = validate_record(
            json.loads(profile_path.read_text(encoding="utf-8")), directory.name
        )
        character_id = record["id"]
        if character_id in seen_ids:
            raise ValueError(f"idが重複しています: {character_id}")
        seen_ids.add(character_id)

        for filename in ("portrait.webp", "original.webp"):
            image_path = directory / filename
            if not image_path.is_file() or image_path.stat().st_size == 0:
                raise FileNotFoundError(f"{directory.name}/{filename}がありません。")

        profiles.append(record)

    if not profiles:
        raise ValueError("キャラクターが1名も登録されていません。")
    return profiles


def compile_catalog(root: Path) -> list[dict]:
    profiles = load_profiles(root)
    profiles.sort(key=lambda item: (item.get("order", 1_000_000), item["id"]))

    catalog: list[dict] = []
    for profile in profiles:
        character = {key: value for key, value in profile.items() if key != "order"}
        character_id = character["id"]
        character_root = root / "characters-data" / character_id
        portrait = character_root / "portrait.webp"
        original = character_root / "original.webp"
        character["images"] = {
            "portrait": (
                f"characters-data/{character_id}/portrait.webp"
                f"?v={file_version(portrait)}"
            ),
            "original": (
                f"characters-data/{character_id}/original.webp"
                f"?v={file_version(original)}"
            ),
        }
        catalog.append(character)
    return catalog


def write_json_atomic(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp"
    ) as temporary:
        json.dump(data, temporary, ensure_ascii=False, indent=2)
        temporary.write("\n")
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)
