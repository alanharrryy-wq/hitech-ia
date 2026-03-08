from __future__ import annotations

import json
from difflib import unified_diff

def build_manifest_diff(before: dict | None, after: dict) -> str:
    before_text = json.dumps(before or {}, indent=2, ensure_ascii=False).splitlines(keepends=True)
    after_text = json.dumps(after, indent=2, ensure_ascii=False).splitlines(keepends=True)
    return "".join(unified_diff(before_text, after_text, fromfile="before_manifest.json", tofile="after_manifest.json"))
