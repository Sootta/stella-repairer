import math

class DomeCoord:
    """上半球のドーム状座標系（球面座標）からスクリーン（透視投影）への変換を管理するクラス"""
    def __init__(self, screen_w: int, screen_h: int, fov_deg: float):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.current_fov = fov_deg
        self.set_fov(fov_deg)
        
        self.cam_theta = 0.0 # 水平方向の向き (0〜360度)
        self.cam_phi = 30.0  # 仰角 (0=水平線、90=真上)

    def set_fov(self, fov_deg: float):
        self.current_fov = fov_deg
        # FOVからスクリーン上のスケール値を計算
        self.fov_scale = (self.screen_w / 2) / math.tan(math.radians(max(1.0, fov_deg) / 2))

    def to_screen_3d(self, px: float, py: float, pz: float) -> tuple[float, float, bool]:
        """3D直交座標(px, py, pz)からスクリーン座標(sx, sy)への変換。"""
        # カメラの水平回転（ヨー: Y軸回転）
        ctr = math.radians(-self.cam_theta)
        cos_t = math.cos(ctr)
        sin_t = math.sin(ctr)
        x1 = px * cos_t - pz * sin_t
        z1 = px * sin_t + pz * cos_t
        y1 = py

        # カメラの上下回転（ピッチ: X軸回転）
        cpr = math.radians(-self.cam_phi)
        cos_p = math.cos(cpr)
        sin_p = math.sin(cpr)
        
        x2 = x1
        y2 = y1 * cos_p - z1 * sin_p
        z2 = y1 * sin_p + z1 * cos_p

        # 3D透視投影 (z2 > 0 がカメラの前方)
        if z2 <= 0.01:
            return 0, 0, False
            
        sx = self.screen_w / 2 + (x2 / z2) * self.fov_scale
        sy = self.screen_h / 2 - (y2 / z2) * self.fov_scale
        
        return sx, sy, True

    def to_screen(self, theta: float, phi: float) -> tuple[float, float, bool]:
        """球面座標(theta, phi)からスクリーン座標(sx, sy)への変換。"""
        px, py, pz = self.to_cartesian(theta, phi)
        return self.to_screen_3d(px, py, pz)

    def to_cartesian(self, theta: float, phi: float) -> tuple[float, float, float]:
        """球面座標(theta, phi)から3D直交座標(px, py, pz)へ変換。"""
        tr = math.radians(theta)
        pr = math.radians(phi)
        
        px = math.cos(pr) * math.sin(tr)
        py = math.sin(pr)
        pz = math.cos(pr) * math.cos(tr)
        
        return px, py, pz

    def get_projection_basis(self, theta: float, phi: float) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
        """指定した天球上の中心座標から、接平面の直交基底ベクトル u, v と中心位置 C を返す。"""
        tc = math.radians(theta)
        pc = math.radians(phi)
        
        # 中心の3D位置ベクトル C
        cx = math.cos(pc) * math.sin(tc)
        cy = math.sin(pc)
        cz = math.cos(pc) * math.cos(tc)
        
        # 接平面の直交基底ベクトル u, v
        ux = math.cos(tc)
        uy = 0.0
        uz = -math.sin(tc)
        
        vx = -math.sin(pc) * math.sin(tc)
        vy = math.cos(pc)
        vz = -math.sin(pc) * math.cos(tc)
        
        return (cx, cy, cz), (ux, uy, uz), (vx, vy, vz)

    def get_star_3d_position(self, star_x: float, star_y: float, center_pos: tuple[float, float, float], u_vec: tuple[float, float, float], v_vec: tuple[float, float, float], scale: float) -> tuple[float, float, float]:
        """接平面上のローカル座標を3D空間の天球表面上の座標に投影・正規化して返す。"""
        cx, cy, cz = center_pos
        ux, uy, uz = u_vec
        vx, vy, vz = v_vec
        
        px_un = cx + scale * (star_x * ux + star_y * vx)
        py_un = cy + scale * (star_x * uy + star_y * vy)
        pz_un = cz + scale * (star_x * uz + star_y * vz)
        
        len_s = math.sqrt(px_un**2 + py_un**2 + pz_un**2)
        if len_s < 0.001:
            len_s = 1.0
            
        return px_un / len_s, py_un / len_s, pz_un / len_s
