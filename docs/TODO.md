# EEBot 待辦事項清單

> **專案名稱**: EEBot - TronClass Learning Assistant (代號: AliCorn 天角獸)
> **最後更新**: 2025-01-03
> **維護者**: wizard03 + Claude Code (Opus 4.5)
> **專案版本**: v2.5.0

---

## 🔥 P0 完成: 方法 4 業界框架對應 + 實務操作手冊 (2025-01-03)

> **狀態**: ✅ 完成
> **完成日期**: 2025-01-03
> **相關文檔**: `docs/AI_COLLABORATION_METHOD_4_INDUSTRY_MAPPING.md`

### 完成項目

| # | 任務 | 狀態 | 說明 |
|---|------|------|------|
| 1 | 業界框架對應文檔 | ✅ 完成 | Dual-Track + EA 對應 |
| 2 | 實務操作手冊 | ✅ 完成 | Session 模板、Prompt 庫 |
| 3 | 參考文獻備份 | ✅ 完成 | 4 個文獻彙整文檔 |
| 4 | 索引連結更新 | ✅ 完成 | 多文檔互相連結 |

### 產出檔案

| 檔案 | 說明 |
|------|------|
| `docs/AI_COLLABORATION_METHOD_4_INDUSTRY_MAPPING.md` | 業界框架對應 |
| `docs/AI_COLLABORATION_PRACTICAL_GUIDE.md` | 實務操作手冊 |
| `docs/references/method_4_industry_frameworks/README.md` | 文獻索引 |
| `docs/references/method_4_industry_frameworks/01_dual_track_agile.md` | Dual-Track 文獻 |
| `docs/references/method_4_industry_frameworks/02_evolutionary_architecture.md` | EA 文獻 |
| `docs/references/method_4_industry_frameworks/03_combined_practice.md` | 結合實務 |

### 業界框架對應

| 層級 | 框架 | 提出者 | 對應 |
|------|------|--------|------|
| 上層 | Dual-Track Agile | Marty Cagan (SVPG) | Discovery → 🔄, Delivery → 📋 |
| 下層 | Evolutionary Architecture | ThoughtWorks | Fitness Functions → pytest |

---

## 🔥 P0 完成: AI 協作方法文檔 + 測試框架 (2025-01-01)

> **狀態**: ✅ 完成
> **完成日期**: 2025-01-01
> **相關文檔**: `docs/AI_COLLABORATION_METHODS_COMPARISON.md`

### 完成項目

| # | 任務 | 狀態 | 說明 |
|---|------|------|------|
| 1 | AI 協作方法文檔 | ✅ 完成 | 4 種方法 + 比較分析 |
| 2 | 業界方法對應 | ✅ 完成 | Dual-Track Agile 等 |
| 3 | 測試框架建立 | ✅ 完成 | pytest + 57 個測試 |
| 4 | CI/CD 策略討論 | ✅ 完成 | 採用方案 C 本地 Review |
| 5 | Code Review 指令文檔 | ✅ 完成 | 快速指令參考 |

### 產出檔案

| 檔案 | 說明 |
|------|------|
| `docs/AI_COLLABORATION_METHOD_*.md` | 4 種協作方法 |
| `docs/CI_CD_AND_TESTING_STRATEGY.md` | CI/CD 策略 |
| `docs/CLAUDE_CODE_REVIEW_QUICK_REFERENCE.md` | Code Review 快速指令 |
| `tests/unit/test_*.py` | 3 個測試模組 (57 tests) |

### Code Review 快速指令

```bash
# 互動式
claude → /code-reviewer

# 快速 review
claude -p "/code-reviewer"

# Review 特定檔案
claude -p "review src/xxx.py"
```

---

## 🔥 P0 完成: Burp Suite 流量分析 + 姓名替換 (2025-12-31)

