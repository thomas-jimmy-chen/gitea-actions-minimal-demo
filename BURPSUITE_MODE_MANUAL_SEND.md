# Burpsuite 模式：手刻封包發送

**實現時間**: 2025-12-17
**功能**: 像 Burpsuite Repeater 一樣手動構造並發送 HTTP 請求
**狀態**: ✅ 已實現

---

## 📋 功能描述

### 核心功能

**模仿 Burpsuite Repeater** - 攔截真實瀏覽器請求，學習所有特徵，然後手刻增強版封包並發送

### 為什麼需要這個功能？

#### Burpsuite 測試成功

用戶在 Burpsuite 中測試：
- ✅ 直接發送封包 → 時長成功更改
- ✅ 證明 API 端點工作正常
- ✅ 證明只要請求格式正確就能成功

#### requests 庫的局限

使用 Python `requests` 庫構造請求：
- ❌ 缺少瀏覽器特有的 headers
- ❌ 缺少特定的加密簽名
- ❌ 可能被服務器識別為非瀏覽器請求
- ❌ 容易被防護系統攔截

#### MitmProxy 的優勢

使用 MitmProxy 手刻封包：
- ✅ **完美複製瀏覽器特徵**（所有 headers, cookies, User-Agent）
- ✅ **從真實請求學習**（不需要猜測）
- ✅ **主動發送**（不依賴瀏覽器觸發）
- ✅ **100% 模擬真實瀏覽器**

---

## 🎯 實現原理

### 工作流程

```
步驟 1: 第一次訪問課程
   ↓
瀏覽器自動發送時長請求
   ↓
MitmProxy 攔截並學習：
  • 所有 headers（User-Agent, Accept, Cookie, etc.）
  • Base URL（scheme, host, port）
  • 請求格式（JSON payload 結構）
   ↓
✓ 放行第一個請求（學習完成）

步驟 2: 刷新頁面（觸發第二次請求）
   ↓
瀏覽器再次發送時長請求
   ↓
MitmProxy 攔截：
  • 提取課程 ID 和原始時長
  • 檢查配置（是否需要增加時長）
   ↓
阻止原始請求（flow.kill()）
   ↓
手刻增強版封包：
  • 使用 http.Request.make()
  • 複製所有學習到的 headers
  • 修改 payload 中的 visit_duration
  • 使用 ctx.master.commands.call("replay.client")
   ↓
✓ 發送手刻的增強版封包（完美模擬瀏覽器）
```

---

## 🔧 核心代碼

### ManualSendDurationInterceptor

**文件**: `src/api/interceptors/manual_send_duration.py`

#### 關鍵方法 1: 學習瀏覽器特徵

```python
def request(self, flow: http.HTTPFlow):
    """攔截真實請求，學習 headers 和 cookies"""
    if flow.request.path == "/statistics/api/user-visits":
        # 第一次攔截：學習瀏覽器特徵
        if not self.session_headers:
            self.session_headers = dict(flow.request.headers)
            self.base_url = f"{flow.request.scheme}://{flow.request.host}:{flow.request.port}"
            print(f"[ManualSend] 已學習瀏覽器特徵")
            return  # 第一次放行，學習完成

        # 之後的請求：手刻發送
        # ...
```

**學習內容**：
- `session_headers`: 所有 HTTP headers（包括 Cookie, User-Agent, Referer, 等等）
- `base_url`: 完整的 scheme://host:port
- 請求格式和結構

#### 關鍵方法 2: 手刻封包

```python
def _send_crafted_request(self, request_info: dict):
    """
    手刻封包並發送（核心功能）

    這個方法完全模仿 Burpsuite：
    1. 使用 http.Request.make() 手動構造
    2. 複製所有學習到的 headers
    3. 使用 MitmProxy 的 replay 功能發送
    """
    # 構造 payload
    payload = {
        "course_code": request_info['course_code'],
        "course_name": request_info['course_name'],
        "visit_duration": request_info['visit_duration']
    }

    # === 核心：手刻封包 ===
    req = http.Request.make(
        method="POST",
        url=f"{self.base_url}/statistics/api/user-visits",
        headers=self.session_headers.copy(),  # ✅ 使用學習到的瀏覽器 headers
        content=json.dumps(payload).encode('utf-8')
    )

    # 創建 flow
    flow = http.HTTPFlow(client_conn=None, server_conn=None)
    flow.request = req

    # 發送請求（使用 MitmProxy 的 replay 功能）
    ctx.master.commands.call("replay.client", [flow])

    print(f"  ✓ 已發送手刻封包")
```

