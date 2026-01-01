# Claude Code 專案規則

## 開發方法：混合漸進式開發 (方法 4)

本專案採用**方法 4 - 混合漸進式開發**，各模組有不同的開發節奏。

### 模組狀態定義

| 狀態 | 符號 | 開發方式 |
|------|------|----------|
| 探索中 | 🔄 | 迭代式，不需規格，保持簡單 |
| 轉換中 | 🔄→📋 | 邊做邊寫規格 |
| 已穩定 | 📋 | 依規格開發，修改前檢查規格 |
| 凍結 | 🔒 | 不再變動，僅維護 |

### 當前模組狀態 (2025-01-01)

```
src/
├── core/                    📋 已穩定
│   ├── config_loader.py     📋 配置載入
│   ├── driver_manager.py    📋 WebDriver 管理
│   ├── cookie_manager.py    📋 Cookie 管理
│   ├── proxy_manager.py     📋 MitmProxy 管理
│   └── browser_session.py   📋 瀏覽器會話
│
├── pages/                   📋 已穩定 (POM Pattern)
│   ├── base_page.py         📋 頁面基類
│   ├── login_page.py        📋 登入頁面
│   ├── course_list_page.py  📋 課程列表
│   ├── course_detail_page.py 📋 課程詳情
│   ├── exam_detail_page.py  📋 考試頁面
│   └── exam_answer_page.py  📋 答題頁面
│
├── services/                🔄→📋 轉換中
│   ├── question_bank.py     📋 題庫服務
│   ├── answer_matcher.py    📋 答案匹配
│   ├── api_scanner.py       🔄→📋 API 掃描
│   ├── login_service.py     📋 登入服務
│   ├── course_recommender.py 🔄 課程推薦
│   └── hybrid/              🔄→📋 混合掃描服務
│       ├── course_structure_service.py   🔄→📋
│       ├── duration_send_service.py      🔄→📋
│       ├── payload_capture_service.py    📋
│       └── pass_requirement_service.py   🔄
│
├── api/                     📋 已穩定
│   ├── visit_duration_api.py 📋 時長 API
│   └── interceptors/        📋 MitmProxy 攔截器
│       ├── visit_duration.py      📋
│       ├── payload_capture.py     📋
│       ├── exam_auto_answer.py    🔄→📋
│       └── login_style_modifier.py 📋
│
├── scenarios/               🔄→📋 轉換中
│   ├── course_learning.py   📋 課程學習流程
│   ├── exam_learning.py     📋 考試流程
│   ├── exam_auto_answer.py  🔄→📋 自動答題
│   └── hybrid_duration_send.py 🔄 混合時長發送
│
├── orchestrators/           🔄 探索中 (新架構)
│   ├── base_orchestrator.py 🔄
│   ├── duration_send.py     🔄
│   ├── hybrid_scan.py       🔄
│   └── intelligent_recommendation.py 🔄
│
└── utils/                   📋 已穩定
    ├── screenshot_utils.py  📋 截圖工具
    ├── time_tracker.py      📋 時間追蹤
    ├── execution_wrapper.py 🔄→📋 執行包裝器
    └── captcha_ocr.py       🔄 驗證碼 OCR
```

### 開發規則

| 模組狀態 | 修改前 | 修改後 |
|----------|--------|--------|
| 📋 已穩定 | 必須檢查規格 | 驗證符合規格 |
| 🔄→📋 轉換中 | 參考現有代碼 | 更新規格草稿 |
| 🔄 探索中 | 無限制 | 保持代碼簡單 |

### 規格文檔位置

| 模組 | 規格位置 |
|------|----------|
| 題庫服務 | `docs/AI_ASSISTANT_GUIDE-1.md` (Auto-Answer System) |
| API 掃描 | `docs/WORK_SUMMARY_2025-12-18_API_SCANNER_MIGRATION.md` |
| 時長 API | `docs/BURP_SUITE_ANALYSIS_INDEX.md` → visit_duration |
| MitmProxy 攔截 | `docs/ELEARNING_PLATFORM_TECHNICAL_RESEARCH.md` |

---

## 重構規則 - 切細原則

進行任何重構或實作時，必須執行「切細」：

### 閾值標準

| 類型 | 閾值 | 動作 |
|------|------|------|
| 方法行數 | > 30 行 | 拆分為多個小方法 |
| 類別行數 | > 300 行 | 拆分為多個類別 |
| 方法參數 | > 4 個 | 封裝成 dataclass 或 dict |
| 巢狀層數 | > 3 層 | 提取內層邏輯為方法 |

### 單一職責原則

- 一個方法只做一件事
- 一個類別只有一個變更理由
- 模組邊界清晰，依賴明確

### 實作流程

1. **分析階段**：識別超過閾值的代碼
2. **設計階段**：規劃拆分邊界和模組結構
3. **實作階段**：確保每個單元單一職責
4. **驗證階段**：檢查是否符合閾值標準

### 命名規範

- 方法名：動詞開頭，描述行為（如 `extract_structure`、`send_duration`）
- 類別名：名詞，描述職責（如 `CourseStructureService`、`PayloadCaptureService`）
- 私有方法：底線前綴（如 `_validate_input`、`_process_item`）

---

## 專案架構

```
src/
├── config/          # 配置管理
├── core/            # 核心組件 (driver, proxy, cookie)
├── pages/           # 頁面物件 (Page Object Pattern)
├── services/        # 業務邏輯服務層
│   └── hybrid/      # 混合掃描服務
├── orchestrators/   # 流程編排器
├── api/             # API 相關
│   └── interceptors/  # mitmproxy 攔截器
└── utils/           # 工具函數
```

---

## 功能開關

使用 `src/config/feature_flags.py` 控制新舊代碼切換：

```python
from src.config.feature_flags import feature_enabled

if feature_enabled('use_orchestrators'):
    # 新代碼路徑
else:
    # Legacy 代碼路徑
```

---

## 語言偏好

- 代碼註釋：繁體中文
- 變數/方法名：英文
- 用戶輸出訊息：繁體中文
- 文檔：繁體中文

---

## 🔥 重要技術文檔索引

處理以下任務前，**必須先閱讀對應的技術索引文檔**：

| 任務類型 | 必讀文檔 |
|----------|----------|
| 頁面修改、姓名替換、API 攔截 | `docs/BURP_SUITE_ANALYSIS_INDEX.md` |
| AI 交接、工作狀態 | `docs/CLAUDE_CODE_HANDOVER-11.md` |
| 待辦事項、任務優先級 | `docs/TODO.md` |

### Burp Suite 分析相關

當處理以下任務時，請參考 `docs/BURP_SUITE_ANALYSIS_INDEX.md`：

1. **姓名替換** - 使用 `〇` (U+3007) 遮蔽規則
2. **MitmProxy 攔截器** - `src/api/interceptors/` 目錄
3. **CDP 渲染前注入** - Chrome DevTools Protocol 實作
4. **登入頁面樣式** - CSS 注入和視覺效果
