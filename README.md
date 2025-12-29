# EEBot - TronClass Learning Assistant (for Chunghwa Post e-Learning)

**專案代號**: AliCorn (天角獸)
**當前版本**: v2.4.0
**最後更新**: 2025-12-29

> TronClass 輔助學習系統 (for 中華郵政e大學)，採用 POM (Page Object Model) + API Interceptor 架構

---

## 核心功能

| 功能 | 說明 | 狀態 |
|------|------|------|
| **自動登入** | Cookie 或帳密認證（3 次重試） | ✅ |
| **課程自動化** | 自動瀏覽完成學習課程 | ✅ |
| **考試自動答題** | 題庫比對 (1,766 題) + 智能匹配 | ✅ |
| **時長修改** | MitmProxy 攔截修改 visit_duration | ✅ |
| **一鍵智能執行** | 掃描 → 排程 → 執行 → 清理 (i 選項) | ✅ |
| **批量模式** | 同時處理課程+考試 (h 選項) | ✅ |
| **跨平台截圖** | 支援 Windows/Linux/macOS 字體 | ✅ |
| **時間統計** | 詳細執行時間報告 | ✅ |

---

## 快速開始

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 2. 配置設定

**方法一：使用 CLI 工具（推薦）**
```bash
python setup.py init         # 建立 .env
python setup.py set username # 設定帳號
python setup.py set password # 設定密碼
python setup.py validate     # 驗證配置
```

**方法二：編輯 config/eebot.cfg**
```ini
[SETTINGS]
target_http=https://elearn.post.gov.tw
execute_file=D:/chromedriver.exe
user_name=your_username
password=your_password
modify_visits=y
silent_mitm=y
```

### 3. 執行程式

```bash
# 互動式選單（推薦）
python menu.py

# 直接執行排程
python main.py
```

---

## 主選單操作

```
╔══════════════════════════════════════╗
║     EEBot - AliCorn v2.3.8          ║
╠══════════════════════════════════════╣
║  [智能掃描]                          ║
║    i - 一鍵智能執行（掃描+執行）      ║
║    h - 混合掃描（進階選項）           ║
║                                      ║
║  [快速查詢]                          ║
║    w - 查詢學習履歷                  ║
║    t - 測試 API 連線                 ║
║                                      ║
║  [預製排程]                          ║
║    1-13 - 選擇課程                   ║
║    v - 查看排程                      ║
║    c - 清除排程                      ║
║    s - 儲存排程                      ║
║    r - 執行排程                      ║
╚══════════════════════════════════════╝
```

### h 選項子選單

| 選項 | 功能 | 說明 |
|------|------|------|
| 1 | 目標模式 | 指定課程快速發送時長 |
| 2 | 批量模式 | 掃描並處理所有課程+考試 |
| 3 | 考試答題 | 僅處理考試自動答題 |

---

## 專案架構

```
eebot/
├── main.py                      # 程式入口
├── menu.py                      # 互動式選單
├── setup.py                     # CLI 配置工具
├── .env                         # 環境變數（敏感資料）
│
├── config/
│   └── eebot.cfg                # 系統配置
│
├── data/
│   ├── courses.json             # 課程配置
│   └── schedule.json            # 執行排程（自動生成）
│
├── src/
│   ├── core/                    # 核心基礎設施
│   │   ├── config_loader.py     # 配置載入（支援環境變數）
│   │   ├── driver_manager.py    # WebDriver 管理
│   │   ├── cookie_manager.py    # Cookie 管理
│   │   └── proxy_manager.py     # MitmProxy 管理
│   │
│   ├── pages/                   # 頁面物件 (POM)
│   │   ├── base_page.py         # 頁面基類
│   │   ├── login_page.py        # 登入頁面
│   │   ├── course_list_page.py  # 課程列表
│   │   ├── course_detail_page.py # 課程詳情
│   │   ├── exam_detail_page.py  # 考試頁面
│   │   └── exam_answer_page.py  # 答題頁面
│   │
│   ├── scenarios/               # 業務流程
│   │   ├── course_learning.py   # 課程學習流程
│   │   ├── exam_learning.py     # 考試流程
│   │   └── exam_auto_answer.py  # 自動答題流程
│   │
│   ├── services/                # 業務邏輯
│   │   ├── question_bank.py     # 題庫服務
│   │   ├── answer_matcher.py    # 答案匹配引擎
│   │   └── api_scanner.py       # API 掃描器
│   │
│   ├── api/
│   │   ├── visit_duration_api.py # 時長 API
│   │   └── interceptors/        # MitmProxy 攔截器
│   │       ├── visit_duration.py
│   │       ├── payload_capture.py
│   │       └── exam_auto_answer.py
│   │
│   └── utils/                   # 工具模組
│       ├── screenshot_utils.py  # 截圖管理
│       ├── time_tracker.py      # 時間追蹤
│       ├── execution_wrapper.py # 執行包裝器
│       └── stealth_extractor.py # 反檢測工具
│
├── docs/                        # 項目文檔
│   ├── AI_ASSISTANT_GUIDE.md    # AI 助手指南
│   ├── CLAUDE_CODE_HANDOVER.md  # Claude Code 交接文檔
│   └── changelogs/              # 歷史版本記錄
│
├── reports/                     # 執行報告（自動生成）
├── screenshots/                 # 截圖（自動生成）
└── 郵政E大學114年題庫/           # 題庫資料 (1,766 題)
```

