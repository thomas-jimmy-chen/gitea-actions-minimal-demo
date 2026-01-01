```
        ▐▛███▜▌
       ▝▜█████▛▘
         ▘▘ ▝▝
    Powered by Claude
```

# CI/CD 與自動化測試策略

**建立日期**: 2025-01-01
**專案**: EEBot (TronClass Learning Assistant)

---

## 1. 討論背景

### 1.1 提出的問題

1. **CodeRabbit 需要嗎？** - 是否需要第三方 AI Code Review 工具
2. **Claude Code 能接 CI/CD 嗎？** - Claude Code CLI 的自動化能力
3. **自動化測試怎麼做？** - 專案的測試策略

### 1.2 結論摘要

| 問題 | 決策 | 理由 |
|------|------|------|
| CodeRabbit | **不需要** | 個人工作室，Claude Code 已足夠 |
| Claude Code CI/CD | **可行** | 官方支援 GitHub Actions 整合 |
| 自動化測試 | **立即建立** | 補齊專案的測試缺口 |

---

## 2. CodeRabbit vs Claude Code 比較

### 2.1 工具對比

| 特性 | CodeRabbit | Claude Code |
|------|------------|-------------|
| 費用 | $12-24/月 | 按 API 用量 |
| Code Review | ✅ PR 自動審查 | ✅ 支援 |
| 開發協助 | ❌ | ✅ 完整開發能力 |
| 本地開發 | ❌ | ✅ CLI 直接使用 |
| GitHub 整合 | ✅ | ✅ GitHub App |
| 適合對象 | 多人團隊 | 個人/小團隊 |

### 2.2 決策

對於個人工作室，Claude Code 已經涵蓋 CodeRabbit 的功能，且提供更多開發協助。**不建議額外購買 CodeRabbit**。

---

## 3. Claude Code CI/CD 整合

### 3.1 支援的模式

#### 模式 A：Headless Mode (CLI 自動化)

```bash
# 非互動式執行
claude -p "Your prompt here" --allowedTools "Read,Edit,Bash"

# JSON 輸出
claude -p "Review this code" --output-format json

# 自動核准特定工具
claude -p "Run tests and fix failures" --allowedTools "Bash,Read,Edit"
```

#### 模式 B：GitHub Actions 整合

```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "/code-reviewer"
          claude_args: "--max-turns 5"
```

#### 模式 C：PR 留言互動

在 PR 或 Issue 中使用 `@claude` 觸發：

```
@claude 幫我 review 這個 PR
@claude /code-reviewer
@claude 這段代碼有什麼問題？
```

### 3.2 快速設定

```bash
# 在 Claude Code 中執行
/install-github-app
```

這會引導完成：
1. 安裝 Claude GitHub App 到 repository
2. 設定 `ANTHROPIC_API_KEY` secret
3. 建立 workflow 檔案

---

## 4. EEBot 的 CI/CD 架構

### 4.1 整體流程

```
┌─────────────────────────────────────────────────────────┐
│                    EEBot CI/CD 流程                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  git push ──► GitHub Actions                            │
│                   │                                     │
│                   ├── pytest (自動化測試)               │
│                   │     └── coverage report             │
│                   │                                     │
│                   ├── Claude /code-reviewer (AI 審查)   │
│                   │                                     │
│                   └── Claude /pep8-checker (代碼風格)   │
│                                                         │
│  結果 ──► PR 留言顯示測試結果 + AI 審查意見             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4.2 可用的 Skills

專案已配置的 Skills：

| Skill | 用途 | CI/CD 使用 |
|-------|------|------------|
| `/code-reviewer` | 代碼審查 | PR 自動觸發 |
| `/commit-helper` | Commit 訊息 | 本地使用 |
| `/pep8-checker` | PEP8 檢查 | PR 自動觸發 |
| `/test-runner` | 執行測試 | PR 自動觸發 |

### 4.3 費用估算

| 項目 | 費用 |
|------|------|
| GitHub Actions | 免費（公開 repo）/ 2000 分鐘/月（私有） |
| Claude API | 按用量（每次 review 約 $0.01-0.05） |
| **總計** | 約 $5-10/月（正常使用量） |

---

## 5. 自動化測試策略

### 5.1 測試金字塔

```
                    ╱╲
                   ╱  ╲
                  ╱ E2E╲     (少量，整合測試)
                 ╱──────╲
                ╱ 整合測試╲   (中量，模組間協作)
               ╱──────────╲
              ╱  單元測試   ╲ (大量，函數/類別)
             ╱──────────────╲
