# Claude Code 專案規則

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
