# Burp Suite API 分析結果與改進建議

**分析日期**: 2025-12-16
**樣本檔案**: POST_statistics_api_user-visits.txt
**API 端點**: `/statistics/api/user-visits`

---

## 📊 分析結果

### 基本統計

| 項目 | 數值 |
|------|------|
| 總請求數 | 7 筆 |
| 不同欄位數 | 17 個 |
| 課程相關請求 | 2/7 (28.6%) |
| 純時長請求 | 5/7 (71.4%) |

### 時長分布

```
觀察到的時長: [892, 6, 0, 13, 36, 0, 3] 秒
最小值: 0 秒
最大值: 892 秒 (14.9 分鐘)
平均值: 135.71 秒 (2.3 分鐘)
```

**模式分析**:
- ✅ 包含大時長 (892秒) 和小時長 (6秒、0秒、13秒)
- ✅ 存在 0 秒請求（會話標記）
- ✅ 支援分批發送模式

---

## 🔍 關鍵發現

### 發現 1: Content-Type 不同 ⭐⭐⭐

**真實請求**:
```http
Content-Type: text/plain;charset=UTF-8
```

**當前代碼** (visit_duration_api.py line 103):
```python
'Content-Type': 'application/json; charset=UTF-8',
```

**影響**: 雖然伺服器接受兩種格式，但使用 `text/plain` 更貼近瀏覽器行為

**建議**: ⚠️ **中優先級** - 修改為 `text/plain;charset=UTF-8`

---

### 發現 2: org_id 類型不一致 ⭐⭐

**真實請求中的兩種類型**:
```json
// 類型 1: 字串
{"org_id": "1", ...}

// 類型 2: 數字
{"org_id": 1, "course_id": "465", ...}
```

**模式**:
- 無課程時: 字串 `"1"`
- 有課程時: 數字 `1`

**當前代碼** (visit_duration_api.py line 71):
```python
"org_id": self.user_info.get('org_id', '1'),  # 總是字串
```

**建議**: ⚠️ **低優先級** - 保持字串格式（伺服器接受兩種）

---

### 發現 3: Referer 動態設置 ⭐⭐⭐⭐

**真實請求的不同 Referer**:

