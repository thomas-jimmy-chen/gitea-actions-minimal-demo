# AI 助手交接文檔 #9

**專案**: EEBot v2.4.0 - TronClass Learning Assistant (代號: AliCorn)
**交接日期**: 2025-12-29
**前次交接**: `docs/CLAUDE_CODE_HANDOVER-8.md`
**執行者**: Claude Code (Opus 4.5)

---

## 快速開始 (30 秒)

### 專案狀態

**版本**: v2.4.0 (穩定版)

**本版完成功能**:
- ✅ CAPTCHA OCR 自動識別 (97.6% 準確率)
- ✅ [b] 自動批量模式
- ✅ Cookie 清理機制
- ✅ P1 功能驗證通過

### 你的任務

**P2 優先**: 代碼品質與測試

| # | 任務 | 說明 |
|---|------|------|
| 1 | PEP8 合規性檢查 | 代碼風格統一 |
| 2 | 單元測試補充 | 覆蓋新增功能 |
| 3 | 文檔更新 | 用戶指南同步 |

---

## v2.4.0 變更摘要

### 新功能 (已驗收)

#### 1. CAPTCHA OCR 整合 ✅

```python
# 使用方式
from src.utils.captcha_ocr import solve_captcha
result = solve_captcha('captcha.png')  # 返回 4 位數字或 None
```

**關鍵文件**:
- `src/utils/captcha_ocr.py` - 封裝模組
- `src/pages/login_page.py` - 整合點
- `research/captcha_ocr_analysis/optimized_ocr.py` - 核心 OCR

#### 2. [b] 自動批量模式 ✅

```bash
python menu.py
# 輸入 'b' → 自動掃描 → 自動選擇全部 → 執行
```

**特點**: h2 的自動選擇版本，無需人工確認

#### 3. Cookie 清理機制 ✅

```python
def _clear_cookies():
    files = ['cookies.json', 'resource/cookies/cookies.json']
    for f in files:
        if os.path.exists(f):
            os.remove(f)
```

**時機**: 操作開始時 + 操作結束時 (finally block)

---

## 關鍵路徑

### 核心文件

```
D:\Dev\eebot\
├── menu.py                          # 主選單 ([b], Cookie 清理)
├── src/
│   ├── utils/
│   │   └── captcha_ocr.py           # OCR 封裝
│   └── pages/
│       └── login_page.py            # 登入整合
└── research/
    └── captcha_ocr_analysis/
        └── optimized_ocr.py         # 核心 OCR (97.6%)
```

### 選單選項

| 選項 | 功能 | 說明 |
|------|------|------|
| `i` | 智能推薦 | 原有功能 |
| `b` | 自動批量 | h2 自動版 |
| `h` | 混合掃描 | 1/2/3 子選項 |

---

## 注意事項

### 1. 瀏覽器重啟延遲

多階段操作間瀏覽器重啟需要 3 秒延遲:

```python
driver.quit()
time.sleep(3)  # 必要！避免 session error
driver = driver_manager.create_driver(use_proxy=True)
```

### 2. 登入後等待

登入成功後需要 5 秒等待頁面跳轉:

```python
if self.is_login_success():
    time.sleep(5)  # 等待頁面載入
```

### 3. OCR 回退機制

OCR 失敗時自動切換到手動輸入，不會阻塞流程。

---

## 檔案變更記錄

| 文件 | 變更類型 | 說明 |
|------|---------|------|
| `src/utils/captcha_ocr.py` | 新增 | OCR 封裝 |
| `src/pages/login_page.py` | 修改 | +328 行，整合 OCR |
| `menu.py` | 修改 | +101 行，[b] + 清理 |
| `README.md` | 修改 | 品牌重塑 |
| `src/orchestrators/hybrid_scan.py` | 修改 | +7 行 |

---

## Git 提交 (2025-12-29)

