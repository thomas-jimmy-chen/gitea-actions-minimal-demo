# EEBot - Claude Code CLI 交接文檔 (第 1 段)

> **分段資訊**: 本文檔共 2 段
> - 📄 **當前**: 第 1 段 - 基礎架構與使用指南
> - ➡️ **下一段**: [CLAUDE_CODE_HANDOVER-2.md](./CLAUDE_CODE_HANDOVER-2.md) - 進階功能詳解
> - 📑 **完整索引**: [返回索引](./CLAUDE_CODE_HANDOVER.md)

---

> **專為 Claude Code CLI 優化的項目交接文檔**
>
> 本文檔使用 Claude Code 的最佳實踐格式編寫，方便快速理解項目結構並進行後續開發。

**文檔版本**: 2.0
**最後更新**: 2025-11-24（課程配置優化討論 + 工作日誌規範化）
**項目版本**: 2.0.5
**項目代號**: **Gleipnir** (格萊普尼爾 / 縛狼鎖)
**維護者**: wizard03

---

## 🔗 項目代號：Gleipnir (格萊普尼爾)

北歐神話中用來綑綁魔狼芬里爾 (Fenrir) 的鎖鏈。由矮人工匠用六種不可能的材料鍛造而成，看似輕盈如絲卻牢不可破。

**寓意**:
- **糾纏者 (Entangler)**: 如同此鎖鏈綑綁芬里爾，本工具精準控制複雜的學習流程
- **欺詐者 (Deceiver)**: 外表簡潔優雅的 API 隱藏著複雜的自動化邏輯
- **縛狼鎖**: 象徵系統的可靠性與不可破壞的自動化能力

---

## 🎯 快速開始 (Quick Start for Claude)

### 閱讀本文檔前
1. 使用 `@workspace` 索引整個項目（建議）
2. 閱讀本文檔獲取項目概覽
3. 查看 `CHANGELOG.md` 了解最新修改（歷史版本見 `docs/changelogs/`）

### 關鍵文件路徑
```
D:\Dev\eebot\
├── .env                       ← 環境變數配置（敏感資料，Git ignore）⭐ NEW v2.0.7
├── .env.example               ← 環境變數範本 ⭐ NEW v2.0.7
├── setup.py                   ← CLI 配置工具 ⭐ NEW v2.0.7
├── data/courses.json          ← 課程配置（最重要！）
├── main.py                    ← 程式入口
├── menu.py                    ← 互動式選單
├── config/eebot.cfg           ← 系統配置檔案
├── src/
│   ├── core/
│   │   └── config_loader.py   ← 配置載入器（支援環境變數）⭐ UPDATED v2.0.7
│   ├── scenarios/             ← 業務流程層
│   │   ├── course_learning.py ← 課程流程（原有，勿改）
│   │   └── exam_learning.py   ← 考試流程（2025-01-13 新增）
│   ├── pages/                 ← 頁面操作層 (POM)
│   │   ├── exam_detail_page.py    ← 考試頁面（2025-01-13 新增）
│   │   ├── course_list_page.py    ← 課程列表（原有，勿改）
│   │   └── course_detail_page.py  ← 課程詳情（原有，勿改）
│   └── utils/                 ← 工具類別
│       ├── time_tracker.py        ← 時間追蹤器（2025-01-17 新增）
│       ├── screenshot_utils.py    ← 截圖管理器
│       └── stealth_extractor.py   ← 反檢測工具
├── reports/                   ← 時間統計報告（自動生成）
└── docs/                      ← 項目文檔
    ├── CONFIGURATION_MANAGEMENT_GUIDE.md  ← 配置管理指南 ⭐ NEW v2.0.7
    ├── changelogs/            ← CHANGELOG 歷史歸檔
    │   └── CHANGELOG_archive_2025.md  ← 2025 年歷史版本
    ├── AI_ASSISTANT_GUIDE.md  ← 通用 AI 助手文檔
    └── CHANGELOG.md           ← 修改歷史記錄（最新版本）
```

### ⭐ 配置管理快速指南 (v2.0.7)

**環境變數配置**（推薦用於敏感資料）:
```bash
# 快速設定
python setup.py init             # 1. 建立 .env
python setup.py set username     # 2. 設定帳號
python setup.py set password     # 3. 設定密碼
python setup.py validate         # 4. 驗證配置
```

**配置來源優先級**:
```
1. 環境變數 (.env 或系統環境變數)  [最高優先級]
2. 配置檔案 (config/eebot.cfg)
3. 程式預設值                      [最低優先級]
```

**完整文檔**: 請閱讀 [CONFIGURATION_MANAGEMENT_GUIDE.md](./CONFIGURATION_MANAGEMENT_GUIDE.md) ⭐ **必讀**

---

## 📖 項目概述

