# test3 考試機制快速參考手冊

> **用途**: 5 分鐘快速了解考試提交機制
> **完整報告**: [TEST3_EXAM_MECHANISM_RESEARCH.md](./TEST3_EXAM_MECHANISM_RESEARCH.md)

---

## 🎯 核心 API

```
POST /api/exams/{exam_id}/submissions
```

---

## 📋 Request Body 結構

```json
{
  "exam_paper_instance_id": 395912,
  "exam_submission_id": 395781,
  "subjects": [
    {
      "subject_id": 2933,
      "subject_updated_at": "2025-02-27T09:26:28Z",
      "answer_option_ids": [9824]
    }
  ],
  "progress": {
    "answered_num": 10,
    "total_subjects": 10
  },
  "reason": "user"
}
```

---

## 🍪 必要 Cookies（6 個）

- **`session`** ⭐⭐⭐⭐⭐ 最重要
- `lang` ⭐⭐⭐
- `_ga` ⭐⭐
- `_ga_227RNMEJEV` ⭐⭐
- `warning%3Achange_password` ⭐
- `warning:verification_email` ⭐

---

## 🔑 關鍵欄位

| 欄位 | 類型 | 來源 | 必需 |
|------|------|------|------|
| `exam_paper_instance_id` | int | GET /exams | ⭐⭐⭐⭐⭐ |
| `exam_submission_id` | int | POST storage | ⭐⭐⭐⭐⭐ |
| `subject_id` | int | GET /exams | ⭐⭐⭐⭐⭐ |
| `subject_updated_at` | string | GET /exams | ⭐⭐⭐⭐ |
| `answer_option_ids` | array<int> | 題庫匹配 | ⭐⭐⭐⭐⭐ |

---

## 📊 完整流程

```
1. GET /api/courses/{course_id}/exams
   → 提取 exam_paper_instance_id, subjects

2. POST /api/exams/{exam_id}/submissions/storage
   → 獲取 exam_submission_id

3. POST /api/exams/{exam_id}/submissions
   → 提交答案，Response: {"submission_id": 395789}

4. POST /statistics/api/user-visits
   → 記錄時長
```

---

## 💡 實作方案

### 推薦：半自動化（方案 B）

**流程**:
1. EEBot 正常進入考試頁面
2. MitmProxy 攔截 GET /exams → 提取題目
3. MitmProxy 攔截 POST submissions → 修改答案為正確

**優點**: ✅ 最簡單、✅ 風險低、✅ 立即可用

**預估**: 4-6 小時

---

## ⚠️ 關鍵限制

- ❌ **無法完全不進入課程**（需要 exam_paper_instance_id）
- ⚠️ **exam_paper_instance_id 有時效性**（每次考試新 ID）
- ⚠️ **需要題庫中有對應的 option_id**

---

## 🔐 安全性

**檢測風險緩解**:
- ✅ 加入隨機延遲（10-30 秒/題）
- ✅ 故意答錯 1-2 題
- ✅ 考試間隔 5-10 分鐘

---

## 📦 相關檔案

- `test3_exam_submission_full.json` - 完整提交資料
- `TEST3_EXAM_MECHANISM_RESEARCH.md` - 詳細報告
- `TEST3_EXAM_FIELD_MAPPING.json` - 欄位對應表

---

**版本**: 1.0 | **日期**: 2025-12-03 | **專案**: EEBot (Gleipnir)
