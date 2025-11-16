# EEBot - Claude Code CLI 交接文檔

> **專為 Claude Code CLI 優化的項目交接文檔**
>
> 本文檔使用 Claude Code 的最佳實踐格式編寫，方便快速理解項目結構並進行後續開發。

**文檔版本**: 1.3
**最後更新**: 2025-11-16 晚間
**項目版本**: 2.0.2+auto-answer.3
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
3. 查看 `docs/CHANGELOG.md` 了解最新修改

### 關鍵文件路徑
```
D:\Dev\eebot\
├── data/courses.json          ← 課程配置（最重要！）
├── main.py                    ← 程式入口
├── menu.py                    ← 互動式選單
├── src/scenarios/             ← 業務流程層
│   ├── course_learning.py     ← 課程流程（原有，勿改）
│   └── exam_learning.py       ← 考試流程（2025-01-13 新增）
├── src/pages/                 ← 頁面操作層 (POM)
│   ├── exam_detail_page.py    ← 考試頁面（2025-01-13 新增）
│   ├── course_list_page.py    ← 課程列表（原有，勿改）
│   └── course_detail_page.py  ← 課程詳情（原有，勿改）
└── docs/                      ← 項目文檔
    ├── AI_ASSISTANT_GUIDE.md  ← 通用 AI 助手文檔
    └── CHANGELOG.md           ← 修改歷史記錄
```

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
1. **自動登入**: 使用 Cookies 或帳密登入
2. **課程/考試選擇**: 根據 `data/courses.json` 配置
3. **自動瀏覽**: Selenium 模擬用戶操作
4. **時長修改**: MitmProxy 攔截並修改訪問時長
5. **智能答題**: 題目文字 + 選項內容雙重比對 ⭐ NEW (2025-11-16)
6. **完成學習**: 自動完成課程或考試流程

### ⭐ 最新功能 (2025-11-16 晚間)

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
│   ├── AI_ASSISTANT_GUIDE.md    # 通用 AI 助手指南
│   ├── CLAUDE_CODE_HANDOVER.md  # 本文件
│   └── CHANGELOG.md             # 修改歷史
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

## 🎯 已完成功能：自動答題系統 (Phase 2)

> **狀態**: ✅ **已實作完成** (2025-11-15)
> **版本**: 2.0.2+auto-answer
> **實作者**: wizard03 (with Claude Code CLI)
> **目前進度**: 完整的自動答題系統，含智能匹配引擎

### 功能概述

自動答題系統將透過比對考試頁面題目與題庫答案，實現自動答題功能。

### 題庫資料

**位置**: `郵政E大學114年題庫/`

**統計資料**:
- 總題數：**1,766 題**
- 總大小：**5.3 MB**
- 分類數：**23 個主題**
- 格式：**JSON 檔案**

**範例分類**:
```
窗口線上測驗（390題）
郵務窗口(114年度)（188題）
法令遵循／防制洗錢（262題）
資通安全（30題）
高齡投保（10題）
... 共 23 個分類
```

---

### 考試頁面元素分析

#### 題目元素
```html
<li class="subject">
    <span class="subject-description">題目內容</span>
</li>
```

**定位方式**: `.subject-description` 或 `//span[@class='subject-description']`

#### 選項元素

**單選題 (Radio)**:
```html
<input type="radio" ng-model="subject.answeredOption" />
<div class="option-content"><span>選項內容</span></div>
```

**複選題 (Checkbox)**:
```html
<input type="checkbox" ng-model="option.checked" />
<div class="option-content"><span>選項內容</span></div>
```

**定位方式**: `.option-content`, `input[type="radio"]`, `input[type="checkbox"]`

#### 交卷按鈕
```html
<a class="button button-green" ng-click="calUnsavedSubjects()">交卷</a>
<button ng-click="submitAnswer(...)">確定</button>
```

**重要**: 考試採用**整頁顯示**模式（所有題目在同一頁），非分頁模式。

---

### 資料庫方案評估

#### 推薦方案：混合模式 (SQLite + JSON)

| 方案 | 適用性 | 速度 | 部署難度 | 推薦度 |
|------|-------|------|---------|--------|
| **SQLite** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ (零配置) | **✅ 強烈推薦** |
| JSON | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ (現成) | ✅ 適合 MVP |
| MySQL | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ (需安裝) | ❌ 殺雞用牛刀 |

