# Burp Suite 流量分析技術索引

> **🔥 重要文檔** - 所有 AI 助手在處理頁面修改、API 攔截、姓名替換、時長發送相關任務時，必須先閱讀本文檔
>
> **專案**: EEBot v2.4.1 - TronClass Learning Assistant (代號: AliCorn)
> **建立日期**: 2025-12-31
> **最後更新**: 2025-12-31
> **維護者**: Claude Code (Opus 4.5)

---

## 📑 本文檔目的

本文檔是 **Burp Suite 流量分析** 相關技術文獻的**完整索引**，包含:

1. API 分析報告
2. 時長發送機制
3. 考試自動答題
4. 姓名替換實作
5. MitmProxy 攔截器
6. 分析腳本工具
7. 原始數據檔案

---

## 🗂️ 文檔總覽 (按類別)

### 📊 一、核心分析報告

| 文檔 | 位置 | 日期 | 說明 |
|------|------|------|------|
| **🔥 平台技術研究總報告** | `docs/ELEARNING_PLATFORM_TECHNICAL_RESEARCH.md` | 2025-12-31 | 商業邏輯、技術規格、修改點總整理 |
| **API 端點分析報告** | `BURP_ANALYSIS_REPORT.md` | 2025-12-02 | 登入、課程、時長等 4 個核心 API |
| **詳細分析 (660請求)** | `TEST2_DETAILED_ANALYSIS.md` | 2025-12-02 | 660 個請求的完整分析 |
| **分析總結文檔** | `ANALYSIS_SUMMARY_REPORT.md` | 2025-12-02 | 4 份報告的總結索引 |
| **總結報告** | `ANALYSIS_SUMMARY.md` | 2025-12-02 | test1 分析總結 (20 請求) |
| **快速參考** | `TEST2_QUICK_REFERENCE.md` | 2025-12-02 | 常用 API 快速查閱 (5分鐘) |

### ⏱️ 二、時長發送機制 (user-visits API)

| 文檔 | 位置 | 日期 | 說明 |
|------|------|------|------|
| **visit_duration 專題** | `VISIT_DURATION_ANALYSIS.md` | 2025-12-02 | 時長計算邏輯、防篡改分析 |
| **分析結果與建議** | `BURP_ANALYSIS_FINDINGS_AND_RECOMMENDATIONS.md` | 2025-12-16 | Content-Type, Referer 差異 |
| **行動計畫總結** | `BURP_ANALYSIS_SUMMARY.md` | 2025-12-16 | 3 個關鍵差異與改進方案 |
| **手刻封包發送** | `BURPSUITE_MODE_MANUAL_SEND.md` | 2025-12-17 | MitmProxy 手刻封包技術 |
| **欄位對應表** | `USER_VISITS_FIELD_MAPPING.json` | 2025-12-02 | 19 個欄位完整對應 (80KB) |

### 📝 三、考試自動答題

| 文檔 | 位置 | 日期 | 說明 |
|------|------|------|------|
| **考試 48 可行性分析** | `docs/API_AUTO_ANSWER_FEASIBILITY_EXAM_48.md` | 2025-12-11 | 100% 匹配率驗證 |
| **考試頁面渲染分析** | `docs/EXAM_PAGE_RENDERING_ANALYSIS.md` | 2025-12-27 | 16 個請求時序、滾動容器 |
| **完整流程分析** | `TEST1213_COMPLETE_ANALYSIS_REPORT.md` | 2025-12-13 | 考試提交完整流程 |
| **考試 API 分析** | `docs/API_EXAMS_ANALYSIS.md` | 2025-12-11 | 考試相關 API 端點 |
| **TEST3 考試機制研究** | `TEST3_EXAM_MECHANISM_RESEARCH.md` | 2025-12 | test3 考試機制詳細研究 |
| **TEST3 考試快速參考** | `TEST3_EXAM_QUICK_REFERENCE.md` | 2025-12 | test3 考試快速查閱 |
| **TEST3 考試欄位對應** | `TEST3_EXAM_FIELD_MAPPING.json` | 2025-12 | test3 考試欄位映射表 |

### 📚 四、課程 API 分析

