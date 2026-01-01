```
        ▐▛███▜▌
       ▝▜█████▛▘
         ▘▘ ▝▝
    Powered by Claude
```

# AI 協作工作流程方法 1：結構化規格驅動開發

**方法名稱**: Structured Specification-Driven Development (SSDD)
**適用情境**: 需求明確、功能確定時
**文檔版本**: 1.0
**建立日期**: 2025-12-31

---

## 1. 方法概述

當專案需求與功能**相對明確**時，採用「先規格、後實作」的結構化方法。透過 AI 協助將需求切細切小，產出正式規格文檔，再依規格實作。

---

## 2. 工作流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                    結構化規格驅動開發流程                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [Phase 1: 需求探討]                                                │
│      │                                                              │
│      ├── 1.1 功能性需求 (Functional Requirements)                   │
│      ├── 1.2 非功能性需求 (NFR: 效能、安全、可用性)                  │
│      ├── 1.3 限制條件 (Constraints)                                 │
│      └── 1.4 邊界條件 (Edge Cases)                                  │
│      │                                                              │
│      ▼                                                              │
│  [Phase 2: 切細切小]                                                │
│      │                                                              │
│      ├── 2.1 模組分解 (Module Decomposition)                        │
│      ├── 2.2 User Stories (用戶故事)                                │
│      ├── 2.3 Use Cases (使用案例)                                   │
│      ├── 2.4 Task Breakdown (任務拆解)                              │
│      └── 2.5 API 端點定義                                           │
│      │                                                              │
│      ▼                                                              │
│  [Phase 3: 規格文檔產出]                                            │
│      │                                                              │
│      ├── 3.1 SDD (Software Design Document)                         │
│      ├── 3.2 OpenAPI/Swagger (API 規格)                             │
│      ├── 3.3 ERD (Entity Relationship Diagram)                      │
│      ├── 3.4 邊界值規格表                                           │
│      └── 3.5 測試案例 (Test Cases)                                  │
│      │                                                              │
│      ▼                                                              │
│  [Phase 4: 依規格實作]                                              │
│      │                                                              │
│      ├── 4.1 依模組順序實作                                         │
│      ├── 4.2 每個模組完成後驗證規格                                  │
│      └── 4.3 整合測試                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. 各階段詳細說明

### 3.1 Phase 1: 需求探討

**目標**: 完整理解專案目標與範圍

**AI 會詢問的問題**:
- 目標平台是什麼？(Web/App/API/Desktop)
- 誰是主要使用者？
- 核心功能有哪些？(列出 3-5 個最重要的)
- 有什麼技術限制？(語言、框架、環境)
- 效能需求？(回應時間、並發數)
- 安全需求？(認證、授權、加密)

**產出物**:
```markdown
## 需求摘要

### 功能性需求
1. FR-001: 用戶可以登入系統
2. FR-002: 用戶可以查看課程列表
3. FR-003: ...

### 非功能性需求
1. NFR-001: 回應時間 < 2 秒
2. NFR-002: 支援 1000 並發用戶
3. NFR-003: ...

### 限制條件
1. 必須使用 Python 3.10+
2. 必須支援 Windows/Linux
3. ...
```

---

### 3.2 Phase 2: 切細切小

**目標**: 將大需求分解為可管理的小單元

**切分原則** (依據 CLAUDE.md):

| 閾值 | 動作 |
|------|------|
| 方法 > 30 行 | 拆分為多個小方法 |
| 類別 > 300 行 | 拆分為多個類別 |
| 參數 > 4 個 | 封裝成 dataclass |
| 巢狀 > 3 層 | 提取內層邏輯 |

**模組分解範例**:
```
專案名稱
├── 模組 1: 認證模組 (auth/)
│   ├── 1.1 登入 (login.py)
│   ├── 1.2 登出 (logout.py)
│   └── 1.3 Session 管理 (session.py)
│
├── 模組 2: 核心業務 (core/)
│   ├── 2.1 功能 A
│   ├── 2.2 功能 B
│   └── 2.3 功能 C
│
├── 模組 3: 資料層 (data/)
│   ├── 3.1 資料庫操作
│   └── 3.2 快取管理
│
└── 模組 4: 工具 (utils/)
    ├── 4.1 日誌
    └── 4.2 配置
```

**User Story 格式**:
```gherkin
Feature: 用戶登入

  Scenario: 成功登入
    Given 用戶在登入頁面
    And 用戶輸入正確的帳號密碼
    When 用戶點擊登入按鈕
    Then 系統顯示首頁
    And 系統設置 Session Cookie

  Scenario: 登入失敗 - 密碼錯誤
    Given 用戶在登入頁面
    And 用戶輸入錯誤的密碼
    When 用戶點擊登入按鈕
    Then 系統顯示「帳號或密碼錯誤」
    And 用戶停留在登入頁面
```

---