**為何選擇 SQLite？**
- ✅ 零配置（Python 內建 `sqlite3`）
- ✅ 檔案式（單一 `.db` 檔案）
- ✅ 查詢速度快（毫秒級）
- ✅ 支援全文檢索（FTS5）
- ✅ 適合 5.3MB 資料量

**分階段策略**:
```
階段 1 (MVP)：直接使用現有 JSON 檔案
階段 2 (優化)：首次啟動自動建立 SQLite
階段 3 (正式)：使用 SQLite，保留 JSON 作備份
```

---

### 新增檔案架構（符合 POM 模式）

```
eebot/
├── src/
│   ├── pages/
│   │   ├── exam_detail_page.py        # 現有（勿改）
│   │   └── exam_answer_page.py        # 【新增】答題頁面
│   │
│   ├── scenarios/
│   │   ├── exam_learning.py           # 現有（勿改）
│   │   └── exam_auto_answer.py        # 【新增】自動答題場景
│   │
│   ├── services/                      # 【新增】業務邏輯層
│   │   ├── question_bank.py           # 題庫查詢服務
│   │   └── answer_matcher.py          # 答案匹配引擎
│   │
│   └── models/                        # 【新增】資料模型
│       └── question.py                # 題目/選項資料類別
│
├── data/
│   ├── courses.json                   # 現有
│   └── questions.db                   # 【新增】SQLite 資料庫
│
└── 郵政E大學114年題庫/
    └── *.json                         # 現有（保留作備份）
```

---

### 核心模組設計

#### ExamAnswerPage（答題頁面物件）
```python
class ExamAnswerPage(BasePage):
    def get_all_questions()              # 取得所有題目元素
    def get_question_text(question_elem) # 取得題目文字
    def get_options(question_elem)       # 取得題目選項
    def get_option_text(option_elem)     # 取得選項文字
    def click_option(option_elem)        # 點擊選項
    def submit_exam()                    # 提交考試
```

#### QuestionBankService（題庫服務）
```python
class QuestionBankService:
    def __init__(mode='sqlite', **kwargs)
    def find_answer(question_text) -> Optional[Dict]
    # 返回：{question_id, type, correct_options[]}
```

#### AnswerMatcher（答案匹配引擎）
```python
class AnswerMatcher:
    @staticmethod
    def normalize_text(text)             # 標準化文字
    def find_best_match(web_q, db_qs)    # 模糊匹配
    # 多層級回退：
    # 1. 精確匹配（最快）
    # 2. 包含匹配
    # 3. 相似度匹配（SequenceMatcher）
```

---

### 匹配策略

#### 挑戰：網頁題目 vs 題庫題目差異

| 差異類型 | 範例 | 解決方案 |
|---------|------|---------|
| HTML 標籤 | `<p>題目</p>` vs `題目` | BeautifulSoup 去除 |
| 空白字元 | 多空格 vs 單空格 | 正規化 |
| 標點符號 | 全形 vs 半形 | 統一轉換 |

#### 匹配信心門檻

**設定**: 0.85（85% 相似度）以避免誤配

---

### SQLite 資料表設計

```sql
-- 題目表
CREATE TABLE questions (
    id INTEGER PRIMARY KEY,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    description_text TEXT,              -- 純文字版（用於匹配）
    type TEXT NOT NULL,                 -- single_selection/multiple_selection
    difficulty_level TEXT,
    answer_explanation TEXT
);

-- 選項表
CREATE TABLE options (
    id INTEGER PRIMARY KEY,
    question_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    content_text TEXT,                  -- 純文字版
    is_answer BOOLEAN NOT NULL,         -- 正確答案標記
    sort INTEGER,
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

-- 全文檢索索引（關鍵！）
CREATE VIRTUAL TABLE questions_fts USING fts5(
    description_text,
    content='questions',
    content_rowid='id'
);
```

---

### 實作階段規劃

#### 階段 1：MVP（最小可行產品）
**目標**: 驗證自動答題可行性

- ✅ 使用現有 JSON 檔案
- ✅ 實作 `QuestionBankService`（JSON 模式）
- ✅ 實作基礎 `AnswerMatcher`
- ✅ 實作 `ExamAnswerPage`
- ✅ 整合至 `ExamLearningScenario`