| 文檔 | 位置 | 日期 | 說明 |
|------|------|------|------|
| **API 結構分析** | `API_STRUCTURE_ANALYSIS.md` | 2025-12-09 | 課程物件 37 個欄位 |
| **課程詳情 API** | `COURSE_DETAIL_API_ANALYSIS.md` | 2025-12-09 | 課程結構分析 |
| **課程活動 API** | `COURSE_ACTIVITIES_API_ANALYSIS.md` | 2025-12-09 | 子課程列表 API |

### 🔒 五、姓名替換與樣式注入

| 文檔 | 位置 | 日期 | 說明 |
|------|------|------|------|
| **姓名替換分析** | `NAME_REPLACEMENT_ANALYSIS.md` | 2025-12-31 | 5 個位置、遮蔽規則 |
| **登入頁面範例** | `login_page_modified.html` | 2025-12-31 | 樣式注入後的 HTML |

### 🔍 六、隱藏 API 研究

| 文檔 | 位置 | 日期 | 說明 |
|------|------|------|------|
| **隱藏 API 研究** | `docs/HIDDEN_API_RESEARCH_2025-12-12.md` | 2025-12-12 | 未公開 API 端點發現 |

### 📈 七、學習統計 API (Learning Stats)

| 文檔 | 位置 | 日期 | 說明 |
|------|------|------|------|
| **學習統計 API 測試指南** | `docs/LEARNING_STATS_API_TEST_GUIDE.md` | 2025-12 | API 測試方法與範例 |
| **學習統計整合總結** | `docs/LEARNING_STATS_INTEGRATION_SUMMARY.md` | 2025-12 | 整合進度與狀態 |
| **測試結果** | `learning_stats_api_test_result.json` | 2025-12 | API 測試輸出數據 |

### 📖 八、快速參考文檔

| 文檔 | 位置 | 說明 |
|------|------|------|
| **API 快速參考** | `API_QUICK_REFERENCE.md` | API 端點速查表 |
| **API 直連模式參考** | `docs/API_DIRECT_MODE_QUICK_REFERENCE.md` | 直連模式設定 |
| **一般課程參考** | `GENERAL_COURSE_QUICK_REFERENCE.md` | 課程相關速查 |
| **TEST2 快速參考** | `TEST2_QUICK_REFERENCE.md` | test2 分析速查 |
| **TEST3 考試參考** | `TEST3_EXAM_QUICK_REFERENCE.md` | test3 考試速查 |
| **Git 快速參考** | `docs/GIT_QUICK_REFERENCE.md` | Git 指令速查 |

### 📅 九、工作日誌

| 文檔 | 位置 | 日期 | 說明 |
|------|------|------|------|
| **Burp 分析日誌** | `docs/DAILY_WORK_LOG_20251202_BURP_ANALYSIS.md` | 2025-12-02 | test1 + test2 分析過程 |
| **工作日誌 12-29** | `docs/WORK_LOG_2025-12-29.md` | 2025-12-29 | CAPTCHA OCR 整合 |
| **工作日誌 12-30** | `docs/WORK_LOG_2025-12-30.md` | 2025-12-30 | tour.post CAPTCHA |
| **工作日誌 12-31** | `docs/WORK_LOG_2025-12-31.md` | 2025-12-31 | 姓名替換實作 |

---

## 🛠️ 分析腳本工具

### Python 腳本 - Burp Suite 解析

| 腳本 | 位置 | 功能 |
|------|------|------|
| **parse_burp.py** | 根目錄 | Burp XML 解析器 (v1) |
| **parse_burp_v2.py** | 根目錄 | Burp XML 解析器 (v2) |
| **parse_burp_v3.py** | 根目錄 | Burp XML 解析器 (v3) |
| **parse_burp_analysis.py** | 根目錄 | 解析器 + 分析功能 |
| **analyze_burp_flow.py** | 根目錄 | API 流程分析器 |
| **analyze_burp_user_visits.py** | 根目錄 | user-visits API 分析 |
| **analyze_burp_names.py** | 根目錄 | 姓名出現位置分析 |
| **scripts/analyze_burp_capture.py** | scripts/ | 通用捕獲分析 |
| **comprehensive_analysis.py** | 根目錄 | 綜合分析腳本 |

### Python 腳本 - API 分析

