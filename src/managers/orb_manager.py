import random
import math

from src.entities.energy_orb import EnergyOrb


class OrbManager:
    """エネルギー玉のスポーン・更新・収集を管理するクラス"""

    def __init__(self, max_energy_orbs: int, orb_spawn_rate: float, sfx):
        """
        max_energy_orbs: 同時に存在できる最大数
        orb_spawn_rate:  難易度ベースの出現速度倍率
        sfx:             {"orb_collect": Sound|None}
        """
        self.max_energy_orbs = max_energy_orbs
        self.orb_spawn_rate = orb_spawn_rate
        self.sfx = sfx

        self.orbs: list[EnergyOrb] = []
        self.spawn_timer = random.uniform(25.0, 45.0) / self.orb_spawn_rate

    # ──────────────────────────────────────────
    # 毎フレーム更新
    # ──────────────────────────────────────────
    def update(self, dt: float):
        """玉の位置更新・寿命切れ除去・新規スポーン"""
        for orb in self.orbs:
            orb.update(dt)
        self.orbs = [o for o in self.orbs if o.life_time > 0]

        if len(self.orbs) < self.max_energy_orbs:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.orbs.append(EnergyOrb())
                self.spawn_timer = random.uniform(30.0, 60.0) / self.orb_spawn_rate
                print("エネルギー玉が空中に出現しました！")

    # ──────────────────────────────────────────
    # クリック回収
    # ──────────────────────────────────────────
    def check_click(self, mouse_pos, coord, zoom_ratio: float) -> int:
        """
        マウス位置と重なっている玉を回収して個数を返す。
        収集があった場合は効果音を再生する。
        """
        mx, my = mouse_pos
        collected = []
        for orb in self.orbs:
            ox, oy, visible = coord.to_screen(orb.theta, orb.phi)
            if visible:
                dist = math.sqrt((mx - ox) ** 2 + (my - oy) ** 2)
                if dist < 32.0 * zoom_ratio:
                    collected.append(orb)

        if collected:
            for orb in collected:
                self.orbs.remove(orb)
            self._play_sfx()

        return len(collected)

    # ──────────────────────────────────────────
    # 描画
    # ──────────────────────────────────────────
    def draw(self, screen, coord):
        for orb in self.orbs:
            orb.draw(screen, coord)

    # ──────────────────────────────────────────
    # ヘルパー
    # ──────────────────────────────────────────
    def _play_sfx(self):
        sfx = self.sfx.get("orb_collect")
        if sfx:
            try:
                sfx.play()
            except Exception as e:
                print(f"Error playing Orb SFX: {e}")