**預估時間**: 2-3 小時

#### 階段 2：優化匹配準確度
**目標**: 提升匹配率

- ✅ 改進相似度演算法
- ✅ 處理 HTML 清理邏輯
- ✅ 新增匹配日誌

**預估時間**: 2-3 小時

#### 階段 3：遷移至 SQLite
**目標**: 效能優化

- ✅ 撰寫 JSON → SQLite 遷移腳本
- ✅ 建立 FTS5 全文檢索索引
- ✅ 實作 `QuestionBankService`（SQLite 模式）

**預估時間**: 1-2 小時

#### 階段 4：生產就緒
**目標**: 穩健與可維護

- ✅ 混合模式（首次啟動自動建立 SQLite）
- ✅ 自動偵測題庫更新
- ✅ 失敗時截圖除錯
- ✅ 生成答題準確率報告

**預估時間**: 2-3 小時

---

### 配置選項（規劃）

#### eebot.cfg 新增項目
```ini
# 現有配置...
user_name=your_username
password=your_password

# 新增：自動答題配置
enable_auto_answer=y                     # 啟用自動答題
question_bank_mode=sqlite                # 'sqlite' 或 'json'
question_bank_path=data/questions.db
answer_confidence_threshold=0.85         # 最低相似度門檻
auto_submit_exam=y                       # 自動提交考試
screenshot_on_mismatch=y                 # 無法匹配時截圖
```

---

### 風險評估

| 風險 | 描述 | 緩解策略 |
|------|------|---------|
| **匹配失敗** | 網頁題目與題庫不一致 | 多層級回退 + 信心門檻 |
| **動態載入** | AngularJS 渲染延遲 | 增加 WebDriverWait |
| **檢測風險** | 網站可能偵測自動化 | 已使用 Stealth JS |
| **題庫過期** | 題庫與考試不同步 | 記錄失敗案例 |

---

### 成功標準

**MVP 成功**:
- [ ] 成功匹配 ≥80% 題目
- [ ] 自動點擊正確選項（單選）
- [ ] 自動點擊正確選項（複選）
- [ ] 自動提交考試

**正式版成功**:
- [ ] 匹配率 ≥95%
- [ ] SQLite 查詢 <10ms/題
- [ ] 零誤答（無誤判）
- [ ] 優雅處理未匹配題目

---

### ✅ 實作完成總結 (2025-11-15)

**實作狀態**: ✅ 所有規劃功能已完整實作

**新增檔案**:
```
src/models/
├── __init__.py
└── question.py                  # 資料模型

src/services/
├── __init__.py
├── question_bank.py             # 題庫服務
└── answer_matcher.py            # 匹配引擎

src/pages/
└── exam_answer_page.py          # 答題頁面

src/scenarios/
└── exam_auto_answer.py          # 自動答題場景
```

**修改檔案**:
- `config/eebot.cfg` - 新增 AUTO_ANSWER 配置區塊
- `main.py` - 整合自動答題場景
- `requirements.txt` - 新增 beautifulsoup4 依賴

**使用方式**:
```bash
# 1. 安裝依賴
pip install beautifulsoup4

# 2. 設定排程
python menu.py

# 3. 執行自動答題（enable_auto_answer=y）
python main.py
```

**核心功能**:
- ✅ 自動偵測題目數量與題型
- ✅ 多層級匹配演算法 (85% 門檻)
- ✅ 單選/複選題自動作答
- ✅ 未匹配題目截圖記錄
- ✅ 答題統計報告
- ✅ 使用者確認交卷機制

---

**實作版本**: 2.0.2+auto-answer
**實作者**: wizard03 (with Claude Code CLI - Sonnet 4.5)
**實作日期**: 2025-11-15
**狀態**: ✅ **已完成並可使用**

**詳細變更記錄**: 請參考 `CHANGELOG.md` 版本 2.0.2+auto-answer
**技術細節**: 請參考 `docs/AI_ASSISTANT_GUIDE.md` Phase 2 章節

---

## 🚀 智能模式：按課程啟用自動答題 (2025-11-15 更新)

> **重大變更**: 自動答題邏輯從全局啟用改為按課程啟用

### 變更概述

