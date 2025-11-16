#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
ConfigLoader - 統一配置管理器
負責從配置檔案載入設定，並提供類型安全的存取方法
"""

import os
from typing import Optional, Any


class ConfigLoader:
    """集中式配置載入器，支援從 .cfg 檔案讀取配置"""

    def __init__(self, config_file: str = "config/eebot.cfg"):
        """
        初始化配置載入器

        Args:
            config_file: 配置檔案路徑，預設為 config/eebot.cfg
        """
        self.config_file = config_file
        self._config = {}

    def load(self) -> dict:
        """
        載入配置檔案

        配置檔案格式：
            key=value
            # 註解行

        Returns:
            dict: 配置字典

        Raises:
            FileNotFoundError: 當配置檔案不存在時
        """
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")

        with open(self.config_file, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()

                # 跳過空行、註解和無效行
                if not line or line.startswith('#') or '=' not in line:
                    continue

                # 分割 key=value
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")

                self._config[k] = v

        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """
        取得配置值

        Args:
            key: 配置鍵名
            default: 預設值（當鍵不存在時返回）

        Returns:
            配置值或預設值
        """
        return self._config.get(key, default)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        取得布林值配置

        配置檔中 'y' 或 'Y' 視為 True，其他視為 False

        Args:
            key: 配置鍵名
            default: 預設值

        Returns:
            bool: 布林值
        """
        value = self.get(key, 'y' if default else 'n')
        return value.lower() == 'y'

    def get_int(self, key: str, default: int = 0) -> int:
        """
        取得整數值配置

        Args:
            key: 配置鍵名
            default: 預設值

        Returns:
            int: 整數值
        """
        value = self.get(key, str(default))
        try:
            return int(value)
        except ValueError:
            return default

    def has(self, key: str) -> bool:
        """
        檢查配置鍵是否存在

        Args:
            key: 配置鍵名

        Returns:
            bool: 是否存在
        """
        return key in self._config

    def all(self) -> dict:
        """
        取得所有配置

        Returns:
            dict: 所有配置的字典
        """
        return self._config.copy()

    def __repr__(self) -> str:
        return f"ConfigLoader(config_file='{self.config_file}', loaded={len(self._config)} keys)"

    def load_timing_config(self, timing_config_path: str = 'config/timing.json') -> dict:
        """
        載入時間延遲與截圖配置

        Args:
            timing_config_path: timing.json 路徑

        Returns:
            dict: 配置字典
        """
        import json

        try:
            with open(timing_config_path, 'r', encoding='utf-8-sig') as f:
                timing_config = json.load(f)
            print(f'[配置] 已載入時間配置: {timing_config_path}')
            return timing_config
        except FileNotFoundError:
            print(f'[警告] 找不到 {timing_config_path}，使用預設值')
            return self._get_default_timing_config()
        except Exception as e:
            print(f'[錯誤] 載入時間配置失敗: {e}')
            return self._get_default_timing_config()

    @staticmethod
    def _get_default_timing_config() -> dict:
        """預設時間配置"""
        return {
            "delays": {
                "stage_1_course_list": 3.0,
                "stage_2_program_detail": 11.0,
                "stage_3_lesson_detail": 7.0,
                "stage_2_exam": 7.0
            },
            "screenshot": {
                "enabled": False,
                "base_directory": "screenshots"
            }
        }
