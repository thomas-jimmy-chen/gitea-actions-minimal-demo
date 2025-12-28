# EEBot 待辦事項清單

> **專案名稱**: EEBot (代號: AliCorn 天角獸)
> **最後更新**: 2025-12-29
> **維護者**: wizard03 + Claude Code (Opus 4.5)
> **專案版本**: v2.3.9

---

## 📋 最新待辦 (2025-12-29)

### 🔥 P0 優先: CAPTCHA OCR 整合 (下回必做)

> **交接說明**: 研究已完成，達到 97.6% 準確率，現需整合到主程式

| # | 任務 | 狀態 | 預期產出 |
|---|------|------|---------|
| 1 | 建立 `src/utils/captcha_ocr.py` | 待開始 | 封裝 OCR 函數 |
| 2 | 修改 `src/pages/login_page.py` | 待開始 | 自動識別 + 手動回退 |
| 3 | 測試完整登入流程 | 待開始 | 確認端到端運作 |

#### 任務 1: 建立 captcha_ocr.py

**檔案**: `src/utils/captcha_ocr.py`

```python
from research.captcha_ocr_analysis.optimized_ocr import recognize_with_fallback

def solve_captcha(image_path: str) -> str:
    """
    自動識別 CAPTCHA (97.6% 準確率)
    Returns: 4位數字結果 或 None
    """
    success, result, confidence = recognize_with_fallback(image_path)
    if success and confidence in ('high', 'medium'):
        return result
    return None
```

#### 任務 2: 修改 login_page.py

**位置**: `src/pages/login_page.py` 的 `fill_captcha()` 方法

```python
from src.utils.captcha_ocr import solve_captcha

def fill_captcha(self):
    captcha_path = 'captcha.png'
    self.save_captcha_image(captcha_path)

    result = solve_captcha(captcha_path)
    if result:
        self.captcha_input.send_keys(result)
    else:
        # 回退到手動輸入
        result = input("請輸入驗證碼: ")
        self.captcha_input.send_keys(result)
```

#### 工具程式參考

| 工具 | 路徑 | 用途 |
|------|------|------|
| optimized_ocr.py | `research/captcha_ocr_analysis/` | 97.6% 多策略 OCR |
| benchmark.py | `research/captcha_ocr_analysis/` | 效能測試 |
| analyze_failures.py | `research/captcha_ocr_analysis/` | 失敗案例分析 |

#### 研究成果摘要

```
準確率: 34.8% → 97.6% (+62.8%)
執行時間: 608ms/張 (可接受)
樣本數: 420 張
技術文檔: docs/CAPTCHA_OCR_TECHNICAL_GUIDE.md
```

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