### 項目資訊
- **名稱**: EEBot (Elearn Automation Bot)
- **用途**: 台灣郵政 e 大學自動化學習機器人
- **目標網站**: https://elearn.post.gov.tw
- **主要語言**: Python 3.x
- **核心框架**: Selenium WebDriver + MitmProxy

### 架構模式
```
POM (Page Object Model) + API Interceptor
├── Core Layer       (核心基礎設施)
├── Pages Layer      (頁面物件模型)
├── Scenarios Layer  (業務流程編排)
└── API Layer        (HTTP 請求攔截)
```

### 工作原理
1. **自動登入**: 使用 Cookies 或帳密登入（支援 3 次重試）⭐ NEW (2025-11-17)
2. **課程/考試選擇**: 根據 `data/courses.json` 配置
3. **自動瀏覽**: Selenium 模擬用戶操作
4. **時長修改**: MitmProxy 攔截並修改訪問時長（配置外部化）⭐ NEW (2025-11-17)
5. **智能答題**: 題目文字 + 選項內容雙重比對
6. **完成學習**: 自動完成課程或考試流程
7. **一鍵執行**: 自動掃描、排程、執行所有「修習中」課程（雙層去重）⭐ NEW (2025-11-17)
8. **跨平台截圖**: 支援 Windows/Linux/macOS 字體
9. **時間統計**: 完整追蹤執行時間並生成報告 (2025-01-17)
10. **蟲洞提示**: 在關鍵階段顯示時間加速狀態 ⭐ NEW (2025-11-17)

### ⭐ 最新功能 (2025-11-17)

**穩定性與配置優化（v2.0.5）**

本次更新專注於提升系統穩定性、改善配置管理架構，並優化使用者體驗。

**核心特點**:
- 🔄 **登入重試機制**: 驗證碼錯誤時自動重試（最多 3 次）
- 🛡️ **雙層去重保護**: 掃描階段 + 排程階段雙重防護
- ⚙️ **配置外部化**: 統一配置管理，移除 hardcoded 值
- ⏰ **蟲洞顯示優化**: 在關鍵階段透明化顯示時間加速效果

**1. 登入重試機制強化**
```python
# 智能推薦、課程場景、考試場景全部支援
max_retries = 3
for attempt in range(max_retries):
    if login_success:
        break
    else:
        # 刷新頁面獲取新驗證碼
        login_page.goto(config.get('target_http'))
```

**2. 排程去重機制（雙層保護）**
- **第一層**: 掃描階段使用 `set()` 防止 DOM 重複元素
- **第二層**: 加入排程階段檢查現有排程避免重複
- 考試與課程使用不同的比對邏輯

**3. MitmProxy 配置外部化**
```ini
# config/eebot.cfg
visit_duration_increase = 9000  # 統一管理
```
- 採用「單一數據源」設計模式
- Default 值只在 `main.py` 一處
- 使用依賴注入傳遞配置

**4. 蟲洞功能顯示優化**
在三個關鍵階段顯示：
- 第二階 - 進入時（截圖後）
- 第三階 - 進入時（選擇課程單元後）
- 第二階 - 返回時（返回課程計畫後）

**修改檔案**:
1. `menu.py` - 登入重試 + 排程去重
2. `src/scenarios/course_learning.py` - 登入重試 + 配置參數 + 蟲洞顯示
3. `src/scenarios/exam_learning.py` - 登入重試 + 配置參數
4. `src/pages/course_list_page.py` - 掃描階段去重
5. `config/eebot.cfg` - 新增配置參數
6. `main.py` - 統一配置讀取與傳遞

**向後相容**:
- ✅ 所有原有功能不受影響
- ✅ 配置值向後相容（預設 9000 秒）
- ✅ 蟲洞顯示可隨 `modify_visits` 開關

**詳細記錄**:
- 查看 `CHANGELOG.md` 了解完整技術細節
- 查看 `docs/DAILY_WORK_LOG_20251117.md` 了解開發過程

---

### ⭐ 最新功能 (2025-01-17) - 第三更新

**完整時間統計系統 + 產品化輸出訊息**

新增完整的時間追蹤與統計功能，精確記錄程式執行的每個階段、每個課程/考試的時間，並生成詳細報告。

**核心特點**:
- ⏱️ **全方位追蹤**: 程式總時間、階段時間、課程時間、考試時間
- 📊 **智能分類**: 區分淨執行時間、延遲時間、使用者等待時間
- 📈 **階層統計**: 課程計畫分組 → 課程/考試明細 → 時間明細
- 🖥️ **雙重輸出**: 螢幕格式化報告 + Markdown 文件報告
- 📁 **自動保存**: 報告自動保存到 `reports/` 目錄
- 🎨 **產品化訊息**: 技術術語改為使用者友善描述

