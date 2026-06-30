import cv2
import numpy as np
import os
import json

def process_images():
    base_dir = "/Users/sootta/Documents/git/sootta/stella-repairer/source/constellation_images/download/"
    out_json_path = "/Users/sootta/Documents/git/sootta/stella-repairer/data/downloaded_constellations.json"
    
    # Check directory
    if not os.path.exists(base_dir):
        print(f"Error: {base_dir} does not exist.")
        return
        
    # Constellation info mapping (Id -> Name, English Name, Category, Description)
    info_map = {
        "the_alchemist": {
            "name": "錬金術師座", "english_name": "The Alchemist", "category": "artifact",
            "description": "大いなる賢者の石と世界の真理を追い求める錬金術師の姿を描いた星座。"
        },
        "the_broken_sword_": {
            "name": "折れた剣座", "english_name": "The Broken Sword", "category": "artifact",
            "description": "かつて大いなる戦いで砕かれ、天に召された伝説の聖剣。折れた刃先と緻密な柄の装飾が今も金色に輝く。"
        },
        "the_butterfly": {
            "name": "蝶座", "english_name": "The Butterfly", "category": "creature",
            "description": "星々の間を優雅に舞い、生命の循環と変化を司る美しい蝶の星座。"
        },
        "the_clockwork_owl": {
            "name": "時詠みのフクロウ座", "english_name": "The Clockwork Owl", "category": "creature",
            "description": "精密な歯車で動く心臓を持ち、大きな双眸で宇宙の時間を監視するフクロウの星座。"
        },
        "the_cloud_whale": {
            "name": "雲鯨座", "english_name": "The Cloud Whale", "category": "creature",
            "description": "星界 of 雲海を悠々と泳ぎ、潮の満ち引きと夢を司る巨大な鯨の星座。"
        },
        "the_cross": {
            "name": "十字架座", "english_name": "The Cross", "category": "artifact",
            "description": "天の川の交差点に静かに佇み、宇宙を旅する者たちの行く末を導く聖なる十字架の星座。"
        },
        "the_crystal_cave": {
            "name": "水晶洞窟座", "english_name": "The Crystal Cave", "category": "location",
            "description": "無数の星の光を反射して怪しくも美しく輝く、神秘的なクリスタルの洞窟を象った星座。"
        },
        "the_echo": {
            "name": "反響座", "english_name": "The Echo", "category": "phenomenon",
            "description": "星々の瞬きが宇宙の深淵に響き渡り、波紋のように広がっていく様子を表した星座。"
        },
        "the_fox": {
            "name": "狐座", "english_name": "The Fox", "category": "creature",
            "description": "流星の尾を追いかけて天球を俊敏に駆け巡る、賢く美しい狐の星座。"
        },
        "the_golden_astrolabe": {
            "name": "黄金のアストロラーベ座", "english_name": "The Golden Astrolabe", "category": "artifact",
            "description": "天体の複雑な運行を計算し、運命の航路を指し示す黄金の測定儀の星座。"
        },
        "the_hourglass": {
            "name": "砂時計座", "english_name": "The Hourglass", "category": "artifact",
            "description": "宇宙の始まりから終わりまでの静かな時の流れを、落ちる星屑で刻み続ける砂時計の星座。"
        },
        "the_key": {
            "name": "鍵座", "english_name": "The Key", "category": "artifact",
            "description": "閉ざされた星界の門を開き、失われた大いなる知識を解き放つとされる銀の鍵の星座。"
        },
        "the_labyring": {
            "name": "迷宮座", "english_name": "The Labyrinth", "category": "location",
            "description": "星々の光が複雑に交差し、迷い込んだものを惑わせる天上の迷宮を模した星座。"
        },
        "the_lantern": {
            "name": "ランタン座", "english_name": "The Lantern", "category": "artifact",
            "description": "暗黒の深宇宙を優しく照らし、旅する星の巡礼者たちの道を案内するランタンの星座。"
        },
        "the_lighthouse_keeper": {
            "name": "灯台守座", "english_name": "The Lighthouse Keeper", "category": "creature",
            "description": "星海の果てにある孤高の灯台を守り、彼方へと光を送り続ける孤独な番人の星座。"
        },
        "the_lost_child": {
            "name": "迷い子座", "english_name": "The Lost Child", "category": "creature",
            "description": "失われた母なる星を求めて永遠の夜空をさまよう、小さく愛らしい星の精霊の星座。"
        },
        "the_masks_space": {
            "name": "宇宙の仮面座", "english_name": "The Masks of Space", "category": "artifact",
            "description": "喜劇と悲劇を司り、宇宙の混沌と秩序の二面性を表現する対の仮面の星座。"
        },
        "the_mirage": {
            "name": "蜃気楼座", "english_name": "The Mirage", "category": "phenomenon",
            "description": "光の屈折が生み出す天上の幻影であり、遥か彼方の異世界の姿を映し出す星座。"
        },
        "the_moonbow": {
            "name": "月虹座", "english_name": "The Moonbow", "category": "phenomenon",
            "description": "月の清らかな光が星界の霧に反射して描かれる、淡く美しい七色の架け橋の星座。"
        },
        "the_pen_nib": {
            "name": "ペン先座", "english_name": "The Pen Nib", "category": "artifact",
            "description": "星々の歴史と宇宙の叙事詩を夜空に書き綴り続ける巨大な万年筆のペン先の星座。"
        },
        "the_silent_oath": {
            "name": "静寂の誓い座", "english_name": "The Silent Oath", "category": "artifact",
            "description": "言葉なき誓いを象徴し、永久の忠誠を誓う盾と剣を描いた厳粛な星座。"
        },
        "the_sleeping_dragon": {
            "name": "眠れる竜座", "english_name": "The Sleeping Dragon", "category": "creature",
            "description": "銀河の底で長い眠りにつき、世界の終わりと新生を見守るとされる大竜の星座。"
        },
        "the_spinner": {
            "name": "紡ぎ手座", "english_name": "The Spinner", "category": "creature",
            "description": "運命の糸を紡ぎ出し、星々の絆と命の繋がりを編み上げる紡ぎ手の星座。"
        },
        "the_tree": {
            "name": "世界樹座", "english_name": "The Tree", "category": "creature",
            "description": "宇宙の深淵に深く根を張り、星々の生命力を永遠に支える大樹の星座。"
        },
        "the_twin_volcanoes": {
            "name": "双子火山座", "english_name": "The Twin Volcanoes", "category": "location",
            "description": "激しく星のマグマを噴き出し、宇宙の新たな星々の誕生を告げる二つの火山の星座。"
        },
        "the_two_tailed_cat": {
            "name": "二尾の猫座", "english_name": "The Two-Tailed Cat", "category": "creature",
            "description": "二又に分かれた長い尻尾で星海の星屑を追いかけ回す、いたずら好きな猫の星座。"
        },
        "the_zenith": {
            "name": "天頂座", "english_name": "The Zenith", "category": "location",
            "description": "天球の最上部に位置し、全ての星々の運行を静かに見下ろす宇宙の頂点の星座。"
        }
    }

    files = [f for f in os.listdir(base_dir) if f.endswith(".jpeg") or f.endswith(".jpg")]
    files.sort()
    
    output_constellations = []
    
    for f_name in files:
        base_name = os.path.splitext(f_name)[0]
        # Match info
        info = info_map.get(base_name)
        if not info:
            # Try to match stripping trailing underscores
            stripped_name = base_name.rstrip("_")
            info = info_map.get(stripped_name)
            if not info:
                print(f"Warning: {f_name} not found in info mapping, using default values.")
                info = {
                    "name": base_name.replace("_", " ").capitalize() + "座",
                    "english_name": base_name.replace("_", " ").capitalize(),
                    "category": "creature",
                    "description": "星空に輝く星座の一つ。"
                }
        
        img_path = os.path.join(base_dir, f_name)
        img = cv2.imread(img_path)
        if img is None:
            print(f"Error: Failed to load {f_name}")
            continue
            
        h, w, c = img.shape
        cx_pixel = w / 2.0
        cy_pixel = h / 2.0
        scale_div = h / 2.0  # normalize relative to half height
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # 1. Yellow mask (robust settings)
        lower_yellow = np.array([8, 15, 20])
        upper_yellow = np.array([38, 255, 255])
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        
        # Mask out title and description text areas before finding contours and distance transforms
        # Title area: top 22%, X center 12%-88%
        # Desc area: bottom 15%, X center 12%-88%
        yellow_mask[0:int(0.22*h), int(0.12*w):int(0.88*w)] = 0
        yellow_mask[int(0.85*h):h, int(0.12*w):int(0.88*w)] = 0
        
        # 2. Distance to yellow mask
        yellow_mask_inv = cv2.bitwise_not(yellow_mask)
        dist_to_yellow = cv2.distanceTransform(yellow_mask_inv, cv2.DIST_L2, 3)
        
        # 3. Find max gray value near yellow mask (dist <= 3) using 99th percentile
        near_yellow = (dist_to_yellow <= 3) & (gray > 10)
        if not np.any(near_yellow):
            print(f"Warning: No yellow lines found in {f_name}")
            max_gray_near_yellow = 180 # fallback
        else:
            near_yellow_vals = gray[near_yellow]
            near_yellow_vals = np.sort(near_yellow_vals)
            if len(near_yellow_vals) > 200:
                idx = int(len(near_yellow_vals) * 0.992)
                max_gray_near_yellow = near_yellow_vals[idx]
            else:
                max_gray_near_yellow = np.max(near_yellow_vals)
        
        # Dynamic min_area
        min_area = 2 if max_gray_near_yellow < 180 else 6
        
        # Adaptive threshold feedback loop for stars
        T = int(max_gray_near_yellow - 25)
        T = max(50, min(242, T))
        
        stars = []
        for attempt in range(15):
            _, bright_mask = cv2.threshold(gray, T, 255, cv2.THRESH_BINARY)
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(bright_mask)
            
            stars = []
            for i in range(1, num_labels):
                area = stats[i, cv2.CC_STAT_AREA]
                if area < min_area or area > 1000:
                    continue
                cx, cy = centroids[i]
                
                # Check distance to yellow
                iy, ix = int(round(cy)), int(round(cx))
                if iy < 0 or iy >= h or ix < 0 or ix >= w:
                    continue
                dist = dist_to_yellow[iy, ix]
                if dist > 3:
                    continue
                    
                # Title/desc filters and border margins (ignore outer 10% width)
                if cx < 0.10 * w or cx > 0.90 * w:
                    continue
                if cy < 0.22 * h and (0.15 * w < cx < 0.85 * w):
                    continue
                if cy > 0.85 * h and (0.15 * w < cx < 0.85 * w):
                    continue
                    
                max_val = np.max(gray[labels == i])
                stars.append({
                    "coords": (cx, cy),
                    "area": area,
                    "max_val": max_val
                })
                
            # Check count
            if len(stars) > 28:
                T += 4
                if T >= 250:
                    break
            elif len(stars) < 8 and T > 50:
                T -= 4
            else:
                break
                
        # Keep top 25 stars
        stars.sort(key=lambda x: (x["max_val"], x["area"]), reverse=True)
        top_stars = stars[:25]
        
        # Re-sort top_stars by position (left to right)
        top_stars.sort(key=lambda x: x["coords"][0])
        
        # Convert stars to output format (normalize coordinates)
        out_stars = []
        for s in top_stars:
            # normalize: x_norm = (x - cx) / scale_div, y_norm = -(y - cy) / scale_div
            x_norm = float((s["coords"][0] - cx_pixel) / scale_div)
            y_norm = float(-(s["coords"][1] - cy_pixel) / scale_div)
            
            # Determine magnitude relative to max_gray_near_yellow
            score = s["max_val"] / max_gray_near_yellow if max_gray_near_yellow > 0 else 1.0
            if score > 0.98:
                mag = 0.5
            elif score > 0.94:
                mag = 1.0
            elif score > 0.90:
                mag = 1.5
            elif score > 0.84:
                mag = 2.0
            else:
                mag = 2.5
                
            out_stars.append({
                "x": round(x_norm, 4),
                "y": round(y_norm, 4),
                "magnitude": mag
            })
            
        # Detect lines
        out_lines = []
        for i in range(len(top_stars)):
            for j in range(i + 1, len(top_stars)):
                p1 = np.array(top_stars[i]["coords"])
                p2 = np.array(top_stars[j]["coords"])
                dist = np.linalg.norm(p1 - p2)
                if dist < 20 or dist > 350:
                    continue
                    
                # Sample along line
                num_samples = int(max(10, dist / 2))
                t_vals = np.linspace(0, 1, num_samples)
                yellow_hits = 0
                for t in t_vals:
                    pt = p1 + t * (p2 - p1)
                    px, py = int(round(pt[0])), int(round(pt[1]))
                    if 0 <= px < w and 0 <= py < h:
                        neighborhood = yellow_mask[max(0, py-1):min(h, py+2), max(0, px-1):min(w, px+2)]
                        if np.any(neighborhood > 0):
                            yellow_hits += 1
                ratio = yellow_hits / num_samples
                if ratio > 0.8:
                    out_lines.append([i, j])
                    
        # 4. Extract drawing paths (art_paths)
        # Find contours on yellow_mask (titles masked out)
        contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        out_art_paths = []
        
        for cnt in contours:
            if cv2.arcLength(cnt, True) < 30:
                continue
                
            # Epsilon ~ 1.5 to keep it smooth and simple
            approx = cv2.approxPolyDP(cnt, 1.5, True)
            
            path = []
            for pt in approx:
                px, py = pt[0]
                # Normalize coordinate
                x_norm = float((px - cx_pixel) / scale_div)
                y_norm = float(-(py - cy_pixel) / scale_div)
                path.append([round(x_norm, 4), round(y_norm, 4)])
                
            if len(path) >= 2:
                out_art_paths.append(path)
                
        # Build constellation object
        const_id = "c_" + base_name.rstrip("_")
        constellation = {
            "id": const_id,
            "name": info["name"],
            "english_name": info["english_name"],
            "category": info["category"],
            "description": info["description"],
            "stars": out_stars,
            "lines": out_lines,
            "art_paths": out_art_paths
        }
        
        output_constellations.append(constellation)
        print(f"Processed {f_name} -> ID: {const_id}, Stars: {len(out_stars)}, Lines: {len(out_lines)}, Art Paths: {len(out_art_paths)}")
        
    # Write to JSON
    with open(out_json_path, "w", encoding="utf-8") as out_f:
        json.dump({"constellations": output_constellations}, out_f, ensure_ascii=False, indent=2)
        
    print(f"\nSaved all {len(output_constellations)} constellations to {out_json_path}")

if __name__ == "__main__":
    process_images()
