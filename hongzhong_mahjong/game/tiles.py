from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


SUITS = ("Man", "Pin", "Sou")
WILDCARD = "Chun"


@dataclass(frozen=True, order=True)
class Tile:
    code: str

    @property
    def suit(self) -> str:
        if self.code == WILDCARD:
            return "Honor"
        return self.code[:3]

    @property
    def rank(self) -> int:
        if self.code == WILDCARD:
            return 0
        return int(self.code[3:])


def all_tile_codes() -> List[str]:
    codes: List[str] = []
    for suit in SUITS:
        for rank in range(1, 10):
            codes.extend([f"{suit}{rank}"] * 4)
    codes.extend([WILDCARD] * 4)
    return codes


def build_image_map(repo_root: Path) -> Dict[str, Path]:
    """Map tile code -> PNG path using repository assets."""
    img_dir = repo_root / "Export" / "Regular"
    mapping = {WILDCARD: img_dir / "Chun.png"}
    for suit in SUITS:
        for rank in range(1, 10):
            mapping[f"{suit}{rank}"] = img_dir / f"{suit}{rank}.png"
    return mapping