**新增檔案**:
1. `src/utils/time_tracker.py` - 時間追蹤器類別（596 行）

**修改檔案**:
1. `main.py` - 整合時間追蹤器
2. `src/scenarios/course_learning.py` - 添加課程時間追蹤
3. `src/scenarios/exam_learning.py` - 添加考試時間追蹤
4. `src/core/driver_manager.py` - 產品化輸出訊息
5. `menu.py` - 產品化輸出訊息（2 處）

**使用方式**:
```bash
python main.py
# 程式結束時自動顯示時間統計報告
# 報告同時保存到 reports/time_report_YYYYMMDD_HHMMSS.md
```

**報告範例**:
```
【程式執行時間】
  總執行時間: 15m 30s
  總延遲時間: 5m 20s
  使用者等待: 2m 10s
  淨執行時間: 8m 0s

【課程計畫統計】
  📚 資通安全教育訓練(114年度)
     項目數: 3 (課程: 2, 考試: 1)
     總時間: 10m 30s (執行: 7m 10s + 延遲: 3m 20s)
```

**向後相容**:
- ✅ 所有原有功能不受影響
- ✅ 時間追蹤自動啟用（可選擇性關閉）
- ✅ 無報告文件時優雅降級

---

### ⭐ 最新功能 (2025-01-17) - 第一更新

**一鍵自動執行 + 跨平台字體支援**

將「智能推薦」功能升級為完全自動化的「一鍵自動執行」,並新增跨平台字體載入系統。

**核心特點**:
- 🚀 **全自動執行**: 掃描 → 排程 → 執行 → 清理 (一鍵完成)
- 🧹 **執行前清理**: 自動清除排程、cookies、stealth.min.js
- ⚡ **自動執行**: 呼叫 `python main.py` 執行排程
- 🧹 **執行後清理**: 再次清除所有臨時檔案
- 🌍 **跨平台字體**: 支援 Windows/Linux/macOS (15+ 字體路徑)
- 🔤 **中文優先**: 優先載入中文字體 (微軟雅黑、文泉驛正黑、蘋方)

**修改檔案**:
1. `menu.py` - 智能推薦功能完全重構
2. `src/utils/screenshot_utils.py` - `_load_font()` 完全重寫

**使用方式**:
```bash
python menu.py
# 輸入 'i' → 確認 'y' → 觀察自動執行流程
```

**字體安裝 (Linux)**:
```bash
sudo apt-get install fonts-wqy-zenhei
# 或
sudo apt-get install fonts-noto-cjk
```

**向後相容**:
- ✅ 所有原有功能不受影響
- ✅ 傳統工作流程仍可正常使用
- ✅ Windows 用戶無需任何變更

---

### ⭐ 最新功能 (2025-01-17) - 第二更新

**產品化輸出訊息優化（MVP → Release）**

專案從 MVP 轉向 Release 版本，將所有螢幕輸出訊息從技術性用詞改為使用者友善的描述。

**核心特點**:
- 🎨 **使用者友善**: 隱藏技術細節，使用通用易懂的描述
- 📊 **產品化術語**: `mitmproxy` → `network monitoring`, `stealth evasions` → `browser automation mode`
- 📝 **文檔保留**: 技術文檔完整保留，僅修改螢幕輸出
- 🔧 **零邏輯變更**: 純訊息修改，100% 向後相容

**修改檔案**:
1. `src/core/proxy_manager.py` - 6 處螢幕輸出產品化
2. `src/utils/stealth_extractor.py` - 3 處螢幕輸出產品化
3. `main.py` - 4 處螢幕輸出產品化

**輸出效果對比**:

修改前：
```
[Step 2/6] Extracting stealth evasions...
[Step 3/6] Starting mitmproxy with visit duration interceptor...
[INFO] Starting mitmproxy on 127.0.0.1:8080
```

修改後：
```
[Step 2/6] Activating browser automation mode...
[Step 3/6] Starting network monitoring with visit duration interceptor...
[INFO] Starting network monitoring on 127.0.0.1:8080
```

**產品化優勢**:
- ✅ 降低技術門檻
- ✅ 適合正式產品發布
- ✅ 保持程式碼可維護性
- ✅ 技術文檔完整保留

**修改統計**:
- 修改檔案數: 3 個
- 修改行數: 13 行（純 print 語句）
- 邏輯變更: 0 個
- 向後相容性: 100%

---

### ⭐ 最新功能 (2025-01-16) - 截圖功能實作

**課程學習截圖功能 + 時間配置分離**

在第二階段(課程計畫詳情頁)自動截圖並添加時間戳水印,記錄學習過程。同時將延遲時間配置從課程定義中分離,統一管理。