**舊邏輯** (v2.0.2+auto-answer):
- 全局 `enable_auto_answer` 設定於 `config/eebot.cfg`
- 所有考試統一啟用或停用自動答題
- 需修改配置檔才能切換模式

**新邏輯** (v2.0.2+auto-answer Smart Mode):
- 每個考試獨立設定 `enable_auto_answer` 於 `data/courses.json`
- 不同考試可選擇不同模式（自動/手動）
- 自動偵測考卷區頁面後才啟動
- 懶加載機制（僅在需要時載入題庫）

### 配置變更

#### 1. 課程配置 (courses.json)

**新增 `enable_auto_answer` 欄位**:

```json
{
  "program_name": "高齡客戶投保權益保障(114年度)",
  "exam_name": "高齡測驗(100分及格)",
  "course_type": "exam",
  "enable_auto_answer": true,    // 新增：啟用此考試的自動答題
  "delay": 7.0,
  "description": "高齡測驗 - 自動答題"
}
```

**未設定則預設為手動模式**:

```json
{
  "program_name": "其他考試(114年度)",
  "exam_name": "其他測驗",
  "course_type": "exam",
  // 未設定 enable_auto_answer → 手動模式
  "delay": 7.0,
  "description": "需手動完成"
}
```

#### 2. 系統配置 (eebot.cfg)

**推薦設定**: 改用 `file_mapping` 模式

```ini
[AUTO_ANSWER]
enable_auto_answer = y                          # 保留（舊版相容）
question_bank_mode = file_mapping               # 從 'total_bank' 改為此
question_bank_path = 郵政E大學114年題庫/總題庫.json
answer_confidence_threshold = 0.85
auto_submit_exam = n
screenshot_on_mismatch = y
skip_unmatched_questions = y
screenshot_dir = screenshots/unmatched
```

### 工作流程變更

#### 舊流程（全局模式）
```
1. 編輯 config/eebot.cfg → 設定 enable_auto_answer=y
2. 執行 python menu.py → 選擇考試
3. 執行 python main.py → 所有考試自動答題
4. 如需停用，再編輯 config/eebot.cfg
```

#### 新流程（智能模式）
```
1. 編輯 data/courses.json → 為特定考試加入 "enable_auto_answer": true
2. 執行 python menu.py → 選擇考試
3. 執行 python main.py → 只有標記的考試自動答題
4. 系統自動偵測考卷區後才啟動
```

### 技術實作細節

#### 1. 考卷區頁面偵測

**新增方法**: `_is_in_exam_answer_page()` 於 `ExamLearningScenario`

```python
def _is_in_exam_answer_page(self) -> bool:
    """偵測是否進入考卷區頁面"""
    try:
        driver = self.driver_manager.get_driver()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.subject"))
        )
        questions = driver.find_elements(By.CSS_SELECTOR, "li.subject")
        if len(questions) > 0:
            print(f'  ✅ 偵測到考卷區頁面（共 {len(questions)} 題）')
            return True
        return False
    except Exception as e:
        print(f'  ⚠️  考卷區檢測失敗: {e}')
        return False
```

**目的**: 防止在錯誤頁面啟動自動答題

#### 2. 懶加載機制

**舊方式**: 為所有考試載入題庫和匹配器

**新方式**: 僅在需要時才初始化

```python
class ExamLearningScenario:
    def __init__(self, config, keep_browser_on_error=False):
        # ... 現有代碼 ...
        self.exam_answer_page = ExamAnswerPage(driver)
        self.question_bank = None      # 懶加載
        self.answer_matcher = None     # 懶加載

    def _auto_answer_current_exam(self, exam):
        """僅在需要時初始化題庫"""
        if self.question_bank is None:
            print('[初始化] 載入題庫...')
            self.question_bank = QuestionBankService(self.config)
            question_count = self.question_bank.load_question_bank(
                exam.get('program_name')
            )

        if self.answer_matcher is None:
            print('[初始化] 載入答案匹配器...')
            self.answer_matcher = AnswerMatcher(self.config)
```

**優點**:
- 節省記憶體（手動考試不載入）
- 加快啟動速度
- 只載入相關題庫（file_mapping 模式）

#### 3. 條件啟動邏輯

**新流程** (於 `_process_exam()` 中):

