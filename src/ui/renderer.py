import pygame
import math
import random

SCREEN_W = 1920/1.2
SCREEN_H = 1080/1.2
SHOW_ART_LINES = False

DIRECTION_FONT = None

def get_catmull_rom_point(p0, p1, p2, p3, t):
    """p1 と p2 の間を t (0.0〜1.0) でスプライン補間した座標を返す"""
    t2 = t * t
    t3 = t2 * t
    
    x = 0.5 * ((2.0 * p1[0]) + 
               (-p0[0] + p2[0]) * t + 
               (2.0 * p0[0] - 5.0 * p1[0] + 4.0 * p2[0] - p3[0]) * t2 + 
               (-p0[0] + 3.0 * p1[0] - 3.0 * p2[0] + p3[0]) * t3)
               
    y = 0.5 * ((2.0 * p1[1]) + 
               (-p0[1] + p2[1]) * t + 
               (2.0 * p0[1] - 5.0 * p1[1] + 4.0 * p2[1] - p3[1]) * t2 + 
               (-p0[1] + 3.0 * p1[1] - 3.0 * p2[1] + p3[1]) * t3)
    return (x, y)

def interpolate_path(path, num_segments=10):
    """パス全体の頂点の間を Catmull-Rom スプラインで補間し、高密度な点リストを生成する"""
    if len(path) < 2:
        return path
    
    interpolated = []
    n = len(path)
    
    for i in range(n - 1):
        p0 = path[i-1] if i > 0 else path[0]
        p1 = path[i]
        p2 = path[i+1]
        p3 = path[i+2] if i+2 < n else path[n-1]
        
        for j in range(num_segments):
            t = j / float(num_segments)
            pt = get_catmull_rom_point(p0, p1, p2, p3, t)
            interpolated.append(pt)
            
    interpolated.append(path[-1])
    return interpolated

def generate_stars(count=200):
    stars = []
    for _ in range(count):
        t = random.uniform(0, 360)
        # 上の方ほど星の密度が偏らないように調整
        p = math.degrees(math.asin(random.uniform(0, 1))) 
        size = random.choice([1, 2, 2, 3])
        stars.append((t, p, size))
    return stars

# 初期の背景の星を生成
STARS = generate_stars(300)

def draw_background(screen, coord, ready_state=False, difficulty="FULL_MOON"):
    if ready_state:
        screen.fill((1, 2, 4)) # 夜空の背景色を極めて暗く
    elif difficulty == "NEW_MOON":
        screen.fill((2, 3, 6)) # 新月（EXPERT）用の極限の闇夜
    else:
        screen.fill((5, 10, 20)) # 夜空の背景色

    # ── 経線 (Longitude: 縦の線) ──
    if ready_state:
        grid_color = (8, 10, 18)
    elif difficulty == "NEW_MOON":
        grid_color = (12, 16, 28) # 新月用の暗い経緯線
    else:
        grid_color = (30, 40, 70)
        
    for t in range(0, 360, 10):
        points = []
        for p in range(0, 91, 2):
            sx, sy, visible = coord.to_screen(t, p)
            if visible:
                points.append((sx, sy))
            else:
                if len(points) > 1:
                    for i in range(len(points) - 1):
                        pygame.draw.aaline(screen, grid_color, points[i], points[i+1])
                points = []
        if len(points) > 1:
            for i in range(len(points) - 1):
                pygame.draw.aaline(screen, grid_color, points[i], points[i+1])

    # ── 緯線 (Latitude: 横の線) ──
    for p in range(0, 91, 10):
        points = []
        for t in range(0, 365, 2):
            sx, sy, visible = coord.to_screen(t, p)
            if visible:
                points.append((sx, sy))
            else:
                if len(points) > 1:
                    color = (25, 15, 15) if p == 0 else grid_color
                    for i in range(len(points) - 1):
                        pygame.draw.aaline(screen, color, points[i], points[i+1])
                points = []
        if len(points) > 1:
            color = (25, 15, 15) if p == 0 else grid_color
            for i in range(len(points) - 1):
                pygame.draw.aaline(screen, color, points[i], points[i+1])

    # ── 星の描画 ──
    if ready_state:
        star_color = (40, 50, 60)
    elif difficulty == "NEW_MOON":
        star_color = (130, 145, 175) # 新月用の少し明度を落とした星々
    else:
        star_color = (200, 220, 255)
        
    for t, p, size in STARS:
        sx, sy, visible = coord.to_screen(t, p)
        if visible:
            pygame.draw.circle(screen, star_color, (int(sx), int(sy)), size)

    # ── 天頂（ドームの頂点）の目印 ──
    zenith_color = (60, 25, 25) if ready_state else (255, 100, 100)
    sx, sy, visible = coord.to_screen(0, 90)
    if visible:
        pygame.draw.circle(screen, zenith_color, (int(sx), int(sy)), 5)
        pygame.draw.circle(screen, zenith_color, (int(sx), int(sy)), 10, 1)

    # ── 方角の目印 ──
    global DIRECTION_FONT
    if DIRECTION_FONT is None:
        DIRECTION_FONT = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 18, bold=True)
        if not DIRECTION_FONT:
            DIRECTION_FONT = pygame.font.SysFont(None, 22, bold=True)

    directions = [
        (0, "N (北)"),
        (45, "NE"),
        (90, "E (東)"),
        (135, "SE"),
        (180, "S (南)"),
        (225, "SW"),
        (270, "W (西)"),
        (315, "NW")
    ]

    for theta, label in directions:
        sx, sy, visible = coord.to_screen(theta, 0.0)
        if visible:
            if ready_state:
                color = (60, 25, 25) if " " in label else (35, 35, 40)
            else:
                color = (240, 100, 100) if " " in label else (140, 140, 150)
            text_surf = DIRECTION_FONT.render(label, True, color)
            tx = int(sx) - text_surf.get_width() // 2
            ty = int(sy) - text_surf.get_height() - 4
            screen.blit(text_surf, (tx, ty))

