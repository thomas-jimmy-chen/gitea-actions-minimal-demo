# EEBot 配置管理指南

> **完整的配置管理最佳實踐指南**
>
> 版本: 1.0 | 更新日期: 2025-11-29 | 適用版本: v2.0.7+

---

## 目錄

- [快速開始](#快速開始)
- [配置來源與優先級](#配置來源與優先級)
- [環境變數配置](#環境變數配置)
- [配置檔案 (eebot.cfg)](#配置檔案-eebotcfg)
- [CLI 配置工具](#cli-配置工具)
- [配置項目說明](#配置項目說明)
- [安全最佳實踐](#安全最佳實踐)
- [常見問題排查](#常見問題排查)
- [遷移指南](#遷移指南)

---

## 快速開始

### 方法 1: 使用 CLI 配置工具 (推薦)

```bash
# Step 1: 安裝依賴
pip install -r requirements.txt

# Step 2: 初始化環境變數檔案
python setup.py init

# Step 3: 設定帳號密碼
python setup.py set username
python setup.py set password

# Step 4: 驗證配置
python setup.py validate

# Step 5: 執行 EEBot
python main.py
```

---

### 方法 2: 手動編輯 .env 檔案

```bash
# Step 1: 複製範本
cp .env.example .env

# Step 2: 編輯 .env 填入帳號密碼
# (使用任何文字編輯器)

# Step 3: 執行 EEBot
python main.py
```

---

## 配置來源與優先級

EEBot 支援多種配置來源，優先級由高到低:

```
1. 環境變數 (.env 檔案或系統環境變數)  [最高優先級]
   ↓
2. 配置檔案 (config/eebot.cfg)
   ↓
3. 程式預設值                          [最低優先級]
```

### 優先級範例

假設同時存在以下配置:

**`.env`**:
```bash
EEBOT_USERNAME=user_from_env
```

**`config/eebot.cfg`**:
```ini
user_name=user_from_cfg
```

**實際使用**: `user_from_env` (環境變數優先)

---

## 環境變數配置

### 為什麼使用環境變數?

**優點**:
- ✅ **安全性**: 敏感資料不會被提交到 Git
- ✅ **靈活性**: 不同環境使用不同配置 (開發/測試/生產)
- ✅ **業界標準**: 符合 12-Factor App 最佳實踐
- ✅ **容器化友善**: 易於整合 Docker, Kubernetes

---

### .env 檔案結構

**檔案位置**: `D:\Dev\eebot\.env`

**範例內容**:
```bash
# ======================================================================
# EEBot 環境變數配置
# ======================================================================

# ----------------------------------------------------------------------
# 認證資訊 (必填)
# ----------------------------------------------------------------------
EEBOT_USERNAME=your_username
EEBOT_PASSWORD=your_password

# ----------------------------------------------------------------------
# 代理伺服器設定 (選填)
# ----------------------------------------------------------------------
EEBOT_PROXY_HOST=127.0.0.1
EEBOT_PROXY_PORT=8080

# ----------------------------------------------------------------------
# 瀏覽器設定 (選填)
# ----------------------------------------------------------------------
EEBOT_CHROMEDRIVER_PATH=D:/chromedriver.exe
EEBOT_HEADLESS_MODE=n
EEBOT_KEEP_BROWSER_ON_ERROR=n

# ----------------------------------------------------------------------
# 進階設定 (選填)
# ----------------------------------------------------------------------
EEBOT_TARGET_URL=https://elearn.post.gov.tw
EEBOT_MODIFY_VISITS=y
EEBOT_SILENT_MITM=y
EEBOT_ANSWER_CONFIDENCE_THRESHOLD=0.85
EEBOT_AUTO_SUBMIT_EXAM=n
EEBOT_SCREENSHOT_ON_MISMATCH=y
```

---

### 環境變數命名規則

**格式**: `EEBOT_<配置鍵名大寫>`

**映射表**:

| 配置檔案鍵名 (eebot.cfg) | 環境變數名稱 | 說明 |
|-------------------------|-------------|------|
| `user_name` | `EEBOT_USERNAME` | 登入帳號 |
| `password` | `EEBOT_PASSWORD` | 登入密碼 |
| `target_http` | `EEBOT_TARGET_URL` | 目標網站 URL |
| `execute_file` | `EEBOT_CHROMEDRIVER_PATH` | ChromeDriver 路徑 |
| `headless_mode` | `EEBOT_HEADLESS_MODE` | 是否無頭模式 (y/n) |
| `modify_visits` | `EEBOT_MODIFY_VISITS` | 是否修改訪問時長 (y/n) |

完整映射表見 `src/core/config_loader.py:38-68`

---

### Git 安全保護

**.env 檔案已被 Git 忽略** (不會被提交到版本控制):

**`.gitignore`** 包含:
```gitignore
# 環境變數與敏感資料
.env                    # 實際環境變數檔案
.env.local
.env.*.local
```

**安全檢查**:
```bash
# 確認 .env 不會被提交
git status

# 應顯示: nothing to commit (或不包含 .env)
```

---

## 配置檔案 (eebot.cfg)

### 檔案位置

`D:\Dev\eebot\config\eebot.cfg`

---

### 適用場景

建議將以下配置保留在 `eebot.cfg`:
- ✅ **非敏感配置**: 目標網站 URL、ChromeDriver 路徑
- ✅ **功能開關**: 是否啟用截圖、是否使用代理
- ✅ **預設值**: 延遲時間、端口號

**不建議** 在此檔案儲存:
- ❌ 帳號密碼 (使用 `.env` 代替)
- ❌ API 金鑰 (使用 `.env` 代替)

---

### 範例配置

```ini
# ======================================================================
# EEBot 主配置檔案
# ======================================================================
# 注意: 敏感資料 (帳號密碼) 請使用 .env 檔案
# ======================================================================

[SETTINGS]
target_http=https://elearn.post.gov.tw
execute_file=D:/chromedriver.exe
modify_visits=y
silent_mitm=y
keep_browser_on_error=n

[BROWSER]
headless_mode=n

[PROXY]
listen_host=127.0.0.1
listen_port=8080

[AUTO_ANSWER]
enable_auto_answer=y
question_bank_mode=file_mapping
answer_confidence_threshold=0.85
auto_submit_exam=n
screenshot_on_mismatch=y
skip_unmatched_questions=y
```

**注意**: INI 格式不支援分段，ConfigLoader 會自動忽略 `[SECTION]` 標籤

---

## CLI 配置工具

### 安裝依賴

```bash
pip install python-dotenv
```

---

### 指令列表

| 指令 | 功能 | 範例 |
|------|------|------|
| `init` | 初始化 .env 檔案 | `python setup.py init` |
| `set username` | 設定帳號 | `python setup.py set username` |
| `set password` | 設定密碼 (隱藏輸入) | `python setup.py set password` |
| `show` | 顯示當前配置 (密碼遮蔽) | `python setup.py show` |
| `validate` | 驗證配置完整性 | `python setup.py validate` |
| `help` | 顯示使用說明 | `python setup.py help` |

---

### 使用範例

#### 1. 初始化配置

```bash
$ python setup.py init

======================================================================
 初始化環境變數配置檔案
======================================================================

✓ .env 檔案已建立

下一步:
  1. 執行: python setup.py set username
  2. 執行: python setup.py set password
  3. 或直接編輯 .env 檔案設定您的帳號密碼
```

---

#### 2. 設定帳號

```bash
$ python setup.py set username

======================================================================
 設定帳號
======================================================================

請輸入帳號: your_username
✓ 帳號已設定完成
設定儲存於: .env (已被 Git 忽略)
```

---

#### 3. 設定密碼

```bash
$ python setup.py set password

======================================================================
 設定密碼
======================================================================

請輸入密碼 (輸入時不顯示):
請再次輸入密碼確認:
✓ 密碼已設定完成
設定儲存於: .env (已被 Git 忽略)
```

---

#### 4. 驗證配置

```bash
$ python setup.py validate

======================================================================
 驗證配置完整性
======================================================================

檢查必填欄位:
✓   EEBOT_USERNAME: 已設定
✓   EEBOT_PASSWORD: 已設定

檢查配置檔案:
✓   config/eebot.cfg: 存在

檢查依賴套件:
✓   python-dotenv: 已安裝

======================================================================
✓ 配置驗證通過！

您可以執行以下指令啟動 EEBot:
  python menu.py    # 互動式選單
  python main.py    # 直接執行
======================================================================
```

---

#### 5. 顯示配置

```bash
$ python setup.py show

======================================================================
[配置摘要] EEBot Configuration Summary
======================================================================

[ENV ] password                        = ***
[ENV ] user_name                       = ***
[FILE] target_http                     = https://elearn.post.gov.tw
[FILE] execute_file                    = D:/chromedriver.exe
[FILE] modify_visits                   = y
[FILE] silent_mitm                     = y
[ENV ] headless_mode                   = n

======================================================================
```

**標籤說明**:
- `[ENV]`: 來自環境變數 (.env)
- `[FILE]`: 來自配置檔案 (eebot.cfg)
- `***`: 敏感資料已遮蔽

---

## 配置項目說明

### 認證資訊

| 配置鍵 | 環境變數 | 類型 | 必填 | 預設值 | 說明 |
|--------|---------|------|-----|--------|------|
| `user_name` | `EEBOT_USERNAME` | String | ✅ | 無 | 登入帳號 |
| `password` | `EEBOT_PASSWORD` | String | ✅ | 無 | 登入密碼 |

**安全建議**: 使用 `.env` 檔案儲存，不要提交到 Git

---

### 網站與路徑

| 配置鍵 | 環境變數 | 類型 | 必填 | 預設值 | 說明 |
|--------|---------|------|-----|--------|------|
| `target_http` | `EEBOT_TARGET_URL` | String | ❌ | `https://elearn.post.gov.tw` | 目標網站 URL |
| `execute_file` | `EEBOT_CHROMEDRIVER_PATH` | String | ❌ | (自動搜尋 PATH) | ChromeDriver 路徑 |

---

### 代理伺服器

| 配置鍵 | 環境變數 | 類型 | 必填 | 預設值 | 說明 |
|--------|---------|------|-----|--------|------|
| `listen_host` | `EEBOT_PROXY_HOST` | String | ❌ | `127.0.0.1` | MitmProxy 監聽位址 |
| `listen_port` | `EEBOT_PROXY_PORT` | Integer | ❌ | `8080` | MitmProxy 監聽端口 |
| `modify_visits` | `EEBOT_MODIFY_VISITS` | Boolean | ❌ | `y` | 是否修改訪問時長 |
| `silent_mitm` | `EEBOT_SILENT_MITM` | Boolean | ❌ | `y` | MitmProxy 靜默模式 |

---

### 瀏覽器設定

| 配置鍵 | 環境變數 | 類型 | 必填 | 預設值 | 說明 |
|--------|---------|------|-----|--------|------|
| `headless_mode` | `EEBOT_HEADLESS_MODE` | Boolean | ❌ | `n` | 是否無頭模式 (無 GUI) |
| `keep_browser_on_error` | `EEBOT_KEEP_BROWSER_ON_ERROR` | Boolean | ❌ | `n` | 錯誤時保持瀏覽器開啟 |

---

### 自動答題

| 配置鍵 | 環境變數 | 類型 | 必填 | 預設值 | 說明 |
|--------|---------|------|-----|--------|------|
| `enable_auto_answer` | `EEBOT_ENABLE_AUTO_ANSWER` | Boolean | ❌ | `y` | 是否啟用自動答題 |
| `question_bank_mode` | `EEBOT_QUESTION_BANK_MODE` | String | ❌ | `file_mapping` | 題庫模式 |
| `answer_confidence_threshold` | `EEBOT_ANSWER_CONFIDENCE_THRESHOLD` | Float | ❌ | `0.85` | 答案信心門檻 (0.0-1.0) |
| `auto_submit_exam` | `EEBOT_AUTO_SUBMIT_EXAM` | Boolean | ❌ | `n` | 是否自動提交考試 |
| `screenshot_on_mismatch` | `EEBOT_SCREENSHOT_ON_MISMATCH` | Boolean | ❌ | `y` | 未匹配題目截圖 |

---

### 布林值格式

支援多種格式 (不區分大小寫):

| True | False |
|------|-------|
| `y`, `yes`, `true`, `1` | `n`, `no`, `false`, `0` |

**範例**:
```bash
EEBOT_HEADLESS_MODE=y        # True
EEBOT_HEADLESS_MODE=yes      # True
EEBOT_HEADLESS_MODE=true     # True
EEBOT_HEADLESS_MODE=1        # True
EEBOT_HEADLESS_MODE=n        # False
```

---

## 安全最佳實踐

### 1. 使用 .env 儲存敏感資料

**推薦做法**:
```bash
# .env (不提交到 Git)
EEBOT_USERNAME=your_username
EEBOT_PASSWORD=your_password
```

**不推薦**:
```ini
# config/eebot.cfg (會被提交到 Git)
user_name=your_username  # ❌ 不安全！
password=your_password   # ❌ 不安全！
```

---

### 2. 檢查 .gitignore

確保以下規則存在:
```gitignore
.env
.env.local
.env.*.local
```

驗證:
```bash
git check-ignore .env
# 應輸出: .env
```

---

### 3. 不要提交 .env 到 Git

**如果不小心提交了**:
```bash
# 從 Git 歷史中移除 (危險操作!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 強制推送 (會改寫歷史記錄)
git push origin --force --all
```

**更安全的做法**: 立即修改密碼，重新生成 .env

---

### 4. 使用強密碼

**推薦密碼強度**:
- 長度 ≥ 12 字元
- 包含大小寫字母、數字、符號
- 不使用常見單字或模式

---

### 5. 定期輪換密碼

建議每 3-6 個月更新一次密碼:
```bash
python setup.py set password
```

---

## 常見問題排查

### Q1: .env 檔案不生效

**症狀**: 設定了 .env，但程式仍使用 eebot.cfg 的值

**排查步驟**:
1. 檢查 python-dotenv 是否安裝:
   ```bash
   pip list | grep dotenv
   # 應顯示: python-dotenv x.x.x
   ```

2. 檢查 .env 檔案位置:
   ```bash
   # 應位於專案根目錄
   D:\Dev\eebot\.env
   ```

3. 檢查環境變數名稱是否正確:
   ```bash
   # 正確格式: EEBOT_USERNAME
   # 錯誤格式: EEBOT_USER_NAME, username, USER_NAME
   ```

4. 重新啟動程式 (環境變數需重新載入)

---

### Q2: 啟動時顯示「.env 檔案不存在」

**解決方案**:
```bash
# 方法 1: 使用 CLI 工具
python setup.py init

# 方法 2: 手動複製
cp .env.example .env
```

---

### Q3: 設定密碼後仍顯示「未設定」

**檢查 .env 格式**:
```bash
# 正確格式 (無空格、無引號)
EEBOT_PASSWORD=your_password

# 錯誤格式
EEBOT_PASSWORD = your_password   # ❌ 等號兩側有空格
EEBOT_PASSWORD="your_password"   # ❌ 有引號 (會包含引號字元)
```

**重新設定**:
```bash
python setup.py set password
```

---

### Q4: 帳號密碼正確但登入失敗

**排查步驟**:
1. 確認網站 URL 正確:
   ```bash
   python setup.py show
   # 檢查 target_http
   ```

2. 手動測試登入 (瀏覽器)

3. 檢查是否有特殊字元需要轉義

4. 查看錯誤日誌:
   ```bash
   python main.py 2>&1 | tee debug.log
   ```

---

### Q5: Windows 中文路徑問題

**症狀**: ChromeDriver 路徑包含中文導致錯誤

**解決方案**:
```bash
# .env
# 使用斜線 (/) 而非反斜線 (\)
EEBOT_CHROMEDRIVER_PATH=D:/工具/chromedriver.exe

# 或使用短路徑名 (8.3 格式)
EEBOT_CHROMEDRIVER_PATH=D:/PROGRA~1/chromedriver.exe
```

---

## 遷移指南

### 從舊版 (v2.0.6 及之前) 遷移到 v2.0.7

#### Step 1: 備份現有配置

```bash
# 備份 eebot.cfg
cp config/eebot.cfg config/eebot.cfg.backup
```

---

#### Step 2: 安裝新依賴

```bash
pip install -r requirements.txt
```

---

#### Step 3: 建立 .env 檔案

```bash
# 方法 1: 使用 CLI 工具 (推薦)
python setup.py init
python setup.py set username
python setup.py set password

# 方法 2: 手動建立
cp .env.example .env
# 編輯 .env 填入帳號密碼
```

---

#### Step 4: 遷移敏感資料

**從 eebot.cfg 提取帳號密碼**:
```bash
# 查看舊配置
grep -E "user_name|password" config/eebot.cfg

# 設定到 .env
python setup.py set username
python setup.py set password
```

---

#### Step 5: 清理 eebot.cfg 中的敏感資料

**編輯 `config/eebot.cfg`，移除以下行**:
```ini
user_name=...    # 刪除此行
password=...     # 刪除此行
```

保留其他非敏感配置即可

---

#### Step 6: 驗證配置

```bash
python setup.py validate

# 測試執行
python main.py
```

---

#### Step 7: 確認 Git 安全

```bash
# 確認 .env 不會被提交
git status
# .env 應不出現在列表中

# 確認 .gitignore 包含 .env
cat .gitignore | grep "^\.env$"
```

---

### 向後相容性

**完全向後相容**:
- ✅ 舊版 `eebot.cfg` 仍然有效
- ✅ 不使用 `.env` 也能正常運作
- ✅ 無破壞性變更

**建議升級原因**:
- ✅ 提升安全性 (敏感資料不提交到 Git)
- ✅ 更符合業界標準 (12-Factor App)
- ✅ 更易於部署到不同環境

---

## 附錄

### A. 完整環境變數列表

| 環境變數 | 對應配置鍵 | 說明 |
|---------|-----------|------|
| `EEBOT_USERNAME` | `user_name` | 登入帳號 |
| `EEBOT_PASSWORD` | `password` | 登入密碼 |
| `EEBOT_TARGET_URL` | `target_http` | 目標網站 URL |
| `EEBOT_CHROMEDRIVER_PATH` | `execute_file` | ChromeDriver 路徑 |
| `EEBOT_PROXY_HOST` | `listen_host` | 代理監聽位址 |
| `EEBOT_PROXY_PORT` | `listen_port` | 代理監聽端口 |
| `EEBOT_HEADLESS_MODE` | `headless_mode` | 無頭模式 |
| `EEBOT_KEEP_BROWSER_ON_ERROR` | `keep_browser_on_error` | 錯誤保持瀏覽器 |
| `EEBOT_MODIFY_VISITS` | `modify_visits` | 修改訪問時長 |
| `EEBOT_SILENT_MITM` | `silent_mitm` | MitmProxy 靜默模式 |
| `EEBOT_ENABLE_AUTO_ANSWER` | `enable_auto_answer` | 啟用自動答題 |
| `EEBOT_QUESTION_BANK_MODE` | `question_bank_mode` | 題庫模式 |
| `EEBOT_ANSWER_CONFIDENCE_THRESHOLD` | `answer_confidence_threshold` | 答案信心門檻 |
| `EEBOT_AUTO_SUBMIT_EXAM` | `auto_submit_exam` | 自動提交考試 |
| `EEBOT_SCREENSHOT_ON_MISMATCH` | `screenshot_on_mismatch` | 未匹配題目截圖 |
| `EEBOT_SKIP_UNMATCHED_QUESTIONS` | `skip_unmatched_questions` | 跳過未匹配題目 |

完整映射表見 `src/core/config_loader.py:38-68`

---

### B. 檔案結構

```
eebot/
├── .env                           # 環境變數 (實際配置，Git ignore)
├── .env.example                   # 環境變數範本 (可提交 Git)
├── .gitignore                     # Git 忽略規則
├── setup.py                       # CLI 配置工具
├── requirements.txt               # Python 依賴 (含 python-dotenv)
├── config/
│   └── eebot.cfg                  # 配置檔案 (非敏感配置)
├── src/
│   └── core/
│       └── config_loader.py       # 配置載入器 (支援環境變數)
└── docs/
    └── CONFIGURATION_MANAGEMENT_GUIDE.md  # 本文檔
```

---

### C. 相關文檔

- **交接指南**: [CLAUDE_CODE_HANDOVER-1.md](./CLAUDE_CODE_HANDOVER-1.md)
- **AI 助手指南**: [AI_ASSISTANT_GUIDE-1.md](./AI_ASSISTANT_GUIDE-1.md)
- **變更日誌**: [CHANGELOG.md](./CHANGELOG.md)
- **分段規則**: [DOCUMENT_SEGMENTATION_RULES.md](./DOCUMENT_SEGMENTATION_RULES.md)

---

### D. 聯絡與回饋

**問題回報**:
- 建立 Issue 或直接修改文檔

**改進建議**:
- 歡迎提交 Pull Request

---

**文檔版本**: 1.0
**最後更新**: 2025-11-29
**維護者**: wizard03
**專案**: EEBot (Gleipnir)

---

**Happy Configuring!**
