#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小海桌宠 v2.0 - Windows Desktop Pet
基于 PyQt5 + Pillow 的透明桌面宠物
功能：透明无边框、置顶、拖拽、互动动画、对话气泡、右键菜单、滚轮缩放
"""

import sys
import os
import math
import random
import json
import traceback
from collections import Counter

from PyQt5.QtWidgets import (
    QApplication, QWidget, QMenu, QAction, QSlider, QDialog,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QFileDialog, QMessageBox, QCheckBox, QGroupBox, QDialogButtonBox
)
from PyQt5.QtCore import (
    Qt, QTimer, QPoint, QRect, QPropertyAnimation, QEasingCurve,
    pyqtProperty, QSize, QRectF
)
from PyQt5.QtGui import (
    QPixmap, QPainter, QPainterPath, QFont, QColor, QPen,
    QFontMetrics, QTransform, QIcon, QLinearGradient, QBrush,
    QRadialGradient, QCursor, QImage, QPolygonF
)

# ============================================================
# 配置区域（用户可自定义）
# ============================================================
CONFIG_FILE = "deskpet_config.json"
CHARACTER_IMAGE = "character_nobg.png"
FALLBACK_IMAGE = "character.jpg"
APP_NAME = "小海桌宠"
WINDOW_TITLE = "小海桌宠"

# 默认对话气泡内容
DEFAULT_CHAT_MESSAGES = [
    "嘿！想我了吗？(=^_^=)",
    "今天也要加油鸭！💪",
    "嗯…让我想想…🤔",
    "嘿嘿，好无聊呀~ 😴",
    "你戳我干嘛！(｀へ´)",
    "嘻嘻，再摸摸头~ ❤️",
    "好饿呀，有吃的吗？🍔",
    "今天天气真不错！☀️",
    "代码写完了吗？(￣▽￣)",
    "加油加油！你是最棒的！🌟",
    "呼噜…呼噜…💤",
    "嘿！别走嘛~ 🥺",
    "好开心呀！转圈圈~ 🎉",
    "今天也要认真工作哟！",
    "嗯？你在看什么？👀",
    "我好喜欢你呀！💕",
    "要不要一起摸鱼？🐟",
    "我可是会卖萌的！😝",
    "累了吗？休息一下吧~ ☕",
    "目标：成为最萌桌宠！✨",
    "嘿嘿，被你发现啦~ 😊",
    "今天也要元气满满！💪",
    "哼，我才不胖呢！🐷",
    "好想出去玩呀~ 🎈",
    "我能帮你做点什么吗？🤗",
]

# 互动对应的对话
INTERACTION_SPEECH = {
    "jump": ["哇！飞起来啦！✈️", "咻~ 跳高高！", "蹦蹦蹦！看我跳得多高！🎉"],
    "squish": ["哎呀！被压扁了！😵", "噗叽~ 变成饼了！🫓", "呜哇！快弹回来！"],
    "shake": ["抖抖抖抖抖~~~🌀", "哈哈哈好痒~ 🤪", "停不下来啦！🎢"],
    "pet": ["好舒服呀~ 再摸摸！❤️", "嗯~ 最喜欢被摸头了！🥰", "呼噜呼噜… 真舒服~ 😊"],
    "feed": ["啊呜~ 真好吃！😋", "再来一份！🍽️", "好好吃呀！幸福的味道~ 💕"],
    "chat": [],  # 随机对话
    "wave": ["你好呀！👋", "嗨嗨~ 看这里！", "嘿！朋友！🙌"],
    "dance": ["跟着音乐摇摆~ 🎵", "跳起来！💃", "一起跳舞吧！🕺"],
    "happy": ["好开心呀！🎉", "耶耶耶！✌️", "今天心情超好！🌟"],
}


# ============================================================
# 工具函数
# ============================================================

def remove_background_pil(image_path, threshold=50):
    """使用 PIL 去除图片背景（纯色背景）"""
    try:
        from PIL import Image
        pil_img = Image.open(image_path).convert("RGBA")
        pixels = pil_img.load()
        w, h = pil_img.size

        # 采样边缘像素识别背景色
        samples = []
        for x in range(0, w, max(1, w // 10)):
            samples.append(pixels[x, 0][:3])
            samples.append(pixels[x, h - 1][:3])
        for y in range(0, h, max(1, h // 10)):
            samples.append(pixels[0, y][:3])
            samples.append(pixels[w - 1, y][:3])
        # 加上四个角（更密集）
        for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
            samples.append(pixels[x, y][:3])

        bg_color = Counter(samples).most_common(1)[0][0]

        # 去除背景
        for y in range(h):
            for x in range(w):
                r, g, b, a = pixels[x, y]
                dist = math.sqrt(
                    (r - bg_color[0]) ** 2 +
                    (g - bg_color[1]) ** 2 +
                    (b - bg_color[2]) ** 2
                )
                if dist < threshold:
                    pixels[x, y] = (r, g, b, 0)

        # 智能裁剪空白区域
        bbox = pil_img.getbbox()
        if bbox:
            # 稍微加一点边距
            margin = 5
            bbox = (
                max(0, bbox[0] - margin),
                max(0, bbox[1] - margin),
                min(w, bbox[2] + margin),
                min(h, bbox[3] + margin)
            )
            pil_img = pil_img.crop(bbox)

        out_path = image_path.replace(".jpg", "_nobg.png").replace(".jpeg", "_nobg.png").replace(".png", "_nobg.png")
        if out_path == image_path:
            out_path = image_path.rsplit(".", 1)[0] + "_nobg.png"
        pil_img.save(out_path, "PNG")
        return out_path
    except Exception as e:
        print(f"背景去除失败: {e}")
        return None


def load_image(path):
    """加载图片，自动处理背景"""
    if not os.path.exists(path):
        return None

    pixmap = QPixmap(path)
    if pixmap.isNull():
        return None

    # 如果没有透明通道，尝试自动去背景
    if not pixmap.hasAlphaChannel():
        result = remove_background_pil(path)
        if result and os.path.exists(result):
            pixmap = QPixmap(result)
        else:
            # 使用阈值法直接去背景
            qimg = pixmap.toImage()
            w, h = qimg.width(), qimg.height()
            # 采样边缘颜色
            samples = []
            for x in range(0, w, max(1, w // 5)):
                c = QColor(qimg.pixel(x, 0))
                samples.append((c.red(), c.green(), c.blue()))
                c = QColor(qimg.pixel(x, h - 1))
                samples.append((c.red(), c.green(), c.blue()))
            for y in range(0, h, max(1, h // 5)):
                c = QColor(qimg.pixel(0, y))
                samples.append((c.red(), c.green(), c.blue()))
                c = QColor(qimg.pixel(w - 1, y))
                samples.append((c.red(), c.green(), c.blue()))

            bg_color = Counter(samples).most_common(1)[0][0]
            threshold = 50

            for y in range(h):
                for x in range(w):
                    c = QColor(qimg.pixel(x, y))
                    dist = math.sqrt(
                        (c.red() - bg_color[0]) ** 2 +
                        (c.green() - bg_color[1]) ** 2 +
                        (c.blue() - bg_color[2]) ** 2
                    )
                    if dist < threshold:
                        qimg.setPixelColor(x, y, QColor(0, 0, 0, 0))

            pixmap = QPixmap.fromImage(qimg)

    return pixmap


# ============================================================
# 设置对话框
# ============================================================

class SettingsDialog(QDialog):
    """设置对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("小海桌宠 - 设置")
        self.setFixedSize(400, 350)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: "Microsoft YaHei", "SimHei", sans-serif;
            }
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 8px;
            }
            QLabel {
                font-size: 12px;
            }
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #ddd;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #1976D2;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)

        # 图片选择
        img_group = QGroupBox("角色图片")
        img_layout = QHBoxLayout(img_group)
        self.img_label = QLabel("当前: character.jpg")
        self.img_label.setWordWrap(True)
        img_layout.addWidget(self.img_label, 1)
        btn_change = QPushButton("更换图片")
        btn_change.clicked.connect(self.change_image)
        img_layout.addWidget(btn_change)
        layout.addWidget(img_group)

        # 大小设置
        size_group = QGroupBox("大小设置")
        size_layout = QHBoxLayout(size_group)
        size_layout.addWidget(QLabel("缩放:"))
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(20, 300)
        self.size_slider.setValue(int((parent.pet_scale if parent else 1.0) * 100))
        self.size_slider.valueChanged.connect(self.on_size_changed)
        size_layout.addWidget(self.size_slider, 1)
        self.size_label = QLabel(f"{self.size_slider.value()}%")
        size_layout.addWidget(self.size_label)
        layout.addWidget(size_group)

        # 速度设置
        speed_group = QGroupBox("移动速度")
        speed_layout = QHBoxLayout(speed_group)
        speed_layout.addWidget(QLabel("速度:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 20)
        self.speed_slider.setValue(parent.move_speed if parent else 5)
        speed_layout.addWidget(self.speed_slider, 1)
        self.speed_label = QLabel(str(self.speed_slider.value()))
        speed_layout.addWidget(self.speed_label)
        layout.addWidget(speed_group)

        # 对话气泡设置
        bubble_group = QGroupBox("对话气泡")
        bubble_layout = QHBoxLayout(bubble_group)
        self.bubble_check = QCheckBox("启用对话气泡")
        self.bubble_check.setChecked(True)
        bubble_layout.addWidget(self.bubble_check)
        layout.addWidget(bubble_group)

        # 确认按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.new_image_path = None

    def change_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择角色图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        if path:
            self.new_image_path = path
            self.img_label.setText(f"当前: {os.path.basename(path)}")

    def on_size_changed(self, val):
        self.size_label.setText(f"{val}%")

    def get_settings(self):
        return {
            "size": self.size_slider.value() / 100.0,
            "speed": self.speed_slider.value(),
            "bubble_enabled": self.bubble_check.isChecked(),
            "image_path": self.new_image_path,
        }


# ============================================================
# 对话气泡控件
# ============================================================

class SpeechBubble(QWidget):
    """对话气泡 - 智能定位，不遮挡角色"""

    def __init__(self, text, parent=None, bubble_style="normal"):
        super().__init__(parent)
        self.text = text
        self.opacity = 1.0
        self.font_size = 13
        self.padding_x = 16
        self.padding_y = 10
        self.triangle_size = 10
        self.border_radius = 10
        self.bubble_style = bubble_style

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint |
            Qt.WindowTransparentForInput
        )
        self.setFocusPolicy(Qt.NoFocus)

        # 计算气泡大小
        font = QFont("Microsoft YaHei", self.font_size)
        font.setHintingPreference(QFont.PreferNoHinting)
        self.font_metrics = QFontMetrics(font)
        text_rect = self.font_metrics.boundingRect(
            QRect(0, 0, 280, 200), Qt.TextWordWrap | Qt.AlignLeft, text
        )
        self.bubble_w = max(text_rect.width() + self.padding_x * 2 + 10, 80)
        self.bubble_h = max(text_rect.height() + self.padding_y * 2 + 10, 36)

        self.setFixedSize(self.bubble_w + 20, self.bubble_h + self.triangle_size + 20)

        # 自动消失
        self.fade_timer = QTimer(self)
        self.fade_timer.timeout.connect(self.fade_tick)
        self.fade_tick_count = 0
        self.fade_timer.start(30)

        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setOpacity(self.opacity)

        bw = self.bubble_w
        bh = self.bubble_h
        ts = self.triangle_size

        # 气泡主体矩形
        rect = QRect(10, 10, bw, bh)

        # 根据风格选择颜色
        if self.bubble_style == "happy":
            bg = QColor(255, 243, 224, 240)
            border = QColor(255, 193, 7, 200)
            text_color = QColor(230, 81, 0)
        elif self.bubble_style == "sleepy":
            bg = QColor(227, 242, 253, 240)
            border = QColor(66, 165, 245, 200)
            text_color = QColor(13, 71, 161)
        elif self.bubble_style == "angry":
            bg = QColor(255, 235, 238, 240)
            border = QColor(239, 83, 80, 200)
            text_color = QColor(183, 28, 28)
        else:
            bg = QColor(255, 255, 255, 240)
            border = QColor(200, 200, 200, 180)
            text_color = QColor(50, 50, 50)

        # 绘制阴影
        shadow = QPainterPath()
        shadow.addRoundedRect(QRectF(rect.x() + 2, rect.y() + 2, bw, bh), self.border_radius, self.border_radius)
        painter.fillPath(shadow, QColor(0, 0, 0, 30))

        # 绘制圆角矩形背景
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), self.border_radius, self.border_radius)
        painter.fillPath(path, QBrush(bg))
        painter.setPen(QPen(border, 1.5))
        painter.drawPath(path)

        # 绘制三角尾巴（指向角色方向）
        triangle = QPainterPath()
        cx = bw // 2 + 10
        ty = rect.bottom()
        triangle.moveTo(cx - ts, ty)
        triangle.lineTo(cx, ty + ts)
        triangle.lineTo(cx + ts, ty)
        triangle.closeSubpath()
        painter.fillPath(triangle, QBrush(bg))
        painter.setPen(QPen(border, 1.5))
        painter.drawPath(triangle)

        # 绘制文字
        painter.setPen(text_color)
        painter.setFont(font)
        text_rect = rect.adjusted(self.padding_x - 5, self.padding_y - 5,
                                  -self.padding_x + 5, -self.padding_y + 5)
        painter.drawText(text_rect, Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignVCenter, self.text)

    def font(self):
        return QFont("Microsoft YaHei", self.font_size)

    def fade_tick(self):
        self.fade_tick_count += 1
        if self.fade_tick_count >= 100:  # ~3 seconds
            self.opacity = max(0, self.opacity - 0.05)
            self.update()
            if self.opacity <= 0:
                self.fade_timer.stop()
                self.deleteLater()

    def set_position_relative_to(self, widget_rect):
        """将气泡定位在控件上方（有空间）或下方"""
        screen = QApplication.primaryScreen().geometry()
        margin = 20

        # 优先放在上方
        cx = widget_rect.center().x() - self.width() // 2
        cx = max(margin, min(cx, screen.width() - self.width() - margin))

        if widget_rect.top() > self.height() + margin + 30:
            # 上方有空间
            cy = widget_rect.top() - self.height() - 5
        else:
            # 放在下方
            cy = widget_rect.bottom() + 5
            cy = min(cy, screen.height() - self.height() - margin)

        self.move(cx, cy)


