# 工作日誌 - Windows 兼容性修復

**日期**: 2025-12-06
**版本**: v2.0.8 (開發中)
**負責人**: Claude Code (Sonnet 4.5)
**協作**: wizard03

---

## 📋 工作概述

本次工作主要解決 EEBot 在 Windows 環境下的兼容性問題，包括：
1. Stealth.min.js 下載失敗
2. MitmProxy 無法啟動（multiprocessing + asyncio 兼容性）
3. 靜默模式無效（顯示大量 HTTP 請求日誌）

經過多次迭代和測試，最終成功修復所有問題。

---

## 🐛 問題診斷

### 問題 1: Stealth.min.js 下載失敗

**錯誤訊息**:
```
[WARN] stealth mode file not found, attempting to extract...
[ERROR] Failed to extract stealth mode file: [WinError 2] 系統找不到指定的檔案。
```

**根本原因**:
- Windows 下 `subprocess.run(['npx', ...])` 無法找到 `npx.cmd`
- 需要通過 shell 來執行

**影響檔案**:
- `src/core/driver_manager.py`
- `src/utils/stealth_extractor.py`

---

### 問題 2: MitmProxy 無法啟動

**錯誤訊息**:
```
net::ERR_PROXY_CONNECTION_FAILED
[WARN] Network monitoring may not be ready (port not listening)
```

**根本原因**:
- Windows + Python 3.13.5 環境下
- `multiprocessing.Process` + `asyncio` 事件循環無法正確啟動
- Windows 使用 spawn 模式啟動子進程，asyncio 循環無法正確傳遞

**影響檔案**:
- `src/core/proxy_manager.py`

---

### 問題 3: 靜默模式無效

**現象**:
```
127.0.0.1:11856: GET http://clients2.google.com/time/1/current?...
127.0.0.1:3985: GET https://www.google.com/async/folae?...
[大量 HTTP 請求日誌...]
```

**根本原因**:
- DumpMaster 包含 TermLog 和 Dumper addons，專門用於輸出流量
- Python logging 配置無法抑制 DumpMaster 的直接 stdout 輸出
- 嘗試重定向 sys.stdout 失敗（threading 中 sys.stdout 是全局的）

---

## 🔧 修復過程

### 階段 1: Subprocess Shell 修復

**修改檔案**: `src/core/driver_manager.py`, `src/utils/stealth_extractor.py`

**修改內容**:
```python
import platform

use_shell = platform.system() == 'Windows'

subprocess.run(
    ['npx', 'extract-stealth-evasions'],
    shell=use_shell,  # Windows 下使用 shell
    timeout=60
)
```

**結果**: ✅ stealth.min.js 成功下載

---

### 階段 2: MitmProxy Threading 遷移 (v2.0.2)

**修改檔案**: `src/core/proxy_manager.py`

**核心變更**:
```python
# v2.0.1 (原版 - Windows 下失敗)
from multiprocessing import Process
self.process = Process(target=self._run)
self.process.start()

# v2.0.2 (新版 - Windows 兼容)
import threading
self.thread = threading.Thread(target=self._run, daemon=True)
self.thread.start()
```

**額外修改**:
1. 添加端口健康檢查 `_check_port_listening()`
2. 增加初始等待時間（1s → 3s）
3. 保留原始代碼為詳細註解

**備份文件**: `src/core/proxy_manager.py.multiprocessing.bak`

**結果**: ✅ MitmProxy 成功啟動並監聽端口

---

### 階段 3: 靜默模式修復 (多次迭代)

#### 嘗試 1: Python Logging 配置 (v2.0.2)
```python
logging.getLogger("mitmproxy").setLevel(logging.CRITICAL)
```
**結果**: ❌ 無效（DumpMaster 直接寫入 stdout）

---

#### 嘗試 2: MitmOptions 參數 (v2.0.3)
```python
opts = MitmOptions(
    listen_host=self.host,
    listen_port=self.port,
    termlog_verbosity='error',
    flow_detail=0,
    quiet=True
)
```
**結果**: ❌ KeyError（當前 mitmproxy 版本不支援這些參數）

---

#### 嘗試 3: 使用 Master 類代替 DumpMaster (v2.0.4)
```python
# DumpMaster 有 36 個 addons（包括 ProxyServer）
# Master 有 0 個 addons
master = Master(opts)  # 無輸出但也無功能
```

**測試結果**:
```
Master has 0 addons          ← 沒有 ProxyServer
DumpMaster has 36 addons     ← 包含 ProxyServer
Port NOT listening           ← Master 無法監聽端口
```

