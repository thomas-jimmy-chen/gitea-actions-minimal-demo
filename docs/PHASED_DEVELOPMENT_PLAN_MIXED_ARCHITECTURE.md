# 方案D 混合架構階段性開發計劃

**文檔版本**: 1.0
**創建日期**: 2025-12-01
**專案**: EEBot (Gleipnir) v2.x → v3.0
**架構方案**: 方案D - 混合架構（桌面原生 + API 後端 + 移動端可選）

---

## 目錄

1. [執行摘要](#1-執行摘要)
2. [現有代碼庫分析](#2-現有代碼庫分析)
3. [API 契約設計](#3-api-契約設計)
4. [Phase 1: 核心基礎設施與 API 後端](#phase-1-核心基礎設施與-api-後端)
5. [Phase 2: 桌面 GUI 開發](#phase-2-桌面-gui-開發)
6. [Phase 3: 移動端開發（可選）](#phase-3-移動端開發可選)
7. [測試策略](#7-測試策略)
8. [向後兼容性方案](#8-向後兼容性方案)
9. [部署與維護](#9-部署與維護)
10. [風險評估與緩解](#10-風險評估與緩解)

---

## 1. 執行摘要

### 1.1 目標

將現有的 EEBot v2.0.7 (CLI 單體架構) 重構為**混合架構**，支援：

- ✅ **桌面應用** (Windows/macOS/Linux) - CustomTkinter GUI
- ✅ **REST API 後端** - FastAPI 包裝現有自動化引擎
- ✅ **移動應用** (Android/iOS，Phase 3 可選) - React Native 或 Flutter

### 1.2 總時程估算

| 階段 | 交付成果 | 估計時數 | 優先級 |
|------|---------|---------|--------|
| **Phase 1** | REST API 後端 + 核心重構 | 26-32 小時 | 🔴 必須 |
| **Phase 2** | CustomTkinter 桌面 GUI | 18-26 小時 | 🔴 必須 |
| **Phase 3** | React Native 移動應用 | 16-24 小時 | 🟡 可選 |
| **總計** | 完整混合架構系統 | **60-82 小時** | - |

### 1.3 架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                    前端層 (Frontend)                         │
├──────────────────────────┬──────────────────────────────────┤
│  桌面應用 (Desktop)       │  移動應用 (Mobile - Phase 3)     │
│  • CustomTkinter (Python)│  • React Native / Flutter        │
│  • Windows/macOS/Linux   │  • Android / iOS                 │
└──────────────┬───────────┴──────────────┬───────────────────┘
               │                          │
               │      REST API (HTTP/JSON)│
               │      WebSocket (實時更新) │
               │                          │
┌──────────────▼──────────────────────────▼───────────────────┐
│                    API 層 (Backend)                          │
│  • FastAPI (Python)                                          │
│  • RESTful Endpoints                                         │
│  • WebSocket Server                                          │
│  • JWT 認證 (Phase 2+)                                       │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│              業務邏輯層 (Business Logic)                      │
│  • 現有 EEBot 核心引擎 (v2.0.7)                              │
│    - scenarios/ (CourseLearningScenario, ExamLearningScenario)│
│    - services/ (answer_matcher, question_bank, recommender)  │
│    - pages/ (POM - LoginPage, CourseListPage, etc.)         │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│              基礎設施層 (Infrastructure)                      │
│  • Selenium WebDriver (Browser Automation)                   │
│  • MitmProxy (API Interception)                              │
│  • SQLite / JSON (Data Persistence)                          │
│  • ConfigLoader (Configuration Management)                   │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. 現有代碼庫分析

### 2.1 目錄結構

```
eebot/
├── main.py                    # 主入口（CLI）
├── menu.py                    # 互動式選單（CLI）
├── eebot.py / eebot_legacy.py # 舊版入口
├── config/
│   └── eebot.cfg              # 配置檔案
├── data/
│   ├── courses.json           # 課程定義
│   └── schedule.json          # 排程資料
├── src/
│   ├── core/                  # 核心元件
│   │   ├── config_loader.py   # 配置載入器
│   │   ├── driver_manager.py  # WebDriver 管理
│   │   ├── cookie_manager.py  # Cookie 管理
│   │   └── proxy_manager.py   # MitmProxy 管理
│   ├── pages/                 # 頁面物件（POM）
│   │   ├── base_page.py       # 基底類
│   │   ├── login_page.py      # 登入頁面
│   │   ├── course_list_page.py # 課程列表
│   │   ├── course_detail_page.py # 課程詳情
│   │   ├── exam_detail_page.py # 考試詳情
│   │   └── exam_answer_page.py # 考試作答
│   ├── scenarios/             # 業務場景
│   │   ├── course_learning.py # 課程學習流程
│   │   └── exam_learning.py   # 考試流程
│   ├── services/              # 服務層
│   │   ├── answer_matcher.py  # 答案匹配
│   │   ├── question_bank.py   # 題庫管理
│   │   └── course_recommender.py # 課程推薦
│   ├── api/                   # API 攔截器
│   │   └── interceptors/
│   │       └── visit_duration.py # 訪問時長修改
│   ├── models/                # 資料模型
│   │   └── question.py        # 題目模型
│   └── utils/                 # 工具函數
│       ├── screenshot_utils.py # 截圖工具
│       ├── stealth_extractor.py # Stealth JS 提取
│       └── time_tracker.py    # 時間追蹤
└── docs/                      # 文檔
```

### 2.2 核心模組職責

| 模組 | 職責 | 重構需求 |
|------|------|---------|
| **core/** | 核心基礎設施（配置、Driver、Proxy） | ✅ 保持不變，包裝為 API |
| **pages/** | 頁面物件（POM 模式） | ✅ 保持不變，間接調用 |
| **scenarios/** | 業務流程編排 | ✅ 保持不變，API 層調用 |
| **services/** | 業務服務（答案匹配、題庫） | ✅ 保持不變，API 層調用 |
| **api/interceptors/** | MitmProxy 攔截器 | ✅ 保持不變 |
| **main.py** | CLI 主入口 | ⚠️ 保留但標記為 legacy |
| **menu.py** | 互動式選單 | ⚠️ 保留但標記為 legacy |

### 2.3 重構策略

#### 2.3.1 保留的組件（無需修改）

以下模組**完全保留**，不做任何修改：

- `src/core/` - 核心基礎設施
- `src/pages/` - 頁面物件
- `src/scenarios/` - 業務場景
- `src/services/` - 服務層
- `src/api/interceptors/` - API 攔截器
- `src/models/` - 資料模型
- `src/utils/` - 工具函數

#### 2.3.2 新增的組件

**Phase 1 新增**:

```
src/
├── api_server/              # 新增：API 後端
│   ├── main.py              # FastAPI 主入口
│   ├── api/                 # API 路由
│   │   ├── __init__.py
│   │   ├── courses.py       # 課程 API
│   │   ├── execution.py     # 執行控制 API
│   │   ├── config.py        # 配置 API
│   │   └── status.py        # 狀態監控 API
│   ├── schemas/             # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── course.py        # 課程 Schema
│   │   ├── execution.py     # 執行 Schema
│   │   └── response.py      # 通用 Response
│   ├── services/            # API 服務層（包裝器）
│   │   ├── __init__.py
│   │   ├── course_service.py # 課程服務
│   │   └── execution_service.py # 執行服務
│   └── websocket/           # WebSocket 伺服器
│       ├── __init__.py
│       └── manager.py       # 連線管理
```

**Phase 2 新增**:

```
src/
└── gui/                     # 新增：桌面 GUI
    ├── main.py              # GUI 主入口
    ├── windows/             # 視窗
    │   ├── __init__.py
    │   ├── main_window.py   # 主視窗
    │   ├── course_tab.py    # 課程管理 Tab
    │   ├── execution_tab.py # 執行監控 Tab
    │   └── config_tab.py    # 配置 Tab
    ├── widgets/             # 自訂元件
    │   ├── __init__.py
    │   ├── course_card.py   # 課程卡片
    │   └── log_viewer.py    # 日誌檢視器
    └── api_client/          # API 客戶端
        ├── __init__.py
        └── client.py        # HTTP + WebSocket 客戶端
```

**Phase 3 新增** (可選):

```
mobile/                      # 新增：移動應用
├── package.json             # React Native 配置
├── src/
│   ├── screens/             # 畫面
│   │   ├── CourseListScreen.tsx
│   │   ├── ExecutionScreen.tsx
│   │   └── SettingsScreen.tsx
│   ├── components/          # 元件
│   │   ├── CourseCard.tsx
│   │   └── StatusIndicator.tsx
│   └── services/            # API 服務
│       └── apiClient.ts     # HTTP + WebSocket
└── ...
```

#### 2.3.3 向後兼容性

- ✅ **保留 CLI 模式**：`main.py` 和 `menu.py` 繼續可用
- ✅ **共用配置**：GUI 和 CLI 使用相同的 `config/eebot.cfg`
- ✅ **資料格式**：`data/courses.json` 和 `data/schedule.json` 格式不變

---

## 3. API 契約設計

### 3.1 技術棧

- **框架**: FastAPI (Python)
- **通訊協議**:
  - HTTP/1.1 + JSON (RESTful API)
  - WebSocket (實時狀態更新)
- **認證**:
  - Phase 1: 無認證（本地使用）
  - Phase 2+: JWT Token（遠端訪問）
- **文檔**: Swagger UI (自動生成)

### 3.2 RESTful API 端點設計

#### 3.2.1 課程管理 API

**基礎路徑**: `/api/v1/courses`

| 方法 | 端點 | 描述 | 請求 | 回應 |
|------|------|------|------|------|
| `GET` | `/api/v1/courses` | 取得所有課程 | - | `{ "courses": [...] }` |
| `GET` | `/api/v1/courses/{id}` | 取得單一課程 | - | `{ "course": {...} }` |
| `POST` | `/api/v1/courses` | 新增課程 | `CourseCreate` | `{ "course": {...} }` |
| `PUT` | `/api/v1/courses/{id}` | 更新課程 | `CourseUpdate` | `{ "course": {...} }` |
| `DELETE` | `/api/v1/courses/{id}` | 刪除課程 | - | `{ "message": "..." }` |
| `GET` | `/api/v1/courses/scan` | 掃描可用課程 | - | `{ "available_courses": [...] }` |

**範例請求** (POST `/api/v1/courses`):

```json
{
  "program_name": "金融科技基礎課程",
  "lesson_name": "區塊鏈技術概論",
  "course_id": 12345,
  "course_type": "course",
  "enable_screenshot": false,
  "delay": 7.0
}
```

**範例回應** (200 OK):

```json
{
  "id": "uuid-xxx",
  "program_name": "金融科技基礎課程",
  "lesson_name": "區塊鏈技術概論",
  "course_id": 12345,
  "course_type": "course",
  "enable_screenshot": false,
  "delay": 7.0,
  "created_at": "2025-12-01T10:30:00Z",
  "updated_at": "2025-12-01T10:30:00Z"
}
```

#### 3.2.2 執行控制 API

**基礎路徑**: `/api/v1/execution`

| 方法 | 端點 | 描述 | 請求 | 回應 |
|------|------|------|------|------|
| `POST` | `/api/v1/execution/start` | 開始執行排程 | `{ "course_ids": [...] }` | `{ "execution_id": "..." }` |
| `POST` | `/api/v1/execution/stop` | 停止執行 | - | `{ "message": "..." }` |
| `POST` | `/api/v1/execution/pause` | 暫停執行 | - | `{ "message": "..." }` |
| `POST` | `/api/v1/execution/resume` | 恢復執行 | - | `{ "message": "..." }` |
| `GET` | `/api/v1/execution/status` | 取得執行狀態 | - | `{ "status": "...", "progress": {...} }` |
| `GET` | `/api/v1/execution/logs` | 取得執行日誌 | `?limit=100&offset=0` | `{ "logs": [...] }` |

**範例請求** (POST `/api/v1/execution/start`):

```json
{
  "course_ids": ["uuid-1", "uuid-2", "uuid-3"],
  "config_overrides": {
    "modify_visits": true,
    "visit_duration_increase": 9000,
    "headless_mode": false
  }
}
```

**範例回應** (200 OK):

```json
{
  "execution_id": "exec-2025-12-01-001",
  "status": "running",
  "started_at": "2025-12-01T10:35:00Z",
  "total_courses": 3,
  "current_course": {
    "id": "uuid-1",
    "name": "區塊鏈技術概論",
    "progress": 0
  }
}
```

**狀態回應範例** (GET `/api/v1/execution/status`):

```json
{
  "execution_id": "exec-2025-12-01-001",
  "status": "running",
  "started_at": "2025-12-01T10:35:00Z",
  "current_course": {
    "id": "uuid-1",
    "name": "區塊鏈技術概論",
    "progress": 45,
    "status": "in_progress"
  },
  "total_progress": {
    "completed": 0,
    "in_progress": 1,
    "pending": 2,
    "total": 3,
    "percentage": 15
  },
  "logs": [
    {
      "timestamp": "2025-12-01T10:35:10Z",
      "level": "INFO",
      "message": "登入成功"
    },
    {
      "timestamp": "2025-12-01T10:35:30Z",
      "level": "INFO",
      "message": "進入課程: 區塊鏈技術概論"
    }
  ]
}
```

#### 3.2.3 配置管理 API

**基礎路徑**: `/api/v1/config`

| 方法 | 端點 | 描述 | 請求 | 回應 |
|------|------|------|------|------|
| `GET` | `/api/v1/config` | 取得所有配置 | - | `{ "config": {...} }` |
| `GET` | `/api/v1/config/{key}` | 取得單一配置 | - | `{ "key": "...", "value": "..." }` |
| `PUT` | `/api/v1/config/{key}` | 更新配置 | `{ "value": "..." }` | `{ "key": "...", "value": "..." }` |
| `POST` | `/api/v1/config/reload` | 重新載入配置 | - | `{ "message": "..." }` |
| `GET` | `/api/v1/config/validate` | 驗證配置 | - | `{ "valid": true, "errors": [] }` |

**範例回應** (GET `/api/v1/config`):

```json
{
  "config": {
    "user_name": "***",
    "target_http": "https://elearning.post.gov.tw",
    "modify_visits": true,
    "visit_duration_increase": 9000,
    "headless_mode": false,
    "keep_browser_on_error": false,
    "listen_host": "127.0.0.1",
    "listen_port": "8080"
  },
  "source": {
    "user_name": "file",
    "target_http": "file",
    "modify_visits": "env",
    "visit_duration_increase": "file"
  }
}
```

#### 3.2.4 狀態監控 API

**基礎路徑**: `/api/v1/status`

| 方法 | 端點 | 描述 | 請求 | 回應 |
|------|------|------|------|------|
| `GET` | `/api/v1/status/health` | 健康檢查 | - | `{ "status": "ok" }` |
| `GET` | `/api/v1/status/version` | 取得版本資訊 | - | `{ "version": "3.0.0" }` |
| `GET` | `/api/v1/status/system` | 系統資源狀態 | - | `{ "cpu": 10, "memory": 45, ... }` |

### 3.3 WebSocket API

**端點**: `ws://localhost:8000/api/v1/ws/execution`

**用途**: 實時推送執行狀態更新

**訊息格式**:

```json
{
  "type": "status_update",
  "timestamp": "2025-12-01T10:36:00Z",
  "data": {
    "execution_id": "exec-2025-12-01-001",
    "status": "running",
    "current_course": {
      "id": "uuid-1",
      "name": "區塊鏈技術概論",
      "progress": 60
    },
    "total_progress": {
      "percentage": 20
    }
  }
}
```

**訊息類型**:

| 類型 | 描述 | 觸發時機 |
|------|------|---------|
| `status_update` | 狀態更新 | 每 2 秒或狀態變化時 |
| `log_message` | 日誌訊息 | 有新日誌產生時 |
| `course_completed` | 課程完成 | 單一課程完成時 |
| `execution_completed` | 執行完成 | 所有課程完成時 |
| `error` | 錯誤訊息 | 發生錯誤時 |

### 3.4 錯誤處理

**統一錯誤回應格式**:

```json
{
  "error": {
    "code": "COURSE_NOT_FOUND",
    "message": "找不到課程 ID: uuid-xxx",
    "details": {
      "course_id": "uuid-xxx"
    }
  }
}
```

**HTTP 狀態碼**:

| 狀態碼 | 說明 | 範例 |
|--------|------|------|
| `200` | 成功 | 取得資料成功 |
| `201` | 已創建 | 新增課程成功 |
| `400` | 請求錯誤 | 參數驗證失敗 |
| `404` | 找不到 | 課程 ID 不存在 |
| `409` | 衝突 | 執行中無法啟動新執行 |
| `500` | 伺服器錯誤 | 內部錯誤 |

---

## Phase 1: 核心基礎設施與 API 後端

### 階段目標

構建 REST API 後端，包裝現有 EEBot 核心引擎，提供 HTTP + WebSocket 介面。

### 時程估算

**總計**: 26-32 小時

| 任務 | 子任務 | 估計時數 |
|------|--------|---------|
| **1. 專案結構設置** | 建立 `src/api_server/` 目錄結構 | 1-2 h |
| | 安裝 FastAPI、Uvicorn、Pydantic 等依賴 | 0.5 h |
| | 建立基礎 `main.py` 與路由框架 | 1-2 h |
| **2. Pydantic Schema 設計** | 定義 Course、Execution、Config 模型 | 2-3 h |
| | 定義通用 Response/Error 模型 | 1 h |
| **3. 課程管理 API** | 實作 `/api/v1/courses` CRUD 端點 | 3-4 h |
| | 實作 `/api/v1/courses/scan` 掃描功能 | 2-3 h |
| | 包裝 `CourseRecommender` 服務 | 1-2 h |
| **4. 執行控制 API** | 實作 `/api/v1/execution/start` | 3-4 h |
| | 實作 `/api/v1/execution/stop/pause/resume` | 2-3 h |
| | 實作 `/api/v1/execution/status` | 2 h |
| | 包裝 `CourseLearningScenario` 與 `ExamLearningScenario` | 2-3 h |
| **5. 配置管理 API** | 實作 `/api/v1/config` CRUD 端點 | 2-3 h |
| **6. WebSocket 伺服器** | 實作 WebSocket 連線管理 | 2-3 h |
| | 實作實時狀態推送邏輯 | 2-3 h |
| **7. 測試** | 撰寫單元測試 | 2-3 h |
| | 撰寫整合測試 | 1-2 h |
| | 使用 Postman/Thunder Client 測試 API | 1-2 h |

### 關鍵交付成果

✅ **可運行的 FastAPI 伺服器** (`uvicorn src.api_server.main:app`)
✅ **完整的 RESTful API** (涵蓋課程、執行、配置管理)
✅ **WebSocket 實時更新** (執行狀態推送)
✅ **Swagger UI 文檔** (自動生成，訪問 `/docs`)
✅ **向後兼容** (CLI 模式仍可使用)

### 技術實作細節

#### 1.1 專案結構

```python
# src/api_server/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import courses, execution, config, status
from .websocket import manager

app = FastAPI(
    title="EEBot API",
    description="EEBot 自動化引擎 REST API",
    version="3.0.0"
)

# CORS 中介軟體（允許 GUI 存取）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(courses.router, prefix="/api/v1", tags=["courses"])
app.include_router(execution.router, prefix="/api/v1", tags=["execution"])
app.include_router(config.router, prefix="/api/v1", tags=["config"])
app.include_router(status.router, prefix="/api/v1", tags=["status"])

# WebSocket 端點
@app.websocket("/api/v1/ws/execution")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 保持連線並推送更新
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

#### 1.2 Pydantic Schema 範例

```python
# src/api_server/schemas/course.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class CourseBase(BaseModel):
    program_name: str = Field(..., description="課程計畫名稱")
    lesson_name: Optional[str] = Field(None, description="課程名稱（一般課程）")
    exam_name: Optional[str] = Field(None, description="考試名稱（考試類型）")
    course_id: int = Field(..., description="課程 ID")
    course_type: Literal["course", "exam"] = Field("course", description="類型")
    enable_screenshot: bool = Field(False, description="是否截圖")
    enable_auto_answer: bool = Field(False, description="是否自動答題（考試）")
    delay: float = Field(7.0, description="延遲時間（秒）")

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    program_name: Optional[str] = None
    lesson_name: Optional[str] = None
    exam_name: Optional[str] = None
    enable_screenshot: Optional[bool] = None
    enable_auto_answer: Optional[bool] = None
    delay: Optional[float] = None

class CourseResponse(CourseBase):
    id: str = Field(..., description="UUID")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

#### 1.3 服務層包裝範例

```python
# src/api_server/services/course_service.py
import json
from typing import List
from ...core.config_loader import ConfigLoader
from ...core.driver_manager import DriverManager
from ...pages.course_list_page import CourseListPage
from ...services.course_recommender import CourseRecommender

class CourseService:
    """課程服務 - 包裝現有業務邏輯"""

    def __init__(self):
        self.courses_file = 'data/courses.json'

    def get_all_courses(self) -> List[dict]:
        """取得所有課程（從 courses.json）"""
        with open(self.courses_file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        return data.get('courses', [])

    def create_course(self, course_data: dict) -> dict:
        """新增課程到 courses.json"""
        courses = self.get_all_courses()

        # 生成 UUID
        import uuid
        course_data['id'] = str(uuid.uuid4())
        course_data['created_at'] = datetime.now().isoformat()
        course_data['updated_at'] = datetime.now().isoformat()

        courses.append(course_data)
        self._save_courses(courses)
        return course_data

    def scan_available_courses(self, config: ConfigLoader) -> List[dict]:
        """掃描可用課程（包裝現有功能）"""
        # 初始化 Driver 和 CourseListPage
        driver_manager = DriverManager(config)
        driver = driver_manager.create_driver(use_proxy=False)
        course_list_page = CourseListPage(driver)

        # 登入並掃描
        # ... (省略登入邏輯)

        # 取得修習中課程
        programs = course_list_page.get_in_progress_programs()

        # 關閉 Driver
        driver_manager.quit()

        return programs

    def _save_courses(self, courses: List[dict]):
        """儲存課程到 courses.json"""
        data = {"courses": courses, "version": "1.0"}
        with open(self.courses_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
```

#### 1.4 執行控制服務

```python
# src/api_server/services/execution_service.py
import threading
from typing import List, Dict, Optional
from ...core.config_loader import ConfigLoader
from ...scenarios.course_learning import CourseLearningScenario
from ...scenarios.exam_learning import ExamLearningScenario

class ExecutionService:
    """執行控制服務"""

    def __init__(self):
        self.current_execution: Optional[Dict] = None
        self.execution_thread: Optional[threading.Thread] = None
        self.stop_flag = threading.Event()
        self.pause_flag = threading.Event()

    def start_execution(self, course_ids: List[str], config: ConfigLoader) -> str:
        """開始執行"""
        if self.is_running():
            raise ValueError("已有執行中的任務，無法啟動新執行")

        # 產生執行 ID
        from datetime import datetime
        execution_id = f"exec-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"

        # 載入課程
        courses = self._load_courses_by_ids(course_ids)

        # 建立執行狀態
        self.current_execution = {
            "execution_id": execution_id,
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "total_courses": len(courses),
            "completed_courses": 0,
            "current_course": courses[0] if courses else None,
            "logs": []
        }

        # 在背景執行
        self.stop_flag.clear()
        self.pause_flag.clear()
        self.execution_thread = threading.Thread(
            target=self._execute_courses,
            args=(courses, config)
        )
        self.execution_thread.start()

        return execution_id

    def _execute_courses(self, courses: List[dict], config: ConfigLoader):
        """執行課程（背景執行緒）"""
        # 分離課程和考試
        regular_courses = [c for c in courses if c.get('course_type') != 'exam']
        exams = [c for c in courses if c.get('course_type') == 'exam']

        try:
            # 執行一般課程
            if regular_courses:
                scenario = CourseLearningScenario(config, keep_browser_on_error=False)
                scenario.execute(regular_courses)
                self.current_execution['completed_courses'] += len(regular_courses)

            # 執行考試
            if exams:
                scenario = ExamLearningScenario(config, keep_browser_on_error=False)
                scenario.execute(exams)
                self.current_execution['completed_courses'] += len(exams)

            # 更新狀態
            self.current_execution['status'] = 'completed'

        except Exception as e:
            self.current_execution['status'] = 'failed'
            self.current_execution['error'] = str(e)

    def stop_execution(self):
        """停止執行"""
        if not self.is_running():
            raise ValueError("沒有執行中的任務")

        self.stop_flag.set()
        self.current_execution['status'] = 'stopped'

    def get_status(self) -> Dict:
        """取得執行狀態"""
        if not self.current_execution:
            return {"status": "idle"}
        return self.current_execution

    def is_running(self) -> bool:
        """檢查是否執行中"""
        return (self.current_execution and
                self.current_execution['status'] == 'running')
```

#### 1.5 WebSocket 管理器

```python
# src/api_server/websocket/manager.py
from fastapi import WebSocket
from typing import List

class ConnectionManager:
    """WebSocket 連線管理器"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """接受新連線"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """移除連線"""
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """廣播訊息給所有連線"""
        import json
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message, ensure_ascii=False))
            except:
                # 連線已斷開，移除
                self.active_connections.remove(connection)

manager = ConnectionManager()
```

### 測試計劃

#### 單元測試

```python
# tests/test_api/test_courses.py
import pytest
from fastapi.testclient import TestClient
from src.api_server.main import app

client = TestClient(app)

def test_get_all_courses():
    response = client.get("/api/v1/courses")
    assert response.status_code == 200
    assert "courses" in response.json()

def test_create_course():
    course_data = {
        "program_name": "測試課程計畫",
        "lesson_name": "測試課程",
        "course_id": 999,
        "course_type": "course"
    }
    response = client.post("/api/v1/courses", json=course_data)
    assert response.status_code == 201
    assert response.json()["program_name"] == "測試課程計畫"
```

#### 整合測試

```python
# tests/test_integration/test_execution_flow.py
def test_full_execution_flow():
    """測試完整執行流程"""
    # 1. 取得課程列表
    response = client.get("/api/v1/courses")
    courses = response.json()["courses"]

    # 2. 啟動執行
    course_ids = [c["id"] for c in courses[:1]]
    response = client.post("/api/v1/execution/start", json={"course_ids": course_ids})
    assert response.status_code == 200
    execution_id = response.json()["execution_id"]

    # 3. 檢查狀態
    response = client.get("/api/v1/execution/status")
    assert response.json()["status"] in ["running", "completed"]

    # 4. 停止執行
    response = client.post("/api/v1/execution/stop")
    assert response.status_code == 200
```

### 部署指南

```bash
# 1. 安裝依賴
pip install fastapi uvicorn[standard] pydantic websockets python-multipart

# 2. 啟動 API 伺服器（開發模式）
cd eebot
python -m uvicorn src.api_server.main:app --reload --host 127.0.0.1 --port 8000

# 3. 訪問 Swagger UI
# 瀏覽器開啟: http://127.0.0.1:8000/docs

# 4. 測試 WebSocket
# 使用 wscat 或 Postman 連接: ws://127.0.0.1:8000/api/v1/ws/execution
```

### 風險與緩解

| 風險 | 影響 | 機率 | 緩解措施 |
|------|------|------|---------|
| 現有代碼包裝困難 | 🔴 高 | 🟡 中 | 先進行小規模 PoC，驗證包裝可行性 |
| WebSocket 連線穩定性 | 🟡 中 | 🟡 中 | 實作重連機制 + 心跳檢測 |
| 多執行緒競爭條件 | 🟡 中 | 🟡 中 | 使用 `threading.Lock` 保護共享資源 |
| API 效能不佳 | 🟢 低 | 🟢 低 | 使用 `asyncio` 非同步處理 |

---

## Phase 2: 桌面 GUI 開發

### 階段目標

使用 **CustomTkinter** 開發跨平台桌面應用程式（Windows/macOS/Linux），提供友好的圖形介面取代現有 CLI。

### 時程估算

**總計**: 18-26 小時

| 任務 | 子任務 | 估計時數 |
|------|--------|---------|
| **1. 專案結構設置** | 建立 `src/gui/` 目錄結構 | 0.5 h |
| | 安裝 CustomTkinter 與依賴 | 0.5 h |
| | 建立主視窗框架 | 1-2 h |
| **2. API 客戶端** | 實作 HTTP Client (requests) | 2-3 h |
| | 實作 WebSocket Client | 2-3 h |
| | 實作錯誤處理與重連機制 | 1-2 h |
| **3. 課程管理 Tab** | 課程列表顯示（Table/ListView） | 2-3 h |
| | 新增/編輯/刪除課程對話框 | 2-3 h |
| | 課程掃描功能整合 | 1-2 h |
| **4. 執行監控 Tab** | 執行控制按鈕（開始/停止/暫停） | 1-2 h |
| | 進度條與狀態顯示 | 1-2 h |
| | 實時日誌檢視器 | 2-3 h |
| | WebSocket 實時更新整合 | 2-3 h |
| **5. 配置管理 Tab** | 配置表單（文字框、開關） | 2-3 h |
| | 配置載入與儲存 | 1-2 h |
| **6. UI/UX 優化** | 主題切換（亮色/暗色） | 1 h |
| | 錯誤提示與確認對話框 | 1-2 h |
| | 響應式佈局調整 | 1-2 h |

### 關鍵交付成果

✅ **完整的桌面應用程式** (可執行的 `.exe` / `.app` / Linux binary)
✅ **友好的圖形介面** (取代 CLI 模式)
✅ **實時監控** (WebSocket 自動更新)
✅ **跨平台支援** (Windows/macOS/Linux)

### 技術實作細節

#### 2.1 主視窗框架

```python
# src/gui/main.py
import customtkinter as ctk
from .windows.main_window import MainWindow

def main():
    """GUI 主入口"""
    # 設定主題
    ctk.set_appearance_mode("dark")  # "light", "dark", "system"
    ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

    # 建立主視窗
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
```

```python
# src/gui/windows/main_window.py
import customtkinter as ctk
from .course_tab import CourseTab
from .execution_tab import ExecutionTab
from .config_tab import ConfigTab
from ..api_client.client import APIClient

class MainWindow(ctk.CTk):
    """主視窗"""

    def __init__(self):
        super().__init__()

        # 視窗設定
        self.title("EEBot - Gleipnir v3.0")
        self.geometry("1200x800")

        # 初始化 API 客戶端
        self.api_client = APIClient(base_url="http://127.0.0.1:8000")

        # 建立 Tab 視圖
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # 新增 Tabs
        self.tab_courses = self.tabview.add("課程管理")
        self.tab_execution = self.tabview.add("執行監控")
        self.tab_config = self.tabview.add("配置管理")

        # 初始化各 Tab 內容
        self.course_tab = CourseTab(self.tab_courses, self.api_client)
        self.execution_tab = ExecutionTab(self.tab_execution, self.api_client)
        self.config_tab = ConfigTab(self.tab_config, self.api_client)

        # 啟動 API 伺服器檢查
        self.check_api_server()

    def check_api_server(self):
        """檢查 API 伺服器是否運行"""
        try:
            health = self.api_client.get_health()
            if health["status"] == "ok":
                print("[INFO] API 伺服器連線成功")
            else:
                self.show_error("API 伺服器狀態異常")
        except Exception as e:
            self.show_error(f"無法連線到 API 伺服器\n請先啟動: python -m uvicorn src.api_server.main:app\n\n錯誤: {e}")

    def show_error(self, message: str):
        """顯示錯誤對話框"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("錯誤")
        dialog.geometry("400x200")

        label = ctk.CTkLabel(dialog, text=message, wraplength=350)
        label.pack(padx=20, pady=20)

        button = ctk.CTkButton(dialog, text="確定", command=dialog.destroy)
        button.pack(pady=10)
```

#### 2.2 API 客戶端

```python
# src/gui/api_client/client.py
import requests
import websocket
import json
from typing import Callable, Optional

class APIClient:
    """API 客戶端"""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.ws: Optional[websocket.WebSocketApp] = None

    # ===== HTTP 請求 =====

    def get_all_courses(self):
        """取得所有課程"""
        response = requests.get(f"{self.base_url}/api/v1/courses")
        response.raise_for_status()
        return response.json()

    def create_course(self, course_data: dict):
        """新增課程"""
        response = requests.post(f"{self.base_url}/api/v1/courses", json=course_data)
        response.raise_for_status()
        return response.json()

    def delete_course(self, course_id: str):
        """刪除課程"""
        response = requests.delete(f"{self.base_url}/api/v1/courses/{course_id}")
        response.raise_for_status()
        return response.json()

    def start_execution(self, course_ids: list, config_overrides: dict = None):
        """開始執行"""
        payload = {"course_ids": course_ids}
        if config_overrides:
            payload["config_overrides"] = config_overrides

        response = requests.post(f"{self.base_url}/api/v1/execution/start", json=payload)
        response.raise_for_status()
        return response.json()

    def stop_execution(self):
        """停止執行"""
        response = requests.post(f"{self.base_url}/api/v1/execution/stop")
        response.raise_for_status()
        return response.json()

    def get_execution_status(self):
        """取得執行狀態"""
        response = requests.get(f"{self.base_url}/api/v1/execution/status")
        response.raise_for_status()
        return response.json()

    def get_health(self):
        """健康檢查"""
        response = requests.get(f"{self.base_url}/api/v1/status/health")
        response.raise_for_status()
        return response.json()

    # ===== WebSocket =====

    def connect_websocket(self, on_message: Callable):
        """連接 WebSocket"""
        ws_url = self.base_url.replace("http://", "ws://") + "/api/v1/ws/execution"

        def on_ws_message(ws, message):
            data = json.loads(message)
            on_message(data)

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_ws_message,
            on_error=lambda ws, error: print(f"[WS ERROR] {error}"),
            on_close=lambda ws, close_status_code, close_msg: print("[WS] Disconnected")
        )

        # 在背景執行
        import threading
        ws_thread = threading.Thread(target=self.ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()

    def disconnect_websocket(self):
        """斷開 WebSocket"""
        if self.ws:
            self.ws.close()
```

#### 2.3 課程管理 Tab

```python
# src/gui/windows/course_tab.py
import customtkinter as ctk
from tkinter import ttk

class CourseTab:
    """課程管理 Tab"""

    def __init__(self, parent, api_client):
        self.parent = parent
        self.api_client = api_client

        # 建立 UI
        self.create_widgets()

        # 載入課程
        self.load_courses()

    def create_widgets(self):
        """建立元件"""
        # 工具列
        toolbar = ctk.CTkFrame(self.parent)
        toolbar.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(toolbar, text="新增課程", command=self.add_course).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="掃描課程", command=self.scan_courses).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="刷新", command=self.load_courses).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="刪除", command=self.delete_course).pack(side="left", padx=5)

        # 課程表格
        columns = ("id", "program_name", "lesson_name", "course_id", "type")
        self.tree = ttk.Treeview(self.parent, columns=columns, show="headings", height=20)

        self.tree.heading("id", text="ID")
        self.tree.heading("program_name", text="課程計畫")
        self.tree.heading("lesson_name", text="課程名稱")
        self.tree.heading("course_id", text="課程 ID")
        self.tree.heading("type", text="類型")

        self.tree.column("id", width=100)
        self.tree.column("program_name", width=300)
        self.tree.column("lesson_name", width=300)
        self.tree.column("course_id", width=100)
        self.tree.column("type", width=100)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # 捲軸
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def load_courses(self):
        """載入課程列表"""
        try:
            response = self.api_client.get_all_courses()
            courses = response.get("courses", [])

            # 清空表格
            for item in self.tree.get_children():
                self.tree.delete(item)

            # 填充資料
            for course in courses:
                self.tree.insert("", "end", values=(
                    course.get("id", ""),
                    course.get("program_name", ""),
                    course.get("lesson_name") or course.get("exam_name", ""),
                    course.get("course_id", ""),
                    course.get("course_type", "")
                ))
        except Exception as e:
            print(f"[ERROR] 載入課程失敗: {e}")

    def add_course(self):
        """新增課程對話框"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("新增課程")
        dialog.geometry("400x500")

        # 表單欄位
        ctk.CTkLabel(dialog, text="課程計畫名稱:").pack(pady=5)
        program_name_entry = ctk.CTkEntry(dialog, width=300)
        program_name_entry.pack(pady=5)

        ctk.CTkLabel(dialog, text="課程名稱:").pack(pady=5)
        lesson_name_entry = ctk.CTkEntry(dialog, width=300)
        lesson_name_entry.pack(pady=5)

        ctk.CTkLabel(dialog, text="課程 ID:").pack(pady=5)
        course_id_entry = ctk.CTkEntry(dialog, width=300)
        course_id_entry.pack(pady=5)

        ctk.CTkLabel(dialog, text="類型:").pack(pady=5)
        course_type_var = ctk.StringVar(value="course")
        ctk.CTkRadioButton(dialog, text="一般課程", variable=course_type_var, value="course").pack(pady=2)
        ctk.CTkRadioButton(dialog, text="考試", variable=course_type_var, value="exam").pack(pady=2)

        ctk.CTkLabel(dialog, text="截圖:").pack(pady=5)
        screenshot_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(dialog, text="啟用截圖", variable=screenshot_var).pack(pady=5)

        # 確認按鈕
        def submit():
            course_data = {
                "program_name": program_name_entry.get(),
                "lesson_name": lesson_name_entry.get() if course_type_var.get() == "course" else None,
                "exam_name": lesson_name_entry.get() if course_type_var.get() == "exam" else None,
                "course_id": int(course_id_entry.get()),
                "course_type": course_type_var.get(),
                "enable_screenshot": screenshot_var.get()
            }

            try:
                self.api_client.create_course(course_data)
                dialog.destroy()
                self.load_courses()
            except Exception as e:
                print(f"[ERROR] 新增課程失敗: {e}")

        ctk.CTkButton(dialog, text="確定", command=submit).pack(pady=20)

    def scan_courses(self):
        """掃描課程"""
        # TODO: 實作掃描功能
        print("[INFO] 掃描課程...")

    def delete_course(self):
        """刪除選中的課程"""
        selected = self.tree.selection()
        if not selected:
            return

        course_id = self.tree.item(selected[0])["values"][0]

        try:
            self.api_client.delete_course(course_id)
            self.load_courses()
        except Exception as e:
            print(f"[ERROR] 刪除課程失敗: {e}")
```

#### 2.4 執行監控 Tab

```python
# src/gui/windows/execution_tab.py
import customtkinter as ctk

class ExecutionTab:
    """執行監控 Tab"""

    def __init__(self, parent, api_client):
        self.parent = parent
        self.api_client = api_client
        self.is_running = False

        # 建立 UI
        self.create_widgets()

        # 連接 WebSocket
        self.api_client.connect_websocket(self.on_websocket_message)

    def create_widgets(self):
        """建立元件"""
        # 控制按鈕
        control_frame = ctk.CTkFrame(self.parent)
        control_frame.pack(fill="x", padx=10, pady=10)

        self.start_button = ctk.CTkButton(control_frame, text="開始執行", command=self.start_execution)
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ctk.CTkButton(control_frame, text="停止", command=self.stop_execution, state="disabled")
        self.stop_button.pack(side="left", padx=5)

        # 狀態顯示
        status_frame = ctk.CTkFrame(self.parent)
        status_frame.pack(fill="x", padx=10, pady=10)

        self.status_label = ctk.CTkLabel(status_frame, text="狀態: 閒置", font=("Arial", 16))
        self.status_label.pack(pady=10)

        # 進度條
        self.progress_bar = ctk.CTkProgressBar(self.parent, width=800)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(self.parent, text="0 / 0 課程完成")
        self.progress_label.pack()

        # 日誌檢視器
        log_frame = ctk.CTkFrame(self.parent)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(log_frame, text="執行日誌:", font=("Arial", 14)).pack(anchor="w", padx=5, pady=5)

        self.log_textbox = ctk.CTkTextbox(log_frame, width=800, height=400)
        self.log_textbox.pack(fill="both", expand=True, padx=5, pady=5)

    def start_execution(self):
        """開始執行"""
        try:
            # 取得所有課程 ID
            courses = self.api_client.get_all_courses()
            course_ids = [c["id"] for c in courses.get("courses", [])]

            if not course_ids:
                self.log("沒有可執行的課程")
                return

            # 啟動執行
            response = self.api_client.start_execution(course_ids)
            self.log(f"執行已啟動: {response['execution_id']}")

            # 更新 UI
            self.is_running = True
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.status_label.configure(text="狀態: 執行中")

        except Exception as e:
            self.log(f"[ERROR] 啟動執行失敗: {e}")

    def stop_execution(self):
        """停止執行"""
        try:
            response = self.api_client.stop_execution()
            self.log("執行已停止")

            # 更新 UI
            self.is_running = False
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.status_label.configure(text="狀態: 已停止")

        except Exception as e:
            self.log(f"[ERROR] 停止執行失敗: {e}")

    def on_websocket_message(self, data: dict):
        """處理 WebSocket 訊息"""
        msg_type = data.get("type")

        if msg_type == "status_update":
            # 更新進度
            progress_data = data.get("data", {}).get("total_progress", {})
            completed = progress_data.get("completed", 0)
            total = progress_data.get("total", 1)
            percentage = progress_data.get("percentage", 0)

            self.progress_bar.set(percentage / 100)
            self.progress_label.configure(text=f"{completed} / {total} 課程完成")

        elif msg_type == "log_message":
            # 新增日誌
            log_data = data.get("data", {})
            self.log(f"[{log_data.get('level')}] {log_data.get('message')}")

        elif msg_type == "execution_completed":
            # 執行完成
            self.log("所有課程執行完成！")
            self.is_running = False
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.status_label.configure(text="狀態: 完成")

    def log(self, message: str):
        """新增日誌"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_textbox.insert("end", f"[{timestamp}] {message}\n")
        self.log_textbox.see("end")  # 自動捲動到底部
```

### 打包與分發

#### Windows 打包 (PyInstaller)

```bash
# 安裝 PyInstaller
pip install pyinstaller

# 打包成單一 .exe 檔案
pyinstaller --onefile --windowed --name "EEBot" --icon="resource/icon.ico" src/gui/main.py

# 輸出: dist/EEBot.exe
```

#### macOS 打包 (py2app)

```bash
# 安裝 py2app
pip install py2app

# 生成 setup.py
py2applet --make-setup src/gui/main.py

# 打包
python setup.py py2app

# 輸出: dist/EEBot.app
```

#### Linux 打包 (AppImage)

```bash
# 使用 PyInstaller + AppImage
pyinstaller --onefile src/gui/main.py
# 將輸出包裝成 AppImage (需要額外工具)
```

### 測試計劃

- ✅ **手動測試**: 在 Windows/macOS/Linux 上測試所有功能
- ✅ **UI 測試**: 驗證所有按鈕、輸入框、表格是否正常運作
- ✅ **整合測試**: 確保 GUI 與 API 伺服器通訊正常
- ✅ **效能測試**: 驗證大量課程時 UI 不卡頓

---

## Phase 3: 移動端開發（可選）

### 階段目標

使用 **React Native** 或 **Flutter** 開發 Android/iOS 應用，與桌面版共用同一套 REST API。

### 時程估算

**總計**: 16-24 小時

| 任務 | 子任務 | 估計時數 |
|------|--------|---------|
| **1. 專案設置** | 建立 React Native / Flutter 專案 | 1-2 h |
| | 安裝導航、狀態管理庫 | 1 h |
| **2. API 客戶端** | 實作 HTTP Client (Axios / Dio) | 2-3 h |
| | 實作 WebSocket Client | 1-2 h |
| **3. 畫面開發** | 課程列表畫面 | 3-4 h |
| | 執行監控畫面 | 3-4 h |
| | 設定畫面 | 2-3 h |
| **4. UI/UX 優化** | 響應式設計 | 2-3 h |
| | 錯誤處理與載入狀態 | 1-2 h |
| **5. 打包與測試** | Android APK 打包 | 1 h |
| | iOS IPA 打包 | 1 h |

### 關鍵交付成果

✅ **Android APK** (可安裝的應用程式)
✅ **iOS IPA** (可透過 TestFlight 分發)
✅ **與桌面版功能對等** (課程管理、執行監控)

### 技術實作細節（React Native 範例）

#### 3.1 專案結構

```
mobile/
├── package.json
├── App.tsx                    # 主入口
├── src/
│   ├── screens/               # 畫面
│   │   ├── CourseListScreen.tsx
│   │   ├── ExecutionScreen.tsx
│   │   └── SettingsScreen.tsx
│   ├── components/            # 元件
│   │   ├── CourseCard.tsx
│   │   └── StatusIndicator.tsx
│   ├── services/              # API 服務
│   │   └── apiClient.ts
│   ├── navigation/            # 導航
│   │   └── AppNavigator.tsx
│   └── types/                 # TypeScript 類型
│       └── index.ts
├── android/                   # Android 原生代碼
└── ios/                       # iOS 原生代碼
```

#### 3.2 API 客戶端 (TypeScript)

```typescript
// src/services/apiClient.ts
import axios from 'axios';

const API_BASE_URL = 'http://YOUR_SERVER_IP:8000';  // 替換為實際 IP

class APIClient {
  async getAllCourses() {
    const response = await axios.get(`${API_BASE_URL}/api/v1/courses`);
    return response.data;
  }

  async startExecution(courseIds: string[]) {
    const response = await axios.post(`${API_BASE_URL}/api/v1/execution/start`, {
      course_ids: courseIds
    });
    return response.data;
  }

  async getExecutionStatus() {
    const response = await axios.get(`${API_BASE_URL}/api/v1/execution/status`);
    return response.data;
  }

  // ... 其他方法
}

export default new APIClient();
```

#### 3.3 課程列表畫面

```typescript
// src/screens/CourseListScreen.tsx
import React, { useEffect, useState } from 'react';
import { View, FlatList, Text, TouchableOpacity } from 'react-native';
import apiClient from '../services/apiClient';

export default function CourseListScreen() {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      const data = await apiClient.getAllCourses();
      setCourses(data.courses);
    } catch (error) {
      console.error('載入課程失敗', error);
    }
  };

  return (
    <View style={{ flex: 1 }}>
      <FlatList
        data={courses}
        renderItem={({ item }) => (
          <TouchableOpacity style={{ padding: 15, borderBottomWidth: 1 }}>
            <Text style={{ fontSize: 18 }}>{item.program_name}</Text>
            <Text style={{ color: 'gray' }}>{item.lesson_name || item.exam_name}</Text>
          </TouchableOpacity>
        )}
        keyExtractor={(item) => item.id}
      />
    </View>
  );
}
```

### 部署指南

```bash
# Android 打包
cd mobile
npx react-native bundle --platform android
cd android && ./gradlew assembleRelease
# 輸出: android/app/build/outputs/apk/release/app-release.apk

# iOS 打包（需要 macOS + Xcode）
cd mobile
npx react-native bundle --platform ios
cd ios && xcodebuild -scheme YourApp archive
# 使用 Xcode Organizer 匯出 IPA
```

---

## 7. 測試策略

### 7.1 單元測試

| 層級 | 測試工具 | 覆蓋範圍 |
|------|---------|---------|
| API 後端 | pytest + FastAPI TestClient | 所有 API 端點 |
| GUI | unittest (Python) | API 客戶端邏輯 |
| 移動端 | Jest + React Native Testing Library | 元件與畫面 |

**範例**:

```python
# tests/test_api/test_execution.py
import pytest
from fastapi.testclient import TestClient
from src.api_server.main import app

client = TestClient(app)

def test_start_execution():
    # 1. 建立測試課程
    course_data = {
        "program_name": "測試計畫",
        "lesson_name": "測試課程",
        "course_id": 999,
        "course_type": "course"
    }
    response = client.post("/api/v1/courses", json=course_data)
    course_id = response.json()["id"]

    # 2. 啟動執行
    response = client.post("/api/v1/execution/start", json={"course_ids": [course_id]})
    assert response.status_code == 200
    assert "execution_id" in response.json()

    # 3. 檢查狀態
    response = client.get("/api/v1/execution/status")
    assert response.json()["status"] in ["running", "completed"]
```

### 7.2 整合測試

- ✅ **API + 業務邏輯**: 驗證 API 正確調用現有 scenarios
- ✅ **GUI + API**: 驗證 GUI 與 API 伺服器通訊
- ✅ **WebSocket**: 驗證實時更新機制

### 7.3 E2E 測試

- ✅ **完整流程**: 新增課程 → 啟動執行 → 監控進度 → 完成
- ✅ **錯誤處理**: 測試各種異常情況（API 離線、執行失敗等）

---

## 8. 向後兼容性方案

### 8.1 CLI 模式保留

- ✅ **保留入口**: `main.py` 和 `menu.py` 繼續可用
- ✅ **獨立運行**: 不依賴 API 伺服器，直接調用 scenarios
- ✅ **文檔標記**: 在文檔中標記為 "Legacy Mode"

### 8.2 配置共用

- ✅ **統一配置檔**: `config/eebot.cfg` 同時被 CLI 和 API 讀取
- ✅ **環境變數**: 支援 `.env` 覆蓋配置

### 8.3 資料格式

- ✅ **不修改**: `data/courses.json` 和 `data/schedule.json` 格式保持不變
- ✅ **API 擴展**: API 新增 UUID 等欄位，但不影響原有 JSON 結構

### 8.4 遷移路徑

**階段 1**: 並行運行（v2.x CLI + v3.0 API）

```
用戶可選擇:
- 繼續使用 CLI: python main.py
- 使用 GUI: python src/gui/main.py
```

**階段 2**: 推薦 GUI（v3.1+）

```
- 預設啟動 GUI
- CLI 標記為 "Legacy Mode"
- 文檔建議使用 GUI
```

**階段 3**: 棄用 CLI（v4.0+，可選）

```
- 移除 main.py 和 menu.py（保留在 legacy/ 目錄）
- GUI 成為唯一入口
```

---

## 9. 部署與維護

### 9.1 部署方式

#### 開發環境

```bash
# 1. 啟動 API 伺服器（終端機 1）
python -m uvicorn src.api_server.main:app --reload --host 127.0.0.1 --port 8000

# 2. 啟動 GUI（終端機 2）
python src/gui/main.py
```

#### 生產環境（單機版）

```bash
# 使用 systemd (Linux) 或 NSSM (Windows) 自動啟動 API 伺服器
# GUI 打包成 .exe / .app 分發給使用者
```

#### 生產環境（Client-Server，未來）

```bash
# 伺服器端: 部署 FastAPI 到 VPS
# 客戶端: 分發 GUI .exe / .app
# 認證: 啟用 JWT Token
```

### 9.2 監控與日誌

- ✅ **API 日誌**: 使用 `logging` 模組記錄所有 API 請求
- ✅ **執行日誌**: 透過 WebSocket 即時推送給 GUI
- ✅ **錯誤追蹤**: 記錄 traceback 到 `logs/` 目錄

### 9.3 更新機制

- ✅ **API 版本控制**: 使用 `/api/v1/` 前綴，未來可升級到 `/api/v2/`
- ✅ **GUI 自動更新**: 整合 auto-updater（Phase 2+）

---

## 10. 風險評估與緩解

### 10.1 技術風險

| 風險 | 影響 | 機率 | 緩解措施 |
|------|------|------|---------|
| 現有代碼包裝困難 | 🔴 高 | 🟡 中 | 先進行 PoC，驗證包裝可行性 |
| WebSocket 連線不穩定 | 🟡 中 | 🟡 中 | 實作重連機制 + 心跳檢測 |
| GUI 跨平台兼容問題 | 🟡 中 | 🟢 低 | 在 3 個平台上進行完整測試 |
| 多執行緒競爭條件 | 🟡 中 | 🟡 中 | 使用 `threading.Lock` 保護共享資源 |
| 移動端 API 跨網路訪問 | 🟢 低 | 🟡 中 | 實作 JWT 認證 + HTTPS |

### 10.2 時程風險

| 風險 | 影響 | 機率 | 緩解措施 |
|------|------|------|---------|
| 時間估算不準確 | 🟡 中 | 🟡 中 | 預留 20% buffer time |
| 依賴套件版本衝突 | 🟢 低 | 🟢 低 | 使用虛擬環境 + requirements.txt 鎖定版本 |
| 測試時間不足 | 🟡 中 | 🟡 中 | 將測試納入估算，Phase 1 優先測試 |

### 10.3 使用者體驗風險

| 風險 | 影響 | 機率 | 緩解措施 |
|------|------|------|---------|
| GUI 學習曲線 | 🟢 低 | 🟢 低 | 設計直覺的 UI + 提供教學文檔 |
| API 伺服器啟動複雜 | 🟡 中 | 🟡 中 | GUI 內建啟動腳本 + 一鍵啟動 |
| 移動端網路延遲 | 🟡 中 | 🟡 中 | 優化 API 回應速度 + 載入指示器 |

---

## 11. 總結與建議

### 11.1 推薦實施順序

1. ✅ **Phase 1 (必須)**: REST API 後端 (26-32 小時)
   - 提供核心 API 介面
   - 可獨立測試與驗證
   - 為 Phase 2 打下基礎

2. ✅ **Phase 2 (必須)**: 桌面 GUI (18-26 小時)
   - 提升使用者體驗
   - 跨平台支援（桌面端）
   - 完成混合架構核心

3. 🟡 **Phase 3 (可選)**: 移動端應用 (16-24 小時)
   - 根據實際需求決定
   - 可延後到 v3.1 或 v3.2 版本
   - 需要評估移動端使用場景

### 11.2 開發里程碑

| 里程碑 | 完成標準 | 預計時間 |
|--------|---------|---------|
| **M1: API MVP** | 基礎 CRUD API + 執行控制 | Phase 1 Week 1-2 |
| **M2: API 完整版** | WebSocket + 所有端點 | Phase 1 Week 2-3 |
| **M3: GUI MVP** | 課程管理 + 執行監控基礎 UI | Phase 2 Week 1 |
| **M4: GUI 完整版** | 所有功能 + 打包分發 | Phase 2 Week 2-3 |
| **M5: 移動端 MVP** | 課程列表 + 執行監控 | Phase 3 Week 1 |
| **M6: 移動端完整版** | 所有功能 + 打包分發 | Phase 3 Week 2 |

### 11.3 成功標準

- ✅ API 伺服器穩定運行，所有端點正常
- ✅ 桌面 GUI 在 Windows/macOS/Linux 上流暢運行
- ✅ WebSocket 實時更新無延遲
- ✅ 向後兼容 CLI 模式
- ✅ 完整的測試覆蓋（>80%）
- ✅ 文檔完整（API 文檔 + 使用手冊）

### 11.4 後續優化方向

- 🔹 **Phase 4 (未來)**: Client-Server 架構完整實現
  - JWT 認證
  - RBAC 權限管理
  - 多用戶支援
  - 遠端部署

- 🔹 **Phase 5 (未來)**: TMS+ 平台支援
  - 實作 TMS+ 平台 Locators
  - Strategy Pattern 切換平台
  - 平台自動檢測

---

## 附錄 A: 開發環境設置

### Python 依賴

```bash
# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt
```

**requirements.txt** (Phase 1 + Phase 2):

```
# 現有依賴
selenium==4.16.0
mitmproxy==10.1.5
python-dotenv==1.0.0

# Phase 1 新增
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
websockets==12.0
python-multipart==0.0.6

# Phase 2 新增
customtkinter==5.2.1
Pillow==10.2.0

# 測試
pytest==7.4.3
pytest-asyncio==0.23.3
httpx==0.26.0  # FastAPI 測試客戶端
```

### IDE 建議

- **VSCode** + Python Extension
- **PyCharm Professional** (推薦，內建 FastAPI 支援)

---

## 附錄 B: API 完整端點清單

請參閱 Swagger UI 文檔: `http://127.0.0.1:8000/docs`

---

## 附錄 C: 參考資料

- [FastAPI 官方文檔](https://fastapi.tiangolo.com/)
- [CustomTkinter 文檔](https://github.com/TomSchimansky/CustomTkinter)
- [React Native 官方文檔](https://reactnative.dev/)
- [Flutter 官方文檔](https://flutter.dev/)
- [WebSocket Protocol RFC 6455](https://tools.ietf.org/html/rfc6455)

---

**文檔結束**

**最後更新**: 2025-12-01
**作者**: Claude Code (Anthropic)
**審閱者**: 待定
