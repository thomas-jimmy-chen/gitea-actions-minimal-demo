# Burp Suite 姓名替換分析報告

**分析日期**: 2025-12-30
**資料來源**: `20251230-bu.txt`

---

## 1. 目標姓名資訊

| 項目 | 值 |
|------|-----|
| **姓名** | 陳偉鳴 |
| **UTF-8 Bytes** | `e9 99 b3 e5 81 89 e9 b3 b4` |
| **User ID** | 19688 |
| **Org Name** | 郵政ｅ大學 |

---

## 2. 姓名出現的 HTML 頁面

| 端點 | 出現次數 | 類型 |
|------|---------|------|
| `/user/index` | 4 次 | HTML 頁面 |
| `/user/courses` | 4 次 | HTML 頁面 |
| `/course/{id}/content` | 4 次 | HTML 頁面 |
| `/course/{id}/learning-activity/full-screen` | 2 次 | HTML 頁面 |

---

## 3. 姓名在 HTML 中的具體位置

### 3.1 JavaScript user 物件 (位置 ~7313)

```javascript
user: {
    id: 19688,
    name: "陳偉鳴",    // ← 這裡
    userNo: "522673",
    orgId: 1
}
```

### 3.2 AngularJS root-scope-variable (位置 ~9839)

```html
<root-scope-variable name="currentUserName" value="陳偉鳴"></root-scope-variable>
```

### 3.3 AngularJS ng-init (位置 ~10257)

```html
ng-init="userCurrentName='陳偉鳴'; orgName='郵政ｅ大學'; deliveryOrg='TW-POST'"
```

### 3.4 window.analyticsData (位置 ~168471)

```javascript
window.analyticsData = {
    orgName: '郵政ｅ大學',
    userId: '19688',
    userName: '陳偉鳴'    // ← 這裡
}
```

### 3.5 CurrentName 變數

```javascript
CurrentName='陳偉鳴';
orgName='郵政ｅ大學';
deliveryOrg='TW-POST';
```

---

## 4. MitmProxy 替換方案

### 4.1 攔截條件

```python
# 條件
Host: elearn.post.gov.tw
Path: 任何路徑 (或限制 /user/, /course/)
Content-Type: text/html
```

### 4.2 攔截器程式碼

```python
"""
mitmproxy 姓名替換攔截器
使用方式: mitmdump -s name_replacer.py
"""
from mitmproxy import http


class NameReplacer:
    """替換 HTML 響應中的用戶姓名"""

    def __init__(self):
        # 原始姓名 (要被替換的)
        self.original_name = "陳偉鳴"
        # 替換為遮蔽版本 (使用 U+3007 國字零)
        self.replacement_name = "陳〇〇"

    def response(self, flow: http.HTTPFlow):
        # 只處理 elearn.post.gov.tw
        if "elearn.post.gov.tw" not in flow.request.host:
            return

        # 只處理 HTML 響應
        content_type = flow.response.headers.get("content-type", "")
        if "text/html" not in content_type:
            return

        # 取得 response body
        try:
            body = flow.response.get_text()
        except Exception:
            return

        # 替換姓名
        if self.original_name in body:
            body = body.replace(self.original_name, self.replacement_name)
            flow.response.set_text(body)
            print(f"[NameReplacer] 已替換 {flow.request.path}")


addons = [NameReplacer()]
```

---

## 5. 重要說明

### 5.1 替換時機

- **在網頁渲染之前**: MitmProxy 攔截的是 HTTP 響應，在瀏覽器收到 HTML 之前就已經替換完成
- **前端 JavaScript 會使用替換後的值**: 因為 `user.name`、`currentUserName` 等變數值都在 HTML 中定義

### 5.2 需要注意的地方

1. **只替換 HTML 頁面**: JSON API 響應不需要替換（姓名在 HTML 中嵌入，不是從 API 動態載入）
2. **編碼問題**: 確保 Python 腳本使用 UTF-8 編碼保存
3. **4 個位置全部會被替換**: 使用簡單的字串替換即可覆蓋所有位置

### 5.3 驗證方式

替換後可在瀏覽器開發者工具中檢查：

```javascript
// 在 Console 中執行
console.log(window.analyticsData.userName);  // 應該顯示替換後的名字
console.log(CurrentName);                     // 應該顯示替換後的名字
```

---

## 6. 相關檔案

| 檔案 | 說明 |
|------|------|
| `20251230-bu.txt` | Burp Suite 原始資料 |
| `analyze_burp_names.py` | 分析腳本 |
| `src/api/interceptors/` | 現有 mitmproxy 攔截器目錄 |

---

## 7. 登入頁面樣式修改

### 7.1 需求

1. **輸入欄位樣式**:
   - 背景色: 淺紅色 (`#ffebee`)
   - 邊框: 紅色 (`#e57373`)
   - Focus 時: 亮紅色邊框 (`#f44336`) + 紅色光暈

2. **OCR 提示文字**:
   - Username 欄位上方: `***驗證碼自動 OCR 中***`
   - 驗證碼欄位下方: `***驗證碼自動 OCR 中***`

### 7.2 目標元素

| 欄位 | 選擇器 | HTML 位置 |
|------|--------|----------|
| 帳號 | `#user_name` | 第 70 行 |
| 密碼 | `#password` | 第 87 行 |
| 驗證碼 | `input[name="captcha_code"]` | 第 95 行 |

### 7.3 攔截器位置

```
src/api/interceptors/login_style_modifier.py
```

### 7.4 注入內容

**CSS 樣式**:
```css
/* 淺紅色背景 */
#user_name, #password, input[name="captcha_code"] {
    background-color: #ffebee !important;
    border: 2px solid #e57373 !important;
}

/* Focus 時亮紅色外框 */
#user_name:focus, #password:focus, input[name="captcha_code"]:focus {
    background-color: #ffcdd2 !important;
    border-color: #f44336 !important;
    box-shadow: 0 0 8px rgba(244, 67, 54, 0.6) !important;
}

/* OCR 提示文字 - 閃爍動畫 */
.eebot-ocr-notice {
    text-align: center;
    color: #d32f2f;
    font-weight: bold;
    animation: eebot-blink 1.5s ease-in-out infinite;
}
```

**HTML 注入位置**:
```
[login-tip div]
<div class="eebot-ocr-notice">***驗證碼自動 OCR 中***</div>  ← 注入
[username input]
...
[captcha-verification div]
<div class="eebot-ocr-notice">***驗證碼自動 OCR 中***</div>  ← 注入
[find-password div]
```

---

**分析完成** ✅
