# Eebot - Elearn Automation Bot v2.0

自動化學習機器人，採用 POM (Page Object Model) + API 模組化設計

## 專案架構

```
eebot/
├── src/                          # 主要程式碼
│   ├── core/                     # 核心層 - 基礎設施
│   │   ├── config_loader.py      # 配置載入器
│   │   ├── cookie_manager.py     # Cookie 管理
│   │   ├── driver_manager.py     # WebDriver 管理
│   │   └── proxy_manager.py      # MitmProxy 管理
│   ├── pages/                    # POM 層 - 頁面物件
│   │   ├── base_page.py          # 頁面基類
│   │   ├── login_page.py         # 登入頁
│   │   ├── course_list_page.py   # 課程列表頁
│   │   └── course_detail_page.py # 課程詳情頁
│   ├── api/                      # API 層
│   │   └── interceptors/
│   │       └── visit_duration.py # 訪問時長攔截器
│   ├── scenarios/                # 場景層 - 業務流程編排
│   │   └── course_learning.py   # 課程學習場景
│   └── utils/                    # 工具模組
│       └── stealth_extractor.py  # Stealth JS 提取器
├── data/                         # 資料檔案
│   └── courses.json              # 課程資料配置
├── config/                       # 配置檔案
│   └── eebot.cfg                 # 主配置檔
├── resource/                     # 資源檔案
│   ├── cookies/                  # Cookie 儲存目錄
│   └── plugins/                  # Stealth JS 插件
├── main.py                       # 程式入口
└── eebot_legacy.py               # 原始版本備份
```

## 快速開始

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 2. 配置設定

編輯 config/eebot.cfg：

```
target_http=https://elearn.post.gov.tw
execute_file=D:/chromedriver.exe
cookies_file=cookies.json
user_name=your_username
password=your_password
modify_visits=y
silent_mitm=y
log_save=n
listen_host=127.0.0.1
listen_port=8080
```

### 3. 配置課程資料

編輯 data/courses.json 新增或修改課程：

```json
{
  "courses": [
    {
      "program_name": "課程計畫名稱",
      "lesson_name": "課程名稱",
      "course_id": 369,
      "delay": 7.0
    }
  ]
}
```

### 4. 執行程式

```bash
python main.py
```

## 架構優勢

### 與舊版本比較

舊版本 (eebot_legacy.py):
- 單一檔案 600+ 行
- 難以維護
- 硬編碼課程
- 邏輯耦合
- 無法單元測試

新版本 (v2.0):
- 模組化，分層設計
- 單一職責，易維護
- 資料外部化 (JSON)
- 頁面物件可獨立重用
- 支援單元測試

### 設計模式

1. POM (Page Object Model)
   - 將頁面操作封裝為物件
   - UI 元素與業務邏輯分離
   - 提高程式碼可維護性

2. 模組化設計
   - Core Layer: 基礎設施
   - POM Layer: 頁面操作
   - API Layer: API 攔截
   - Scenario Layer: 業務流程編排

3. 資料驅動
   - 課程資訊儲存在 JSON
   - 配置與程式碼分離
   - 易於新增/修改課程

## 使用範例

### 範例 1：新增課程

只需修改 data/courses.json：

```json
{
  "courses": [
    {
      "program_name": "新課程計畫",
      "lesson_name": "新課程",
      "course_id": 999,
      "delay": 7.0,
      "description": "課程說明"
    }
  ]
}
```

### 範例 2：自訂場景

```python
from src.scenarios.course_learning import CourseLearningScenario
from src.core.config_loader import ConfigLoader

config = ConfigLoader("config/eebot.cfg")
config.load()

scenario = CourseLearningScenario(config)
scenario.execute_single_course(
    program_name="課程計畫",
    lesson_name="課程名稱",
    course_id=369,
    delay=7.0
)
```

### 範例 3：使用頁面物件

```python
from src.pages.login_page import LoginPage
from src.core.driver_manager import DriverManager
from src.core.cookie_manager import CookieManager

driver_manager = DriverManager(config)
driver = driver_manager.create_driver()

cookie_manager = CookieManager('cookies.json')
login_page = LoginPage(driver, cookie_manager)

login_page.auto_login('username', 'password', 'https://example.com')
```

## 維護指南

### 新增頁面物件

1. 在 src/pages/ 建立新的頁面類別
2. 繼承 BasePage
3. 定義元素定位器與操作方法

```python
from .base_page import BasePage
from selenium.webdriver.common.by import By

class NewPage(BasePage):
    ELEMENT = (By.ID, 'element_id')

    def do_something(self):
        self.click(self.ELEMENT)
```

### 新增攔截器

1. 在 src/api/interceptors/ 建立新的攔截器
2. 實作 request 或 response 方法

```python
class NewInterceptor:
    def request(self, flow):
        # 攔截請求邏輯
        pass
```

## 模組說明

### Core Layer (核心層)

- config_loader.py: 統一配置管理，支援從 .cfg 檔案讀取設定
- cookie_manager.py: Cookie 的載入、儲存與管理
- driver_manager.py: WebDriver 的初始化、配置與生命週期管理
- proxy_manager.py: MitmProxy 的啟動、配置與管理

### Pages Layer (頁面物件層)

- base_page.py: 所有頁面物件的基類，提供通用方法
- login_page.py: 登入頁面操作（Cookie 登入、手動登入、驗證碼處理）
- course_list_page.py: 課程列表頁面操作（選擇課程、返回等）
- course_detail_page.py: 課程詳情頁面操作（選擇課程、返回課程計畫）

### API Layer (API 層)

- visit_duration.py: 攔截並修改訪問時長的 API 請求

### Scenarios Layer (場景層)

- course_learning.py: 課程學習場景，編排多個頁面物件完成業務流程

### Utils Layer (工具層)

- stealth_extractor.py: 提取 Stealth JS 腳本以繞過自動化檢測

## 版本歷史

- v2.0.0 (2025/01/08) - 重構為 POM + API 模組化架構
- v1.0.0 (2025/07/22) - 初始版本

## 已知問題

- 驗證碼需手動輸入（未來可整合 OCR）
- 部分動態元素需調整等待時間

## 授權

此專案僅供學習與研究使用。

## 作者

Guy Fawkes

## 技術支援

如有問題，請參考：
1. 原始版本：eebot_legacy.py
2. 配置範例：config/eebot.cfg
3. 課程資料範例：data/courses.json
