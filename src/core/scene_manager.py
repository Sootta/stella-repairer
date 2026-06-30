import pygame

class SceneManager:
    def __init__(self, base_dir, screen, clock):
        self.base_dir = base_dir
        self.screen = screen
        self.clock = clock
        self.current_scene = None
        self.shared_data = {}  # 画面間で共有するデータ (coord, stage_idx等)

    def switch_scene(self, scene_class, **kwargs):
        self.current_scene = scene_class(self, **kwargs)

    def handle_events(self, events):
        if self.current_scene:
            self.current_scene.handle_events(events)

    def update(self, dt):
        if self.current_scene:
            self.current_scene.update(dt)

    def draw(self, screen):
        if self.current_scene:
            self.current_scene.draw(screen)

class BaseScene:
    def __init__(self, scene_manager: SceneManager):
        self.manager = scene_manager

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass
