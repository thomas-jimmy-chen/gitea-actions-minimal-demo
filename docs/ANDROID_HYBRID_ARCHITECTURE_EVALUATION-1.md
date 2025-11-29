# EEBot Android 移植評估報告 - 混合架構方案 (第 1 段)

> **分段資訊**: 本文檔共 2 段
> - 📄 **當前**: 第 1 段 - 執行摘要、技術架構與實施計畫
> - ➡️ **下一段**: [ANDROID_HYBRID_ARCHITECTURE_EVALUATION-2.md](./ANDROID_HYBRID_ARCHITECTURE_EVALUATION-2.md)
> - 📑 **完整索引**: [返回索引](./ANDROID_HYBRID_ARCHITECTURE_EVALUATION.md)

---

> **文檔類型**: 技術評估報告
> **專案代號**: Gleipnir (格萊普尼爾)
> **評估日期**: 2025-11-24
> **報告版本**: 1.0 (分段處理: 2025-11-27)
> **評估者**: wizard03 (with Claude Code CLI - Sonnet 4.5)

---

## 📋 目錄

- [執行摘要](#執行摘要)
- [技術架構詳解](#技術架構詳解)
- [實施計畫](#實施計畫)
- [成本效益分析](#成本效益分析)
- [風險評估與緩解](#風險評估與緩解)
- [概念驗證 (PoC)](#概念驗證-poc)
- [部署選項分析](#部署選項分析)
- [安全性設計](#安全性設計)
- [使用者體驗設計](#使用者體驗設計)
- [可擴展性規劃](#可擴展性規劃)
- [結論與建議](#結論與建議)

---

## 📊 執行摘要

### 背景

EEBot (Gleipnir) 是基於 Python + Selenium + MitmProxy 的桌面自動化工具，用於台灣郵政 e 大學課程自動化學習。使用者希望將此工具移植到 Android 平台。

### 核心問題

**能否完整移植到 Android？**
- ❌ **完全移植**: 不可行
  - Selenium WebDriver 無 Android Chrome 官方支援
  - MitmProxy 需要系統級權限（Root 或 VPN Service）
  - 預估需重寫 60-80% 代碼，開發時間 150+ 小時

### 推薦方案

**🏆 混合架構 (Hybrid Architecture)**
- ✅ **可行性**: 完全可行
- ✅ **成本**: 低 (18-28 小時開發)
- ✅ **相容性**: 100% 保留現有功能
- ✅ **體驗**: 隨時隨地控制執行

### 方案概述

```
Android 設備 (控制端)
  ├── Termux (Python 環境)
  ├── 簡化版選單介面
  └── API Client (HTTP/HTTPS)
        ↓
        ↓ RESTful API
        ↓
雲端/PC 伺服器 (執行端)
  ├── Flask API Server
  ├── 原有 EEBot 核心 (無需修改)
  ├── Selenium WebDriver
  ├── MitmProxy
  └── Chrome Browser
```

### 關鍵優勢

| 優勢 | 說明 |
|------|------|
| **零代碼重寫** | 核心邏輯 100% 保留 |
| **快速實施** | 18-28 小時完成 |
| **靈活部署** | 雲端或本地 PC 均可 |
| **安全隔離** | Android 端無需 Root |
| **易於維護** | 分離架構，獨立更新 |

---

## 🏗️ 技術架構詳解

### 系統分層架構

```
┌─────────────────────────────────────────────────────────────┐
│                        用戶層 (User Layer)                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Android 設備 (手機/平板)                              │  │
│  │  └── Termux App (Python 3.x 環境)                     │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ HTTPS (TLS 1.3)
                             │ JSON over HTTP
                             │
┌────────────────────────────▼────────────────────────────────┐
│                     API 層 (API Layer)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Flask RESTful API Server                             │  │
│  │  ├── 認證中介層 (JWT Token)                           │  │
│  │  ├── 路由控制 (Routes)                                │  │
│  │  ├── 請求驗證 (Validation)                            │  │
│  │  └── 錯誤處理 (Error Handling)                        │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ 內部調用
                             │
┌────────────────────────────▼────────────────────────────────┐
│                   業務邏輯層 (Business Layer)                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  EEBot 核心 (100% 原有代碼)                           │  │
│  │  ├── src/scenarios/course_learning.py                 │  │
│  │  ├── src/scenarios/exam_learning.py                   │  │
│  │  ├── src/pages/* (所有頁面物件)                       │  │
│  │  ├── src/services/* (所有服務)                        │  │
│  │  └── src/core/* (所有核心模組)                        │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ WebDriver Protocol
                             │ MitmProxy API
                             │
┌────────────────────────────▼────────────────────────────────┐
│                  基礎設施層 (Infrastructure)                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  ├── Selenium WebDriver                               │  │
│  │  ├── MitmProxy                                        │  │
│  │  ├── Chrome Browser (Headless/GUI)                    │  │
│  │  └── ChromeDriver                                     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

### API 端點設計

#### 1. 認證與授權

```http
POST /api/auth/login
Content-Type: application/json

Request:
{
  "username": "user",
  "password": "hashed_password",
  "device_id": "android_device_123"
}

Response:
{
  "status": "success",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

#### 2. 課程管理

```http
GET /api/courses
Authorization: Bearer <token>

Response:
{
  "status": "success",
  "courses": [
    {
      "id": 1,
      "program_name": "資通安全教育訓練(114年度)",
      "lesson_name": "資通安全基礎課程",
      "course_type": "course",
      "description": "..."
    }
  ]
}
```

#### 3. 排程管理

```http
POST /api/schedule/add
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "course_ids": [1, 2, 3]
}

Response:
{
  "status": "success",
  "scheduled_count": 3
}
```

```http
GET /api/schedule
Authorization: Bearer <token>

Response:
{
  "status": "success",
  "schedule": [
    {
      "id": 1,
      "program_name": "...",
      "lesson_name": "...",
      "added_at": "2025-11-24T23:00:00Z"
    }
  ]
}
```

```http
DELETE /api/schedule/clear
Authorization: Bearer <token>

Response:
{
  "status": "success",
  "message": "Schedule cleared"
}
```

#### 4. 執行控制

```http
POST /api/execute
Authorization: Bearer <token>
Content-Type: application/json

Request:
{
  "async": true,  // 是否非同步執行
  "notify": true  // 完成後是否通知
}

Response (async=true):
{
  "status": "accepted",
  "task_id": "task_uuid_123",
  "message": "Execution started in background"
}

Response (async=false):
{
  "status": "success",
  "execution_summary": {
    "total_courses": 5,
    "completed": 5,
    "failed": 0,
    "duration": "15m 30s"
  }
}
```

#### 5. 狀態查詢

```http
GET /api/status
Authorization: Bearer <token>

Response:
{
  "status": "success",
  "server": {
    "is_running": true,
    "current_task": "course_learning",
    "progress": "3/5 courses completed"
  }
}
```

```http
GET /api/tasks/<task_id>
Authorization: Bearer <token>

Response:
{
  "status": "success",
  "task": {
    "id": "task_uuid_123",
    "state": "running",  // pending, running, completed, failed
    "progress": 60,      // 0-100
    "message": "Processing course 3/5",
    "started_at": "2025-11-24T23:00:00Z",
    "estimated_completion": "2025-11-24T23:15:00Z"
  }
}
```

#### 6. 報告與日誌

```http
GET /api/reports
Authorization: Bearer <token>

Response:
{
  "status": "success",
  "reports": [
    {
      "id": "report_001",
      "type": "time_statistics",
      "created_at": "2025-11-24T23:30:00Z",
      "download_url": "/api/reports/report_001/download"
    }
  ]
}
```

```http
GET /api/logs?lines=100
Authorization: Bearer <token>

Response:
{
  "status": "success",
  "logs": [
    "[2025-11-24 23:00:00] [INFO] Starting execution...",
    "[2025-11-24 23:01:00] [INFO] Course 1/5 completed"
  ]
}
```

---

### 資料流設計

#### 執行流程時序圖

```
Android Client          API Server              EEBot Core           Selenium
     │                      │                       │                    │
     │  POST /api/execute   │                       │                    │
     ├─────────────────────>│                       │                    │
     │                      │  create_task()        │                    │
     │                      ├──────────────────────>│                    │
     │                      │                       │  initialize()      │
     │                      │                       ├───────────────────>│
     │  HTTP 202 Accepted   │                       │                    │
     │<─────────────────────┤                       │                    │
     │                      │                       │  navigate()        │
     │                      │                       ├───────────────────>│
     │                      │                       │                    │
     │  GET /api/tasks/...  │                       │  execute_course()  │
     ├─────────────────────>│                       ├───────────────────>│
     │  Progress: 33%       │                       │                    │
     │<─────────────────────┤                       │                    │
     │                      │                       │                    │
     │       (輪詢狀態)      │                       │  complete()        │
     │         ...          │                       │<───────────────────┤
     │                      │                       │                    │
     │  GET /api/tasks/...  │                       │                    │
     ├─────────────────────>│                       │                    │
     │  Status: completed   │                       │                    │
     │<─────────────────────┤                       │                    │
     │                      │                       │                    │
```

---

### 資料持久化設計

#### 伺服器端資料結構

```
eebot_server/
├── data/
│   ├── courses.json              # 課程配置 (原有)
│   ├── schedule.json             # 排程配置 (原有)
│   ├── tasks.db                  # 任務資料庫 (新增)
│   └── users.db                  # 使用者資料庫 (新增)
│
├── reports/                      # 執行報告 (原有)
│   └── time_report_*.md
│
└── logs/                         # API 日誌 (新增)
    ├── api_access.log
    └── execution.log
```

#### SQLite 資料表設計

```sql
-- 使用者表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    device_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- 任務表
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,              -- UUID
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL,               -- 'execute', 'scan', etc.
    state TEXT NOT NULL,              -- 'pending', 'running', 'completed', 'failed'
    progress INTEGER DEFAULT 0,       -- 0-100
    message TEXT,
    result TEXT,                      -- JSON 格式的執行結果
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- API Token 表
CREATE TABLE api_tokens (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 執行歷史表
CREATE TABLE execution_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    total_courses INTEGER,
    completed_courses INTEGER,
    failed_courses INTEGER,
    duration_seconds INTEGER,
    report_path TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
```

---

## 📅 實施計畫

### 階段規劃概覽

| 階段 | 任務 | 時間 | 優先級 | 依賴 |
|------|------|------|--------|------|
| **Phase 0** | 環境準備與設計確認 | 2-3h | P0 | - |
| **Phase 1** | API Server 開發 | 8-12h | P0 | Phase 0 |
| **Phase 2** | Android Client 開發 | 6-10h | P0 | Phase 1 |
| **Phase 3** | 整合測試 | 2-4h | P0 | Phase 2 |
| **Phase 4** | Docker 化部署 | 4-6h | P1 | Phase 3 |
| **Phase 5** | 文檔與交付 | 2-3h | P1 | Phase 4 |

**總計**: 24-38 小時（保守估計 **28 小時**）

---

### Phase 0: 環境準備與設計確認 (2-3h)

#### 目標
- ✅ 確認技術棧
- ✅ 設定開發環境
- ✅ API 設計評審

#### 任務清單

**Task 0.1: 技術棧確認** (30 min)
```bash
# 確認所需套件版本
pip list | grep -E "flask|flask-restful|flask-jwt-extended|pyjwt"

# 若未安裝，安裝依賴
pip install flask flask-restful flask-jwt-extended flask-cors
```

**Task 0.2: 目錄結構規劃** (30 min)
```
eebot/
├── api_server/                    # 新增目錄
│   ├── __init__.py
│   ├── app.py                     # Flask 應用主程式
│   ├── routes/                    # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py                # 認證相關
│   │   ├── courses.py             # 課程管理
│   │   ├── schedule.py            # 排程管理
│   │   ├── execute.py             # 執行控制
│   │   └── status.py              # 狀態查詢
│   ├── middleware/                # 中介層
│   │   ├── __init__.py
│   │   ├── auth.py                # JWT 驗證
│   │   └── error_handler.py       # 錯誤處理
│   ├── models/                    # 資料模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── task.py
│   └── utils/                     # 工具函數
│       ├── __init__.py
│       ├── db.py                  # 資料庫工具
│       └── jwt_utils.py           # JWT 工具
│
├── android_client/                # 新增目錄
│   ├── menu_android.py            # Android 版選單
│   ├── api_client.py              # API 客戶端
│   └── config_android.py          # Android 配置
│
├── docker/                        # 新增目錄
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf                 # (可選) Nginx 反向代理
│
└── (原有目錄結構保持不變)
```

**Task 0.3: API 設計文檔** (1h)
- 編寫 OpenAPI/Swagger 規格
- 定義所有端點的 Request/Response 格式
- 確定錯誤代碼規範

**Task 0.4: 資料庫設計** (30 min)
- 設計 SQLite Schema
- 編寫初始化腳本
- 規劃資料遷移策略

---

### Phase 1: API Server 開發 (8-12h)

#### 目標
- ✅ 實現所有 RESTful API 端點
- ✅ 整合原有 EEBot 核心
- ✅ 完成單元測試

#### 任務清單

**Task 1.1: Flask 應用骨架** (1-2h)

```python
# api_server/app.py
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)

    # 配置
    app.config['SECRET_KEY'] = 'your-secret-key'  # 應從環境變數讀取
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'

    # 啟用 CORS
    CORS(app)

    # 初始化 JWT
    jwt = JWTManager(app)

    # 註冊路由
    from .routes import auth, courses, schedule, execute, status
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(courses.bp, url_prefix='/api/courses')
    app.register_blueprint(schedule.bp, url_prefix='/api/schedule')
    app.register_blueprint(execute.bp, url_prefix='/api')
    app.register_blueprint(status.bp, url_prefix='/api')

    # 錯誤處理
    from .middleware.error_handler import register_error_handlers
    register_error_handlers(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Task 1.2: 認證系統** (2-3h)

```python
# api_server/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from ..models.user import User

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    """使用者登入"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 驗證使用者
    user = User.authenticate(username, password)
    if not user:
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

    # 生成 JWT Token
    access_token = create_access_token(identity=user.id)

    return jsonify({
        'status': 'success',
        'token': access_token,
        'user': user.to_dict()
    })

@bp.route('/register', methods=['POST'])
def register():
    """註冊新使用者"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 建立使用者
    try:
        user = User.create(username, password)
        return jsonify({
            'status': 'success',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
```

**Task 1.3: 課程管理 API** (1-2h)

```python
# api_server/routes/courses.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
import json

bp = Blueprint('courses', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
def get_courses():
    """取得所有課程列表"""
    # 讀取 data/courses.json (原有檔案)
    with open('data/courses.json', 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
        courses = data.get('courses', [])

    return jsonify({
        'status': 'success',
        'courses': courses,
        'total': len(courses)
    })

@bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    """取得單一課程詳情"""
    with open('data/courses.json', 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
        courses = data.get('courses', [])

    # 找到對應課程（假設 courses 是列表，使用索引）
    if course_id < len(courses):
        return jsonify({
            'status': 'success',
            'course': courses[course_id]
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Course not found'
        }), 404
```

**Task 1.4: 排程管理 API** (1-2h)

```python
# api_server/routes/schedule.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import json

bp = Blueprint('schedule', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
def get_schedule():
    """取得目前排程"""
    try:
        with open('data/schedule.json', 'r', encoding='utf-8-sig') as f:
            schedule = json.load(f)
        return jsonify({
            'status': 'success',
            'schedule': schedule
        })
    except FileNotFoundError:
        return jsonify({
            'status': 'success',
            'schedule': []
        })

@bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_schedule():
    """新增課程到排程"""
    data = request.get_json()
    course_ids = data.get('course_ids', [])

    # 讀取課程資料
    with open('data/courses.json', 'r', encoding='utf-8-sig') as f:
        courses_data = json.load(f)
        all_courses = courses_data.get('courses', [])

    # 讀取現有排程
    try:
        with open('data/schedule.json', 'r', encoding='utf-8-sig') as f:
            schedule = json.load(f)
    except FileNotFoundError:
        schedule = []

    # 新增課程到排程
    for course_id in course_ids:
        if course_id < len(all_courses):
            schedule.append(all_courses[course_id])

    # 儲存排程
    with open('data/schedule.json', 'w', encoding='utf-8') as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)

    return jsonify({
        'status': 'success',
        'scheduled_count': len(course_ids),
        'total_in_schedule': len(schedule)
    })

@bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_schedule():
    """清空排程"""
    with open('data/schedule.json', 'w', encoding='utf-8') as f:
        json.dump([], f)

    return jsonify({
        'status': 'success',
        'message': 'Schedule cleared'
    })
```

**Task 1.5: 執行控制 API (非同步)** (3-4h)

```python
# api_server/routes/execute.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
import threading
from ..models.task import Task
from main import main as execute_main  # 導入原有主程式

bp = Blueprint('execute', __name__)

def execute_in_background(task_id, user_id):
    """背景執行任務"""
    task = Task.get(task_id)
    task.update_state('running', progress=0, message='Initializing...')

    try:
        # 執行原有主程式
        # 這裡需要修改 main.py 使其能接受回調函數來更新進度
        execute_main()

        # 執行成功
        task.update_state('completed', progress=100, message='Execution completed')
    except Exception as e:
        # 執行失敗
        task.update_state('failed', progress=0, message=str(e))

@bp.route('/execute', methods=['POST'])
@jwt_required()
def execute():
    """執行排程 (非同步)"""
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    async_mode = data.get('async', True)

    # 建立任務
    task_id = str(uuid.uuid4())
    task = Task.create(task_id, user_id, 'execute')

    if async_mode:
        # 非同步執行
        thread = threading.Thread(
            target=execute_in_background,
            args=(task_id, user_id)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            'status': 'accepted',
            'task_id': task_id,
            'message': 'Execution started in background'
        }), 202
    else:
        # 同步執行
        execute_in_background(task_id, user_id)
        task = Task.get(task_id)

        return jsonify({
            'status': 'success',
            'task': task.to_dict()
        })

@bp.route('/tasks/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """查詢任務狀態"""
    task = Task.get(task_id)

    if not task:
        return jsonify({
            'status': 'error',
            'message': 'Task not found'
        }), 404

    return jsonify({
        'status': 'success',
        'task': task.to_dict()
    })
```

**Task 1.6: 狀態查詢 API** (1h)

```python
# api_server/routes/status.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

bp = Blueprint('status', __name__)

@bp.route('/status', methods=['GET'])
@jwt_required()
def get_status():
    """取得伺服器狀態"""
    # TODO: 實現狀態追蹤邏輯
    return jsonify({
        'status': 'success',
        'server': {
            'is_running': True,
            'version': '2.0.5',
            'uptime': '24h 30m'
        }
    })
```

**Task 1.7: 單元測試** (1-2h)

```python
# tests/test_api.py
import unittest
from api_server.app import create_app

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_login(self):
        response = self.client.post('/api/auth/login', json={
            'username': 'test',
            'password': 'test'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('token', data)

    def test_get_courses(self):
        # 先登入取得 token
        login_response = self.client.post('/api/auth/login', json={
            'username': 'test',
            'password': 'test'
        })
        token = login_response.get_json()['token']

        # 取得課程列表
        response = self.client.get('/api/courses',
                                     headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('courses', data)

if __name__ == '__main__':
    unittest.main()
```

---

### Phase 2: Android Client 開發 (6-10h)

#### 目標
- ✅ 實現 Android 端選單介面
- ✅ 完成 API 客戶端
- ✅ 處理認證與 Token 管理

#### 任務清單

**Task 2.1: API 客戶端基礎** (2-3h)

```python
# android_client/api_client.py
import requests
import json
from typing import Optional, Dict, List

class EEBotAPIClient:
    """EEBot API 客戶端"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        """建立請求標頭"""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def login(self, username: str, password: str) -> bool:
        """登入"""
        try:
            response = self.session.post(
                f'{self.base_url}/api/auth/login',
                json={'username': username, 'password': password}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                return True
            return False
        except Exception as e:
            print(f'Login error: {e}')
            return False

    def get_courses(self) -> List[Dict]:
        """取得課程列表"""
        try:
            response = self.session.get(
                f'{self.base_url}/api/courses',
                headers=self._headers()
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('courses', [])
            return []
        except Exception as e:
            print(f'Get courses error: {e}')
            return []

    def get_schedule(self) -> List[Dict]:
        """取得排程"""
        try:
            response = self.session.get(
                f'{self.base_url}/api/schedule',
                headers=self._headers()
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('schedule', [])
            return []
        except Exception as e:
            print(f'Get schedule error: {e}')
            return []

    def add_to_schedule(self, course_ids: List[int]) -> bool:
        """新增課程到排程"""
        try:
            response = self.session.post(
                f'{self.base_url}/api/schedule/add',
                json={'course_ids': course_ids},
                headers=self._headers()
            )
            return response.status_code == 200
        except Exception as e:
            print(f'Add to schedule error: {e}')
            return False

    def clear_schedule(self) -> bool:
        """清空排程"""
        try:
            response = self.session.delete(
                f'{self.base_url}/api/schedule/clear',
                headers=self._headers()
            )
            return response.status_code == 200
        except Exception as e:
            print(f'Clear schedule error: {e}')
            return False

    def execute(self, async_mode: bool = True) -> Optional[str]:
        """執行排程"""
        try:
            response = self.session.post(
                f'{self.base_url}/api/execute',
                json={'async': async_mode},
                headers=self._headers()
            )
            if response.status_code in (200, 202):
                data = response.json()
                return data.get('task_id')
            return None
        except Exception as e:
            print(f'Execute error: {e}')
            return None

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """查詢任務狀態"""
        try:
            response = self.session.get(
                f'{self.base_url}/api/tasks/{task_id}',
                headers=self._headers()
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('task')
            return None
        except Exception as e:
            print(f'Get task status error: {e}')
            return None
```

**Task 2.2: Android 配置管理** (1h)

```python
# android_client/config_android.py
import json
import os

class AndroidConfig:
    """Android 端配置管理"""

    CONFIG_FILE = os.path.expanduser('~/.eebot_android.json')

    def __init__(self):
        self.config = self.load()

    def load(self) -> dict:
        """載入配置"""
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.default_config()

    def save(self):
        """儲存配置"""
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)

    def default_config(self) -> dict:
        """預設配置"""
        return {
            'server_url': 'http://localhost:5000',
            'username': '',
            'remember_credentials': False
        }

    def get(self, key: str, default=None):
        """取得配置值"""
        return self.config.get(key, default)

    def set(self, key: str, value):
        """設定配置值"""
        self.config[key] = value
        self.save()
```

**Task 2.3: Android 選單介面** (3-5h)

```python
# android_client/menu_android.py
import sys
import time
from api_client import EEBotAPIClient
from config_android import AndroidConfig

class AndroidMenu:
    """Android 版選單"""

    def __init__(self):
        self.config = AndroidConfig()
        self.client = None
        self.is_logged_in = False

    def clear_screen(self):
        """清除螢幕 (Android Termux)"""
        print('\033[2J\033[H', end='')

    def print_header(self):
        """顯示標題"""
        print('=' * 50)
        print('  EEBot (Gleipnir) - Android Remote Control')
        print('  專案版本: 2.0.5')
        print('=' * 50)
        print()

    def login(self):
        """登入"""
        server_url = self.config.get('server_url')
        print(f'伺服器位址: {server_url}')
        print()

        username = input('使用者名稱: ').strip()
        import getpass
        password = getpass.getpass('密碼: ')

        print('\n正在登入...')
        self.client = EEBotAPIClient(server_url)

        if self.client.login(username, password):
            print('✅ 登入成功!')
            self.is_logged_in = True

            # 詢問是否記住設定
            remember = input('記住伺服器位址? (y/n): ').strip().lower()
            if remember == 'y':
                self.config.set('server_url', server_url)
                self.config.set('username', username)

            time.sleep(1)
            return True
        else:
            print('❌ 登入失敗，請檢查帳號密碼')
            time.sleep(2)
            return False

    def display_menu(self):
        """顯示主選單"""
        self.clear_screen()
        self.print_header()

        print('【主選單】')
        print('  1. 檢視課程列表')
        print('  2. 檢視目前排程')
        print('  3. 新增課程到排程')
        print('  4. 清空排程')
        print('  5. 執行排程')
        print('  6. 查詢執行狀態')
        print('  s. 伺服器設定')
        print('  q. 登出')
        print()

    def view_courses(self):
        """檢視課程列表"""
        print('\n正在取得課程列表...')
        courses = self.client.get_courses()

        if not courses:
            print('❌ 無課程資料')
            return

        print(f'\n【課程列表】(共 {len(courses)} 個)')
        print('-' * 80)

        for i, course in enumerate(courses):
            course_type = course.get('course_type', 'course')
            type_label = '[考試]' if course_type == 'exam' else '[課程]'

            print(f'{i+1:3d}. {type_label} {course.get("program_name")}')
            print(f'       └─ {course.get("lesson_name", course.get("exam_name"))}')
            print(f'       └─ {course.get("description", "")[:60]}')
            print()

        input('\n按 Enter 繼續...')

    def view_schedule(self):
        """檢視目前排程"""
        print('\n正在取得排程...')
        schedule = self.client.get_schedule()

        if not schedule:
            print('📋 排程目前是空的')
        else:
            print(f'\n【目前排程】(共 {len(schedule)} 個)')
            print('-' * 80)

            for i, item in enumerate(schedule):
                course_type = item.get('course_type', 'course')
                type_label = '[考試]' if course_type == 'exam' else '[課程]'

                print(f'{i+1:3d}. {type_label} {item.get("program_name")}')
                print(f'       └─ {item.get("lesson_name", item.get("exam_name"))}')
                print()

        input('\n按 Enter 繼續...')

    def add_to_schedule(self):
        """新增課程到排程"""
        # 顯示課程列表
        courses = self.client.get_courses()

        if not courses:
            print('❌ 無課程資料')
            input('按 Enter 繼續...')
            return

        print(f'\n【課程列表】(共 {len(courses)} 個)')
        for i, course in enumerate(courses):
            course_type = course.get('course_type', 'course')
            type_label = '[考試]' if course_type == 'exam' else '[課程]'
            print(f'{i+1:3d}. {type_label} {course.get("lesson_name", course.get("exam_name"))}')

        print()
        user_input = input('請輸入課程編號 (多個用逗號分隔, 0 取消): ').strip()

        if user_input == '0':
            return

        try:
            # 解析輸入
            course_ids = [int(x.strip()) - 1 for x in user_input.split(',')]

            # 驗證範圍
            valid_ids = [cid for cid in course_ids if 0 <= cid < len(courses)]

            if not valid_ids:
                print('❌ 無有效的課程編號')
                input('按 Enter 繼續...')
                return

            # 新增到排程
            print(f'\n正在新增 {len(valid_ids)} 個課程到排程...')
            if self.client.add_to_schedule(valid_ids):
                print(f'✅ 成功新增 {len(valid_ids)} 個課程')
            else:
                print('❌ 新增失敗')

            time.sleep(1)

        except ValueError:
            print('❌ 輸入格式錯誤')
            input('按 Enter 繼續...')

    def clear_schedule(self):
        """清空排程"""
        confirm = input('\n⚠️  確定要清空排程? (y/n): ').strip().lower()

        if confirm == 'y':
            print('正在清空排程...')
            if self.client.clear_schedule():
                print('✅ 排程已清空')
            else:
                print('❌ 清空失敗')
            time.sleep(1)

    def execute_schedule(self):
        """執行排程"""
        print('\n準備執行排程...')

        # 確認排程不是空的
        schedule = self.client.get_schedule()
        if not schedule:
            print('❌ 排程是空的，無法執行')
            input('按 Enter 繼續...')
            return

        print(f'排程中有 {len(schedule)} 個項目')
        confirm = input('確定要執行? (y/n): ').strip().lower()

        if confirm != 'y':
            return

        print('\n正在啟動執行...')
        task_id = self.client.execute(async_mode=True)

        if task_id:
            print(f'✅ 執行已啟動 (Task ID: {task_id})')
            print('使用選項 6 查詢執行狀態')

            # 詢問是否監控
            monitor = input('是否持續監控執行狀態? (y/n): ').strip().lower()

            if monitor == 'y':
                self.monitor_task(task_id)
        else:
            print('❌ 執行失敗')

        input('\n按 Enter 繼續...')

    def monitor_task(self, task_id: str):
        """監控任務執行"""
        print(f'\n【監控任務】Task ID: {task_id}')
        print('(按 Ctrl+C 停止監控)\n')

        try:
            while True:
                task = self.client.get_task_status(task_id)

                if not task:
                    print('❌ 無法取得任務狀態')
                    break

                state = task.get('state')
                progress = task.get('progress', 0)
                message = task.get('message', '')

                # 顯示進度
                bar_length = 30
                filled = int(bar_length * progress / 100)
                bar = '█' * filled + '░' * (bar_length - filled)

                print(f'\r狀態: {state:10s} [{bar}] {progress:3d}% - {message}', end='', flush=True)

                # 檢查是否完成
                if state in ('completed', 'failed'):
                    print()
                    if state == 'completed':
                        print('\n✅ 執行完成!')
                    else:
                        print('\n❌ 執行失敗!')
                    break

                time.sleep(2)  # 每 2 秒查詢一次

        except KeyboardInterrupt:
            print('\n\n監控已停止')

    def query_status(self):
        """查詢執行狀態"""
        task_id = input('\n請輸入 Task ID: ').strip()

        if not task_id:
            return

        print('\n正在查詢...')
        task = self.client.get_task_status(task_id)

        if task:
            print(f'\n【任務狀態】')
            print(f'  ID: {task.get("id")}')
            print(f'  狀態: {task.get("state")}')
            print(f'  進度: {task.get("progress")}%')
            print(f'  訊息: {task.get("message")}')
            print(f'  開始時間: {task.get("started_at")}')
        else:
            print('❌ 找不到該任務')

        input('\n按 Enter 繼續...')

    def server_settings(self):
        """伺服器設定"""
        print('\n【伺服器設定】')
        print(f'目前伺服器: {self.config.get("server_url")}')
        print()

        new_url = input('新的伺服器位址 (留空保持不變): ').strip()

        if new_url:
            self.config.set('server_url', new_url)
            print('✅ 伺服器位址已更新')
            print('請重新登入')
            self.is_logged_in = False
            time.sleep(1)

    def run(self):
        """主程式"""
        # 登入
        if not self.login():
            print('無法登入，程式結束')
            return

        # 主選單循環
        while self.is_logged_in:
            self.display_menu()
            choice = input('請選擇: ').strip().lower()

            if choice == '1':
                self.view_courses()
            elif choice == '2':
                self.view_schedule()
            elif choice == '3':
                self.add_to_schedule()
            elif choice == '4':
                self.clear_schedule()
            elif choice == '5':
                self.execute_schedule()
            elif choice == '6':
                self.query_status()
            elif choice == 's':
                self.server_settings()
            elif choice == 'q':
                print('\n登出中...')
                self.is_logged_in = False
                time.sleep(1)
            else:
                print('❌ 無效的選項')
                time.sleep(1)

        print('Goodbye!')

if __name__ == '__main__':
    menu = AndroidMenu()
    menu.run()
```

**Task 2.4: Android 端測試** (1-2h)
- 在 Termux 中測試所有功能
- 驗證 API 連接
- 測試錯誤處理

---

### Phase 3: 整合測試 (2-4h)

#### 目標
- ✅ 端到端測試
- ✅ 效能測試
- ✅ 錯誤場景測試

#### 任務清單

**Task 3.1: 功能測試** (1-2h)
- 測試完整工作流程 (登入 → 新增排程 → 執行 → 查詢)
- 驗證所有 API 端點
- 測試非同步執行

**Task 3.2: 錯誤處理測試** (1h)
- 測試網路中斷場景
- 測試認證失效場景
- 測試伺服器錯誤場景

**Task 3.3: 效能測試** (1h)
- 測試 API 回應時間
- 測試並發請求處理
- 測試大量課程載入

---

### Phase 4: Docker 化部署 (4-6h)

#### 目標
- ✅ 建立 Docker 映像
- ✅ Docker Compose 配置
- ✅ 部署文檔

#### 任務清單

**Task 4.1: Dockerfile 編寫** (2-3h)

```dockerfile
# docker/Dockerfile
FROM python:3.11-slim

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 安裝 ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1) \
    && wget -q "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}" -O /tmp/version \
    && DRIVER_VERSION=$(cat /tmp/version) \
    && wget -q "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm chromedriver_linux64.zip \
    && chmod +x /usr/local/bin/chromedriver

# 設定工作目錄
WORKDIR /app

# 複製依賴檔案
COPY requirements.txt .
COPY api_server/requirements_api.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements_api.txt

# 複製專案檔案
COPY . .

# 建立必要目錄
RUN mkdir -p data reports logs screenshots

# 暴露 API 端口
EXPOSE 5000

# 啟動 API Server
CMD ["python", "-m", "api_server.app"]
```

**Task 4.2: Docker Compose 配置** (1-2h)

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  eebot-api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: eebot-api-server
    ports:
      - "5000:5000"
    volumes:
      # 持久化資料
      - ../data:/app/data
      - ../reports:/app/reports
      - ../logs:/app/logs
      - ../screenshots:/app/screenshots
      # 配置檔案
      - ../config:/app/config:ro
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY:-change-me-in-production}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-jwt-change-me}
    restart: unless-stopped
    networks:
      - eebot-network

  # (可選) Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: eebot-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - eebot-api
    restart: unless-stopped
    networks:
      - eebot-network

networks:
  eebot-network:
    driver: bridge
```

**Task 4.3: 部署文檔編寫** (1h)

編寫詳細的部署指南，包括：
- Docker 安裝步驟
- 環境變數配置
- SSL 憑證設定
- 備份與復原

---

### Phase 5: 文檔與交付 (2-3h)

#### 任務清單

**Task 5.1: API 文檔** (1h)
- 使用 Swagger/OpenAPI 生成互動式文檔
- 編寫 API 使用範例

**Task 5.2: 使用者手冊** (1h)
- Android 端安裝指南
- 伺服器端部署指南
- 常見問題解答

**Task 5.3: 開發文檔** (30 min)
- 架構說明
- 擴展指南
- 貢獻指南

---


---

**本段結束**

📍 繼續閱讀: [ANDROID_HYBRID_ARCHITECTURE_EVALUATION-2.md](./ANDROID_HYBRID_ARCHITECTURE_EVALUATION-2.md)