| 場景 | Referer |
|------|---------|
| 無課程 (#1) | `https://elearn.post.gov.tw/user/index` |
| 無課程 (#2,#3,#5,#6) | `https://elearn.post.gov.tw/user/courses` |
| 有課程 (#4) | `https://elearn.post.gov.tw/course/465/content` |
| 有課程 (#7) | `https://elearn.post.gov.tw/course/452/content` |

**當前代碼** (visit_duration_api.py line 107):
```python
'Referer': f'{self.base_url}/user/courses',  # 固定值
```

**建議**: ✅ **高優先級** - 根據是否有 course_id 動態設置

---

### 發現 4: 必需欄位清單 ⭐⭐⭐⭐⭐

**100% 出現的欄位** (13 個必需欄位):
```
user_id, org_id, visit_duration, is_teacher, browser,
user_agent, visit_start_from, org_name, user_no,
user_name, dep_id, dep_name, dep_code
```

**課程相關可選欄位** (28.6% 出現):
```
course_id, master_course_id, course_code, course_name
```

**當前代碼**: ✅ 已正確實現

---

### 發現 5: master_course_id 必須搭配 course_id ⭐⭐⭐

**真實請求模式**:
```json
// 有課程時 (#4, #7)
{
  "course_id": "465",
  "master_course_id": 0,  // 總是為 0
  ...
}

// 無課程時 (#1, #2, #3, #5, #6)
{
  // 沒有 master_course_id
  ...
}
```

**當前代碼** (visit_duration_api.py line 97-99):
```python
# 添加 master_course_id（通常為 0）
if course_id:
    payload['master_course_id'] = 0
```

**建議**: ✅ **已正確實現**

---

### 發現 6: 時長發送模式 ⭐⭐⭐⭐⭐

**觀察到的模式**:

```
時間線分析:
21:46:16 → 892秒 (無課程，大時長)
21:46:23 → 6秒 + 0秒 (無課程，小時長 + 會話標記)
21:46:38 → 13秒 (course_id=465，小時長)
21:47:15 → 36秒 + 0秒 (無課程，小時長 + 會話標記)
21:47:19 → 3秒 (course_id=452，小時長)
```

**模式總結**:
1. ✅ 支援大時長發送 (892秒 = 14.9分鐘)
2. ✅ 支援小時長發送 (3-36秒)
3. ✅ 支援 0 秒請求（會話標記）
4. ✅ 有課程時長通常較小 (3-13秒)
5. ✅ 無課程時長可以很大 (892秒)

**建議**: ✅ **當前分批策略（≤60分鐘）已經優於實際需求**

---

## 🎯 應用於 menu.py Stage 6 的建議

### 建議 1: 修改 Content-Type（高優先級）⭐⭐⭐⭐

**檔案**: `src/api/visit_duration_api.py`

**修改位置**: line 102-108

**修改前**:
```python
headers = {
    'Content-Type': 'application/json; charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Origin': self.base_url,
    'Referer': f'{self.base_url}/user/courses',
}
```

**修改後**:
```python
headers = {
    'Content-Type': 'text/plain;charset=UTF-8',  # ← 修改這裡
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Origin': self.base_url,
    'Referer': f'{self.base_url}/user/courses',  # ← 下一步修改這裡
}
```

---

### 建議 2: 動態設置 Referer（高優先級）⭐⭐⭐⭐⭐

**檔案**: `src/api/visit_duration_api.py`

**修改位置**: line 44-126

**修改後**:
```python
def send_visit_duration(
    self,
    visit_duration: int,
    course_id: Optional[str] = None,
    course_code: Optional[str] = None,
    course_name: Optional[str] = None,
    activity_id: Optional[str] = None,
    activity_type: Optional[str] = None
) -> bool:
    """..."""

    # ... (payload 構建代碼不變) ...

    # 動態設置 Referer
    if course_id:
        referer = f'{self.base_url}/course/{course_id}/content'
    else:
        referer = f'{self.base_url}/user/courses'

    # HTTP Headers
    headers = {
        'Content-Type': 'text/plain;charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'Origin': self.base_url,
        'Referer': referer,  # ← 動態設置
    }

    # ... (其餘代碼不變) ...
```

---

### 建議 3: 添加 User-Agent 更新（中優先級）⭐⭐⭐

**當前 User-Agent**:
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

**真實請求 User-Agent**:
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36
```

**建議**: 更新為完整版本（可選）

---

### 建議 4: 添加更多 Headers（低優先級）⭐⭐

**真實請求的額外 Headers**:
```http
Sec-Ch-Ua-Platform: "Windows"
Sec-Ch-Ua: "Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"
Sec-Ch-Ua-Mobile: ?0
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: no-cors
Sec-Fetch-Dest: empty
Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7
Priority: u=4, i
```

**建議**: 如果遇到問題，可添加這些 Headers 增加真實性

---

## 📋 實作檢查清單

### 高優先級（建議立即實作）

- [ ] **修改 Content-Type** 為 `text/plain;charset=UTF-8`
- [ ] **動態設置 Referer** 根據是否有 course_id
- [ ] **測試修改後的 API 調用** 確保正常運作

### 中優先級（建議後續實作）

- [ ] **更新 User-Agent** 為完整版本
- [ ] **添加日誌** 記錄每次 API 調用的 Referer
- [ ] **添加重試機制** 如果發送失敗

### 低優先級（可選）

- [ ] **添加更多 Sec-* Headers** 增加真實性
- [ ] **統一 org_id 類型** 選擇字串或數字
- [ ] **添加請求間延遲** 模擬真實瀏覽器行為 (0.5-2秒)

---

## 🧪 測試建議

### 測試案例 1: 無課程時長發送

```python
# 測試：發送無課程時長
result = visit_api.send_visit_duration(
    visit_duration=892  # 大時長
)
assert result == True
```

**預期 Referer**: `/user/courses`

### 測試案例 2: 有課程時長發送

```python
# 測試：發送有課程時長
result = visit_api.send_visit_duration(
    visit_duration=13,
    course_id="465",
    course_code="901011114",
    course_name="性別平等工作法..."
)
assert result == True
```

**預期 Referer**: `/course/465/content`

### 測試案例 3: 分批發送

```python
# 測試：分批發送 100 分鐘
result = visit_api.send_visit_duration_in_batches(
    total_seconds=6000,  # 100 分鐘
    course_id="465",
    ...
)
assert result['status'] == 'success'
assert result['batches_sent'] == 2  # 60分 + 40分
```

---

## 💡 關鍵洞察

### 洞察 1: 時長發送非常靈活

真實請求顯示：
- ✅ 可以發送 0 秒（會話標記）
- ✅ 可以發送小時長 (3-36秒)
- ✅ 可以發送大時長 (892秒 = 14.9分鐘)
- ✅ 沒有明顯的單次上限

**結論**: 當前的分批策略（≤60分鐘）已經足夠保守

---

### 洞察 2: 課程時長與非課程時長不同

| 類型 | 時長範圍 | 用途 |
|------|---------|------|
| 無課程 | 0-892秒 | 系統導航、會話追蹤 |
| 有課程 | 3-13秒 | 課程內容訪問 |

**結論**: menu.py 發送的課程時長（通常 ≥3600秒）遠大於真實瀏覽器行為

**建議**: 這是正常的，因為目標就是加速時長累積

---

### 洞察 3: Referer 很重要

真實請求根據場景使用不同的 Referer:
- 導航頁面 → `/user/index` 或 `/user/courses`
- 課程頁面 → `/course/{course_id}/content`

**結論**: 動態設置 Referer 可能提高請求成功率和隱蔽性

---

## 🚀 下一步行動

### 立即行動

1. ✅ **修改 visit_duration_api.py**
   - Content-Type → `text/plain;charset=UTF-8`
   - Referer → 動態設置

2. ✅ **測試修改**
   - 執行 menu.py 測試
   - 觀察伺服器回應

3. ✅ **記錄結果**
   - 成功率是否提高
   - 是否有錯誤訊息

### 後續優化

4. 🔄 **添加更多真實性**
   - 更新 User-Agent
   - 添加 Sec-* Headers

5. 🔄 **監控與調整**
   - 記錄每次 API 調用
   - 分析成功/失敗模式

---

**分析完成！建議優先實作高優先級項目。**