> **狀態**: ✅ 完成
> **完成日期**: 2025-12-31
> **相關文檔**: `docs/BURP_SUITE_ANALYSIS_INDEX.md` (技術索引)

### 完成項目

| # | 任務 | 狀態 | 說明 |
|---|------|------|------|
| 1 | Burp Suite XML 分析 | ✅ 完成 | 分析 12.5MB 流量數據 |
| 2 | 姓名出現位置識別 | ✅ 完成 | 5 個 HTML 位置 |
| 3 | MitmProxy 攔截器開發 | ✅ 完成 | `login_style_modifier.py` |
| 4 | CDP 渲染前注入實作 | ✅ 完成 | Demo 程式更新 |
| 5 | 技術文檔整理 | ✅ 完成 | 建立索引文檔 |

### 產出檔案

| 檔案 | 說明 |
|------|------|
| `src/api/interceptors/login_style_modifier.py` | MitmProxy 攔截器 |
| `docs/BURP_SUITE_ANALYSIS_INDEX.md` | 技術索引 (必讀) |
| `NAME_REPLACEMENT_ANALYSIS.md` | 姓名替換分析報告 |

### 姓名遮蔽規則

**規則**: 保留第一個字，其餘用 `〇` (U+3007 國字零) 替換

| 原始姓名 | 遮蔽後 |
|----------|--------|
| 陳偉鳴 | 陳〇〇 |
| 李四 | 李〇 |
| 司馬相如 | 司〇〇〇 |

---

## 🔥 P0 優先: tour.post.gov.tw CAPTCHA OCR 研究 (2025-12-30)

> **狀態**: 🔄 進行中
> **預計時間**: 下午/晚上繼續
> **相關目錄**: `research/captcha_ocr_analysis/`

### 背景

研究 https://tour.post.gov.tw/login.aspx 網站的 CAPTCHA 驗證碼辨識。

### 已完成

| # | 任務 | 狀態 | 說明 |
|---|------|------|------|
| 1 | 修復樣本收集腳本 | ✅ 完成 | 修正圖片格式檢測 (magic bytes) |
| 2 | 收集 99 個 CAPTCHA 樣本 | ✅ 完成 | `samples_tour_post/*.jpg` |
| 3 | ddddocr 辨識測試 | ✅ 完成 | 99% 辨識 6 位字符 |

### CAPTCHA 技術特徵分析

| 特徵 | 分析結果 |
|------|----------|
| **字符數** | 6 位 |
| **字符類型** | 數字 + 字母 (主要是 X) |
| **字體風格** | 手寫體/傾斜 |
| **字符顏色** | 藍色 |
| **背景** | 純白色 |
| **干擾元素** | 藍色斜線 (2-3 條) |
| **圖片尺寸** | 228×38 像素 |
| **圖片格式** | JPEG |

### ddddocr 測試結果

| 指標 | 結果 |
|------|------|
| 總樣本數 | 99 |
| 6位辨識率 | 98/99 (99%) |
| 5位辨識率 | 1/99 (1%) - 漏字符 |
| 含 X/x 比例 | 44/99 (44%) |

### 待辦事項

| # | 任務 | 狀態 | 說明 |
|---|------|------|------|
| 1 | 建立 tour_post_ocr.py 模組 | 📋 待開始 | 可直接使用的辨識模組 |
| 2 | 準確率驗證 | 📋 待開始 | 人工比對驗證實際準確率 |
| 3 | 登入流程整合 | 📋 待開始 | 整合到自動登入功能 |

### 關鍵檔案

```
research/captcha_ocr_analysis/
├── collect_tour_post_samples.py  # 樣本收集腳本 (已修復)
├── test_tour_post_ocr.py         # OCR 測試腳本
└── samples_tour_post/            # 99 個 CAPTCHA 樣本 (*.jpg)
```

### 環境需求

```bash
# 使用 ddddocr 環境
conda activate ddddocr
# 或直接調用
C:/Users/user123456/miniconda3/envs/ddddocr/python.exe
```