**核心特點**:
- 📸 **雙重截圖**: 每個課程在第二階段拍攝 2 張截圖(進入時 + 返回時)
- ⏰ **時間戳水印**: 右下角顯示黃色日期時間(64px 字體,清晰可見)
- 📁 **自動分類**: 按 `{username}/{date}/` 結構存儲
- 🎨 **可自訂外觀**: 字體大小、顏色、背景透明度全可調
- 🔧 **獨立控制**: 每個課程可單獨啟用/停用截圖
- ⚡ **延遲時間集中管理**: 從 courses.json 分離到 timing.json

**新增檔案**:
1. `config/timing.json` - 延遲時間與截圖配置
2. `src/utils/screenshot_utils.py` - 截圖管理器

**修改檔案**:
- `src/core/config_loader.py` - 添加 timing 配置載入
- `src/scenarios/course_learning.py` - 整合截圖功能
- `data/courses.json` - 移除 delay,添加 enable_screenshot
- `requirements.txt` - 添加 Pillow>=10.0.0
- `menu.py` - 顯示截圖狀態
- `main.py` - 自動清除排程

**使用範例**:
```json
// data/courses.json
{
  "lesson_name": "某課程",
  "course_id": 465,
  "enable_screenshot": true,  // 啟用截圖
  "description": "課程描述"
}
```

**截圖存儲**:
```
screenshots/
└── {username}/
    └── 2025-01-16/
        ├── 課程名稱_2501161530-1.jpg  (第1次截圖)
        └── 課程名稱_2501161530-2.jpg  (第2次截圖)
```

**延遲時間調整**:
- Stage 2 (課程計畫詳情): 7.0 → **11.0 秒** (截圖需要更多載入時間)
- 其他階段維持不變

