# Burp Suite API 流程分析器

## 功能說明

這個工具可以分析 Burp Suite 匯出的完整 HTTP 記錄，自動識別：

1. **API 調用順序** - 按時間順序顯示所有 API 請求
2. **請求/響應內容** - 自動解析 JSON 格式的請求體和響應體
3. **ID 流動追蹤** - 自動識別 ID 在不同 API 之間的傳遞
4. **流程總結** - 生成 API 端點統計和調用順序圖
5. **完整報告** - 保存詳細分析結果到 JSON 檔案

## 使用方式

### 1. 從 Burp Suite 匯出記錄

在 Burp Suite 中：
1. 選擇要分析的 HTTP 請求（可以選擇多個）
2. 右鍵 → Save items
3. 保存為 XML 格式（例如：`exam_complete_flow.txt`）

### 2. 執行分析

```bash
python analyze_burp_flow.py <burp_suite_file.txt>
```

### 範例

```bash
# 分析單一 API
python analyze_burp_flow.py api_my-courses.txt

# 分析完整的測驗流程（多個 API）
python analyze_burp_flow.py exam_48_complete_flow.txt

# 分析課程學習流程
python analyze_burp_flow.py course_learning_flow.txt
```

## 輸出說明

### 終端輸出

```
====================================================================================================
Burp Suite API 流程分析
====================================================================================================

[檔案] exam_48_complete_flow.txt
[請求總數] 15
[API 請求數] 6

====================================================================================================
API 調用流程（按時間順序）
====================================================================================================

[1] Thu Dec 11 14:30:15 CST 2025
    GET /api/courses/452/exams
    Status: 200
    Response Body:
      exams: list (長度: 1)
        第一項: {'id': 48, 'title': '高齡測驗', ...}
    ----------------------------------------------------------------------------------------------

[2] Thu Dec 11 14:30:20 CST 2025
    POST /api/exams/48/distribute
    Status: 200
    Response Body:
      exam_paper_instance_id: 403095
      subjects: list (長度: 10)
    ----------------------------------------------------------------------------------------------

[3] Thu Dec 11 14:30:25 CST 2025
    POST /api/exams/48/submissions/storage
    Status: 200
    Request Body:
      exam_paper_instance_id: 403095
      exam_submission_id: None  ← 關鍵！
    Response Body:
      id: 403114  ← 這是 exam_submission_id
      left_time: 1746229.679764
    ----------------------------------------------------------------------------------------------

[4] Thu Dec 11 14:30:30 CST 2025
    POST /api/exams/48/submissions
    Status: 200
    Request Body:
      exam_submission_id: 403114  ← 使用前面獲取的 ID
      answers: [...]
    ----------------------------------------------------------------------------------------------

====================================================================================================
ID 流動追蹤
====================================================================================================

[id=403114]
  來源: /api/exams/48/submissions/storage
  值: 403114
  被使用於: /api/exams/48/submissions

[exam_paper_instance_id=403095]
  來源: /api/exams/48/distribute
  值: 403095
  被使用於: /api/exams/48/submissions/storage

====================================================================================================
API 調用流程總結
====================================================================================================

[API 端點統計]
  /api/courses/{id}/exams
    調用次數: 1
    HTTP 方法: GET

  /api/exams/{id}/distribute
    調用次數: 1
    HTTP 方法: POST

  /api/exams/{id}/submissions/storage
    調用次數: 1
    HTTP 方法: POST

  /api/exams/{id}/submissions
    調用次數: 1
    HTTP 方法: POST

[API 調用順序]
  1. GET /api/courses/{id}/exams
     ↓
  2. POST /api/exams/{id}/distribute
     ↓
  3. POST /api/exams/{id}/submissions/storage
     ↓
  4. POST /api/exams/{id}/submissions
```

### JSON 輸出檔案

分析結果會自動保存為 `<原檔名>_flow_analysis.json`，包含：

```json
{
  "total_requests": 6,
  "api_calls": [
    {
      "time": "Thu Dec 11 14:30:15 CST 2025",
      "method": "GET",
      "url": "https://elearn.post.gov.tw/api/courses/452/exams",
      "path": "/api/courses/452/exams",
      "status": "200",
      "request_body": null,
      "response_body": {
        "exams": [...]
      }
    },
    ...
  ],
  "id_tracker": {
    "id=403114": {
      "source": "/api/exams/48/submissions/storage",
      "value": 403114,
      "used_in": ["/api/exams/48/submissions"]
    }
  }
}
```

## 典型使用場景

### 場景 1: 分析測驗完整流程

當你想了解測驗答題的完整 API 調用順序時：

1. 在瀏覽器中完整操作一次測驗（從進入到提交）
2. 在 Burp Suite 中選擇所有相關請求
3. 匯出並分析

```bash
python analyze_burp_flow.py exam_complete_flow.txt
```

### 場景 2: 分析課程學習流程

當你想了解課程學習的 API 調用時：

1. 在瀏覽器中進入課程、觀看章節、完成學習
2. 匯出 Burp Suite 記錄
3. 分析流程

```bash
python analyze_burp_flow.py course_learning_flow.txt
```

### 場景 3: 逆向工程 API 依賴

當你想知道某個 API 需要哪些前置 API 時：

1. 從頭到尾操作一遍完整流程
2. 匯出所有請求
3. 工具會自動識別 ID 在不同 API 之間的傳遞關係

## 工具優勢

✅ **自動化分析** - 不需要手動一個個查看 API
✅ **ID 追蹤** - 自動識別參數依賴關係
✅ **流程可視化** - 生成清晰的調用順序
✅ **批次處理** - 一次分析多個 API
✅ **JSON 輸出** - 方便後續處理和文檔化

## 注意事項

1. **檔案格式**: 必須是 Burp Suite 的 XML 格式匯出
2. **編碼問題**: 如果終端顯示亂碼，請查看 JSON 輸出檔案（UTF-8 編碼）
3. **大檔案**: 如果記錄太多，建議只匯出關鍵的 API 請求
4. **時間順序**: 確保 Burp Suite 記錄按時間順序排列

## 進階用法

### 過濾特定 API

如果只想分析特定路徑的 API：

```python
# 修改工具，添加路徑過濾
api_requests = [r for r in self.requests if '/api/exams/' in r['url']]
```

### 生成流程圖

工具輸出的調用順序可以直接用於繪製流程圖：

```
GET /api/courses/{id}/exams
  ↓
POST /api/exams/{id}/distribute
  ↓
POST /api/exams/{id}/submissions/storage
  ↓
POST /api/exams/{id}/submissions
```

## 相關檔案

- `analyze_burp_flow.py` - 主程式
- `README_BURP_FLOW_ANALYZER.md` - 本文檔
- `*_flow_analysis.json` - 分析結果輸出檔案

## 更新日誌

- **2025-12-11**: 初版發布
  - 支援基本 API 流程分析
  - 支援 ID 流動追蹤
  - 支援 JSON 輸出

## 作者

Claude Code (Sonnet 4.5)
EEBot 專案
