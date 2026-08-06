#!/usr/bin/env python3
"""小海桌宠 - 自动去除图片背景脚本"""
import os
import sys
from collections import Counter
from math import sqrt

try:
    from PIL import Image
except ImportError:
    print("请先安装 Pillow: pip install pillow")
    sys.exit(1)

def remove_background(image_path, threshold=50):
    """去除图片纯色背景"""
    try:
        img = Image.open(image_path).convert("RGBA")
        pixels = img.load()
        w, h = img.size
        
        # 采样边缘像素识别背景色
        samples = []
        for x in range(0, w, max(1, w // 10)):
            samples.append(pixels[x, 0][:3])
            samples.append(pixels[x, h-1][:3])
        for y in range(0, h, max(1, h // 10)):
            samples.append(pixels[0, y][:3])
            samples.append(pixels[w-1, y][:3])
        for x, y in [(0,0), (w-1,0), (0,h-1), (w-1,h-1)]:
            samples.append(pixels[x, y][:3])
        
        bg_color = Counter(samples).most_common(1)[0][0]
        print(f"检测到背景色: RGB{bg_color}")
        
        # 去除背景
        for y in range(h):
            for x in range(w):
                r, g, b, a = pixels[x, y]
                dist = sqrt((r-bg_color[0])**2 + (g-bg_color[1])**2 + (b-bg_color[2])**2)
                if dist < threshold:
                    pixels[x, y] = (r, g, b, 0)
        
        # 智能裁剪
        bbox = img.getbbox()
        if bbox:
            margin = 5
            bbox = (max(0, bbox[0]-margin), max(0, bbox[1]-margin),
                    min(w, bbox[2]+margin), min(h, bbox[3]+margin))
            img = img.crop(bbox)
        
        out_path = "character_nobg.png"
        img.save(out_path, "PNG")
        print(f"背景去除成功！已保存为: {out_path}")
        return out_path
    except Exception as e:
        print(f"背景去除失败: {e}")
        return None

if __name__ == "__main__":
    for path in ["character.jpg", "character.png", "character.jpeg"]:
        if os.path.exists(path):
            print(f"处理图片: {path}")
            remove_background(path)
            break
    else:
        print("未找到角色图片")
