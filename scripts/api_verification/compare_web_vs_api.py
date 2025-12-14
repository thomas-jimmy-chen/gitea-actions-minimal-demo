#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Web Scan vs API Scan 資料一致性比對
比對 Selenium Web Scan 與 API 資料的差異與匹配度

創建日期: 2025-12-05
用途: 評估如何整合 Web Scan 與 API Scan 資料
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# 添加專案根目錄到 Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class DataComparator:
    """Web Scan 與 API Scan 資料比對器"""

    def __init__(self):
        """初始化比對器"""
        self.web_data = None
        self.api_data = None
        self.comparison_results = {
            'matched': [],
            'unmatched_web': [],
            'unmatched_api': [],
            'field_mapping': {}
        }

    def step1_load_web_scan_data(self):
        """Step 1: 載入 Web Scan 資料"""
        print("=" * 60)
        print("[Step 1/5] 載入 Web Scan 資料...")
        print("=" * 60)

        web_file = PROJECT_ROOT / 'data' / 'courses.json'

        if not web_file.exists():
            print(f"[ERROR] Web Scan 資料不存在: {web_file}")
            print("[HINT] 這是 Selenium 掃描的課程資料")
            sys.exit(1)

        try:
            with open(web_file, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                # 只取一般課程，排除考試
                self.web_data = [
                    c for c in data.get('courses', [])
                    if c.get('course_type') != 'exam'
                ]

            print(f"[SUCCESS] 載入 {len(self.web_data)} 個 Web Scan 課程")
            print(f"[INFO] 資料來源: {web_file}")

            # 顯示範例
            if self.web_data:
                example = self.web_data[0]
                print("\n[DEBUG] Web Scan 資料範例:")
                print(f"  - program_name: {example.get('program_name')}")
                print(f"  - lesson_name: {example.get('lesson_name')}")
                print(f"  - course_id: {example.get('course_id')}")

        except Exception as e:
            print(f"[ERROR] 載入 Web Scan 資料失敗: {e}")
            sys.exit(1)

        print()

    def step2_load_api_data(self):
        """Step 2: 載入 API 資料"""
        print("=" * 60)
        print("[Step 2/5] 載入 API 資料...")
        print("=" * 60)

        api_file = PROJECT_ROOT / 'scripts' / 'api_verification' / 'results' / 'api_response.json'

        if not api_file.exists():
            print(f"[ERROR] API 資料不存在: {api_file}")
            print("[HINT] 請先執行 test_my_courses_api.py")
            sys.exit(1)

        try:
            with open(api_file, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                self.api_data = data.get('courses', [])

            print(f"[SUCCESS] 載入 {len(self.api_data)} 個 API 課程")
            print(f"[INFO] 資料來源: {api_file}")

            # 顯示範例
            if self.api_data:
                example = self.api_data[0]
                print("\n[DEBUG] API 資料範例:")
                print(f"  - id: {example.get('id')}")
                print(f"  - name: {example.get('name')}")
                print(f"  - course_code: {example.get('course_code')}")

        except Exception as e:
            print(f"[ERROR] 載入 API 資料失敗: {e}")
            sys.exit(1)

        print()

    def step3_match_courses(self):
        """Step 3: 匹配課程資料"""
        print("=" * 60)
        print("[Step 3/5] 匹配課程資料...")
        print("=" * 60)
        print("[INFO] 匹配策略: course_id (Web) == id (API)")
        print()

        # 建立 API 資料的索引（用 id 作為 key）
        api_index = {course['id']: course for course in self.api_data}

        matched_count = 0
        unmatched_count = 0

        for web_course in self.web_data:
            course_id = web_course.get('course_id')

            if course_id in api_index:
                # 找到匹配
                api_course = api_index[course_id]
                self.comparison_results['matched'].append({
                    'web': web_course,
                    'api': api_course
                })
                matched_count += 1

                # 刪除已匹配的 API 課程
                del api_index[course_id]
            else:
                # Web Scan 有，但 API 沒有
                self.comparison_results['unmatched_web'].append(web_course)
                unmatched_count += 1

        # 剩餘的 API 課程（API 有，但 Web Scan 沒有）
        self.comparison_results['unmatched_api'] = list(api_index.values())

        print(f"[SUCCESS] 匹配完成")
        print(f"  ✅ 成功匹配: {matched_count} 個課程")
        print(f"  ⚠️  Web Scan 獨有: {unmatched_count} 個課程")
        print(f"  ⚠️  API 獨有: {len(self.comparison_results['unmatched_api'])} 個課程")
        print()

    def step4_analyze_fields(self):
        """Step 4: 分析欄位對應"""
        print("=" * 60)
        print("[Step 4/5] 分析欄位對應...")
        print("=" * 60)

        if not self.comparison_results['matched']:
            print("[WARNING] 沒有匹配的課程，無法分析欄位")
            print()
            return

        # 取第一個匹配的課程作為範例
        example = self.comparison_results['matched'][0]
        web_course = example['web']
        api_course = example['api']

        print("[INFO] 欄位對應分析（基於匹配的課程）:\n")

        # Web Scan 欄位
        print("### Web Scan 欄位:")
        for key in web_course.keys():
            print(f"  - {key}: {type(web_course[key]).__name__}")

        print()

        # API 欄位
        print("### API 欄位:")
        for key in api_course.keys():
            value = api_course[key]
            value_type = type(value).__name__
            print(f"  - {key}: {value_type}")

        print()

        # 欄位對應關係
        print("### 欄位對應關係:")
        mapping = {
            'course_id (Web)': 'id (API)',
            'program_name (Web)': '可能對應 name (API)',
            'lesson_name (Web)': '可能對應 name (API)',
        }

        for web_field, api_field in mapping.items():
            print(f"  - {web_field} → {api_field}")

        self.comparison_results['field_mapping'] = mapping

        print()

        # 分析 API 獨有欄位（Web Scan 沒有的）
        web_fields = set(web_course.keys())
        api_fields = set(api_course.keys())

        api_unique_fields = api_fields - {'id', 'name'}  # 排除已知對應的欄位

        print("### API 提供的額外欄位（Web Scan 沒有）:")
        for field in sorted(api_unique_fields):
            example_value = api_course[field]
            if example_value is not None:
                value_str = str(example_value)
                if len(value_str) > 50:
                    value_str = value_str[:50] + "..."
                print(f"  ✨ {field}: {value_str}")
            else:
                print(f"  - {field}: null")

        print()

    def step5_generate_report(self):
        """Step 5: 生成比對報告"""
        print("=" * 60)
        print("[Step 5/5] 生成比對報告...")
        print("=" * 60)

        report = self._build_report()

        # 儲存報告
        output_dir = PROJECT_ROOT / 'scripts' / 'api_verification' / 'results'
        output_dir.mkdir(parents=True, exist_ok=True)

        report_file = output_dir / 'comparison_report.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        # 儲存 JSON 格式的比對結果
        json_file = output_dir / 'comparison_results.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            # 簡化輸出（不包含完整課程資料）
            summary = {
                'matched_count': len(self.comparison_results['matched']),
                'unmatched_web_count': len(self.comparison_results['unmatched_web']),
                'unmatched_api_count': len(self.comparison_results['unmatched_api']),
                'field_mapping': self.comparison_results['field_mapping'],
                'matched_course_ids': [
                    m['web']['course_id'] for m in self.comparison_results['matched']
                ]
            }
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"[SUCCESS] 報告已儲存:")
        print(f"  - {report_file}")
        print(f"  - {json_file}")
        print()

    def _build_report(self) -> str:
        """生成 Markdown 報告"""
        matched_count = len(self.comparison_results['matched'])
        unmatched_web_count = len(self.comparison_results['unmatched_web'])
        unmatched_api_count = len(self.comparison_results['unmatched_api'])
        total_web = len(self.web_data)
        total_api = len(self.api_data)

        match_rate = (matched_count / total_web * 100) if total_web > 0 else 0

        report = f"""# Web Scan vs API Scan 資料比對報告
**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 執行摘要

| 項目 | 數量 |
|------|------|
| **Web Scan 課程總數** | {total_web} |
| **API Scan 課程總數** | {total_api} |
| **成功匹配** | {matched_count} |
| **Web Scan 獨有** | {unmatched_web_count} |
| **API Scan 獨有** | {unmatched_api_count} |
| **匹配率** | {match_rate:.1f}% |

---

## 匹配策略

**使用欄位**: `course_id` (Web Scan) == `id` (API Scan)

**匹配邏輯**:
1. 以 Web Scan 的 `course_id` 為基準
2. 在 API 資料中尋找相同 `id` 的課程
3. 記錄匹配成功與失敗的課程

---

## 資料結構比較

### Web Scan 資料結構

```json
{{
  "program_name": "主課程名稱",
  "lesson_name": "子課程名稱",
  "course_id": 369,
  "enable_screenshot": true,
  "description": "課程描述"
}}
```

**特點**:
- ✅ 包含**階層資訊**（主課程 + 子課程）
- ✅ 提供自動化控制欄位（enable_screenshot）
- ❌ 缺少課程詳細資訊（學分、日期等）

### API Scan 資料結構

```json
{{
  "id": 465,
  "name": "課程完整名稱",
  "course_code": "901011114",
  "course_type": 1,
  "credit": "2.0",
  "start_date": "2025-03-01",
  "end_date": "2025-12-31",
  "is_graduated": true,
  ...
}}
```

**特點**:
- ❌ **無階層資訊**（扁平結構）
- ✅ 提供豐富的課程詳細資訊
- ✅ 包含狀態資訊（is_graduated, compulsory 等）

---

## 欄位對應表

| Web Scan 欄位 | API Scan 欄位 | 對應關係 |
|--------------|--------------|---------|
| `course_id` | `id` | ✅ 完全對應（用於匹配） |
| `program_name` | `name` | ⚠️ 部分對應（API name 可能是完整名稱） |
| `lesson_name` | `name` | ⚠️ 部分對應 |
| - | `course_code` | ✨ API 獨有 |
| - | `course_type` | ✨ API 獨有 |
| - | `credit` | ✨ API 獨有 |
| - | `start_date` | ✨ API 獨有 |
| - | `end_date` | ✨ API 獨有 |
| - | `is_graduated` | ✨ API 獨有 |
| - | `compulsory` | ✨ API 獨有 |
| `enable_screenshot` | - | 📝 Web Scan 獨有（自動化控制） |
| `description` | - | 📝 Web Scan 獨有（人工註記） |

---

## API 提供的額外欄位

"""
        # 分析額外欄位（如果有匹配的課程）
        if self.comparison_results['matched']:
            example = self.comparison_results['matched'][0]
            api_course = example['api']

            extra_fields = [
                'course_code', 'course_type', 'credit',
                'start_date', 'end_date', 'is_graduated',
                'compulsory', 'academic_year', 'semester'
            ]

            for field in extra_fields:
                if field in api_course:
                    value = api_course[field]
                    report += f"- **{field}**: {value}\n"

        report += """
---

## 整合建議

"""
        if match_rate >= 90:
            report += f"""### ✅ 高匹配率 ({match_rate:.1f}%)

**建議整合策略**:

1. **保留 Web Scan 作為主要資料來源**
   - 保留階層資訊（program_name + lesson_name）
   - 保留自動化控制欄位

2. **使用 API Scan 補充額外欄位**
   - 通過 `course_id` == `id` 匹配
   - 添加 API 獨有欄位到 courses.json

3. **整合後的資料結構**:
```json
{{
  "program_name": "主課程名稱",
  "lesson_name": "子課程名稱",
  "course_id": 369,
  "enable_screenshot": true,
  "description": "課程描述",

  // 以下為 API 補充欄位
  "course_code": "901011114",
  "course_type": 1,
  "credit": "2.0",
  "start_date": "2025-03-01",
  "end_date": "2025-12-31",
  "is_graduated": true,
  "compulsory": true
}}
```

4. **實作方式**:
   - 方案 A: 手動補充（一次性）
   - 方案 B: 編寫腳本自動合併
   - 方案 C: 在 menu.py 中整合 API 掃描功能

"""
        else:
            report += f"""### ⚠️ 低匹配率 ({match_rate:.1f}%)

**問題分析**:
- Web Scan 與 API 資料有{unmatched_web_count}個課程無法匹配
- 可能原因：資料來源不同步、課程 ID 變更

**建議**:
1. 檢查未匹配課程的詳細資訊
2. 考慮使用課程名稱進行模糊匹配
3. 手動檢查資料一致性

"""

        # 未匹配課程列表
        if unmatched_web_count > 0:
            report += f"""
---

## 未匹配課程列表

### Web Scan 獨有課程 ({unmatched_web_count}個)

"""
            for course in self.comparison_results['unmatched_web']:
                report += f"""- **{course.get('program_name')}** / {course.get('lesson_name')}
  - course_id: {course.get('course_id')}
"""

        if unmatched_api_count > 0:
            report += f"""
### API Scan 獨有課程 ({unmatched_api_count}個)

"""
            for course in self.comparison_results['unmatched_api'][:10]:  # 只顯示前 10 個
                report += f"""- **{course.get('name')}**
  - id: {course.get('id')}
  - course_code: {course.get('course_code')}
"""
            if unmatched_api_count > 10:
                report += f"\n... 以及其他 {unmatched_api_count - 10} 個課程\n"

        report += """
---

**報告結束**
"""
        return report

    def run(self):
        """執行完整比對流程"""
        print("""
============================================================
  Web Scan vs API Scan 資料比對
============================================================
  目的: 比對兩種掃描方式的資料差異
  輸出: 比對報告 + 欄位對應表 + 整合建議
============================================================
""")

        input("按 Enter 鍵開始比對...")
        print()

        self.step1_load_web_scan_data()
        self.step2_load_api_data()
        self.step3_match_courses()
        self.step4_analyze_fields()
        self.step5_generate_report()

        print("""
============================================================
  比對完成！
============================================================
  請查看:
  - scripts/api_verification/results/comparison_report.md
  - scripts/api_verification/results/comparison_results.json
============================================================
""")


if __name__ == '__main__':
    comparator = DataComparator()
    comparator.run()
