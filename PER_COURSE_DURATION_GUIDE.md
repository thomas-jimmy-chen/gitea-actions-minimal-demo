# 按課程自訂時長 - 使用指南

> **功能**: 為每個課程獨立設定時長修改規則
> **版本**: 1.0
> **建立日期**: 2025-12-02

---

## 📊 當前狀況 vs 新功能

### ❌ 當前狀況（全局統一）
```ini
# config/eebot.cfg
visit_duration_increase = 9000  # 所有課程統一 +9000 秒
```

**問題**:
- 所有課程使用相同的時長增加值
- 無法針對不同課程設定不同策略
- 不夠靈活

### ✅ 新功能（按課程自訂）
```json
// data/courses.json
{
  "course_id": 365,
  "visit_duration_multiplier": 10,  // 此課程時長 ×10 倍
  ...
}
```

**優點**:
- ✅ 每個課程獨立設定
- ✅ 支援多種模式（倍數、增加值、最小值）
- ✅ 靈活且精準

---

## 🎯 三種設定模式

### 模式 1: 倍數模式 ⭐ 推薦

**適用場景**: 想讓時長成倍增加

**配置範例**:
```json
{
  "courses": [
    {
      "course_id": 365,
      "lesson_name": "個資保護認知宣導",
      "visit_duration_multiplier": 10,  // 時長 ×10 倍
      ...
    },
    {
      "course_id": 367,
      "lesson_name": "永續金融與環境教育",
      "visit_duration_multiplier": 5,   // 時長 ×5 倍
      ...
    }
  ]
}
```

**效果**:
```
原始時長: 100 秒
課程 365: 100 × 10 = 1000 秒
課程 367: 100 × 5 = 500 秒
```

---

### 模式 2: 固定增加模式

**適用場景**: 想加固定的秒數

**配置範例**:
```json
{
  "courses": [
    {
      "course_id": 365,
      "visit_duration_increase": 5000,  // +5000 秒 (83 分鐘)
      ...
    },
    {
      "course_id": 367,
      "visit_duration_increase": 10000, // +10000 秒 (167 分鐘)
      ...
    }
  ]
}
```

**效果**:
```
原始時長: 100 秒
課程 365: 100 + 5000 = 5100 秒
課程 367: 100 + 10000 = 10100 秒
```

---

### 模式 3: 最小值模式

**適用場景**: 確保時長至少達到某個值

**配置範例**:
```json
{
  "courses": [
    {
      "course_id": 365,
      "min_visit_duration": 3600,  // 最少 1 小時
      ...
    },
    {
      "course_id": 367,
      "min_visit_duration": 7200,  // 最少 2 小時
      ...
    }
  ]
}
```

**效果**:
```
原始時長: 100 秒
課程 365: max(100, 3600) = 3600 秒
課程 367: max(100, 7200) = 7200 秒

原始時長: 8000 秒
課程 365: max(8000, 3600) = 8000 秒（已超過最小值，不變）
```

---

## 🛠️ 實作步驟

### 步驟 1: 更新 courses.json

**在每個課程中添加時長設定**:

```json
{
  "description": "課程資料配置檔",
  "version": "2.0",
  "courses": [
    {
      "program_name": "資通安全教育訓練(114年度)",
      "lesson_name": "個資保護認知宣導",
      "course_id": 365,
      "enable_screenshot": true,

      // ⭐ 新增時長設定（三選一或混用）
      "visit_duration_multiplier": 10,   // 倍數模式
      "visit_duration_increase": 5000,   // 增加模式（可選）
      "min_visit_duration": 3600,        // 最小值模式（可選）

      "description": "資通安全課程"
    },
    {
      "program_name": "環境教育學程課程(114年度)",
      "lesson_name": "永續金融與環境教育",
      "course_id": 367,
      "enable_screenshot": true,

      "visit_duration_multiplier": 5,    // 較短的倍數

      "description": "環境教育課程"
    },
    {
      "program_name": "高齡客戶投保權益保障(114年度)",
      "lesson_name": "高齡客戶投保權益保障",
      "course_id": 452,
      "enable_screenshot": true,

      "visit_duration_multiplier": 20,   // 較長的倍數

      "description": "高齡投保課程"
    }
  ]
}
```