def draw_constellations(screen, coord, constellations, placements, ready_state=False, ready_target_consts=None):
    for const in constellations:
        # 準備状態の時は、選択可能な3つの星座以外の描画を完全にスキップする
        if ready_state and ready_target_consts is not None:
            if const not in ready_target_consts:
                continue

        placement = placements.get(const.id, (0.0, 45.0, 0.2))
        theta_c, phi_c, scale = placement
        
        # 天球上の中心から接平面の直交基底ベクトルと中心位置を算出
        center_pos, u_vec, v_vec = coord.get_projection_basis(theta_c, phi_c)
        cx, cy, cz = center_pos
        ux, uy, uz = u_vec
        vx, vy, vz = v_vec
        
        star_screen_coords = []
        for star in const.stars:
            # 星の現在の座標を3D投影・正規化して取得
            px, py, pz = coord.get_star_3d_position(star.curr_x, star.curr_y, center_pos, u_vec, v_vec, scale)
            sx, sy, visible = coord.to_screen_3d(px, py, pz)
            star_screen_coords.append((sx, sy, visible))
            
        # 星座がすべて繋がっているか判定（壊れている星が一つもない）
        is_fully_connected = not any(star.is_broken for star in const.stars)

        # 星座線の描画
        for line in const.lines:
            idx1, idx2 = line
            if idx1 < len(star_screen_coords) and idx2 < len(star_screen_coords):
                # 接続する星のどちらかが壊れて（漂って）いたら線を描画しない
                if const.stars[idx1].is_broken or const.stars[idx2].is_broken:
                    continue
                sx1, sy1, vis1 = star_screen_coords[idx1]
                sx2, sy2, vis2 = star_screen_coords[idx2]
                if vis1 and vis2:
                    if ready_state:
                        # 選択可能な星座の線をエネルギー玉と同じ色（ネオンシアン）にする
                        pygame.draw.line(screen, (0, 255, 230), (int(sx1), int(sy1)), (int(sx2), int(sy2)), 2)
                    elif is_fully_connected:
                        # 金色で少し太い線（太さ2）
                        pygame.draw.line(screen, (235, 180, 60), (int(sx1), int(sy1)), (int(sx2), int(sy2)), 2)
                    else:
                        # 通常の青っぽい細い線（太さ1）
                        pygame.draw.line(screen, (80, 130, 200), (int(sx1), int(sy1)), (int(sx2), int(sy2)), 1)
                    
        # 星の描画
        for i, star in enumerate(const.stars):
            # 1. 壊れている星は、元の位置に「影（ゴースト）」を描画する
            if star.is_broken:
                px_o, py_o, pz_o = coord.get_star_3d_position(star.orig_x, star.orig_y, center_pos, u_vec, v_vec, scale)
                sox, soy, s_vis = coord.to_screen_3d(px_o, py_o, pz_o)
                if s_vis:
                    # 薄い半透明の星の影を描画 (点線のように見える外枠二重円)
                    pygame.draw.circle(screen, (60, 85, 110), (int(sox), int(soy)), 5, 1)
                    pygame.draw.circle(screen, (35, 45, 55), (int(sox), int(soy)), 2)
            
            # 2. 現在の位置の星を描画 (動的な位置)
            sx, sy, visible = star_screen_coords[i]
            if visible:
                size = max(1, int(4 - star.magnitude))
                # 壊れている星は赤く、通常は白く描画
                if star.is_broken:
                    color = (255, 50, 70)
                else:
                    if ready_state:
                        color = (200, 255, 255)
                    else:
                        color = (240, 240, 255)
                pygame.draw.circle(screen, color, (int(sx), int(sy)), size)
                
        # ── イラスト線画 (art_paths) の描画 ──
        if SHOW_ART_LINES:
            for raw_path in const.art_paths:
                # 各パスを10分割して非常に滑らかにスプライン補間する
                path = interpolate_path(raw_path, num_segments=10)
                
                projected_points = []
                for pt in path:
                    # 接平面上で座標を算出し、天球表面へ正規化射影する
                    px, py, pz = coord.get_star_3d_position(pt[0], pt[1], center_pos, u_vec, v_vec, scale)
                    sx, sy, visible = coord.to_screen_3d(px, py, pz)
                    projected_points.append((sx, sy, visible))
                    
                # 補間された点同士を接続して滑らかなイラスト線を描画
                for i in range(len(projected_points) - 1):
                    sx1, sy1, vis1 = projected_points[i]
                    sx2, sy2, vis2 = projected_points[i+1]
                    
                    if vis1 and vis2:
                        line_color = (0, 200, 200) if ready_state else (220, 175, 75)
                        pygame.draw.aaline(screen, line_color, (sx1, sy1), (sx2, sy2))

        # 星座名（日本語）の描画
        cx_s, cy_s, c_visible = coord.to_screen(theta_c, phi_c)
        if c_visible:
            font = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 20)
            if not font:
                font = pygame.font.SysFont(None, 24)
            text_color = (0, 255, 230) if ready_state else (150, 180, 225)
            name_text = font.render(const.name, True, text_color)
            screen.blit(name_text, (int(cx_s) - name_text.get_width() // 2, int(cy_s) - 25))

def draw_title_screen(screen, elapsed_time):
    # タイトルロゴの描画
    font_large = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 64, bold=True)
    if not font_large:
        font_large = pygame.font.SysFont(None, 80)
        
    title_text = font_large.render("Stella Repairer", True, (255, 255, 255))
    # タイトル文字の影（シャドウ）
    title_shadow = font_large.render("Stella Repairer", True, (10, 15, 30))
    
    # 画面中央上部
    tx = SCREEN_W // 2 - title_text.get_width() // 2
    ty = SCREEN_H // 3
    screen.blit(title_shadow, (tx + 4, ty + 4))
    screen.blit(title_text, (tx, ty))

    # スタートガイダンスの描画（滑らかな明滅効果）
    font_sub = pygame.font.SysFont(None, 32)
    # 1秒間に約1往復するブレス効果
    pulse = (math.sin(elapsed_time * 3.0) + 1.0) / 2.0  # 0.0 〜 1.0
    color_val = int(100 + pulse * 155)  # 100 〜 255 の間で明るさを変化
    guidance_color = (color_val, color_val, int(color_val * 1.1) if color_val * 1.1 < 255 else 255)
    
    guidance_text = font_sub.render("[ CLICK OR PRESS ENTER TO START ]", True, guidance_color)
    gx = SCREEN_W // 2 - guidance_text.get_width() // 2
    gy = SCREEN_H * 2 // 3
    screen.blit(guidance_text, (gx, gy))

def draw_moon(screen, coord, theta, phi, phase, ready_state=False):
    """月の描画（半透明グロー付きの美しい月 - 満ち欠け対応・ズーム対応）"""
    sx, sy, visible = coord.to_screen(theta, phi)
    if not visible:
        return
        
    # ズーム倍率
    zoom_ratio = 90.0 / coord.current_fov
    r = int(24 * zoom_ratio)  # 月のコア半径
    
    # 半透明の月光グロー効果
    glow_surf = pygame.Surface((r * 8, r * 8), pygame.SRCALPHA)
    glow_center = r * 4
    
    # グローの色と不透明度
    if ready_state:
        glow_color = (255, 245, 180)
        glow_alphas = [4, 10, 20]
    else:
        glow_color = (255, 245, 180)
        glow_alphas = [20, 50, 90]
        
    pygame.draw.circle(glow_surf, (glow_color[0], glow_color[1], glow_color[2], glow_alphas[0]), (glow_center, glow_center), int(90 * zoom_ratio))
    pygame.draw.circle(glow_surf, (glow_color[0], glow_color[1], glow_color[2], glow_alphas[1]), (glow_center, glow_center), int(56 * zoom_ratio))
    pygame.draw.circle(glow_surf, (glow_color[0], glow_color[1], glow_color[2], glow_alphas[2]), (glow_center, glow_center), int(32 * zoom_ratio))
    screen.blit(glow_surf, (int(sx) - glow_center, int(sy) - glow_center))
    
    # 月のコアの描画 (満ち欠け対応)
    moon_color = (70, 68, 60) if ready_state else (255, 253, 225)
    shadow_color = (5, 10, 20)  # 夜空の背景色

    # 新月
    if phase == 0.0:
        pygame.draw.circle(screen, (40, 50, 70), (int(sx), int(sy)), r)
        pygame.draw.circle(screen, shadow_color, (int(sx), int(sy)), max(1, r - int(2 * zoom_ratio)))
    elif phase == 1.0:
        # 満月
        pygame.draw.circle(screen, moon_color, (int(sx), int(sy)), r)
        # クレーター
        pygame.draw.circle(screen, (245, 235, 195) if not ready_state else (60, 56, 48), (int(sx) - int(6 * zoom_ratio), int(sy) - int(4 * zoom_ratio)), int(6 * zoom_ratio))
        pygame.draw.circle(screen, (245, 235, 195) if not ready_state else (60, 56, 48), (int(sx) + int(8 * zoom_ratio), int(sy) + int(6 * zoom_ratio)), int(4 * zoom_ratio))
    elif phase == 0.5:
        # 上弦の月 (右半分が光る)
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, moon_color, (r, r), r)
        surf.fill((0, 0, 0, 0), (0, 0, r, r * 2), special_flags=pygame.BLEND_RGBA_MIN)
        pygame.draw.circle(surf, (245, 235, 195) if not ready_state else (60, 56, 48), (r + int(6 * zoom_ratio), r + int(4 * zoom_ratio)), int(4 * zoom_ratio))
        screen.blit(surf, (int(sx) - r, int(sy) - r))
        pygame.draw.arc(screen, (40, 50, 70), (int(sx) - r, int(sy) - r, r * 2, r * 2), math.pi/2, 3*math.pi/2, 1)
    elif phase == -0.5:
        # 下弦の月 (左半分が光る)
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, moon_color, (r, r), r)
        surf.fill((0, 0, 0, 0), (r, 0, r, r * 2), special_flags=pygame.BLEND_RGBA_MIN)
        pygame.draw.circle(surf, (245, 235, 195) if not ready_state else (60, 56, 48), (r - int(6 * zoom_ratio), r + int(4 * zoom_ratio)), int(4 * zoom_ratio))
        screen.blit(surf, (int(sx) - r, int(sy) - r))
        pygame.draw.arc(screen, (40, 50, 70), (int(sx) - r, int(sy) - r, r * 2, r * 2), -math.pi/2, math.pi/2, 1)
    elif phase == 0.75:
        # 十三夜月 (右側が大きく光る)
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, moon_color, (r, r), r)
        mask = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        mask.fill((255, 255, 255, 255))
        pygame.draw.circle(mask, (0, 0, 0, 0), (r - int(r * 1.25), r), r)
        surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        pygame.draw.circle(surf, (245, 235, 195) if not ready_state else (60, 56, 48), (r + int(4 * zoom_ratio), r - int(4 * zoom_ratio)), int(4 * zoom_ratio))
        screen.blit(surf, (int(sx) - r, int(sy) - r))
        pygame.draw.arc(screen, (40, 50, 70), (int(sx) - r, int(sy) - r, r * 2, r * 2), math.pi/2, 3*math.pi/2, 1)
    elif phase == -0.75:
        # 凸月 (左側が大きく光る)
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, moon_color, (r, r), r)
        mask = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        mask.fill((255, 255, 255, 255))
        pygame.draw.circle(mask, (0, 0, 0, 0), (r + int(r * 1.25), r), r)
        surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        pygame.draw.circle(surf, (245, 235, 195) if not ready_state else (60, 56, 48), (r - int(4 * zoom_ratio), r - int(4 * zoom_ratio)), int(4 * zoom_ratio))
        screen.blit(surf, (int(sx) - r, int(sy) - r))
        pygame.draw.arc(screen, (40, 50, 70), (int(sx) - r, int(sy) - r, r * 2, r * 2), -math.pi/2, math.pi/2, 1)