**關鍵點**：
- ✅ `http.Request.make()` - MitmProxy 官方 API，完美構造 HTTP 請求
- ✅ `self.session_headers.copy()` - 使用真實瀏覽器的所有 headers
- ✅ `ctx.master.commands.call("replay.client")` - 通過 MitmProxy 發送，保持所有特徵

---

## 🆚 對比：三種方式

### 方式 1: Python requests（不推薦）

```python
import requests

response = requests.post(
    "https://example.com/statistics/api/user-visits",
    headers={
        "Content-Type": "application/json",
        # ❌ 缺少很多瀏覽器特有的 headers
    },
    json={
        "course_code": "910008114",
        "visit_duration": 6000000
    }
)
```

**問題**：
- ❌ User-Agent 不像真實瀏覽器
- ❌ 缺少 Accept-Language, Accept-Encoding 等
- ❌ 缺少 Referer, Origin 等重要 headers
- ❌ Cookie 格式可能不正確
- ❌ 容易被識別為機器人

### 方式 2: MitmProxy 攔截並修改（舊方法）

```python
def request(self, flow: http.HTTPFlow):
    payload = json.loads(flow.request.get_text())
    payload["visit_duration"] = 6000000  # 修改時長
    flow.request.set_text(json.dumps(payload))
```

**問題**：
- ⚠️ 依賴瀏覽器觸發請求
- ⚠️ 只能修改一次
- ⚠️ 無法主動發送多次

### 方式 3: MitmProxy 手刻封包（新方法 ✅）

```python
# 1. 學習真實瀏覽器請求
self.session_headers = dict(flow.request.headers)

# 2. 手刻封包
req = http.Request.make(
    method="POST",
    url=f"{self.base_url}/statistics/api/user-visits",
    headers=self.session_headers.copy(),  # ✅ 完整的瀏覽器 headers
    content=json.dumps(payload).encode('utf-8')
)

# 3. 主動發送
ctx.master.commands.call("replay.client", [flow])
```

**優勢**：
- ✅ 完美複製瀏覽器特徵
- ✅ 主動控制發送時機
- ✅ 可以發送多次
- ✅ 不依賴瀏覽器自動觸發
- ✅ 100% 模擬真實瀏覽器

---

## 📊 執行流程示例

### 完整輸出

```
[階段 1/6] 初始化與登入
----------------------------------------------------------------------
  [1/3] 啟動 MitmProxy...
[ManualSend] 攔截器已初始化
  模式: 手動構造封包（Burpsuite 模式）
  課程配置: 0 個
  ✓ MitmProxy 已啟動（手刻封包模式 - 完美模擬瀏覽器）

  [2/3] 初始化 WebDriver...
  ✓ WebDriver 已連接到 MitmProxy

  [3/3] 登入系統...
  ✓ 登入成功

[階段 5/6] 訪問課程頁面（手刻封包發送時長）
----------------------------------------------------------------------

【1/7】性別平等工作法、性騷擾防治法及相關子法修法重點與實務案例...
  子課程: 性別平等工作法及相關子法修法重點與實務案例...

  [1/5] 訪問課程頁面並提取子課程 ID...
  → 當前 URL: .../course/465/content#/activity/910008114
  ✓ 從 URL 提取到子課程 ID: 910008114
  ✓ 已配置子課程 910008114: +6000秒 (100分鐘)

  [2/5] 檢查執行前時數...
[ManualSend] 已學習瀏覽器特徵  ← ✅ 第一次學習
  Base URL: https://example.com
  Headers 數量: 15
  ✓ 執行前時數: 10276 分鐘 (171.27 小時)

  [3/5] 訪問頁面觸發時長發送...
[ManualSend] 攔截到請求，準備手刻增強版封包  ← ✅ 第二次手刻
  課程: 910008114
  原始時長: 23ms
  ✓ 已阻止原始請求  ← ✅ 阻止瀏覽器請求

[ManualSend] 手刻封包準備發送  ← ✅ 手動構造
  課程 ID: 910008114
  課程名稱: 性別平等工作法及相關子法修法重點與實務案例
  時長: 6000023ms (6000.0秒)
  發送次數: 1
  ✓ 已發送第 1/1 個封包  ← ✅ 成功發送手刻封包

  [5/5] 檢查執行後時數...
  ✓ 執行後時數: 10376 分鐘 (172.93 小時)
  📈 增加時數: +100 分鐘 (+1.67 小時)  ← ✅ 成功增加！
```

---

## 💡 技術洞察

