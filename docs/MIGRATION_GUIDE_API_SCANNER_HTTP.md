# API Scanner 與 HTTP 狀態碼統一遷移指南

**建立日期**: 2025-12-18
**版本**: 1.0.0

---

## 目錄
1. [概述](#概述)
2. [APIScanner 遷移](#apiscanner-遷移)
3. [HTTP 狀態碼統一](#http-狀態碼統一)
4. [遷移檢查清單](#遷移檢查清單)
5. [測試驗證](#測試驗證)

---

## 概述

本指南說明如何：
1. 使用新的 `APIScanner` 類替代重複的 API 掃描代碼
2. 使用 `is_http_success()` 統一所有 HTTP 狀態碼檢查

### 受影響的文件

| 文件 | 需要修改的位置 | 類型 |
|-----|---------------|------|
| menu.py | 10+ 處 | HTTP 狀態碼 + API 掃描 |
| src/api/visit_duration_api.py | 3 處 | HTTP 狀態碼 |

---

## APIScanner 遷移

### 1. 導入新模組

在文件開頭添加導入：

```python
# menu.py 開頭
from src.services.api_scanner import APIScanner, create_scanner_from_config
from src.constants import is_http_success
```

---

### 2. 替換重複的 API 掃描代碼

#### 位置 1: menu.py 行 1077-1107 (混合掃描模式)

**修改前** (❌ 重複代碼):
```python
# 階段 2: API 掃描 - 從 /api/my-courses 獲取課程 ID
print('\n' + '=' * 70)
print('[階段 2/6] API 掃描 - 獲取課程 ID')
print('-' * 70)

try:
    # 提取 Session Cookie
    print('\n提取 Session Cookie...')
    selenium_cookies = driver.get_cookies()
    session_cookie = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
    print('  ✓ Session Cookie 已提取')

    # 調用 /api/my-courses API
    print('\n調用 /api/my-courses API...')

    from urllib.parse import urlparse
    target_url = config.get('target_http')
    parsed = urlparse(target_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    api_url = f"{base_url}/api/my-courses"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-TW,zh;q=0.9',
        'Referer': base_url,
    }

    # 禁用 SSL 警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    response = requests.get(
        api_url,
        cookies=session_cookie,
        headers=headers,
        verify=False,
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        api_courses = data.get('courses', [])
        print(f'✓ 獲取成功，共 {len(api_courses)} 門課程')
    else:
        print(f'✗ API 請求失敗，狀態碼: {response.status_code}')
        raise Exception(f'API 請求失敗: {response.status_code}')

except Exception as e:
    print(f'✗ API 掃描失敗: {e}')
    if driver:
        driver.quit()
    input('\n按 Enter 返回主選單...')
    return
```

**修改後** (✅ 使用 APIScanner):
```python
# 階段 2: API 掃描 - 從 /api/my-courses 獲取課程 ID
print('\n' + '=' * 70)
print('[階段 2/6] API 掃描 - 獲取課程 ID')
print('-' * 70)

try:
    # 使用 APIScanner
    from src.services.api_scanner import create_scanner_from_config
    from src.exceptions import APIError

    print('\n調用 /api/my-courses API...')
    scanner = create_scanner_from_config(config)
    api_courses = scanner.scan_my_courses_from_driver(driver)

    # 打印摘要
    scanner.print_courses_summary(api_courses)

except APIError as e:
    print(f'✗ API 掃描失敗 (狀態碼: {e.status_code}): {e}')
    if driver:
        driver.quit()
    input('\n按 Enter 返回主選單...')
    return
except Exception as e:
    print(f'✗ API 掃描失敗: {e}')
    if driver:
        driver.quit()
    input('\n按 Enter 返回主選單...')
    return
```

**優勢**:
- ✅ 代碼從 40+ 行減少到 10 行
- ✅ 統一的錯誤處理
- ✅ 可讀性更高
- ✅ 易於測試

---

#### 位置 2: menu.py 行 2285-2343 (批量模式)

**修改方式相同**，替換為：

```python
# Stage 1A: API 掃描 - 獲取課程 ID
print('\n' + '-' * 70)
print('[Stage 1A] API 掃描 - 獲取課程 ID')
print('-' * 70)

api_courses = []
try:
    from src.services.api_scanner import create_scanner_from_config
    from src.exceptions import APIError

    print('\n調用 /api/my-courses API...')
    scanner = create_scanner_from_config(config)
    api_courses = scanner.scan_my_courses_from_driver(driver)

    scanner.print_courses_summary(api_courses)

except APIError as e:
    print(f'✗ API 掃描失敗 (狀態碼: {e.status_code}): {e}')
    if driver:
        driver.quit()
    if proxy_manager:
        proxy_manager.stop()
    input('\n按 Enter 返回主選單...')
    return
except Exception as e:
    print(f'✗ API 掃描失敗: {e}')
    if driver:
        driver.quit()
    if proxy_manager:
        proxy_manager.stop()
    input('\n按 Enter 返回主選單...')
    return
```

---

### 3. 替換課程 ID 匹配邏輯

#### 位置 3: menu.py 行 1419-1427 (混合掃描模式)

**修改前** (❌ 重複代碼):
```python
# 匹配 API 課程 ID
for api_course in api_courses:
    api_name = api_course.get('name', '')
    if api_name == program_name or api_name in program_name or program_name in api_name:
        program_data['api_course_id'] = api_course.get('id') or api_course.get('course_id')
        print(f'  ✓ 匹配到 API 課程 ID: {program_data["api_course_id"]}')
        break
```

**修改後** (✅ 使用 APIScanner 方法):
```python
# 匹配 API 課程 ID
api_course_id = scanner.match_course_id_by_name(program_name, api_courses)
if api_course_id:
    program_data['api_course_id'] = api_course_id
    print(f'  ✓ 匹配到 API 課程 ID: {api_course_id}')
```

**優勢**:
- ✅ 代碼從 7 行減少到 4 行
- ✅ 邏輯集中管理
- ✅ 易於測試和修改匹配策略

---

#### 位置 4: menu.py 行 2407-2421 (批量模式)

**修改方式相同**，替換為：

```python
# 步驟 2: 匹配 API 課程 ID（參考混合掃描模式）
print(f'  [2/3] 匹配 API 課程 ID...')
api_course_id = scanner.match_course_id_by_name(program_name, api_courses)

if not api_course_id:
    print(f'  ⚠️  無法匹配 API 課程 ID，跳過')
    driver.back()
    time.sleep(1.5)
    continue

print(f'  ✓ 匹配到 API 課程 ID: {api_course_id}')
```

---

## HTTP 狀態碼統一

### 需要修改的所有位置

#### menu.py

| 行號 | 當前代碼 | 修改後 |
|-----|---------|--------|
| 663 | `if response.status_code == 200:` | `if is_http_success(response.status_code):` |
| 1094 | `if response.status_code == 200:` | *使用 APIScanner 替代* |
| 1939 | `if response.status_code == 200:` | *使用 APIScanner 替代* |
| 2640 | `if response.status_code == 200:` | *使用 APIScanner 替代* |
| 2995 | `if 200 <= response.status_code < 300:` | ✅ 已正確（保持不變或改用函數） |
| 3225 | `if response.status_code == 200:` | `if is_http_success(response.status_code):` |
| 3310 | `if response.status_code == 200:` | `if is_http_success(response.status_code):` |
| 3566 | `if response.status_code == 200:` | `if is_http_success(response.status_code):` |
| 3656 | `if response.status_code == 200:` | `if is_http_success(response.status_code):` |
| 3945 | `if response.status_code == 200:` | `if is_http_success(response.status_code):` |

---

#### src/api/visit_duration_api.py

| 行號 | 當前代碼 | 修改後 |
|-----|---------|--------|
| 180 | `if response.status_code == 200:` | `if is_http_success(response.status_code):` |
| 240 | `if response.status_code == 200:` | `if is_http_success(response.status_code):` |
| 435 | `if response.status_code == 200:` | `if is_http_success(response.status_code):` |

---

### 統一修改示例

#### 示例 1: menu.py 行 663

**修改前**:
```python
response = requests.get(
    api_url,
    cookies=cookies,
    headers=headers,
    verify=False,
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    return data.get("activities", [])
else:
    print(f"  ✗ API 請求失敗，狀態碼: {response.status_code}")
    return []
```

**修改後**:
```python
from src.constants import is_http_success

response = requests.get(
    api_url,
    cookies=cookies,
    headers=headers,
    verify=False,
    timeout=30
)

if is_http_success(response.status_code):
    data = response.json()
    return data.get("activities", [])
else:
    print(f"  ✗ API 請求失敗，狀態碼: {response.status_code}")
    return []
```

---

#### 示例 2: src/api/visit_duration_api.py 行 180

**修改前**:
```python
response = requests.get(
    api_url,
    cookies=session_cookies,
    headers=headers,
    verify=False,
    timeout=10
)

if response.status_code == 200:
    data = response.json()
    return float(data.get('sum', 0))
```

**修改後**:
```python
from src.constants import is_http_success
from src.exceptions import APIRequestError

response = requests.get(
    api_url,
    cookies=session_cookies,
    headers=headers,
    verify=False,
    timeout=10
)

if is_http_success(response.status_code):
    data = response.json()
    return float(data.get('sum', 0))
else:
    raise APIRequestError(
        url=api_url,
        method='GET',
        status_code=response.status_code
    )
```

---

#### 示例 3: menu.py 行 2995 (已正確)

**當前代碼** (✅ 已正確):
```python
# HTTP 2xx 都視為成功（包括 200 OK 和 204 No Content）
if 200 <= response.status_code < 300:
    print(f"  ✓ 發送成功（HTTP {response.status_code}）")
```

**可選優化** (使用函數更清晰):
```python
from src.constants import is_http_success

# HTTP 2xx 都視為成功（包括 200 OK 和 204 No Content）
if is_http_success(response.status_code):
    print(f"  ✓ 發送成功（HTTP {response.status_code}）")
```

---

## 遷移檢查清單

### Phase 1: 準備工作

- [x] ✅ 創建 `src/constants.py`
- [x] ✅ 創建 `src/exceptions.py`
- [x] ✅ 創建 `src/services/api_scanner.py`
- [ ] 閱讀本遷移指南
- [ ] 備份當前代碼（創建 Git 分支）

### Phase 2: APIScanner 遷移

#### menu.py

- [ ] 在文件開頭添加導入
  ```python
  from src.services.api_scanner import APIScanner, create_scanner_from_config
  from src.constants import is_http_success
  from src.exceptions import APIError
  ```

- [ ] 替換混合掃描模式 API 掃描代碼 (行 1077-1107)
- [ ] 替換混合掃描模式課程 ID 匹配 (行 1419-1427)
- [ ] 替換批量模式 API 掃描代碼 (行 2285-2343)
- [ ] 替換批量模式課程 ID 匹配 (行 2407-2421)

#### 其他位置

- [ ] 檢查是否還有其他重複的 API 掃描代碼
- [ ] 使用 `scanner.match_course_id_by_name()` 替代所有匹配邏輯

### Phase 3: HTTP 狀態碼統一

#### menu.py

- [ ] 行 663: `if response.status_code == 200:` → `if is_http_success(response.status_code):`
- [ ] 行 1094: *已由 APIScanner 處理*
- [ ] 行 1939: *已由 APIScanner 處理*
- [ ] 行 2640: *已由 APIScanner 處理*
- [ ] 行 2995: (可選) 改用 `is_http_success()`
- [ ] 行 3225: `if response.status_code == 200:` → `if is_http_success(response.status_code):`
- [ ] 行 3310: `if response.status_code == 200:` → `if is_http_success(response.status_code):`
- [ ] 行 3566: `if response.status_code == 200:` → `if is_http_success(response.status_code):`
- [ ] 行 3656: `if response.status_code == 200:` → `if is_http_success(response.status_code):`
- [ ] 行 3945: `if response.status_code == 200:` → `if is_http_success(response.status_code):`

#### src/api/visit_duration_api.py

- [ ] 行 180: `if response.status_code == 200:` → `if is_http_success(response.status_code):`
- [ ] 行 240: `if response.status_code == 200:` → `if is_http_success(response.status_code):`
- [ ] 行 435: `if response.status_code == 200:` → `if is_http_success(response.status_code):`

### Phase 4: 測試驗證

- [ ] 運行混合掃描模式 (選項 i)
  - [ ] API 掃描階段成功
  - [ ] 課程 ID 匹配成功
  - [ ] 整體流程完成

- [ ] 運行批量模式 (選項 15)
  - [ ] Stage 1A API 掃描成功
  - [ ] Stage 1B Web 掃描成功
  - [ ] Stage 3 批量發送成功

- [ ] 測試其他功能
  - [ ] 檢查所有 API 請求
  - [ ] 驗證 HTTP 204 被正確處理
  - [ ] 確認錯誤處理正常

---

## 測試驗證

### 1. 單元測試 APIScanner

創建測試文件 `tests/test_api_scanner.py`:

```python
import pytest
from src.services.api_scanner import APIScanner
from src.exceptions import APIRequestError, APIResponseError

class TestAPIScanner:
    """APIScanner 單元測試"""

    def test_extract_cookies_from_driver(self, mock_driver):
        """測試從 WebDriver 提取 Cookie"""
        cookies = APIScanner.extract_cookies_from_driver(mock_driver)

        assert isinstance(cookies, dict)
        assert 'session_id' in cookies

    def test_match_course_id_by_name_exact_match(self):
        """測試完全匹配"""
        scanner = APIScanner('https://example.com')
        courses = [
            {'id': 465, 'name': '課程A'},
            {'id': 452, 'name': '課程B'}
        ]

        course_id = scanner.match_course_id_by_name('課程A', courses)
        assert course_id == 465

    def test_match_course_id_by_name_partial_match(self):
        """測試部分匹配"""
        scanner = APIScanner('https://example.com')
        courses = [
            {'id': 465, 'name': '性別平等工作法'},
            {'id': 452, 'name': '高齡客戶投保'}
        ]

        course_id = scanner.match_course_id_by_name('性別平等', courses)
        assert course_id == 465

    def test_match_course_id_by_name_not_found(self):
        """測試未找到"""
        scanner = APIScanner('https://example.com')
        courses = [
            {'id': 465, 'name': '課程A'}
        ]

        course_id = scanner.match_course_id_by_name('不存在的課程', courses)
        assert course_id is None
```

### 2. 集成測試

```python
def test_api_scanner_integration(driver, config):
    """集成測試：完整的 API 掃描流程"""
    from src.services.api_scanner import create_scanner_from_config

    # 創建掃描器
    scanner = create_scanner_from_config(config)

    # 掃描課程
    courses = scanner.scan_my_courses_from_driver(driver)

    # 驗證結果
    assert len(courses) > 0
    assert 'id' in courses[0]
    assert 'name' in courses[0]

    # 測試課程匹配
    course_id = scanner.match_course_id_by_name(courses[0]['name'], courses)
    assert course_id == courses[0]['id']
```

### 3. 手動測試步驟

1. **測試 API 掃描**
   ```bash
   python menu.py
   # 選擇 i (混合掃描模式)
   # 觀察 API 掃描輸出
   ```

   預期輸出：
   ```
   [階段 2/6] API 掃描 - 獲取課程 ID
   調用 /api/my-courses API...
   ✓ 獲取成功，共 7 門課程
   [1] 課程A (ID: 465)
   [2] 課程B (ID: 452)
   ...
   ```

2. **測試批量模式**
   ```bash
   python menu.py
   # 選擇 15 (批量模式)
   # 觀察各階段輸出
   ```

   預期輸出：
   ```
   [Stage 1A] API 掃描 - 獲取課程 ID
   ✓ 獲取成功，共 7 門課程

   [Stage 1B] Web 掃描 - 獲取子課程並捕獲 Payload
   【1/7】課程名稱...
     [2/3] 匹配 API 課程 ID...
     ✓ 匹配到 API 課程 ID: 465
   ```

3. **測試 HTTP 狀態碼**
   - 確認 HTTP 200 正常處理
   - 確認 HTTP 204 被識別為成功
   - 確認錯誤狀態碼被正確處理

---

## 效益總結

### 代碼量減少

| 位置 | 修改前行數 | 修改後行數 | 減少 |
|-----|-----------|-----------|------|
| 混合掃描 API 掃描 | 40+ | 10 | -75% |
| 批量模式 API 掃描 | 40+ | 10 | -75% |
| 課程 ID 匹配 (x2) | 7 x 2 = 14 | 4 x 2 = 8 | -43% |
| **總計** | **94+** | **28** | **-70%** |

### 質量提升

1. ✅ **消除重複代碼**: API 掃描邏輯統一管理
2. ✅ **統一錯誤處理**: 使用自定義異常
3. ✅ **提高可測試性**: APIScanner 易於單元測試
4. ✅ **改善可讀性**: 代碼意圖更清晰
5. ✅ **易於維護**: 修改只需一處
6. ✅ **支持 HTTP 204**: 正確處理所有 2xx 狀態碼

---

## 故障排除

### 問題 1: ImportError

**錯誤**:
```
ImportError: cannot import name 'APIScanner' from 'src.services.api_scanner'
```

**解決方案**:
確保 `src/services/__init__.py` 文件存在（可以為空）。

---

### 問題 2: APIRequestError

**錯誤**:
```
APIRequestError: API 請求失敗 (狀態碼: 401)
```

**解決方案**:
Session 已過期，需要重新登入。

---

### 問題 3: 課程 ID 匹配失敗

**錯誤**:
```
⚠️  無法匹配 API 課程 ID
```

**解決方案**:
1. 檢查課程名稱是否正確
2. 打印 `api_courses` 和 `program_name` 對比
3. 可能需要調整匹配邏輯

---

## 下一步

完成本遷移後，建議繼續：

1. **添加單元測試** (TODO #11)
   - 為 APIScanner 編寫測試
   - 測試覆蓋率 > 80%

2. **提取其他重複代碼** (TODO #2)
   - WebScanner
   - DurationSender

3. **改善錯誤處理** (TODO #4)
   - 所有 API 請求使用異常
   - 統一錯誤處理流程

---

**文檔版本**: 1.0.0
**最後更新**: 2025-12-18
**維護者**: EEBot Development Team