```python
def _process_exam(self, exam: Dict[str, any]):
    # ... 現有考試流程（登入、導航、點擊考試）...

    # 新增：檢查該考試是否啟用自動答題
    enable_auto_answer = exam.get('enable_auto_answer', False)

    if enable_auto_answer and self._is_in_exam_answer_page():
        print('【自動答題模式啟動】')
        self._auto_answer_current_exam(exam)
    else:
        print('請手動完成考試')
        input('完成後按 Enter 繼續...')
```

**決策樹**:
```
是否 enable_auto_answer=true?
  ├─ 否 → 手動模式（等待使用者）
  └─ 是 → 檢查是否在考卷區頁面
      ├─ 否 → 手動模式（頁面錯誤）
      └─ 是 → 自動答題模式（啟動）
```

### 主程式簡化

**舊方式**: 兩個分離的場景

```python
# 舊代碼（已移除）
if enable_auto_answer:
    exam_scenario = ExamAutoAnswerScenario(...)
else:
    exam_scenario = ExamLearningScenario(...)
```

**新方式**: 統一場景

```python
# 新代碼（簡化）
exam_scenario = ExamLearningScenario(config, keep_browser_on_error)
exam_scenario.execute(exams)
# 每個考試內部自行決定模式
```

**優點**:
- 單一瀏覽器會話處理所有考試
- 無需在考試間重啟瀏覽器
- main.py 代碼更簡潔

### 重要 Bug 修復 (2025-11-15)

#### 1. UTF-8 BOM 編碼
**問題**: JSON 檔案含有 UTF-8 BOM 標記
**解決**: 所有 JSON 讀取改用 `encoding='utf-8-sig'`

**影響檔案**:
- `src/services/question_bank.py` (2 處)
- `main.py` (1 處)
- `menu.py` (3 處)

#### 2. 分頁結構解析
**問題**: 題庫檔案使用 `[{"subjects": [...]}]` 分頁結構
**解決**: `_load_specific_bank()` 新增分頁偵測處理

```python
if isinstance(data[0], dict) and 'subjects' in data[0]:
    # 分頁結構
    for page in data:
        if 'subjects' in page:
            for subject in page['subjects']:
                # 處理題目
```

#### 3. 元素互動問題
**問題**: 交卷按鈕無法點擊 (element not interactable)
**解決**: 使用 JavaScript 點擊 + 精確 XPath

```python
# 更新定位器 (exam_answer_page.py)
SUBMIT_BUTTON = (By.XPATH, "/html/body/div[3]/div[4]/div[3]/div[9]/div/div/div[3]/div/div[3]/a")
CONFIRM_BUTTON = (By.XPATH, "//*[@id='submit-exam-confirmation-popup']/div/div[3]/div/button[1]")

# JavaScript 點擊
self.driver.execute_script("arguments[0].click();", submit_btn)
time.sleep(3)
```

#### 4. QuestionBankService 初始化
**問題**: 使用錯誤參數 `mode=...`, `total_bank_path=...`
**解決**: 正確初始化方式

```python
self.question_bank = QuestionBankService(self.config)
question_count = self.question_bank.load_question_bank(exam.get('program_name'))
```

#### 5. 方法名稱不一致
**問題**: `get_all_questions()` 等方法不存在
**解決**: 統一命名

```python
# 正確的方法名稱 (ExamAnswerPage)
detect_questions()             # 非 get_all_questions()
extract_question_text()        # 非 get_question_text()
extract_options()              # 非 get_options()
submit_exam_with_confirmation() # 非 submit_exam()
```

#### 6. 回傳型別處理
**問題**: `find_best_match()` 回傳 tuple 非 dict
**解決**: 正確的 tuple 解包

```python
match_result = self.answer_matcher.find_best_match(question_text, questions)
if match_result is None:
    # 處理無匹配
else:
    db_question, confidence = match_result  # tuple 解包
```

### 測試結果

**測試課程**: 高齡客戶投保權益保障考試

| 項目 | 結果 |
|-----|------|
| 題庫載入 | 10 題 |
| 匹配成功 | 10/10 (100%) |
| 匹配信心度 | 95-100% |
| 自動作答 | ✅ 全部正確 |
| 考試提交 | ✅ 成功 |

### 使用範例

#### 範例 1: 為特定考試啟用自動答題

