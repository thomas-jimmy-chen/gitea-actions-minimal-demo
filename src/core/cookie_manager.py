#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
CookieManager - Cookie 管理器
負責 Cookie 的載入、儲存與管理
"""

import os
import json
from typing import List, Dict, Any


class CookieManager:
    """處理 Cookie 的存取邏輯"""

    def __init__(self, cookie_file: str = "cookies.json", base_dir: str = "resource/cookies"):
        """
        初始化 Cookie 管理器

        Args:
            cookie_file: Cookie 檔案名稱
            base_dir: Cookie 檔案儲存目錄
        """
        self.cookie_path = os.path.join(base_dir, cookie_file)
        self._ensure_directory()

    def _ensure_directory(self):
        """確保 Cookie 目錄存在"""
        os.makedirs(os.path.dirname(self.cookie_path), exist_ok=True)

    def load(self) -> List[Dict[str, Any]]:
        """
        載入 Cookies

        Returns:
            List[Dict]: Cookie 列表，若檔案不存在則返回空列表
        """
        if not os.path.exists(self.cookie_path):
            return []

        try:
            with open(self.cookie_path, 'r', encoding='utf-8-sig') as f:
                cookies = json.load(f)
                return cookies if isinstance(cookies, list) else []
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARN] Failed to load cookies from {self.cookie_path}: {e}")
            return []

    def save(self, cookies: List[Dict[str, Any]]):
        """
        儲存 Cookies

        Args:
            cookies: Cookie 列表
        """
        try:
            with open(self.cookie_path, 'w', encoding='utf-8-sig') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[ERROR] Failed to save cookies to {self.cookie_path}: {e}")

    def exists(self) -> bool:
        """
        檢查 Cookie 檔案是否存在

        Returns:
            bool: 檔案是否存在
        """
        return os.path.exists(self.cookie_path)

    def clear(self):
        """刪除 Cookie 檔案"""
        if os.path.exists(self.cookie_path):
            try:
                os.remove(self.cookie_path)
            except OSError as e:
                print(f"[ERROR] Failed to delete cookie file: {e}")

    def __repr__(self) -> str:
        return f"CookieManager(cookie_path='{self.cookie_path}', exists={self.exists()})"
