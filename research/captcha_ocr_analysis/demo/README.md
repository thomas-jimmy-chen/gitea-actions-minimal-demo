# CAPTCHA OCR 示範程式

## 功能特色

1. **Stealth 模式** - 使用 `stealth.min.js` 繞過自動化檢測
2. **自動驗證碼辨識** - 使用 eebot optimized OCR (針對 4 位數字驗證碼)
3. **渲染前樣式注入** - 使用 CDP 在頁面載入前注入樣式
4. **自動重試** - 驗證碼錯誤時自動重試 (最多 3 次)
5. **循環執行** - 可配置重複執行次數
6. **自動清理** - 結束時刪除 cookies 和 stealth.min.js

## 渲染前修改效果

### 姓名替換

| 原始值 | 替換為 | 位置 |
|--------|--------|------|
| 陳偉鳴 | 陳〇〇 | `window.analyticsData.userName` |
| 陳偉鳴 | 陳〇〇 | `window.CurrentName` |
| 陳偉鳴 | 陳〇〇 | `<root-scope-variable>` |
| 陳偉鳴 | 陳〇〇 | 所有文字節點 |

### 視覺效果

| 項目 | 效果 |
|------|------|
| 輸入框背景 | 淺紅色 `#ffebee` |
| Focus 外框 | 亮紅色 `#f44336` + 光暈 |
| Username 上方 | 顯示 `***驗證碼自動 OCR 中***` |
| 驗證碼下方 | 顯示 `***驗證碼自動 OCR 中***` |
| 提示文字 | 閃爍動畫效果 |

### 技術實現

使用 **Chrome DevTools Protocol (CDP)** 的 `Page.addScriptToEvaluateOnNewDocument`：

```python
driver.execute_cdp_cmd(
    'Page.addScriptToEvaluateOnNewDocument',
    {'source': PRE_RENDER_INJECTION_SCRIPT}
)
```

**姓名替換技術**:
```javascript
// 攔截 JavaScript 變數賦值
Object.defineProperty(window, 'analyticsData', {
    set: function(val) {
        if (val && val.userName) {
            val.userName = val.userName.replace('陳偉鳴', '陳〇〇');
        }
        _analyticsData = val;
    }
});
```

這確保腳本在每個頁面的 DOM 載入**之前**執行，實現真正的「渲染前」修改。

## 檔案結構

```
demo/
├── captcha_demo.py      # 主程式
├── credentials.json     # 登入憑證 (需自行修改)
├── README.md            # 本說明文件
└── (執行時產生)
    ├── cookies.json     # Cookie 暫存 (結束時刪除)
    ├── stealth.min.js   # Stealth 腳本 (結束時刪除)
    └── captcha_temp.png # 驗證碼暫存 (結束時刪除)
```

## 使用方式

### 1. 設定登入憑證

編輯 `credentials.json`:

```json
{
    "url": "https://elearn.post.gov.tw/login",
    "username": "你的帳號",
    "password": "你的密碼",
    "repeat_count": 5,
    "wait_after_login": 5
}
```

### 2. 執行程式

```bash
# 啟用 eebot 環境
conda activate eebot

# 執行示範程式
cd research/captcha_ocr_analysis/demo
python captcha_demo.py
```

## 執行流程

```
[1] 提取 stealth.min.js (首次執行)
     ↓
[2] 啟動 Chrome
     ├─ 注入 Stealth JS (繞過檢測)
     └─ 注入樣式腳本 (渲染前生效)
     ↓
[3] 前往登入頁面
     ↓
    ┌──────────────────────────────────┐
    │  【渲染前自動生效】               │
    │  • 輸入框背景: 淺紅色            │
    │  • OCR 提示: username 上方       │
    │  • OCR 提示: 驗證碼下方          │
    │  • 閃爍動畫效果                  │
    └──────────────────────────────────┘
     ↓
[4] 填入帳號
     ↓
[5] 填入密碼
     ↓
[6] 擷取驗證碼圖片
     ↓
[7] ddddocr 辨識驗證碼
     ↓
[8] 填入驗證碼
     ↓
[9] 點擊登入按鈕
     ↓
[10] 檢查登入結果
     ├─ 成功 → 儲存 Cookies → 等待 5 秒 → 下一輪
     └─ 失敗 → 重新整理 → 重試 (最多 3 次)
     ↓
[11] 重複 [2]-[10] 共 5 次
     ↓
[12] 清理暫存檔案
     - cookies.json
     - stealth.min.js
     - captcha_temp.png
```

## 參數說明

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `url` | 登入頁面網址 | - |
| `username` | 登入帳號 | - |
| `password` | 登入密碼 | - |
| `repeat_count` | 重複執行次數 | 5 |
| `wait_after_login` | 登入成功後等待秒數 | 5 |

## 技術細節

### Stealth 模式

使用 `puppeteer-extra-plugin-stealth` 的 evasion 腳本:

```bash
npx extract-stealth-evasions
```

### OCR 引擎

使用 `ddddocr`:
- 支援數字 + 字母混合驗證碼
- 無需訓練，開箱即用
- 準確率約 95%+

### 元素定位

程式會嘗試多個選擇器來定位元素:

```python
USERNAME_SELECTORS = [
    (By.ID, 'user_name'),
    (By.NAME, 'user_name'),
    (By.CSS_SELECTOR, 'input[type="text"]'),
]
```

## 注意事項

1. **首次執行** 需要安裝 Node.js 以提取 stealth.min.js
2. **ChromeDriver** 需要與 Chrome 版本匹配
3. **網站結構** 如果目標網站結構不同，需要調整選擇器
4. **合法使用** 請確保有權限自動化登入目標網站

## 依賴套件

```
selenium
ddddocr
```

## 作者

Claude Code (Opus 4.5) - 2025-12-30
