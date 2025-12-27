# 常量與異常模組使用指南

**建立日期**: 2025-12-18
**版本**: 1.0.0

---

## 目錄
1. [概述](#概述)
2. [constants.py 使用指南](#constantspy-使用指南)
3. [exceptions.py 使用指南](#exceptionspy-使用指南)
4. [遷移指南](#遷移指南)
5. [最佳實踐](#最佳實踐)

---

## 概述

本指南說明如何使用新創建的 `src/constants.py` 和 `src/exceptions.py` 模組。

### 創建的模組

| 模組 | 文件 | 行數 | 內容 |
|-----|------|------|------|
| constants.py | src/constants.py | 450+ | 80+ 個常量 + 5 個輔助函數 |
| exceptions.py | src/exceptions.py | 700+ | 28 個異常類 + 1 個工具函數 |

### 主要目標

1. **消除魔術數字**: 所有硬編碼的數字和字符串提取為常量
2. **統一異常處理**: 使用自定義異常類替代通用 Exception
3. **提高可維護性**: 集中管理配置，易於修改
4. **改善代碼可讀性**: 常量名稱明確表達意圖

---

## constants.py 使用指南

### 1. 導入常量

#### 方式 1: 導入特定常量（推薦）
```python
from src.constants import (
    HTTP_SUCCESS_MIN,
    HTTP_SUCCESS_MAX,
    DEFAULT_PAGE_LOAD_DELAY,
    MAX_LOGIN_RETRIES
)
```

#### 方式 2: 導入整個模組
```python
from src import constants

# 使用時加前綴
timeout = constants.DEFAULT_PAGE_LOAD_DELAY
```

#### 方式 3: 使用別名
```python
from src import constants as const

# 使用時加簡短前綴
timeout = const.DEFAULT_PAGE_LOAD_DELAY
```

---

### 2. HTTP 相關常量

#### 使用前（❌ 不推薦）
```python
# 硬編碼狀態碼
if response.status_code == 200:
    print('成功')

# 魔術數字
response = requests.get(url, timeout=30)
```

#### 使用後（✅ 推薦）
```python
from src.constants import (
    is_http_success,
    HTTP_OK,
    HTTP_TIMEOUT
)

# 使用輔助函數
if is_http_success(response.status_code):
    print('成功')

# 使用常量
response = requests.get(url, timeout=HTTP_TIMEOUT)
```

#### 完整示例
```python
from src.constants import (
    is_http_success,
    HTTP_OK,
    HTTP_NO_CONTENT,
    HTTP_UNAUTHORIZED,
    HTTP_TIMEOUT
)

def send_duration(url, payload):
    """發送時長數據"""
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=HTTP_TIMEOUT
        )

        # 使用輔助函數檢查成功
        if is_http_success(response.status_code):
            if response.status_code == HTTP_OK:
                return response.json()
            elif response.status_code == HTTP_NO_CONTENT:
                return {'success': True}

        # 特定錯誤處理
        if response.status_code == HTTP_UNAUTHORIZED:
            raise SessionExpiredError()

        return None

    except Exception as e:
        print(f'發送失敗: {e}')
        return None
```

---

### 3. 時長相關常量

#### 使用前（❌ 不推薦）
```python
# 硬編碼計算
need_seconds = (required_minutes * 60) + 10
display_minutes = seconds / 60
```

#### 使用後（✅ 推薦）
```python
from src.constants import (
    BUFFER_SECONDS,
    seconds_to_minutes,
    minutes_to_seconds
)

# 使用常量和輔助函數
need_seconds = minutes_to_seconds(required_minutes) + BUFFER_SECONDS
display_minutes = seconds_to_minutes(seconds)
```

#### 完整示例
```python
from src.constants import (
    BUFFER_SECONDS,
    MINIMUM_DURATION_SECONDS,
    minutes_to_seconds,
    seconds_to_minutes
)

def calculate_send_duration(required_minutes: float) -> dict:
    """
    計算需要發送的時長

    Args:
        required_minutes: 要求的分鐘數

    Returns:
        包含秒數和分鐘數的字典
    """
    # 轉換為秒並添加緩衝
    base_seconds = minutes_to_seconds(required_minutes)
    total_seconds = max(base_seconds + BUFFER_SECONDS, MINIMUM_DURATION_SECONDS)

    return {
        'seconds': total_seconds,
        'minutes': seconds_to_minutes(total_seconds),
        'buffer': BUFFER_SECONDS
    }
```

---

### 4. 延遲相關常量

#### 使用前（❌ 不推薦）
```python
# 魔術數字，不知道為什麼是這個值
time.sleep(7)
time.sleep(2)
time.sleep(1)
```

#### 使用後（✅ 推薦）
```python
from src.constants import (
    DEFAULT_PAGE_LOAD_DELAY,
    LESSON_SELECT_DELAY,
    API_REQUEST_DELAY
)

# 清楚表達意圖
time.sleep(DEFAULT_PAGE_LOAD_DELAY)  # 等待頁面完全加載
time.sleep(LESSON_SELECT_DELAY)      # 選擇課程後的延遲
time.sleep(API_REQUEST_DELAY)        # 避免 API 請求過快
```

#### 完整示例
```python
from src.constants import (
    DEFAULT_PAGE_LOAD_DELAY,
    LESSON_SELECT_DELAY,
    PAYLOAD_CAPTURE_WAIT
)

def click_and_capture(detail_page, subcourse_name):
    """點擊子課程並捕獲 Payload"""
    # 點擊子課程
    detail_page.select_lesson_by_name(
        subcourse_name,
        delay=LESSON_SELECT_DELAY
    )

    # 等待頁面加載
    time.sleep(DEFAULT_PAGE_LOAD_DELAY)

    # 等待 Payload 捕獲
    time.sleep(PAYLOAD_CAPTURE_WAIT)
```

---

### 5. 文件路徑常量

#### 使用前（❌ 不推薦）
```python
# 硬編碼路徑
config = ConfigLoader('config/eebot.cfg')
cookies = load_cookies('resource/cookies/cookies.json')

# 生成結果文件名
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'batch_result_{timestamp}.json'
```

#### 使用後（✅ 推薦）
```python
from src.constants import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_COOKIES_PATH,
    get_result_filename,
    BATCH_RESULT_PREFIX
)

# 使用常量
config = ConfigLoader(DEFAULT_CONFIG_PATH)
cookies = load_cookies(DEFAULT_COOKIES_PATH)

# 使用輔助函數
filename = get_result_filename(BATCH_RESULT_PREFIX)
```

---

### 6. API 端點常量

#### 使用前（❌ 不推薦）
```python
# 硬編碼 API 路徑
api_url = f"{base_url}/api/my-courses"
visits_url = f"{base_url}/api/user-visits"
```

#### 使用後（✅ 推薦）
```python
from src.constants import (
    API_MY_COURSES,
    API_USER_VISITS,
    API_COURSE_ACTIVITIES
)

# 使用常量
api_url = f"{base_url}{API_MY_COURSES}"
visits_url = f"{base_url}{API_USER_VISITS}"
activities_url = f"{base_url}{API_COURSE_ACTIVITIES.format(course_id=465)}"
```

---

### 7. 狀態常量

#### 使用前（❌ 不推薦）
```python
# 字符串字面量
if status == 'success':
    ...
if course['status'] == 'completed':
    ...
```

#### 使用後（✅ 推薦）
```python
from src.constants import (
    EXEC_STATUS_SUCCESS,
    EXEC_STATUS_FAILED,
    STATUS_COMPLETED,
    STATUS_IN_PROGRESS
)

# 使用常量
if status == EXEC_STATUS_SUCCESS:
    ...
if course['status'] == STATUS_COMPLETED:
    ...
```

---

## exceptions.py 使用指南

### 1. 基本用法

#### 使用前（❌ 不推薦）
```python
# 使用通用 Exception
if not login_success:
    raise Exception('登入失敗')

try:
    response = requests.get(api_url)
    if response.status_code != 200:
        raise Exception(f'API 錯誤: {response.status_code}')
except Exception as e:
    print(f'錯誤: {e}')
```

#### 使用後（✅ 推薦）
```python
from src.exceptions import LoginError, APIRequestError

# 使用自定義異常
if not login_success:
    raise LoginError(username=username, reason='驗證碼錯誤')

try:
    response = requests.get(api_url)
    if not is_http_success(response.status_code):
        raise APIRequestError(
            url=api_url,
            method='GET',
            status_code=response.status_code
        )
except LoginError as e:
    print(f'登入錯誤 (用戶: {e.username}): {e.reason}')
    # 特定處理：刷新驗證碼
except APIRequestError as e:
    print(f'API 錯誤 (狀態碼: {e.status_code}): {e.url}')
    # 特定處理：重試或記錄
```

---

### 2. 配置相關異常

#### ConfigFileNotFoundError

```python
from src.exceptions import ConfigFileNotFoundError
from src.constants import DEFAULT_CONFIG_PATH

try:
    if not os.path.exists(config_path):
        raise ConfigFileNotFoundError(config_path)

    config = load_config(config_path)
except ConfigFileNotFoundError as e:
    print(f'配置文件不存在: {e.config_path}')
    # 創建默認配置或退出
    create_default_config(DEFAULT_CONFIG_PATH)
```

#### ConfigKeyMissingError

```python
from src.exceptions import ConfigKeyMissingError

REQUIRED_KEYS = ['user_name', 'password', 'target_http']

missing_keys = [key for key in REQUIRED_KEYS if key not in config]
if missing_keys:
    raise ConfigKeyMissingError(missing_keys)
```

#### ConfigValidationError

```python
from src.exceptions import ConfigValidationError

errors = []
if not (1024 <= config['proxy_port'] <= 65535):
    errors.append('proxy_port 必須在 1024-65535 範圍內')
if not config['target_http'].startswith('https://'):
    errors.append('target_http 必須使用 HTTPS')

if errors:
    raise ConfigValidationError(errors)
```

---

### 3. 認證相關異常

#### LoginError

```python
from src.exceptions import LoginError
from src.constants import MAX_LOGIN_RETRIES

retry_count = 0
while retry_count < MAX_LOGIN_RETRIES:
    try:
        login_success = auto_login(username, password)
        if not login_success:
            raise LoginError(
                username=username,
                reason='用戶名或密碼錯誤',
                retry_count=retry_count
            )
        break
    except LoginError as e:
        retry_count += 1
        if retry_count >= MAX_LOGIN_RETRIES:
            print(f'登入失敗（已重試 {e.retry_count} 次）')
            raise
        # 重試邏輯
```

#### SessionExpiredError

```python
from src.exceptions import SessionExpiredError, APIRequestError

try:
    response = requests.get(api_url, cookies=cookies)

    if response.status_code == HTTP_UNAUTHORIZED:
        raise SessionExpiredError()

except SessionExpiredError:
    print('Session 已過期，重新登入...')
    auto_login(username, password)
    # 重新請求
```

---

### 4. API 相關異常

#### APIRequestError

```python
from src.exceptions import APIRequestError
from src.constants import is_http_success, HTTP_TIMEOUT

try:
    response = requests.get(
        api_url,
        cookies=cookies,
        timeout=HTTP_TIMEOUT
    )

    if not is_http_success(response.status_code):
        raise APIRequestError(
            url=api_url,
            method='GET',
            status_code=response.status_code,
            response_text=response.text[:200]
        )

    return response.json()

except APIRequestError as e:
    print(f'API 請求失敗:')
    print(f'  URL: {e.url}')
    print(f'  方法: {e.method}')
    print(f'  狀態碼: {e.status_code}')

    # 根據狀態碼處理
    if e.status_code == HTTP_UNAUTHORIZED:
        # 重新登入
        pass
    elif e.status_code >= 500:
        # 服務器錯誤，稍後重試
        pass
```

#### APITimeoutError

```python
from src.exceptions import APITimeoutError
from src.constants import HTTP_TIMEOUT, API_RETRY_DELAY
import requests

try:
    response = requests.get(api_url, timeout=HTTP_TIMEOUT)
except requests.Timeout:
    raise APITimeoutError(url=api_url, timeout=HTTP_TIMEOUT)
except APITimeoutError as e:
    print(f'API 超時 (URL: {e.url}, 超時: {e.timeout}秒)')
    time.sleep(API_RETRY_DELAY)
    # 重試
```

---

### 5. 掃描相關異常

#### CourseNotFoundError

```python
from src.exceptions import CourseNotFoundError

def find_course(course_name, course_list):
    """查找課程"""
    for course in course_list:
        if course['name'] == course_name:
            return course

    # 找不到課程
    raise CourseNotFoundError(course_name=course_name)

try:
    course = find_course('數學', courses)
except CourseNotFoundError as e:
    print(f'找不到課程: {e.course_name}')
    # 跳過或使用備選方案
```

#### PayloadNotFoundError

```python
from src.exceptions import PayloadNotFoundError
from src.constants import PAYLOAD_CAPTURE_WAIT

# 等待 Payload 捕獲
time.sleep(PAYLOAD_CAPTURE_WAIT)

payload = payload_interceptor.get_payload_by_course_id(course_id)
if not payload:
    raise PayloadNotFoundError(
        course_id=course_id,
        timeout=PAYLOAD_CAPTURE_WAIT
    )
```

---

### 6. 異常層次處理

```python
from src.exceptions import (
    EEBotError,
    ConfigError,
    AuthenticationError,
    APIError,
    ScanError
)

def batch_mode():
    """批量模式主函數"""
    try:
        # 配置階段
        config = load_config()

        # 登入階段
        login(config)

        # API 掃描階段
        api_courses = scan_api_courses()

        # Web 掃描階段
        scanned_courses = scan_web_courses(api_courses)

    except ConfigError as e:
        # 配置錯誤 - 檢查配置文件
        print(f'配置錯誤: {e}')
        print('請檢查 config/eebot.cfg 文件')

    except AuthenticationError as e:
        # 認證錯誤 - 檢查用戶名密碼
        print(f'認證錯誤: {e}')
        print('請檢查用戶名和密碼')

    except APIError as e:
        # API 錯誤 - 可能是網絡問題
        print(f'API 錯誤 (狀態碼: {e.status_code}): {e}')
        print('請檢查網絡連接或稍後重試')

    except ScanError as e:
        # 掃描錯誤 - 可能是頁面變化
        print(f'掃描錯誤: {e}')
        print('請檢查頁面元素是否變化')

    except EEBotError as e:
        # 其他 EEBot 錯誤
        print(f'EEBot 錯誤: {e}')
        error_dict = e.to_dict()
        print(f'錯誤類型: {error_dict["error_type"]}')
        print(f'詳情: {error_dict["details"]}')

    except Exception as e:
        # 未預期的錯誤
        print(f'未預期的錯誤: {e}')
        import traceback
        traceback.print_exc()
```

---

### 7. 異常工具函數

```python
from src.exceptions import handle_exception
import logging

logger = logging.getLogger('eebot')

try:
    # 執行操作
    ...
except Exception as e:
    # 統一處理異常
    error_info = handle_exception(e, logger.error)

    # error_info 包含:
    # {
    #     'error_type': 'LoginError',
    #     'message': '登入失敗: 驗證碼錯誤',
    #     'details': {'username': 'user123', 'retry_count': 2}
    # }

    # 保存錯誤信息
    save_error_log(error_info)
```

---

## 遷移指南

### 步驟 1: 替換魔術數字

**文件**: menu.py

#### 示例 1: HTTP 狀態碼

```python
# 修改前
if response.status_code == 200:
    ...

# 修改後
from src.constants import is_http_success

if is_http_success(response.status_code):
    ...
```

#### 示例 2: 延遲時間

```python
# 修改前
time.sleep(7)

# 修改後
from src.constants import DEFAULT_PAGE_LOAD_DELAY

time.sleep(DEFAULT_PAGE_LOAD_DELAY)
```

#### 示例 3: 時長計算

```python
# 修改前
need_seconds = (required_minutes * 60) + 10

# 修改後
from src.constants import BUFFER_SECONDS, minutes_to_seconds

need_seconds = minutes_to_seconds(required_minutes) + BUFFER_SECONDS
```

---

### 步驟 2: 替換異常

#### 示例 1: 配置錯誤

```python
# 修改前
if key not in config:
    raise Exception(f'缺少配置: {key}')

# 修改後
from src.exceptions import ConfigKeyMissingError

missing_keys = [k for k in REQUIRED_KEYS if k not in config]
if missing_keys:
    raise ConfigKeyMissingError(missing_keys)
```

#### 示例 2: API 錯誤

```python
# 修改前
if response.status_code != 200:
    raise Exception(f'API 錯誤: {response.status_code}')

# 修改後
from src.exceptions import APIRequestError
from src.constants import is_http_success

if not is_http_success(response.status_code):
    raise APIRequestError(
        url=api_url,
        status_code=response.status_code
    )
```

---

### 步驟 3: 改善錯誤處理

```python
# 修改前
try:
    # 執行操作
    ...
except Exception as e:
    print(f'錯誤: {e}')

# 修改後
from src.exceptions import (
    ConfigError,
    LoginError,
    APIError
)

try:
    # 執行操作
    ...
except ConfigError as e:
    # 配置錯誤的特定處理
    print(f'配置錯誤: {e}')
    create_default_config()
except LoginError as e:
    # 登入錯誤的特定處理
    print(f'登入失敗 (重試: {e.retry_count}): {e.reason}')
    retry_login()
except APIError as e:
    # API 錯誤的特定處理
    print(f'API 錯誤 (狀態碼: {e.status_code})')
    if e.status_code == 401:
        re_login()
    else:
        retry_request()
```

---

## 最佳實踐

### 1. 常量命名

✅ **推薦**:
- 使用 `UPPERCASE_WITH_UNDERSCORES`
- 名稱清楚表達意圖
- 添加註釋說明用途

```python
# ✅ 好的命名
DEFAULT_PAGE_LOAD_DELAY = 7  # 默認頁面加載等待時間（秒）
MAX_LOGIN_RETRIES = 3  # 最大登入重試次數
BUFFER_SECONDS = 10  # 發送時長的緩衝時間（秒）
```

❌ **不推薦**:
```python
# ❌ 不好的命名
DELAY = 7  # 太模糊
MAX_RETRY = 3  # 重試什麼？
BUFFER = 10  # 緩衝什麼？
```

---

### 2. 異常使用

✅ **推薦**:
- 使用最具體的異常類
- 提供詳細的錯誤信息
- 包含上下文信息

```python
# ✅ 好的用法
raise CourseNotFoundError(
    course_name='數學',
    course_id=465
)

raise APIRequestError(
    url='https://example.com/api/courses',
    method='GET',
    status_code=404
)
```

❌ **不推薦**:
```python
# ❌ 不好的用法
raise EEBotError('錯誤')  # 太泛泛
raise Exception('課程未找到')  # 不使用自定義異常
raise CourseNotFoundError()  # 缺少上下文
```

---

### 3. 錯誤處理順序

```python
# ✅ 正確順序：從具體到一般
try:
    ...
except ConfigKeyMissingError as e:  # 最具體
    ...
except ConfigValidationError as e:  # 較具體
    ...
except ConfigError as e:  # 一般
    ...
except EEBotError as e:  # 最一般
    ...
except Exception as e:  # 兜底
    ...
```

---

### 4. 常量分組

```python
# ✅ 相關常量分組導入
from src.constants import (
    # HTTP 相關
    HTTP_OK,
    HTTP_NO_CONTENT,
    is_http_success,

    # 延遲相關
    DEFAULT_PAGE_LOAD_DELAY,
    API_REQUEST_DELAY,

    # 重試相關
    MAX_LOGIN_RETRIES,
    LOGIN_RETRY_DELAY,
)
```

---

### 5. 文檔字符串

```python
# ✅ 添加清晰的文檔字符串
from src.constants import BUFFER_SECONDS

def calculate_duration(minutes: float) -> int:
    """
    計算需要發送的時長（秒）

    Args:
        minutes: 要求的分鐘數

    Returns:
        總秒數（包含緩衝時間）

    Note:
        自動添加 BUFFER_SECONDS (10秒) 確保超過最低要求
    """
    return int(minutes * 60) + BUFFER_SECONDS
```

---

## 總結

### 完成的工作

1. ✅ 創建 `src/constants.py`
   - 80+ 個常量
   - 5 個輔助函數
   - 完整的文檔字符串

2. ✅ 創建 `src/exceptions.py`
   - 28 個自定義異常類
   - 清晰的異常層次結構
   - 1 個異常處理工具函數

### 下一步

1. **立即行動**:
   - 在新代碼中使用這些模組
   - 逐步遷移現有代碼

2. **漸進式遷移**:
   - 從新功能開始使用
   - 修復 Bug 時順便遷移
   - 不強制一次性替換所有代碼

3. **持續改進**:
   - 發現新的魔術數字時添加到 constants.py
   - 遇到新的錯誤場景時添加到 exceptions.py

---

**文檔版本**: 1.0.0
**最後更新**: 2025-12-18
**維護者**: EEBot Development Team
