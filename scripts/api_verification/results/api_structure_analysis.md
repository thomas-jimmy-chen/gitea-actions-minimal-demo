# API 結構分析報告
**生成時間**: 2025-12-05 19:29:17
**API 端點**: GET /api/my-courses
---

## 頂層結構

頂層鍵值: `courses`

## 課程列表 (courses)

**課程數量**: 18

### 第一個課程範例

```json
{
  "academic_year": null,
  "compulsory": true,
  "course_attributes": {
    "published": true,
    "student_count": 25481,
    "teaching_class_name": null
  },
  "course_code": "901011114",
  "course_type": 1,
  "credit": "2.0",
  "department": null,
  "end_date": "2025-12-31",
  "grade": null,
  "id": 465,
  "instructors": [],
  "is_graduated": true,
  "is_manual_registered": false,
  "is_mute": false,
  "klass": null,
  "name": "性別平等工作法、性騷擾防治法及相關子法修法重點與實務案例(114年度)",
  "org": {
    "is_enterprise_or_organization": null
  },
  "org_id": 1,
  "semester": null,
  "start_date": "2025-03-01"
}
```

### 課程物件欄位清單

| 欄位名稱 | 類型 | 範例值 |
|---------|------|--------|
| `academic_year` | NoneType | null |
| `compulsory` | bool | True |
| `course_attributes` | dict | {'published': True, 'student_count': 25481, 'teach |
| `course_code` | str | 901011114 |
| `course_type` | int | 1 |
| `credit` | str | 2.0 |
| `department` | NoneType | null |
| `end_date` | str | 2025-12-31 |
| `grade` | NoneType | null |
| `id` | int | 465 |
| `instructors` | list | null |
| `is_graduated` | bool | True |
| `is_manual_registered` | bool | null |
| `is_mute` | bool | null |
| `klass` | NoneType | null |
| `name` | str | 性別平等工作法、性騷擾防治法及相關子法修法重點與實務案例(114年度) |
| `org` | dict | {'is_enterprise_or_organization': None} |
| `org_id` | int | 1 |
| `semester` | NoneType | null |
| `start_date` | str | 2025-03-01 |

## 結構分析結論

**情境判斷**: 情境 C - 扁平結構，無階層資訊

- ⚠️ API 僅有 `courses` 扁平列表
- ❌ 無 `master_course_id` 或階層資訊
- ⚠️ 只能部分整合
- ⚠️ 建議採用**部分整合策略**