---

## 🔥 P1 優先: 動態頁面載入檢測 (2025-12-30)

> **狀態**: 📋 待實作
> **預計時間**: 下午/晚上實作
> **整合位置**: `src/pages/base_page.py`

### 問題描述

1. e大學使用 AngularJS 動態載入，頁面內容非同步渲染
2. 頁面可能包含多個 iframe，內容分布在不同框架
3. 現有代碼沒有處理這些情況，可能導致頁面空白或載入不完全

### 階段 0: Burp Suite 頁面分析（前置作業）

> **狀態**: 待進行
> **執行者**: wizard03

**工作流程**:
```
[1] Burp Suite 抓取
    └─ 記錄完整的動作流程（登入→課程列表→課程詳情→考試等）

[2] 提供給 AI 分析
    └─ 每個頁面的：
       ├─ 請求/響應結構
       ├─ iframe 結構
       ├─ AngularJS 載入順序
       └─ 關鍵元素定位

[3] AI 逐一分析
    └─ 針對每個頁面：
       ├─ 邏輯流程
       ├─ 採用技術
       ├─ frame 結構
       └─ 檢測策略建議

[4] 微調實作
    └─ 根據分析結果調整檢測函數
```

**產出**: 頁面結構分析報告，作為實作依據

---

### 待實作功能

| # | 功能 | 說明 | 狀態 |
|---|------|------|------|
| 1 | `wait_for_angular()` | 等待 AngularJS 完成渲染 | 待開始 |
| 2 | `check_angular_bindings_loaded()` | 檢查 ng-bind 資料是否載入 | 待開始 |
| 3 | `is_loading_visible()` | 檢查 loading 指示器 | 待開始 |
| 4 | `get_all_iframes()` | 獲取頁面所有 iframe | 待開始 |
| 5 | `switch_to_content_frame()` | 自動切換到有內容的 frame | 待開始 |
| 6 | `find_element_in_any_frame()` | 跨 frame 尋找元素 | 待開始 |
| 7 | `check_page_with_frames()` | 綜合頁面檢測 | 待開始 |
| 8 | `is_error_page()` | 檢測 502/503/504 錯誤頁面 | 待開始 |
| 9 | `navigate_with_retry()` | 帶自動重試的頁面導航 | 待開始 |

### 技術方案摘要

```python
# AngularJS 檢測
def wait_for_angular(driver, timeout=30) -> bool:
    # 檢查 $http.pendingRequests.length === 0
    # 檢查 $browser.outstandingRequestCount === 0

# iframe 處理
def switch_to_content_frame(driver) -> str:
    # 自動切換到有 Angular 內容的 frame
    # 返回 frame 識別符

# 綜合檢測
def check_page_with_frames(driver, timeout=30) -> dict:
    # 檢測主框架 + 所有 iframe
    # 返回 ready 狀態和詳細資訊
```

### 相關文檔

- 討論記錄: `docs/WORK_LOG_2025-12-29.md` (Section 8.3)
- AI 交接: `docs/CLAUDE_CODE_HANDOVER-9.md`

---

## 📋 最新待辦 (2025-12-29)

### ✅ P0 完成: CAPTCHA OCR 整合

> **完成日期**: 2025-12-29
> **實現狀態**: 已整合到登入流程，97.6% 準確率

| # | 任務 | 狀態 | 產出 |
|---|------|------|------|
| 1 | 建立 `src/utils/captcha_ocr.py` | ✅ 完成 | OCR 封裝模組 |
| 2 | 修改 `src/pages/login_page.py` | ✅ 完成 | 自動識別 + 手動回退 |
| 3 | 測試完整登入流程 | ✅ 完成 | 端到端運作正常 |
| 4 | 新增 [b] 自動批量模式 | ✅ 完成 | h2 自動選擇版本 |
| 5 | Cookie 清理機制 | ✅ 完成 | 操作前後自動清理 |