---

## 架構設計

```
┌─────────────────────────────────────────────────────────┐
│                    Entry Layer                           │
│              main.py / menu.py                          │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  Scenarios Layer                         │
│   CourseLearning | ExamLearning | ExamAutoAnswer        │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    Pages Layer (POM)                     │
│   LoginPage | CourseListPage | ExamDetailPage | ...     │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    Core Layer                            │
│   ConfigLoader | DriverManager | ProxyManager | ...     │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    API Layer                             │
│   VisitDurationAPI | PayloadCapture | ExamAutoAnswer    │
└─────────────────────────────────────────────────────────┘
```

---

## 課程配置

### 一般課程

```json
{
  "program_name": "課程計畫名稱",
  "lesson_name": "課程名稱",
  "course_id": 369,
  "delay": 7.0,
  "enable_screenshot": true,
  "description": "課程描述"
}
```

### 考試類型

```json
{
  "program_name": "課程計畫名稱",
  "exam_name": "考試名稱",
  "course_type": "exam",
  "enable_auto_answer": true,
  "delay": 7.0,
  "description": "考試描述"
}
```

---

## 自動答題系統

### 題庫統計

- **總題數**: 1,766 題
- **分類數**: 23 個主題
- **匹配策略**: 題目文字 (40%) + 選項內容 (60%)

### 匹配算法

1. **精確匹配** - 題目完全一致
2. **包含匹配** - 題目互相包含
3. **相似度匹配** - SequenceMatcher >= 85%

### 配置選項

```ini
# config/eebot.cfg
enable_auto_answer = y
question_bank_mode = total_bank
answer_confidence_threshold = 0.85
auto_submit_exam = n
screenshot_on_mismatch = y
```

---

## 版本歷史

| 版本 | 日期 | 重點更新 |
|------|------|----------|
| v2.3.8 | 2025-12-26 | Stage 6 Proxy 修復 + 專案改名 AliCorn |
| v2.3.7 | 2025-12-21 | 批量模式整合考試自動答題 |
| v2.3.6 | 2025-12-18 | APIScanner 統一 + HTTP 狀態碼標準化 |
| v2.3.2 | 2025-12-09 | 學習履歷統計整合 |
| v2.0.8 | 2025-12-06 | Windows 兼容性修復 |
| v2.0.5 | 2025-11-17 | 穩定性與配置優化 |
| v2.0.2 | 2025-11-15 | 自動答題系統實作 |
| v2.0.1 | 2025-11-10 | 互動式選單與排程系統 |
| v2.0.0 | 2025-01-08 | POM + API 模組化架構 |

> 完整更新記錄請見 [CHANGELOG.md](./CHANGELOG.md)

---

## 文檔索引

| 文檔 | 說明 |
|------|------|
| [AI_ASSISTANT_GUIDE.md](./docs/AI_ASSISTANT_GUIDE.md) | AI 助手交接指南 |
| [CLAUDE_CODE_HANDOVER.md](./docs/CLAUDE_CODE_HANDOVER.md) | Claude Code 專用文檔 |
| [CONFIGURATION_MANAGEMENT_GUIDE.md](./docs/CONFIGURATION_MANAGEMENT_GUIDE.md) | 配置管理指南 |
| [CHANGELOG.md](./CHANGELOG.md) | 版本更新記錄 |

---

## 技術棧

- **語言**: Python 3.x
- **瀏覽器自動化**: Selenium WebDriver
- **HTTP 攔截**: MitmProxy
- **圖像處理**: Pillow
- **HTML 解析**: BeautifulSoup4

---

## 授權

此專案僅供學習與研究使用。

---

## 作者

- **Guy Fawkes** - v2.0.0 原始架構設計
- **wizard03** - v2.0.1+ 功能開發與維護
- **Claude Code** - AI 輔助開發

---

*This project is enhanced with AI assistance (Claude Code CLI)*
