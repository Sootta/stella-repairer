import pygame
from src.core.scene_manager import BaseScene
from src.ui.renderer import SCREEN_W, SCREEN_H, draw_background, draw_constellations, draw_title_screen, draw_clear_screen, draw_game_over_screen, draw_stage_intro_screen, draw_letter_notice, draw_letter_image
from src.core.game import Game

def play_bgm(manager, track_name):
    import os
    audio_file = os.path.join(manager.base_dir, "source", track_name)
    if os.path.exists(audio_file):
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    else:
        print(f"Warning: Audio file not found at {audio_file}")

class TitleScene(BaseScene):
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    play_bgm(self.manager, "Coffee_on_the_Balcony.mp3")
                    self.manager.switch_scene(LetterNoticeScene)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                play_bgm(self.manager, "Coffee_on_the_Balcony.mp3")
                self.manager.switch_scene(LetterNoticeScene)

    def update(self, dt):
        self.manager.coord.cam_theta = (self.manager.coord.cam_theta + 3.0 * dt) % 360.0

    def draw(self, screen):
        draw_background(screen, self.manager.coord)
        draw_constellations(screen, self.manager.coord, self.manager.game.constellations, self.manager.game.constellation_placements)
        draw_title_screen(screen, self.manager.elapsed_time)


class LetterNoticeScene(BaseScene):
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.manager.switch_scene(LetterImageScene)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.manager.switch_scene(LetterImageScene)

    def update(self, dt):
        pass

    def draw(self, screen):
        draw_letter_notice(screen, self.manager.elapsed_time)


class LetterImageScene(BaseScene):
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.manager.switch_scene(LetterTextScene)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.manager.switch_scene(LetterTextScene)

    def update(self, dt):
        pass

    def draw(self, screen):
        draw_letter_image(screen, self.manager.shared_data["letter_image"], self.manager.elapsed_time, show_text=False)


class LetterTextScene(BaseScene):
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    play_bgm(self.manager, "Above_the_Midnight_Meridian.mp3")
                    self.manager.switch_scene(StageIntroScene)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                play_bgm(self.manager, "Above_the_Midnight_Meridian.mp3")
                self.manager.switch_scene(StageIntroScene)

    def update(self, dt):
        pass

    def draw(self, screen):
        draw_letter_image(screen, self.manager.shared_data["letter_image"], self.manager.elapsed_time, show_text=True, letter_text=self.manager.shared_data["letter_text"])


class StageIntroScene(BaseScene):
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.start_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.start_game()
                
    def start_game(self):
        stage_cycle = self.manager.shared_data["STAGE_CYCLE"]
        idx = self.manager.shared_data["current_stage_idx"]
        cycle_count = self.manager.shared_data.get("cycle_count", 0)
        self.manager.game = Game(self.manager.coord, self.manager.base_dir, stage_cycle[idx], cycle_count)
        pygame.mouse.set_visible(False)
        self.manager.switch_scene(GameScene)

    def update(self, dt):
        self.manager.coord.cam_theta = (self.manager.coord.cam_theta + 3.0 * dt) % 360.0

    def draw(self, screen):
        draw_background(screen, self.manager.coord)
        idx = self.manager.shared_data["current_stage_idx"]
        stage_cycle = self.manager.shared_data["STAGE_CYCLE"]
        cycle_count = self.manager.shared_data.get("cycle_count", 0)
        
        diff_name = self.manager.shared_data["STAGE_NAMES"][stage_cycle[idx]]
        phase = self.manager.shared_data["STAGE_PHASES"][stage_cycle[idx]]
        
        is_lunar_eclipse = (stage_cycle[idx] == "FULL_MOON" and cycle_count == 1)
        if is_lunar_eclipse:
            diff_name = "レッドムーン"
            
        draw_stage_intro_screen(screen, self.manager.elapsed_time, diff_name, phase, is_lunar_eclipse=is_lunar_eclipse)


class GameScene(BaseScene):
    def handle_events(self, events):
        game = self.manager.game
        for event in events:
            if event.type == pygame.KEYDOWN:
                if getattr(game, "true_clear_view_mode", False) and event.key == pygame.K_q:
                    self.manager.shared_data["current_stage_idx"] = 0
                    self.manager.shared_data["cycle_count"] = 0
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                    play_bgm(self.manager, "Beneath_the_Midnight_Flow.mp3")
                    self.manager.switch_scene(TitleScene)
                elif event.key == pygame.K_e:
                    game.toggle_energy_ready()
                elif event.key == pygame.K_c:
                    game.mouse_look_mode = not game.mouse_look_mode
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(game.mouse_look_mode)
                    if game.mouse_look_mode:
                        pygame.mouse.get_rel()
                        pygame.mouse.set_pos(SCREEN_W // 2, SCREEN_H // 2)
                        game.ability_activation_message = "操作モード: マウス視点移動"
                    else:
                        game.ability_activation_message = "操作モード: WASDキー視点移動"
                    game.ability_message_timer = 2.0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.manager.game.update(dt, keys)
        
        if self.manager.game.game_over:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
            self.manager.switch_scene(GameOverScene)
        elif self.manager.game.game_cleared:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
            self.manager.switch_scene(ClearScene)

    def draw(self, screen):
        self.manager.game.draw(screen)


class ClearScene(BaseScene):
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if getattr(self.manager.game, "true_clear", False):
                        self.manager.shared_data["current_stage_idx"] = 0
                        self.manager.shared_data["cycle_count"] = 0
                        play_bgm(self.manager, "Beneath_the_Midnight_Flow.mp3")
                        self.manager.switch_scene(TitleScene)
                    else:
                        stages = len(self.manager.shared_data["STAGE_CYCLE"])
                        next_idx = (self.manager.shared_data["current_stage_idx"] + 1) % stages
                        if next_idx == 0:
                            self.manager.shared_data["cycle_count"] = self.manager.shared_data.get("cycle_count", 0) + 1
                        self.manager.shared_data["current_stage_idx"] = next_idx
                        self.manager.switch_scene(StageIntroScene)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if getattr(self.manager.game, "true_clear", False):
                    sw, sh = SCREEN_W, SCREEN_H
                    panel_w, panel_h = 700, 450
                    btn_rect = pygame.Rect(sw // 2 - panel_w // 2 + panel_w // 2 - 100, sh // 2 - panel_h // 2 + 310, 200, 40)
                    if btn_rect.collidepoint(event.pos):
                        self.manager.game.enter_view_mode()
                        self.manager.game.game_cleared = False
                        pygame.mouse.set_visible(False)
                        self.manager.switch_scene(GameScene)

    def update(self, dt):
        self.manager.coord.cam_theta = (self.manager.coord.cam_theta + 3.0 * dt) % 360.0

    def draw(self, screen):
        draw_background(screen, self.manager.coord)
        draw_constellations(screen, self.manager.coord, self.manager.game.constellations, self.manager.game.constellation_placements)
        draw_clear_screen(screen, self.manager.game)


class GameOverScene(BaseScene):
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.manager.shared_data["current_stage_idx"] = 0
                    self.manager.shared_data["cycle_count"] = 0
                    play_bgm(self.manager, "Beneath_the_Midnight_Flow.mp3")
                    self.manager.switch_scene(TitleScene)

    def update(self, dt):
        self.manager.coord.cam_theta = (self.manager.coord.cam_theta + 3.0 * dt) % 360.0

    def draw(self, screen):
        draw_background(screen, self.manager.coord)
        draw_constellations(screen, self.manager.coord, self.manager.game.constellations, self.manager.game.constellation_placements)
        draw_game_over_screen(screen, self.manager.game)
