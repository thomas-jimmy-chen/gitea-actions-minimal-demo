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

---

## 🗂️ 文檔總覽 (按類別)

### 📊 一、核心分析報告

| 文檔 | 位置 | 日期 | 說明 |
|------|------|------|------|
| **API 端點分析報告** | `BURP_ANALYSIS_REPORT.md` | 2025-12-02 | 登入、課程、時長等 4 個核心 API |
| **詳細分析 (660請求)** | `TEST2_DETAILED_ANALYSIS.md` | 2025-12-02 | 660 個請求的完整分析 |
| **分析總結文檔** | `ANALYSIS_SUMMARY_REPORT.md` | 2025-12-02 | 4 份報告的總結索引 |
| **快速參考** | `TEST2_QUICK_REFERENCE.md` | 2025-12-02 | 常用 API 快速查閱 |

### ⏱️ 二、時長發送機制

| 文檔 | 位置 | 日期 | 說明 |
|------|------|------|------|
| **visit_duration 專題** | `VISIT_DURATION_ANALYSIS.md` | 2025-12-02 | 時長計算邏輯、防篡改分析 |
| **分析結果與建議** | `BURP_ANALYSIS_FINDINGS_AND_RECOMMENDATIONS.md` | 2025-12-16 | Content-Type, Referer 差異 |
| **行動計畫總結** | `BURP_ANALYSIS_SUMMARY.md` | 2025-12-16 | 3 個關鍵差異與改進方案 |
| **手刻封包發送** | `BURPSUITE_MODE_MANUAL_SEND.md` | 2025-12-17 | MitmProxy 手刻封包技術 |

### 📝 三、考試自動答題

| 文檔 | 位置 | 日期 | 說明 |
|------|------|------|------|
| **考試 48 可行性分析** | `docs/API_AUTO_ANSWER_FEASIBILITY_EXAM_48.md` | 2025-12-11 | 100% 匹配率驗證 |
| **考試頁面渲染分析** | `docs/EXAM_PAGE_RENDERING_ANALYSIS.md` | 2025-12-27 | 16 個請求時序、滾動容器 |
| **完整流程分析** | `TEST1213_COMPLETE_ANALYSIS_REPORT.md` | 2025-12-13 | 考試提交完整流程 |

### 🔒 四、姓名替換與樣式注入

| 文檔 | 位置 | 日期 | 說明 |
|------|------|------|------|
| **姓名替換分析** | `NAME_REPLACEMENT_ANALYSIS.md` | 2025-12-31 | 5 個位置、遮蔽規則 |
| **登入頁面範例** | `login_page_modified.html` | 2025-12-31 | 樣式注入後的 HTML |

### 🔍 五、隱藏 API 研究

| 文檔 | 位置 | 日期 | 說明 |
|------|------|------|------|
| **隱藏 API 研究** | `docs/HIDDEN_API_RESEARCH_2025-12-12.md` | 2025-12-12 | 未公開 API 端點發現 |
| **課程詳情 API** | `COURSE_DETAIL_API_ANALYSIS.md` | 2025-12-09 | 課程結構分析 |

### 📅 六、工作日誌

| 文檔 | 位置 | 日期 | 說明 |
|------|------|------|------|
| **Burp 分析日誌** | `docs/DAILY_WORK_LOG_20251202_BURP_ANALYSIS.md` | 2025-12-02 | test1 + test2 分析過程 |
| **今日工作日誌** | `docs/WORK_LOG_2025-12-31.md` | 2025-12-31 | 姓名替換實作 |

---

## 🛠️ 分析腳本工具

### Python 腳本

| 腳本 | 位置 | 功能 |
|------|------|------|
| **parse_burp.py** | 根目錄 | Burp XML 解析器 (v1) |
| **parse_burp_v2.py** | 根目錄 | Burp XML 解析器 (v2) |
| **parse_burp_v3.py** | 根目錄 | Burp XML 解析器 (v3) |
| **analyze_burp_flow.py** | 根目錄 | API 流程分析器 |
| **analyze_burp_user_visits.py** | 根目錄 | user-visits API 分析 |
| **analyze_burp_names.py** | 根目錄 | 姓名出現位置分析 |
| **scripts/analyze_burp_capture.py** | scripts/ | 通用捕獲分析 |

### 使用說明

```bash
# 分析 API 流程
python analyze_burp_flow.py <burp_export.txt>

# 分析 user-visits API
python analyze_burp_user_visits.py <burp_export.txt>

# 分析姓名位置
python analyze_burp_names.py <burp_export.txt>
```

---

## 📁 原始數據檔案

### Burp Suite 匯出檔

| 檔案 | 說明 | 大小 |
|------|------|------|
| `20251230-bu.txt` | 最新流量捕獲 (姓名分析) | 12.5 MB |
| `test1` | 登入流程 (20 請求) | 984 KB |
| `test2` | 完整會話 (660 請求) | 56.5 MB |
| `test3` | 考試流程 | - |
| `test1213.txt` | 考試提交流程 | - |

### JSON 數據檔

| 檔案 | 說明 |
|------|------|
| `USER_VISITS_FIELD_MAPPING.json` | user-visits API 欄位對應表 (80KB) |
| `API_TECHNICAL_SPEC.json` | API 技術規格 |
| `burp_analysis_summary.json` | 分析結果摘要 |

### API 原始響應

| 檔案 | 說明 |
|------|------|
| `api_my-courses.txt` | 課程列表 API 響應 |
| `api_exams_48_*.txt` | 考試 48 相關 API |
| `api_courses_*.txt` | 課程相關 API |
| `POST_statistics_api_user-visits.txt` | 時長發送請求樣本 |

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

---

## 📚 相關文檔連結

### AI 交接文檔
- [CLAUDE_CODE_HANDOVER-11.md](./CLAUDE_CODE_HANDOVER-11.md) - 最新交接
- [CLAUDE_CODE_HANDOVER-10.md](./CLAUDE_CODE_HANDOVER-10.md) - 前次交接

### 工作日誌
- [WORK_LOG_2025-12-31.md](./WORK_LOG_2025-12-31.md) - 姓名替換
- [WORK_LOG_2025-12-27.md](./WORK_LOG_2025-12-27.md) - 考試頁面分析

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
| API 端點查詢 | `TEST2_DETAILED_ANALYSIS.md` |

---

## 📅 更新歷史

| 日期 | 版本 | 說明 |
|------|------|------|
| 2025-12-31 | 1.1 | 新增完整文檔索引 |
| 2025-12-31 | 1.0 | 初版建立 |

---

*文檔建立: 2025-12-31 | 維護者: Claude Code (Opus 4.5)*
