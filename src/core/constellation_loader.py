import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple

# --- データ構造の定義（構造体のように扱う） ---

@dataclass
class Star:
    x: float
    y: float
    magnitude: float
    orig_x: float = 0.0
    orig_y: float = 0.0
    curr_x: float = 0.0
    curr_y: float = 0.0
    is_broken: bool = False
    drift_vx: float = 0.0
    drift_vy: float = 0.0

@dataclass
class Constellation:
    id: str
    name: str
    english_name: str
    category: str
    description: str
    stars: List[Star]
    lines: List[Tuple[int, int]]
    art_paths: List[List[Tuple[float, float]]] = field(default_factory=list)
    unbroken_time: float = 0.0

# --- デコード処理を担うクラス ---

class ConstellationLoader:
    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.constellations: List[Constellation] = []

    def load(self) -> bool:
        """JSONを読み込み、内部のリストに格納する。成功すればTrueを返す"""
        if not self.file_path.exists():
            print(f"エラー: {self.file_path} が見つかりません。")
            return False

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # JSONの辞書データを、上で定義したdataclassのインスタンスに変換
            for c_data in data.get("constellations", []):
                # 星のリストをStarオブジェクトに変換し、現在の位置と元の位置を初期設定する
                stars = []
                for s in c_data.get("stars", []):
                    sx = s["x"]
                    sy = s["y"]
                    stars.append(Star(
                        x=sx, y=sy, magnitude=s["magnitude"],
                        orig_x=sx, orig_y=sy,
                        curr_x=sx, curr_y=sy
                    ))
                # 線のリストをタプルに変換
                lines = [tuple(l) for l in c_data.get("lines", [])]

                # イラスト用パスのパース
                art_paths = []
                for path_data in c_data.get("art_paths", []):
                    path = []
                    for pt in path_data:
                        if len(pt) == 2:
                            path.append((float(pt[0]), float(pt[1])))
                    if len(path) >= 2:
                        art_paths.append(path)

                constellation = Constellation(
                    id=c_data["id"],
                    name=c_data["name"],
                    english_name=c_data["english_name"],
                    category=c_data["category"],
                    description=c_data["description"],
                    stars=stars,
                    lines=lines,
                    art_paths=art_paths
                )
                self.constellations.append(constellation)
            
            return True

        except json.JSONDecodeError as e:
            print(f"JSONのパースに失敗しました: {e}")
            return False
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")
            return False

    def get_all(self) -> List[Constellation]:
        """読み込んだすべての星座データを返す"""
        return self.constellations

    def get_by_id(self, const_id: str) -> Constellation | None:
        """特定のIDを持つ星座データを検索して返す（便利機能）"""
        for c in self.constellations:
            if c.id == const_id:
                return c
        return None
