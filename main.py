import pygame
import sys
import os
import math
from src.core.dome_coord import DomeCoord
from src.ui.renderer import SCREEN_W, SCREEN_H, draw_background, draw_constellations, draw_title_screen, draw_clear_screen, draw_game_over_screen, draw_difficulty_screen
from src.core.game import Game

FPS = 60
FOV_DEG = 90.0

def main():
    pygame.init()

    # オーディオ初期化と再生
    pygame.mixer.init()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_file = os.path.join(base_dir, "source", "Beneath_the_Midnight_Flow.mp3")
    
    if os.path.exists(audio_file):
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    else:
        print(f"Warning: Audio file not found at {audio_file}")

    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Stella Repairer - ドーム視点テスト")
    clock = pygame.time.Clock()

    coord = DomeCoord(SCREEN_W, SCREEN_H, FOV_DEG)
    
    # ゲームマネージャクラスの初期化
    game = Game(coord, base_dir, "FULL_MOON")

    state = "TITLE"  # "TITLE", "DIFFICULTY", "GAME", "CLEAR", "GAME_OVER"
    selected_difficulty_idx = 3
    show_ability_list = False  # デフォルト: 満月 (EASY)
    elapsed_time = 0.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        elapsed_time += dt

        # イベントハンドリング
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if state == "TITLE":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        state = "DIFFICULTY"
                elif state == "DIFFICULTY":
                    if show_ability_list:
                        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE, pygame.K_h):
                            show_ability_list = False
                    else:
                        if event.key == pygame.K_h:
                            show_ability_list = True
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            selected_difficulty_idx = (selected_difficulty_idx - 1) % 6
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            selected_difficulty_idx = (selected_difficulty_idx + 1) % 6
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            diff_names = ["NEW_MOON", "FIRST_QUARTER", "WAXING_GIBBOUS", "FULL_MOON", "WANING_GIBBOUS", "LAST_QUARTER"]
                            game = Game(coord, base_dir, diff_names[selected_difficulty_idx])
                            state = "GAME"
                            pygame.mouse.set_visible(False)
                elif state == "GAME":
                    if event.key == pygame.K_e:
                        game.toggle_energy_ready()
                    elif event.key == pygame.K_c:
                        # マウス視点移動モードのトグル
                        game.mouse_look_mode = not game.mouse_look_mode
                        # マウスは常に非表示（レティクルがポインターの役割を果たすため）
                        pygame.mouse.set_visible(False)
                        # マウスをウィンドウ内に閉じ込める (マウスモード時のみ)
                        pygame.event.set_grab(game.mouse_look_mode)
                        if game.mouse_look_mode:
                            # 最初の移動差分をクリアするために get_rel を1回読み捨てる
                            pygame.mouse.get_rel()
                            # 画面中央にマウスをワープさせる
                            pygame.mouse.set_pos(SCREEN_W // 2, SCREEN_H // 2)
                            game.ability_activation_message = "操作モード: マウス視点移動"
                        else:
                            game.ability_activation_message = "操作モード: WASDキー視点移動"
                        game.ability_message_timer = 2.0
                elif state == "CLEAR":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        # ゲームリセットしてタイトル画面へ戻す
                        game = Game(coord, base_dir, "FULL_MOON")
                        state = "TITLE"
                elif state == "GAME_OVER":
                    if event.key == pygame.K_RETURN:
                        # ゲームリセットしてタイトル画面へ戻す
                        game = Game(coord, base_dir, "FULL_MOON")
                        state = "TITLE"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if state == "TITLE":
                    state = "DIFFICULTY"
                elif state == "DIFFICULTY":
                    if show_ability_list:
                        show_ability_list = False
                    else:
                        # 右上のボタン領域のクリック判定
                        btn_x = SCREEN_W - 190
                        btn_y = 30
                        btn_w = 160
                        btn_h = 36
                        mx, my = event.pos
                        if btn_x <= mx <= btn_x + btn_w and btn_y <= my <= btn_y + btn_h:
                            show_ability_list = True
                        else:
                            # マウスクリックでの選択と決定
                            cx, cy = SCREEN_W // 2, SCREEN_H // 2 - 20
                            orbit_r = 180
                            diff_angles = [270, 330, 30, 90, 150, 210]  # 新月, 三日月, 上弦, 満月, 下弦, 二十六夜月
                            for idx, angle in enumerate(diff_angles):
                                rad = math.radians(angle)
                                mx_moon = cx + int(orbit_r * math.cos(rad))
                                my_moon = cy + int(orbit_r * math.sin(rad))
                                dist = math.sqrt((event.pos[0] - mx_moon)**2 + (event.pos[1] - my_moon)**2)
                                if dist < 45:
                                    selected_difficulty_idx = idx
                                    diff_names = ["NEW_MOON", "FIRST_QUARTER", "WAXING_GIBBOUS", "FULL_MOON", "WANING_GIBBOUS", "LAST_QUARTER"]
                                    game = Game(coord, base_dir, diff_names[selected_difficulty_idx])
                                    state = "GAME"
                                    break
                elif state == "GAME":
                    if event.button == 1:  # 左クリック
                        game.handle_click(event.pos)

        if state == "TITLE":
            # ── タイトル画面の更新と描画 ──
            # 背景をゆっくりと自動回転させ、動的な演出にします
            coord.cam_theta = (coord.cam_theta + 3.0 * dt) % 360.0
            
            # 星空と星座を背景として描画
            draw_background(screen, coord)
            draw_constellations(screen, coord, game.constellations, game.constellation_placements)
            
            # タイトルUIの描画
            draw_title_screen(screen, elapsed_time)

        elif state == "DIFFICULTY":
            # ── 難易度選択画面の更新と描画 ──
            coord.cam_theta = (coord.cam_theta + 3.0 * dt) % 360.0
            draw_background(screen, coord)
            draw_difficulty_screen(screen, elapsed_time, selected_difficulty_idx, show_ability_list)

        elif state == "GAME":
            # ── ゲーム操作の更新と描画 ──
            keys = pygame.key.get_pressed()
            game.update(dt, keys)
            game.draw(screen)
            
            if game.game_over:
                state = "GAME_OVER"
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)
            elif game.game_cleared:
                state = "CLEAR"
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)

        elif state == "CLEAR":
            # ── ゲームクリア画面の更新と描画 ──
            # 背景をゆっくり自動回転させつつ描画
            coord.cam_theta = (coord.cam_theta + 3.0 * dt) % 360.0
            draw_background(screen, coord)
            draw_constellations(screen, coord, game.constellations, game.constellation_placements)
            
            draw_clear_screen(screen, game)

        elif state == "GAME_OVER":
            # ── ゲームオーバー画面の更新と描画 ──
            # 背景をゆっくり自動回転させつつ描画
            coord.cam_theta = (coord.cam_theta + 3.0 * dt) % 360.0
            draw_background(screen, coord)
            draw_constellations(screen, coord, game.constellations, game.constellation_placements)
            
            draw_game_over_screen(screen, game)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
