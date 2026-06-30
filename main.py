import pygame
import sys
import os
import math
from src.core.dome_coord import DomeCoord
from src.ui.renderer import SCREEN_W, SCREEN_H
from src.core.game import Game
from src.core.scene_manager import SceneManager
from src.scenes.game_scenes import TitleScene

FPS = 60
FOV_DEG = 90.0

def play_bgm(base_dir, track_name):
    audio_file = os.path.join(base_dir, "source", track_name)
    if os.path.exists(audio_file):
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    else:
        print(f"Warning: Audio file not found at {audio_file}")

def main():
    pygame.init()

    # オーディオ初期化と再生
    pygame.mixer.init()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    play_bgm(base_dir, "Beneath_the_Midnight_Flow.mp3")

    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Stella Repairer - ドーム視点テスト")
    clock = pygame.time.Clock()

    coord = DomeCoord(SCREEN_W, SCREEN_H, FOV_DEG)
    
    # ゲームマネージャクラスの初期化
    game = Game(coord, base_dir, "FULL_MOON")

    letter_image_path = os.path.join(base_dir, "source", "images", "Letter.jpeg")
    if os.path.exists(letter_image_path):
        letter_image = pygame.image.load(letter_image_path).convert_alpha()
    else:
        letter_image = pygame.Surface((1, 1))

    letter_text = """親愛なるあなたへ

突然の手紙をどうか許してほしい。単刀直入に伝えよう。あなたに、この世界の「夜空の管理者」の職を託したいのだ。

遥か昔より、我々の頭上に広がる空は、歴代の管理者たちによって崩壊の危機から守られてきた。しかし先日、先代の管理者が惜しまれつつも現役を退くこととなった。そこで、類稀なる素質を持つあなたに、次代の管理者として夜の空を――すなわち、星々の崩壊を防ぐ重大な任務をお願いしたい。

依頼の報酬は、先払いとしてあらかじめ手配しておいた。また、任務に必要となる「魔道具」もすでに手元に届いているはずだ。急な話で申し訳ないが、今晩から早速、監視の目を光らせてほしい。

夜空には、この世の歪みから生まれる「バグ」と呼ばれる欠陥……空を崩壊させようと破壊活動を目論む異形の生物がしばしば発生する。どうかその魔道具を駆使して「バグ」を排除し、万が一星が傷ついてしまった場合には、速やかに修復を行ってほしい。

最後に、もし夜空で「エネルギーの玉」を見かけたら、忘れずに回収しておくといい。それは星座たちが自らの力で夜空を守り抜くための、大いなる糧となるはずだ。

美しい夜天の命運は、あなたの双肩に懸かっている。よろしく頼んだ。"""

    STAGE_CYCLE = [
        "FULL_MOON",
        "WANING_GIBBOUS",
        "LAST_QUARTER",
        "NEW_MOON",
        "FIRST_QUARTER",
        "WAXING_GIBBOUS"
    ]
    STAGE_NAMES = {
        "FULL_MOON": "満月",
        "WANING_GIBBOUS": "下弦の月",
        "LAST_QUARTER": "下弦の半月",
        "NEW_MOON": "新月",
        "FIRST_QUARTER": "上弦の半月",
        "WAXING_GIBBOUS": "上弦の月"
    }
    STAGE_PHASES = {
        "FULL_MOON": 1.0,
        "WANING_GIBBOUS": -0.75,
        "LAST_QUARTER": -0.5,
        "NEW_MOON": 0.0,
        "FIRST_QUARTER": 0.5,
        "WAXING_GIBBOUS": 0.75
    }
    current_stage_idx = 0

    scene_manager = SceneManager(base_dir, screen, clock)
    scene_manager.coord = coord
    scene_manager.game = game
    scene_manager.elapsed_time = 0.0

    scene_manager.shared_data = {
        "letter_image": letter_image,
        "letter_text": letter_text,
        "STAGE_CYCLE": STAGE_CYCLE,
        "STAGE_NAMES": STAGE_NAMES,
        "STAGE_PHASES": STAGE_PHASES,
        "current_stage_idx": current_stage_idx,
        "cycle_count": 1
    }

    scene_manager.switch_scene(TitleScene)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        scene_manager.elapsed_time += dt

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        scene_manager.handle_events(events)
        scene_manager.update(dt)
        scene_manager.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
