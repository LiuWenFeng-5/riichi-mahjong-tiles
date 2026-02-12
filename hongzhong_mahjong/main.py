from __future__ import annotations

from pathlib import Path
import tkinter as tk

from game.ui import HongZhongMahjongApp


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    root = tk.Tk()
    HongZhongMahjongApp(root, repo_root)
    root.mainloop()


if __name__ == "__main__":
    main()