**Git 提交**:
- `1cc55d6` feat(login): integrate CAPTCHA OCR and add auto-batch menu option
- `4d6e6c7` feat(menu): add cookie cleanup at start/end of operations

### ✅ P1 完成: 功能驗證

> **完成日期**: 2025-12-29
> **驗收狀態**: 全部通過

| # | 任務 | 狀態 | 說明 |
|---|------|------|------|
| 1 | 驗證 [b] 自動批量模式 | ✅ 通過 | 真實環境完整流程測試 |
| 2 | 驗證 Cookie 清理機制 | ✅ 通過 | 確認不影響正常操作 |
| 3 | 多帳號切換場景測試 | ✅ 通過 | 切換帳號後 session 正確 |

### 🔥 P2 優先: 代碼品質 (下回可做)

| # | 任務 | 狀態 | 說明 |
|---|------|------|------|
| 1 | PEP8 合規性檢查 | 待開始 | 代碼風格統一 |
| 2 | 單元測試補充 | 待開始 | 覆蓋新增功能 |
| 3 | 用戶文檔更新 | 待開始 | 同步最新功能說明 |

### ⏳ 待測試項目

| 項目 | 優先級 | 狀態 | 說明 |
|------|--------|------|------|
| 多策略滾動函數驗證 | P1 | 待驗證 | 新增考試頁面專用選擇器 |
| Stage 6 考試截圖驗證 | P1 | 待驗證 | 確認 Before/After URL 一致 |
| h 選項 2 批量模式完整測試 | P1 | 待驗證 | 課程+考試混合處理 |

### ✅ 已完成 (v2.3.9)

| 項目 | 完成日期 | 說明 |
|------|---------|------|
| Burp Suite 頁面分析 | 2025-12-27 | 分析考試頁面渲染流程 |
| 滾動容器識別 | 2025-12-27 | .fullscreen-right 等 5 個選擇器 |
| 多策略滾動更新 | 2025-12-27 | 加入考試頁面專用選擇器 |
| 分析報告撰寫 | 2025-12-27 | EXAM_PAGE_RENDERING_ANALYSIS.md |

### ✅ 已完成 (v2.3.8)

| 項目 | 完成日期 | 說明 |
|------|---------|------|
| Stage 6 Proxy 修復 | 2025-12-26 | 重啟瀏覽器使用 use_proxy=True |
| 考試截圖流程優化 | 2025-12-26 | Before/After 在同一頁面 |
| URL 驗證機制 | 2025-12-26 | 等待進入全螢幕考試頁 |
| 主選單重組 | 2025-12-26 | 邏輯分組、簡潔風格 |
| 專案代號 | 2025-12-26 | 新增代號 AliCorn (天角獸) |
| 詳細時間追蹤 | 2025-12-26 | h 功能 start_item/end_item |
| Debug 日誌清理 | 2025-12-26 | 移除冗長輸出 |

### ✅ 已完成 (v2.3.7)

| 項目 | 完成日期 | 說明 |
|------|---------|------|
| 批量模式整合考試 | 2025-12-21 | h 選項 2 支持課程+考試 |
| 考試返回機制 | 2025-12-21 | 雙重備援返回 |
| Stage 4 KeyError 修復 | 2025-12-21 | 正確處理考試類型 |

---

## 📋 Windows 兼容性修復

### ✅ 已完成 (v2.0.8)

| 項目 | 完成版本 | 完成日期 | 說明 |
|------|---------|---------|------|
| Stealth.min.js 下載修復 | v2.0.8 | 2025-12-06 | Windows subprocess shell=True |
| MitmProxy 啟動修復 | v2.0.8 | 2025-12-06 | multiprocessing → threading |
| 靜默模式修復 | v2.0.8 | 2025-12-06 | 移除 TermLog + Dumper addons |
| Chrome 靜默模式 | v2.0.8 | 2025-12-06 | --log-level=3 + 禁用日誌 |

