# API 驗證實驗 - 執行指南

> **重要**: 本實驗腳本完全使用專案現有的核心模組，確保安全性一致。

**創建日期**: 2025-12-05
**目的**: 驗證 Web Scan 與 MitmProxy API Scan 的整合可行性
**狀態**: 實驗階段（不影響現有程式碼）

---

## 📋 實驗目標

1. ✅ **獲取更多資訊** - 補充 API 獨有欄位
2. ✅ **驗證資料一致性** - 比對 Web 與 API 資料
3. ✅ **評估反偵測風險** - 確認 API 直接調用的安全性 ⭐

---

## 🔒 安全性保證

本測試腳本使用的**所有核心模組**均來自專案現有程式碼：

| 模組 | 路徑 | 用途 |
|------|------|------|
| `ConfigLoader` | `src/core/config_loader.py` | 讀取 `eebot.cfg` |
| `DriverManager` | `src/core/driver_manager.py` | WebDriver 管理 |
| `CookieManager` | `src/core/cookie_manager.py` | Cookie 載入/儲存 |
| `LoginPage` | `src/pages/login_page.py` | 登入流程 |
| `SteathExtractor` | `src/utils/stealth_extractor.py` | ⭐ 載入 `stealth.min.js` |

**保證**:
- ✅ 使用與 `main.py` 相同的登入流程
- ✅ 自動載入 `stealth.min.js` 反偵測腳本
- ✅ 讀取 `eebot.cfg` 配置
- ✅ 支援手動輸入驗證碼

---

## 🖥️ 執行環境選擇

### 方案 A: WSL 執行（推薦）✅

**優點**: 與 Windows 隔離，安全性更高

**前提要求**:
```bash
# 1. 確認 WSL 已安裝
wsl --version

# 2. 進入 WSL
wsl

# 3. 安裝 Chrome (如果尚未安裝)
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

# 4. 安裝 ChromeDriver (需與 Chrome 版本匹配)
# 查看 Chrome 版本
google-chrome --version

# 下載對應版本的 ChromeDriver
# https://chromedriver.chromium.org/downloads

# 5. 確認專案路徑可訪問
cd /mnt/d/Dev/eebot  # 從 WSL 訪問 D:\Dev\eebot
```

**執行方式**:
```bash
# 在 WSL 中執行
cd /mnt/d/Dev/eebot
python3 scripts/api_verification/test_my_courses_api.py
```

---

### 方案 B: Windows 執行（備選）

**優點**: 可視化操作，輸入驗證碼更方便

**執行方式**:
```powershell
# 在 Windows CMD/PowerShell 中執行
cd D:\Dev\eebot
python scripts\api_verification\test_my_courses_api.py
```

---

## 📦 依賴套件

本測試腳本使用的所有套件均為專案現有依賴，無需額外安裝：

```txt
selenium
requests
beautifulsoup4
```

如果需要確認：
```bash
pip install -r requirements.txt
```

---

## 🚀 執行流程

### Step 1: 準備配置

確認 `config/eebot.cfg` 設置正確：

```ini
[SETTINGS]
target_http = https://elearn.post.gov.tw
execute_file = D:/chromedriver.exe        # Windows
# execute_file = /usr/bin/chromedriver    # WSL/Linux
user_name = your_username
password = your_password
```

---

### Step 2: 執行 API 結構驗證

```bash
python scripts/api_verification/test_my_courses_api.py
```

**流程**:
1. 自動載入 `stealth.min.js` ✅
2. 啟動瀏覽器（使用 `DriverManager`）
3. 自動填入帳號密碼
4. **等待您手動輸入驗證碼** ⏸️
5. 登入成功後，提取 Session Cookie
6. 調用 `GET /api/my-courses`
7. 儲存原始回應並分析結構

**輸出**:
- `results/api_response.json` - API 原始回應
- `results/api_structure_analysis.md` - 結構分析報告

**預計時間**: 2-3 分鐘（含手動驗證碼）

---

### Step 3: 執行反偵測風險評估 ⭐ 關鍵

```bash
python scripts/api_verification/test_api_security.py
```

**流程**:
1. 使用步驟 2 獲得的 Session Cookie
2. 執行 5 種測試場景:
   - Scenario 1: 使用 Selenium Cookie（基準測試）
   - Scenario 2: 純 requests 調用（模擬 API 直接調用）
   - Scenario 3: 高頻請求測試（10次/分鐘）
   - Scenario 4: 缺少請求頭測試
   - Scenario 5: 延遲測試（模擬真實行為）
3. 評估伺服器反偵測機制
4. 生成風險評估報告

**輸出**:
- `results/security_assessment.md` - 風險評估報告
- **包含：是否建議使用 API 直接調用模式**

**預計時間**: 3-5 分鐘

---

### Step 4: 執行資料一致性比對

