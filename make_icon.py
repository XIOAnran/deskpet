#!/usr/bin/env python3
"""生成桌宠图标"""
from PIL import Image, ImageDraw
import os

def create_icon():
    sizes = [16, 32, 48, 64, 128, 256]
    
    for path in ["character_nobg.png", "character.jpg", "character.png"]:
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            # Create ICO with multiple sizes
            img.save("icon.ico", format="ICO", sizes=[(s, s) for s in sizes if s <= max(img.size)])
            print(f"图标已生成: icon.ico")
            return
    
    # Create fallback icon
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([30, 30, 226, 226], fill=(100, 150, 255, 200))
    draw.ellipse([20, 15, 60, 55], fill=(100, 150, 255, 200))
    draw.ellipse([196, 15, 236, 55], fill=(100, 150, 255, 200))
    draw.ellipse([70, 80, 100, 110], fill=(255, 255, 255))
    draw.ellipse([156, 80, 186, 110], fill=(255, 255, 255))
    draw.ellipse([78, 88, 92, 102], fill=(50, 50, 50))
    draw.ellipse([164, 88, 178, 102], fill=(50, 50, 50))
    img.save("icon.ico", format="ICO", sizes=[(s, s) for s in sizes])
    print("已生成默认图标: icon.ico")

if __name__ == "__main__":
    create_icon()
