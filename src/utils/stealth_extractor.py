#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
StealthExtractor - Stealth JS 提取器
負責提取 puppeteer-extra-plugin-stealth 的 evasion 腳本
"""

import os
import subprocess


class StealthExtractor:
    """提取 Stealth JS 腳本以繞過自動化檢測"""

    def __init__(self, output_dir: str = "resource/plugins", output_file: str = "stealth.min.js"):
        """
        初始化 Stealth 提取器

        Args:
            output_dir: 輸出目錄
            output_file: 輸出檔案名稱
        """
        self.output_dir = output_dir
        self.output_file = output_file
        self.output_path = os.path.join(output_dir, output_file)

    def run(self) -> bool:
        """
        執行提取

        Returns:
            bool: 是否成功提取
        """
        try:
            # 確保輸出目錄存在
            os.makedirs(self.output_dir, exist_ok=True)

            # 執行 npx extract-stealth-evasions
            print('[INFO] Activating automated browser stealth mode...')
            result = subprocess.run(
                ['npx', 'extract-stealth-evasions'],
                check=True,
                capture_output=True,
                text=True,
                timeout=60
            )

            # 移動生成的檔案到指定位置
            if os.path.exists("stealth.min.js"):
                # 如果目標位置已存在舊檔案，先刪除
                if os.path.exists(self.output_path):
                    os.remove(self.output_path)

                os.replace("stealth.min.js", self.output_path)
                print('[SUCCESS] Automated browser stealth mode activated')
                return True
            else:
                print('[WARN] Browser automation mode not available')
                return False

        except subprocess.TimeoutExpired:
            print('[ERROR] Stealth extraction timed out')
            return False
        except subprocess.CalledProcessError as e:
            print(f'[ERROR] Stealth extraction failed: {e}')
            if e.stderr:
                print(f'[ERROR] stderr: {e.stderr}')
            return False
        except Exception as e:
            print(f'[ERROR] Unexpected error during stealth extraction: {e}')
            return False

    def exists(self) -> bool:
        """
        檢查 Stealth JS 檔案是否存在

        Returns:
            bool: 檔案是否存在
        """
        return os.path.exists(self.output_path)

    def __repr__(self) -> str:
        return f"StealthExtractor(output_path='{self.output_path}', exists={self.exists()})"