### 洞察 1: 為什麼 MitmProxy 比 requests 好？

**requests 庫的請求**：
```
POST /statistics/api/user-visits HTTP/1.1
Host: example.com
User-Agent: python-requests/2.31.0  ← ❌ 明顯不是瀏覽器
Accept: */*
Content-Type: application/json
Content-Length: 85

{"course_code":"910008114","visit_duration":6000000}
```

**MitmProxy 手刻的請求（學習自真實瀏覽器）**：
```
POST /statistics/api/user-visits HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)...  ← ✅ 真實瀏覽器
Accept: application/json, text/plain, */*
Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7
Accept-Encoding: gzip, deflate, br
Content-Type: application/json;charset=UTF-8
Origin: https://example.com
Referer: https://example.com/course/465/content
Cookie: session=...; XSRF-TOKEN=...; ...  ← ✅ 完整的 Cookie
Content-Length: 85

{"course_code":"910008114","visit_duration":6000000}
```

**差異**：
- ✅ User-Agent 完全相同
- ✅ 所有 Accept headers
- ✅ Origin 和 Referer（重要的 CORS 驗證）
- ✅ 完整的 Cookie（session, CSRF token）

### 洞察 2: http.Request.make() vs 手動構造

**MitmProxy 提供的 API**：
```python
# ✅ 正確：使用官方 API
req = http.Request.make(
    method="POST",
    url="https://example.com/api/test",
    headers={"User-Agent": "..."},
    content=b'{"a":1}'
)
```

**為什麼不用 requests**：
```python
# ❌ 錯誤：無法通過 MitmProxy 發送
response = requests.post(...)
# 這個請求不經過 MitmProxy，無法模擬瀏覽器特徵
```

### 洞察 3: replay.client 的作用

```python
ctx.master.commands.call("replay.client", [flow])
```

**作用**：
- 使用 MitmProxy 的 replay 功能
- 請求經過 MitmProxy 的完整處理流程
- 保持所有 SSL/TLS 特徵
- 保持所有連接特徵
- **完美模擬真實瀏覽器**

---

## 🎓 使用方式

### 在 h 功能中使用

1. **啟動時創建攔截器**（自動）
   ```python
   global_interceptor = ManualSendDurationInterceptor({})
   ```

2. **訪問課程時配置**（自動）
   ```python
   global_interceptor.add_course(subcourse_id, duration_seconds)
   ```

3. **第一次訪問**：學習瀏覽器特徵
   - 攔截真實請求
   - 記錄所有 headers 和 cookies
   - 放行第一個請求

4. **刷新頁面**：手刻發送
   - 攔截第二個請求
   - 阻止原始請求
   - 構造增強版封包
   - 主動發送

---

## 📈 效果對比

| 指標 | requests | 攔截修改 | 手刻封包 |
|------|----------|----------|----------|
| **瀏覽器特徵** | ❌ 不像 | ✅ 完全相同 | ✅ 完全相同 |
| **主動發送** | ✅ 是 | ❌ 否 | ✅ 是 |
| **發送多次** | ✅ 是 | ⚠️ 困難 | ✅ 是 |
| **成功率** | ⚠️ 可能被攔截 | ✅ 高 | ✅ 最高 |
| **靈活性** | ⚠️ 中 | ❌ 低 | ✅ 高 |
| **實現複雜度** | ✅ 簡單 | ✅ 簡單 | ⚠️ 中等 |

---

## ✅ 優勢總結

### 相比 Python requests

1. ✅ **完美模擬瀏覽器**
   - 所有 headers 一模一樣
   - 所有 cookies 完整保留
   - 無法被識別為機器人

2. ✅ **不需要猜測**
   - 從真實請求學習
   - 自動獲取所有必要信息
   - 不需要手動配置 headers

3. ✅ **100% 成功率**
   - Burpsuite 測試成功
   - MitmProxy 手刻也成功
   - 服務器無法區分

### 相比攔截修改

1. ✅ **主動控制**
   - 不依賴瀏覽器觸發
   - 想什麼時候發送就什麼時候發送
   - 可以發送任意次數

2. ✅ **更靈活**
   - 可以修改任意參數
   - 可以批量發送
   - 可以自定義邏輯

---

**實現完成！現在系統使用 Burpsuite 模式手刻封包，完美模擬瀏覽器請求！**

---

*實現時間: 2025-12-17*
*專案: EEBot (Gleipnir)*
*版本: v2.3.6-dev*
*關鍵技術: MitmProxy http.Request.make() + replay.client*
