from __future__ import annotations

import random
import tkinter as tk
from collections import Counter
from pathlib import Path
from tkinter import messagebox
from typing import Dict, List

from .ai import choose_discard
from .rules import is_win, normalize_hand, sort_key
from .tiles import WILDCARD, all_tile_codes, build_image_map


class HongZhongMahjongApp:
    def __init__(self, root: tk.Tk, repo_root: Path) -> None:
        self.root = root
        self.root.title("红中麻将（简化人机对战）")

        self.images = self._load_images(repo_root)

        self.deck: List[str] = []
        self.player_hand: List[str] = []
        self.ai_hand: List[str] = []
        self.last_discard: str | None = None
        self.status_var = tk.StringVar(value="点击“开始新局”开始游戏")

        self._build_layout()

    def _load_images(self, repo_root: Path) -> Dict[str, tk.PhotoImage]:
        mapping = build_image_map(repo_root)
        images: Dict[str, tk.PhotoImage] = {}
        for code, path in mapping.items():
            images[code] = tk.PhotoImage(file=str(path))
        images["BACK"] = tk.PhotoImage(file=str(repo_root / "Export" / "Regular" / "Back.png"))
        return images

    def _build_layout(self) -> None:
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=8, pady=8)

        tk.Button(top, text="开始新局", command=self.start_game).pack(side="left")
        tk.Label(top, textvariable=self.status_var, anchor="w").pack(side="left", padx=10)

        center = tk.Frame(self.root)
        center.pack(fill="both", expand=True, padx=8, pady=8)

        self.ai_frame = tk.LabelFrame(center, text="电脑手牌")
        self.ai_frame.pack(fill="x", pady=4)

        self.discard_frame = tk.LabelFrame(center, text="上一次弃牌")
        self.discard_frame.pack(fill="x", pady=4)

        self.player_frame = tk.LabelFrame(center, text="你的手牌（点击要打出的牌）")
        self.player_frame.pack(fill="x", pady=4)

    def start_game(self) -> None:
        self.deck = all_tile_codes()
        random.shuffle(self.deck)
        self.last_discard = None

        self.player_hand = [self.deck.pop() for _ in range(13)]
        self.ai_hand = [self.deck.pop() for _ in range(13)]

        self.status_var.set("新局开始，你先摸牌。")
        self.player_draw()

    def player_draw(self) -> None:
        if not self.deck:
            self.end_game("牌墙已空，流局！")
            return
        self.player_hand.append(self.deck.pop())
        self.player_hand = normalize_hand(self.player_hand)
        if is_win(self.player_hand):
            self.refresh_ui()
            self.end_game("恭喜你自摸胡牌！")
            return
        self.status_var.set("请选择一张牌打出。")
        self.refresh_ui(player_can_discard=True)

    def on_player_discard(self, tile: str) -> None:
        self.player_hand.remove(tile)
        self.last_discard = tile
        self.player_hand = normalize_hand(self.player_hand)
        self.refresh_ui(player_can_discard=False)

        if is_win(self.ai_hand + [tile]):
            self.end_game(f"电脑荣和你的 {tile}，你输了。")
            return

        self.root.after(350, self.ai_turn)

    def ai_turn(self) -> None:
        if not self.deck:
            self.end_game("牌墙已空，流局！")
            return

        self.ai_hand.append(self.deck.pop())
        self.ai_hand = normalize_hand(self.ai_hand)

        if is_win(self.ai_hand):
            self.refresh_ui()
            self.end_game("电脑自摸胡牌，你输了。")
            return

        discard = choose_discard(self.ai_hand)
        self.ai_hand.remove(discard)
        self.last_discard = discard

        if is_win(self.player_hand + [discard]):
            self.refresh_ui(player_can_discard=False)
            self.end_game(f"你荣和电脑打出的 {discard}，你赢了！")
            return

        self.status_var.set(f"电脑打出 {discard}，轮到你摸牌。")
        self.refresh_ui(player_can_discard=False)
        self.root.after(250, self.player_draw)

    def refresh_ui(self, player_can_discard: bool = False) -> None:
        for frame in (self.ai_frame, self.discard_frame, self.player_frame):
            for child in frame.winfo_children():
                child.destroy()

        # AI cards (hidden)
        for _ in self.ai_hand:
            tk.Label(self.ai_frame, image=self.images["BACK"]).pack(side="left", padx=1)

        # discard
        if self.last_discard:
            tk.Label(self.discard_frame, image=self.images[self.last_discard], text=self.last_discard, compound="top").pack(
                side="left", padx=2
            )

        # player cards
        hand_counts = Counter(self.player_hand)
        for tile in self.player_hand:
            label = tile + ("(红中)" if tile == WILDCARD else "")
            if player_can_discard:
                btn = tk.Button(
                    self.player_frame,
                    image=self.images[tile],
                    text=label,
                    compound="top",
                    command=lambda t=tile: self.on_player_discard(t),
                )
                if hand_counts[tile] <= 0:
                    btn.configure(state="disabled")
                btn.pack(side="left", padx=1)
                hand_counts[tile] -= 1
            else:
                tk.Label(self.player_frame, image=self.images[tile], text=label, compound="top").pack(side="left", padx=1)

    def end_game(self, message: str) -> None:
        self.status_var.set(message)
        self.refresh_ui(player_can_discard=False)
        messagebox.showinfo("对局结束", message)