```bash
python scripts/api_verification/compare_web_vs_api.py
```

**流程**:
1. 讀取 `data/courses.json`（Web Scan 資料）
2. 讀取 `results/api_response.json`（API Scan 資料）
3. 比對資料一致性
4. 生成欄位對應表

**輸出**:
- `results/field_mapping.json` - 欄位對應表
- `results/consistency_report.md` - 一致性報告

**預計時間**: 1 分鐘

---

## 📊 預期產出

執行完成後，`results/` 目錄將包含：

```
results/
├── api_response.json              # API 原始回應
├── api_structure_analysis.md      # 結構分析
├── security_assessment.md         # ⭐ 風險評估報告
├── field_mapping.json             # 欄位對應表
└── consistency_report.md          # 一致性報告
```

**關鍵報告**: `security_assessment.md`

此報告將明確指出：
- 🟢 **綠燈**: 可安全使用 API 直接調用
- 🟡 **黃燈**: 謹慎使用，需要緩解措施
- 🔴 **紅燈**: 不建議使用 API 直接調用

---

## 🐛 故障排除

### 問題 1: stealth.min.js 未找到

**錯誤訊息**:
```
[ERROR] stealth.min.js not found
```

**解決方案**:
```bash
# 使用專案的 SteathExtractor 提取
python -c "from src.utils.stealth_extractor import extract_stealth; extract_stealth()"
```

---

### 問題 2: ChromeDriver 版本不匹配

**錯誤訊息**:
```
SessionNotCreatedException: session not created: This version of ChromeDriver only supports Chrome version XX
```

**解決方案**:
```bash
# 1. 查看 Chrome 版本
google-chrome --version  # Linux/WSL
# 或在 Windows: 開啟 Chrome → 設定 → 關於 Chrome

# 2. 下載對應版本的 ChromeDriver
# https://chromedriver.chromium.org/downloads

# 3. 更新 eebot.cfg 中的 execute_file 路徑
```

---

### 問題 3: 無法訪問網站

**錯誤訊息**:
```
[ERROR] Failed to connect to https://elearn.post.gov.tw
```

**可能原因**:
- 網路連線問題
- VPN 或防火牆阻擋
- 網站維護中

**解決方案**:
- 確認可直接在瀏覽器中訪問網站
- 檢查網路連線
- 稍後再試

---

### 問題 4: Cookie 無效

**錯誤訊息**:
```
[ERROR] Session Cookie expired or invalid
```

**解決方案**:
```bash
# 重新執行 Step 2，重新登入並獲取新的 Cookie
python scripts/api_verification/test_my_courses_api.py
```

---

## ⚠️ 重要提醒

### 執行前
1. ✅ 確認 `eebot.cfg` 配置正確
2. ✅ 確認 ChromeDriver 版本匹配
3. ✅ 確認網路連線正常
4. ✅ 準備好手動輸入驗證碼

### 執行中
1. ⏸️ 當瀏覽器彈出時，**手動輸入驗證碼**
2. ⏸️ 等待腳本自動完成後續流程
3. ⏸️ **不要關閉終端機視窗**

### 執行後
1. 📊 查看 `results/security_assessment.md` 決定下一步
2. 📝 根據報告決定是否繼續 API 整合開發
3. 🗑️ 可選：清理 `results/` 目錄（如需重新測試）

---

## 🔐 隱私與安全

### 資料儲存
- ✅ 所有 API 回應儲存在本地 `results/` 目錄
- ✅ 不會上傳到任何遠端伺服器
- ✅ Session Cookie 僅用於測試，不會外洩

### 敏感資訊處理
- ⚠️ `api_response.json` 可能包含個人資訊
- ⚠️ 建議測試完成後檢查並移除敏感資訊
- ⚠️ **不要將 `results/` 目錄提交到 Git**

### 已添加到 .gitignore
```gitignore
# API 驗證實驗結果
scripts/api_verification/results/*.json
scripts/api_verification/results/*.md
```

---

## 📞 支援

如果遇到問題：
1. 查看本文檔的故障排除章節
2. 檢查 `results/` 目錄中的錯誤日誌
3. 聯繫專案維護者

---

## 📝 後續步驟

### 如果風險評估為 🟢 綠燈
→ 進入 Phase 2: 整合實作
→ 開發 `src/utils/course_scanner.py`
→ 在 `courses.json` 中添加 API 欄位

### 如果風險評估為 🟡 黃燈
→ 評估緩解措施的可行性
→ 實作頻率控制、延遲機制
→ 重新評估風險

### 如果風險評估為 🔴 紅燈
→ 停止 API 直接調用計畫
→ 改用混合模式（Selenium + MitmProxy 被動攔截）
→ 更新專案文檔

---

**最後更新**: 2025-12-05
**維護者**: wizard03
**專案**: EEBot (Gleipnir) v2.0.7