| 腳本 | 位置 | 功能 |
|------|------|------|
| **analyze_activities.py** | 根目錄 | 活動列表分析 |
| **analyze_announcement_api.py** | 根目錄 | 公告 API 分析 |
| **analyze_api_response.py** | 根目錄 | API 響應分析 |
| **analyze_bulk_activities.py** | 根目錄 | 批量活動分析 |
| **analyze_course_450.py** | 根目錄 | 課程 450 專項分析 |
| **analyze_course_detail_api.py** | 根目錄 | 課程詳情 API 分析 |
| **analyze_my_courses.py** | 根目錄 | 我的課程分析 |
| **analyze_my_courses_api.py** | 根目錄 | 課程 API 響應分析 |
| **analyze_storage_api.py** | 根目錄 | 暫存 API 分析 |
| **analyze_submission_api.py** | 根目錄 | 提交 API 分析 |

### Python 腳本 - 考試分析

| 腳本 | 位置 | 功能 |
|------|------|------|
| **analyze_test3_exam.py** | 根目錄 | test3 考試分析 |
| **analyze_exam_48_distribute.py** | 根目錄 | 考試 48 派發分析 |
| **analyze_exam_flow_test1213.py** | 根目錄 | test1213 考試流程分析 |
| **analyze_flow_deep.py** | 根目錄 | 深度流程分析 |

### Python 腳本 - 學習統計

| 腳本 | 位置 | 功能 |
|------|------|------|
| **scripts/quick_learning_stats.py** | scripts/ | 快速學習統計查詢 |
| **scripts/test_learning_stats_api.py** | scripts/ | 學習統計 API 測試 |

### 使用說明

```bash
# 分析 API 流程
python analyze_burp_flow.py <burp_export.txt>

# 分析 user-visits API
python analyze_burp_user_visits.py <burp_export.txt>

# 分析姓名位置
python analyze_burp_names.py <burp_export.txt>

# 綜合分析
python comprehensive_analysis.py <burp_export.txt>
```

### 腳本使用指南

| 文檔 | 位置 | 說明 |
|------|------|------|
| **流程分析器說明** | `README_BURP_FLOW_ANALYZER.md` | analyze_burp_flow.py 使用手冊 |

### Scripts 子目錄分析報告

#### API 驗證 (`scripts/api_verification/`)

| 文檔 | 位置 | 說明 |
|------|------|------|
| **API 結構分析** | `scripts/api_verification/results/api_structure_analysis.md` | API 結構詳細分析 |
| **比較報告** | `scripts/api_verification/results/comparison_report.md` | API 版本比較 |
| **最終整合報告** | `scripts/api_verification/results/final_integration_report.md` | 整合結果 |
| **安全評估** | `scripts/api_verification/results/security_assessment.md` | API 安全性評估 |
| **使用說明** | `scripts/api_verification/README.md` | 驗證腳本使用手冊 |

#### 課程需求實驗 (`scripts/course_requirements_experiment/`)

| 文檔 | 位置 | 說明 |
|------|------|------|
| **API 探索報告** | `scripts/course_requirements_experiment/results/api_exploration_report.md` | API 端點探索 |
| **提取測試報告** | `scripts/course_requirements_experiment/results/extraction_test_report.md` | 數據提取測試 |
| **使用說明** | `scripts/course_requirements_experiment/README.md` | 實驗腳本使用手冊 |

---

## 📁 原始數據檔案

### Burp Suite 匯出檔

| 檔案 | 說明 | 大小 |
|------|------|------|
| `20251230-bu.txt` | 最新流量捕獲 (姓名分析) | 12.5 MB |
| `test1` | 登入流程 (20 請求) | 984 KB |
| `test2` | 完整會話 (660 請求) | 56.5 MB |
| `test3` | 考試流程 | - |
| `test1.txt` | test1 文字版 | - |
| `test1213.txt` | 考試提交流程 | - |
| `高齡測驗(100分及格).txt` | 考試頁面渲染 | - |

### JSON 數據檔