### ⏳ 待測試 (v2.0.8)

**狀態**: 📋 待測試

**優先級**: 高

**項目**:
- [ ] 完整課程執行測試
- [ ] 訪問時長攔截功能測試
- [ ] 自動答題功能測試
- [ ] Linux 環境兼容性測試
- [ ] macOS 環境兼容性測試

**相關文檔**:
- `docs/DAILY_WORK_LOG_20251206_WINDOWS_COMPATIBILITY.md`
- `CHANGELOG.md` v2.0.8

---

## 📋 配置管理改進

### ✅ 已完成

| 項目 | 完成版本 | 完成日期 | Git Commit |
|------|---------|---------|-----------|
| 環境變數隔離 (.env + CLI 工具) | v2.0.7 | 2025-11-30 | f71a685 |

---

### 📋 待辦事項

#### Phase 2: Keyring 整合（可選）

**狀態**: 📋 待辦（未來評估）

**優先級**: 低

**預估時間**: 6-9 小時

**決策**: 2025-11-29 - 列為待辦，未來再評估

**實施時機**:
- GUI 桌面版本開發時
- 使用者明確要求更高安全性
- 發布給更多使用者時

**相關文檔**:
- 完整技術方案見本次討論記錄

**依賴**:
- 需安裝 `keyring` 套件
- 需要桌面環境（GUI）

---

#### SQLite 配置儲存

**狀態**: 📋 待評估

**優先級**: 低

**預估時間**: 4-5 小時

**說明**: 使用 SQLite 儲存配置，支援複雜查詢與版本歷史

**適用場景**:
- 多用戶配置管理
- 配置版本歷史追蹤
- 配置審計需求

**實施建議**: 目前需求不明確，暫不推薦實施

---

#### 配置驗證增強

**狀態**: 💬 討論階段

**優先級**: 低

**預估時間**: 2 小時

**功能**:
- 配置格式驗證（email 格式、URL 格式）
- 配置值範圍檢查
- 依賴配置檢查
- 警告與錯誤分級

---

#### 配置匯入/匯出

**狀態**: 💬 討論階段

**優先級**: 低

**預估時間**: 2 小時

**功能**:
- 匯出配置為 JSON/YAML
- 從檔案匯入配置
- 配置備份與還原
- 配置模板功能

---

#### 多環境配置切換

**狀態**: 💬 討論階段

**優先級**: 低

**預估時間**: 3 小時

**功能**:
- 支援 `.env.dev`, `.env.test`, `.env.prod`
- 環境切換指令
- 環境隔離
- 預設環境設定

---

## 🖥️ GUI 開發計畫

### Selenium Headless Mode

**狀態**: 📋 技術驗證完成

**優先級**: 高

**預估時間**: 2 小時

**說明**:
- 技術驗證已完成（見 `docs/SELENIUM_HEADLESS_GUIDE.md`）
- 待整合到主程式

**修改檔案**:
- `config/eebot.cfg` - 新增 `headless_mode` 參數
- `src/core/driver_manager.py` - 支援 headless 模式

---

### FastAPI Server

**狀態**: 📋 規劃完成

**優先級**: 高

**預估時間**: 2-3 weeks

**說明**:
- Client-Server 架構的後端實作
- RESTful API + WebSocket
- 完整規劃見 `docs/CLIENT_SERVER_ARCHITECTURE_PLAN.md`

**核心功能**:
- 課程管理 API
- 即時執行狀態推送
- 截圖傳輸
- 使用者認證

---

### Desktop Client (Electron)

**狀態**: 📋 規劃完成

**優先級**: 中

**預估時間**: 2-3 weeks

**技術棧**:
- Electron + React + TypeScript
- Material-UI
- Socket.io-client

**核心功能**:
- 課程管理介面
- 即時執行進度顯示
- 配置管理 GUI（整合 Keyring）
- 截圖檢視器

