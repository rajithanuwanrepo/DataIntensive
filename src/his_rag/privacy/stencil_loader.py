"""Load JSON privacy stencil definitions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_stencil(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as source:
        stencil = json.load(source)
    if not isinstance(stencil.get("entities"), dict):
        raise ValueError("stencil must define entities as an object of permitted attributes")
    if not isinstance(stencil.get("relationships"), list):
        raise ValueError("stencil must define relationships as a list")
    return stencil