```
4d6e6c7 feat(menu): add cookie cleanup at start/end of operations
bb1e2aa docs(readme): rebrand to TronClass Learning Assistant (v2.4.0)
1cc55d6 feat(login): integrate CAPTCHA OCR and add auto-batch menu option
47ddae1 docs: update handover documents for CAPTCHA OCR integration
fcf401f feat(captcha): add CAPTCHA OCR research with 97.6% accuracy
```

---

## 相關文檔

| 文檔 | 說明 |
|------|------|
| `docs/WORK_LOG_2025-12-29.md` | 今日工作日誌 |
| `docs/TODO.md` | 待辦事項 |
| `CHANGELOG-A.md` | v2.4.0 變更記錄 |
| `docs/CAPTCHA_OCR_TECHNICAL_GUIDE.md` | OCR 技術指南 |

---

## 驗收狀態 (v2.4.0)

- [x] CAPTCHA OCR 整合完成
- [x] [b] 自動批量模式可用
- [x] Cookie 清理機制運作
- [x] P1 功能驗證通過 (2025-12-29)

---

## 下階段任務

### 🔥 P1 優先: 動態頁面載入檢測 (2025-12-30 新增)

> **狀態**: 待實作
> **預計時間**: 下午/晚上
> **整合位置**: `src/pages/base_page.py`

**問題**:
1. e大學使用 AngularJS 動態載入
2. 頁面可能包含多個 iframe
3. 現有代碼沒有處理這些情況

**階段 0: Burp Suite 頁面分析（前置作業）**:
```
[1] wizard03 用 Burp Suite 抓取動作流程
[2] 提供給 AI 分析每個頁面的：
    ├─ 請求/響應結構
    ├─ iframe 結構
    ├─ AngularJS 載入順序
    └─ 關鍵元素定位
[3] AI 逐一分析邏輯流程、技術、frame 結構
[4] 根據分析結果微調實作
```

**待實作功能**:

| # | 功能 | 說明 |
|---|------|------|
| 1 | `wait_for_angular()` | 等待 AngularJS 完成渲染 |
| 2 | `check_angular_bindings_loaded()` | 檢查 ng-bind 資料載入 |
| 3 | `is_loading_visible()` | 檢查 loading 指示器 |
| 4 | `get_all_iframes()` | 獲取所有 iframe |
| 5 | `switch_to_content_frame()` | 自動切換到有內容的 frame |
| 6 | `find_element_in_any_frame()` | 跨 frame 尋找元素 |
| 7 | `check_page_with_frames()` | 綜合頁面檢測 |
| 8 | `is_error_page()` | 檢測 502/503/504 錯誤頁面 |
| 9 | `navigate_with_retry()` | 帶自動重試的頁面導航 |

**技術方案**:
```python
# AngularJS 檢測
script = """
var inj = angular.element(document.body).injector();
return inj.get('$http').pendingRequests.length === 0;
"""

# iframe 處理
def switch_to_content_frame(driver):
    iframes = get_all_iframes(driver)
    for frame in iframes:
        driver.switch_to.frame(frame['id'])
        if has_angular_content():
            return frame['id']
    driver.switch_to.default_content()
```

**詳細討論**: `docs/WORK_LOG_2025-12-29.md` (Section 8.3)

---

### P2: 代碼品質

- PEP8 合規性檢查
- 單元測試補充
- 用戶文檔更新

### P3: 長期規劃

- GUI 開發
- 多平台支援
- 效能優化

---

## 今日變更 (2025-12-30)

### 已完成

| 項目 | 說明 |
|------|------|
| 登入延遲調整 | 5秒 → 3秒 (`login_page.py` L293, L341) |
| 頁面點擊邏輯分析 | 完整梳理所有頁面延遲時間 |

### 頁面延遲時間對照表

| 頁面 | 操作 | 延遲 |
|------|------|------|
| LoginPage | 登入成功後 | **3s** |
| CourseListPage | 選擇課程後 | 7s |
| CourseDetailPage | 選擇章節前 | 7s |
| ExamDetailPage | 每步驟前 | 10s |
| ExamAnswerPage | 交卷後 | 3s |

---

**v2.4.0 已穩定** | 下次 AI 助手請優先處理 P1 動態頁面載入檢測任務