---

### Mobile Clients (Android/iOS)

**狀態**: 📋 規劃完成

**優先級**: 低

**預估時間**: 3-4 weeks

**說明**:
- Android (Kotlin + Jetpack Compose)
- iOS (Swift + SwiftUI)
- 遠端控制桌面執行

---

## 🔧 MitmProxy 精密攔截

### 按課程動態調整訪問時長

**狀態**: 💬 討論階段

**優先級**: 中

**預估時間**: 3-4 小時

**功能**:
- 不同課程設定不同時長增量
- 從 `courses.json` 讀取配置
- 動態攔截規則

---

### 多條件攔截規則

**狀態**: 💬 討論階段

**優先級**: 低

**預估時間**: 2-3 小時

**功能**:
- URL 模式匹配
- HTTP 方法過濾
- 請求參數過濾
- 規則鏈組合

---

### 攔截記錄與統計

**狀態**: 💬 討論階段

**優先級**: 低

**預估時間**: 2 小時

**功能**:
- 記錄所有攔截事件
- 統計攔截次數
- 生成攔截報告
- 調試模式輸出

---

## 📚 課程配置優化

### 課程 Import/Export

**狀態**: 💬 討論階段

**優先級**: 中

**預估時間**: 2-3 小時

**功能**:
- 匯出課程配置為 JSON
- 從 JSON 匯入課程
- 課程模板功能
- 批次匯入

---

### 課程流程標準化

**狀態**: 💬 討論階段

**優先級**: 中

**預估時間**: 3-4 小時

**功能**:
- 定義標準課程流程
- 流程驗證
- 流程可視化
- 自訂流程支援

---

### 課程標籤系統

**狀態**: 💬 討論階段

**優先級**: 低

**預估時間**: 2 小時

**功能**:
- 課程標籤分類
- 標籤篩選
- 標籤統計
- 標籤管理

---

## 📊 優先級說明

| 優先級 | 說明 | 實施時機 |
|--------|------|---------|
| **高** | 重要且緊急 | 近期實施 |
| **中** | 重要但不緊急 | 中期規劃 |
| **低** | 可選功能 | 長期評估 |

---

## 🏷️ 狀態說明

| 狀態 | 說明 |
|------|------|
| ✅ **已完成** | 已實施並測試通過 |
| 📋 **待辦** | 已決定實施，等待排程 |
| 💬 **討論階段** | 需求討論中，尚未決定 |
| 📋 **待評估** | 需進一步評估可行性 |
| 📋 **技術驗證完成** | 技術可行，待整合 |
| 📋 **規劃完成** | 詳細規劃已完成，待實施 |

---

## 📅 版本規劃（參考）

### v2.0.8（近期）
- 無新功能規劃
- 維護與 bug 修復

### v2.1.0（中期）
- Selenium Headless Mode 整合
- 可能新增部分配置管理增強功能

### v3.0.0（長期）
- Client-Server 架構
- GUI 桌面客戶端
- Keyring 整合（配合 GUI）

---

## 🔄 定期檢視

**建議檢視頻率**: 每 2-3 個月

**檢視重點**:
1. 待辦事項是否仍符合需求
2. 優先級是否需要調整
3. 新增需求評估
4. 已完成項目歸檔

---

## 📞 相關文檔

- **配置管理指南**: `docs/CONFIGURATION_MANAGEMENT_GUIDE.md`
- **變更日誌**: `docs/CHANGELOG.md`
- **交接文檔**: `docs/CLAUDE_CODE_HANDOVER-1.md`
- **架構規劃**: `docs/CLIENT_SERVER_ARCHITECTURE_PLAN.md`
- **Selenium Headless**: `docs/SELENIUM_HEADLESS_GUIDE.md`

---

**文檔版本**: 1.0
**建立日期**: 2025-11-29
**維護者**: wizard03
