#!/usr/bin/env python3
"""Validate the independent STORY catalog and its shared assets."""
import json
from pathlib import Path
from catalog_lib import validate_record

ROOT = Path(__file__).resolve().parents[1]
characters = json.loads((ROOT / 'story/characters.json').read_text())
metadata = json.loads((ROOT / 'story/source.json').read_text())
assert len(characters) == metadata['characterCount']
assert len({p['id'] for p in characters}) == len(characters)
for character in characters:
    validate_record(character)
    assert character['story']['appearances'][0] == character['story']['first']
    appearances = character['story']['appearances']
    assert len({a['id'] for a in appearances}) == len(appearances)
    assert all(a['title'] and a['id'] for a in appearances)
    for image in character['images'].values():
        path = (ROOT / 'story' / image.split('?')[0]).resolve()
        assert path.is_relative_to(ROOT.resolve()) and path.is_file(), image
    assert 'changeTarget' not in character
assert next(p for p in characters if p['id'] == 'plus')['facts'][3]['value'] == '1'
for id in ['hikaru', 'kobal']:
    assert next(f['value'] for p in characters if p['id'] == id for f in p['facts'] if f['label'] == 'Grade') == '4'
print(f'STORY名鑑検証完了: {len(characters)}名')