**結果**: ❌ Master 無 ProxyServer addon，無法監聽端口

---

#### 嘗試 4: 線程內部重定向 stdout (v2.0.5)
```python
def _run(self):
    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')  # 重定向
    ...
    sys.stdout = old_stdout  # 恢復
```

**問題**:
- Python threading 中 `sys.stdout` 是全局共享的
- 線程修改 sys.stdout 會影響主線程
- 導致主線程所有輸出都被重定向到 /dev/null

**結果**: ❌ 程式卡住，主線程無法輸出

---

#### 成功方案: 移除輸出 Addons (v2.0.6) ✅

**關鍵發現**:
```
DumpMaster addons:
 1. TermLog      ← 終端日誌輸出
33. Dumper       ← 流量轉儲輸出
17. Proxyserver  ← 必要（監聽端口）
```

**最終方案**:
```python
master = DumpMaster(opts)

if self.silent:
    # 移除 TermLog addon（終端日誌）
    for addon in master.addons.chain:
        if type(addon).__name__ == 'TermLog':
            master.addons.remove(addon)
            break

    # 移除 Dumper addon（流量轉儲）
    for addon in master.addons.chain:
        if type(addon).__name__ == 'Dumper':
            master.addons.remove(addon)
            break
```

**優勢**:
- ✅ 保留 DumpMaster 的所有功能（包括 ProxyServer）
- ✅ 抑制所有流量日誌輸出
- ✅ 不影響主線程
- ✅ 代碼簡潔且線程安全

**結果**: ✅ 完美解決靜默模式問題

---

### 階段 4: Chrome 靜默模式

**修改檔案**: `src/core/driver_manager.py`

**新增配置**:
```python
silent_mode = self.config.get_bool('silent_mitm', False)
if silent_mode:
    opts.add_argument('--log-level=3')     # 只顯示 FATAL 錯誤
    opts.add_argument('--disable-logging')  # 禁用日誌
    opts.add_experimental_option('excludeSwitches',
        ['enable-automation', 'enable-logging'])
```

**抑制的訊息**:
- `DevTools listening on ws://...`
- Chrome 內部錯誤訊息
- TensorFlow 訊息

**結果**: ✅ Chrome 日誌已抑制

---

## 📝 修改總結

### 修改的檔案

| 檔案 | 變更類型 | 說明 |
|------|---------|------|
| `src/core/proxy_manager.py` | 重大重構 | multiprocessing → threading，移除輸出 addons |
| `src/core/driver_manager.py` | 功能增強 | Windows subprocess 修復，Chrome 靜默模式 |
| `src/utils/stealth_extractor.py` | Bug 修復 | Windows subprocess 修復 |

### 新增的檔案

| 檔案 | 類型 | 說明 |
|------|------|------|
| `src/core/proxy_manager.py.multiprocessing.bak` | 備份 | v2.0.1 原始版本備份 |

### 刪除的檔案

| 檔案 | 原因 |
|------|------|
| `nul` | v2.0.5 誤創建的文件（stdout 重定向測試） |

---

## 🧪 測試與驗證

### 測試環境
- **作業系統**: Windows 10/11
- **Python**: 3.13.5
- **Conda 環境**: eebot
- **Chrome 版本**: 143.0.7499.41

### 測試項目

#### 1. Stealth.min.js 下載
- [x] 首次執行自動下載
- [x] 下載成功訊息顯示
- [x] 文件存在於 `resource/plugins/stealth.min.js`

#### 2. MitmProxy 啟動
- [x] 端口成功監聽 (8080)
- [x] 健康檢查通過
- [x] 線程正常運行

#### 3. 靜默模式
- [x] 無 HTTP 請求日誌
- [x] 無 Chrome DevTools 訊息
- [x] 無 Chrome 內部錯誤
- [x] 主線程訊息正常顯示

#### 4. 功能驗證
- [ ] 完整課程執行（待測試）
- [ ] 訪問時長攔截（待測試）
- [ ] 自動答題（待測試）

---

## 📚 技術總結

### 學習要點

#### 1. Windows Subprocess 處理
```python
# Windows 需要 shell=True 來找到 .cmd 文件
import platform
use_shell = platform.system() == 'Windows'
subprocess.run(['npx', 'command'], shell=use_shell)
```

#### 2. Python Threading vs Multiprocessing
| 特性 | threading | multiprocessing |
|------|-----------|----------------|
| **全局狀態** | 共享（sys.stdout 等） | 獨立 |
| **Windows 兼容** | ✅ 良好 | ⚠️ spawn 模式有問題 |
| **asyncio 支援** | ✅ 良好 | ⚠️ 需特殊處理 |
| **適用場景** | I/O 密集 | CPU 密集 |

