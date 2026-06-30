import math

class MoonManager:
    def __init__(self, start_p: float, end_p: float, moon_duration: float, moon_phase: float, visible: bool):
        self.moon_time = 0.0
        self.moon_duration = moon_duration
        self.start_p = start_p
        self.end_p = end_p
        self.moon_phase = moon_phase
        self.visible = visible

        self.moon_theta = 90.0 + start_p * 180.0
        self.moon_phi = 45.0 * math.sin(start_p * math.pi)
        
    def update(self, dt: float, is_view_mode: bool, broken_star_ratio: float):
        if not is_view_mode:
            moon_speed_multiplier = max(0.0, 1.0 - broken_star_ratio)
            self.moon_time += dt * moon_speed_multiplier

        progress = min(1.0, self.moon_time / self.moon_duration)
        base_progress = self.start_p + progress * (self.end_p - self.start_p)
        self.moon_theta = 90.0 + base_progress * 180.0
        self.moon_phi = 45.0 * math.sin(base_progress * math.pi)
        
        return progress

    def get_phase(self) -> float:
        return self.moon_phase
