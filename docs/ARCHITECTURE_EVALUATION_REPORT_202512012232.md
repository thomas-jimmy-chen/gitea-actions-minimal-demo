# EEBot 架構評估與實施建議報告

**專案代號**: Gleipnir (格萊普尼爾)
**報告日期**: 2025-12-01
**報告編號**: ARCH-EVAL-202512012232
**記錄者**: wizard03 (with Claude Code CLI - Sonnet 4.5)
**報告類型**: 技術評估與實施建議

---

## 📋 執行摘要

本報告針對 EEBot 專案提出的兩個優先項目進行深入分析：
1. **GUI 開發** - 提供圖形化使用者介面
2. **Client-Server 架構分離** - 將自動化引擎與控制介面分離

**核心結論**:
- ✅ **GUI 開發**: 建議實施，推薦 CustomTkinter，預估 18-26 小時
- ⚠️ **Client-Server 架構**: 需評估必要性，預估 40-60 小時，建議延後至 Phase 2

---

## 📊 目錄

- [第一部分：TMS+ 平台分析](#第一部分tms-平台分析)
- [第二部分：GUI 開發方案評估](#第二部分gui-開發方案評估)
- [第三部分：Client-Server 架構評估](#第三部分client-server-架構評估)
- [第四部分：API 設計與認證方案](#第四部分api-設計與認證方案)
- [第五部分：業界最佳實踐比較](#第五部分業界最佳實踐比較)
- [第六部分：實施建議](#第六部分實施建議)
- [第七部分：風險評估與緩解策略](#第七部分風險評估與緩解策略)

---

## 第一部分：TMS+ 平台分析

### 1.1 平台資訊確認

**原先誤認**: elearning 平台
**實際平台**: TMS+ (台灣數位學習科技 FormosaSoft 開發)
**測試網站**: https://tms.utaipei.edu.tw/ (臺北市立大學)

### 1.2 TronClass vs TMS+ 差異分析

#### 技術架構對比

| 特性 | TronClass | TMS+ | 差異程度 |
|------|-----------|------|---------|
| **前端框架** | AngularJS | jQuery + Bootstrap | 🔴 完全不同 |
| **DOM 屬性** | `ng-bind`, `ng-model`, `ng-click` | `data-url`, `data-toggle`, `data-target` | 🔴 完全不同 |
| **路由機制** | AngularJS SPA 路由 | 傳統 HTML + iframe 模態 | 🔴 完全不同 |
| **資料綁定** | AngularJS 雙向綁定 | jQuery AJAX + DOM 操作 | 🔴 完全不同 |
| **本地化** | `$translate` | `fs.lang` 物件 | 🟡 方法不同 |
| **響應式設計** | 自訂 CSS | Bootstrap 響應式 | 🟡 方法不同 |

#### 定位器策略對比

**TronClass 定位器範例**:
```python
# 絕對 XPath (極度脆弱)
courses_container = "/html/body/div[2]/div[5]/div/div/div[2]/div/div[1]/div[2]"

# AngularJS 屬性定位
course_link = "//a[@ng-bind='course.display_name']"
activity_link = "//a[@ng-bind='activity.title']"

# DOM 層級遍歷
for ancestor_level in range(2, 8):
    course_card = course_link.find_element(By.XPATH, f"./ancestor::div[{ancestor_level}]")
```

**TMS+ 定位器建議**:
```python
# CSS Selector (更穩定)
courses_container = ".fs-mobile-navbar, #mod_successionCourse_8"

# Bootstrap data 屬性定位
course_modal = "a[data-toggle='modal'][data-target^='#courseInfo_modal']"
search_button = "button[data-url*='searchBulletin']"

# ID 定位 (最穩定)
course_info_modal = "#courseInfo_modal243"
```

### 1.3 平台相依性分析

**掃描模組相依度評估** (基於 TronClass 經驗):

| 模組 | TronClass 相依度 | TMS+ 相依度預估 | 重構工作量 |
|-----|----------------|----------------|----------|
| `course_list_page.py` | 🔴🔴🔴🔴🔴 (95%) | 🔴🔴🔴🔴🔴 (95%) | 6-8 小時 |
| `course_detail_page.py` | 🔴🔴🔴🔴 (80%) | 🔴🔴🔴🔴 (85%) | 4-6 小時 |
| `exam_detail_page.py` | 🔴🔴🔴🔴 (80%) | 🔴🔴🔴 (70%) | 4-6 小時 |
| `login_page.py` | 🟡🟡🟡 (60%) | 🟡🟡🟡 (65%) | 2-3 小時 |

**總計重構工作量**: 16-23 小時

### 1.4 平台遷移建議

**推薦方案**: 策略模式 (Strategy Pattern)

**優點**:
- ✅ 完全解耦平台邏輯
- ✅ 易於新增新平台
- ✅ 保持向後相容
- ✅ 符合 SOLID 原則

**檔案結構設計**:
```
src/pages/
├── base_page.py                    # 保持不變
├── platforms/                      # 【新增】平台抽象層
│   ├── __init__.py
│   ├── base_platform.py            # 抽象基類
│   ├── tronclass/                  # TronClass 實作
│   │   ├── __init__.py
│   │   ├── course_list_page.py
│   │   ├── course_detail_page.py
│   │   ├── exam_detail_page.py
│   │   └── locators.py             # 定位器配置
│   └── tmsplus/                    # 【新增】TMS+ 實作
│       ├── __init__.py
│       ├── course_list_page.py
│       ├── course_detail_page.py
│       ├── exam_detail_page.py
│       └── locators.py
└── factory.py                      # 【新增】平台工廠
```

---

## 第二部分：GUI 開發方案評估

### 2.1 業界 GUI 框架比較 (2024-2025)

#### 方案 A: CustomTkinter ⭐⭐⭐⭐⭐ (強烈推薦)

**優點**:
- ✅ 基於 Tkinter，Python 內建，無額外依賴
- ✅ 現代化 UI 設計 (Material Design 風格)
- ✅ 支援深色/淺色主題切換
- ✅ 完全跨平台 (Windows/Linux/macOS)
- ✅ 學習曲線平緩
- ✅ 活躍開發與社群支援
- ✅ 安裝簡單: `pip install customtkinter`

**缺點**:
- ❌ 功能相對簡單，不適合複雜商業應用
- ❌ 元件數量較少

**適用場景**:
- 中小型桌面應用
- 快速原型開發
- 個人專案或內部工具

**預估開發時間**: 18-26 小時

**參考資源**:
- GitHub: https://github.com/TomSchimansky/CustomTkinter
- 文檔: https://customtkinter.tomschimansky.com/

---

#### 方案 B: PyQt6 ⭐⭐⭐⭐

**優點**:
- ✅ 功能強大，超過 600 個類別
- ✅ 商業級應用品質
- ✅ 完整的 GUI 元件庫
- ✅ 支援跨平台 (Windows/Linux/macOS/iOS/Android)
- ✅ 專業文檔與範例

**缺點**:
- ❌ 學習曲線陡峭
- ❌ 授權問題 (GPL 或商業授權)
- ❌ 安裝包較大 (>50MB)

**適用場景**:
- 大型商業應用
- 需要複雜 UI 的專案
- 企業級軟體

**預估開發時間**: 30-40 小時

---

#### 方案 C: Tkinter (原生) ⭐⭐⭐

**優點**:
- ✅ Python 內建，零依賴
- ✅ 穩定性高
- ✅ 文檔豐富

**缺點**:
- ❌ UI 外觀過時
- ❌ 缺乏現代化元件

**適用場景**:
- 簡單工具
- 學習用途

**預估開發時間**: 15-20 小時

---

### 2.2 EEBot GUI 需求分析

#### 核心功能模組 (基於現有規劃)

1. **課程管理介面** (替代 menu.py)
   - 視覺化課程選擇
   - 排程管理 (新增、移除、清空)
   - 課程標記 (課程 vs 考試、自動答題標誌)

2. **配置管理介面** (編輯 eebot.cfg)
   - 圖形化編輯所有配置項
   - 帳號設定、Proxy 設定、自動答題設定
   - 即時驗證與儲存

3. **執行監控介面**
   - 即時進度條 (總進度 + 當前課程進度)
   - 執行日誌滾動顯示
   - 蟲洞狀態顯示 (時間加速)
   - 暫停/停止控制

4. **智能推薦介面** (替代 menu.py 的 'i' 功能)
   - 自動掃描「修習中」課程
   - 樹狀顯示掃描結果
   - 一鍵執行確認對話框

5. **時間統計報告查看器**
   - 讀取 `reports/time_report_*.md`
   - 圖表化顯示 (圓餅圖、長條圖)
   - 課程明細表格

6. **截圖瀏覽器**
   - 縮圖網格顯示
   - 點擊放大檢視

#### 技術要點

**多執行緒管理** (關鍵):
```python
import threading

def start_execution(self):
    # 在背景執行緒執行避免 GUI 凍結
    thread = threading.Thread(
        target=self.run_automation,
        args=(scheduled,),
        daemon=True
    )
    thread.start()
```

**進度回呼機制**:
```python
# Scenario 呼叫 callback
if self.progress_callback:
    self.progress_callback({
        'type': 'progress',
        'current': 2,
        'total': 5,
        'message': '正在執行課程 2/5'
    })
```

### 2.3 GUI 開發實施計畫

| 階段 | 工作內容 | 預估時間 | 優先級 |
|-----|---------|---------|--------|
| **Phase 1** | 基礎 GUI 框架 + 課程選擇器 | 4-6 小時 | P0 |
| **Phase 2** | 配置編輯器 + 執行監控 | 4-6 小時 | P0 |
| **Phase 3** | 智能推薦 GUI + 多執行緒整合 | 3-4 小時 | P0 |
| **Phase 4** | 時間統計報告查看器 + 截圖瀏覽 | 3-4 小時 | P1 |
| **Phase 5** | 測試與優化 + 打包 | 4-6 小時 | P1 |
| **總計** | | **18-26 小時** | |

### 2.4 GUI 開發建議

**推薦方案**: CustomTkinter ⭐⭐⭐⭐⭐

**理由**:
1. ✅ 完美符合專案需求 (中小型桌面工具)
2. ✅ 快速開發 (18-26 小時)
3. ✅ 現代化外觀
4. ✅ 跨平台支援 (Windows/Linux/macOS)
5. ✅ 學習曲線平緩
6. ✅ 無授權問題
7. ✅ 部署簡單 (pip install)

**實施優先級**: 🟢 **建議實施** (Phase 1 優先)

---

## 第三部分：Client-Server 架構評估

### 3.1 當前架構分析

**現有架構** (Monolithic):
```
┌────────────────────────────────────┐
│         EEBot (單體架構)             │
├────────────────────────────────────┤
│  • main.py (主程式)                 │
│  • menu.py (選單系統)               │
│  • src/core/* (核心模組)            │
│  • src/pages/* (頁面物件)           │
│  • src/scenarios/* (業務流程)       │
│  • src/services/* (服務層)          │
│  • MitmProxy (API 攔截)             │
│  • Selenium WebDriver               │
│  • Chrome Browser                   │
└────────────────────────────────────┘
```

**優點**:
- ✅ 架構簡單，易於開發與維護
- ✅ 無網路延遲
- ✅ 無需處理分散式系統複雜性
- ✅ 適合單機使用

**缺點**:
- ❌ 無法遠端控制
- ❌ 無法多人協作
- ❌ 無法行動裝置控制
- ❌ 資源無法共享

### 3.2 Client-Server 架構設計

#### 方案 A: RESTful API 架構 ⭐⭐⭐⭐⭐

**架構圖**:
```
┌──────────────────┐         ┌──────────────────────────┐
│   Client 端       │         │   Server 端 (PC/雲端)      │
├──────────────────┤  HTTP   ├──────────────────────────┤
│  • GUI 介面       │◄──────►│  • FastAPI REST API       │
│  • Android App    │  HTTPS  │  • EEBot 自動化引擎       │
│  • Web Dashboard  │   TLS   │  • Selenium WebDriver     │
│  • CLI 工具       │         │  • MitmProxy              │
│                  │         │  • Chrome Browser         │
│  [控制端]         │         │  [執行端]                 │
└──────────────────┘         └──────────────────────────┘
```

**API 端點設計**:
```python
# 課程管理 API
POST   /api/v1/courses/schedule     # 排程課程
GET    /api/v1/courses/scheduled    # 查看排程
DELETE /api/v1/courses/scheduled/:id # 移除排程

# 執行控制 API
POST   /api/v1/execution/start      # 開始執行
POST   /api/v1/execution/stop       # 停止執行
POST   /api/v1/execution/pause      # 暫停執行
GET    /api/v1/execution/status     # 查詢狀態

# 進度監控 API
GET    /api/v1/progress/current     # 當前進度
WS     /api/v1/progress/stream      # WebSocket 即時進度

# 配置管理 API
GET    /api/v1/config               # 取得配置
PUT    /api/v1/config               # 更新配置
POST   /api/v1/config/validate      # 驗證配置

# 報告查詢 API
GET    /api/v1/reports/time         # 時間統計報告
GET    /api/v1/reports/screenshots  # 截圖列表

# 健康檢查 API
GET    /api/v1/health               # 服務健康狀態
```

**技術棧建議**:
- **Server**: FastAPI (Python) + Pydantic + SQLite
- **Client**: CustomTkinter (Desktop) / React (Web) / Kotlin (Android)
- **通訊**: RESTful API + WebSocket (即時進度)
- **認證**: JWT Token + API Key

**優點**:
- ✅ RESTful API 標準化
- ✅ 支援多種客戶端 (Desktop/Web/Mobile)
- ✅ WebSocket 即時進度推送
- ✅ 易於擴展與維護
- ✅ 完整的 API 文檔 (自動生成)

**缺點**:
- ❌ 開發工作量大 (40-60 小時)
- ❌ 需處理網路延遲與錯誤
- ❌ 安全性考量 (API 認證、HTTPS)

---

#### 方案 B: Selenium RemoteWebDriver ⭐⭐⭐⭐

**架構圖**:
```
┌──────────────────┐         ┌─────────────────────────┐
│   Client 端       │         │   Server 端 (Selenium)   │
├──────────────────┤  HTTP   ├─────────────────────────┤
│  • Python Script  │◄──────►│  • Selenium Grid / Hub  │
│  • RemoteWebDriver│  4444   │  • Chrome/Firefox Node  │
│                  │         │  • MitmProxy            │
└──────────────────┘         └─────────────────────────┘
```

**實作範例**:
```python
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Client 端連接到 Server 端的 Selenium Grid
driver = webdriver.Remote(
    command_executor='http://server_ip:4444/wd/hub',
    desired_capabilities=DesiredCapabilities.CHROME
)

# 執行自動化操作 (與現有程式碼相同)
driver.get('https://elearn.post.gov.tw')
```

**優點**:
- ✅ 實作簡單 (僅需修改 WebDriver 初始化)
- ✅ Selenium 官方支援
- ✅ 適合跨平台測試
- ✅ 預估工作量: 8-12 小時

**缺點**:
- ❌ 功能受限 (僅限瀏覽器操作)
- ❌ 無法控制 MitmProxy
- ❌ 無法管理排程與配置
- ❌ 無法查看報告與截圖

---

#### 方案 C: 混合架構 (推薦) ⭐⭐⭐⭐⭐

**架構設計**:
```
階段 1 (立即): GUI 開發 (CustomTkinter)
階段 2 (未來): 選擇性添加 API 層 (FastAPI)
```

**優點**:
- ✅ 漸進式開發，風險低
- ✅ 先滿足當前需求 (單機 GUI)
- ✅ 為未來擴展預留空間
- ✅ 符合 YAGNI 原則 (You Ain't Gonna Need It)

---

### 3.3 Client-Server 架構實施建議

**實施優先級**: 🟡 **建議延後** (Phase 2 或更晚)

**理由**:
1. ❌ **當前無明確需求** - 用戶未提及遠端控制或多人協作需求
2. ❌ **投資報酬率低** - 40-60 小時開發時間 vs 目前單機使用足夠
3. ❌ **增加複雜性** - 需處理網路、安全性、錯誤恢復等問題
4. ✅ **GUI 開發更緊迫** - 直接改善使用者體驗

**建議**:
- 先完成 GUI 開發 (Phase 1)
- 評估實際使用情況
- 若未來有遠端控制需求，再評估 Client-Server 架構

---

## 第四部分：API 設計與認證方案

### 4.1 RESTful API 設計原則 (業界最佳實踐)

#### 1. HTTP 方法使用

| HTTP 方法 | 用途 | 範例 |
|----------|------|------|
| `GET` | 查詢資源 | `GET /api/v1/courses` |
| `POST` | 建立資源 | `POST /api/v1/courses/schedule` |
| `PUT` | 更新資源 (完整替換) | `PUT /api/v1/config` |
| `PATCH` | 更新資源 (部分更新) | `PATCH /api/v1/courses/:id` |
| `DELETE` | 刪除資源 | `DELETE /api/v1/courses/:id` |

#### 2. RESTful URI 命名規範

**最佳實踐**:
```
✅ 使用名詞複數:       /api/v1/courses
✅ 使用小寫:          /api/v1/courses (不使用 /api/v1/Courses)
✅ 使用連字符:        /api/v1/time-reports (不使用 /api/v1/time_reports)
✅ 階層化結構:        /api/v1/courses/{id}/exams
✅ 版本控制:         /api/v1/, /api/v2/
```

**避免**:
```
❌ 使用動詞:         /api/v1/getCourses (應使用 GET /api/v1/courses)
❌ 查詢參數作為動作: /api/v1/courses?action=delete
❌ 檔案副檔名:       /api/v1/courses.json
```

#### 3. HTTP 狀態碼使用

| 狀態碼 | 意義 | 使用時機 |
|--------|------|---------|
| `200 OK` | 成功 | GET, PUT, PATCH 成功 |
| `201 Created` | 已建立 | POST 成功建立資源 |
| `204 No Content` | 無內容 | DELETE 成功 |
| `400 Bad Request` | 錯誤請求 | 請求參數錯誤 |
| `401 Unauthorized` | 未授權 | 未提供或錯誤的 API Key |
| `403 Forbidden` | 禁止訪問 | API Key 權限不足 |
| `404 Not Found` | 未找到 | 資源不存在 |
| `429 Too Many Requests` | 請求過多 | Rate Limiting |
| `500 Internal Server Error` | 伺服器錯誤 | 內部錯誤 |

#### 4. 資料驗證 (Pydantic)

**FastAPI + Pydantic 範例**:
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List

class CourseScheduleRequest(BaseModel):
    program_name: str = Field(..., min_length=1, max_length=200)
    exam_name: str = Field(..., min_length=1, max_length=200)
    enable_auto_answer: bool = Field(default=False)
    delay: float = Field(default=7.0, ge=0, le=60)

    @validator('delay')
    def validate_delay(cls, v):
        if v < 0:
            raise ValueError('Delay must be non-negative')
        return v

@app.post("/api/v1/courses/schedule", status_code=201)
async def schedule_course(request: CourseScheduleRequest):
    # Pydantic 自動驗證資料
    return {"message": "Course scheduled successfully"}
```

---

### 4.2 API Key 認證方案

#### 方案 A: 簡單 API Key 認證 ⭐⭐⭐

**適用場景**: 個人使用、內部工具、信任網路環境

**實作方式**:
```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != "your-secret-api-key-here":
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

@app.get("/api/v1/courses")
async def get_courses(api_key: str = Depends(verify_api_key)):
    return {"courses": [...]}
```

**優點**:
- ✅ 實作簡單 (1-2 小時)
- ✅ 無額外依賴

**缺點**:
- ❌ 無權限控制
- ❌ 無法撤銷 Key (除非重啟服務)
- ❌ 無法追蹤 Key 使用情況

---

#### 方案 B: API Key + RBAC (Role-Based Access Control) ⭐⭐⭐⭐⭐

**適用場景**: 多用戶、需要權限控制、生產環境

**架構設計**:
```python
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime

# 資料庫模型
class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    name = Column(String)  # Key 名稱 (例如: "Desktop App", "Mobile App")
    role = Column(String)  # 角色: "admin", "user", "readonly"
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    rate_limit = Column(Integer, default=100)  # 每小時請求限制

# 權限定義
ROLE_PERMISSIONS = {
    "admin": [
        "courses:read", "courses:write", "courses:delete",
        "execution:start", "execution:stop",
        "config:read", "config:write",
        "reports:read"
    ],
    "user": [
        "courses:read", "courses:write",
        "execution:start", "execution:stop",
        "config:read",
        "reports:read"
    ],
    "readonly": [
        "courses:read",
        "reports:read"
    ]
}

# API Key 驗證中介層
async def verify_api_key(x_api_key: str = Header(...), db: Session = Depends(get_db)):
    # 查詢 API Key
    api_key = db.query(APIKey).filter(APIKey.key == x_api_key).first()

    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    if not api_key.is_active:
        raise HTTPException(status_code=403, detail="API Key is disabled")

    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise HTTPException(status_code=403, detail="API Key has expired")

    # 更新最後使用時間
    api_key.last_used_at = datetime.utcnow()
    db.commit()

    return api_key

# 權限檢查裝飾器
def require_permission(permission: str):
    def decorator(api_key: APIKey = Depends(verify_api_key)):
        if permission not in ROLE_PERMISSIONS.get(api_key.role, []):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {permission} not allowed for role {api_key.role}"
            )
        return api_key
    return decorator

# API 端點使用範例
@app.post("/api/v1/courses/schedule")
async def schedule_course(
    request: CourseScheduleRequest,
    api_key: APIKey = Depends(require_permission("courses:write"))
):
    return {"message": "Course scheduled successfully"}

@app.delete("/api/v1/courses/{course_id}")
async def delete_course(
    course_id: int,
    api_key: APIKey = Depends(require_permission("courses:delete"))
):
    return {"message": "Course deleted successfully"}
```

**權限控制範例**:

| 角色 | 可執行功能 | 不可執行功能 |
|------|----------|------------|
| `admin` | ✅ 查看、新增、修改、刪除課程<br>✅ 啟動、停止執行<br>✅ 查看、修改配置<br>✅ 查看報告 | - |
| `user` | ✅ 查看、新增、修改課程<br>✅ 啟動、停止執行<br>✅ 查看配置<br>✅ 查看報告 | ❌ 刪除課程<br>❌ 修改配置 |
| `readonly` | ✅ 查看課程<br>✅ 查看報告 | ❌ 新增、修改、刪除課程<br>❌ 啟動、停止執行<br>❌ 查看、修改配置 |

**API Key 管理 CLI 工具**:
```bash
# 生成新 API Key
python api_key_manager.py create --name "Desktop App" --role "admin"
# 輸出: API Key: sk_live_abc123def456...

# 列出所有 API Key
python api_key_manager.py list

# 撤銷 API Key
python api_key_manager.py revoke --key "sk_live_abc123def456..."

# 更新 API Key 權限
python api_key_manager.py update --key "sk_live_abc123def456..." --role "readonly"
```

**優點**:
- ✅ 完整的權限控制 (RBAC)
- ✅ 可撤銷 Key
- ✅ 可追蹤使用情況
- ✅ 支援 Key 過期時間
- ✅ 支援 Rate Limiting
- ✅ 符合業界最佳實踐

**缺點**:
- ❌ 實作複雜 (6-8 小時)
- ❌ 需要資料庫 (SQLite)

---

#### 方案 C: JWT Token 認證 ⭐⭐⭐⭐

**適用場景**: 需要狀態管理、多用戶、Web 應用

**實作方式**:
```python
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**優點**:
- ✅ 無需資料庫查詢 (stateless)
- ✅ 支援過期時間
- ✅ 標準化 (OAuth 2.0)

**缺點**:
- ❌ 無法撤銷 Token (除非使用黑名單)
- ❌ 需要處理 Token 刷新邏輯

---

### 4.3 API 認證方案建議

**推薦方案**: API Key + RBAC ⭐⭐⭐⭐⭐

**理由**:
1. ✅ 完整的權限控制
2. ✅ 可撤銷 Key (重要)
3. ✅ 易於管理與追蹤
4. ✅ 適合桌面應用 + 未來行動應用
5. ✅ 符合業界最佳實踐 (2024-2025)

**實施建議**:
- 使用 SQLite 儲存 API Key 資訊
- 實作 CLI 工具管理 Key
- 預設角色: `admin` (本地使用), `readonly` (遠端查看)

---

## 第五部分：業界最佳實踐比較

### 5.1 GUI 開發最佳實踐 (2024-2025)

**參考專案**:
1. **VS Code** - Electron + TypeScript
2. **PyCharm** - Swing (Java)
3. **Postman** - Electron + React
4. **Docker Desktop** - Electron + React

**共通特點**:
- ✅ 現代化 UI 設計
- ✅ 響應式佈局
- ✅ 深色/淺色主題
- ✅ 多分頁/模組化介面
- ✅ 即時更新與通知

**EEBot 可借鑑**:
- ✅ 使用 CustomTkinter 實現現代化 UI
- ✅ 支援主題切換
- ✅ 多分頁設計 (課程管理、執行監控、報告查看)
- ✅ WebSocket 即時進度推送

---

### 5.2 API 設計最佳實踐 (2024-2025)

**業界標準參考**:
1. **GitHub API** - RESTful + OAuth 2.0
2. **Stripe API** - RESTful + API Key + Versioning
3. **AWS API** - RESTful + IAM + RBAC
4. **Google Cloud API** - RESTful + OAuth 2.0 + Service Account

**共通特點**:
- ✅ RESTful 設計原則
- ✅ API Key + RBAC 權限控制
- ✅ Rate Limiting (防止濫用)
- ✅ 詳細的 API 文檔 (Swagger/OpenAPI)
- ✅ 版本控制 (/api/v1/, /api/v2/)
- ✅ HTTPS 加密傳輸

**EEBot 可借鑑**:
- ✅ 採用 RESTful API 設計
- ✅ API Key + RBAC 認證
- ✅ FastAPI 自動生成 API 文檔
- ✅ 版本控制設計 (/api/v1/)

---

### 5.3 Selenium 遠端執行最佳實踐

**業界解決方案**:
1. **Selenium Grid** - 官方分散式執行方案
2. **BrowserStack** - 雲端瀏覽器測試平台
3. **Sauce Labs** - 雲端自動化測試平台
4. **LambdaTest** - 雲端跨瀏覽器測試

**共通特點**:
- ✅ Selenium RemoteWebDriver
- ✅ Docker 容器化部署
- ✅ 支援並行執行
- ✅ 即時日誌與截圖

**EEBot 若要實現遠端執行**:
- ✅ 使用 Selenium Grid (開源、免費)
- ✅ Docker Compose 快速部署
- ✅ 支援 Windows/Linux 遠端節點

---

## 第六部分：實施建議

### 6.1 優先級排序

| 項目 | 優先級 | 工作量 | 效益 | 建議 |
|------|--------|--------|------|------|
| **GUI 開發 (CustomTkinter)** | 🔴 P0 - 高 | 18-26 小時 | 🟢 高 | ✅ **立即實施** |
| **TMS+ 平台支援** | 🟡 P1 - 中 | 16-23 小時 | 🟢 中高 | ✅ **Phase 1 實施** |
| **Client-Server 架構** | 🟢 P2 - 低 | 40-60 小時 | 🟡 中 | ⚠️ **延後至 Phase 2** |
| **API Key + RBAC** | 🟢 P2 - 低 | 6-8 小時 | 🟡 低 | ⚠️ **依賴 Client-Server** |

### 6.2 階段式實施計畫

#### Phase 1: GUI 開發 + TMS+ 支援 (優先)

**目標**: 提升使用者體驗 + 支援多平台

**工作項目**:
1. ✅ GUI 基礎框架 (CustomTkinter) - 4-6 小時
2. ✅ 課程管理介面 - 4-6 小時
3. ✅ 執行監控介面 - 3-4 小時
4. ✅ TMS+ 平台支援 (策略模式重構) - 16-23 小時

**總計**: 34-49 小時

**預期效益**:
- ✅ 圖形化介面，降低使用門檻
- ✅ 支援 TronClass + TMS+ 雙平台
- ✅ 即時監控執行進度

---

#### Phase 2: Client-Server 架構 (可選)

**前提條件**: 確認有遠端控制需求

**工作項目**:
1. FastAPI REST API 開發 - 12-16 小時
2. API Key + RBAC 認證 - 6-8 小時
3. WebSocket 即時進度推送 - 4-6 小時
4. Client 端適配 (GUI/Mobile) - 8-12 小時
5. Docker 容器化部署 - 4-6 小時
6. 測試與文檔 - 6-12 小時

**總計**: 40-60 小時

**預期效益**:
- ✅ 遠端控制 (行動裝置/其他電腦)
- ✅ 多用戶協作
- ✅ 雲端部署可能性

**風險**:
- ⚠️ 增加系統複雜性
- ⚠️ 需處理網路安全性
- ⚠️ 需處理錯誤恢復邏輯

---

### 6.3 實施決策建議

#### 立即實施：GUI 開發 ✅

**理由**:
1. ✅ 直接改善使用者體驗
2. ✅ 工作量適中 (18-26 小時)
3. ✅ 技術風險低
4. ✅ 無需外部依賴

**建議方案**: CustomTkinter

**實施步驟**:
1. 安裝 CustomTkinter: `pip install customtkinter`
2. 建立 GUI 基礎框架
3. 逐步實現功能模組
4. 整合現有 Scenario 與 Service

**預估時程**: 2-3 週 (每天 3-4 小時)

---

#### 延後實施：Client-Server 架構 ⚠️

**理由**:
1. ❌ 當前無明確需求
2. ❌ 工作量大 (40-60 小時)
3. ❌ 增加系統複雜性
4. ⚠️ YAGNI 原則 (You Ain't Gonna Need It)

**建議**:
- 先完成 GUI 開發
- 評估實際使用情況
- 若未來有遠端控制需求，再實施

**觸發條件** (何時考慮實施):
- ✅ 需要行動裝置控制
- ✅ 需要多人協作
- ✅ 需要雲端部署
- ✅ 需要 API 整合其他系統

---

### 6.4 技術債務與重構建議

#### 1. 定位器策略優化

**問題**: TronClass 使用絕對 XPath，極度脆弱

**建議**:
```python
# 現有 (❌ 脆弱)
courses_container = "/html/body/div[2]/div[5]/div/div/div[2]/div/div[1]/div[2]"

# 建議 (✅ 穩定)
courses_container = ".course-list-container, [data-role='course-list']"
```

**工作量**: 2-4 小時
**優先級**: P1

---

#### 2. 錯誤處理增強

**問題**: 部分 Scenario 缺乏完整的錯誤處理

**建議**:
```python
try:
    self.driver.find_element(By.CSS_SELECTOR, locator)
except NoSuchElementException:
    self.logger.error(f"Element not found: {locator}")
    self.screenshot_utils.capture("error_element_not_found")
    raise
except Exception as e:
    self.logger.error(f"Unexpected error: {e}")
    self.screenshot_utils.capture("error_unexpected")
    raise
```

**工作量**: 4-6 小時
**優先級**: P1

---

#### 3. 日誌系統標準化

**問題**: 混用 `print()` 和 `logging` 模組

**建議**:
- 統一使用 `logging` 模組
- 定義日誌等級 (DEBUG, INFO, WARNING, ERROR)
- 輸出到檔案 + 終端

**工作量**: 3-4 小時
**優先級**: P2

---

## 第七部分：風險評估與緩解策略

### 7.1 GUI 開發風險

| 風險 | 嚴重性 | 可能性 | 緩解策略 |
|-----|-------|-------|---------|
| CustomTkinter 元件不足 | 🟡 中 | 🟢 低 | 可自訂元件或使用原生 Tkinter 補充 |
| 多執行緒同步問題 | 🟡 中 | 🟡 中 | 使用 `queue.Queue` 進行執行緒間通訊 |
| GUI 凍結 (未使用多執行緒) | 🔴 高 | 🟢 低 | 強制使用背景執行緒執行長時間操作 |
| 跨平台字體問題 | 🟢 低 | 🟢 低 | 已有字體載入解決方案 (v2.0.3) |

### 7.2 Client-Server 架構風險

| 風險 | 嚴重性 | 可能性 | 緩解策略 |
|-----|-------|-------|---------|
| 網路延遲與斷線 | 🟡 中 | 🟡 中 | 實作重試機制與錯誤恢復 |
| API 安全性漏洞 | 🔴 高 | 🟡 中 | HTTPS + API Key + RBAC + Rate Limiting |
| 狀態不一致 | 🟡 中 | 🟡 中 | 使用資料庫持久化狀態 |
| 並行執行衝突 | 🟡 中 | 🟢 低 | 僅允許單一執行任務 (互斥鎖) |
| 開發時間超出預估 | 🟡 中 | 🔴 高 | 分階段交付，優先核心功能 |

### 7.3 TMS+ 平台遷移風險

| 風險 | 嚴重性 | 可能性 | 緩解策略 |
|-----|-------|-------|---------|
| TMS+ 定位器不穩定 | 🟡 中 | 🟡 中 | 使用 CSS Selector + ID (更穩定) |
| 功能差異過大 | 🔴 高 | 🟢 低 | 策略模式完全隔離平台邏輯 |
| 測試覆蓋不足 | 🟡 中 | 🟡 中 | 完整的回歸測試覆蓋 |

---

## 📊 成本效益分析

### GUI 開發 (CustomTkinter)

| 項目 | 數值 |
|-----|------|
| **開發時間** | 18-26 小時 |
| **技術風險** | 🟢 低 |
| **預期效益** | 🟢 高 (直接改善 UX) |
| **投資報酬率 (ROI)** | ⭐⭐⭐⭐⭐ (5/5) |
| **建議** | ✅ **立即實施** |

### Client-Server 架構 (FastAPI)

| 項目 | 數值 |
|-----|------|
| **開發時間** | 40-60 小時 |
| **技術風險** | 🟡 中 |
| **預期效益** | 🟡 中 (需有遠端控制需求) |
| **投資報酬率 (ROI)** | ⭐⭐ (2/5) - 當前需求下 |
| **建議** | ⚠️ **延後至 Phase 2** |

---

## 🎯 最終建議

### 立即實施項目

#### 1. GUI 開發 (CustomTkinter) ✅ 強烈建議

**理由**:
- ✅ 直接改善使用者體驗
- ✅ 工作量適中 (18-26 小時)
- ✅ 技術風險低
- ✅ 符合當前需求

**建議框架**: CustomTkinter ⭐⭐⭐⭐⭐

**實施時程**: 2-3 週

---

#### 2. TMS+ 平台支援 ✅ 建議實施

**理由**:
- ✅ 用戶已提供平台資訊
- ✅ 工作量可控 (16-23 小時)
- ✅ 提升專案通用性

**建議方案**: 策略模式重構

**實施時程**: 2-3 週

---

### 延後實施項目

#### 1. Client-Server 架構 ⚠️ 建議延後

**理由**:
- ❌ 當前無明確需求
- ❌ 工作量大 (40-60 小時)
- ❌ 投資報酬率低 (當前需求下)
- ⚠️ 符合 YAGNI 原則

**建議**:
- 先完成 GUI 開發
- 評估實際使用情況
- 若未來有需求，再實施

---

#### 2. API Key + RBAC ⚠️ 依賴 Client-Server

**理由**:
- ❌ 依賴 Client-Server 架構
- ❌ 單機 GUI 無需 API 認證

**建議**:
- 若實施 Client-Server，則必須實施
- 推薦方案: API Key + RBAC

---

## 📚 附錄

### 附錄 A: CustomTkinter 範例程式碼

```python
import customtkinter as ctk
from threading import Thread

class EEBotGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 設定視窗
        self.title("EEBot - Gleipnir")
        self.geometry("1200x800")

        # 設定主題
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 建立分頁
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # 新增分頁
        self.tab_courses = self.tabview.add("課程管理")
        self.tab_execution = self.tabview.add("執行監控")
        self.tab_config = self.tabview.add("配置管理")

        # 課程管理介面
        self._build_courses_tab()

        # 執行監控介面
        self._build_execution_tab()

    def _build_courses_tab(self):
        # 課程列表
        self.courses_list = ctk.CTkScrollableFrame(self.tab_courses)
        self.courses_list.pack(fill="both", expand=True, padx=10, pady=10)

        # 操作按鈕
        button_frame = ctk.CTkFrame(self.tab_courses)
        button_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            button_frame,
            text="新增課程",
            command=self.add_course
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="開始執行",
            command=self.start_execution
        ).pack(side="left", padx=5)

    def _build_execution_tab(self):
        # 進度條
        self.progress_label = ctk.CTkLabel(
            self.tab_execution,
            text="準備就緒"
        )
        self.progress_label.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(self.tab_execution)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)

        # 日誌區域
        self.log_text = ctk.CTkTextbox(self.tab_execution)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

    def add_course(self):
        # 開啟課程新增對話框
        pass

    def start_execution(self):
        # 在背景執行緒執行
        thread = Thread(target=self._run_automation, daemon=True)
        thread.start()

    def _run_automation(self):
        # 執行自動化邏輯
        # 更新 GUI (使用 self.after() 確保執行緒安全)
        self.after(0, lambda: self.progress_bar.set(0.5))
        self.after(0, lambda: self.log_text.insert("end", "執行中...\n"))

if __name__ == "__main__":
    app = EEBotGUI()
    app.mainloop()
```

### 附錄 B: FastAPI RESTful API 範例

```python
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

app = FastAPI(title="EEBot API", version="1.0.0")

# 資料模型
class CourseScheduleRequest(BaseModel):
    program_name: str
    exam_name: str
    enable_auto_answer: bool = False
    delay: float = 7.0

class ExecutionStatus(BaseModel):
    status: str  # "idle", "running", "paused", "completed", "error"
    current_course: Optional[str]
    progress: float  # 0.0 - 1.0
    message: str

# API Key 驗證 (簡化版)
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != "your-secret-api-key":
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

# 課程管理 API
@app.post("/api/v1/courses/schedule", status_code=201)
async def schedule_course(
    request: CourseScheduleRequest,
    api_key: str = Depends(verify_api_key)
):
    # 排程邏輯
    return {"message": "Course scheduled successfully", "course_id": 1}

@app.get("/api/v1/courses/scheduled")
async def get_scheduled_courses(api_key: str = Depends(verify_api_key)):
    # 查詢排程
    return {"courses": []}

# 執行控制 API
@app.post("/api/v1/execution/start")
async def start_execution(api_key: str = Depends(verify_api_key)):
    # 啟動執行
    return {"message": "Execution started"}

@app.get("/api/v1/execution/status")
async def get_execution_status(api_key: str = Depends(verify_api_key)):
    # 查詢狀態
    return ExecutionStatus(
        status="idle",
        current_course=None,
        progress=0.0,
        message="Ready"
    )

# 健康檢查
@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow()}

# 自動生成 API 文檔
# 訪問 http://localhost:8000/docs
```

### 附錄 C: 參考資源

**GUI 開發**:
- [CustomTkinter GitHub](https://github.com/TomSchimansky/CustomTkinter)
- [CustomTkinter 文檔](https://customtkinter.tomschimansky.com/)
- [Python GUI 比較](https://www.pythonguis.com/faq/which-python-gui-library/)

**FastAPI & REST API**:
- [FastAPI 官方文檔](https://fastapi.tiangolo.com/)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [RESTful API 設計指南](https://www.geeksforgeeks.org/python/fastapi-rest-architecture/)

**API 認證與安全**:
- [RBAC 完整指南](https://www.eyer.ai/blog/role-based-access-control-rbac-complete-guide-2024/)
- [API Key 認證最佳實踐](https://zuplo.com/learning-center/how-rbac-improves-api-permission-management)
- [Auth0 RBAC 文檔](https://auth0.com/docs/manage-users/access-control/rbac)

**Selenium 遠端執行**:
- [Selenium RemoteWebDriver](https://www.selenium.dev/documentation/webdriver/drivers/remote_webdriver/)
- [Selenium WebDriver 架構](https://www.browserstack.com/guide/architecture-of-selenium-webdriver)

---

## 📝 結論

本報告針對 EEBot 專案提出的兩個優先項目進行了深入分析。基於業界最佳實踐、技術可行性、工作量評估與成本效益分析，提出以下建議：

### 核心建議

1. ✅ **GUI 開發** (CustomTkinter) - **立即實施**
   - 預估時間: 18-26 小時
   - 投資報酬率: ⭐⭐⭐⭐⭐ (5/5)
   - 技術風險: 🟢 低

2. ⚠️ **Client-Server 架構** - **建議延後至 Phase 2**
   - 預估時間: 40-60 小時
   - 投資報酬率: ⭐⭐ (2/5) - 當前需求下
   - 技術風險: 🟡 中

3. ✅ **TMS+ 平台支援** - **建議實施**
   - 預估時間: 16-23 小時
   - 投資報酬率: ⭐⭐⭐⭐ (4/5)
   - 技術風險: 🟡 中

### 建議實施順序

**Phase 1**: GUI 開發 (CustomTkinter) + TMS+ 平台支援
**Phase 2**: 評估 Client-Server 架構需求
**Phase 3**: 若需要，實施 Client-Server 架構 + API Key + RBAC

---

**報告完成日期**: 2025-12-01
**報告編號**: ARCH-EVAL-202512012232
**記錄者**: wizard03 (with Claude Code CLI - Sonnet 4.5)

---

*This report was created with AI assistance (Claude Code CLI - Sonnet 4.5)*