### 3.3 Phase 3: 規格文檔產出

**AI 可產出的文檔類型**:

#### 3.3.1 OpenAPI 3.0 規格

```yaml
openapi: 3.0.0
info:
  title: 專案 API
  version: 1.0.0
  description: API 規格說明

servers:
  - url: https://api.example.com/v1

paths:
  /auth/login:
    post:
      summary: 用戶登入
      tags:
        - Authentication
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - username
                - password
              properties:
                username:
                  type: string
                  minLength: 3
                  maxLength: 50
                password:
                  type: string
                  minLength: 8
      responses:
        '200':
          description: 登入成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  token:
                    type: string
                  expires_at:
                    type: string
                    format: date-time
        '401':
          description: 認證失敗
```

#### 3.3.2 邊界值規格表

| 欄位 | 類型 | 最小值 | 最大值 | 預設值 | 必填 | 正則表達式 | 說明 |
|------|------|--------|--------|--------|------|------------|------|
| `username` | string | 3 chars | 50 chars | - | ✓ | `^[a-zA-Z0-9_]+$` | 用戶名 |
| `password` | string | 8 chars | 100 chars | - | ✓ | - | 密碼 |
| `age` | int | 0 | 150 | null | ✗ | - | 年齡 |
| `email` | string | 5 chars | 255 chars | - | ✗ | RFC 5322 | 電子郵件 |

#### 3.3.3 SDD 文檔結構

```markdown
# 軟體設計文檔 (SDD)

## 1. 簡介
### 1.1 目的
### 1.2 範圍
### 1.3 參考文檔
### 1.4 術語定義

## 2. 系統概述
### 2.1 系統背景
### 2.2 系統目標
### 2.3 系統限制

## 3. 架構設計
### 3.1 系統架構圖
### 3.2 模組分解
### 3.3 資料流程圖
### 3.4 部署架構

## 4. 詳細設計
### 4.1 模組 A
#### 4.1.1 職責
#### 4.1.2 介面定義
#### 4.1.3 演算法描述
#### 4.1.4 錯誤處理

## 5. 資料設計
### 5.1 ERD
### 5.2 資料字典
### 5.3 資料庫 Schema

## 6. 介面設計
### 6.1 API 規格
### 6.2 UI 規格

## 7. 安全設計
### 7.1 認證機制
### 7.2 授權機制
### 7.3 資料加密

## 8. 測試策略
### 8.1 單元測試
### 8.2 整合測試
### 8.3 驗收測試
```

---

### 3.4 Phase 4: 依規格實作

**實作順序建議**:

1. **核心模組優先**: 先實作最關鍵的業務邏輯
2. **由內而外**: 先資料層 → 業務層 → 介面層
3. **測試驅動**: 每個模組先寫測試，再實作

**每個模組完成檢查項**:
- [ ] 符合 SDD 規格
- [ ] 通過單元測試
- [ ] 邊界值測試通過
- [ ] 程式碼符合風格規範
- [ ] 文檔更新

---

## 4. 適用情境

| 情境 | 適用程度 |
|------|----------|
| 需求明確、範圍固定 | ⭐⭐⭐⭐⭐ |
| 有明確的交付時間 | ⭐⭐⭐⭐⭐ |
| 團隊協作專案 | ⭐⭐⭐⭐⭐ |
| 需要正式文檔 | ⭐⭐⭐⭐⭐ |
| 需求可能變動 | ⭐⭐ |
| 探索性專案 | ⭐ |

---

## 5. 與 AI 協作的對話範本

### 開始專案

```
你：我要開發一個 [專案描述]，功能包括 [功能列表]

AI：好的，讓我確認幾個問題：
    1. 目標平台？
    2. 技術限制？
    3. 效能需求？
    4. 安全需求？
    ...
```

### 請求切分

```
你：請幫我把這個功能切細

AI：根據你的需求，我建議分成以下模組：
    [模組分解圖]

    每個模組的職責：
    - 模組 A: ...
    - 模組 B: ...
```

### 請求規格文檔

```
你：請產出 OpenAPI 規格

AI：[OpenAPI YAML 內容]

你：請產出邊界值規格表

AI：[邊界值表格]
```

---

## 6. 產出文檔清單

完成此方法後，你會得到：

```
docs/
├── SDD.md                    # 軟體設計文檔
├── REQUIREMENTS.md           # 需求規格
├── api/
│   └── openapi.yaml          # API 規格
├── database/
│   ├── ERD.md                # 實體關係圖
│   └── SCHEMA.sql            # 資料庫 Schema
├── specs/
│   ├── BOUNDARY_VALUES.md    # 邊界值規格
│   └── USER_STORIES.md       # 用戶故事
└── tests/
    └── TEST_CASES.md         # 測試案例
```

---

**文檔建立者**: Claude Code (Opus 4.5)
**方法論基礎**: Waterfall + Specification-Driven Development
