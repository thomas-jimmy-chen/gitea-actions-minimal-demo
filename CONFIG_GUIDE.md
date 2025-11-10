# 配置說明文件

## config/eebot.cfg 配置項目說明

### 必要配置

```ini
# 目標網站 URL
target_http=https://elearn.post.gov.tw

# ChromeDriver 執行檔路徑（請使用絕對路徑）
execute_file=D:/chromedriver.exe

# Cookie 檔案名稱（儲存在 resource/cookies/ 目錄下）
cookies_file=cookies.json

# 登入帳號
user_name=your_username

# 登入密碼
password=your_password
```

### 可選配置

```ini
# 是否修改訪問時長（y=啟用, n=停用）
# 啟用後會使用 MitmProxy 攔截並增加訪問時長
modify_visits=y

# MitmProxy 是否靜音模式（y=靜音, n=顯示輸出）
silent_mitm=y

# 是否儲存 MitmProxy 日誌（y=儲存到 log 目錄, n=不儲存）
log_save=n

# MitmProxy 監聽地址
listen_host=127.0.0.1

# MitmProxy 監聽埠號
listen_port=8080

# 發生錯誤時是否保持瀏覽器開啟（y=保持開啟以便除錯, n=自動關閉）
# 預設為 n（自動關閉）
keep_browser_on_error=n
```

## 完整配置範例

### 範例 1：正常使用（錯誤時自動關閉瀏覽器）

```ini
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
keep_browser_on_error=n
```

### 範例 2：除錯模式（錯誤時保持瀏覽器開啟）

```ini
target_http=https://elearn.post.gov.tw
execute_file=D:/chromedriver.exe
cookies_file=cookies.json
user_name=your_username
password=your_password
modify_visits=y
silent_mitm=n
log_save=y
listen_host=127.0.0.1
listen_port=8080
keep_browser_on_error=y
```

### 範例 3：不使用 Proxy

```ini
target_http=https://elearn.post.gov.tw
execute_file=D:/chromedriver.exe
cookies_file=cookies.json
user_name=your_username
password=your_password
modify_visits=n
silent_mitm=y
log_save=n
listen_host=127.0.0.1
listen_port=8080
keep_browser_on_error=n
```

## 配置項目詳細說明

### keep_browser_on_error 行為說明

**設定為 n（預設）：**
- 當程式執行過程中發生錯誤時，瀏覽器會立即自動關閉
- 適合正常使用場景
- 不需要手動按 Ctrl+C

**設定為 y：**
- 當程式執行過程中發生錯誤時，瀏覽器會保持開啟
- 可以檢查錯誤發生時的頁面狀態
- 適合除錯場景
- 需要手動按 Ctrl+C 來關閉程式

### modify_visits 說明

- 設定為 y：啟動 MitmProxy 攔截 API 請求，並增加 visit_duration 值
- 設定為 n：不使用 Proxy，直接連線到目標網站

### silent_mitm 說明

- 設定為 y：MitmProxy 的輸出會被隱藏（靜音模式）
- 設定為 n：顯示 MitmProxy 的所有輸出訊息

### log_save 說明

- 設定為 y：MitmProxy 的輸出會儲存到 log/mitm_YYYYMMDDHHMMSS.log
- 設定為 n：不儲存日誌檔案

## 常見問題

### Q1：程式發生錯誤後卡在「Keeping browser open」，需要按 Ctrl+C 才能關閉？

**A1：** 這是因為 `keep_browser_on_error` 設定為 `y`。請將其改為 `n` 或完全移除該行（預設為 n）。

### Q2：想要在錯誤時檢查瀏覽器狀態該如何設定？

**A2：** 將 `keep_browser_on_error=y` 加入配置檔即可。程式發生錯誤時會保持瀏覽器開啟，方便檢查問題。

### Q3：如何完全停用 MitmProxy？

**A3：** 將 `modify_visits=n` 設定即可，程式會跳過 Proxy 啟動步驟。

### Q4：配置檔的編碼格式？

**A4：** 建議使用 UTF-8 with BOM (utf-8-sig) 編碼，以確保中文正常顯示。

## 注意事項

1. ChromeDriver 路徑必須使用正斜線（/）或雙反斜線（\\\\），不能使用單反斜線（\\）
   - 正確：`D:/chromedriver.exe` 或 `D:\\\\chromedriver.exe`
   - 錯誤：`D:\chromedriver.exe`

2. 帳號密碼如果包含特殊字元（如 =），需要用引號包起來
   - 範例：`password="pass=word123"`

3. 布林值設定只認 `y` 和 `n`（不分大小寫）
   - 正確：`modify_visits=y` 或 `modify_visits=Y`
   - 錯誤：`modify_visits=true` 或 `modify_visits=yes`
