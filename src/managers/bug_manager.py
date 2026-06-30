import math
import random

from src.entities.bug import Bug


class BugManager:
    """
    バグ（グリッチ）のスポーン・AI（群れ行動・合体）・
    星座接触判定・アビリティ効果適用を管理するクラス。
    """

    def __init__(self, coord, bug_spawn_rate: float, sfx):
        """
        coord:          DomeCoord インスタンス
        bug_spawn_rate: 難易度ベースのスポーン速度倍率
        sfx:            {"bug_kill": Sound|None}
        """
        self.coord = coord
        self.bug_spawn_rate = bug_spawn_rate
        self.sfx = sfx

        self.bugs: list[Bug] = [Bug()]
        self.spawn_timer = random.uniform(6.0, 12.0) / self.bug_spawn_rate

    # ──────────────────────────────────────────
    # 毎フレーム更新
    # ──────────────────────────────────────────
    def update(self, dt: float, ability_manager, constellations,
               constellation_placements, progress: float, moon_phi: float,
               game, is_lunar_eclipse: bool = False):
        """
        ability_manager: AbilityManager
        constellations:  星座リスト
        constellation_placements: {id: (theta, phi, scale)}
        progress:        月の進捗 0.0–1.0
        moon_phi:        月の仰角
        game:            Game（defeated_bugs_count / repaired_consts_session_count 等）
        """
        self._update_flocking(ability_manager)
        self._update_movement(dt, ability_manager, is_lunar_eclipse)
        self._update_merging()
        self._spawn_if_needed(progress, moon_phi)
        self._check_star_collisions(dt, ability_manager, constellations,
                                    constellation_placements, game)

    # ──────────────────────────────────────────
    # 群れ行動・アビリティ効果
    # ──────────────────────────────────────────
    def _update_flocking(self, ability_manager):
        """バグ同士の引き寄せ（群れ行動）"""
        num_bugs = len(self.bugs)
        for i in range(num_bugs):
            bug_a = self.bugs[i]
            closest_bug = None
            min_dist = float('inf')
            closest_d_theta = 0.0
            closest_d_phi = 0.0

            for j in range(num_bugs):
                if i == j:
                    continue
                bug_b = self.bugs[j]
                d_theta = (bug_b.theta - bug_a.theta + 180) % 360 - 180
                d_phi = bug_b.phi - bug_a.phi
                dist = math.sqrt(d_theta ** 2 + d_phi ** 2)
                if dist < min_dist:
                    min_dist = dist
                    closest_bug = bug_b
                    closest_d_theta = d_theta
                    closest_d_phi = d_phi

            if closest_bug and min_dist < 25.0:
                angle = math.atan2(closest_d_phi, closest_d_theta)
                is_bh_involved = bug_a.is_blackhole or closest_bug.is_blackhole
                current_speed = bug_a.speed * (1.5 if is_bh_involved else 1.1)
                bug_a.vx = current_speed * math.cos(angle)
                bug_a.vy = current_speed * math.sin(angle)
                bug_a.change_dir_timer = random.uniform(2.0, 6.0)

        # こだま座「音響ノックバック」
        if ability_manager.is_active('knockback_bugs'):
            for bug in self.bugs:
                bug.phi = 20.0
                bug.vy = 0.0

        # 鯨座「宿まりの重力」
        if ability_manager.is_active('anti_gravity'):
            for bug in self.bugs:
                if bug.is_blackhole:
                    bug.is_blackhole = False
                    bug.level = 1
                    bug.size_scale = 1.0

    def _update_movement(self, dt: float, ability_manager, is_lunar_eclipse: bool = False):
        """各バグの位置更新"""
        bug_dt = dt * 0.6 if ability_manager.is_active('slow_bugs') else dt
        if is_lunar_eclipse:
            bug_dt *= 1.3
        for bug in self.bugs:
            bug.update(bug_dt)

    # ──────────────────────────────────────────
    # 合体・BH化
    # ──────────────────────────────────────────
    def _update_merging(self):
        """バグ同士が極接近したら合体してブラックホール化"""
        num_bugs = len(self.bugs)
        merged_indices = set()
        for i in range(num_bugs):
            if i in merged_indices:
                continue
            bug_a = self.bugs[i]
            for j in range(i + 1, num_bugs):
                if j in merged_indices:
                    continue
                bug_b = self.bugs[j]
                t_a, p_a = math.radians(bug_a.theta), math.radians(bug_a.phi)
                xa, ya, za = (math.cos(p_a) * math.sin(t_a),
                              math.sin(p_a),
                              math.cos(p_a) * math.cos(t_a))
                t_b, p_b = math.radians(bug_b.theta), math.radians(bug_b.phi)
                xb, yb, zb = (math.cos(p_b) * math.sin(t_b),
                              math.sin(p_b),
                              math.cos(p_b) * math.cos(t_b))
                dist_3d = math.sqrt((xa - xb) ** 2 + (ya - yb) ** 2 + (za - zb) ** 2)
                if dist_3d < 0.08:
                    bug_a.level += bug_b.level
                    bug_a.is_blackhole = True
                    bug_a.size_scale = 1.0 + (bug_a.level - 1) * 0.4
                    merged_indices.add(j)
                    print(f"バグが合体しました！ブラックホール化 "
                          f"(レベル: {bug_a.level}, サイズスケール: {bug_a.size_scale:.1f}倍)")

        self.bugs = [self.bugs[k] for k in range(num_bugs) if k not in merged_indices]

    # ──────────────────────────────────────────
    # スポーン
    # ──────────────────────────────────────────
    def _spawn_if_needed(self, progress: float, moon_phi: float):
        """月の進捗に応じてバグを自動スポーン"""
        max_bugs = 10 + int(progress * 4)
        if len(self.bugs) >= max_bugs:
            return

        self.spawn_timer -= 0  # dt は呼び出し元の update から渡す必要があるため
        # ※ dt を引数に追加してここで使う実装にする
        # （後の _spawn_with_dt で対処）

    def _spawn_with_dt(self, dt: float, progress: float, moon_phi: float):
        max_bugs = 10 + int(progress * 4)
        if len(self.bugs) >= max_bugs:
            return
        self.spawn_timer -= dt
        if self.spawn_timer > 0.0:
            return

        is_near_zenith = moon_phi >= 35.0
        if is_near_zenith and len(self.bugs) + 1 < max_bugs:
            theta1 = random.uniform(0.0, 360.0)
            phi1 = random.uniform(25.0, 70.0)
            theta2 = (theta1 + random.uniform(60.0, 300.0)) % 360.0
            phi2 = random.uniform(25.0, 70.0)
            self.bugs.append(Bug(theta1, phi1))
            self.bugs.append(Bug(theta2, phi2))
            print(f"バグが2体出現（天頂付近、異なる位置）: 残り: {len(self.bugs)}体")
        else:
            self.bugs.append(Bug())
            print(f"バグが出現！ 残り: {len(self.bugs)}体")

        min_spawn = max(1.5, 6.0 - progress * 5.0)
        max_spawn = max(3.5, 12.0 - progress * 9.0)
        self.spawn_timer = random.uniform(min_spawn, max_spawn) / self.bug_spawn_rate
        print(f"次のバグ出現間隔: {min_spawn:.1f}〜{max_spawn:.1f}秒 (最大上限: {max_bugs})")

    # ──────────────────────────────────────────
    # 星座接触判定
    # ──────────────────────────────────────────
    def _check_star_collisions(self, dt, ability_manager, constellations,
                               constellation_placements, game):
        """バグと星の衝突判定・星の漂流更新"""
        for const in constellations:
            placement = constellation_placements.get(const.id)
            if not placement:
                continue
            theta_c, phi_c, scale = placement
            center_pos, u_vec, v_vec = self.coord.get_projection_basis(theta_c, phi_c)
            cx, cy, cz = center_pos
            ux, uy, uz = u_vec
            vx, vy, vz = v_vec

            for star in const.stars:
                if not star.is_broken:
                    # 糸紡ぎ座「守護の結」による無敵状態
                    if not ability_manager.is_active('immune_stars'):
                        star_p = self.coord.get_star_3d_position(
                            star.curr_x, star.curr_y, center_pos, u_vec, v_vec, scale)
                        bug_to_remove = None
                        for bug in self.bugs:
                            bx, by, bz = bug.get_3d_position()
                            dist = math.sqrt((star_p[0] - bx) ** 2 +
                                             (star_p[1] - by) ** 2 +
                                             (star_p[2] - bz) ** 2)
                            break_threshold = 0.07 * (2.2 if bug.is_blackhole else 1.0) * bug.size_scale
                            if dist < break_threshold:
                                shield = ability_manager.get_charge('dragon_shield')
                                if shield > 0:
                                    ability_manager.set_charge('dragon_shield', shield - 1)
                                    ability_manager.set_message(
                                        f"天壁の盾が発動！ (残りシールド: {shield - 1}回)", 2.0)
                                    print(f"天壁の盾が星の破壊を防いだ！ "
                                          f"バグを撃退しました。 残り: {shield - 1}回")
                                    bug_to_remove = bug
                                else:
                                    star.is_broken = True
                                    star.drift_vx = random.uniform(-0.15, 0.15)
                                    star.drift_vy = random.uniform(-0.15, 0.15)
                                    print(f"バグ接触（範囲: {break_threshold:.2f}）、"
                                          f"星の繋ぎが崩れました！")
                                break
                        if bug_to_remove and bug_to_remove in self.bugs:
                            self.bugs.remove(bug_to_remove)
                            self._play_sfx()
                            game.defeated_bugs_count += 1
                else:
                    # 漂流処理
                    if ability_manager.is_active('auto_pull_stars'):
                        dx = star.orig_x - star.curr_x
                        dy = star.orig_y - star.curr_y
                        p_dist = math.sqrt(dx ** 2 + dy ** 2)
                        if p_dist > 0.001:
                            pull_speed = 0.175
                            star.curr_x += (dx / p_dist) * pull_speed * dt
                            star.curr_y += (dy / p_dist) * pull_speed * dt
                            new_dist = math.sqrt((star.orig_x - star.curr_x) ** 2 +
                                                 (star.orig_y - star.curr_y) ** 2)
                            if new_dist < 0.03:
                                star.is_broken = False
                                star.curr_x = star.orig_x
                                star.curr_y = star.orig_y
                                if not any(s.is_broken for s in const.stars):
                                    game.selected_constellation = const
                                    game.message_timer = 4.0
                                    print(f"蝶座の力により {const.name} が修復されました！")
                    else:
                        star.curr_x += star.drift_vx * dt
                        star.curr_y += star.drift_vy * dt

                        # ブラックホールによる引力
                        if not ability_manager.is_active('anti_gravity'):
                            for bug in self.bugs:
                                if not bug.is_blackhole:
                                    continue
                                bx, by, bz = bug.get_3d_position()
                                star_p = self.coord.get_star_3d_position(
                                    star.curr_x, star.curr_y, center_pos, u_vec, v_vec, scale)
                                dist_3d = math.sqrt((star_p[0] - bx) ** 2 +
                                                    (star_p[1] - by) ** 2 +
                                                    (star_p[2] - bz) ** 2)
                                if dist_3d < 0.35:
                                    bdx, bdy, bdz = bx - cx, by - cy, bz - cz
                                    bh_lx = (bdx * ux + bdy * uy + bdz * uz) / scale
                                    bh_ly = (bdx * vx + bdy * vy + bdz * vz) / scale
                                    pdx = bh_lx - star.curr_x
                                    pdy = bh_ly - star.curr_y
                                    p_dist = math.sqrt(pdx ** 2 + pdy ** 2)
                                    if p_dist > 0.02:
                                        pull = (0.25 * bug.size_scale) / (p_dist + 0.1)
                                        star.curr_x += (pdx / p_dist) * pull * dt
                                        star.curr_y += (pdy / p_dist) * pull * dt

                        # バウンド
                        if not ability_manager.is_active('auto_pull_stars'):
                            dist_from_orig = math.sqrt(
                                (star.curr_x - star.orig_x) ** 2 +
                                (star.curr_y - star.orig_y) ** 2)
                            if dist_from_orig > 0.40:
                                dx = star.orig_x - star.curr_x
                                dy = star.orig_y - star.curr_y
                                angle = math.atan2(dy, dx) + random.uniform(-0.4, 0.4)
                                star.drift_vx = 0.15 * math.cos(angle)
                                star.drift_vy = 0.15 * math.sin(angle)

    # ──────────────────────────────────────────
    # クリック判定
    # ──────────────────────────────────────────
    def check_click(self, mouse_pos, zoom_ratio: float, ability_manager,
                    game, splash_effects) -> bool:
        """
        クリックされたバグを撃破する。
        折れた剣座「衝撃の刃」によるスプラッシュも処理する。
        戻り値: クリックが何かに当たったか
        """
        mx, my = mouse_pos
        bugs_to_remove = []
        for bug in self.bugs:
            bx, by, visible = self.coord.to_screen(bug.theta, bug.phi)
            if visible:
                dist = math.sqrt((mx - bx) ** 2 + (my - by) ** 2)
                if dist < 32.0 * zoom_ratio:
                    bugs_to_remove.append(bug)

        if not bugs_to_remove:
            return False

        self._play_sfx()
        game.defeated_bugs_count += len(bugs_to_remove)

        # 折れた剣座「衝撃の刃」スプラッシュ
        if ability_manager.is_active('splash_kill'):
            clicked_bug = bugs_to_remove[0]
            cx_b, cy_b, _ = self.coord.to_screen(clicked_bug.theta, clicked_bug.phi)
            splash_bugs = []
            for other in self.bugs:
                if other not in bugs_to_remove:
                    ox, oy, visible = self.coord.to_screen(other.theta, other.phi)
                    if visible:
                        dist = math.sqrt((cx_b - ox) ** 2 + (cy_b - oy) ** 2)
                        if dist < 150.0:
                            splash_bugs.append(other)
            if splash_bugs:
                self._play_sfx()
                game.defeated_bugs_count += len(splash_bugs)
                for b in splash_bugs:
                    self.bugs.remove(b)
                splash_effects.append({
                    "pos": (cx_b, cy_b),
                    "timer": 0.4,
                    "max_timer": 0.4
                })
                print(f"衝撃の刃！波動により周囲のバグを{len(splash_bugs)}体殲滅！")

        for b in bugs_to_remove:
            if b in self.bugs:
                self.bugs.remove(b)
        print(f"バグを修復（駆除）しました！ 残り: {len(self.bugs)}体")
        return True

    # ──────────────────────────────────────────
    # 描画
    # ──────────────────────────────────────────
    def draw(self, screen, coord):
        for bug in self.bugs:
            bug.draw(screen, coord)

    # ──────────────────────────────────────────
    # ヘルパー
    # ──────────────────────────────────────────
    def _play_sfx(self):
        sfx = self.sfx.get("bug_kill")
        if sfx:
            try:
                sfx.play()
            except Exception as e:
                print(f"Error playing Bug Kill SFX: {e}")
