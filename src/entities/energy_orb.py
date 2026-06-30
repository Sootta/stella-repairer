import random
import math
import pygame

class EnergyOrb:
    """天球ドーム上を飛行する、星座の能力を発動するためのエネルギー玉クラス"""
    def __init__(self, theta=None, phi=None):
        # 指定がない場合はドーム上のランダムな位置に配置
        self.theta = theta if theta is not None else random.uniform(0.0, 360.0)
        self.phi = phi if phi is not None else random.uniform(25.0, 65.0)
        
        # 移動速度 (バグより速い 6.0度/秒)
        self.speed = 6.0
        angle = random.uniform(0, 2 * math.pi)
        self.vx = self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)
        
        # 寿命（18.0秒で自動消滅）
        self.life_time = 18.0
        self.glitch_time = 0.0

    def update(self, dt):
        # 位置の更新 (方位角は360度ループ)
        self.theta = (self.theta + self.vx * dt) % 360.0
        # 仰角は 20度〜75度 の範囲に制限
        self.phi = self.phi + self.vy * dt
        
        # 仰角の限界に達したらバウンド
        if self.phi <= 20.0:
            self.phi = 20.0
            self.vy = -self.vy
        elif self.phi >= 75.0:
            self.phi = 75.0
            self.vy = -self.vy
            
        # 寿命のカウントダウン
        self.life_time -= dt
        self.glitch_time += dt

    def draw(self, screen, coord):
        # 天球座標からスクリーン座標へ投影
        sx, sy, visible = coord.to_screen(self.theta, self.phi)
        if not visible:
            return
            
        # シアン/ブルー系の美しい光を放つエネルギー玉の描画
        # 明滅アニメーション効果
        pulse = (math.sin(self.glitch_time * 15.0) + 1.0) / 2.0
        r_size = int(8 + pulse * 6)
        
        # 半透明のシアン色グローサーフェスを作成
        glow_surf = pygame.Surface((r_size * 4, r_size * 4), pygame.SRCALPHA)
        # 外側の淡いグロー (シアン)
        pygame.draw.circle(glow_surf, (0, 220, 255, 40), (r_size * 2, r_size * 2), r_size * 2)
        # 内側のやや強いグロー (シアン/グリーン)
        pygame.draw.circle(glow_surf, (0, 255, 200, 100), (r_size * 2, r_size * 2), int(r_size * 1.2))
        
        screen.blit(glow_surf, (int(sx) - r_size * 2, int(sy) - r_size * 2))
        
        # コア中心の白いコア輝点
        pygame.draw.circle(screen, (230, 255, 250), (int(sx), int(sy)), 3)
