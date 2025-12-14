# 課程詳細 API 探索報告

**生成時間**: 2025-12-05 21:50:01

---

## 執行摘要

| 項目 | 結果 |
|------|------|
| **測試端點數量** | 7 |
| **成功端點數量** | 2 |
| **成功率** | 28.6% |

---

## 測試結果


### 1. /api/courses/465

- **狀態**: ✅ 成功
- **狀態碼**: 200
- **回應大小**: 1729 bytes
- **格式**: JSON
- **欄位數量**: 28
- **欄位**: academic_year, allow_admin_update_basic_info, allow_update_basic_info, allowed_to_invite_assistant, allowed_to_invite_student, allowed_to_join_course, classroom_schedule, compulsory, course_code, course_outline, course_type, cover, created_user, credit, department
  ... 及其他 13 個欄位

### 2. /api/courses/465/details

- **狀態**: ❌ 失敗
- **狀態碼**: 404

### 3. /api/courses/465/modules

- **狀態**: ✅ 成功
- **狀態碼**: 200
- **回應大小**: 240 bytes
- **格式**: JSON
- **欄位數量**: 1
- **欄位**: modules

### 4. /api/courses/465/requirements

- **狀態**: ❌ 失敗
- **狀態碼**: 404

### 5. /api/courses/465/info

- **狀態**: ❌ 失敗
- **狀態碼**: 404

### 6. /api/my-courses/465

- **狀態**: ❌ 失敗
- **狀態碼**: 404

### 7. /api/course/465

- **狀態**: ❌ 失敗
- **狀態碼**: 404

---

## 結論

### ⚠️ 找到 2 個有效端點，但都不包含通過條件

雖然找到有效的 API 端點，但它們都不包含以下相關欄位：
- `required_duration` / `duration_requirement` / `required_time`
- `required_score` / `score_requirement` / `pass_score`
- `requirements` / `pass_requirements` / `completion_requirements`

**建議**: 改用 Selenium 從頁面提取通過條件（XPath）。

---

**報告結束**