**字體設定優化**:
- 字體大小: 48 → **64px** (更清晰)
- 顏色: 白色 → **黃色 (#FFFF00)** (更醒目)
- 背景透明度: 180 → **200** (對比更強)

**向後相容**:
- ✅ 未安裝 Pillow 時優雅降級
- ✅ 缺少 timing.json 時使用預設值
- ✅ 所有原有功能不受影響

**安裝依賴**:
```bash
pip install Pillow
```

---

### ⭐ 最新功能 (2025-11-16 晚間) - 第二更新

**安全性增強：自動清理臨時檔案**

在程式結束時自動刪除敏感的臨時檔案（cookies.json 和 stealth.min.js），提升安全性與隱私保護。

**清理目標**:
1. `cookies.json` - 根目錄臨時 Cookie 檔案
2. `resource/cookies/cookies.json` - 登入憑證
3. `stealth.min.js` - 根目錄臨時反檢測腳本
4. `resource/plugins/stealth.min.js` - 反檢測腳本

**實作位置**:
- `main.py` (Line 144-159) - 程式結束時清理
- `menu.py` (Line 414-429) - 智能推薦後清理

**執行時機**:
- ✅ 程式正常執行完成
- ✅ 使用者按 Ctrl+C 中斷
- ✅ 程式發生異常錯誤
- ✅ 智能推薦功能執行完成

**優點**:
- **安全性**: 防止登入憑證洩漏
- **隱私保護**: 不保留登入狀態記錄
- **自動化**: 無需手動清理，程式結束時自動執行
- **可靠性**: 在正常結束、中斷、錯誤時均會執行

**向後相容性**:
- ✅ 不影響任何現有功能
- ✅ 所需檔案會在下次執行時自動重新生成
- ✅ CookieManager 會在需要時重新建立 Cookie 檔案
- ✅ StealthExtractor 會在需要時重新提取反檢測腳本

---

### ⭐ 最新功能 (2025-11-16 早上)

**智能推薦功能修復** - 修正課程掃描問題

**問題**: 智能推薦功能（menu.py 中的 `i` 選項）無法找到「修習中」的課程
- 症狀: 掃描返回 0 個課程計畫、0 個課程、0 個考試
- 根因: XPath 選擇器與實際 HTML 結構不匹配

**解決方案**:
- 修正 `get_in_progress_programs()` - 使用正確的課程連結選擇器
- 修正 `get_program_courses_and_exams()` - 使用正確的活動選擇器
- 添加 10 秒頁面載入延遲

**測試結果**: 100% 成功率
- 找到 8 個「修習中」的課程計畫
- 成功掃描所有課程內部項目
- 智能推薦功能完全正常

**修改文件**:
- `src/pages/course_list_page.py` (2 個方法)
- `menu.py` (添加載入延遲)

---

### ⭐ 最新功能 (2025-11-16 早上)

**選項比對邏輯實作** - 提升答題準確度

**問題**: 題庫中存在題目文字相似但選項內容完全不同的重複題目
- 範例: ID:191 "下列敘述何者正確" vs ID:187 "下列敘述何者正確?"
- 差異: 題目相似度 94%，但選項主題完全不同（個資 vs 業務員）

**解決方案**: 雙重比對機制
- 舊邏輯: 僅比對題目文字 → 可能選錯答案
- 新邏輯: 題目文字 (40%) + 選項內容 (60%) → 精準匹配

**測試結果**: 100% 通過率
- ID:191 綜合評分: 44.32% (選項相似度 11%)
- ID:187 綜合評分: 100.00% (選項相似度 100%) ✓ 正確選中

**優勢**:
- ✅ 完全向下兼容（選項參數可選）
- ✅ 最小效能影響（僅多候選時觸發）
- ✅ 顯著提升準確度（11% vs 100% 選項差異）

**新增文件**:
- `test_duplicate_questions.py` - 單元測試腳本

**修改文件**:
- `src/services/answer_matcher.py` - 新增 `_calculate_option_similarity()`
- `src/scenarios/exam_learning.py` - 傳入選項參數
- `src/scenarios/exam_auto_answer.py` - 傳入選項參數
- `data/courses.json` - 新增壽險業務員測驗

---

## 🏗️ 項目架構

### 分層架構圖
```
┌─────────────────────────────────────────────┐
│              main.py (入口)                  │
│  ┌─────────────────────────────────────┐   │
│  │    menu.py (互動式排程管理)          │   │
│  └─────────────────────────────────────┘   │
└──────────────┬──────────────────────────────┘
               │
        ┌──────▼──────────────┐
        │  Scenarios Layer    │ ← 業務流程編排
        │  - course_learning  │   (勿改原有檔案)
        │  - exam_learning ✨ │   (新增)
        └──────┬──────────────┘
               │
        ┌──────▼──────────────┐
        │   Pages Layer       │ ← 頁面物件 (POM)
        │  - login_page       │
        │  - course_list_page │   (勿改)
        │  - course_detail    │   (勿改)
        │  - exam_detail ✨   │   (新增)
        └──────┬──────────────┘
               │
        ┌──────▼──────────────┐
        │    Core Layer       │ ← 核心模組
        │  - driver_manager   │   (勿改)
        │  - config_loader    │   (勿改)
        │  - cookie_manager   │   (勿改)
        │  - proxy_manager    │   (勿改)
        └─────────────────────┘
```

### 目錄結構
```
eebot/
├── src/
│   ├── core/                    # 核心基礎設施
│   │   ├── config_loader.py     # 配置載入器
│   │   ├── driver_manager.py    # WebDriver 管理
│   │   ├── cookie_manager.py    # Cookie 管理
│   │   └── proxy_manager.py     # MitmProxy 管理
│   │
│   ├── pages/                   # 頁面物件 (POM)
│   │   ├── base_page.py         # 基類（提供通用方法）
│   │   ├── login_page.py        # 登入頁面
│   │   ├── course_list_page.py  # 課程列表頁面 (勿改)
│   │   ├── course_detail_page.py # 課程詳情頁面 (勿改)
│   │   └── exam_detail_page.py  # 考試詳情頁面 (新增 ✨)
│   │
│   ├── scenarios/               # 業務流程編排
│   │   ├── course_learning.py   # 課程學習流程 (勿改)
│   │   └── exam_learning.py     # 考試流程 (新增 ✨)
│   │
│   ├── api/
│   │   └── interceptors/
│   │       └── visit_duration.py # HTTP 攔截器（修改訪問時長）
│   │
│   └── utils/
│       └── stealth_extractor.py  # 反檢測工具
│
├── data/
│   ├── courses.json             # 課程配置 (重要！)
│   └── schedule.json            # 排程配置（自動生成）
│
├── config/
│   └── eebot.cfg                # 系統配置
│
├── docs/                        # 項目文檔
│   ├── changelogs/              # CHANGELOG 歷史歸檔目錄
│   │   └── CHANGELOG_archive_2025.md  # 2025 年歷史版本
│   ├── AI_ASSISTANT_GUIDE.md    # 通用 AI 助手指南
│   ├── CLAUDE_CODE_HANDOVER.md  # 本文件
│   └── CHANGELOG.md             # 修改歷史（最新版本）
│
├── main.py                      # 主程式入口
└── menu.py                      # 互動式選單
```

---

## 🔧 核心概念

### 1. 課程配置 (courses.json)

這是整個系統的**數據核心**，定義所有可執行的課程和考試。

#### 課程類型 (course)
```json
{
  "program_name": "課程計畫名稱",
  "lesson_name": "課程名稱",
  "course_id": 369,
  "delay": 7.0,
  "description": "課程描述"
}
```

#### 考試類型 (exam) - 2025-01-13 新增
```json
{
  "program_name": "課程計畫名稱",
  "exam_name": "考試名稱",
  "course_type": "exam",
  "delay": 7.0,
  "description": "考試描述"
}
```

**⚠️ 重要規則**: 所有課程（一般課程與考試）的 `delay` **必須統一為 7.0 秒**。這是強制標準。

**關鍵差異**:
- 課程使用 `lesson_name` + `course_id`
- 考試使用 `exam_name` + `course_type: "exam"`
- 考試沒有 `course_id`（因為考試的返回邏輯不同）
- 延遲時間與一般課程相同（7.0 秒統一標準）

### 2. 執行流程

#### 課程流程 (course_learning.py)
```
登入 → 我的課程 → 選擇計畫 → 選擇課程 → 返回計畫 → 返回列表
```

#### 考試流程 (exam_learning.py) - 新增
```
登入 → 我的課程 → 選擇計畫 → 點擊考試
  → 點擊"繼續答題" → 勾選同意 → 確認 → 考卷區
```

### 3. MitmProxy 機制

MitmProxy 用於攔截並修改 HTTP 請求，特別是修改訪問時長參數。

**工作流程**:
1. `ProxyManager` 啟動 MitmProxy 伺服器
2. `VisitDurationInterceptor` 攔截特定請求
3. 修改請求中的 `visit_duration` 參數（+9000 秒）
4. 讓系統誤以為用戶已觀看足夠時長

**配置**: `config/eebot.cfg` 中的 `modify_visits` 選項

---

## 📝 常見任務指南

### 任務 1: 添加新的課程（學習類型）

#### Step 1: 編輯 courses.json
```json
{
  "program_name": "新課程計畫名稱",
  "lesson_name": "新課程名稱",
  "course_id": 999,          // 從網頁 HTML 找到 ng-click='goBackCourse(XXX)'
  "delay": 7.0,
  "description": "課程描述"
}
```

#### Step 2: 使用 menu.py 選擇課程
```bash
python menu.py
# 選擇課程編號
# 輸入 's' 儲存排程
```

#### Step 3: 執行
```bash
python main.py
```

**注意**: 不需要修改任何代碼！

---

### 任務 2: 添加新的考試（考試類型）

#### Step 1: 編輯 courses.json
```json
{
  "program_name": "考試計畫名稱",
  "exam_name": "考試名稱",
  "course_type": "exam",      // 必須設為 "exam"
  "delay": 7.0,               // 統一標準：所有課程必須為 7.0 秒
  "description": "考試描述"
}
```

#### Step 2-3: 同上（使用 menu.py 和 main.py）

---

### 任務 3: 修改考試流程

如果需要調整考試流程的點擊邏輯：

#### 編輯文件
- `src/pages/exam_detail_page.py`
- `src/scenarios/exam_learning.py`

#### 可修改的方法
```python
# exam_detail_page.py
def click_exam_by_name()          # 點擊考試名稱
def check_agreement_checkbox()    # 勾選同意條款
def click_popup_continue_button() # 確認進入考試
```

#### ⚠️ 不可修改的文件
- `src/scenarios/course_learning.py`
- `src/pages/course_list_page.py`
- `src/pages/course_detail_page.py`
- 任何 `src/core/*` 檔案

---

### 任務 4: 新增新類型的流程

假設你需要添加「問卷」類型：

#### Step 1: 創建頁面類
```python
# src/pages/survey_page.py
from .base_page import BasePage

class SurveyPage(BasePage):
    def click_survey_by_name(self, survey_name, delay=10.0):
        # 實作邏輯
        pass
```

#### Step 2: 創建場景類
```python
# src/scenarios/survey_learning.py
from ..pages.survey_page import SurveyPage

class SurveyLearningScenario:
    def execute(self, surveys):
        # 實作邏輯
        pass
```

#### Step 3: 修改 main.py
```python
from src.scenarios.survey_learning import SurveyLearningScenario

# 在 main() 中添加分離邏輯
surveys = [item for item in courses if item.get('course_type') == 'survey']
```

#### Step 4: 修改 menu.py
在 `display_menu()` 和 `display_schedule()` 中添加問卷類型的顯示邏輯。

---

## 🚫 禁止修改清單

以下文件**絕對不可修改**（除非有明確需求並經過審查）：

### Scenarios Layer
- ❌ `src/scenarios/course_learning.py`

### Pages Layer
- ❌ `src/pages/base_page.py`
- ❌ `src/pages/login_page.py`
- ❌ `src/pages/course_list_page.py`
- ❌ `src/pages/course_detail_page.py`

### Core Layer
- ❌ `src/core/config_loader.py`
- ❌ `src/core/driver_manager.py`
- ❌ `src/core/cookie_manager.py`
- ❌ `src/core/proxy_manager.py`

### API Layer
- ❌ `src/api/interceptors/visit_duration.py`

### 配置文件
- ❌ `config/eebot.cfg`
- ❌ `data/courses.json` 中的**原有課程條目**

### 原因
這些文件是系統的核心，已經過充分測試且穩定運行。修改可能導致現有功能崩潰。

---

## 📋 文檔管理規則

### CHANGELOG.md 拆分策略 (2025-01-17 新增規則)

**背景**: CHANGELOG.md 文件過長（769 行, 23KB）會影響 Claude Code CLI 的讀取效能。

**拆分規則**:
1. **主 CHANGELOG.md**: 保留最新 2-3 個版本（約 400 行以內）
2. **歷史歸檔**: 舊版本移至 `docs/changelogs/CHANGELOG_archive_YYYY.md`
3. **導航鏈接**: 主文件頂部包含歸檔文件的導航鏈接

**當前結構**:
```
CHANGELOG.md                              # 最新版本（v2.0.4, v2.0.2+auto-answer.1, v2.0.2+auto-answer）
docs/changelogs/
└── CHANGELOG_archive_2025.md            # 歷史版本（v2.0.1, v2.0.0）
```

**觸發條件**:
- CHANGELOG.md 超過 **400 行**或 **15KB**
- Claude Code CLI 提示文件過大無法正常讀取

**拆分流程**:
1. 創建歸檔文件（如果不存在）
2. 將舊版本移至歸檔
3. 更新主 CHANGELOG.md，添加歸檔鏈接
4. 更新相關文檔（本文檔、AI_ASSISTANT_GUIDE.md）

**查看歷史版本**:
```bash
# 查看最新版本
cat CHANGELOG.md

# 查看歷史歸檔
cat docs/changelogs/CHANGELOG_archive_2025.md
```

### 工作日誌檔名規範 (2025-11-24 新增規則)

**背景**: 一天可能有多次工作記錄，舊格式 `DAILY_WORK_LOG_yyyymmdd.md` 會造成檔名衝突，曾出現 `_v2` 後綴的不一致命名。

**新規範**: `DAILY_WORK_LOG_yyyymmddhhmm.md`

**格式說明**:
- **yyyy**: 年份（4位數）
- **mm**: 月份（2位數，01-12）
- **dd**: 日期（2位數，01-31）
- **hh**: 小時（2位數，00-23）
- **mm**: 分鐘（2位數，00-59）

**範例**:
```
DAILY_WORK_LOG_202511241430.md  (2025年11月24日 14:30)
DAILY_WORK_LOG_202511241445.md  (2025年11月24日 14:45)
```

**自動分段規則**:
- **觸發條件**: 單一檔案超過 **500 行**或 **20KB**
- **分段格式**: `DAILY_WORK_LOG_yyyymmddhhmm-{num}.md`
- **範例**:
  ```
  DAILY_WORK_LOG_202511241430-1.md  (第1段)
  DAILY_WORK_LOG_202511241430-2.md  (第2段)
  DAILY_WORK_LOG_202511241430-3.md  (第3段)
  ```

**分段原則**:
- 在合適的章節結束處分段（不在段落中間切斷）
- 每個分段檔案開頭包含導航連結
- 分段檔案末尾包含「續下一檔案」連結

**分段模板**:
```markdown
# EEBot 工作日誌 - 2025-11-24 14:30 (第1段)

> **分段資訊**: 本日誌共 3 段
> - 📄 當前: 第 1 段
> - ➡️ 下一段: [DAILY_WORK_LOG_202511241430-2.md](./DAILY_WORK_LOG_202511241430-2.md)

---

[工作日誌內容...]

---

**本段結束，請繼續閱讀下一段**: [DAILY_WORK_LOG_202511241430-2.md](./DAILY_WORK_LOG_202511241430-2.md)
```

**舊格式檔案處理**:
- ✅ 保留所有舊格式檔案（不重新命名，避免破壞歷史記錄）
- ✅ 從 2025-11-24 開始使用新格式
- ⚠️ 舊格式問題案例: `DAILY_WORK_LOG_20250117_v2.md`（1月17日第2次記錄，被迫使用 `_v2` 後綴）

**當前檔案清單**:
```
舊格式（yyyymmdd）:
├── 2025年1月
│   ├── DAILY_WORK_LOG_20250116.md  (截圖功能實作)
│   ├── DAILY_WORK_LOG_20250117.md  (一鍵自動執行)
│   └── DAILY_WORK_LOG_20250117_v2.md  (時間統計系統) ← 第2次記錄
└── 2025年11月
    ├── DAILY_WORK_LOG_20251114.md  (早期開發)
    ├── DAILY_WORK_LOG_20251115.md  (自動答題系統)
    ├── DAILY_WORK_LOG_20251116.md  (安全性增強)
    └── DAILY_WORK_LOG_20251117.md  (穩定性優化 v2.0.5)

新格式（yyyymmddhhmm）:
└── DAILY_WORK_LOG_202511242157.md  (課程配置優化討論) ← 首個新格式檔案
```

**生效時間**: 2025-11-24 立即生效

---

## 🔍 關鍵代碼索引

### 1. 如何定位網頁元素？

查看 `src/pages/base_page.py`:
```python
def find_element(self, locator: tuple) -> WebElement:
    # 使用 WebDriverWait 等待元素出現
    return self.wait.until(EC.presence_of_element_located(locator))

def click(self, locator: tuple, use_js: bool = False):
    # 智能點擊（處理被遮擋的情況）
    # 如果普通點擊失敗，會自動使用 JS 點擊
```

**使用範例**:
```python
# 在任何 Page 類中
exam_button = (By.XPATH, "//button[text()='繼續答題']")
self.click(exam_button)
```

### 2. 如何添加延遲等待？

```python
import time
time.sleep(10.0)  # 固定延遲 10 秒

# 或使用 BasePage 提供的方法
self.sleep(10.0)
```

### 3. 如何處理彈窗？

查看 `src/pages/exam_detail_page.py`:
```python
def check_agreement_checkbox(self, delay: float = 10.0):
    # 使用 JavaScript 點擊（避免被其他元素覆蓋）
    element = self.find_element(self.AGREEMENT_CHECKBOX)
    self.driver.execute_script("arguments[0].click();", element)
```

### 4. 如何讀取配置？

查看 `src/core/config_loader.py`:
```python
config = ConfigLoader("config/eebot.cfg")
config.load()

username = config.get('user_name')
password = config.get('password')
modify_visits = config.get_bool('modify_visits')
```

---

## 💡 Claude Code 特定建議

### 使用 @workspace
在與 Claude Code 對話時，使用 `@workspace` 快速索引項目：
```
@workspace 請幫我找到所有定義 click 方法的文件
@workspace 課程配置檔在哪裡？
@workspace 考試流程是如何實現的？
```

### 快速命令參考
```bash
# 查看課程列表並排程
python menu.py

# 執行排程
python main.py

# 查看配置
cat config/eebot.cfg

# 查看課程配置
cat data/courses.json

# 查看排程
cat data/schedule.json

# 查看修改歷史
cat docs/CHANGELOG.md
```

### 代碼修改流程
1. **閱讀本文檔** → 理解項目結構
2. **查看 CHANGELOG.md** → 了解最新修改
3. **定位目標文件** → 使用上方的文件索引
4. **檢查禁止清單** → 確保不修改核心文件
5. **進行修改** → 遵循現有代碼風格
6. **更新 CHANGELOG.md** → 記錄你的修改
7. **測試** → 使用 menu.py 和 main.py 測試

---

## 📞 問題排查

### 問題 1: 考試按鈕無法點擊 (已於 2025-01-13 修復)

#### 1.1 考試頁面"繼續答題"按鈕找不到

**症狀**: `Element not found` 在 Step 2

**原因**: XPath 定位器過於嚴格

**解決方案** (已實現):
- `click_continue_exam_button()` 現在使用 4 種備用策略
- 如果仍失敗：增加 `delay` 到 15 秒

#### 1.2 彈窗內"繼續答題"按鈕無法點擊

**症狀**: `Element not clickable` 在 Step 4

**原因**:
- 按鈕在 checkbox 勾選後需要時間啟用
- AngularJS 更新狀態延遲
- 元素可能被遮擋

**解決方案** (已實現):
- `click_popup_continue_button()` 使用 5 種策略
- 自動檢查 disabled 狀態並等待
- 使用 JavaScript 點擊
- 詳見：`exam_detail_page.py` 第 142-200 行

**如果仍失敗**:
1. 增加 `delay` 時間（從 10 秒增加到 15 秒）
2. 檢查彈窗 ID 是否為 `start-exam-confirmation-popup`
3. 使用瀏覽器 DevTools 檢查實際結構

### 問題 2: MitmProxy 無法啟動

**可能原因**:
- 端口被佔用
- 權限不足

**解決方案**:
1. 檢查 `config/eebot.cfg` 中的 `listen_port`
2. 更改為其他端口（例如 8081）
3. 或設置 `modify_visits=n` 禁用代理

### 問題 3: 課程和考試混合執行順序問題

**現狀**:
當排程包含課程和考試時，會先執行所有課程，再執行所有考試。

**原因**:
每種類型使用獨立的 Scenario，避免頻繁切換造成瀏覽器重啟。

**如需交叉執行**:
需要修改 `main.py`，實現單一 Scenario 統一處理。

---


---

**本段結束**

📍 繼續閱讀: [CLAUDE_CODE_HANDOVER-2.md](./CLAUDE_CODE_HANDOVER-2.md) - 進階功能詳解

---

*文檔版本: 2.0 | 最後更新: 2025-11-24 | 專案: Gleipnir*