```

### 5.2 測試範圍

| 優先級 | 模組 | 測試類型 | 目標覆蓋率 |
|--------|------|----------|------------|
| P0 | `answer_matcher.py` | 單元測試 | 90% |
| P0 | `question_bank.py` | 單元測試 | 80% |
| P1 | `time_tracker.py` | 單元測試 | 80% |
| P1 | `models/question.py` | 單元測試 | 90% |
| P2 | `config_loader.py` | 單元測試 | 70% |
| P2 | `cookie_manager.py` | 單元測試 | 70% |

### 5.3 測試框架

```
tests/
├── __init__.py
├── conftest.py              # 共用 fixtures
├── unit/                    # 單元測試
│   ├── test_answer_matcher.py
│   ├── test_question_bank.py
│   ├── test_time_tracker.py
│   └── test_models.py
└── integration/             # 整合測試 (未來)
    └── test_exam_flow.py
```

### 5.4 執行測試

```bash
# 執行所有測試
pytest

# 執行特定測試
pytest tests/unit/test_answer_matcher.py

# 顯示覆蓋率
pytest --cov=src --cov-report=html

# 只執行快速測試
pytest -m "not slow"
```

---

## 6. Pre-commit Hooks

### 6.1 配置內容

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest tests/unit -x -q
        language: system
        pass_filenames: false
        always_run: true
```

### 6.2 安裝

```bash
pip install pre-commit
pre-commit install
```

### 6.3 效果

每次 `git commit` 時自動執行：
1. Black 格式化
2. isort 排序 imports
3. Flake8 風格檢查
4. pytest 快速測試

---

## 7. 開發經驗缺口分析

### 7.1 已掌握技術

| 領域 | 技術 | 程度 |
|------|------|------|
| Web 自動化 | Selenium, Cookie, 等待機制 | ██████████ 精通 |
| API 分析 | Burp Suite, HTTP 抓包 | ████████░░ 熟練 |
| 網路層控制 | MitmProxy 攔截器 | ████████░░ 熟練 |
| 架構設計 | POM, Service Layer, Orchestrator | ███████░░░ 中上 |
| 文檔能力 | 交接文檔, 規格文檔 | ██████████ 精通 |

### 7.2 待補強領域

| 優先級 | 領域 | 英文名稱 | 補強方式 |
|--------|------|----------|----------|
| P0 | 單元測試 | Unit Testing | pytest 框架 + 實作 |
| P1 | 結構化日誌 | Structured Logging | structlog 套件 |
| P1 | Pre-commit | Pre-commit Hooks | 本次設定 |
| P2 | 資料持久化 | SQLite + ORM | SQLAlchemy |
| P3 | 非同步編程 | asyncio | aiohttp 學習 |
| P3 | CI/CD | GitHub Actions | 本次設定 |

### 7.3 一句話建議

> 你的「寫文檔」能力已經超越大多數開發者，現在需要把同樣的嚴謹態度用在「寫測試」上。

---

## 8. 業界認可的開發方法名稱

### 8.1 開發流程方法

| 方法 | 英文名稱 | 中文名稱 | 提出者 |
|------|----------|----------|--------|
| 方法 1 | Specification-Driven Development (SDD) | 規格驅動開發 | 傳統軟體工程 |
| 方法 1 變體 | Design-First Development | 設計優先開發 | API 開發領域 |
| 方法 2 | Iterative Development | 迭代式開發 | Agile 方法論 |
| 方法 2 變體 | Exploratory Programming | 探索式編程 | Kent Beck |
| 方法 3 | Iterative-to-Structured Transition | 迭代到結構化過渡 | (綜合歸納) |
| 方法 4 | **Dual-Track Agile** | 雙軌敏捷 | Marty Cagan (SVPG) |
| 方法 4 變體 | Evolutionary Architecture | 演進式架構 | ThoughtWorks |
| 方法 4 變體 | Incremental Commitment Model | 漸進承諾模型 | Barry Boehm |

### 8.2 EEBot 採用的方法

**Dual-Track Agile (雙軌敏捷)**：

- **Discovery Track (探索軌)** = 🔄 探索中
- **Delivery Track (交付軌)** = 📋 已穩定

這是由 Marty Cagan 在《Inspired》書中推廣的方法。

---

## 9. 相關文檔

| 文檔 | 說明 |
|------|------|
| [AI_COLLABORATION_METHOD_4_HYBRID.md](./AI_COLLABORATION_METHOD_4_HYBRID.md) | 混合漸進式開發詳解 |
| [AI_COLLABORATION_METHODS_COMPARISON.md](./AI_COLLABORATION_METHODS_COMPARISON.md) | 四種方法比較 |
| [TODO.md](./TODO.md) | 專案待辦事項 |

---

**文檔建立者**: Claude Code (Opus 4.5)
**用途**: 記錄 CI/CD、測試策略與開發經驗分析的討論結果
