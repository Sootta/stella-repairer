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

def draw_background(screen, coord, ready_state=False, difficulty="FULL_MOON", view_mode=False):
    if ready_state:
        screen.fill((1, 2, 4)) # 夜空の背景色を極めて暗く
    elif difficulty == "NEW_MOON" and not view_mode:
        screen.fill((2, 3, 6)) # 新月（EXPERT）用の極限の闇夜
    elif view_mode:
        screen.fill((20, 30, 50)) # 鑑賞モード用の少し明るい綺麗な紺色
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
    elif view_mode:
        star_color = (255, 225, 100) # 鑑賞モード用のゴールドの星
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

def draw_multiline_text(screen, text, font, color, rect, line_spacing=5):
    """指定された矩形領域内にテキストを自動折り返しして描画する"""
    lines = text.split('\n')
    rendered_lines = []
    
    for line in lines:
        if not line:
            rendered_lines.append("")
            continue
        
        current_line = ""
        for char in line:
            test_line = current_line + char
            width, _ = font.size(test_line)
            if width > rect.width:
                rendered_lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        if current_line:
            rendered_lines.append(current_line)
            
    y = rect.y
    for line in rendered_lines:
        if line:
            text_surf = font.render(line, True, color)
            screen.blit(text_surf, (rect.x, y))
        y += font.get_height() + line_spacing