| 檔案 | 說明 |
|------|------|
| `USER_VISITS_FIELD_MAPPING.json` | user-visits API 欄位對應表 (80KB) |
| `API_TECHNICAL_SPEC.json` | API 技術規格 |
| `burp_analysis_summary.json` | 分析結果摘要 |
| `comprehensive_analysis.json` | 綜合分析結果 |
| `user_visits_analysis.json` | user-visits 分析結果 |
| `visit_duration_analysis.json` | 時長分析結果 |
| `test1_flow_analysis.json` | test1 流程分析 |
| `test1213_flow_analysis.json` | test1213 流程分析 |
| `test3_exam_analysis.json` | test3 考試分析 |
| `test3_post_requests.json` | test3 POST 請求 |
| `test3_exam_submission_full.json` | 考試提交完整資料 |
| `exam_api_detailed_analysis.json` | 考試 API 詳細分析 |
| `exam_48_distribute_analysis.json` | 考試 48 派發分析 |
| `exams_apis_comparison.json` | 考試 API 比較 |

### API 原始響應 (*.txt)

| 檔案 | 說明 |
|------|------|
| `api_my-courses.txt` | 課程列表 API 響應 |
| `api_my-courses_condition.txt` | 課程條件查詢 |
| `api_courses_465_activities.txt` | 課程 465 活動列表 |
| `api_courses_465_activities-1.txt` | 活動列表備份 |
| `api_courses_465_exams.txt` | 課程 465 考試列表 |
| `api_courses_465_field.txt` | 課程欄位詳情 |
| `api_courses_450_activities .txt` | 課程 450 活動列表 |
| `api_courses_450_exams.txt` | 課程 450 考試列表 |
| `api_courses_452_exams.txt` | 課程 452 考試列表 |
| `api_activities_1491.txt` | 活動 1491 詳情 |
| `api_activities_1492.txt` | 活動 1492 詳情 |
| `api_exams_48_distribute.txt` | 考試 48 派發 |
| `api_exams_48_submissions.txt` | 考試 48 提交記錄 |
| `api_exams_48_submissions_storage.txt` | 考試 48 暫存 |
| `POST_statistics_api_user-visits.txt` | 時長發送請求樣本 |
| `GET_api_announcement.txt` | 公告 API |

### 分析中間產物

| 檔案 | 說明 |
|------|------|
| `course_detail_analysis.txt` | 課程詳情分析 |
| `test1_deep_analysis.txt` | test1 深度分析 |
| `test1_analysis_report.md` | test1 分析報告 |
| `test1213_deep_analysis.txt` | test1213 深度分析 |
| `test1213_exam_analysis_report.txt` | 考試分析報告 |
| `my_courses_analysis.json` | 我的課程分析 |
| `my_courses_api_analysis.json` | 課程 API 分析 |
| `course_450_analysis.json` | 課程 450 分析 |
| `first_subcourse_analysis.json` | 首個子課程分析 |
| `activity_chapters_analysis.json` | 活動章節分析 |
| `bulk_activities_analysis.json` | 批量活動分析 |
| `submission_api_analysis.json` | 提交 API 分析 |
| `storage_api_analysis.json` | 暫存 API 分析 |
| `api_my-courses_flow_analysis.json` | 課程流程分析 |

---

## 🔧 MitmProxy 攔截器

| 檔案 | 位置 | 功能 |
|------|------|------|
| **登入樣式修改器** | `src/api/interceptors/login_style_modifier.py` | 姓名替換 + CSS 注入 |
| **手動時長發送** | `src/api/interceptors/manual_send_duration.py` | 手刻封包發送 |
| **訪問時長 API** | `src/api/visit_duration_api.py` | 時長 API 封裝 |

---

## 🎯 關鍵技術摘要

### 1. user-visits API (時長發送)

**端點**: `POST /statistics/api/user-visits`

**必填欄位** (13 個):
```json
{
  "user_id": 19688,
  "org_id": 1,
  "visit_duration": 3600,
  "visit_start_time": 1735000000000,
  "visit_end_time": 1735003600000,
  "course_id": 450,
  "master_course_id": 450,
  "activity_id": null,
  "activity_type": null,
  "page_source": "course_detail",
  "user_agent": "...",
  "ip": "...",
  "region": "..."
}
```

**Content-Type**: `text/plain;charset=UTF-8` (非 application/json)

### 2. 姓名遮蔽規則

**規則**: 保留第一個字，其餘用 `〇` (U+3007 國字零) 替換

| 原始 | 遮蔽後 |
|------|--------|
| 陳偉鳴 | 陳〇〇 |
| 李四 | 李〇 |
| 司馬相如 | 司〇〇〇 |