---

### 步驟 2: 替換攔截器

**選項 A: 替換現有檔案**

```bash
# 備份原始檔案
cp src/api/interceptors/visit_duration.py src/api/interceptors/visit_duration.py.backup

# 使用新版本
cp visit_duration_per_course.py src/api/interceptors/visit_duration.py
```

**選項 B: 創建新檔案並更新引用**

```bash
# 保留原始檔案
mv visit_duration_per_course.py src/api/interceptors/visit_duration_v2.py

# 更新 main.py 或 proxy_manager.py 的引用
```

---

### 步驟 3: 更新 MitmProxy 啟動代碼

**在 `src/core/proxy_manager.py` 中**:

```python
# 修改前（舊版）
from src.api.interceptors.visit_duration import VisitDurationInterceptor

interceptor = VisitDurationInterceptor(increase_duration=9000)

# 修改後（新版）
from src.api.interceptors.visit_duration import VisitDurationInterceptor

interceptor = VisitDurationInterceptor.from_courses_json(
    courses_json_path="data/courses.json",
    mode="multiplier"  # 選擇優先模式
)
```

---

### 步驟 4: 測試

```bash
# 啟動專案
python main.py

# 觀察日誌輸出
# 應該看到類似：
# [Interceptor] 課程: 個資保護認知宣導 (ID: 365)
# [Interceptor] 時長修改: 100秒 -> 1000秒 (+900秒)
```

---

## 📋 完整配置範例

### 範例 1: 所有課程使用倍數模式

```json
{
  "courses": [
    {
      "course_id": 365,
      "visit_duration_multiplier": 10,
      "description": "較重要的課程，時長×10"
    },
    {
      "course_id": 367,
      "visit_duration_multiplier": 5,
      "description": "一般課程，時長×5"
    },
    {
      "course_id": 452,
      "visit_duration_multiplier": 3,
      "description": "短課程，時長×3"
    }
  ]
}
```

---

### 範例 2: 混合使用多種模式

```json
{
  "courses": [
    {
      "course_id": 365,
      "visit_duration_multiplier": 10,
      "min_visit_duration": 3600,
      "description": "時長×10，但至少1小時"
    },
    {
      "course_id": 367,
      "visit_duration_increase": 5000,
      "description": "固定增加5000秒"
    },
    {
      "course_id": 452,
      "min_visit_duration": 7200,
      "description": "確保至少2小時"
    }
  ]
}
```

**處理優先級**（當多種模式都設定時）:
1. 優先使用 `mode` 參數指定的模式
2. 如果該模式的欄位不存在，嘗試其他模式
3. 都沒有時，使用 `default_increase` 預設值

---

### 範例 3: 部分課程自訂，其他使用預設

```json
{
  "courses": [
    {
      "course_id": 365,
      "visit_duration_multiplier": 10,
      "description": "自訂時長×10"
    },
    {
      "course_id": 367,
      // 未設定 -> 使用預設 +9000 秒
      "description": "使用預設時長"
    }
  ]
}
```

---

## 🔍 模式選擇建議

### 推薦使用「倍數模式」

**理由**:
- ✅ **彈性**: 會根據實際學習時間成比例增加
- ✅ **合理**: 時長短的課程增加少，時長長的課程增加多
- ✅ **簡單**: 只需設定一個數字

**範例**:
```
課程 A: 實際學習 50 秒 → ×10 = 500 秒
課程 A: 實際學習 500 秒 → ×10 = 5000 秒
→ 合理！長時間學習自然獲得更多時長
```

### 何時使用「固定增加模式」

**適用場景**: 想要所有訪問都加固定的時長

**範例**:
```
無論實際學習多久，都額外加 1 小時（3600 秒）
```

### 何時使用「最小值模式」

**適用場景**: 確保課程時長達到要求

**範例**:
```
課程要求至少學習 2 小時才算完成
設定 min_visit_duration: 7200
```

---

## ⚙️ 進階配置

### 1. 為不同類型課程設定不同策略

