# -*- coding: utf-8 -*-
"""
截圖管理器
支援在右下角添加時間戳的網頁截圖功能

Created: 2025-01-16
Author: wizard03 (with Claude Code CLI)
"""

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os


class ScreenshotManager:
    """截圖管理器 - 支援右下角時間戳"""

    def __init__(self, config_loader, timing_config: dict):
        """
        初始化截圖管理器

        Args:
            config_loader: ConfigLoader 實例 (用於讀取 user_name)
            timing_config: timing.json 配置字典
        """
        screenshot_config = timing_config.get('screenshot', {})

        self.enabled = screenshot_config.get('enabled', False)
        self.base_dir = screenshot_config.get('base_directory', 'screenshots')
        self.organize_by_user = screenshot_config.get('organize_by_user', True)
        self.organize_by_date = screenshot_config.get('organize_by_date', True)
        self.date_format = screenshot_config.get('date_format', '%Y-%m-%d')
        self.timestamp_format = screenshot_config.get('timestamp_format', '%Y-%m-%d %H:%M:%S')
        self.filename_timestamp = screenshot_config.get('filename_timestamp', '%y%m%d%H%M')

        # 字體設定
        font_settings = screenshot_config.get('font_settings', {})
        self.font_size = font_settings.get('size', 48)
        self.font_color = font_settings.get('color', '#FFFFFF')
        self.bg_color = font_settings.get('background_color', '#000000')
        self.bg_opacity = font_settings.get('background_opacity', 180)
        self.margin = font_settings.get('margin', 20)

        # 從 eebot.cfg 讀取 user_name
        self.username = config_loader.get('user_name', 'unknown_user')

        if self.enabled:
            print('[截圖] 截圖功能已啟用')
            print(f'  使用者: {self.username}')
            print(f'  基礎路徑: {self.base_dir}')

    def _get_save_directory(self) -> str:
        """
        取得儲存目錄路徑（自動建立）

        Returns:
            str: 完整的儲存目錄路徑
        """
        path_parts = [self.base_dir]

        # 第一層：使用者名稱
        if self.organize_by_user:
            path_parts.append(self.username)

        # 第二層：日期
        if self.organize_by_date:
            date_str = datetime.now().strftime(self.date_format)
            path_parts.append(date_str)

        save_dir = os.path.join(*path_parts)

        # 確保目錄存在
        os.makedirs(save_dir, exist_ok=True)

        return save_dir

    def take_screenshot(self, driver, lesson_name: str, sequence: int) -> str:
        """
        截取網頁並在右下角添加時間戳

        Args:
            driver: Selenium WebDriver
            lesson_name: 課程名稱（用於檔名）
            sequence: 序號（1 或 2）

        Returns:
            str: 截圖檔案路徑，若未啟用則返回 None
        """
        if not self.enabled:
            return None

        # 取得儲存目錄
        save_dir = self._get_save_directory()

        # 生成檔名
        timestamp_str = datetime.now().strftime(self.filename_timestamp)
        filename = f"{lesson_name}_{timestamp_str}-{sequence}.jpg"
        filepath = os.path.join(save_dir, filename)

        # Step 1: Selenium 截圖到臨時檔案
        temp_path = filepath.replace('.jpg', '_temp.png')

        try:
            driver.save_screenshot(temp_path)

            # Step 2: 使用 PIL 添加時間戳
            img = Image.open(temp_path)
            draw = ImageDraw.Draw(img)

            # 載入字體
            font = self._load_font()

            # 準備時間文字
            datetime_text = datetime.now().strftime(self.timestamp_format)

            # 計算文字邊界框
            bbox = draw.textbbox((0, 0), datetime_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 計算右下角位置
            x = img.width - text_width - self.margin
            y = img.height - text_height - self.margin

            # 繪製半透明背景
            bg_padding = 10
            draw.rectangle(
                [
                    x - bg_padding,
                    y - bg_padding,
                    x + text_width + bg_padding,
                    y + text_height + bg_padding
                ],
                fill=self._hex_to_rgba(self.bg_color, self.bg_opacity)
            )

            # 繪製時間文字
            draw.text((x, y), datetime_text, fill=self.font_color, font=font)

            # 儲存為 JPEG
            img.convert('RGB').save(filepath, 'JPEG', quality=95)

            # 刪除臨時檔案
            if os.path.exists(temp_path):
                os.remove(temp_path)

            # 顯示相對路徑（更清晰）
            relative_path = os.path.relpath(filepath, self.base_dir)
            print(f'  ✅ 截圖已儲存: {self.base_dir}/{relative_path}')

            return filepath

        except Exception as e:
            print(f'  ❌ 截圖失敗: {e}')
            # 如果處理失敗，至少保留原始截圖
            if os.path.exists(temp_path):
                try:
                    os.rename(temp_path, filepath)
                    print(f'  ⚠️  已保留原始截圖（無時間戳）: {filename}')
                    return filepath
                except:
                    pass
            return None

    def _load_font(self):
        """載入字體（支援 Windows 與 Linux）"""
        # 字體搜尋順序列表
        font_paths = [
            # Windows 字體
            "C:/Windows/Fonts/msyh.ttc",          # 微軟雅黑（支援中文）
            "C:/Windows/Fonts/arial.ttf",         # Arial

            # Linux 字體（支援中文）
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",           # 文泉驛正黑
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", # Noto Sans CJK
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/arphic/uming.ttc",             # AR PL UMing

            # Linux 字體（通用拉丁字母）
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",

            # macOS 字體
            "/System/Library/Fonts/PingFang.ttc",     # 蘋方（支援中文）
            "/Library/Fonts/Arial.ttf",

            # 相對路徑
            "arial.ttf",
        ]

        # 嘗試載入字體
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, self.font_size)
                print(f'[截圖] 已載入字體: {font_path}')
                return font
            except (OSError, IOError):
                continue

        # 所有字體都失敗，使用預設字體
        print('[警告] 無法載入任何 TrueType 字體，使用預設字體')
        print('[提示] 在 Linux 上可安裝字體：')
        print('       sudo apt-get install fonts-wqy-zenhei')
        print('       或 sudo apt-get install fonts-noto-cjk')
        return ImageFont.load_default()

    @staticmethod
    def _hex_to_rgba(hex_color: str, opacity: int):
        """將 HEX 顏色轉為 RGBA"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (r, g, b, opacity)
