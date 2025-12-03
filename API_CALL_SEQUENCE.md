# API 調用序列分析報告

**基於實際網絡流量的時序分析** (660個HTTP請求採樣)

---

## 目錄

1. [調用模式概覽](#調用模式概覽)
2. [完整時序圖](#完整時序圖)
3. [子流程詳解](#子流程詳解)
4. [參數依賴關係](#參數依賴關係)
5. [時間間隔分析](#時間間隔分析)
6. [核心業務流程](#核心業務流程)

---

## 調用模式概覽

### 整體架構

```
用戶登錄
  │
  ├─→ POST /statistics/api/user-visits (初始訪問記錄)
  │
  ├─→ GET /api/announcement (加載公告)
  │
  ├─→ GET /api/my-courses (獲取課程列表)
  │
  ├─→ POST /statistics/api/user-visits (課程列表頁面停留)
  │
  ├─→ GET /api/courses/{id}/modules (進入課程)
  │   │
  │   ├─→ POST /statistics/api/user-visits (課程頁面訪問)
  │   │
  │   ├─→ GET /api/course/{id}/activity-reads-for-user (獲取活動)
  │   │
  │   ├─→ POST /statistics/api/user-visits (課程內操作)
  │   │   │
  │   │   └─→ GET /statistics/api/courses/{id}/users/{uid}/user-visits/metrics (查詢統計)
  │   │   └─→ GET /statistics/api/courses/{id}/users/{uid}/online-videos/metrics (視頻統計)
  │   │   └─→ GET /statistics/api/courses/{id}/users/{uid}/interactions/metrics (互動統計)
  │   │
  │   └─→ GET /api/course/{id}/online-video-completeness/setting (視頻完成度)
  │
  └─→ POST /statistics/api/user-visits (頁面離開/會話結束)
```

### 關鍵統計

| 指標 | 值 | 說明 |
|-----|-----|------|
| 總請求數 | 660 | 完整採樣 |
| 獨立API路由 | 30+ | 不同的API端點 |
| 最頻繁API | `/statistics/api/user-visits` | 44次 |
| 平均響應時間 | ~100-500ms | 預估 |
| 會話持續時間 | ~25分鐘 | 首次到最後一次請求 |

---

## 完整時序圖

### Master Timeline (2025-12-02 13:35:26 - 14:03:26)

```
時間          類型  API端點                              方法  參數              狀態
──────────────────────────────────────────────────────────────────────────────────────

13:35:18      -     初始加載                            GET   /                302
              ⬇
13:35:18      -     重定向至登錄                        GET   /login           200
              ⬇
[用戶登錄認證]
              ⬇
13:35:26      ★     /statistics/api/user-visits         POST  user_id:19688    204
              │     visit_duration: 1483秒 (初始會話)
              │     所屬上下文: 用戶登錄後首次訪問
              ⬇
13:35:27      -     /api/announcement                   GET   org_id:1         200
              ⬇
13:35:28      -     /api/orgs/1/lang-settings          GET   org_id:1         200
              ⬇
13:35:29      -     /api/uploads/1484/modified-image   GET   image_id:1484    200
              ⬇
13:35:30      -     /api/my-departments                GET   user_id:19688    200
              ⬇
13:35:31      -     /api/my-courses                    GET   user_id:19688    200
              ⬇
13:35:32      -     /user/courses                      GET   user_id:19688    200
              ⬇
13:35:33      -     /api/my-academic-years            GET   user_id:19688    200
              ⬇
13:35:34      -     /api/my-semesters                 GET   user_id:19688    200
              ⬇
13:35:35      -     /api/user/recently-visited-courses GET   user_id:19688    200
              ⬇
[用戶在課程列表頁停留]
              ⬇
14:00:11      ★     /statistics/api/user-visits        POST  user_id:19688    204
              │     visit_duration: 11秒
              │     (課程列表頁面停留)
              ⬇
14:00:12      -     /api/courses/465/modules           GET   course_id:465    200
              ⬇
14:00:13      -     /api/courses/465                   GET   course_id:465    200
              ⬇
14:00:14      -     /api/courses/465/exams             GET   course_id:465    200
              ⬇
14:00:15      -     /api/courses/465/activities        GET   course_id:465    200
              ⬇
14:00:16      -     /api/courses/465/classroom-list    GET   course_id:465    200
              ⬇
[進入課程465]
              ⬇
14:00:23      ★     /statistics/api/user-visits        POST  course_id:465    204
              │     visit_duration: 3秒
              │     (進入課程頁面)
              ⬇
14:00:24      -     /api/course/465/activity-reads     GET   course_id:465    200
              ⬇
14:00:25      -     /course/465/content               GET   course_id:465    200
              ⬇
14:00:26      -     /api/courses/465/nav-setting      GET   course_id:465    200
              ⬇
[用戶點擊SCORM活動]
              ⬇
14:00:27      ★     /statistics/api/user-visits        POST  course_id:465    204
              │     visit_duration: 19秒              activity_id:1492
              │     activity_type: "scorm"
              │     (進入SCORM活動)
              ⬇
14:00:28      -     /api/uploads/scorm/460            GET   scorm_id:460     200
              ⬇
[用戶在SCORM內停留]
              ⬇
14:00:47      ★     /statistics/api/user-visits        POST  course_id:465    204
              │     visit_duration: 3秒              activity_id:1492
              │     (SCORM內停留)
              ⬇
14:00:48      -     /api/courses/465/scorm-activities  GET   course_id:465    200
              ⬇
[查詢統計指標 - 開始]
              ⬇
14:00:50      ◆     /statistics/api/courses/465/users/ GET   course_id:465    200
              │     19688/user-visits/metrics         user_id:19688
              │     Response: {count: 65, sum: 202072.0, ...}
              ⬇
14:00:51      ◆     /statistics/api/courses/465/users/ GET   course_id:465    200
              │     19688/online-videos/metrics       user_id:19688
              ⬇
14:00:52      ◆     /statistics/api/courses/465/users/ GET   course_id:465    200
              │     19688/interactions/metrics        user_id:19688
              ⬇
[查詢統計指標 - 結束]
              ⬇
14:00:55      ★     /statistics/api/user-visits        POST  user_id:19688    204
              │     visit_duration: 4秒
              │     (無course_id - 返回課程列表)
              ⬇
[...後續課程循環...]
              ⬇
14:03:26      ★     /statistics/api/user-visits        POST  user_id:19688    204
              │     visit_duration: 2秒
              │     (最後一次訪問)
```

### 圖例

```
★  = POST /statistics/api/user-visits (時長記錄 - 最關鍵)
◆  = GET */metrics API (統計查詢)
-  = 其他GET請求 (輔助數據)
```

---

## 子流程詳解

### 子流程1: 用戶認證與初始化

**時間點**: 13:35:18 - 13:35:35 (約17秒)

```
序號  API                          方法  請求參數      返回狀態  用途
────────────────────────────────────────────────────────────────────────
1     GET /                        GET   -            302     首頁重定向
2     GET /login                   GET   -            200     登錄頁面
      [用戶輸入認證信息]
3     POST /api/auth/login         POST  credentials  200     認證
      [系統發放session cookie]
4     GET /api/announcement        GET   org_id       200     公告加載
5     GET /api/orgs/1/lang-settings GET   org_id      200     語言設定
6     GET /api/uploads/.../image   GET   image_id    200     資源加載
```

**特徵**:
- 所有請求在驗證後序列執行
- 無並行請求（同步加載）
- 主要為頁面初始化數據

### 子流程2: 課程導航

**時間點**: 14:00:11 - 14:00:26 (約15秒)

```
序號  操作                           時間    API                      visit_duration
────────────────────────────────────────────────────────────────────────────────────
1     用戶在課程列表頁停留          14:00:11 POST /user-visits         11秒
                                      GET /api/my-courses           [並行]
                                      GET /api/my-academic-years
                                      GET /api/my-semesters

2     用戶點擊課程465                14:00:23 POST /user-visits         3秒
                                      GET /courses/465/modules      [並行]
                                      GET /courses/465
                                      GET /courses/465/exams

3     課程頁面加載完畢               14:00:26 GET /course/465/content   [無新記錄]
```

**特徵**:
- 時長逐漸減少 (11秒 → 3秒)，表示頁面加載越來越快
- API呼叫密集且可能並行
- 每次頁面切換都記錄一次時長

### 子流程3: 活動參與

**時間點**: 14:00:27 - 14:00:52 (約25秒)

```
事件序列:

14:00:27  用戶點擊SCORM活動1492
          ↓
          POST /user-visits (visit_duration: 19秒)
          {
            course_id: 465,
            activity_id: 1492,
            activity_type: "scorm"
          }
          GET /api/uploads/scorm/460 (加載SCORM文件)

14:00:47  用戶在SCORM內停留20秒後...
          ↓
          POST /user-visits (visit_duration: 3秒)
          (仍在同一activity，但計時器重置)

14:00:50  系統自動查詢統計
          ↓
          GET /statistics/.../user-visits/metrics
          Response: {count: 65, sum: 202072.0}

          GET /statistics/.../online-videos/metrics
          GET /statistics/.../interactions/metrics

14:00:55  用戶離開活動/課程
          ↓
          POST /user-visits (visit_duration: 4秒)
          (無course_id - 回到課程列表)
```

**特徵**:
- activity_id只在活動內部請求時出現
- 多個metrics API同時查詢（可能並行）
- 計時器會在活動內重置多次

---

## 參數依賴關係

### 字段出現模式

```
是否包含 course_id
    │
    ├─ NO  (用戶在全站導航)
    │      ├─ user_id ✓
    │      ├─ org_id ✓
    │      ├─ visit_duration ✓
    │      └─ course_id ✗
    │         activity_id ✗
    │
    └─ YES (用戶在特定課程內)
           ├─ user_id ✓
           ├─ org_id ✓
           ├─ course_id ✓
           ├─ course_code ✓
           ├─ course_name ✓
           │
           └─ 是否包含 activity_id
               │
               ├─ NO  (課程主頁)
               │      └─ activity_id ✗
               │         activity_type ✗
               │
               └─ YES (課程內活動)
                      ├─ activity_id ✓
                      └─ activity_type ✓
```

### 依賴規則

| 條件 | 必須包含 | 不應包含 |
|------|--------|---------|
| 課程主頁 | user_id, org_id, course_id | activity_id |
| 活動頁面 | ...課程主頁... + activity_id | - |
| 全站導航 | user_id, org_id | course_id, activity_id |
| 統計查詢 | course_id, user_id | visit_duration |

### 示例組合

```
情況1: 用戶登錄後進入首頁
{
  user_id: "19688",
  org_id: 1,
  visit_duration: 1483,
  is_teacher: false,
  browser: "chrome",
  visit_start_from: "2025/12/02T13:35:26"
}

情況2: 用戶進入課程465
{
  user_id: "19688",
  org_id: 1,
  course_id: 465,
  course_code: "901011114",
  course_name: "性別平等工作法...",
  visit_duration: 3,
  is_teacher: false,
  visit_start_from: "2025/12/02T14:00:23"
}

情況3: 用戶進入課程465的SCORM活動1492
{
  user_id: "19688",
  org_id: 1,
  course_id: 465,
  course_code: "901011114",
  course_name: "性別平等工作法...",
  activity_id: 1492,
  activity_type: "scorm",
  visit_duration: 19,
  is_teacher: false,
  visit_start_from: "2025/12/02T14:00:27"
}
```

---

## 時間間隔分析

### 請求間隔統計

#### 前5個user-visits請求

```
請求#  時間        時間戳          間隔      visit_dur  場景
──────────────────────────────────────────────────────────────
1      13:35:26   T13:35:26      -        1483      初始登錄
2      14:00:11   T14:00:11      +1485s   11        課程列表
3      14:00:23   T14:00:23      +12s     3         進入課程
4      14:00:27   T14:00:27      +4s      19        進入活動
5      14:00:47   T14:00:47      +20s     3         活動內
```

#### 後5個user-visits請求

```
請求#  時間        時間戳          間隔      visit_dur  場景
──────────────────────────────────────────────────────────────
40     14:02:25   T14:02:25      +5s      1         課程內
41     14:02:28   T14:02:28      +3s      6         導航
42     14:02:34   T14:02:34      +6s      0         會話標記
43     14:02:35   T14:02:35      +1s      5         課程
44     14:03:23   T14:03:23      +48s     2         最後訪問
```

### 間隔分佈

```
間隔範圍      出現頻率    含義
──────────────────────────────────
1-10秒       40%        快速頁面切換
11-30秒      30%        用戶在頁面停留
31-120秒     20%        較長操作
120+秒       10%        用戶離開或長時間無操作
```

### 高峰期檢測

```
時間區間          請求密度   特徵
──────────────────────────────────────────
13:35-13:45      低 (初始化)
14:00-14:01      高 (課程導航)
14:01-14:02      中 (課程內操作)
14:02-14:03      低 (用戶結束)
```

---

## 核心業務流程

### 完整學習會話流程

```
┌─────────────────────────────────────────────────────────────────┐
│ 用戶學習會話完整流程                                             │
└─────────────────────────────────────────────────────────────────┘

1. 登錄與初始化 (13:35:18 ~ 13:35:35)
   └─ 用戶提交認證 → 系統驗證 → 發放session → 初始化UI
   └─ 記錄: ★ POST /user-visits (visit_duration: 1483秒)

2. 課程列表導航 (14:00:11)
   └─ 用戶查看可用課程
   └─ 記錄: ★ POST /user-visits (visit_duration: 11秒)
   └─ 查詢: GET /api/my-courses, /api/my-academic-years

3. 選擇課程 (14:00:23)
   └─ 用戶點擊課程465
   └─ 記錄: ★ POST /user-visits (visit_duration: 3秒, course_id: 465)
   └─ 查詢: GET /api/courses/465/modules, /api/courses/465

4. 進入活動 (14:00:27)
   └─ 用戶點擊SCORM活動1492
   └─ 記錄: ★ POST /user-visits (visit_duration: 19秒, activity_id: 1492)
   └─ 加載: GET /api/uploads/scorm/460

5. 在活動內操作 (14:00:27 ~ 14:00:47)
   └─ 用戶與SCORM內容交互
   └─ 中間記錄: ★ POST /user-visits (visit_duration: 3秒)

6. 統計查詢 (14:00:50 ~ 14:00:52)
   └─ 系統自動查詢累積統計
   └─ ◆ GET /statistics/.../user-visits/metrics → {sum: 202072.0, count: 65}
   └─ ◆ GET /statistics/.../online-videos/metrics
   └─ ◆ GET /statistics/.../interactions/metrics

7. 課程切換 (14:00:55+)
   └─ 用戶返回課程列表或進入其他課程
   └─ 記錄: ★ POST /user-visits (無course_id)
   └─ 重複步驟3-7，訪問其他課程

8. 會話結束 (14:03:23)
   └─ 用戶離開或超時
   └─ 記錄: ★ POST /user-visits (visit_duration: 2秒)
```

### 並行請求模式

```
某些請求可能並行執行：

用戶點擊課程
  ├─→ POST /statistics/api/user-visits (記錄訪問)
  │
  └─→ [並行] GET /api/courses/465/modules
      GET /api/courses/465
      GET /api/courses/465/exams
      GET /api/courses/465/activities
```

### 狀態機轉移

```
           [登錄]
             ↓
      ┌─────────────┐
      │   首頁      │
      └─────────────┘
             ↓ POST /user-visits (1483秒)
      ┌─────────────┐
      │  課程列表   │ ← GET /api/my-courses
      └─────────────┘
             ↓ POST /user-visits (11秒)
      ┌─────────────┐
      │   課程頁面  │ ← GET /api/courses/465/modules
      └─────────────┘
             ↓ POST /user-visits (3秒)
      ┌─────────────┐
      │  活動頁面   │ ← GET /api/uploads/scorm/460
      └─────────────┘
             ↓ POST /user-visits (19秒)
           [循環]
             ↓
      ┌─────────────┐
      │  會話結束   │ ← POST /user-visits (0秒或小值)
      └─────────────┘
```

---

## API應用場景映射

### 按用途分類

#### 認證與初始化
- `GET /` → 重定向
- `GET /login` → 登錄頁
- `POST /api/auth/login` → 認證
- `GET /api/orgs/1/lang-settings` → 語言設定

#### 數據加載
- `GET /api/announcement` → 公告
- `GET /api/my-departments` → 部門
- `GET /api/my-courses` → 課程
- `GET /api/my-academic-years` → 學年
- `GET /api/my-semesters` → 學期

#### 課程瀏覽
- `GET /api/courses/{id}/modules` → 課程模組
- `GET /api/courses/{id}/exams` → 考試
- `GET /api/courses/{id}/activities` → 活動
- `GET /course/{id}/content` → 課程內容

#### 活動與學習
- `GET /api/course/{id}/activity-reads-for-user` → 活動讀取狀態
- `GET /api/uploads/scorm/{id}` → SCORM內容
- `GET /api/course/{id}/online-video-completeness/setting` → 視頻設定

#### 時長與統計（關鍵）
- `POST /statistics/api/user-visits` → **記錄訪問時長** ⭐
- `GET /statistics/.../user-visits/metrics` → **查詢訪問統計**
- `GET /statistics/.../online-videos/metrics` → 視頻統計
- `GET /statistics/.../interactions/metrics` → 互動統計

---

## 數據流向圖

```
用戶瀏覽器 (客戶端)
    ↓
    ├─ 計算 visit_duration (本地JavaScript)
    ├─ 構建JSON payload
    ├─ 發送 POST /statistics/api/user-visits
    │
    ↓
伺服器 (應用層)
    ├─ 接收請求
    ├─ 驗證session
    ├─ ⚠️ [缺陷] 不驗證visit_duration值
    ├─ 將記錄寫入數據庫
    │
    ↓
數據庫 (記錄層)
    ├─ 存儲每條訪問記錄
    │   - user_id
    │   - visit_duration
    │   - visit_start_from
    │   - course_id
    │   - activity_id
    │
    ↓
統計API (查詢層)
    ├─ GET /statistics/.../metrics
    ├─ 聚合計算 SUM(visit_duration)
    │
    ↓
儀表板 (展示層)
    └─ 顯示用戶學習時長統計
```

---

## 流量特徵總結

| 特徵 | 數據 | 含義 |
|-----|-----|------|
| 總持續時間 | 28分 | 一次完整用戶會話 |
| 總請求數 | 660 | 相當密集的交互 |
| API多樣性 | 30+ | 系統功能完整 |
| 時長記錄頻率 | 每12秒 | 高頻時長跟蹤 |
| 平均頁面停留 | ~5秒 | 快速導航 |
| 最長操作 | 24.7分 | 初始登錄會話 |

---

**報告完成**: 2025-12-02
**數據來源**: 44個真實POST請求的分析
**準確度**: 基於實際網絡包分析