**步驟 1**: 編輯 `data/courses.json`

```json
{
  "description": "課程資料配置檔",
  "version": "1.0",
  "courses": [
    {
      "program_name": "高齡客戶投保權益保障(114年度)",
      "exam_name": "高齡測驗(100分及格)",
      "course_type": "exam",
      "enable_auto_answer": true,    // 啟用此考試
      "delay": 7.0,
      "description": "高齡測驗 - 自動答題"
    },
    {
      "program_name": "資通安全測驗(114年度)",
      "exam_name": "資通安全測驗",
      "course_type": "exam",
      "enable_auto_answer": true,    // 啟用此考試
      "delay": 7.0,
      "description": "資通安全測驗 - 自動答題"
    },
    {
      "program_name": "其他考試(114年度)",
      "exam_name": "其他測驗",
      "course_type": "exam",
      // 未設定 → 手動模式
      "delay": 7.0,
      "description": "其他測驗 - 手動完成"
    }
  ]
}
```

**步驟 2**: 排程與執行

```bash
python menu.py
# 選擇三個考試

python main.py
# 考試 1 (高齡測驗): 自動答題 ✅
# 考試 2 (資通安全測驗): 自動答題 ✅
# 考試 3 (其他測驗): 手動模式 ⏸️
```

#### 範例 2: 混合課程與考試排程

```bash
python menu.py
# 選擇:
# [1] 課程 A (一般課程)
# [2] 課程 B (一般課程)
# [3] 考試 A (enable_auto_answer: true)
# [4] 考試 B (enable_auto_answer: false)

python main.py
# 執行順序:
# 1. 課程 A → 自動完成 ✅
# 2. 課程 B → 自動完成 ✅
# 3. 考試 A → 自動答題 ✅
# 4. 考試 B → 手動模式 ⏸️
```

### 向後相容性

**相容性說明**:
- ✅ 未設定 `enable_auto_answer` 的考試預設為手動模式
- ✅ 原有手動考試流程完全保留
- ✅ 所有課程學習功能不受影響
- ✅ 配置檔 `enable_auto_answer` 保留但作用改變

**破壞性變更**:
- ❌ 全局 `enable_auto_answer` 不再控制所有考試
- ❌ 必須為每個考試明確設定配置
- ❌ `ExamAutoAnswerScenario` 類別已移除（功能整合至 `ExamLearningScenario`）

### 遷移指南

**如果你正在使用全局 `enable_auto_answer`**:

1. 保留 `enable_auto_answer=y` 於 `config/eebot.cfg`（向後相容）
2. 為需要自動答題的考試加入 `"enable_auto_answer": true`
3. 將 `question_bank_mode` 改為 `file_mapping` 提升準確度
4. 移除舊的 `ExamAutoAnswerScenario` 匯入（如果有）

### 最佳實踐

#### 1. 先手動測試
```json
{
  "enable_auto_answer": false,  // 或省略此欄位
  "description": "先手動測試"
}
```

#### 2. 確認題庫對應
檢查 `src/services/question_bank.py` 中的 program name 對應:

```python
QUESTION_BANK_MAPPING = {
    "高齡客戶投保權益保障(114年度)": "高齡投保（10題）.json",
    "資通安全測驗(114年度)": "資通安全（30題）.json",
    "壽險業務員在職訓練學程課程及測驗(114年度)": "壽險業務員在職訓練（30題）.json",
    # 根據需求新增更多對應
}
```

#### 3. 監控匹配成功率
觀察終端輸出:
```
[匹配] 第 1 題: 題目內容
  ✅ 匹配成功（信心: 100.00%）
  ✅ 正確答案: ['選項1', '選項2']
```

#### 4. 檢視失敗截圖
未匹配題目儲存於 `screenshots/unmatched/`:
```
question_5_20251115_143022.png
question_5_20251115_143022.txt  // 含題目文字
```

### 問題排查

#### 問題 1: 自動答題未啟動

**檢查**:
1. `courses.json` 中是否設定 `"enable_auto_answer": true`？
2. 是否成功進入考卷區頁面？
3. 查看終端是否有頁面偵測訊息

**除錯輸出**:
```
✅ 偵測到考卷區頁面（共 10 題）
【自動答題模式啟動】
[初始化] 載入題庫...
```