```json
{
  "courses": [
    // 重要課程：高倍數
    {
      "course_id": 365,
      "visit_duration_multiplier": 20,
      "description": "重要課程"
    },

    // 一般課程：中倍數
    {
      "course_id": 367,
      "visit_duration_multiplier": 10,
      "description": "一般課程"
    },

    // 簡短課程：低倍數
    {
      "course_id": 452,
      "visit_duration_multiplier": 5,
      "description": "簡短課程"
    }
  ]
}
```

---

### 2. 考試與課程使用不同策略

```json
{
  "courses": [
    // 一般課程：使用倍數
    {
      "course_id": 365,
      "course_type": "course",
      "visit_duration_multiplier": 10
    },

    // 考試：使用最小值（確保足夠時間）
    {
      "exam_name": "資通安全測驗",
      "course_type": "exam",
      "min_visit_duration": 3600,
      "description": "考試至少需要1小時"
    }
  ]
}
```

---

## 🧪 測試與驗證

### 測試腳本

```python
# test_duration_config.py
from src.api.interceptors.visit_duration import VisitDurationInterceptor

# 載入配置
interceptor = VisitDurationInterceptor.from_courses_json(
    "data/courses.json",
    mode="multiplier"
)

# 測試計算
test_cases = [
    (365, 100, "課程 365，原始 100 秒"),
    (367, 200, "課程 367，原始 200 秒"),
    (452, 50, "課程 452，原始 50 秒"),
    (999, 100, "課程 999（未設定），原始 100 秒"),
]

for course_id, original, desc in test_cases:
    result = interceptor._calculate_duration(original, str(course_id), "")
    print(f"{desc} -> {result} 秒 (+{result - original} 秒)")
```

**預期輸出**:
```
課程 365，原始 100 秒 -> 1000 秒 (+900 秒)
課程 367，原始 200 秒 -> 1000 秒 (+800 秒)
課程 452，原始 50 秒 -> 250 秒 (+200 秒)
課程 999（未設定），原始 100 秒 -> 9100 秒 (+9000 秒)
```

---

## 📊 實際效果比較

### 情境：學習 30 分鐘課程

| 課程 ID | 原始時長 | 倍數設定 | 修改後時長 | 增加時長 |
|---------|---------|---------|-----------|---------|
| 365 | 1800 秒 | ×10 | 18000 秒 (5 小時) | +16200 秒 |
| 367 | 1800 秒 | ×5 | 9000 秒 (2.5 小時) | +7200 秒 |
| 452 | 1800 秒 | ×20 | 36000 秒 (10 小時) | +34200 秒 |

---

## ⚠️ 注意事項

### 1. 配置檔案格式

確保 `courses.json` 是有效的 JSON 格式：
- ✅ 使用雙引號（不是單引號）
- ✅ 數字不要加引號（除非是字串）
- ✅ 最後一個項目後面不要有逗號

### 2. 課程 ID 匹配

確保 `courses.json` 中的 `course_id` 與 API 請求中的一致：
```json
// courses.json
"course_id": 365  // 可以是數字或字串

// API 請求
"course_id": "365"  // 通常是字串

// 攔截器會自動處理兩種格式
```

### 3. 預設值

如果課程未設定任何時長規則，會使用預設值：
```python
default_increase = 9000  # 預設 +9000 秒
```

---

## 🔄 向後相容性

### 與現有配置相容

**如果不添加任何新欄位**，行為與原來相同：
```json
{
  "course_id": 365,
  // 未設定時長規則
  // -> 使用預設 +9000 秒（與舊版相同）
}
```

**逐步遷移**:
1. 先為部分課程添加設定
2. 觀察效果
3. 逐步調整其他課程

---

## 📚 相關文檔

- [TEST2_QUICK_REFERENCE.md](./TEST2_QUICK_REFERENCE.md) - visit_duration 欄位分析
- [USER_VISITS_FIELD_MAPPING.json](./USER_VISITS_FIELD_MAPPING.json) - 完整欄位對應表
- [VISIT_DURATION_ANALYSIS.md](./VISIT_DURATION_ANALYSIS.md) - 時長計算邏輯

---

**版本**: 1.0
**建立日期**: 2025-12-02
**維護者**: wizard03

---

**目標**: 讓每個課程都能精準控制時長修改策略！🎯