**姓名出現位置** (5 處):
1. JavaScript `user.name`
2. AngularJS `root-scope-variable`
3. AngularJS `ng-init`
4. `window.analyticsData.userName`
5. `CurrentName` 變數

### 3. 考試頁面渲染

**滾動容器層級**:
```
fullscreen-right
  └─ activity-content-box
      └─ exam-subjects
```

**技術棧**: AngularJS + Vue.js 混合

### 4. 課程 API 結構

**課程物件欄位**: 37 個
- `id`, `name`, `display_name`, `course_code`
- `is_graduated`, `credit`, `start_date`, `end_date`
- 詳見 `API_STRUCTURE_ANALYSIS.md`

---

## 📚 相關文檔連結

### AI 交接文檔
- [CLAUDE_CODE_HANDOVER-11.md](./CLAUDE_CODE_HANDOVER-11.md) - 最新交接 (2025-12-31)
- [CLAUDE_CODE_HANDOVER-10.md](./CLAUDE_CODE_HANDOVER-10.md) - 前次交接
- [CLAUDE_CODE_HANDOVER-9.md](./CLAUDE_CODE_HANDOVER-9.md) - v2.4.0 交接

### 功能分析文檔
- [H_FUNCTION_WORKFLOW_ANALYSIS.md](./H_FUNCTION_WORKFLOW_ANALYSIS.md) - h 功能工作流程
- [H_FUNCTION_ANALYSIS_REPORT.md](./H_FUNCTION_ANALYSIS_REPORT.md) - h 功能分析報告
- [SCAN_LOGIC_ANALYSIS_REPORT.md](./SCAN_LOGIC_ANALYSIS_REPORT.md) - 掃描邏輯分析

### 技術指南
- [HYBRID_DURATION_SEND_GUIDE.md](./HYBRID_DURATION_SEND_GUIDE.md) - 混合時長發送

---

## 💡 AI 助手注意事項

### 必須遵守

1. **姓名替換必須使用 `〇` (U+3007)**，不是普通圓圈 `○`
2. **MitmProxy 只處理 HTML 響應**，JSON API 不需要處理
3. **時長發送使用 text/plain**，不是 application/json
4. **考試滾動必須使用專用選擇器**

### 常見任務對應文檔

| 任務 | 優先閱讀 |
|------|----------|
| 修改時長發送 | `VISIT_DURATION_ANALYSIS.md`, `BURP_ANALYSIS_SUMMARY.md` |
| 考試自動答題 | `docs/API_AUTO_ANSWER_FEASIBILITY_EXAM_48.md` |
| 姓名替換 | `NAME_REPLACEMENT_ANALYSIS.md` |
| 頁面渲染問題 | `docs/EXAM_PAGE_RENDERING_ANALYSIS.md` |
| API 端點查詢 | `TEST2_DETAILED_ANALYSIS.md`, `API_STRUCTURE_ANALYSIS.md` |
| 課程 API | `COURSE_ACTIVITIES_API_ANALYSIS.md`, `COURSE_DETAIL_API_ANALYSIS.md` |
| 隱藏 API | `docs/HIDDEN_API_RESEARCH_2025-12-12.md` |

---

## 📊 統計摘要

| 類別 | 數量 |
|------|------|
| Markdown 分析報告 | 30+ |
| Python 分析腳本 | 25+ |
| JSON 數據檔 | 20+ |
| API 原始響應 (txt) | 16 |
| Burp 匯出檔 | 7 |
| MitmProxy 攔截器 | 3 |
| Scripts 子目錄報告 | 8 |
| 快速參考文檔 | 6 |
| **總計** | **100+ 檔案** |

---

## 📅 更新歷史

| 日期 | 版本 | 說明 |
|------|------|------|
| 2025-12-31 | 1.3 | 使用 Everything 搜尋，擴展至 100+ 檔案 |
| 2025-12-31 | 1.2 | 新增完整檔案清單 (70+ 檔案) |
| 2025-12-31 | 1.1 | 新增完整文檔索引 |
| 2025-12-31 | 1.0 | 初版建立 |

---

*文檔建立: 2025-12-31 | 維護者: Claude Code (Opus 4.5)*