#### 問題 2: 題目無法匹配

**檢查**:
1. `question_bank_mode` 是否正確設定？
2. program name 是否精確對應題庫對應表？
3. 信心門檻是否過高（預設 0.85）

**除錯輸出**:
```
[載入] 題庫檔案: 郵政E大學114年題庫/高齡投保（10題）.json
[成功] 載入題庫: 10 題
```

#### 問題 3: 交卷按鈕無法使用

**檢查**:
1. `exam_answer_page.py` 中的 XPath 定位器
2. 點擊間的等待時間（預設 3 秒）
3. JavaScript 執行是否啟用

**解決方案**: 定位器已更新為使用者提供的精確 XPath

#### 問題 4: 第二個考試 0% 匹配率 (嚴重 Bug - 已修復)

**症狀**:
- 第一個考試: 100% 匹配率 ✅
- 第二個考試: 0% 匹配率 ❌
- 所有題目顯示「無法匹配」

**根本原因**:
`src/scenarios/exam_learning.py:261` 的懶載入邏輯錯誤，導致多個考試共用同一個題庫實例。

**問題機制**:
```python
# ❌ 錯誤代碼（修復前）
if self.question_bank is None:
    self.question_bank = QuestionBankService(self.config)
    question_count = self.question_bank.load_question_bank(exam.get('program_name'))
```

1. 考試 1 載入題庫 A（例如：高齡投保 10 題）
2. `self.question_bank` 不再是 `None`
3. 考試 2 跳過初始化
4. 考試 2 嘗試用錯誤的題庫 A 匹配題庫 B 的題目
5. 結果：0% 匹配率

**修復方案** (v2.0.2+auto-answer.1):
```python
# ✅ 修復後代碼
# 為每個考試重新載入對應題庫
self.question_bank = QuestionBankService(self.config)
program_name = exam.get('program_name')
question_count = self.question_bank.load_question_bank(program_name)
```

**關鍵改變**:
- ✅ 移除 `if self.question_bank is None` 檢查
- ✅ 每個考試都創建新的 `QuestionBankService` 實例
- ✅ 每個考試都載入對應的題庫
- ✅ 新增 program_name 日誌輸出

**驗證方式**:
執行包含多個考試的流程，應看到每個考試都正確載入對應題庫：
```
--- Processing Exam 1/2 ---
  📚 正在載入題庫...
  ✅ 題庫已載入（共 10 題）
  📋 課程名稱: 高齡客戶投保權益保障(114年度)

--- Processing Exam 2/2 ---
  📚 正在載入題庫...
  ✅ 題庫已載入（共 21 題）
  📋 課程名稱: 金融服務業公平待客原則＆洗錢防制及打擊資恐教育訓練(114年度)
```

**⚠️ 重要經驗**:
> **懶載入 + 共享狀態 = 潛在 Bug**
>
> 當物件實例被重複使用處理不同資料集時：
> - ❌ 不要在不檢查資料上下文的情況下使用懶載入
> - ✅ 處理新資料時務必重新載入資源
> - ✅ 加入日誌追蹤載入的資源
> - ✅ 測試多個連續操作的場景

**程式碼審查檢查清單**:
- [ ] 是否有懶載入邏輯（`if self.resource is None`）？
- [ ] 該實例是否會被重複使用處理不同資料？
- [ ] 資源是否依賴輸入參數？
- [ ] 是否有測試多個連續操作的情境？

---

**智能模式版本**: 2.0.2+auto-answer.1 (懶載入 Bug 已修復)
**更新日期**: 2025-11-15 晚間
**更新者**: wizard03 (with Claude Code CLI - Gleipnir Project)

---

## 📚 延伸閱讀

- **通用 AI 助手指南**: `docs/AI_ASSISTANT_GUIDE.md`
- **修改歷史**: `docs/CHANGELOG.md`
- **Selenium 文檔**: https://www.selenium.dev/documentation/
- **MitmProxy 文檔**: https://docs.mitmproxy.org/

---

**維護者**: wizard03
**文檔版本**: 1.1
**最後更新**: 2025-11-15 (新增自動答題系統實作記錄)

如有任何問題，請參考 `docs/AI_ASSISTANT_GUIDE.md` 或查看 `docs/CHANGELOG.md` 了解最新修改。
