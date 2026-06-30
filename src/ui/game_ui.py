import math
import pygame


FOV_DEG = 90.0  # game.py と同じ定数


class GameUI:
    """ゲーム中の全HUD描画を担当するクラス"""

    ABILITY_INFO = {
        'slow_bugs':      ('吟遊詩人座: 安らぎの旋律',       (150, 200, 255)),
        'fast_camera':    ('狐座: 疾出のステップ',            (255, 180, 100)),
        'mark_bugs':      ('鍵座: 知理の瞳',                  (255, 100, 100)),
        'immune_stars':   ('糸紡ぎ座: 守護の結',              (100, 255, 150)),
        'knockback_bugs': ('こだま座: 音響ノックバック',       (200, 150, 255)),
        'splash_kill':    ('折れた剣座: 衝撃の刃',            (255, 230, 100)),
        'auto_pull_stars':('蝶座: 導きの羽ばたき',            (255, 150, 200)),
        'anti_gravity':   ('鯨座: 宿まりの重力',              (100, 200, 255)),
        'dragon_shield':  ('ドラゴン座: 天壁の盾',            (255, 215,   0)),
    }

    def draw_all(self, screen, game):
        """ゲーム中のすべてのHUDをまとめて描画する"""
        sw, sh = screen.get_width(), screen.get_height()
        zoom_ratio = FOV_DEG / game.coord.current_fov

        self._draw_bug_trackers(screen, game, sw, sh, zoom_ratio)
        self._draw_splash_effects(screen, game.splash_effects)
        self._draw_ability_status(screen, game.ability_manager, sw)
        self._draw_camera_ui(screen, game)
        self._draw_constellation_info(screen, game.selected_constellation, game.message_timer, sw, sh)
        self._draw_star_count(screen, game.constellations, sw, sh)
        self._draw_energy_display(screen, game, sw, sh)
        self._draw_ability_message(screen, game.ability_manager, sw, sh)
        self._draw_reticle(screen, game, sw, sh, zoom_ratio)

    # ──────────────────────────────────────────
    # バグトラッカー
    # ──────────────────────────────────────────
    def _draw_bug_trackers(self, screen, game, sw, sh, zoom_ratio):
        """鍵座「知理の瞳」によるバグ追跡表示とレーダー警告"""
        if not game.ability_manager.is_active('mark_bugs'):
            return
        for bug in game.bug_manager.bugs:
            bx, by, visible = game.coord.to_screen(bug.theta, bug.phi)
            if visible:
                box_size = int(32 * bug.size_scale * zoom_ratio)
                box_rect = pygame.Rect(bx - box_size, by - box_size, box_size * 2, box_size * 2)
                pygame.draw.rect(screen, (255, 60, 60), box_rect, 2)
                line_len = int(8 * zoom_ratio)
                # 左上
                pygame.draw.line(screen, (255, 255, 100), (bx - box_size, by - box_size), (bx - box_size + line_len, by - box_size), 2)
                pygame.draw.line(screen, (255, 255, 100), (bx - box_size, by - box_size), (bx - box_size, by - box_size + line_len), 2)
                # 右上
                pygame.draw.line(screen, (255, 255, 100), (bx + box_size, by - box_size), (bx + box_size - line_len, by - box_size), 2)
                pygame.draw.line(screen, (255, 255, 100), (bx + box_size, by - box_size), (bx + box_size, by - box_size + line_len), 2)
                # 左下
                pygame.draw.line(screen, (255, 255, 100), (bx - box_size, by + box_size), (bx - box_size + line_len, by + box_size), 2)
                pygame.draw.line(screen, (255, 255, 100), (bx - box_size, by + box_size), (bx - box_size, by + box_size - line_len), 2)
                # 右下
                pygame.draw.line(screen, (255, 255, 100), (bx + box_size, by + box_size), (bx + box_size - line_len, by + box_size), 2)
                pygame.draw.line(screen, (255, 255, 100), (bx + box_size, by + box_size), (bx + box_size, by + box_size - line_len), 2)
            else:
                # 画面外バグのレーダー矢印
                dx = (bug.theta - game.coord.cam_theta + 180) % 360 - 180
                dy = -(bug.phi - game.coord.cam_phi)
                angle = math.atan2(dy, dx)
                margin = 40
                max_x = sw // 2 - margin
                max_y = sh // 2 - margin
                dir_x, dir_y = math.cos(angle), math.sin(angle)
                if dir_x == 0:
                    t = max_y / abs(dir_y)
                elif dir_y == 0:
                    t = max_x / abs(dir_x)
                else:
                    t = min(max_x / abs(dir_x), max_y / abs(dir_y))
                ix = sw // 2 + dir_x * t
                iy = sh // 2 + dir_y * t
                pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1.0) / 2.0
                arrow_color = (255, int(50 + 100 * pulse), int(50 + 100 * pulse))
                length, width = 15, 10
                p0 = (ix + math.cos(angle) * length, iy + math.sin(angle) * length)
                p1 = (ix + math.cos(angle + math.radians(135)) * width,
                      iy + math.sin(angle + math.radians(135)) * width)
                p2 = (ix + math.cos(angle - math.radians(135)) * width,
                      iy + math.sin(angle - math.radians(135)) * width)
                pygame.draw.polygon(screen, arrow_color, [p0, p1, p2])
                pygame.draw.circle(screen, arrow_color, (int(ix), int(iy)), 5)

    # ──────────────────────────────────────────
    # スプラッシュエフェクト
    # ──────────────────────────────────────────
    def _draw_splash_effects(self, screen, splash_effects):
        """スプラッシュエフェクト（衝撃の波紋）の描画"""
        for effect in splash_effects:
            cx_e, cy_e = effect["pos"]
            progress = 1.0 - (effect["timer"] / effect["max_timer"])
            current_radius = int(150.0 * progress)
            alpha = int(180 * (1.0 - progress))
            surf = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 200, 50, alpha),
                               (current_radius, current_radius), current_radius, 3)
            pygame.draw.circle(surf, (255, 100, 0, alpha // 3),
                               (current_radius, current_radius), current_radius)
            screen.blit(surf, (int(cx_e - current_radius), int(cy_e - current_radius)))

    # ──────────────────────────────────────────
    # アビリティステータス
    # ──────────────────────────────────────────
    def _draw_ability_status(self, screen, ability_manager, sw):
        """アクティブなアビリティ状態の描画 (右上)"""
        y_offset = 60
        font_stat = pygame.font.SysFont(
            "notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 20, bold=True)
        if not font_stat:
            font_stat = pygame.font.SysFont(None, 22, bold=True)

        for key, val in ability_manager.active.items():
            if key not in self.ABILITY_INFO:
                continue
            name, color = self.ABILITY_INFO[key]
            if isinstance(val, float) and val > 0:
                status_str = f"✦ {name} ({val:.1f}s)"
            elif isinstance(val, int) and val > 0:
                status_str = f"✦ {name} ({val}回)"
            else:
                continue
            stat_surf = font_stat.render(status_str, True, color)
            screen.blit(stat_surf, (sw - stat_surf.get_width() - 40, y_offset))
            y_offset += stat_surf.get_height() + 8

    # ──────────────────────────────────────────
    # カメラ情報 UI
    # ──────────────────────────────────────────
    def _draw_camera_ui(self, screen, game):
        """操作UIテキストの描画 (左上)"""
        font = pygame.font.SysFont(None, 36)
        ui_text = (f"Yaw: {game.coord.cam_theta:.1f} "
                   f"Pitch: {-game.coord.cam_phi:.1f} "
                   f"FOV: {game.coord.current_fov:.1f} "
                   f"[WASD: Move, SPACE: Telescope, C: Mouse Look]")
        text = font.render(ui_text, True, (255, 255, 255))
        screen.blit(text, (20, 20))

    # ──────────────────────────────────────────
    # 星座インフォパネル
    # ──────────────────────────────────────────
    def _draw_constellation_info(self, screen, selected_const, message_timer, sw, sh):
        """クリックされた星座のインフォメーションUI描画"""
        if message_timer <= 0.0 or selected_const is None:
            return
        alpha = min(255, int(255 * (message_timer / 0.5))) if message_timer < 0.5 else 255
        panel_w, panel_h = 640, 110
        overlay = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        overlay.fill((8, 15, 30, int(alpha * 0.85)))
        pygame.draw.rect(overlay, (215, 170, 70, alpha), (0, 0, panel_w, panel_h), 2)
        pygame.draw.rect(overlay, (100, 80, 30, alpha), (3, 3, panel_w - 6, panel_h - 6), 1)

        font_title = pygame.font.SysFont(
            "notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 26, bold=True)
        if not font_title:
            font_title = pygame.font.SysFont(None, 30)
        font_desc = pygame.font.SysFont(
            "notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 16)
        if not font_desc:
            font_desc = pygame.font.SysFont(None, 18)

        title_text = f"発見: {selected_const.name} ({selected_const.english_name})"
        title_surf = font_title.render(title_text, True, (255, 225, 120))
        desc_surf = font_desc.render(selected_const.description, True, (210, 230, 255))
        title_surf.set_alpha(alpha)
        desc_surf.set_alpha(alpha)

        overlay.blit(title_surf, (panel_w // 2 - title_surf.get_width() // 2, 20))
        overlay.blit(desc_surf,  (panel_w // 2 - desc_surf.get_width()  // 2, 65))
        screen.blit(overlay, (sw // 2 - panel_w // 2, sh - 170))

    # ──────────────────────────────────────────
    # 星数・星座数カウンター
    # ──────────────────────────────────────────
    def _draw_star_count(self, screen, constellations, sw, sh):
        """画面左下に現在の壊れていない星座の数と星の数を表示"""
        total_count = len(constellations)
        repaired_count = sum(1 for c in constellations
                             if not any(s.is_broken for s in c.stars))
        total_stars = sum(len(c.stars) for c in constellations)
        unbroken_stars = sum(sum(1 for s in c.stars if not s.is_broken)
                             for c in constellations)

        font_ui = pygame.font.SysFont(
            "notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 26, bold=True)
        if not font_ui:
            font_ui = pygame.font.SysFont(None, 28, bold=True)

        stars_surf = font_ui.render(
            f"Stars: {unbroken_stars}/{total_stars}", True, (200, 220, 255))
        ui_surf = font_ui.render(
            f"Repaired: {repaired_count}/{total_count}", True, (235, 180, 60))

        # 星の数UIの描画位置 (星座数UIの上に12pxの余白)
        screen.blit(stars_surf, (40, sh - ui_surf.get_height() - stars_surf.get_height() - 52))
        screen.blit(ui_surf,    (40, sh - ui_surf.get_height() - 40))

    # ──────────────────────────────────────────
    # エネルギー表示
    # ──────────────────────────────────────────
    def _draw_energy_display(self, screen, game, sw, sh):
        """画面右下に所持エネルギー数を表示"""
        if game.possessed_energy <= 0:
            return
        ready = game.ability_manager.energy_ready_state
        pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1.0) / 2.0
        flash_alpha = int(100 + pulse * 155) if ready else 255

        font_energy = pygame.font.SysFont(
            "notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 26, bold=True)
        if not font_energy:
            font_energy = pygame.font.SysFont(None, 28, bold=True)

        if ready:
            energy_str = f"READY: CLICK CONSTELLATION (Energy: {game.possessed_energy})"
            energy_color = (0, 255, 230)
        else:
            energy_str = f"Energy: {game.possessed_energy} [Press E]"
            energy_color = (200, 255, 240)

        energy_surf = font_energy.render(energy_str, True, energy_color)
        if ready:
            energy_surf_alpha = energy_surf.copy()
            energy_surf_alpha.fill((255, 255, 255, flash_alpha),
                                   special_flags=pygame.BLEND_RGBA_MULT)
            energy_surf = energy_surf_alpha

        screen.blit(energy_surf,
                    (sw - energy_surf.get_width() - 40, sh - energy_surf.get_height() - 40))

    # ──────────────────────────────────────────
    # アビリティ発動メッセージ
    # ──────────────────────────────────────────
    def _draw_ability_message(self, screen, ability_manager, sw, sh):
        """画面中央上部にアビリティ発動通知メッセージを描画"""
        if ability_manager.message_timer <= 0.0:
            return
        msg = ability_manager.message
        font_msg = pygame.font.SysFont(
            "notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 32, bold=True)
        if not font_msg:
            font_msg = pygame.font.SysFont(None, 36, bold=True)

        if "所持していません" in msg or "警告" in msg:
            msg_color = (255, 100, 100)
        elif "座" in msg or "回収" in msg or "READY" in msg:
            msg_color = (255, 215, 0)
        else:
            msg_color = (0, 255, 200)

        msg_surf = font_msg.render(msg, True, msg_color)
        timer = ability_manager.message_timer
        msg_alpha = min(255, int(255 * (timer / 0.5))) if timer < 0.5 else 255
        msg_surf_alpha = msg_surf.copy()
        msg_surf_alpha.fill((255, 255, 255, msg_alpha),
                            special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(msg_surf_alpha, (sw // 2 - msg_surf.get_width() // 2, sh // 2 - 120))

    # ──────────────────────────────────────────
    # レティクル
    # ──────────────────────────────────────────
    def _draw_reticle(self, screen, game, sw, sh, zoom_ratio):
        """レティクルの描画 (当たり判定のサイズに合わせる)"""
        R = int(32.0 * zoom_ratio)
        if game.mouse_look_mode:
            cx, cy = sw // 2, sh // 2
        else:
            cx, cy = pygame.mouse.get_pos()

        reticle_color = (0, 255, 230, 180)
        pygame.draw.circle(screen, reticle_color, (cx, cy), R, 1)
        pygame.draw.line(screen, reticle_color, (cx, cy - R - 10), (cx, cy - R - 2), 1)
        pygame.draw.line(screen, reticle_color, (cx, cy + R + 2), (cx, cy + R + 10), 1)
        pygame.draw.line(screen, reticle_color, (cx - R - 10, cy), (cx - R - 2, cy), 1)
        pygame.draw.line(screen, reticle_color, (cx + R + 2, cy), (cx + R + 10, cy), 1)
        pygame.draw.circle(screen, reticle_color, (cx, cy), 2)