def draw_clear_screen(screen, game):
    """ゲームクリア画面の描画"""
    sw = screen.get_width()
    sh = screen.get_height()
    
    # 1. 画面全体のフェードアウト半透明オーバーレイ
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((5, 10, 25, 200)) # 深い紺色の半透明マスク
    screen.blit(overlay, (0, 0))
    
    # 2. ゴールドを基調とした中央の装飾パネル
    panel_w, panel_h = 700, 450
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((10, 20, 40, 230))
    # ゴールドの外枠二重線
    pygame.draw.rect(panel, (235, 180, 60), (0, 0, panel_w, panel_h), 3)
    pygame.draw.rect(panel, (120, 90, 30), (4, 4, panel_w - 8, panel_h - 8), 1)
    
    # フォント読み込み
    font_large = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 54, bold=True)
    if not font_large:
        font_large = pygame.font.SysFont(None, 64, bold=True)
    font_medium = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 24)
    if not font_medium:
        font_medium = pygame.font.SysFont(None, 28)
    font_small = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 18)
    if not font_small:
        font_small = pygame.font.SysFont(None, 22)
        
    # テキストレンダリング
    title_text = font_large.render("GAME CLEAR", True, (255, 225, 100))
    
    total_count = len(game.constellations)
    repaired_count = sum(1 for const in game.constellations if not any(star.is_broken for star in const.stars))
    
    desc_text1 = font_medium.render("月は西の地平線へと沈み、静寂が訪れました。", True, (220, 235, 255))
    stat_text1 = font_medium.render(f"最後に残った星座の数: {repaired_count} / {total_count}", True, (235, 180, 60))
    stat_text2 = font_medium.render(f"星座を修正した回数: {game.repaired_consts_session_count} 回", True, (235, 180, 60))
    stat_text3 = font_medium.render(f"バグを消した個数: {game.defeated_bugs_count} 個", True, (235, 180, 60))
    
    # ブレス効果によるEnter案内
    import time
    pulse = (math.sin(time.time() * 3.0) + 1.0) / 2.0
    alpha = int(100 + pulse * 155)
    
    guidance_text = font_small.render("[ PRESS ENTER TO RETURN TO TITLE ]", True, (255, 255, 255))
    guidance_surf = guidance_text.copy()
    guidance_surf.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    
    # パネルに配置
    panel.blit(title_text, (panel_w // 2 - title_text.get_width() // 2, 50))
    panel.blit(desc_text1, (panel_w // 2 - desc_text1.get_width() // 2, 130))
    panel.blit(stat_text1, (panel_w // 2 - stat_text1.get_width() // 2, 190))
    panel.blit(stat_text2, (panel_w // 2 - stat_text2.get_width() // 2, 240))
    panel.blit(stat_text3, (panel_w // 2 - stat_text3.get_width() // 2, 290))
    panel.blit(guidance_surf, (panel_w // 2 - guidance_surf.get_width() // 2, 380))
    
    # 画面中央に blit
    screen.blit(panel, (sw // 2 - panel_w // 2, sh // 2 - panel_h // 2))

def draw_game_over_screen(screen, game):
    """ゲームオーバー画面の描画"""
    sw = screen.get_width()
    sh = screen.get_height()
    
    # 1. 画面全体のフェードアウト半透明オーバーレイ (赤みがかったダークマスク)
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((30, 5, 5, 200)) 
    screen.blit(overlay, (0, 0))
    
    # 2. クリムゾンを基調とした中央の装飾パネル
    panel_w, panel_h = 700, 400
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((25, 8, 8, 230))
    # 赤い外枠二重線
    pygame.draw.rect(panel, (220, 50, 50), (0, 0, panel_w, panel_h), 3)
    pygame.draw.rect(panel, (120, 30, 30), (4, 4, panel_w - 8, panel_h - 8), 1)
    
    # フォント読み込み
    font_large = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 54, bold=True)
    if not font_large:
        font_large = pygame.font.SysFont(None, 64, bold=True)
    font_medium = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 24)
    if not font_medium:
        font_medium = pygame.font.SysFont(None, 28)
    font_small = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 18)
    if not font_small:
        font_small = pygame.font.SysFont(None, 22)
        
    # テキストレンダリング
    title_text = font_large.render("GAME OVER", True, (255, 80, 80))
    
    total_count = len(game.constellations)
    repaired_count = sum(1 for const in game.constellations if not any(star.is_broken for star in const.stars))
    
    desc_text1 = font_medium.render("星座の多くが崩れ去り、夜空が混沌に包まれました。", True, (255, 200, 200))
    desc_text2 = font_medium.render(f"修復できた星座: {repaired_count} / {total_count}", True, (220, 50, 50))
    
    # ブレス効果によるEnter案内
    import time
    pulse = (math.sin(time.time() * 3.0) + 1.0) / 2.0
    alpha = int(100 + pulse * 155)
    
    guidance_text = font_small.render("[ PRESS ENTER TO RETURN TO TITLE ]", True, (255, 255, 255))
    guidance_surf = guidance_text.copy()
    guidance_surf.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    
    # パネルに配置
    panel.blit(title_text, (panel_w // 2 - title_text.get_width() // 2, 60))
    panel.blit(desc_text1, (panel_w // 2 - desc_text1.get_width() // 2, 160))
    panel.blit(desc_text2, (panel_w // 2 - desc_text2.get_width() // 2, 220))
    panel.blit(guidance_surf, (panel_w // 2 - guidance_surf.get_width() // 2, 310))
    
    # 画面中央に blit
    screen.blit(panel, (sw // 2 - panel_w // 2, sh // 2 - panel_h // 2))

def draw_moon_icon(screen, cx, cy, r, phase, is_selected):
    """月の満ち欠けアイコンを描画する (phase: 0.0=新月, 0.5=上弦, -0.5=下弦, 1.0=満月, 0.75=十三夜, -0.75=凸月)"""
    # 選択されている場合のグロー効果
    if is_selected:
        glow_surf = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        # 選択時の強い光輪
        for i in range(15, 0, -1):
            alpha = int(12 * (1.2 ** -i))
            pygame.draw.circle(glow_surf, (255, 235, 150, alpha), (r * 2, r * 2), r + i * 2)
        screen.blit(glow_surf, (cx - r * 2, cy - r * 2))

    # 月の基本円 (黄色/クリーム色)
    moon_color = (255, 253, 220)

    # 新月 (phase = 0.0) の場合は、地球照のように極めて薄い青グレーで輪郭を描く
    if phase == 0.0:
        pygame.draw.circle(screen, (40, 50, 70), (cx, cy), r)
        pygame.draw.circle(screen, (10, 15, 25), (cx, cy), r - 2)
    elif phase == 1.0:
        # 満月
        pygame.draw.circle(screen, moon_color, (cx, cy), r)
        # クレーターのうっすらとしたディテール
        pygame.draw.circle(screen, (245, 235, 195), (cx - r//4, cy - r//6), r//4)
        pygame.draw.circle(screen, (245, 235, 195), (cx + r//3, cy + r//4), r//6)
    elif phase == 0.5:
        # 上弦の月 (右半分が光る)
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, moon_color, (r, r), r)
        # 左半分を透過（または削る）
        surf.fill((0, 0, 0, 0), (0, 0, r, r * 2), special_flags=pygame.BLEND_RGBA_MIN)
        # クレーター
        pygame.draw.circle(surf, (245, 235, 195), (r + r//3, r + r//4), r//6)
        screen.blit(surf, (cx - r, cy - r))
        # 左側の影（地球照の輪郭をうっすらと）
        pygame.draw.arc(screen, (40, 50, 70), (cx - r, cy - r, r * 2, r * 2), math.pi/2, 3*math.pi/2, 1)
    elif phase == -0.5:
        # 下弦の月 (左半分が光る)
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, moon_color, (r, r), r)
        # 右半分を透過（または削る）
        surf.fill((0, 0, 0, 0), (r, 0, r, r * 2), special_flags=pygame.BLEND_RGBA_MIN)
        # クレーター
        pygame.draw.circle(surf, (245, 235, 195), (r - r//3, r + r//4), r//6)
        screen.blit(surf, (cx - r, cy - r))
        # 右側の影（地球照の輪郭をうっすらと）
        pygame.draw.arc(screen, (40, 50, 70), (cx - r, cy - r, r * 2, r * 2), -math.pi/2, math.pi/2, 1)
    elif phase == 0.75:
        # 十三夜月 (右側が大きく光り、左端が少し欠ける)
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, moon_color, (r, r), r)
        # 左側から少しだけ削る
        mask = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        mask.fill((255, 255, 255, 255))
        pygame.draw.circle(mask, (0, 0, 0, 0), (r - int(r * 1.25), r), r)
        surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # クレーター
        pygame.draw.circle(surf, (245, 235, 195), (r + r//6, r - r//6), r//5)
        screen.blit(surf, (cx - r, cy - r))
        # 影の輪郭 (うっすらと)
        pygame.draw.arc(screen, (40, 50, 70), (cx - r, cy - r, r * 2, r * 2), math.pi/2, 3*math.pi/2, 1)
    elif phase == -0.75:
        # 十三夜月の下弦 / 凸月 (左側が大きく光り、右端が少し欠ける)
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, moon_color, (r, r), r)
        # 右側から少しだけ削る
        mask = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        mask.fill((255, 255, 255, 255))
        pygame.draw.circle(mask, (0, 0, 0, 0), (r + int(r * 1.25), r), r)
        surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # クレーター
        pygame.draw.circle(surf, (245, 235, 195), (r - r//6, r - r//6), r//5)
        screen.blit(surf, (cx - r, cy - r))
        # 影の輪郭
        pygame.draw.arc(screen, (40, 50, 70), (cx - r, cy - r, r * 2, r * 2), -math.pi/2, math.pi/2, 1)

    # 選択されている場合の追加枠線
    if is_selected:
        pygame.draw.circle(screen, (255, 220, 100), (cx, cy), r + 2, 2)

def draw_difficulty_screen(screen, elapsed_time, selected_idx, show_ability_list=False):
    """難易度選択画面の描画"""
    sw = screen.get_width()
    sh = screen.get_height()
    
    # 1. タイトル用フォントとテキスト用フォントの読み込み
    font_large = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 48, bold=True)
    if not font_large:
        font_large = pygame.font.SysFont(None, 54, bold=True)
    font_medium = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 28, bold=True)
    if not font_medium:
        font_medium = pygame.font.SysFont(None, 32, bold=True)
    font_desc = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 20)
    if not font_desc:
        font_desc = pygame.font.SysFont(None, 24)
    font_small = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 18)
    if not font_small:
        font_small = pygame.font.SysFont(None, 22)

    # 2. タイトルの描画
    title_text = font_large.render("SELECT DIFFICULTY", True, (255, 255, 255))
    screen.blit(title_text, (sw // 2 - title_text.get_width() // 2, 80))

    # 3. 円環状の軌道を描く
    cx, cy = sw // 2, sh // 2 - 20
    orbit_r = 180
    pygame.draw.circle(screen, (30, 45, 75), (cx, cy), orbit_r, 1)

    # 難易度（月の状態）の定義
    difficulties = [
        {"name": "新月 - EXPERT", "phase": 0.0, "angle": 270, "desc": "漆黒の闇夜。バグが最凶化し、極めて過酷な修復作業となります。"},
        {"name": "上弦の月 - HARD", "phase": 0.5, "angle": 330, "desc": "満ちゆく半月。バグが活性化し、星の崩壊速度が速くなります。"},
        {"name": "十三夜月 - NORMAL", "phase": 0.75, "angle": 30, "desc": "満月手前の月。標準的なバグの出現頻度とゲームバランス。"},
        {"name": "満月 - EASY", "phase": 1.0, "angle": 90, "desc": "満ちる月光。バグの出現が控えめで、初心者向けの難易度。"},
        {"name": "凸月 - NORMAL", "phase": -0.75, "angle": 150, "desc": "欠け始めの月。標準的なバグの出現頻度とゲームバランス。"},
        {"name": "下弦の月 - HARD", "phase": -0.5, "angle": 210, "desc": "欠けゆく半月。バグが活性化し、星の崩壊速度が速くなります。"}
    ]

    # 4. 円環上に各月を描画
    for idx, diff in enumerate(difficulties):
        rad = math.radians(diff["angle"])
        mx = cx + int(orbit_r * math.cos(rad))
        my = cy + int(orbit_r * math.sin(rad))
        
        is_selected = (idx == selected_idx)
        r_size = 40 if is_selected else 30
        
        draw_moon_icon(screen, mx, my, r_size, diff["phase"], is_selected)
        
        # 難易度名のラベルを各月の外側に配置
        label_color = (255, 235, 150) if is_selected else (140, 160, 190)
        offset_dist = 65 if is_selected else 55
        lx = cx + int((orbit_r + offset_dist) * math.cos(rad))
        ly = cy + int((orbit_r + offset_dist) * math.sin(rad))
        
        label_text = font_small.render(diff["name"].split(" - ")[0], True, label_color)
        screen.blit(label_text, (lx - label_text.get_width() // 2, ly - label_text.get_height() // 2))

    # 5. 中央に選択中の難易度の詳細説明を描画
    selected_diff = difficulties[selected_idx]
    
    # 難易度タイトル
    diff_title = font_medium.render(selected_diff["name"], True, (255, 225, 100))
    screen.blit(diff_title, (sw // 2 - diff_title.get_width() // 2, cy - 35))
    
    # 難易度説明
    desc_str = selected_diff["desc"]
    desc_text = font_desc.render(desc_str, True, (200, 220, 255))
    screen.blit(desc_text, (sw // 2 - desc_text.get_width() // 2, cy + 15))

    # 6. 操作ガイド
    pulse = (math.sin(elapsed_time * 3.0) + 1.0) / 2.0
    alpha = int(100 + pulse * 155)
    
    guide_text = font_small.render("[ LEFT / RIGHT: SELECT  |  ENTER: DECIDE ]", True, (255, 255, 255))
    guide_surf = guide_text.copy()
    guide_surf.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(guide_surf, (sw // 2 - guide_surf.get_width() // 2, sh - 100))

    # 7. 「星座能力一覧」ボタンの描画 (右上)
    btn_x = sw - 190
    btn_y = 30
    btn_w = 160
    btn_h = 36
    
    # ボタンの背景と枠線を描く
    btn_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
    btn_surf.fill((10, 25, 50, 200)) # 半透明ダークブルー
    pygame.draw.rect(btn_surf, (215, 170, 70), (0, 0, btn_w, btn_h), 1) # ゴールド枠
    pygame.draw.rect(btn_surf, (100, 80, 30), (2, 2, btn_w - 4, btn_h - 4), 1)
    
    # テキストを描画
    font_btn = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 14, bold=True)
    if not font_btn:
        font_btn = pygame.font.SysFont(None, 15, bold=True)
    btn_text = font_btn.render("星座の能力一覧 [H]", True, (235, 195, 100))
    btn_surf.blit(btn_text, (btn_w // 2 - btn_text.get_width() // 2, btn_h // 2 - btn_text.get_height() // 2))
    screen.blit(btn_surf, (btn_x, btn_y))

    # 8. 「星座アビリティ一覧」ポップアップパネルの描画
    if show_ability_list:
        panel_w = 780
        panel_h = 510
        px = sw // 2 - panel_w // 2
        py = sh // 2 - panel_h // 2
        
        # 半透明の背景パネル
        overlay = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        overlay.fill((8, 16, 32, 245))
        pygame.draw.rect(overlay, (215, 170, 70), (0, 0, panel_w, panel_h), 2)
        pygame.draw.rect(overlay, (100, 80, 30), (3, 3, panel_w - 6, panel_h - 6), 1)
        
        # タイトル描画
        title_font = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 24, bold=True)
        if not title_font:
            title_font = pygame.font.SysFont(None, 26, bold=True)
        title_surf = title_font.render("星座のアビリティ（特殊能力）一覧", True, (255, 220, 100))
        overlay.blit(title_surf, (panel_w // 2 - title_surf.get_width() // 2, 20))
        
        # 13個の星座アビリティの一覧データ
        abilities = [
            ("吟遊詩人座", "安らぎの旋律", "バグの移動速度を25秒間40%低下させます。"),
            ("狐座", "疾出のステップ", "カメラの移動速度が25秒間1.6倍になります。"),
            ("鍵座", "知理の瞳", "25秒間、画面外のバグの方向と距離を警告表示します。"),
            ("珈琲座", "アロマの癒やし", "ランダムに13個の崩れた星を瞬時に修復します。"),
            ("糸紡ぎ座", "守護の結", "25秒間、すべての星をバグの破壊から完全保護します。"),
            ("灯台守座", "導きの光", "現在の視野内にいるすべてのバグを一掃します。"),
            ("万年筆座", "天空の一筆", "ランダムに壊れている星座1つを完全修復します。"),
            ("双子火山座", "スターバースト", "現在出現しているすべてのバグを一掃します。"),
            ("こだま座", "音響ノックバック", "すべてのバグを地平線まで強制的に押し戻します。"),
            ("折れた剣座", "衝撃の刃", "25秒間、バグ撃破時に周囲のバグも巻き込んで殲滅します。"),
            ("蝶座", "導きの羽ばたき", "25秒間、漂流している星を自動で元の位置に引き寄せます。"),
            ("鯨座", "宿まり of 重力", "出現しているすべてのブラックホールを通常バグに戻します。"),
            ("ドラゴン座", "天壁 of 盾", "星の破壊を最大3回まで完全に防ぐバリアを展開します。")
        ]
        
        # フォント定義
        const_font = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 15, bold=True)
        if not const_font:
            const_font = pygame.font.SysFont(None, 16, bold=True)
        desc_font = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 13)
        if not desc_font:
            desc_font = pygame.font.SysFont(None, 14)
            
        # 左右の列に分けて描画 (左に7つ、右に6つ)
        for i, (name, skill, desc) in enumerate(abilities):
            # 列判定と座標計算
            is_right_col = (i >= 7)
            col_x = 410 if is_right_col else 30
            row_idx = (i - 7) if is_right_col else i
            item_y = 75 + row_idx * 55
            
            # 星座名とアビリティ名
            display_skill = skill
            if "of" in display_skill:
                display_skill = display_skill.replace("of", "の")
            header_text = f"{name} : {display_skill}"
            header_surf = const_font.render(header_text, True, (235, 195, 100))
            overlay.blit(header_surf, (col_x, item_y))
            
            # 効果説明
            desc_surf = desc_font.render(desc, True, (190, 210, 235))
            overlay.blit(desc_surf, (col_x + 16, item_y + 22))
            
        # 下部操作ガイド
        close_font = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 14)
        if not close_font:
            close_font = pygame.font.SysFont(None, 15)
        close_text = close_font.render("[ 画面をクリックするか、ESC または H キーで閉じる ]", True, (150, 170, 200))
        overlay.blit(close_text, (panel_w // 2 - close_text.get_width() // 2, panel_h - 30))
        
        screen.blit(overlay, (px, py))