#### 3. MitmProxy Addon 架構
```
Master (基礎類，0 addons)
  └── DumpMaster (繼承，36 addons)
       ├── TermLog (終端日誌) ← 可移除
       ├── Dumper (流量轉儲) ← 可移除
       ├── Proxyserver (代理服務器) ← 必要
       └── [其他 33 個 addons...]
```

#### 4. Threading 中的全局變數陷阱
```python
# ❌ 錯誤：sys.stdout 是全局的
def thread_func():
    sys.stdout = open('file.txt', 'w')  # 影響所有線程！

# ✅ 正確：使用上下文管理或 addon 機制
def thread_func():
    master.addons.remove(output_addon)  # 只影響當前實例
```

---

## 🔄 版本演進

```
v2.0.1 (multiprocessing)
  ├─ Windows 兼容性問題
  └─ asyncio 事件循環問題
       ↓
v2.0.2 (threading 基礎)
  ├─ 修復 Windows 啟動問題
  ├─ 添加端口健康檢查
  └─ 保留詳細註解
       ↓
v2.0.3 (MitmOptions 嘗試)
  └─ KeyError: 不支援的參數
       ↓
v2.0.4 (Master 類嘗試)
  └─ 無 ProxyServer addon
       ↓
v2.0.5 (stdout 重定向嘗試)
  └─ sys.stdout 全局問題
       ↓
v2.0.6 (移除 addons) ✅
  ├─ 移除 TermLog + Dumper
  ├─ 保留所有其他功能
  └─ 完美解決所有問題
```

---

## 📋 待辦事項

### 已完成 ✅
- [x] 修復 stealth.min.js 下載
- [x] 修復 MitmProxy Windows 啟動
- [x] 修復靜默模式
- [x] 添加 Chrome 靜默模式
- [x] 清除 Python 緩存
- [x] 刪除問題文件 (nul)
- [x] 創建備份文件

### 未完成 ⏳
- [ ] 完整功能測試（課程執行）
- [ ] 訪問時長攔截測試
- [ ] 自動答題功能測試
- [ ] 性能測試與優化
- [ ] 用戶文檔更新

### 後續工作
- [ ] 考慮 Linux 環境測試
- [ ] 考慮 macOS 環境測試
- [ ] 整合到 CI/CD 流程

---

## 📊 性能影響

### 修改前後對比

| 指標 | v2.0.1 (multiprocessing) | v2.0.6 (threading + addons) |
|------|-------------------------|----------------------------|
| **Windows 啟動** | ❌ 失敗 | ✅ 成功 |
| **端口監聽時間** | N/A | ~3 秒 |
| **靜默模式** | ✅ 有效（子進程） | ✅ 有效（移除 addons） |
| **資源消耗** | 較高（獨立進程） | 較低（共享記憶體） |
| **維護性** | 一般 | 良好（詳細註解） |

---

## 🔗 相關文檔

- **CHANGELOG.md** - 版本變更記錄
- **CLAUDE_CODE_HANDOVER-2.md** - AI 交接文檔
- **proxy_manager.py.multiprocessing.bak** - 原始版本備份
- **CONFIGURATION_MANAGEMENT_GUIDE.md** - 配置管理指南

---

## 👥 協作記錄

**開發**: Claude Code (Sonnet 4.5)
**測試**: wizard03
**審查**: wizard03

### 重要決策

1. **採用 threading 而非 multiprocessing**
   - 原因：Windows + Python 3.13 兼容性
   - 權衡：功能性 > 進程隔離

2. **保留詳細版本歷史註解**
   - 原因：便於日後參考和回滾
   - 用戶明確要求："原程式碼做成註解也做成備份"

3. **移除 addons 而非重定向 stdout**
   - 原因：sys.stdout 是全局的
   - 優勢：線程安全、代碼簡潔

---

## 📝 結語

本次 Windows 兼容性修復歷經多次迭代和嘗試，最終找到了最優解決方案。關鍵學習點包括：

1. **Windows subprocess 需要 shell=True**
2. **threading 中 sys.stdout 是全局的**
3. **MitmProxy addon 架構的深入理解**
4. **測試驅動開發的重要性**

所有修改都保留了詳細的版本歷史註解，便於日後維護和參考。

---

**文檔版本**: 1.0
**最後更新**: 2025-12-06
**維護者**: Claude Code (Sonnet 4.5)
