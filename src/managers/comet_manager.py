import math
import random
import pygame
from src.ui.renderer import draw_comet

class CometManager:
    """彗星の状態と振る舞いを管理するクラス"""

    def __init__(self):
        self.active = False
        self.timer = 0.0
        self.theta = 0.0
        self.phi = 0.0
        self.start_theta = 0.0
        self.start_phi = 0.0
        self.end_theta = 0.0
        self.end_phi = 0.0
        self.spawned = False
        self.is_faint = False

    def update(self, dt: float, progress: float, moon_phase: float, can_spawn: bool = True, is_lunar_eclipse: bool = False):
        """彗星の出現と移動を更新する"""
        # 新月・上弦の半月・上弦の月・月食で発生
        if moon_phase in (0.0, 0.5, 0.75) or is_lunar_eclipse:
            if can_spawn and not self.spawned and progress >= 0.3:
                self.spawned = True
                self.active = True
                self.timer = 7.0
                self.is_faint = (moon_phase > 0.0) and not is_lunar_eclipse
                
                # ドーム座標での開始・終了地点を設定
                self.start_theta = random.uniform(0, 360)
                self.start_phi = random.uniform(40, 80)
                theta_diff = random.choice([-120, 120])
                self.end_theta = self.start_theta + theta_diff
                self.end_phi = self.start_phi - random.uniform(30, 60)
            
            if self.active:
                self.timer -= dt
                if self.timer <= 0:
                    self.active = False
                else:
                    p = 1.0 - (self.timer / 7.0)
                    # ドーム座標上で補間
                    self.theta = self.start_theta + (self.end_theta - self.start_theta) * p
                    self.phi = self.start_phi + (self.end_phi - self.start_phi) * p

    def draw(self, screen, coord, ability_manager):
        """彗星を描画する"""
        if self.active:
            sx, sy, visible = coord.to_screen(self.theta, self.phi)
            if visible:
                # 尾の角度を計算するために少し前の位置を取得
                prev_p = max(0.0, 1.0 - ((self.timer + 0.1) / 7.0))
                ptheta = self.start_theta + (self.end_theta - self.start_theta) * prev_p
                pphi = self.start_phi + (self.end_phi - self.start_phi) * prev_p
                px, py, _ = coord.to_screen(ptheta, pphi)
                
                angle = math.pi / 4
                if px != sx or py != sy:
                    angle = math.atan2(sy - py, sx - px)
                
                # Eキーモード中なら薄い彗星もはっきり描画
                is_faint = self.is_faint and not ability_manager.energy_ready_state
                draw_comet(screen, sx, sy, angle, self.timer, is_faint)

    def handle_click(self, mx: int, my: int, coord, ability_manager) -> bool:
        """彗星がクリックされたか判定する"""
        if self.active:
            is_clickable = not self.is_faint or ability_manager.energy_ready_state
            if is_clickable:
                sx, sy, visible = coord.to_screen(self.theta, self.phi)
                if visible:
                    dist = math.sqrt((mx - sx)**2 + (my - sy)**2)
                    if dist < 45:
                        self.active = False
                        return True
        return False
