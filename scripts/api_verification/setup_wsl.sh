#!/bin/bash
# WSL 環境設置腳本
# 用途: 在 WSL 中設置測試環境
# 執行方式: wsl bash scripts/api_verification/setup_wsl.sh

echo "========================================="
echo "  WSL 環境設置 - EEBot API 驗證測試"
echo "========================================="

# 1. 更新套件列表
echo "[Step 1/5] 更新套件列表..."
sudo apt update

# 2. 安裝 Python3
echo "[Step 2/5] 安裝 Python3..."
sudo apt install -y python3 python3-pip python3-venv
python3 --version

# 3. 安裝 Chrome
echo "[Step 3/5] 安裝 Google Chrome..."
if ! command -v google-chrome &> /dev/null; then
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install ./google-chrome-stable_current_amd64.deb -y
    rm google-chrome-stable_current_amd64.deb
    google-chrome --version
else
    echo "Google Chrome 已安裝"
fi

# 4. 安裝 ChromeDriver
echo "[Step 4/5] 安裝 ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
echo "Chrome 版本: $CHROME_VERSION"

# 下載對應版本的 ChromeDriver（需手動調整版本）
echo "請手動下載 ChromeDriver 並放置到 /usr/local/bin/"
echo "下載連結: https://chromedriver.chromium.org/downloads"

# 5. 安裝 Python 依賴
echo "[Step 5/5] 安裝 Python 依賴..."
cd /mnt/d/Dev/eebot
pip3 install selenium requests beautifulsoup4

echo ""
echo "========================================="
echo "  ✅ WSL 環境設置完成！"
echo "========================================="
echo ""
echo "下一步:"
echo "1. 手動下載 ChromeDriver 並放到 /usr/local/bin/"
echo "2. 執行測試: python3 scripts/api_verification/test_my_courses_api.py"
echo ""
