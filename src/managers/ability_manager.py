import random


class AbilityManager:
    """星座アビリティの発動・残り時間・準備状態を一元管理するクラス"""

    def __init__(self, sfx):
        """
        sfx: {"bug_kill": Sound|None, "orb_collect": Sound|None, "ability": Sound|None}
        """
        self.sfx = sfx
        self.active = {}           # {ability_name: float(残り秒) | int(残り回数)}
        self.message = ""
        self.message_timer = 0.0
        self.energy_ready_state = False
        self.ready_target_consts = []

    # ──────────────────────────────────────────
    # 毎フレーム更新
    # ──────────────────────────────────────────
    def update(self, dt):
        """各アビリティの残り時間を減らし、切れたものを削除する"""
        keys_to_remove = []
        for key, val in self.active.items():
            if isinstance(val, float):
                self.active[key] -= dt
                if self.active[key] <= 0:
                    keys_to_remove.append(key)
            elif isinstance(val, int) and val <= 0:
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del self.active[key]

        if self.message_timer > 0.0:
            self.message_timer = max(0.0, self.message_timer - dt)

    # ──────────────────────────────────────────
    # アビリティ発動
    # ──────────────────────────────────────────
    def activate(self, const_id, game):
        """
        星座IDに対応したアビリティを発動する。
        game: Game インスタンス（bugs / constellations 等へのアクセスに使用）
        """
        self._play_sfx("ability")

        if const_id == 'c_the_bard':
            self.active['slow_bugs'] = 25.0
            self.message = "吟遊詩人座：安らぎの旋律 (バグ速度40%低下)"

        elif const_id == 'c_the_fox_variant':
            self.active['fast_camera'] = 25.0
            self.message = "狐座：疾出のステップ (カメラ移動1.6倍、ズーム高速化)"

        elif const_id == 'c_the_key':
            self.active['mark_bugs'] = 25.0
            self.message = "鍵座：知理の瞳 (バグ位置の追跡・警告)"

        elif const_id == 'c_coffee_cup':
            pre_repaired = {c.id: not any(s.is_broken for s in c.stars) for c in game.constellations}
            broken_stars = [s for c in game.constellations for s in c.stars if s.is_broken]
            repaired_count = 0
            if broken_stars:
                for star in random.sample(broken_stars, min(13, len(broken_stars))):
                    star.is_broken = False
                    star.curr_x = star.orig_x
                    star.curr_y = star.orig_y
                    repaired_count += 1
            # 修復統計を反映
            for c in game.constellations:
                if not pre_repaired.get(c.id, False) and not any(s.is_broken for s in c.stars):
                    game.repaired_consts_session_count += 1
            self.message = f"珈琲座：アロマの癒やし (ランダムに星を{repaired_count}個修復)"

        elif const_id == 'c_the_spinner':
            self.active['immune_stars'] = 25.0
            self.message = "糸紡ぎ座：守護の結 (すべての星を完全保護)"

        elif const_id == 'c_todaimori':
            visible_bugs = [b for b in game.bugs if game.coord.to_screen(b.theta, b.phi)[2]]
            if visible_bugs:
                self._play_sfx("bug_kill")
                game.defeated_bugs_count += len(visible_bugs)
            for b in visible_bugs:
                game.bugs.remove(b)
            self.message = f"灯台守座：導きの光 (視野内バグを{len(visible_bugs)}体一掃)"

        elif const_id == 'c_fountain_pen':
            pre_repaired = {c.id: not any(s.is_broken for s in c.stars) for c in game.constellations}
            broken_consts = [c for c in game.constellations if any(s.is_broken for s in c.stars)]
            if broken_consts:
                target = random.choice(broken_consts)
                for star in target.stars:
                    star.is_broken = False
                    star.curr_x = star.orig_x
                    star.curr_y = star.orig_y
                for c in game.constellations:
                    if not pre_repaired.get(c.id, False) and not any(s.is_broken for s in c.stars):
                        game.repaired_consts_session_count += 1
                self.message = f"万年筆座：天空の一筆 ({target.name}を完全修復)"
            else:
                self.message = "万年筆座：天空の一筆 (壊れている星座はありません)"

        elif const_id == 'c_twin_volcanoes':
            count = len(game.bugs)
            if count > 0:
                self._play_sfx("bug_kill")
                game.defeated_bugs_count += count
            game.bugs.clear()
            self.message = f"双子火山座：スターバースト (全バグ{count}体を一掃)"

        elif const_id == 'c_echo':
            self.active['knockback_bugs'] = 25.0
            for bug in game.bugs:
                bug.phi = 20.0
                bug.vy = 0.0
            self.message = "こだま座：音響ノックバック (バグを地平線に強制後退)"

        elif const_id == 'c_broken_sword':
            self.active['splash_kill'] = 25.0
            self.message = "折れた剣座：衝撃の刃 (バグ撃破時に周囲も一掃)"

        elif const_id == 'c_butterfly':
            self.active['auto_pull_stars'] = 25.0
            self.message = "蝶座：導きの羽ばたき (ちぎれた星の自動引き寄せ修復)"

        elif const_id == 'c_whale':
            self.active['anti_gravity'] = 25.0
            for bug in game.bugs:
                if bug.is_blackhole:
                    bug.is_blackhole = False
                    bug.level = 1
                    bug.size_scale = 1.0
            self.message = "鯨座：宿まりの重力 (ブラックホール全無力化)"

        elif const_id == 'c_child':
            count = len(game.bugs)
            if count > 0:
                self._play_sfx("bug_kill")
                game.defeated_bugs_count += count
            game.bugs.clear()
            self.message = f"こども座：星屑の悪戯 (全バグ{count}体を流れ星として消散)"

        elif const_id == 'c_dragon':
            self.active['dragon_shield'] = 3
            self.message = "ドラゴン座：天壁の盾 (星の破壊を防ぐバリア 3回分)"

        self.message_timer = 4.0

    # ──────────────────────────────────────────
    # 準備状態トグル
    # ──────────────────────────────────────────
    def toggle_ready(self, possessed_energy, constellations):
        """
        Eキー押下時に準備状態をトグルする。
        possessed_energy: int
        constellations: list
        戻り値: (energy_ready_state: bool, ready_target_consts: list)
        """
        if possessed_energy > 0:
            self.energy_ready_state = not self.energy_ready_state
            if self.energy_ready_state:
                repaired = [c for c in constellations if not any(s.is_broken for s in c.stars)]
                self.ready_target_consts = random.sample(repaired, min(3, len(repaired)))
                print(f"能力発動準備状態に入りました。選択可能星座: {[c.name for c in self.ready_target_consts]}")
            else:
                self.ready_target_consts = []
                print("能力発動準備状態を解除しました。")
        else:
            self.energy_ready_state = False
            self.ready_target_consts = []
            self.message = "エネルギーを所持していません"
            self.message_timer = 2.0
            print("警告: エネルギーを所持していないため、準備状態に移行できません。")
        return self.energy_ready_state, self.ready_target_consts

    # ──────────────────────────────────────────
    # ヘルパー
    # ──────────────────────────────────────────
    def is_active(self, name: str) -> bool:
        return name in self.active

    def get_charge(self, name: str):
        """残り時間(float)または残り回数(int)を返す。存在しない場合は0"""
        return self.active.get(name, 0)

    def set_charge(self, name: str, value):
        """直接セット（dragon_shield の消費など）"""
        self.active[name] = value

    def set_message(self, msg: str, timer: float = 2.0):
        self.message = msg
        self.message_timer = timer

    def _play_sfx(self, kind: str):
        sfx = self.sfx.get(kind)
        if sfx:
            try:
                sfx.play()
            except Exception as e:
                print(f"Error playing SFX ({kind}): {e}")
