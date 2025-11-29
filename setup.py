#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EEBot 配置工具 - CLI 配置管理工具

功能:
- init: 初始化環境變數配置檔案
- set: 設定特定配置項 (帳號/密碼/其他)
- show: 顯示當前配置 (密碼遮蔽)
- validate: 驗證配置完整性
- test: 測試登入連線

使用範例:
    python setup.py init              # 初始化 .env 檔案
    python setup.py set username      # 設定帳號
    python setup.py set password      # 設定密碼
    python setup.py show              # 顯示配置
    python setup.py validate          # 驗證配置
    python setup.py test              # 測試連線
"""

import os
import sys
import getpass
import shutil


def print_header(title):
    """輸出標題"""
    print('\n' + '=' * 70)
    print(f' {title}')
    print('=' * 70 + '\n')


def print_success(message):
    """輸出成功訊息"""
    print(f'\u2713 {message}')


def print_error(message):
    """輸出錯誤訊息"""
    print(f'\u2717 {message}')


def print_warning(message):
    """輸出警告訊息"""
    print(f'\u26a0 {message}')


def check_dotenv_installed():
    """檢查 python-dotenv 是否已安裝"""
    try:
        import dotenv
        return True
    except ImportError:
        return False


def init_env_file():
    """初始化 .env 檔案"""
    print_header('初始化環境變數配置檔案')

    # 檢查 .env 是否已存在
    if os.path.exists('.env'):
        confirm = input('.env 檔案已存在，是否覆蓋? (y/n): ')
        if confirm.lower() != 'y':
            print_warning('已取消初始化')
            return

        # 備份現有 .env
        backup_path = '.env.backup'
        shutil.copy('.env', backup_path)
        print_success(f'已備份現有配置至: {backup_path}')

    # 檢查 .env.example 是否存在
    if not os.path.exists('.env.example'):
        print_error('.env.example 範本檔案不存在！')
        print('請確保專案包含 .env.example 範本檔案')
        return

    # 複製 .env.example 為 .env
    shutil.copy('.env.example', '.env')
    print_success('.env 檔案已建立')

    print('\n下一步:')
    print('  1. 執行: python setup.py set username')
    print('  2. 執行: python setup.py set password')
    print('  3. 或直接編輯 .env 檔案設定您的帳號密碼')


def set_env_value(key, value, description=''):
    """設定環境變數值到 .env 檔案"""
    if not os.path.exists('.env'):
        print_error('.env 檔案不存在，請先執行: python setup.py init')
        return False

    # 讀取現有 .env
    with open('.env', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 尋找並更新目標鍵值
    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f'{key}='):
            lines[i] = f'{key}={value}\n'
            found = True
            break

    # 如果找不到，則新增
    if not found:
        lines.append(f'\n# {description}\n' if description else '\n')
        lines.append(f'{key}={value}\n')

    # 寫回 .env
    with open('.env', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    return True


def set_credential(credential_type):
    """設定認證資訊 (帳號或密碼)"""
    print_header(f'設定 {"帳號" if credential_type == "username" else "密碼"}')

    if credential_type == 'username':
        value = input('請輸入帳號: ')
        key = 'EEBOT_USERNAME'
    else:  # password
        value = getpass.getpass('請輸入密碼 (輸入時不顯示): ')
        confirm = getpass.getpass('請再次輸入密碼確認: ')

        if value != confirm:
            print_error('兩次密碼輸入不一致！')
            return

        key = 'EEBOT_PASSWORD'

    # 設定到 .env
    if set_env_value(key, value):
        print_success(f'{"帳號" if credential_type == "username" else "密碼"}已設定完成')
        print(f'設定儲存於: .env (已被 Git 忽略)')


def show_config():
    """顯示當前配置"""
    print_header('當前配置摘要')

    # 檢查 python-dotenv 是否安裝
    if not check_dotenv_installed():
        print_warning('python-dotenv 未安裝，請執行: pip install python-dotenv')
        print('將嘗試直接讀取 .env 檔案...\n')

        if not os.path.exists('.env'):
            print_error('.env 檔案不存在')
            return

        # 手動讀取 .env
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if 'PASSWORD' in key.upper():
                        display_value = '***' if value else '(未設定)'
                    else:
                        display_value = value if value else '(未設定)'
                    print(f'{key:35} = {display_value}')
        return

    # 使用 ConfigLoader 載入配置
    try:
        from src.core.config_loader import ConfigLoader

        config = ConfigLoader()
        config.load()
        config.print_config_summary(mask_sensitive=True)

    except Exception as e:
        print_error(f'載入配置失敗: {e}')


def validate_config():
    """驗證配置完整性"""
    print_header('驗證配置完整性')

    required_keys = ['EEBOT_USERNAME', 'EEBOT_PASSWORD']
    missing_keys = []
    valid = True

    # 檢查 .env 是否存在
    if not os.path.exists('.env'):
        print_error('.env 檔案不存在')
        print('請先執行: python setup.py init')
        return

    # 讀取 .env
    env_vars = {}
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value

    # 檢查必填欄位
    print('檢查必填欄位:')
    for key in required_keys:
        if key not in env_vars or not env_vars[key]:
            print_error(f'  {key}: 未設定')
            missing_keys.append(key)
            valid = False
        else:
            print_success(f'  {key}: 已設定')

    # 檢查 config/eebot.cfg
    print('\n檢查配置檔案:')
    if os.path.exists('config/eebot.cfg'):
        print_success('  config/eebot.cfg: 存在')
    else:
        print_warning('  config/eebot.cfg: 不存在 (將使用預設值)')

    # 檢查 python-dotenv
    print('\n檢查依賴套件:')
    if check_dotenv_installed():
        print_success('  python-dotenv: 已安裝')
    else:
        print_warning('  python-dotenv: 未安裝')
        print('  執行: pip install python-dotenv')
        valid = False

    # 總結
    print('\n' + '=' * 70)
    if valid:
        print_success('配置驗證通過！')
        print('\n您可以執行以下指令啟動 EEBot:')
        print('  python menu.py    # 互動式選單')
        print('  python main.py    # 直接執行')
    else:
        print_error('配置驗證失敗，請修正以上問題')
        if missing_keys:
            print('\n缺少的配置項:')
            for key in missing_keys:
                if 'USERNAME' in key:
                    print('  執行: python setup.py set username')
                elif 'PASSWORD' in key:
                    print('  執行: python setup.py set password')
    print('=' * 70)


def test_connection():
    """測試登入連線"""
    print_header('測試登入連線')

    print_warning('此功能尚未實作')
    print('未來版本將提供快速測試登入功能')


def print_usage():
    """輸出使用說明"""
    print('''
EEBot 配置工具

使用方式:
    python setup.py <command>

可用指令:
    init            初始化 .env 環境變數檔案
    set username    設定帳號
    set password    設定密碼
    show            顯示當前配置 (密碼遮蔽)
    validate        驗證配置完整性
    test            測試登入連線 (尚未實作)
    help            顯示此說明

範例:
    # 快速設定流程
    python setup.py init             # 1. 建立 .env 檔案
    python setup.py set username     # 2. 設定帳號
    python setup.py set password     # 3. 設定密碼
    python setup.py validate         # 4. 驗證配置
    python main.py                   # 5. 執行 EEBot

    # 查看配置
    python setup.py show

注意事項:
    - .env 檔案已被 Git 忽略，不會被提交到版本控制
    - 環境變數優先級高於 config/eebot.cfg
    - 建議敏感資料 (帳號密碼) 使用 .env，其他配置使用 eebot.cfg
    ''')


def main():
    """主程式入口"""
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    if command == 'init':
        init_env_file()

    elif command == 'set':
        if len(sys.argv) < 3:
            print_error('請指定要設定的項目 (username/password)')
            print('範例: python setup.py set username')
            return

        item = sys.argv[2].lower()
        if item in ['username', 'user', 'account']:
            set_credential('username')
        elif item in ['password', 'pass', 'pwd']:
            set_credential('password')
        else:
            print_error(f'不支援的設定項目: {item}')
            print('可用項目: username, password')

    elif command == 'show':
        show_config()

    elif command == 'validate':
        validate_config()

    elif command == 'test':
        test_connection()

    elif command in ['help', '--help', '-h']:
        print_usage()

    else:
        print_error(f'未知的指令: {command}')
        print('執行 python setup.py help 查看使用說明')


if __name__ == '__main__':
    main()
