import pygame
import math
import os
import random

from src.ui.renderer import draw_background, draw_constellations, draw_moon, draw_comet
from src.core.constellation_loader import ConstellationLoader
from src.entities.bug import Bug
from src.managers.bug_manager import BugManager
from src.managers.orb_manager import OrbManager
from src.managers.ability_manager import AbilityManager
from src.managers.comet_manager import CometManager
from src.managers.moon_manager import MoonManager
from src.ui.game_ui import GameUI

# ──────────────────────────────────────────
# 定数
# ──────────────────────────────────────────
FOV_DEG = 90.0
CAM_SPEED = 90.0


class Game:
    """GAME状態におけるカメラ操作とゲーム状態の更新・描画を管理するオーケストレータークラス"""

    def __init__(self, coord, base_dir, difficulty="FULL_MOON"):
        self.coord = coord
        self.difficulty = difficulty
        self.mouse_look_mode = False

        # ── 星座データのロードと配置 ──
        self.const_loader = ConstellationLoader(
            os.path.join(base_dir, "data", "sample.json"))
        self.const_loader.load()
        self.constellations = self.const_loader.get_all()
        self.constellation_placements = self._place_constellations()

        # ── 選択済み星座とメッセージ ──
        self.selected_constellation = None
        self.message_timer = 0.0

        # 難易度による調整
        params = self._build_difficulty_params(difficulty)
        self.start_p          = params["start_p"]
        self.end_p            = params["end_p"]

        # ── 月の初期位置 ──
        self.moon_manager = MoonManager(
            start_p=params["start_p"],
            end_p=params["end_p"],
            moon_duration=params["moon_duration"],
            moon_phase=params["moon_phase"],
            visible=params["draw_moon_visible"]
        )

        self.game_cleared = False
        self.game_over    = False
        self.true_clear   = False

        # ── 彗星 ──
        self.comet_manager = CometManager()
        
        # ── 星空観賞モード ──
        self.true_clear_view_mode = False

        # ── エネルギー ──
        self.possessed_energy = 0

        # ── スプラッシュエフェクト ──
        self.splash_effects = []

        # ── 統計 ──
        self.defeated_bugs_count = 0
        self.repaired_consts_session_count = 0

        # ── 効果音のロード ──
        self.sfx = self._load_sfx(base_dir)
        sfx = self.sfx

        # ── 各マネージャーの初期化 ──
        self.ability_manager = AbilityManager(sfx)
        self.bug_manager     = BugManager(coord, params["bug_spawn_rate"], sfx)
        self.orb_manager     = OrbManager(params["max_energy_orbs"], params["orb_spawn_rate"], sfx)
        self.ui              = GameUI()

    # ══════════════════════════════════════════
    # 星座配置（衝突回避付きランダム配置）
    # ══════════════════════════════════════════
    def _place_constellations(self) -> dict:
        """起動ごとに同一配置になるよう固定シードでランダム配置する"""
        random.seed(100)
        placements = {}
        placed_vectors = []
        num_const = len(self.constellations)

        def to_vec(theta_deg, phi_deg):
            t, p = math.radians(theta_deg), math.radians(phi_deg)
            return (math.cos(p) * math.sin(t), math.sin(p), math.cos(p) * math.cos(t))

        for i, const in enumerate(self.constellations):
            angle_step = 360.0 / max(1, num_const)
            base_theta = i * angle_step
            best = None

            for _ in range(300):
                theta = (base_theta + random.uniform(-18, 18)) % 360.0
                phi   = random.uniform(25.0, 75.0)
                scale = random.uniform(0.18, 0.24)
                v = to_vec(theta, phi)
                min_dist_required = 0.46

                if all(math.sqrt((v[0] - pv[0])**2 + (v[1] - pv[1])**2 + (v[2] - pv[2])**2)
                       >= min_dist_required for pv in placed_vectors):
                    best = (theta, phi, scale, v)
                    break

            if best is None:
                theta = (base_theta + random.uniform(-18, 18)) % 360.0
                phi   = random.uniform(25.0, 75.0)
                scale = random.uniform(0.18, 0.22)
                best  = (theta, phi, scale, to_vec(theta, phi))

            theta, phi, scale, v = best
            placements[const.id] = (theta, phi, scale)
            placed_vectors.append(v)

        return placements

    # ══════════════════════════════════════════
    # 難易度パラメータ
    # ══════════════════════════════════════════
    @staticmethod
    def _build_difficulty_params(difficulty: str) -> dict:
        defaults = dict(
            bug_spawn_rate=0.7, orb_spawn_rate=1.0, max_energy_orbs=1,
            moon_duration=96.0, moon_phase=1.0, draw_moon_visible=True,
            start_p=0.0, end_p=1.0,
        )
        overrides = {
            "NEW_MOON":       dict(moon_phase=0.0, draw_moon_visible=False,
                                   bug_spawn_rate=2.0, orb_spawn_rate=3.0, max_energy_orbs=3),
            "FIRST_QUARTER":  dict(start_p=0.5, moon_duration=48.0, moon_phase=0.5,
                                   bug_spawn_rate=1.5, orb_spawn_rate=2.0, max_energy_orbs=2),
            "WAXING_GIBBOUS": dict(start_p=0.25, moon_duration=72.0, moon_phase=0.75,
                                   bug_spawn_rate=1.0, orb_spawn_rate=1.0, max_energy_orbs=1),
            "FULL_MOON":      dict(moon_phase=1.0, bug_spawn_rate=0.35),
            "WANING_GIBBOUS": dict(end_p=0.75, moon_duration=72.0, moon_phase=-0.75),
            "LAST_QUARTER":   dict(end_p=0.5, moon_duration=48.0, moon_phase=-0.5,
                                   bug_spawn_rate=1.5, orb_spawn_rate=2.0, max_energy_orbs=2),
        }
        params = {**defaults, **overrides.get(difficulty, {})}
        return params

    # ══════════════════════════════════════════
    # 効果音ロード
    # ══════════════════════════════════════════
    def _load_sfx(self, base_dir: str) -> dict:
        sfx_files = {
            "bug_kill":    "A_bursting_sound_nea_#1-1782568383801.mp3",
            "orb_collect": "Sparkly_sound_effect_#3-1782568707614.mp3",
            "ability":     "A_sparkling_sound_ef_#2-1782569003434.mp3",
            "comet_click": "true_clear.mp3",
        }
        volumes = {"bug_kill": 1.0, "orb_collect": 0.4, "ability": 0.4, "comet_click": 0.8}
        result = {}
        for key, fname in sfx_files.items():
            path = os.path.join(base_dir, "source", fname)
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(volumes[key])
                    result[key] = sound
                except Exception as e:
                    print(f"Error loading SFX ({key}): {e}")
                    result[key] = None
            else:
                print(f"Warning: SFX file not found: {path}")
                result[key] = None
        return result

    def enter_view_mode(self):
        """星空観賞モードへ移行し、全状態を正常にリセットする"""
        self.true_clear_view_mode = True
        self.bug_manager.bugs.clear()
        self.orb_manager.orbs.clear()
        for const in self.constellations:
            const.is_broken = False
            for star in const.stars:
                star.is_broken = False

    # ══════════════════════════════════════════
    # 更新
    # ══════════════════════════════════════════
    def update(self, dt: float, keys):
        """ゲームロジック・入力に応じたカメラ操作の更新"""
        # アビリティ残り時間更新
        self.ability_manager.update(dt)

        # スプラッシュエフェクト更新
        for eff in self.splash_effects:
            eff["timer"] -= dt
        self.splash_effects = [e for e in self.splash_effects if e["timer"] > 0]

        # メッセージタイマー更新
        self.message_timer = max(0.0, self.message_timer - dt)

        # カメラ操作
        self._update_camera(dt, keys)

        # 月進捗
        broken_star_ratio = 0.0 # Placeholder logic for broken star count ratio
        progress = self.moon_manager.update(
            dt, 
            getattr(self, "true_clear_view_mode", False), 
            broken_star_ratio
        )

        # 彗星の更新 (新月・上弦の半月・上弦の月で発生)
        self.comet_manager.update(dt, progress, self.moon_manager.moon_phase)

        # バグマネージャー更新（スポーン含む）
        ab = self.ability_manager
        if not getattr(self, "true_clear_view_mode", False):
            self.bug_manager._update_flocking(ab)
            self.bug_manager._update_movement(dt, ab)
            self.bug_manager._update_merging()
            self.bug_manager._spawn_with_dt(dt, progress, self.moon_manager.moon_phi)
            self.bug_manager._check_star_collisions(
                dt, ab, self.constellations, self.constellation_placements, self)

        # エネルギー玉更新
        if not getattr(self, "true_clear_view_mode", False):
            self.orb_manager.update(dt)

        # 各星座の連続繋がり時間更新
        for const in self.constellations:
            if not any(s.is_broken for s in const.stars):
                const.unbroken_time += dt
            else:
                const.unbroken_time = 0.0

        # 月の進行・クリア/ゲームオーバー判定
        self._update_moon(dt, progress)

    def _update_camera(self, dt: float, keys):
        """カメラのヨー・ピッチ・ズームを更新"""
        zoom_ratio = self.coord.current_fov / FOV_DEG
        cam_speed = CAM_SPEED * zoom_ratio
        if self.ability_manager.is_active('fast_camera'):
            cam_speed *= 1.6

        if self.mouse_look_mode:
            dx, dy = pygame.mouse.get_rel()
            sensitivity = 0.12 * zoom_ratio
            if self.ability_manager.is_active('fast_camera'):
                sensitivity *= 1.6
            self.coord.cam_theta = (self.coord.cam_theta - dx * sensitivity) % 360.0
            self.coord.cam_phi = max(-90.0, min(10.0, self.coord.cam_phi + dy * sensitivity))
            screen = pygame.display.get_surface()
            if screen:
                sw, sh = screen.get_size()
                pygame.mouse.set_pos(sw // 2, sh // 2)
        else:
            speed_theta = 0.0
            speed_phi = 0.0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                speed_theta = cam_speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                speed_theta = -cam_speed
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                speed_phi = -cam_speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                speed_phi = cam_speed
            self.coord.cam_theta = (self.coord.cam_theta + speed_theta * dt) % 360.0
            self.coord.cam_phi = max(-90.0, min(10.0, self.coord.cam_phi + speed_phi * dt))

        # ズーム（望遠鏡機能）
        target_fov = 20.0 if keys[pygame.K_SPACE] else FOV_DEG
        zoom_lerp = 10.0 * (2.0 if self.ability_manager.is_active('fast_camera') else 1.0)
        new_fov = self.coord.current_fov + (target_fov - self.coord.current_fov) * zoom_lerp * dt
        self.coord.set_fov(new_fov)

    def _update_moon(self, dt: float, progress: float):
        """月の進行・クリア/ゲームオーバー判定"""
        if self.game_cleared or self.game_over:
            return

        if progress >= 1.0:
            self.game_cleared = True
            print("ゲームクリア！月が西に沈みました。")

        total_consts = len(self.constellations)
        broken_consts = sum(1 for c in self.constellations if any(s.is_broken for s in c.stars))
        unbroken_consts = total_consts - broken_consts
        if total_consts > 0 and unbroken_consts <= 3:
            self.game_over = True
            print(f"ゲームオーバー！残りの正常な星座が{unbroken_consts}個以下になりました。")

    # ══════════════════════════════════════════
    # 描画
    # ══════════════════════════════════════════
    def draw(self, screen):
        """ゲーム画面の描画"""
        ready = self.ability_manager.energy_ready_state
        ready_targets = self.ability_manager.ready_target_consts

        # 1. 星空の描画
        draw_background(screen, self.coord, ready_state=ready, difficulty=self.difficulty)

        # 2. 月の描画
        if self.moon_manager.visible:
            draw_moon(screen, self.coord, self.moon_manager.moon_theta, self.moon_manager.moon_phi,
                      self.moon_manager.moon_phase, ready_state=ready)

        # 3. 星座の描画
        draw_constellations(screen, self.coord, self.constellations,
                            self.constellation_placements,
                            ready_state=ready,
                            ready_target_consts=ready_targets)

        # 4. エネルギー玉の描画
        self.orb_manager.draw(screen, self.coord)

        # 5. バグの描画
        self.bug_manager.draw(screen, self.coord)

        # 5.5 彗星の描画
        self.comet_manager.draw(screen, self.coord, self.ability_manager)

        # 6. HUD / UIの描画
        self.ui.draw_all(screen, self)

    # ══════════════════════════════════════════
    # クリックハンドラ
    # ══════════════════════════════════════════
    def handle_click(self, mouse_pos) -> bool:
        """マウスクリックイベントが発生した際の処理"""
        if self.mouse_look_mode:
            surface = pygame.display.get_surface()
            if surface:
                sw, sh = surface.get_size()
                mouse_pos = (sw // 2, sh // 2)

        zoom_ratio = FOV_DEG / self.coord.current_fov
        is_zoomed_in = self.coord.current_fov < 50.0
        mx, my = mouse_pos
        clicked_any = False

        # 彗星のクリック判定
        if self.comet_manager.handle_click(mx, my, self.coord, self.ability_manager):
            if self.sfx.get("comet_click"):
                self.sfx["comet_click"].play()
            self.game_cleared = True
            self.true_clear = True
            return True

        # 0. 準備状態の星座クリック判定（アビリティ発動）
        if self.ability_manager.energy_ready_state:
            clicked = self._get_clicked_constellation(mouse_pos)
            if clicked and clicked in self.ability_manager.ready_target_consts:
                self.possessed_energy = max(0, self.possessed_energy - 1)
                self.ability_manager.energy_ready_state = False
                self.ability_manager.ready_target_consts = []
                self.ability_manager.activate(clicked.id, self)
                clicked_any = True

        # 0.5. エネルギー玉の回収
        collected = self.orb_manager.check_click(mouse_pos, self.coord, zoom_ratio)
        if collected > 0:
            self.possessed_energy += collected
            self.ability_manager.set_message(
                f"エネルギー玉を回収！ (所持数: {self.possessed_energy})", 2.0)
            print(f"エネルギー玉を回収しました！ 所持数: {self.possessed_energy}")
            clicked_any = True

        # 1. 壊れている星の修復
        if self._try_repair_stars(mouse_pos, zoom_ratio, is_zoomed_in):
            clicked_any = True

        # 2. バグの撃破
        if self.bug_manager.check_click(
                mouse_pos, zoom_ratio, self.ability_manager, self, self.splash_effects):
            clicked_any = True

        # 3. 星座クリック（詳細表示）
        clicked = self._get_clicked_constellation(mouse_pos)
        if clicked:
            if not any(s.is_broken for s in clicked.stars):
                clicked.unbroken_time = 0.0
                print(f"クリックされた星座: {clicked.name} ({clicked.english_name}) のタイマーをリセットしました")
            clicked_any = True

        return clicked_any

    def _get_clicked_constellation(self, mouse_pos):
        """マウス位置が最も近い星座を返す"""
        mx, my = mouse_pos
        zoom_ratio = FOV_DEG / self.coord.current_fov
        clicked_const = None
        min_dist = float('inf')

        for const in self.constellations:
            placement = self.constellation_placements.get(const.id)
            if not placement:
                continue
            theta_c, phi_c, scale = placement
            cx_s, cy_s, visible = self.coord.to_screen(theta_c, phi_c)
            if not visible:
                continue
            base_radius = 120.0 * (scale / 0.22)
            click_radius = base_radius * zoom_ratio
            dist = math.sqrt((mx - cx_s) ** 2 + (my - cy_s) ** 2)
            if dist < click_radius and dist < min_dist:
                min_dist = dist
                clicked_const = const

        return clicked_const

    def _try_repair_stars(self, mouse_pos, zoom_ratio, is_zoomed_in) -> bool:
        """壊れている星をクリックで修復する"""
        mx, my = mouse_pos
        pre_repaired = {c.id: not any(s.is_broken for s in c.stars) for c in self.constellations}
        repaired_any = False

        for const in self.constellations:
            placement = self.constellation_placements.get(const.id)
            if not placement:
                continue
            theta_c, phi_c, scale = placement
            center_pos, u_vec, v_vec = self.coord.get_projection_basis(theta_c, phi_c)
            const_repaired = False

            for star in const.stars:
                if not star.is_broken:
                    continue
                px, py, pz = self.coord.get_star_3d_position(
                    star.curr_x, star.curr_y, center_pos, u_vec, v_vec, scale)
                sx, sy, visible = self.coord.to_screen_3d(px, py, pz)
                if not visible:
                    continue
                dist = math.sqrt((mx - sx) ** 2 + (my - sy) ** 2)
                click_radius = (self.coord.screen_w / 4.0) if is_zoomed_in else (24.0 * zoom_ratio)
                if dist < click_radius:
                    star.is_broken = False
                    star.curr_x = star.orig_x
                    star.curr_y = star.orig_y
                    repaired_any = True
                    const_repaired = True

            if const_repaired:
                if not any(s.is_broken for s in const.stars):
                    self.selected_constellation = const
                    self.message_timer = 4.0
                    print(f"星を元の位置に修復し、星座が完成しました！ (星座: {const.name})")
                else:
                    print(f"星を元の位置に修復しました！ (星座: {const.name}、まだ欠けがあります)")

        if repaired_any:
            for c in self.constellations:
                if not pre_repaired.get(c.id, False) and not any(s.is_broken for s in c.stars):
                    self.repaired_consts_session_count += 1

        return repaired_any

    # ══════════════════════════════════════════
    # エネルギー準備状態
    # ══════════════════════════════════════════
    def toggle_energy_ready(self):
        """Eキー押下時に準備状態をトグルする"""
        self.ability_manager.toggle_ready(self.possessed_energy, self.constellations)

    # ══════════════════════════════════════════
    # bugs プロパティ（後方互換）
    # ══════════════════════════════════════════
    @property
    def bugs(self):
        return self.bug_manager.bugs

    @bugs.setter
    def bugs(self, value):
        self.bug_manager.bugs = value
