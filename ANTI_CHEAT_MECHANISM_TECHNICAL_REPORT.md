# 防作弊機制 API 運作原理技術報告

**文檔版本**: 1.0
**撰寫日期**: 2025-12-14
**專案**: EEBot (Gleipnir)
**目標讀者**: 開發人員

---

## 📋 目錄

1. [執行摘要](#執行摘要)
2. [API 端點概覽](#api-端點概覽)
3. [欄位詳細說明](#欄位詳細說明)
4. [運作機制分析](#運作機制分析)
5. [實作建議](#實作建議)
6. [風險評估](#風險評估)
7. [程式碼範例](#程式碼範例)

---

## 🎯 執行摘要

本報告詳細分析台灣郵政 e 大學測驗系統的防作弊機制 API，包括：
- **API 端點**: `/api/exam/{exam_id}/check-exam-qualification`
- **用途**: 檢查考試資格與防作弊設定
- **發現**: 12 個防作弊相關欄位
- **調用時機**: 答題開始前（必須調用）

**關鍵發現**：
- ✅ 系統支援完整的防作弊機制
- ⚠️ 離開視窗次數/時間會被追蹤
- ⚠️ 可能限制單一裝置作答
- ⚠️ 可強制全螢幕模式

---

## 📡 API 端點概覽

### 基本資訊

```http
GET /api/exam/{exam_id}/check-exam-qualification?no-intercept=true&check_status=start
```

**參數**：
- `exam_id` (路徑參數, 必須): 測驗 ID
- `no-intercept` (查詢參數): 值為 `true`（用途未知，推測為跳過某些攔截器）
- `check_status` (查詢參數): 值為 `start`（檢查狀態：開始答題）

**HTTP 方法**: GET
**回應格式**: JSON
**認證**: 需要 Session Cookie

---

### 完整回應結構

```json
{
  "disable_copy_paste": false,
  "disable_right_click": false,
  "enable_anti_cheat": false,
  "has_audio": false,
  "is_closed": false,
  "is_fullscreen_mode": false,
  "is_leaving_window_constrained": false,
  "is_leaving_window_timeout": false,
  "is_submit_started": true,
  "leaving_window_limit": null,
  "leaving_window_timeout": null,
  "limit_answer_on_signle_client": false,
  "message": "測驗已截止"
}
```

---

## 🔍 欄位詳細說明

### 核心防作弊欄位

#### 1. `enable_anti_cheat`

**類型**: `boolean`
**預設值**: `false`

**說明**:
- 總開關，控制是否啟用防作弊機制
- 當 `true` 時，其他防作弊設定才會生效

**運作機制**:
```python
if response['enable_anti_cheat']:
    # 啟用以下所有防作弊檢查
    check_fullscreen_mode()
    check_copy_paste()
    check_right_click()
    check_window_focus()
```

**影響**:
- ✅ `false`: 可以自由作答，無任何限制
- ⚠️ `true`: 需遵守所有防作弊規則

**實作建議**:
- 答題前檢查此欄位
- 如為 `true`，準備應對其他防作弊機制

---

#### 2. `is_fullscreen_mode`

**類型**: `boolean`
**預設值**: `false`

**說明**:
- 是否強制全螢幕模式作答
- 離開全螢幕可能觸發警告或記錄

**運作機制**:
```javascript
// 前端 JavaScript 偵測
if (is_fullscreen_mode) {
    // 進入全螢幕
    document.documentElement.requestFullscreen();

    // 監聽全螢幕退出事件
    document.addEventListener('fullscreenchange', () => {
        if (!document.fullscreenElement) {
            // 記錄離開全螢幕行為
            logAntiCheatViolation('exit_fullscreen');
        }
    });
}
```

**影響**:
- ✅ `false`: 可以正常視窗模式作答
- ⚠️ `true`: 必須全螢幕，退出可能被記錄

**繞過方式** (僅供技術研究):
- 純 API 模式不受影響（無瀏覽器環境）
- Selenium 無頭模式不受影響

---

#### 3. `disable_copy_paste`

**類型**: `boolean`
**預設值**: `false`

**說明**:
- 禁止複製貼上操作
- 防止考生複製題目到外部搜尋

**運作機制**:
```javascript
if (disable_copy_paste) {
    // 禁用複製事件
    document.addEventListener('copy', (e) => {
        e.preventDefault();
        alert('禁止複製內容');
    });

    // 禁用貼上事件
    document.addEventListener('paste', (e) => {
        e.preventDefault();
        alert('禁止貼上內容');
    });

    // 禁用剪下事件
    document.addEventListener('cut', (e) => {
        e.preventDefault();
    });
}
```

**影響**:
- ✅ `false`: 可以複製貼上
- ⚠️ `true`: 無法使用 Ctrl+C/V

**繞過方式**:
- 純 API 模式獲取題目文字（無需複製）
- OCR 截圖識別（不推薦，效率低）

---

#### 4. `disable_right_click`

**類型**: `boolean`
**預設值**: `false`

**說明**:
- 禁止右鍵選單（防止「檢視原始碼」等操作）

**運作機制**:
```javascript
if (disable_right_click) {
    document.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });
}
```

**影響**:
- ✅ `false`: 可以右鍵
- ⚠️ `true`: 無法右鍵

**繞過方式**:
- 純 API 模式不受影響
- 瀏覽器開發者工具仍可用（F12）

---

### 離開視窗追蹤欄位 ⚠️ 最重要

#### 5. `is_leaving_window_constrained`

**類型**: `boolean`
**預設值**: `false`

**說明**:
- **最關鍵的防作弊機制**
- 追蹤考生是否離開考試視窗（切換分頁、最小化等）

**運作機制**:
```javascript
if (is_leaving_window_constrained) {
    let leave_count = 0;

    // 監聽視窗失焦事件
    window.addEventListener('blur', () => {
        leave_count++;
        console.log(`離開視窗 ${leave_count} 次`);

        // 檢查是否超過限制
        if (leaving_window_limit !== null && leave_count > leaving_window_limit) {
            alert(`已超過離開視窗次數上限 (${leaving_window_limit} 次)`);
            // 可能強制提交或鎖定考試
            forceSubmitExam();
        }

        // 記錄到後端
        recordLeaveWindow(exam_id, leave_count);
    });

    // 監聽視窗聚焦事件
    window.addEventListener('focus', () => {
        console.log('返回視窗');
    });
}
```

**影響**:
- ✅ `false`: 可以自由切換視窗
- ⚠️ `true`: 離開視窗會被追蹤，可能有次數限制

**API 模式風險**:
- ⚠️ 如果使用 Selenium，切換到其他程式會觸發
- ⚠️ 建議保持瀏覽器視窗在前景
- ✅ 純 API 模式（無瀏覽器）不受影響

---

#### 6. `leaving_window_limit`

**類型**: `number | null`
**預設值**: `null`

**說明**:
- 允許離開視窗的最大次數
- `null` 表示無限制（但仍會記錄）

**可能的值**:
- `null`: 無限制
- `0`: 完全不允許離開
- `3`, `5`, `10`: 常見限制值

**運作機制**:
```python
# 後端檢查邏輯
def check_leave_window_violation(exam_id, user_id):
    leave_count = get_user_leave_count(exam_id, user_id)
    limit = get_exam_leave_window_limit(exam_id)

    if limit is not None and leave_count > limit:
        # 標記為違規
        mark_anti_cheat_violation(exam_id, user_id, 'exceed_leave_limit')
        # 可能的處罰：強制提交、成績無效、通知管理員
        return False

    return True
```

**影響**:
- `null`: 僅記錄，不限制
- `> 0`: 超過次數可能被標記作弊

---

#### 7. `is_leaving_window_timeout`

**類型**: `boolean`
**預設值**: `false`

**說明**:
- 是否啟用離開視窗超時機制
- 離開視窗超過指定時間會觸發處罰

**運作機制**:
```javascript
if (is_leaving_window_timeout) {
    let leave_start_time = null;

    window.addEventListener('blur', () => {
        leave_start_time = Date.now();

        // 設定超時檢查
        setTimeout(() => {
            if (leave_start_time !== null) {
                const duration = (Date.now() - leave_start_time) / 1000;
                if (duration >= leaving_window_timeout) {
                    alert(`離開視窗超過 ${leaving_window_timeout} 秒，考試已鎖定`);
                    lockExam();
                }
            }
        }, leaving_window_timeout * 1000);
    });

    window.addEventListener('focus', () => {
        leave_start_time = null; // 清除計時
    });
}
```

**影響**:
- ✅ `false`: 離開多久都無妨
- ⚠️ `true`: 超時可能鎖定考試

---

#### 8. `leaving_window_timeout`

**類型**: `number | null`
**預設值**: `null`

**說明**:
- 離開視窗的超時時間（秒）
- 配合 `is_leaving_window_timeout` 使用

**可能的值**:
- `null`: 無超時限制
- `30`, `60`, `120`: 常見超時值（秒）

**影響**:
- 離開視窗超過此秒數會觸發處罰

---

### 裝置限制欄位

#### 9. `limit_answer_on_signle_client`

**類型**: `boolean`
**預設值**: `false`

**說明**:
- **非常關鍵**：限制只能在單一裝置/瀏覽器作答
- 防止同時多人協作答題

**運作機制**:
```python
# 後端實作（推測）
class ExamSession:
    def start_exam(self, exam_id, user_id, client_fingerprint):
        # 檢查是否已有其他裝置在答題
        active_session = get_active_exam_session(exam_id, user_id)

        if active_session and active_session.client_id != client_fingerprint:
            raise Exception('已有其他裝置正在作答此測驗')

        # 創建新會話
        create_exam_session(exam_id, user_id, client_fingerprint)
```

**裝置識別方式**（推測）:
- IP 地址
- Browser User-Agent
- Session ID
- 可能使用 Canvas Fingerprinting 或 WebGL Fingerprinting

**影響**:
- ✅ `false`: 可以多裝置作答
- ⚠️ `true`: 只能單一裝置，切換裝置會被拒絕

**API 模式風險**:
- ⚠️ 如果使用純 API，需使用相同的 Session Cookie
- ⚠️ 不要在多台電腦同時調用 API
- ✅ 單一電腦的 API 呼叫應該沒問題

---

### 其他狀態欄位

#### 10. `has_audio`

**類型**: `boolean`
**預設值**: `false`

**說明**:
- 測驗是否包含音訊題目
- 需要音訊播放功能

**影響**:
- ✅ `false`: 純文字/圖片題目
- ⚠️ `true`: 需要處理音訊

---

#### 11. `is_closed`

**類型**: `boolean`
**預設值**: `false`

**說明**:
- 測驗是否已關閉（截止）
- **必須檢查**：關閉的測驗無法作答

**影響**:
- ✅ `false`: 可以作答
- ❌ `true`: 測驗已截止，無法作答

**實作建議**:
```python
def can_answer_exam(exam_id):
    qualification = check_exam_qualification(exam_id)

    if qualification['is_closed']:
        print(f'測驗 {exam_id} 已截止')
        return False

    return True
```

---

#### 12. `is_submit_started`

**類型**: `boolean`
**預設值**: `false`

**說明**:
- 是否已開始提交流程
- 可能用於防止重複提交

**影響**:
- `true`: 已開始提交，可能無法再修改答案

---

#### 13. `message`

**類型**: `string`
**預設值**: `""`

**說明**:
- 系統訊息（錯誤提示、警告等）

**常見訊息**:
- `"測驗已截止"`
- `"未達開始時間"`
- `"已超過作答次數"`

---

## ⚙️ 運作機制分析

### 完整檢查流程

```
步驟 1: 答題前檢查
  ├─ 調用 check-exam-qualification API
  ├─ 檢查 is_closed (測驗是否截止)
  ├─ 檢查 enable_anti_cheat (是否啟用防作弊)
  └─ 檢查 limit_answer_on_signle_client (裝置限制)

步驟 2: 啟用防作弊機制（如果 enable_anti_cheat = true）
  ├─ 全螢幕模式 (is_fullscreen_mode)
  ├─ 禁用複製貼上 (disable_copy_paste)
  ├─ 禁用右鍵 (disable_right_click)
  └─ 追蹤視窗焦點 (is_leaving_window_constrained)

步驟 3: 持續監控（答題過程中）
  ├─ 視窗失焦事件 → 記錄離開次數
  ├─ 視窗失焦時長 → 檢查是否超時
  └─ 複製貼上操作 → 阻止並可能記錄

步驟 4: 違規處理
  ├─ 超過離開次數 → 可能強制提交
  ├─ 超過離開時長 → 可能鎖定考試
  └─ 多裝置作答 → 拒絕提交
```

### 前端與後端配合

```
┌─────────────┐         API Request          ┌─────────────┐
│   前端      │ ──────────────────────────▶ │   後端      │
│  (Browser)  │                              │  (Server)   │
└─────────────┘                              └─────────────┘
      │                                             │
      │ 1. 獲取防作弊設定                           │
      │ ─────────────────────────────────────────▶ │
      │                                             │
      │ 2. 返回設定                                 │
      │ ◀───────────────────────────────────────── │
      │                                             │
      │ 3. 前端啟用監控                             │
      │   - 視窗焦點追蹤                            │
      │   - 禁用複製貼上                            │
      │   - 強制全螢幕                              │
      │                                             │
      │ 4. 記錄違規行為                             │
      │ ─────────────────────────────────────────▶ │
      │   (離開視窗、退出全螢幕等)                  │
      │                                             │
      │ 5. 後端驗證與處罰                           │
      │                                             │ - 檢查違規次數
      │                                             │ - 決定是否鎖定
      │                                             │
      │ 6. 提交答案時驗證                           │
      │ ─────────────────────────────────────────▶ │
      │                                             │ - 檢查裝置 ID
      │                                             │ - 驗證違規記錄
      │                                             │ - 決定是否接受
```

---

## 💡 實作建議

### 方案一：完全遵守（推薦）

```python
class AntiCheatCompliantAnswerer:
    """遵守防作弊規則的答題器"""

    def check_and_prepare(self, exam_id):
        """檢查並準備防作弊環境"""

        # 1. 檢查資格
        qualification = self.get_qualification(exam_id)

        # 2. 檢查是否可作答
        if qualification['is_closed']:
            raise Exception('測驗已截止')

        # 3. 警告防作弊設定
        if qualification['enable_anti_cheat']:
            print('[WARNING] 測驗啟用防作弊機制:')

            if qualification['is_fullscreen_mode']:
                print('  - 需要全螢幕模式')

            if qualification['is_leaving_window_constrained']:
                limit = qualification['leaving_window_limit']
                print(f'  - 離開視窗限制: {limit if limit else "無限制(會記錄)"}')

            if qualification['limit_answer_on_signle_client']:
                print('  - 限制單一裝置作答')

        # 4. 如果使用 Selenium，配置環境
        if self.mode == 'selenium':
            if qualification['is_fullscreen_mode']:
                self.driver.fullscreen_window()

            # 保持視窗在前景
            self.driver.switch_to.window(self.driver.current_window_handle)

        return qualification

    def get_qualification(self, exam_id):
        """獲取防作弊設定"""
        url = f'{self.base_url}/api/exam/{exam_id}/check-exam-qualification'
        params = {'no-intercept': 'true', 'check_status': 'start'}
        response = self.session.get(url, params=params)
        return response.json()
```

### 方案二：純 API 模式（最安全）

```python
class PureAPIAnswerer:
    """純 API 模式 - 不受大部分防作弊影響"""

    def auto_answer_exam(self, exam_id):
        """使用純 API 答題，繞過前端防作弊"""

        # 1. 檢查基本資格
        qualification = self.check_qualification(exam_id)

        if qualification['is_closed']:
            return {'success': False, 'reason': '測驗已截止'}

        # 2. 純 API 優勢：
        #    ✓ 不受 is_fullscreen_mode 影響（無瀏覽器）
        #    ✓ 不受 disable_copy_paste 影響（直接獲取文字）
        #    ✓ 不受 disable_right_click 影響（無右鍵操作）
        #    ✓ 不受 is_leaving_window_constrained 影響（無視窗）

        # 3. 仍需注意：
        #    ⚠️ limit_answer_on_signle_client（可能檢查 Session/IP）

        # 4. 獲取試卷
        paper = self.get_exam_paper(exam_id)

        # 5. 比對題庫
        answers = self.match_question_bank(paper['subjects'])

        # 6. 提交答案
        return self.submit_answers(exam_id, answers)

    def check_qualification(self, exam_id):
        """檢查資格（僅關心 is_closed 和 limit_answer_on_signle_client）"""
        url = f'/api/exam/{exam_id}/check-exam-qualification'
        params = {'no-intercept': 'true', 'check_status': 'start'}
        response = self.session.get(url, params=params)
        data = response.json()

        # 警告裝置限制
        if data.get('limit_answer_on_signle_client'):
            print('[WARNING] 測驗限制單一裝置，請確保使用相同 Session')

        return data
```

---

## ⚠️ 風險評估

### 各欄位風險等級

| 欄位 | 風險等級 | Selenium 模式 | 純 API 模式 | 說明 |
|------|---------|--------------|------------|------|
| `is_closed` | 🔴 高 | 阻斷 | 阻斷 | 測驗截止，無法作答 |
| `limit_answer_on_signle_client` | 🟠 中高 | 需注意 | 需注意 | 可能檢查裝置/Session |
| `is_leaving_window_constrained` | 🟠 中高 | 風險 | 無影響 | Selenium 需保持焦點 |
| `leaving_window_limit` | 🟠 中 | 風險 | 無影響 | 超過次數可能失敗 |
| `is_fullscreen_mode` | 🟡 中低 | 需配置 | 無影響 | Selenium 可設全螢幕 |
| `enable_anti_cheat` | 🟡 中低 | 需注意 | 低影響 | 總開關，影響其他欄位 |
| `disable_copy_paste` | 🟢 低 | 無影響 | 無影響 | 不依賴複製貼上 |
| `disable_right_click` | 🟢 低 | 無影響 | 無影響 | 不使用右鍵 |

### 模式比較

| 模式 | 繞過能力 | 穩定性 | 速度 | 推薦度 |
|------|---------|--------|------|--------|
| **純 API** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **強烈推薦** |
| **Selenium (配合防作弊)** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 可行 |
| **Selenium (忽略防作弊)** | ⭐⭐ | ⭐⭐ | ⭐⭐ | 高風險 |

---

## 📝 程式碼範例

### 完整檢查與處理流程

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""防作弊機制處理範例"""

import requests
from typing import Dict, Any

class AntiCheatHandler:
    """防作弊機制處理器"""

    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url

    def check_qualification(self, exam_id: int) -> Dict[str, Any]:
        """檢查考試資格與防作弊設定"""

        url = f'{self.base_url}/api/exam/{exam_id}/check-exam-qualification'
        params = {
            'no-intercept': 'true',
            'check_status': 'start'
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()

        return response.json()

    def analyze_anti_cheat_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """分析防作弊設定並返回風險評估"""

        analysis = {
            'can_answer': True,
            'risk_level': 'low',
            'warnings': [],
            'recommendations': []
        }

        # 1. 檢查測驗是否截止
        if settings.get('is_closed'):
            analysis['can_answer'] = False
            analysis['risk_level'] = 'blocked'
            analysis['warnings'].append('測驗已截止，無法作答')
            return analysis

        # 2. 檢查是否啟用防作弊
        if not settings.get('enable_anti_cheat'):
            analysis['risk_level'] = 'low'
            analysis['recommendations'].append('未啟用防作弊，可安全作答')
            return analysis

        # 3. 分析各項防作弊設定
        risk_score = 0

        # 全螢幕模式
        if settings.get('is_fullscreen_mode'):
            risk_score += 2
            analysis['warnings'].append('需要全螢幕模式')
            analysis['recommendations'].append('使用純 API 模式或配置 Selenium 全螢幕')

        # 離開視窗限制
        if settings.get('is_leaving_window_constrained'):
            risk_score += 3
            limit = settings.get('leaving_window_limit')
            if limit is not None:
                analysis['warnings'].append(f'離開視窗限制: {limit} 次')
                risk_score += 2
            else:
                analysis['warnings'].append('離開視窗會被記錄（無次數限制）')

            timeout = settings.get('leaving_window_timeout')
            if timeout is not None:
                analysis['warnings'].append(f'離開視窗超時: {timeout} 秒')
                risk_score += 2

            analysis['recommendations'].append('保持瀏覽器視窗焦點或使用純 API 模式')

        # 單一裝置限制
        if settings.get('limit_answer_on_signle_client'):
            risk_score += 3
            analysis['warnings'].append('限制單一裝置作答')
            analysis['recommendations'].append('使用相同 Session，不要多裝置同時答題')

        # 禁用複製貼上
        if settings.get('disable_copy_paste'):
            risk_score += 1
            analysis['warnings'].append('禁用複製貼上')
            analysis['recommendations'].append('直接使用 API 獲取題目文字')

        # 禁用右鍵
        if settings.get('disable_right_click'):
            risk_score += 1
            analysis['warnings'].append('禁用右鍵')

        # 音訊題目
        if settings.get('has_audio'):
            risk_score += 1
            analysis['warnings'].append('包含音訊題目')
            analysis['recommendations'].append('需要音訊處理能力')

        # 計算風險等級
        if risk_score >= 8:
            analysis['risk_level'] = 'high'
        elif risk_score >= 4:
            analysis['risk_level'] = 'medium'
        else:
            analysis['risk_level'] = 'low'

        return analysis

    def print_analysis(self, exam_id: int):
        """輸出防作弊分析報告"""

        print(f'\n{"="*60}')
        print(f'測驗 {exam_id} 防作弊分析報告')
        print(f'{"="*60}\n')

        # 獲取設定
        settings = self.check_qualification(exam_id)

        # 分析
        analysis = self.analyze_anti_cheat_settings(settings)

        # 輸出結果
        print(f'📊 風險等級: {analysis["risk_level"].upper()}')
        print(f'✅ 可以作答: {"是" if analysis["can_answer"] else "否"}\n')

        if analysis['warnings']:
            print('⚠️ 警告事項:')
            for warning in analysis['warnings']:
                print(f'   - {warning}')
            print()

        if analysis['recommendations']:
            print('💡 建議:')
            for rec in analysis['recommendations']:
                print(f'   - {rec}')
            print()

        # 顯示原始設定
        print('📋 原始設定:')
        for key, value in settings.items():
            print(f'   {key}: {value}')

        print(f'\n{"="*60}\n')

        return analysis

# 使用範例
if __name__ == '__main__':
    # 建立 Session
    session = requests.Session()
    # ... 登入並獲取 Cookie ...

    # 建立處理器
    handler = AntiCheatHandler(session, 'https://elearn.post.gov.tw')

    # 分析測驗 48
    analysis = handler.print_analysis(48)

    # 根據分析結果決定答題策略
    if not analysis['can_answer']:
        print('無法作答，程式終止')
    elif analysis['risk_level'] == 'high':
        print('建議使用純 API 模式')
    else:
        print('可以正常作答')
```

---

## 📌 重要結論

1. **純 API 模式最安全**：
   - 不受前端 JavaScript 防作弊影響
   - 僅需注意 `limit_answer_on_signle_client`

2. **必須檢查的欄位**：
   - `is_closed` - 決定能否作答
   - `limit_answer_on_signle_client` - 裝置限制

3. **Selenium 模式注意事項**：
   - 保持視窗焦點（避免觸發 `is_leaving_window_constrained`）
   - 可能需要全螢幕模式
   - 不要多裝置同時作答

4. **系統未發現的機制**：
   - 無網路攝影頭監控
   - 無螢幕錄影要求
   - 無時間戳驗證（可能存在但未暴露）

---

**文檔結束**
**最後更新**: 2025-12-14
**維護者**: EEBot Development Team
