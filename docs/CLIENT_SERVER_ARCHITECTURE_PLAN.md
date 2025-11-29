# EEBot Client-Server 架構規劃

**專案代號**: Gleipnir (格萊普尼爾)
**文檔版本**: 1.0
**建立日期**: 2025-11-27
**規劃者**: wizard03 (with Claude Code CLI - Sonnet 4.5)
**狀態**: 📋 規劃階段

---

## 📋 目錄

- [執行摘要](#執行摘要)
- [背景與動機](#背景與動機)
- [架構設計](#架構設計)
- [技術選型](#技術選型)
- [API 設計](#api-設計)
- [實施計畫](#實施計畫)
- [成本效益分析](#成本效益分析)
- [風險評估](#風險評估)
- [參考文檔](#參考文檔)

---

## 📊 執行摘要

### 核心問題

EEBot 目前是基於 Python 的單體桌面應用，需要支援多平台（Windows/macOS/Linux/Android/iOS/Web）。

**挑戰**:
- Selenium WebDriver 在移動平台沒有官方支援
- MitmProxy 在 Android/iOS 需要 Root 權限
- 每個平台需要重寫 60-80% 的代碼
- 維護成本極高（5 個獨立代碼庫）

### 推薦方案

**Client-Server 架構（混合架構）**

```
輕量級 Client (多平台)
        ↓ API
Server 端 (Python + Selenium + MitmProxy)
```

### 核心優勢

- ✅ 核心代碼 100% 重用
- ✅ 開發成本節省 50-60%
- ✅ 維護成本節省 80%
- ✅ 部署靈活（本地/雲端）
- ✅ 用戶體驗優秀（原生 GUI）

---

## 🎯 背景與動機

### 當前架構

**單體桌面應用**:
```
EEBot (Python)
├── menu.py (CLI Interface)
├── Selenium WebDriver
├── MitmProxy
└── Core Business Logic (src/)
```

**限制**:
1. ❌ CLI 介面體驗差
2. ❌ 僅支援 Windows/macOS/Linux
3. ❌ 無法在移動平台運行（Selenium/MitmProxy 限制）
4. ❌ GUI 開發困難（PyQt 體驗差）
5. ❌ 多平台維護成本極高

### 多平台需求

**目標平台**:
- Windows Desktop
- macOS Desktop
- Linux Desktop
- Android Mobile
- iOS Mobile
- Web Browser (可選)

**用戶期望**:
- 現代化的圖形介面
- 隨時隨地控制執行
- 即時查看執行狀態
- 截圖查看功能
- 跨設備同步

---

## 🏗️ 架構設計

### 系統架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                    Client 端（控制端）                        │
│  ┌────────────┬────────────┬────────────┬────────────┐      │
│  │  Windows   │   macOS    │   Linux    │    Web     │      │
│  │  (Electron)│ (Electron) │ (Electron) │  (React)   │      │
│  └────────────┴────────────┴────────────┴────────────┘      │
│  ┌────────────┬────────────┐                                │
│  │  Android   │    iOS     │                                │
│  │  (Kotlin)  │  (Swift)   │                                │
│  └────────────┴────────────┘                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ RESTful API (HTTPS/JSON)
                       │ WebSocket (Real-time)
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  Server 端（執行端）                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Flask/FastAPI RESTful API Server                    │  │
│  │  ├── Authentication Layer (JWT)                      │  │
│  │  ├── Route Handlers                                  │  │
│  │  ├── WebSocket Manager                               │  │
│  │  └── Error Handling                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  EEBot Core (100% 原有代碼，無需修改)                 │  │
│  │  ├── src/scenarios/* (課程學習、考試自動答題)         │  │
│  │  ├── src/pages/* (POM 頁面物件)                      │  │
│  │  ├── src/services/* (服務層)                         │  │
│  │  └── src/core/* (核心管理器)                         │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Infrastructure Layer                                 │  │
│  │  ├── Selenium WebDriver (Headless 模式)              │  │
│  │  ├── MitmProxy (Silent 模式)                         │  │
│  │  ├── Chrome Browser                                  │  │
│  │  └── ChromeDriver                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 職責劃分

#### Client 端

**職責**:
- 用戶介面（UI/UX）
- 用戶輸入處理
- API 請求發送
- 即時狀態顯示（WebSocket）
- 本地狀態管理

**不負責**:
- 業務邏輯
- 瀏覽器自動化
- 網路代理
- 數據持久化

#### Server 端

**職責**:
- 業務邏輯執行
- 瀏覽器自動化（Selenium）
- 網路代理（MitmProxy）
- 狀態管理
- 截圖生成
- 執行日誌

**不負責**:
- UI 渲染
- 用戶輸入處理

---

## 🔧 技術選型

### Server 端

#### API Framework

**推薦：FastAPI** ⭐

**理由**:
- ✅ 現代化、高效能
- ✅ 自動生成 API 文檔（Swagger/OpenAPI）
- ✅ 內建異步支援
- ✅ WebSocket 支援
- ✅ 類型檢查（Pydantic）
- ✅ 與 Python 生態完美整合

**替代方案：Flask**
- 輕量級
- 簡單易學
- 生態成熟

**技術棧**:
```python
# API Framework
FastAPI 0.104+

# ASGI Server
Uvicorn + Gunicorn

# 認證
python-jose (JWT)
passlib (密碼加密)

# WebSocket
websockets

# 數據庫（可選）
SQLite (輕量) 或 PostgreSQL (生產)

# ORM（可選）
SQLAlchemy

# 部署
Docker + Nginx
```

#### 核心邏輯

**保留 100%**:
```python
# 現有 EEBot 代碼完全不需修改
src/scenarios/course_learning.py
src/scenarios/exam_learning.py
src/scenarios/exam_auto_answer.py
src/pages/*.py
src/services/*.py
src/core/*.py
```

**包裝方式**:
```python
# server/api/routes/courses.py
from src.scenarios.course_learning import start_course_learning

@app.post("/api/courses/start")
async def start_course(course_id: str):
    # 包裝現有函數
    result = await run_in_executor(start_course_learning, course_id)
    return {"status": "success", "data": result}
```

---

### Client 端

#### 桌面平台（Windows/macOS/Linux）

**推薦：Electron** ⭐⭐⭐⭐⭐

**理由**:
- ✅ 一套代碼，三個平台
- ✅ 現代化 UI 框架（React/Vue）
- ✅ 豐富的生態系統
- ✅ 自動更新支援
- ✅ 可直接轉成 Web 版（代碼共用 90%）
- ✅ 成功案例：VS Code, Discord, Slack, Figma

**技術棧**:
```javascript
// Framework
Electron 28+

// UI Framework
React 18+ + TypeScript

// UI Library
Material-UI 或 Ant Design

// 狀態管理
Redux Toolkit 或 Zustand

// HTTP Client
Axios

// WebSocket Client
Socket.io-client
```

**替代方案：PyQt6**
- 原生感較強
- 與 Python 整合容易
- 但 UI 開發較繁瑣，不適合 Web 化

---

#### 移動平台

**Android**

**技術棧**:
```kotlin
// 語言
Kotlin 1.9+

// UI Framework
Jetpack Compose (現代化聲明式 UI)

// 架構
MVVM + Clean Architecture

// 網路
Retrofit 2.9+ (HTTP)
OkHttp 4.12+ (WebSocket)

// 異步
Coroutines + Flow

// 依賴注入
Hilt
```

**iOS**

**技術棧**:
```swift
// 語言
Swift 5.9+

// UI Framework
SwiftUI (現代化聲明式 UI)

// 架構
MVVM + Combine

// 網路
URLSession (HTTP/WebSocket)
或 Alamofire

// 異步
async/await
```

---

#### Web 平台（可選）

**技術棧**:
```javascript
// Framework
React 18+ + TypeScript

// UI Library
Material-UI 或 Ant Design

// 狀態管理
Redux Toolkit

// HTTP Client
Axios

// WebSocket
Socket.io-client

// 建置工具
Vite 或 Create React App
```

**優勢**:
- 與 Electron 版本共用 90% 代碼
- 無需安裝，瀏覽器直接訪問
- 更新即時生效

---

## 📡 API 設計

### RESTful API 端點

#### 1. 認證與授權

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}

Response 200:
{
  "token": "jwt_token",
  "user": {
    "id": "string",
    "username": "string"
  }
}
```

```http
POST /api/auth/logout
Authorization: Bearer {token}

Response 200:
{
  "message": "Logged out successfully"
}
```

---

#### 2. 課程管理

**獲取課程清單**
```http
GET /api/courses
Authorization: Bearer {token}

Response 200:
{
  "courses": [
    {
      "id": "string",
      "name": "string",
      "status": "pending|in_progress|completed",
      "progress": 0-100
    }
  ]
}
```

**開始課程**
```http
POST /api/courses/start
Authorization: Bearer {token}
Content-Type: application/json

{
  "course_id": "string",
  "mode": "auto|manual",
  "enable_screenshot": boolean
}

Response 200:
{
  "task_id": "string",
  "status": "started",
  "message": "Course learning started"
}
```

**停止課程**
```http
POST /api/courses/stop
Authorization: Bearer {token}
Content-Type: application/json

{
  "task_id": "string"
}

Response 200:
{
  "status": "stopped",
  "message": "Course learning stopped"
}
```

---

#### 3. 執行狀態

**查詢任務狀態**
```http
GET /api/tasks/{task_id}/status
Authorization: Bearer {token}

Response 200:
{
  "task_id": "string",
  "status": "pending|running|completed|failed",
  "progress": 0-100,
  "current_step": "string",
  "logs": ["string"],
  "started_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

---

#### 4. 截圖管理

**獲取截圖清單**
```http
GET /api/screenshots
Authorization: Bearer {token}
Query: ?date=2025-11-27&course_id=xxx

Response 200:
{
  "screenshots": [
    {
      "id": "string",
      "course_name": "string",
      "timestamp": "ISO8601",
      "url": "/api/screenshots/{id}"
    }
  ]
}
```

**下載截圖**
```http
GET /api/screenshots/{id}
Authorization: Bearer {token}

Response 200:
Content-Type: image/png
[Binary Data]
```

---

#### 5. 配置管理

**獲取配置**
```http
GET /api/config
Authorization: Bearer {token}

Response 200:
{
  "headless_mode": boolean,
  "auto_answer_enabled": boolean,
  "screenshot_enabled": boolean,
  ...
}
```

**更新配置**
```http
PUT /api/config
Authorization: Bearer {token}
Content-Type: application/json

{
  "headless_mode": true,
  "auto_answer_enabled": true
}

Response 200:
{
  "message": "Configuration updated"
}
```

---

### WebSocket 即時通訊

**連接**
```javascript
// Client 端
const ws = new WebSocket('ws://server:8000/ws?token=jwt_token');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

**訊息格式**
```json
{
  "type": "task_update",
  "task_id": "string",
  "status": "running",
  "progress": 45,
  "message": "Processing lesson 3/7",
  "timestamp": "ISO8601"
}
```

**訊息類型**:
- `task_update`: 任務狀態更新
- `log`: 執行日誌
- `screenshot`: 新截圖通知
- `error`: 錯誤通知
- `completed`: 任務完成

---

## 📅 實施計畫

### Phase 1: Server 端 API 開發（2-3 週）

**Week 1**:
- ✅ FastAPI 專案初始化
- ✅ 設計 API 端點規格
- ✅ 實作認證系統（JWT）
- ✅ 包裝現有核心邏輯為 API

**Week 2**:
- ✅ 實作課程管理 API
- ✅ 實作執行控制 API
- ✅ 實作狀態查詢 API
- ✅ WebSocket 即時通訊

**Week 3**:
- ✅ 截圖管理 API
- ✅ 配置管理 API
- ✅ Docker 容器化
- ✅ 測試與文檔（Swagger）

**交付物**:
- Server API 完整實作
- API 文檔（Swagger UI）
- Docker 映像檔
- 部署腳本

---

### Phase 2: 桌面 Client 開發（2-3 週）

**Week 4**:
- ✅ Electron + React 專案初始化
- ✅ 基礎 UI 框架搭建
- ✅ API Client 開發（Axios）
- ✅ WebSocket Client 整合

**Week 5**:
- ✅ 登入介面
- ✅ 課程清單介面
- ✅ 控制面板（開始/停止）
- ✅ 即時狀態顯示

**Week 6**:
- ✅ 截圖查看功能
- ✅ 配置管理介面
- ✅ 執行日誌顯示
- ✅ 打包與安裝程式（Windows/macOS/Linux）

**交付物**:
- 桌面應用程式（三平台）
- 安裝程式（.exe, .dmg, .AppImage）
- 用戶手冊

---

### Phase 3: Android Client 開發（2-3 週）

**Week 7**:
- ✅ Android 專案初始化（Kotlin + Compose）
- ✅ API Client（Retrofit）
- ✅ 登入功能

**Week 8**:
- ✅ 課程清單 UI
- ✅ 控制功能
- ✅ 即時狀態更新（WebSocket）

**Week 9**:
- ✅ 截圖查看
- ✅ 通知功能
- ✅ 測試與優化
- ✅ 發布到 Google Play（可選）

**交付物**:
- Android APK
- 用戶手冊

---

### Phase 4: iOS Client 開發（2-3 週）

**Week 10**:
- ✅ iOS 專案初始化（Swift + SwiftUI）
- ✅ API Client
- ✅ 登入功能

**Week 11**:
- ✅ 課程清單 UI
- ✅ 控制功能
- ✅ 即時狀態更新

**Week 12**:
- ✅ 截圖查看
- ✅ 通知功能
- ✅ 測試與優化
- ✅ 發布到 App Store（可選）

**交付物**:
- iOS IPA
- 用戶手冊

---

### Phase 5: Web Client 開發（1-2 週，可選）

**Week 13-14**:
- ✅ 從 Electron 版本提取共用代碼
- ✅ 調整為純 Web 版本（去除 Electron API）
- ✅ 響應式設計優化
- ✅ 部署到雲端（Vercel/Netlify）

**交付物**:
- Web 應用
- 部署文檔

---

### 總時程

| Phase | 內容 | 時間 | 優先級 |
|-------|------|------|--------|
| Phase 1 | Server API | 2-3 週 | 🔥 最高 |
| Phase 2 | 桌面 Client | 2-3 週 | 🔥 高 |
| Phase 3 | Android Client | 2-3 週 | ⚠️ 中 |
| Phase 4 | iOS Client | 2-3 週 | ⚠️ 中 |
| Phase 5 | Web Client | 1-2 週 | 💡 低（可選）|

**總計**：9-14 週（~2-3.5 個月）

---

## 💰 成本效益分析

### 開發成本比較

| 架構模式 | Windows GUI | macOS GUI | Linux GUI | Android | iOS | 總計 |
|---------|------------|----------|----------|---------|-----|------|
| **單體架構** | 2-3 週 | 2-3 週 | 2-3 週 | 4-6 週 | 4-6 週 | 18-24 週 |
| **Client-Server** | - | - | 2-3 週（共用）| 2-3 週 | 2-3 週 | 9-14 週 |

**開發時間節省**：50-60%

### 維護成本比較

| 項目 | 單體架構 | Client-Server |
|------|---------|--------------|
| **代碼庫數量** | 5 個獨立代碼庫 | 1 Server + N Clients |
| **核心邏輯更新** | 需在 5 處更新 | 只需更新 Server |
| **Bug 修復** | 每平台獨立修復 | Server 修復一次即可 |
| **功能新增** | 重複開發 5 次 | Server 開發一次 |
| **技術債務** | 高（5 個技術棧） | 低（1 Server + 各平台 UI） |

**維護成本節省**：80%

### 投資報酬率

**初始投資**:
- Server API 開發：2-3 週
- 桌面 Client：2-3 週
- **總計**：4-6 週

**長期收益**:
- 新平台開發成本降低 70%
- 維護成本降低 80%
- 功能更新效率提升 500%（一次更新，所有平台受益）

**ROI**: 約 **400-500%**

---

## ⚠️ 風險評估

### 技術風險

| 風險 | 機率 | 影響 | 緩解措施 |
|------|------|------|---------|
| **Headless 模式被檢測** | 低 | 中 | stealth.min.js 已足夠，可切換回 GUI |
| **API 安全漏洞** | 中 | 高 | JWT 認證 + HTTPS + Rate Limiting |
| **WebSocket 連接不穩定** | 中 | 中 | 自動重連機制 + 降級方案（輪詢）|
| **跨平台兼容性問題** | 低 | 低 | 使用成熟框架（Electron/React Native）|
| **效能瓶頸** | 低 | 中 | 非同步處理 + 任務佇列 |

### 營運風險

| 風險 | 機率 | 影響 | 緩解措施 |
|------|------|------|---------|
| **Server 端單點故障** | 中 | 高 | Docker 容器化 + 健康檢查 + 備份機制 |
| **雲端成本超預算** | 低 | 中 | 提供本地部署選項 |
| **用戶接受度低** | 低 | 高 | 保留 CLI 版本，逐步遷移 |

### 開發風險

| 風險 | 機率 | 影響 | 緩解措施 |
|------|------|------|---------|
| **開發時間超期** | 中 | 中 | 採用 MVP 策略，優先完成核心功能 |
| **技術選型錯誤** | 低 | 高 | 使用業界成熟方案（FastAPI/Electron）|
| **團隊技能不足** | 中 | 中 | 提供培訓 + 詳細文檔 |

---

## 📚 參考文檔

### 已存在的文檔

- 📖 [ANDROID_HYBRID_ARCHITECTURE_EVALUATION.md](./ANDROID_HYBRID_ARCHITECTURE_EVALUATION.md)
  - 混合架構詳細評估
  - API 端點設計範例
  - 成本效益分析
  - 部署方案

- 📖 [DAILY_WORK_LOG_202511272230.md](./DAILY_WORK_LOG_202511272230.md)
  - 今日討論記錄
  - 決策過程
  - 技術分析

### 相關技術文檔

- 📘 [FastAPI 官方文檔](https://fastapi.tiangolo.com/)
- 📘 [Electron 官方文檔](https://www.electronjs.org/)
- 📘 [Jetpack Compose 指南](https://developer.android.com/jetpack/compose)
- 📘 [SwiftUI 指南](https://developer.apple.com/xcode/swiftui/)

---

## 🎯 下一步行動

### 立即（本週）

1. **決策確認**
   - 確認是否採用 Client-Server 架構
   - 確認優先支援的平台順序
   - 確認開發時程

2. **技術準備**
   - 安裝 FastAPI 開發環境
   - 熟悉 API 設計最佳實踐
   - 準備 Docker 環境

### 短期（1-2 週）

1. **Phase 1 啟動**
   - 建立 FastAPI 專案
   - 實作第一個 API 端點
   - 測試與現有代碼整合

2. **文檔完善**
   - API 詳細規格文檔
   - 開發環境設置指南
   - 貢獻者指南

### 中期（1-3 個月）

1. **完成 Server + 桌面 Client**
   - 可用的 MVP 版本
   - 基本功能完整
   - 用戶測試

2. **移動端開發啟動**
   - Android 或 iOS 擇一優先
   - 根據用戶反饋調整

---

## 📝 變更記錄

| 日期 | 版本 | 變更內容 | 作者 |
|------|------|---------|------|
| 2025-11-27 | 1.0 | 初版建立 | wizard03 |

---

*文檔建立日期: 2025-11-27*
*專案代號: Gleipnir (格萊普尼爾)*
*協作工具: Claude Code CLI - Sonnet 4.5*

---

**Happy Coding! 🚀**

*This architecture plan was created with AI assistance (Claude Code CLI)*