def draw_letter_notice(screen, elapsed_time):
    screen.fill((10, 10, 15))
    font = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 36)
    if not font:
        font = pygame.font.SysFont(None, 40)
    
    text = "あなたに一通の手紙が届きました"
    alpha = int(abs(math.sin(elapsed_time * 2.0)) * 255)
    surf = font.render(text, True, (255, 255, 255))
    surf.set_alpha(alpha)
    screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, SCREEN_H // 2 - surf.get_height() // 2))

    font_sub = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 20)
    if not font_sub:
        font_sub = pygame.font.SysFont(None, 24)
    click_surf = font_sub.render("[ CLICK TO OPEN ]", True, (150, 150, 150))
    screen.blit(click_surf, (SCREEN_W // 2 - click_surf.get_width() // 2, SCREEN_H // 2 + 60))

def draw_letter_image(screen, letter_image, elapsed_time, show_text=False, letter_text=""):
    img_w, img_h = letter_image.get_size()
    scale = min(SCREEN_W / img_w, SCREEN_H / img_h)
    new_w, new_h = int(img_w * scale), int(img_h * scale)
    scaled_img = pygame.transform.smoothscale(letter_image, (new_w, new_h))
    
    x = (SCREEN_W - new_w) // 2
    y = (SCREEN_H - new_h) // 2
    screen.fill((0, 0, 0))
    screen.blit(scaled_img, (x, y))
    
    if show_text:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 24)
        if not font:
            font = pygame.font.SysFont(None, 28)
            
        rect = pygame.Rect(SCREEN_W * 0.15, SCREEN_H * 0.15, SCREEN_W * 0.7, SCREEN_H * 0.7)
        draw_multiline_text(screen, letter_text, font, (240, 240, 240), rect, line_spacing=12)
        
        font_sub = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 20)
        if not font_sub:
            font_sub = pygame.font.SysFont(None, 24)
        click_surf = font_sub.render("[ CLICK TO CONTINUE ]", True, (200, 200, 200))
        alpha = int(abs(math.sin(elapsed_time * 2.0)) * 255)
        click_surf.set_alpha(alpha)
        screen.blit(click_surf, (SCREEN_W // 2 - click_surf.get_width() // 2, SCREEN_H - 80))

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
        
    # ズーム倍率 (サイズを2倍にするため * 2.0)
    zoom_ratio = (90.0 / coord.current_fov) * 2.0
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

def draw_comet(screen, cx, cy, angle, elapsed_time, is_faint=False):
    """彗星と尾の描画"""
    import random
    
    alpha_mult = 0.15 if is_faint else 1.0
    
    r = 10
    core_color = (200, 240, 255, int(255 * alpha_mult))
    if is_faint:
        surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, core_color, (r, r), r)
        screen.blit(surf, (int(cx) - r, int(cy) - r))
    else:
        pygame.draw.circle(screen, (core_color[0], core_color[1], core_color[2]), (int(cx), int(cy)), r)
    
    glow_surf = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (150, 220, 255, int(60 * alpha_mult)), (r * 3, r * 3), r * 3)
    pygame.draw.circle(glow_surf, (200, 240, 255, int(120 * alpha_mult)), (r * 3, r * 3), r * 2)
    screen.blit(glow_surf, (int(cx) - r * 3, int(cy) - r * 3))
    
    tail_length = 150
    tail_base_angle = angle + math.pi
    
    for i in range(20):
        offset_ang = tail_base_angle + random.uniform(-0.15, 0.15)
        length = random.uniform(20, tail_length)
        tx = cx + length * math.cos(offset_ang)
        ty = cy + length * math.sin(offset_ang)
        
        alpha = int(255 * (1.0 - length / tail_length) * alpha_mult)
        pygame.draw.line(screen, (150, 220, 255, alpha), (cx, cy), (tx, ty), max(1, int(4 * (1.0 - length / tail_length))))
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
    total_count = len(game.constellations)
    repaired_count = sum(1 for const in game.constellations if not any(star.is_broken for star in const.stars))
    
    if getattr(game, "true_clear", False):
        title_text = font_large.render("TRUE CLEAR", True, (255, 255, 255))
        desc_text1 = font_medium.render("彗星がトリガーとなり、夜空のバグが生まれない星空へと再構成されました", True, (220, 235, 255))
        guidance_text = font_small.render("[ PRESS ENTER TO RETURN TO TITLE ]", True, (255, 255, 255))
        
        # 星空を見るボタン
        btn_rect = pygame.Rect(panel_w // 2 - 100, 250, 200, 40)
        btn_color = (60, 100, 150)
        mx, my = pygame.mouse.get_pos()
        btn_rect_global = pygame.Rect(sw // 2 - panel_w // 2 + btn_rect.x, sh // 2 - panel_h // 2 + btn_rect.y, btn_rect.width, btn_rect.height)
        if btn_rect_global.collidepoint(mx, my):
            btn_color = (80, 130, 190)
        pygame.draw.rect(panel, btn_color, btn_rect, border_radius=5)
        pygame.draw.rect(panel, (200, 220, 255), btn_rect, 2, border_radius=5)
        btn_text = font_medium.render("星空を見る", True, (255, 255, 255))
        panel.blit(btn_text, (btn_rect.x + btn_rect.width // 2 - btn_text.get_width() // 2, btn_rect.y + btn_rect.height // 2 - btn_text.get_height() // 2))
    else:
        title_text = font_large.render("STAGE CLEAR", True, (255, 225, 100))
        desc_text1 = font_medium.render("月は西の地平線へと沈み、静寂が訪れました。", True, (220, 235, 255))
        guidance_text = font_small.render("[ PRESS ENTER TO CONTINUE TO NEXT STAGE ]", True, (255, 255, 255))
        
    stat_text1 = font_medium.render(f"最後に残った星座の数: {repaired_count} / {total_count}", True, (235, 180, 60))
    stat_text2 = font_medium.render(f"星座を修正した回数: {game.repaired_consts_session_count} 回", True, (235, 180, 60))
    stat_text3 = font_medium.render(f"バグを消した個数: {game.defeated_bugs_count} 個", True, (235, 180, 60))
        
    # ブレス効果によるEnter案内
    import time
    pulse = (math.sin(time.time() * 3.0) + 1.0) / 2.0
    alpha = int(100 + pulse * 155)
    guidance_surf = guidance_text.copy()
    guidance_surf.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    
    # パネルに配置
    panel.blit(title_text, (panel_w // 2 - title_text.get_width() // 2, 50))
    panel.blit(desc_text1, (panel_w // 2 - desc_text1.get_width() // 2, 130))
    if not getattr(game, "true_clear", False):
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

def draw_stage_intro_screen(screen, elapsed_time, difficulty_name, phase):
    """ステージ開始前の月齢表示画面を描画"""
    sw = screen.get_width()
    sh = screen.get_height()
    
    font_large = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 64, bold=True)
    if not font_large:
        font_large = pygame.font.SysFont(None, 70, bold=True)
    font_small = pygame.font.SysFont("notosanscjkjp,applecsgothic,hiraginosansgb,msgothic", 24)
    if not font_small:
        font_small = pygame.font.SysFont(None, 28)

    cx, cy = sw // 2, sh // 2 - 40
    
    # 大きな月を描画
    draw_moon_icon(screen, cx, cy, 150, phase, False)
    
    # 月齢の名前を描画
    title_text = font_large.render(difficulty_name, True, (255, 235, 150))
    screen.blit(title_text, (cx - title_text.get_width() // 2, cy + 180))

    # 操作ガイド（点滅）
    pulse = (math.sin(elapsed_time * 3.0) + 1.0) / 2.0
    alpha = int(100 + pulse * 155)
    
    guide_text = font_small.render("[ CLICK OR PRESS ENTER TO START ]", True, (255, 255, 255))
    guide_surf = guide_text.copy()
    guide_surf.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(guide_surf, (cx - guide_surf.get_width() // 2, sh - 80))