# ============================================================
# 主桌宠窗口
# ============================================================

class DesktopPet(QWidget):
    """桌面宠物主窗口"""

    # 自定义信号
    DROP_SHADOW_RADIUS = 8

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.original_pixmap = None
        self.current_pixmap = None

        # 基础状态
        self.pet_scale = 1.0
        self.is_dragging = False
        self.drag_offset = QPoint()
        self.anim_frame = 0
        self.always_on_top = True
        self.bubble_enabled = True

        # 动画定时器
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.setInterval(30)

        # 模式
        self.MODE_IDLE = "idle"
        self.MODE_WALKING = "walking"
        self.MODE_SLEEPING = "sleeping"
        self.current_mode = self.MODE_IDLE

        # 互动动画状态
        self.interaction_type = None
        self.interaction_frame = 0
        self.interaction_max_frame = 20
        self.is_interacting = False
        self.interact_count = 0

        # 走路动画
        self.walk_frame = 0
        self.walk_direction = 1
        self.move_target = None
        self.is_moving = False
        self.move_speed = 5
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.update_move)
        self.move_timer.setInterval(30)

        # 随机漫步
        self.random_walk_timer = QTimer(self)
        self.random_walk_timer.timeout.connect(self.random_walk_tick)
        self.random_walk_timer.setInterval(5000)

        # 睡觉动画
        self.sleep_breath = 0
        self.zzz_frame = 0

        # 呼吸动画（空闲时）
        self.idle_breath = 0
        self.idle_breath_active = False

        # 对话气泡
        self.speech_bubble = None
        self.current_bubble_text = None
        self.bubble_auto_timer = QTimer(self)
        self.bubble_auto_timer.timeout.connect(self.show_random_speech)
        self.bubble_auto_timer.setInterval(30000)  # 每30秒自动说一句

        # 跟随鼠标
        self.follow_mouse = False
        self.follow_timer = QTimer(self)
        self.follow_timer.timeout.connect(self.follow_mouse_update)
        self.follow_timer.setInterval(30)

        # 聊天模式
        self.chat_mode = False
        self.chat_messages = DEFAULT_CHAT_MESSAGES[:]

        # 影子位置
        self.shadow_bottom = 0

        self.init_ui()
        self.load_character()
        self.center_on_screen()
        self.bubble_auto_timer.start()

    def init_ui(self):
        """初始化窗口"""
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet("background: transparent;")

        flags = Qt.FramelessWindowHint | Qt.Tool
        if self.always_on_top:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        self.setWindowTitle(WINDOW_TITLE)
        self.setMouseTracking(True)
        self.setMinimumSize(30, 30)

        self.setup_context_menu()

    def setup_context_menu(self):
        """设置右键菜单"""
        self.menu = QMenu(self)
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 5px 0px;
                font-size: 13px;
                font-family: "Microsoft YaHei", "SimHei", sans-serif;
            }
            QMenu::item {
                padding: 8px 30px 8px 20px;
                min-width: 130px;
            }
            QMenu::item:selected {
                background-color: #e3f2fd;
                color: #1565c0;
            }
            QMenu::item:disabled {
                color: #aaaaaa;
            }
            QMenu::separator {
                height: 1px;
                background: #eeeeee;
                margin: 4px 10px;
            }
            QMenu::indicator {
                width: 14px;
                height: 14px;
                margin-left: 4px;
            }
        """)

        # 互动菜单
        c = self.menu.addAction("💬 陪我聊聊天")
        c.triggered.connect(lambda: self.start_interaction("chat"))
        p = self.menu.addAction("🤚 摸摸头")
        p.triggered.connect(lambda: self.start_interaction("pet"))
        f = self.menu.addAction("🍔 喂吃的")
        f.triggered.connect(lambda: self.start_interaction("feed"))
        w = self.menu.addAction("👋 打个招呼")
        w.triggered.connect(lambda: self.start_interaction("wave"))

        self.menu.addSeparator()

        # 动作菜单
        a1 = self.menu.addAction("🚶 让她走路")
        a1.triggered.connect(self.start_walking)
        a2 = self.menu.addAction("💤 让她睡觉")
        a2.triggered.connect(self.start_sleeping)
        a3 = self.menu.addAction("🕺 跳个舞")
        a3.triggered.connect(lambda: self.start_interaction("dance"))

        self.menu.addSeparator()

        a4 = self.menu.addAction("🖱️ 跟随鼠标")
        a4.setCheckable(True)
        a4.setChecked(self.follow_mouse)
        a4.triggered.connect(lambda c: self.toggle_follow_mouse(c))
        self.follow_menu_action = a4

        # 大小子菜单
        size_menu = self.menu.addMenu("📏 调整大小")
        size_menu.setStyleSheet(self.menu.styleSheet())
        size_menu.addAction("超小 (0.3x)", lambda: self.set_pet_size(0.3))
        size_menu.addAction("小 (0.5x)", lambda: self.set_pet_size(0.5))
        size_menu.addAction("中 (0.8x)", lambda: self.set_pet_size(0.8))
        size_menu.addAction("标准 (1.0x)", lambda: self.set_pet_size(1.0))
        size_menu.addAction("大 (1.5x)", lambda: self.set_pet_size(1.5))
        size_menu.addAction("超大 (2.0x)", lambda: self.set_pet_size(2.0))
        size_menu.addAction("巨大 (3.0x)", lambda: self.set_pet_size(3.0))

        self.menu.addSeparator()

        a5 = self.menu.addAction("📌 置顶开关")
        a5.setCheckable(True)
        a5.setChecked(self.always_on_top)
        a5.triggered.connect(self.toggle_pin)
        self.pin_menu_action = a5

        self.menu.addSeparator()

        self.menu.addAction("⚙️ 设置", self.open_settings)
        self.menu.addSeparator()
        self.menu.addAction("❌ 退出程序", self.exit_app)

    def load_character(self):
        """加载角色图片"""
        pixmap = load_image(self.image_path)
        if pixmap is None or pixmap.isNull():
            # 尝试备用路径
            alt_path = self.image_path.replace("_nobg.png", ".jpg")
            pixmap = load_image(alt_path)

        if pixmap is None or pixmap.isNull():
            # 创建默认占位图 - 可爱圆形角色
            size = 200
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            # 身体
            painter.setBrush(QColor(100, 150, 255, 200))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(30, 30, 140, 140)

            # 耳朵
            painter.drawEllipse(20, 15, 40, 40)
            painter.drawEllipse(140, 15, 40, 40)

            # 眼睛
            painter.setBrush(Qt.white)
            painter.drawEllipse(60, 70, 30, 30)
            painter.drawEllipse(110, 70, 30, 30)
            painter.setBrush(QColor(50, 50, 50))
            painter.drawEllipse(70, 80, 12, 12)
            painter.drawEllipse(120, 80, 12, 12)

            # 嘴巴
            painter.setPen(QPen(QColor(50, 50, 50), 2))
            painter.drawArc(70, 100, 60, 30, 0, -180 * 16)

            # 腮红
            painter.setBrush(QColor(255, 150, 150, 80))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(40, 100, 25, 15)
            painter.drawEllipse(135, 100, 25, 15)

            painter.end()

        self.original_pixmap = pixmap
        self.update_pixmap()
        self.resize(self.current_pixmap.size())
        self.shadow_bottom = self.height() - 2

    def update_pixmap(self):
        """根据当前缩放更新显示图片"""
        if self.original_pixmap is None:
            return

        size = self.original_pixmap.size() * self.pet_scale
        self.current_pixmap = self.original_pixmap.scaled(
            size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.resize(self.current_pixmap.size())
        self.shadow_bottom = self.height() - 2
        self.update()

    def set_pet_size(self, scale):
        """设置宠物大小"""
        old_scale = self.pet_scale
        self.pet_scale = max(0.2, min(4.0, scale))
        # 保持中心位置
        old_center = self.geometry().center()
        self.update_pixmap()
        new_rect = self.geometry()
        new_rect.moveCenter(old_center)
        self.setGeometry(new_rect)

    def center_on_screen(self):
        """居中显示"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    # ============================================================
    # 绘制事件
    # ============================================================

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.current_pixmap is None:
            return

        # 绘制阴影
        self.draw_ground_shadow(painter)

        # 根据当前模式/动画绘制角色
        if self.is_interacting:
            self.draw_interaction(painter)
        elif self.current_mode == self.MODE_SLEEPING:
            self.draw_sleeping(painter)
        elif self.is_moving or self.is_dragging:
            self.draw_walking(painter)
        else:
            self.draw_idle(painter)

    def draw_ground_shadow(self, painter):
        """绘制角色脚下的柔和阴影"""
        w = self.width()
        h = self.height()
        el_w = max(20, w * 0.5)
        el_h = max(6, el_w * 0.2)
        cx = w // 2
        bottom = h - 2

        shadow = QRadialGradient(cx, bottom, el_w / 2)
        shadow.setColorAt(0, QColor(0, 0, 0, 60))
        shadow.setColorAt(0.6, QColor(0, 0, 0, 30))
        shadow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(shadow))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, bottom), el_w / 2, el_h)

    def draw_idle(self, painter):
        """绘制空闲状态 - 带轻微呼吸动画"""
        self.idle_breath += 1
        breath = math.sin(self.idle_breath * 0.03) * 0.008
        scale = 1.0 + breath

        w = self.width()
        h = self.height()
        painter.save()
        painter.translate(w // 2, h // 2)
        painter.scale(scale, scale)
        painter.translate(-w // 2, -h // 2)
        painter.drawPixmap(0, 0, self.current_pixmap)
        painter.restore()

    def draw_walking(self, painter):
        """绘制走路状态 - 轻微上下晃动"""
        if self.is_dragging:
            # 被拖动时：轻微倾斜
            dx = self.drag_offset.x() - self.width() / 2 if hasattr(self, 'drag_offset') else 0
            tilt = max(-0.05, min(0.05, dx * 0.001))
        else:
            # 走路时：上下颠簸 + 轻微左右摆动
            tilt = math.sin(self.walk_frame * 0.3) * 0.03
            bounce = abs(math.sin(self.walk_frame * 0.3)) * 3

        w = self.width()
        h = self.height()
        painter.save()
        painter.translate(w // 2, h // 2)

        if self.is_dragging:
            painter.rotate(tilt * 180 / math.pi)
        else:
            painter.translate(tilt * 20, -bounce)
            painter.rotate(tilt * 180 / math.pi)

        # 走路时稍微左右拉伸
        squeeze = 1.0 + math.sin(self.walk_frame * 0.3) * 0.02
        painter.scale(squeeze, 1.0 / squeeze)

        painter.translate(-w // 2, -h // 2)
        painter.drawPixmap(0, 0, self.current_pixmap)
        painter.restore()

    def draw_sleeping(self, painter):
        """绘制睡觉状态 - 呼吸动画 + Zzz"""
        breath = math.sin(self.sleep_breath * 0.05) * 0.03
        scale = 1.0 + breath

        w = self.width()
        h = self.height()
        painter.save()
        painter.translate(w // 2, h // 2)
        painter.scale(scale, scale)
        painter.translate(-w // 2, -h // 2)

        # 睡觉时降低亮度
        painter.setOpacity(0.9)
        painter.drawPixmap(0, 0, self.current_pixmap)
        painter.restore()

        # 绘制 Zzz 气泡
        zz = self.sleep_breath % 120
        if zz < 80:
            z_count = (zz // 20) % 3 + 1
            for i in range(z_count):
                size = 14 + i * 5
                painter.setFont(QFont("Arial", size))
                alpha = max(40, 180 - zz * 2 - i * 30)
                painter.setPen(QColor(100, 100, 255, alpha))
                x = w - 10 + i * 12
                y = 10 + i * 22 - (zz % 40)
                painter.drawText(int(x), int(y), "Z" * (i + 1))

    # ============================================================
    # 互动动画绘制
    # ============================================================

    def draw_interaction(self, painter):
        if self.interaction_type == "jump":
            self.draw_jump(painter)
        elif self.interaction_type == "squish":
            self.draw_squish(painter)
        elif self.interaction_type == "shake":
            self.draw_shake(painter)
        elif self.interaction_type == "pet":
            self.draw_pet(painter)
        elif self.interaction_type == "feed":
            self.draw_feed(painter)
        elif self.interaction_type == "dance":
            self.draw_dance(painter)
        elif self.interaction_type == "wave":
            self.draw_wave(painter)
        elif self.interaction_type == "happy":
            self.draw_happy(painter)
        else:
            painter.drawPixmap(0, 0, self.current_pixmap)

    def draw_jump(self, painter):
        """跳跃动画 - 弧线弹跳"""
        progress = self.interaction_frame / self.interaction_max_frame
        # 弧线弹跳
        jump_height = -90 * math.sin(progress * math.pi)
        stretch = 1.0 + 0.08 * math.sin(progress * math.pi * 2)
        # 落地时压扁
        squash = 1.0 - 0.12 * abs(math.sin(progress * math.pi))

        w = self.width()
        h = self.height()
        painter.save()
        painter.translate(w // 2, h // 2 + jump_height)
        painter.scale(1.0 + (stretch - 1.0) * 0.5, squash)
        painter.translate(-w // 2, -h // 2)
        painter.drawPixmap(0, 0, self.current_pixmap)
        painter.restore()

    def draw_squish(self, painter):
        """压扁回弹动画 - 物理弹性效果"""
        progress = self.interaction_frame / self.interaction_max_frame
        # 弹性回弹曲线
        if progress < 0.2:
            # 快速压扁
            t = progress / 0.2
            sx = 1.0 + t * 0.5
            sy = 1.0 - t * 0.35
        elif progress < 0.5:
            # 开始回弹
            t = (progress - 0.2) / 0.3
            sx = 1.5 - t * 0.4
            sy = 0.65 + t * 0.25
        elif progress < 0.8:
            # 过冲回弹
            t = (progress - 0.5) / 0.3
            sx = 1.1 - t * 0.15
            sy = 0.9 + t * 0.1
        else:
            # 稳定
            t = (progress - 0.8) / 0.2
            sx = 0.95 + t * 0.05
            sy = 1.0

        w = self.width()
        h = self.height()
        painter.save()
        painter.translate(w // 2, h // 2)
        painter.scale(sx, sy)
        painter.translate(-w // 2, -h // 2)
        painter.drawPixmap(0, 0, self.current_pixmap)
        painter.restore()

    def draw_shake(self, painter):
        """左右抖动动画 - 弹簧效果"""
        offset = math.sin(self.interaction_frame * 0.8) * 15 * \
                 max(0, 1 - self.interaction_frame / self.interaction_max_frame)
        rotation = math.sin(self.interaction_frame * 0.6) * 0.1 * \
                   max(0, 1 - self.interaction_frame / self.interaction_max_frame)

        w = self.width()
        h = self.height()
        painter.save()
        painter.translate(w // 2 + offset, h // 2)
        painter.rotate(rotation * 180 / math.pi)
        painter.translate(-w // 2, -h // 2)
        painter.drawPixmap(0, 0, self.current_pixmap)
        painter.restore()

    def draw_pet(self, painter):
        """摸摸头动画 - 幸福上下晃动"""
        offset = -abs(math.sin(self.interaction_frame * 0.4)) * 6
        painter.drawPixmap(0, offset, self.current_pixmap)

    def draw_feed(self, painter):
        """喂食动画 - 开心上下跳"""
        progress = self.interaction_frame / self.interaction_max_frame
        if progress < 0.5:
            t = progress / 0.5
            offset = -abs(math.sin(t * math.pi)) * 20
        else:
            t = (progress - 0.5) / 0.5
            offset = -abs(math.sin(t * math.pi * 0.5)) * 8

        painter.drawPixmap(0, offset, self.current_pixmap)

    def draw_dance(self, painter):
        """跳舞动画"""
        sway = math.sin(self.interaction_frame * 0.2) * 15
        rotation = math.sin(self.interaction_frame * 0.15) * 0.15
        bounce = abs(math.sin(self.interaction_frame * 0.25)) * 5

        w = self.width()
        h = self.height()
        painter.save()
        painter.translate(w // 2 + sway, h // 2 - bounce)
        painter.rotate(rotation * 180 / math.pi)
        painter.translate(-w // 2, -h // 2)
        painter.drawPixmap(0, 0, self.current_pixmap)
        painter.restore()

    def draw_wave(self, painter):
        """打招呼动画"""
        progress = self.interaction_frame / self.interaction_max_frame
        offset = -abs(math.sin(progress * math.pi * 2)) * 10
        rotation = math.sin(progress * math.pi * 2) * 0.08

        w = self.width()
        h = self.height()
        painter.save()
        painter.translate(w // 2, h // 2 + offset)
        painter.rotate(rotation * 180 / math.pi)
        painter.translate(-w // 2, -h // 2)
        painter.drawPixmap(0, 0, self.current_pixmap)
        painter.restore()

    def draw_happy(self, painter):
        """开心动画"""
        scale = 1.0 + 0.05 * math.sin(self.interaction_frame * 0.3)

        w = self.width()
        h = self.height()
        painter.save()
        painter.translate(w // 2, h // 2)
        painter.scale(scale, scale)
        painter.translate(-w // 2, -h // 2)
        painter.drawPixmap(0, 0, self.current_pixmap)
        painter.restore()

    # ============================================================
    # 动画更新
    # ============================================================

    def update_animation(self):
        """主动画更新"""
        if self.current_mode == self.MODE_SLEEPING:
            self.sleep_breath += 1
            self.update()

        if self.is_interacting:
            self.interaction_frame += 1
            if self.interaction_frame > self.interaction_max_frame:
                self.is_interacting = False
                self.interaction_type = None
                self.anim_timer.stop()
                self.current_mode = self.MODE_IDLE
                self.update()

    def update_move(self):
        """移动更新"""
        if self.move_target is None:
            self.stop_moving()
            return

        pos = self.pos()
        dx = self.move_target.x() - pos.x()
        dy = self.move_target.y() - pos.y()
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < self.move_speed:
            self.stop_moving()
            return

        # 朝目标移动
        step_x = (dx / dist) * self.move_speed
        step_y = (dy / dist) * self.move_speed

        self.walk_direction = 1 if dx > 0 else -1
        self.walk_frame += 1

        new_pos = QPoint(int(pos.x() + step_x), int(pos.y() + step_y))
        self.move(new_pos)
        self.update()

    # ============================================================
    # 鼠标事件
    # ============================================================

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_offset = event.pos()
            self.current_mode = self.MODE_WALKING
            self.setCursor(Qt.ClosedHandCursor)
            # 停止移动
            if self.is_moving:
                self.stop_moving()

            if self.follow_mouse:
                self.toggle_follow_mouse(False)

            self.update()
        elif event.button() == Qt.RightButton:
            self.pin_menu_action.setChecked(self.always_on_top)
            self.follow_menu_action.setChecked(self.follow_mouse)
            self.menu.exec_(event.globalPos())

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() & Qt.LeftButton:
            new_pos = self.mapToGlobal(event.pos() - self.drag_offset)
            self.move(new_pos)
            self.walk_frame += 1
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_dragging:
                self.is_dragging = False
                self.setCursor(Qt.ArrowCursor)

                # 如果拖动的距离很小，视为点击
                drag_dist = math.sqrt(
                    (event.pos().x() - self.drag_offset.x()) ** 2 +
                    (event.pos().y() - self.drag_offset.y()) ** 2
                )
                if drag_dist < 8:
                    self.on_click()
                else:
                    self.current_mode = self.MODE_IDLE
                    self.update()
                    self.show_speech(random.choice(["呼~ 到了这里！", "嘿咻嘿咻！🚶", "走一走真舒服~"]))

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_interaction("chat")

    def wheelEvent(self, event):
        """鼠标滚轮调整大小"""
        delta = event.angleDelta().y()
        if delta > 0:
            self.set_pet_size(self.pet_scale + 0.1)
        else:
            self.set_pet_size(self.pet_scale - 0.1)

    def enterEvent(self, event):
        """鼠标进入"""
        if self.current_mode == self.MODE_IDLE and not self.is_interacting:
            self.show_speech(random.choice(["你来啦！👋", "嘿！看这边~", "等你很久啦！"]))

    def keyPressEvent(self, event):
        """键盘快捷键"""
        key = event.key()
        if key == Qt.Key_Escape:
            self.exit_app()
        elif key == Qt.Key_Plus or key == Qt.Key_Equal:
            self.set_pet_size(self.pet_scale + 0.1)
        elif key == Qt.Key_Minus:
            self.set_pet_size(self.pet_scale - 0.1)
        elif key == Qt.Key_W:
            self.start_walking()
        elif key == Qt.Key_S:
            self.start_sleeping()
        elif key == Qt.Key_F:
            self.toggle_follow_mouse()
        elif key == Qt.Key_T:
            self.toggle_pin()
        elif key == Qt.Key_H:
            self.start_interaction("wave")
        elif key == Qt.Key_D:
            self.start_interaction("dance")

    # ============================================================
    # 交互逻辑
    # ============================================================

    def on_click(self):
        """点击角色 - 轮流触发互动"""
        self.interact_count += 1
        interactions = ["jump", "squish", "shake", "pet", "happy", "wave"]
        idx = self.interact_count % len(interactions)
        self.start_interaction(interactions[idx])

    def start_interaction(self, inter_type):
        """开始互动动画"""
        if self.is_interacting:
            return

        self.is_interacting = True
        self.interaction_type = inter_type
        self.interaction_frame = 0

        # 设置持续帧数和对话
        speech_list = INTERACTION_SPEECH.get(inter_type, [])
        if speech_list:
            text = random.choice(speech_list)
        else:
            text = self.get_random_chat()

        if inter_type == "jump":
            self.interaction_max_frame = 25
            style = "happy"
        elif inter_type == "squish":
            self.interaction_max_frame = 22
            style = "angry"
        elif inter_type == "shake":
            self.interaction_max_frame = 35
            style = "happy"
        elif inter_type == "pet":
            self.interaction_max_frame = 40
            style = "happy"
        elif inter_type == "feed":
            self.interaction_max_frame = 35
            style = "happy"
        elif inter_type == "dance":
            self.interaction_max_frame = 50
            style = "happy"
        elif inter_type == "wave":
            self.interaction_max_frame = 25
            style = "happy"
        elif inter_type == "happy":
            self.interaction_max_frame = 25
            style = "happy"
        elif inter_type == "chat":
            self.interaction_max_frame = 15
            style = "normal"
            text = self.get_random_chat()
        else:
            self.interaction_max_frame = 20
            style = "normal"

        self.show_speech(text, style)
        self.anim_timer.start()

    def get_random_chat(self):
        """获取随机聊天内容"""
        return random.choice(self.chat_messages)

    # ============================================================
    # 对话气泡
    # ============================================================

    def show_speech(self, text, style="normal"):
        """显示对话气泡"""
        if not self.bubble_enabled:
            return

        # 移除旧气泡
        if self.speech_bubble and self.speech_bubble.isVisible():
            self.speech_bubble.deleteLater()
            self.speech_bubble = None

        self.current_bubble_text = text
        self.speech_bubble = SpeechBubble(text, None, style)
        self.speech_bubble.set_position_relative_to(self.geometry())

    def show_random_speech(self):
        """自动随机显示对话"""
        if self.current_mode == self.MODE_SLEEPING:
            return
        if self.is_interacting:
            return
        if self.follow_mouse:
            return

        # 不总是说话，有概率限制
        if random.random() < 0.4:
            return

        self.show_speech(self.get_random_chat())

    # ============================================================
    # 模式切换
    # ============================================================

    def start_walking(self):
        """让宠物走路"""
        if self.is_interacting:
            return

        self.current_mode = self.MODE_WALKING
        if self.anim_timer.isActive():
            self.anim_timer.stop()

        # 随机目标位置
        screen = QApplication.primaryScreen().geometry()
        margin = 80
        tx = random.randint(margin, screen.width() - margin - self.width())
        ty = random.randint(margin, screen.height() - margin - self.height())
        self.move_target = QPoint(tx, ty)
        self.is_moving = True
        self.move_timer.start()
        self.show_speech("出门散步咯~ 🚶")

        # 随机漫步定时器
        self.random_walk_timer.start()

    def stop_moving(self):
        """停止移动"""
        self.is_moving = False
        self.move_target = None
        self.move_timer.stop()
        self.current_mode = self.MODE_IDLE
        self.update()

    def random_walk_tick(self):
        """随机漫步"""
        if self.is_moving:
            # 换个目标
            screen = QApplication.primaryScreen().geometry()
            margin = 80
            tx = random.randint(margin, screen.width() - margin - self.width())
            ty = random.randint(margin, screen.height() - margin - self.height())
            self.move_target = QPoint(tx, ty)
        else:
            self.random_walk_timer.stop()

    def start_sleeping(self):
        """让宠物睡觉"""
        if self.is_interacting:
            return

        self.current_mode = self.MODE_SLEEPING
        self.sleep_breath = 0
        self.anim_timer.start()
        self.show_speech("呼噜呼噜… 晚安~ 💤", "sleepy")

    def wake_up(self):
        """叫醒宠物"""
        if self.current_mode == self.MODE_SLEEPING:
            self.current_mode = self.MODE_IDLE
            self.anim_timer.stop()
            self.show_speech("嗯… 早上了吗？🌅", "happy")

    def toggle_follow_mouse(self, checked=None):
        """切换跟随鼠标模式"""
        if checked is not None:
            self.follow_mouse = checked
        else:
            self.follow_mouse = not self.follow_mouse

        if self.follow_mouse:
            # 停止走路
            if self.is_moving:
                self.stop_moving()
            if self.current_mode == self.MODE_SLEEPING:
                self.wake_up()

            self.show_speech("我来跟着你啦！🏃")
            self.current_mode = self.MODE_WALKING
            self.follow_timer.start()
        else:
            self.follow_timer.stop()
            self.current_mode = self.MODE_IDLE
            self.show_speech("好啦，不跟了~")
            self.update()

    def follow_mouse_update(self):
        """跟随鼠标更新"""
        cursor_pos = QCursor.pos()
        pos = self.pos()
        cx = pos.x() + self.width() // 2
        cy = pos.y() + self.height() // 2
        dx = cursor_pos.x() - cx
        dy = cursor_pos.y() - cy
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 30:
            # 太近了，不动
            return

        # 保持一定距离，不要完全挡住鼠标
        follow_dist = 60
        if dist > follow_dist:
            ratio = (dist - follow_dist) / dist
            step_x = dx * ratio * 0.15
            step_y = dy * ratio * 0.15
        else:
            return

        self.walk_direction = 1 if dx > 0 else -1
        self.walk_frame += 1

        new_pos = QPoint(int(pos.x() + step_x), int(pos.y() + step_y))
        self.move(new_pos)
        self.update()

    def toggle_pin(self, checked=None):
        """切换置顶状态"""
        if checked is not None:
            self.always_on_top = checked
        else:
            self.always_on_top = not self.always_on_top

        self.hide()
        flags = Qt.FramelessWindowHint | Qt.Tool
        if self.always_on_top:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

        if self.always_on_top:
            self.show_speech("已置顶！我就在你眼前~ 👀")
        else:
            self.show_speech("取消置顶啦~ 😴")

    def open_settings(self):
        """打开设置对话框"""
        dlg = SettingsDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            settings = dlg.get_settings()
            self.set_pet_size(settings["size"])
            self.move_speed = settings["speed"]
            self.bubble_enabled = settings["bubble_enabled"]
            if settings["image_path"]:
                self.load_new_image(settings["image_path"])

    def load_new_image(self, path):
        """加载新图片"""
        self.image_path = path
        self.load_character()
        self.show_speech("换上新衣服啦！好看吗？✨", "happy")

    def exit_app(self):
        """退出程序"""
        self.anim_timer.stop()
        self.move_timer.stop()
        self.follow_timer.stop()
        self.bubble_auto_timer.stop()
        self.random_walk_timer.stop()
        QApplication.quit()


# ============================================================
# 单实例管理器
# ============================================================

class SingleInstance:
    """使用 QSharedMemory 实现单实例"""
    def __init__(self, key):
        from PyQt5.QtCore import QSharedMemory
        self.memory = QSharedMemory(key)
        self.is_attached = False
        if self.memory.attach():
            self.is_attached = True
        else:
            self.memory.create(1)

    def has_previous(self):
        return self.is_attached


# ============================================================
# 程序入口
# ============================================================

def main():
    # 启用高DPI支持
    try:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except:
        pass

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    # 单实例检测
    # instance = SingleInstance("XiaoHaiDeskPet")
    # if instance.has_previous():
    #     print("小海桌宠已在运行！")
    #     return

    # 确定图片路径
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0] if getattr(sys, 'frozen', False) else __file__))
    img_path = os.path.join(script_dir, CHARACTER_IMAGE)

    if not os.path.exists(img_path):
        img_path = os.path.join(script_dir, FALLBACK_IMAGE)

    # 如果还是没有图，尝试自动去背景
    if not os.path.exists(img_path):
        # 查找目录中的图片
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']:
            import glob
            files = glob.glob(os.path.join(script_dir, ext))
            if files:
                img_path = files[0]
                break

    if not os.path.exists(img_path):
        QMessageBox.warning(None, "提示", "未找到角色图片，将使用默认占位图。\n请将图片放在程序同目录下。")

    pet = DesktopPet(img_path)
    pet.show()

    # 启动时打招呼
    QTimer.singleShot(500, lambda: (
        pet.show_speech(random.choice(["你好呀！我是小海桌宠~ 🦦", "嗨！欢迎使用~ 👋", "终于等到你啦！🎉"]))
    ))

    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # 写错误日志
        with open("deskpet_error.log", "w", encoding="utf-8") as f:
            f.write(f"错误: {e}\n")
            traceback.print_exc(file=f)
        print(f"小海桌宠启动失败: {e}")
        print("详情请查看 deskpet_error.log")