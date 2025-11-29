#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
ConfigLoader - 統一配置管理器
負責從配置檔案與環境變數載入設定，並提供類型安全的存取方法

支援配置來源優先級 (由高到低):
1. 環境變數 (.env 檔案或系統環境變數)
2. 配置檔案 (config/eebot.cfg)
3. 預設值
"""

import os
from typing import Optional, Any

# 嘗試載入 python-dotenv (向後相容，如果未安裝則略過)
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class ConfigLoader:
    """
    集中式配置載入器，支援環境變數與配置檔案

    環境變數命名規則:
        EEBOT_<配置鍵名大寫>

    範例:
        user_name -> EEBOT_USER_NAME
        target_http -> EEBOT_TARGET_HTTP
    """

    # 環境變數與配置鍵映射表
    ENV_KEY_MAPPING = {
        # 認證資訊
        'user_name': 'EEBOT_USERNAME',
        'password': 'EEBOT_PASSWORD',

        # 目標網站
        'target_http': 'EEBOT_TARGET_URL',

        # WebDriver 設定
        'execute_file': 'EEBOT_CHROMEDRIVER_PATH',

        # 代理伺服器設定
        'listen_host': 'EEBOT_PROXY_HOST',
        'listen_port': 'EEBOT_PROXY_PORT',

        # 瀏覽器設定
        'headless_mode': 'EEBOT_HEADLESS_MODE',
        'keep_browser_on_error': 'EEBOT_KEEP_BROWSER_ON_ERROR',

        # MitmProxy 設定
        'modify_visits': 'EEBOT_MODIFY_VISITS',
        'silent_mitm': 'EEBOT_SILENT_MITM',

        # 自動答題設定
        'enable_auto_answer': 'EEBOT_ENABLE_AUTO_ANSWER',
        'question_bank_mode': 'EEBOT_QUESTION_BANK_MODE',
        'answer_confidence_threshold': 'EEBOT_ANSWER_CONFIDENCE_THRESHOLD',
        'auto_submit_exam': 'EEBOT_AUTO_SUBMIT_EXAM',
        'screenshot_on_mismatch': 'EEBOT_SCREENSHOT_ON_MISMATCH',
        'skip_unmatched_questions': 'EEBOT_SKIP_UNMATCHED_QUESTIONS',
    }

    def __init__(self, config_file: str = "config/eebot.cfg"):
        """
        初始化配置載入器

        Args:
            config_file: 配置檔案路徑，預設為 config/eebot.cfg
        """
        self.config_file = config_file
        self._config = {}

        # 載入環境變數 (.env 檔案)
        self._load_env()

    def _load_env(self):
        """載入 .env 檔案中的環境變數"""
        if DOTENV_AVAILABLE:
            env_path = os.path.join(os.getcwd(), '.env')
            if os.path.exists(env_path):
                load_dotenv(env_path)
                print('[配置] 已載入環境變數檔案: .env')
            else:
                # 即使 .env 不存在，仍可使用系統環境變數
                load_dotenv()  # 載入系統環境變數
        else:
            # 如果 python-dotenv 未安裝，顯示提示 (不中斷執行)
            if os.path.exists('.env'):
                print('[提示] 發現 .env 檔案，但 python-dotenv 未安裝')
                print('[提示] 執行: pip install python-dotenv')

    def load(self) -> dict:
        """
        載入配置檔案

        配置檔案格式:
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
        取得配置值 (優先讀取環境變數)

        優先級:
        1. 環境變數 (EEBOT_<KEY>)
        2. 配置檔案 (eebot.cfg)
        3. 預設值

        Args:
            key: 配置鍵名
            default: 預設值（當鍵不存在時返回）

        Returns:
            配置值或預設值
        """
        # 優先級 1: 讀取環境變數
        env_key = self.ENV_KEY_MAPPING.get(key)
        if env_key:
            env_value = os.getenv(env_key)
            if env_value is not None:
                return env_value

        # 優先級 2: 讀取配置檔案
        if key in self._config:
            return self._config[key]

        # 優先級 3: 使用預設值
        return default

    def get_env(self, env_key: str, default: Any = None) -> Any:
        """
        直接讀取環境變數 (不經過映射表)

        Args:
            env_key: 環境變數名稱 (例: EEBOT_USERNAME)
            default: 預設值

        Returns:
            環境變數值或預設值
        """
        return os.getenv(env_key, default)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        取得布林值配置

        配置檔中 'y' 或 'Y' 視為 True，其他視為 False
        環境變數中 'y', 'Y', 'true', 'True', '1' 視為 True

        Args:
            key: 配置鍵名
            default: 預設值

        Returns:
            bool: 布林值
        """
        value = self.get(key, 'y' if default else 'n')

        # 支援多種布林值表示
        if isinstance(value, str):
            return value.lower() in ('y', 'yes', 'true', '1')

        return bool(value)

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
        except (ValueError, TypeError):
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """
        取得浮點數值配置

        Args:
            key: 配置鍵名
            default: 預設值

        Returns:
            float: 浮點數值
        """
        value = self.get(key, str(default))
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def has(self, key: str) -> bool:
        """
        檢查配置鍵是否存在 (檢查環境變數與配置檔案)

        Args:
            key: 配置鍵名

        Returns:
            bool: 是否存在
        """
        # 檢查環境變數
        env_key = self.ENV_KEY_MAPPING.get(key)
        if env_key and os.getenv(env_key) is not None:
            return True

        # 檢查配置檔案
        return key in self._config

    def all(self) -> dict:
        """
        取得所有配置 (合併環境變數與配置檔案)

        Returns:
            dict: 所有配置的字典
        """
        # 複製配置檔案的配置
        all_config = self._config.copy()

        # 用環境變數覆蓋 (環境變數優先)
        for cfg_key, env_key in self.ENV_KEY_MAPPING.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                all_config[cfg_key] = env_value

        return all_config

    def get_config_source(self, key: str) -> str:
        """
        取得配置來源 (用於調試)

        Args:
            key: 配置鍵名

        Returns:
            str: 'env' (環境變數) / 'file' (配置檔案) / 'none' (不存在)
        """
        env_key = self.ENV_KEY_MAPPING.get(key)
        if env_key and os.getenv(env_key) is not None:
            return 'env'

        if key in self._config:
            return 'file'

        return 'none'

    def print_config_summary(self, mask_sensitive: bool = True):
        """
        輸出配置摘要 (用於調試)

        Args:
            mask_sensitive: 是否遮蔽敏感資料 (密碼)
        """
        print('\n' + '=' * 70)
        print('[配置摘要] EEBot Configuration Summary')
        print('=' * 70)

        all_config = self.all()
        sensitive_keys = ['password', 'user_name']

        for key, value in sorted(all_config.items()):
            source = self.get_config_source(key)

            # 遮蔽敏感資料
            if mask_sensitive and key in sensitive_keys:
                display_value = '***' if value else '(未設定)'
            else:
                display_value = value

            print(f'[{source.upper():4}] {key:30} = {display_value}')

        print('=' * 70 + '\n')

    def __repr__(self) -> str:
        return f"ConfigLoader(config_file='{self.config_file}', loaded={len(self._config)} keys)"

    # ----------------------------------------------------------------
    # 以下為向後相容方法 (保持不變)
    # ----------------------------------------------------------------

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
