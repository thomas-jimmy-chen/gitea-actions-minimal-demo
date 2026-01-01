```
        ▐▛███▜▌
       ▝▜█████▛▘
         ▘▘ ▝▝
    Powered by Claude
```

# Claude Code Review 快速指令參考

**建立日期**: 2025-01-01
**用途**: 使用 Claude Code CLI 進行本地 Code Review

---

## 快速指令一覽

| 情境 | 指令 |
|------|------|
| 互動式 review | `claude` → `/code-reviewer` |
| 快速 review | `claude -p "/code-reviewer"` |
| Review 特定檔案 | `claude -p "review src/xxx.py"` |
| PEP8 檢查 | `claude` → `/pep8-checker` |
| 執行測試 | `claude` → `/test-runner` |
| Commit 訊息 | `claude` → `/commit-helper` |

---

## 詳細使用方式

### 1. Review 當前變更

```bash
# 互動模式
claude
> /code-reviewer

# 非互動模式
claude -p "/code-reviewer"

# 自訂提示
claude -p "請幫我 review 目前的 git diff 變更，重點檢查安全性問題"
```

### 2. Review 特定檔案

```bash
# 單一檔案
claude -p "請幫我 review src/services/answer_matcher.py"

# 多個檔案
claude -p "請幫我 review src/services/ 目錄下的所有檔案"

# 帶上下文
claude -p "這個檔案是答案匹配引擎，請檢查匹配邏輯是否有問題：src/services/answer_matcher.py"
```

### 3. Review Commit 或 PR

```bash
# Review 最近一次 commit
claude -p "請幫我 review 最近一次 commit 的變更"

# Review 特定 commit
claude -p "請幫我 review commit abc1234 的變更"

# Review 分支差異（PR 前）
claude -p "請幫我 review 這個分支相對於 main 的所有變更"
```

### 4. 專項檢查

```bash
# 安全性檢查
claude -p "請檢查這段代碼是否有安全漏洞：src/api/visit_duration_api.py"

# 效能檢查
claude -p "請分析這個檔案的效能瓶頸：src/services/question_bank.py"

# 重構建議
claude -p "請給我重構建議：src/scenarios/course_learning.py"
```

---

## 專案 Skills

EEBot 已配置的 Skills：

| Skill | 用途 | 觸發方式 |
|-------|------|----------|
| `/code-reviewer` | 代碼審查 | `claude` → `/code-reviewer` |
| `/commit-helper` | Commit 訊息 | `claude` → `/commit-helper` |
| `/pep8-checker` | PEP8 檢查 | `claude` → `/pep8-checker` |
| `/test-runner` | 執行測試 | `claude` → `/test-runner` |

---

## 常用工作流程

### A. 提交前 Review

```bash
# 1. 查看變更
git status
git diff

# 2. 請 Claude review
claude -p "/code-reviewer"

# 3. 修正問題後提交
git add .
claude -p "/commit-helper"
```

### B. PR 前完整檢查

```bash
# 1. PEP8 檢查
claude -p "/pep8-checker"

# 2. 執行測試
pytest tests/unit/ -v

# 3. Code Review
claude -p "/code-reviewer"

# 4. 推送
git push origin feature/xxx
```

### C. 重構檢查

```bash
# 1. 請 Claude 分析
claude -p "請分析 src/menu.py 的重構建議，根據 CLAUDE.md 的切細原則"

# 2. 執行重構

# 3. 驗證測試
pytest tests/unit/ -v

# 4. 再次 review
claude -p "/code-reviewer"
```

---

## 輸出格式選項

```bash
# 預設文字輸出
claude -p "/code-reviewer"

# JSON 輸出（適合自動化）
claude -p "/code-reviewer" --output-format json

# 限制回應長度
claude -p "/code-reviewer" --max-turns 3
```

---

## 為什麼選擇本地 Review？

| 優點 | 說明 |
|------|------|
| **隱私** | 代碼不經過 GitHub Actions |
| **成本控制** | 只有你手動觸發時才消耗 API |
| **靈活性** | 可以自訂提示詞 |
| **即時** | 不需等待 CI 完成 |

---

## 相關文檔

| 文檔 | 說明 |
|------|------|
| [CI_CD_AND_TESTING_STRATEGY.md](./CI_CD_AND_TESTING_STRATEGY.md) | CI/CD 與測試策略 |
| [AI_ASSISTANT_GUIDE.md](./AI_ASSISTANT_GUIDE.md) | AI 協作指南 |

---

**文檔建立者**: Claude Code (Opus 4.5)
