import pygame
import random
import math

class Bug:
    """天球ドーム上を漂い、デジタルグリッチノイズを発生させるバグ（グリッチ）クラス"""
    def __init__(self, theta=None, phi=None):
        # 指定がない場合はドーム上のランダムな位置に配置
        self.theta = theta if theta is not None else random.uniform(0.0, 360.0)
        self.phi = phi if phi is not None else random.uniform(25.0, 70.0)
        
        # 移動速度 (度/秒)
        self.speed = 3.0
        angle = random.uniform(0, 2 * math.pi)
        self.vx = self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)
        
        self.glitch_time = 0.0
        self.change_dir_timer = random.uniform(2.0, 6.0)

        # ── 合体・ブラックホール用の追加パラメータ ──
        self.level = 1
        self.is_blackhole = False
        self.size_scale = 1.0

    def update(self, dt):
        # 位置の更新 (方位角は360度ループ)
        self.theta = (self.theta + self.vx * dt) % 360.0
        # 仰角は 20度〜80度 の範囲に制限
        self.phi = max(20.0, min(80.0, self.phi + self.vy * dt))
        
        # 仰角の限界に達したらバウンド
        if self.phi <= 20.0 or self.phi >= 80.0:
            self.vy = -self.vy
            
        # 一定時間ごとにランダムに移動方向を変える (ランダムウォーク)
        self.change_dir_timer -= dt
        if self.change_dir_timer <= 0:
            angle = random.uniform(0, 2 * math.pi)
            self.vx = self.speed * math.cos(angle)
            self.vy = self.speed * math.sin(angle)
            self.change_dir_timer = random.uniform(2.0, 6.0)
            
        self.glitch_time += dt

    def get_3d_position(self) -> tuple[float, float, float]:
        """バグの天球上の球面座標から3D直交座標を算出する。"""
        bt = math.radians(self.theta)
        bp = math.radians(self.phi)
        bx = math.cos(bp) * math.sin(bt)
        by = math.sin(bp)
        bz = math.cos(bp) * math.cos(bt)
        return bx, by, bz

    def draw(self, screen, coord):
        # 天球座標からスクリーン座標へ投影
        sx, sy, visible = coord.to_screen(self.theta, self.phi)
        if not visible:
            return
            
        # ズーム倍率
        zoom_ratio = 90.0 / coord.current_fov
            
        if self.is_blackhole:
            # ── ブラックホールのビジュアル描画 ──
            # 1. 外側の渦巻く降着円盤（アクレッションディスク）
            pulse = (math.sin(self.glitch_time * 8.0) + 1.0) / 2.0
            base_r = int(14 * self.size_scale * zoom_ratio)
            glow_r = int(base_r * (2.2 + pulse * 0.4))
            
            # グラデーション状 of 渦を作るための半透明サーフェス
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            # オレンジ・赤の外部ガス光輪
            pygame.draw.circle(glow_surf, (255, 80, 0, 35), (glow_r, glow_r), glow_r)
            # 紫・マゼンタの内部光輪
            pygame.draw.circle(glow_surf, (140, 20, 255, 75), (glow_r, glow_r), int(glow_r * 0.7))
            # 黄色く輝くリング
            pygame.draw.circle(glow_surf, (255, 210, 40, 130), (glow_r, glow_r), int(glow_r * 0.55), max(1, int(3 * zoom_ratio)))
            
            # 回転させて渦巻き感を演出
            rotated_surf = pygame.transform.rotate(glow_surf, self.glitch_time * 90.0)
            rect = rotated_surf.get_rect(center=(int(sx), int(sy)))
            screen.blit(rotated_surf, rect.topleft)
            
            # 2. 事象の地平面（イベントホライズン）- 完全な黒のコア
            core_r = max(4, int(base_r * 0.45))
            pygame.draw.circle(screen, (5, 5, 10), (int(sx), int(sy)), core_r)
            # コアの外側の白い極細アインシュタインリング
            pygame.draw.circle(screen, (255, 255, 255), (int(sx), int(sy)), core_r + 1, 1)
            
            # 3. 周囲の強力なデジタルシアラインノイズ
            if random.random() < 0.4:
                line_y = int(sy) + random.randint(-int(18 * self.size_scale * zoom_ratio), int(18 * self.size_scale * zoom_ratio))
                line_w = random.randint(int(30 * zoom_ratio), int(70 * self.size_scale * zoom_ratio))
                offset_x = random.randint(-int(20 * zoom_ratio), int(20 * zoom_ratio))
                pygame.draw.line(screen, (160, 0, 255), 
                                 (int(sx) - line_w // 2 + offset_x, line_y), 
                                 (int(sx) + line_w // 2 + offset_x, line_y), max(1, int(2 * zoom_ratio)))
        else:
            # ── 通常のグリッチバグの描画 ──
            # 1. コアの明滅 (周期的なサイン波グロー)
            pulse = (math.sin(self.glitch_time * 12.0) + 1.0) / 2.0  # 0.0 〜 1.0
            r_size = int((7 + pulse * 5) * zoom_ratio)
            
            # 赤/ピンク系のグローサーフェスを作成
            glow_surf = pygame.Surface((r_size * 4, r_size * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 20, 80, 45), (r_size * 2, r_size * 2), r_size * 2)
            pygame.draw.circle(glow_surf, (255, 20, 80, 120), (r_size * 2, r_size * 2), r_size)
            screen.blit(glow_surf, (int(sx) - r_size * 2, int(sy) - r_size * 2))
            
            # コア中心の白いコア輝点
            pygame.draw.circle(screen, (255, 230, 240), (int(sx), int(sy)), max(1, int(2 * zoom_ratio)))
            
            # 2. デジタルノイズ（スリット線とピクセルブロック）
            if random.random() < 0.35:
                # 水平方向のシアグリッチライン (水色または紫)
                line_y = int(sy) + random.randint(-int(12 * zoom_ratio), int(12 * zoom_ratio))
                line_w = random.randint(int(15 * zoom_ratio), int(45 * zoom_ratio))
                offset_x = random.randint(-int(15 * zoom_ratio), int(15 * zoom_ratio))
                color_line = random.choice([(0, 255, 220), (255, 0, 150)])
                pygame.draw.line(screen, color_line, 
                                 (int(sx) - line_w // 2 + offset_x, line_y), 
                                 (int(sx) + line_w // 2 + offset_x, line_y), 1)
                
                # ピクセルグリッチブロック
                box_w = random.randint(int(4 * zoom_ratio), int(10 * zoom_ratio))
                box_h = random.randint(int(3 * zoom_ratio), int(8 * zoom_ratio))
                box_x = int(sx) + random.randint(-int(20 * zoom_ratio), int(20 * zoom_ratio))
                box_y = int(sy) + random.randint(-int(20 * zoom_ratio), int(20 * zoom_ratio))
                color_box = random.choice([(255, 0, 128), (0, 230, 255), (140, 20, 255)])
                pygame.draw.rect(screen, color_box, (box_x, box_y, box_w, box_h))
                
                # 低い確率でデジタルな「×」印を瞬かせ、エラー感を強調
                if random.random() < 0.25:
                    size_x = int(5 * zoom_ratio)
                    pygame.draw.line(screen, (255, 10, 50), 
                                     (int(sx) - size_x, int(sy) - size_x), 
                                     (int(sx) + size_x, int(sy) + size_x), max(1, int(2 * zoom_ratio)))
                    pygame.draw.line(screen, (255, 10, 50), 
                                     (int(sx) + size_x, int(sy) - size_x), 
                                     (int(sx) - size_x, int(sy) + size_x), max(1, int(2 * zoom_ratio)))
