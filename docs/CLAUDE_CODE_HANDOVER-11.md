# AI 助手交接文檔 #11

**專案**: EEBot v2.4.1 - TronClass Learning Assistant (代號: AliCorn)
**交接日期**: 2025-12-31
**前次交接**: `docs/CLAUDE_CODE_HANDOVER-10.md`
**執行者**: Claude Code (Opus 4.5)

---

## 快速開始 (30 秒)

### 本次完成工作

**主題**: Burp Suite 流量分析 + 姓名替換 + 登入頁面樣式注入

| 項目 | 狀態 | 說明 |
|------|------|------|
| Burp Suite XML 分析 | ✅ 完成 | 分析 12.5MB 流量數據 |
| 姓名出現位置識別 | ✅ 完成 | 5 個位置 |
| MitmProxy 攔截器 | ✅ 完成 | `login_style_modifier.py` |
| CDP 渲染前注入 | ✅ 完成 | Demo 程式更新 |
| 技術文檔整理 | ✅ 完成 | 建立索引文檔 |

### 🔥 重要：新增技術索引

```
docs/BURP_SUITE_ANALYSIS_INDEX.md
```

**所有 AI 助手在處理以下任務時，必須先讀取此文檔**:
- 頁面修改
- API 攔截
- 姓名替換
- 樣式注入

---

## 本次工作詳情

### 1. Burp Suite XML 分析

**來源**: `20251230-bu.txt` (12.5 MB)

**發現**:
- 使用者姓名: 陳偉鳴 (User ID: 19688)
- 姓名出現在 5 個 HTML 位置

**姓名位置**:

| # | 位置 | 範例 |
|---|------|------|
| 1 | JS `user` 物件 | `user: { name: "陳偉鳴" }` |
| 2 | `root-scope-variable` | `value="陳偉鳴"` |
| 3 | `ng-init` | `userCurrentName='陳偉鳴'` |
| 4 | `analyticsData` | `userName: '陳偉鳴'` |
| 5 | `CurrentName` | `CurrentName='陳偉鳴'` |

### 2. 姓名遮蔽規則

**規則**: 保留第一個字，其餘用 `〇` (U+3007) 替換

```python
def _mask_name(name: str) -> str:
    first_char = name[0]
    return first_char + '〇' * (len(name) - 1)
```

**範例**:
- 陳偉鳴 → 陳〇〇
- 李四 → 李〇
- 司馬相如 → 司〇〇〇

### 3. MitmProxy 攔截器

**檔案**: `src/api/interceptors/login_style_modifier.py`

**功能**:
1. 姓名替換 (所有 HTML 頁面)
2. 登入頁 CSS 樣式注入
3. OCR 提示文字 (閃爍動畫)

**使用**:
```bash
mitmdump -s src/api/interceptors/login_style_modifier.py
```

### 4. CDP 渲染前注入

**檔案**: `research/captcha_ocr_analysis/demo/captcha_demo.py`

**技術**: Chrome DevTools Protocol

```python
driver.execute_cdp_cmd(
    'Page.addScriptToEvaluateOnNewDocument',
    {'source': INJECTION_SCRIPT}
)
```

---

## 關鍵檔案

### 新增

| 檔案 | 說明 |
|------|------|
| `src/api/interceptors/login_style_modifier.py` | MitmProxy 攔截器 |
| `docs/BURP_SUITE_ANALYSIS_INDEX.md` | 技術索引 (必讀) |
| `docs/WORK_LOG_2025-12-31.md` | 工作日誌 |
| `NAME_REPLACEMENT_ANALYSIS.md` | 姓名分析報告 |

### 修改

| 檔案 | 變更 |
|------|------|
| `research/captcha_ocr_analysis/demo/captcha_demo.py` | CDP 注入 + 姓名替換 |
| `docs/TODO.md` | 新增 P0 任務 |

---

## 待辦清單

### P0: Burp Suite 相關 (已完成)

| # | 任務 | 狀態 |
|---|------|------|
| 1 | 流量分析 | ✅ 完成 |
| 2 | 姓名替換實作 | ✅ 完成 |
| 3 | 樣式注入實作 | ✅ 完成 |
| 4 | 技術文檔整理 | ✅ 完成 |

### P1: 待測試

| # | 任務 | 狀態 |
|---|------|------|
| 1 | MitmProxy 攔截器測試 | 📋 待做 |
| 2 | CDP 注入測試 | 📋 待做 |
| 3 | 整合到主程式 | 📋 待做 |

### P2: tour.post CAPTCHA OCR (前次進度)

| # | 任務 | 狀態 |
|---|------|------|
| 1 | 建立 `tour_post_ocr.py` | 📋 待做 |
| 2 | 準確率驗證 | 📋 待做 |
| 3 | 登入流程整合 | 📋 待做 |

---

## 技術重點

### 1. 字符選擇

**必須使用 `〇` (U+3007 國字零)**，不是普通圓圈 `○`

### 2. 攔截條件

```python
# Host 過濾
if "elearn.post.gov.tw" not in flow.request.host:
    return

# Content-Type 過濾
if "text/html" not in content_type:
    return
```

### 3. 樣式注入只在 /login

```python
if "/login" in flow.request.path:
    # 注入 CSS
```

---

## 相關文檔

| 文檔 | 說明 | 重要度 |
|------|------|--------|
| `docs/BURP_SUITE_ANALYSIS_INDEX.md` | 技術索引 | 🔥 必讀 |
| `docs/WORK_LOG_2025-12-31.md` | 工作日誌 | 參考 |
| `NAME_REPLACEMENT_ANALYSIS.md` | 姓名分析 | 參考 |
| `docs/TODO.md` | 待辦事項 | 參考 |

---

## 下次接續建議

1. **測試 MitmProxy 攔截器** - 確認姓名替換和樣式注入效果
2. **測試 CDP 注入** - 確認渲染前修改生效
3. **繼續 tour.post CAPTCHA OCR** - 建立可用模組

---

*交接文檔 #11 | 2025-12-31 | Claude Code (Opus 4.5)*
