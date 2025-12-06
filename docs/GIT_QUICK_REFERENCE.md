# Git 快速參考手冊

> **⚡ 常用 Git 命令與配置**
> 專為 EEBot 專案設計的 Git 操作指南

**最後更新**: 2025-12-04
**專案**: EEBot (Gleipnir)

---

## 🔐 認證配置

### 自動儲存認證 ⭐

```bash
# 配置 Git 自動儲存認證（避免每次輸入密碼）
git config --global credential.helper store
```

**說明**:
- ✅ 首次推送時輸入一次帳號密碼
- ✅ 認證資訊自動儲存到 `~/.git-credentials`
- ✅ 後續推送自動使用儲存的認證
- ⚠️ 認證以明文儲存，請確保系統安全

---

### 檢查配置

```bash
# 查看 credential helper 配置
git config --global credential.helper

# 查看所有 Git 全局配置
git config --global --list
```

---

### 清除認證

```bash
# 刪除儲存的認證檔案
rm ~/.git-credentials

# 或使用 Git 命令
git credential reject
```

---

## 🌐 遠程倉庫管理

### 查看遠程倉庫

```bash
# 查看所有遠程倉庫
git remote -v
```

**EEBot 專案遠程倉庫**:
- `github`: https://github.com/thomas-jimmy-chen/eebot-ai-refactor.git
- `origin`: http://localhost:3001/user123456/eebot-ai-refactor.git (本地測試)

---

### 推送到遠程倉庫

```bash
# 推送到 GitHub
git push github main

# 推送到 origin（如果可用）
git push origin main

# 推送所有分支
git push github --all

# 強制推送（謹慎使用）
git push github main --force
```

---

## 📝 提交管理

### 標準提交流程

```bash
# 1. 查看狀態
git status

# 2. 查看變更
git diff

# 3. 添加文件
git add docs/

# 4. 創建提交
git commit -m "docs: 更新文檔

詳細說明...

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 5. 推送到遠程
git push github main
```

---

### 查看提交歷史

```bash
# 查看最近 5 次提交
git log -5 --oneline

# 查看詳細提交歷史
git log --oneline --graph --all

# 查看特定文件的提交歷史
git log --oneline -- docs/CHANGELOG.md
```

---

### 撤銷操作

```bash
# 撤銷未暫存的變更
git restore <file>

# 撤銷已暫存的文件
git restore --staged <file>

# 撤銷最後一次提交（保留變更）
git reset --soft HEAD~1

# 撤銷最後一次提交（丟棄變更）⚠️
git reset --hard HEAD~1
```

---

## 🌿 分支管理

### 基本操作

```bash
# 查看所有分支
git branch -a

# 創建新分支
git branch feature/new-feature

# 切換分支
git checkout feature/new-feature

# 創建並切換分支（一步完成）
git checkout -b feature/new-feature

# 刪除本地分支
git branch -d feature/old-feature

# 強制刪除本地分支⚠️
git branch -D feature/old-feature
```

---

### 合併分支

```bash
# 切換到主分支
git checkout main

# 合併功能分支
git merge feature/new-feature

# 推送合併後的主分支
git push github main
```

---

## 🔍 查看變更

### 比較差異

```bash
# 查看工作區變更（未暫存）
git diff

# 查看已暫存的變更
git diff --staged

# 查看變更統計
git diff --stat

# 比較兩個提交
git diff HEAD~1 HEAD
```

---

### 查看文件狀態

```bash
# 簡潔狀態
git status -s

# 詳細狀態
git status

# 忽略未追蹤文件
git status -uno
```

---

## 🛠️ 常見問題解決

### 問題 1: 推送失敗（認證錯誤）

```bash
# 解決方案：配置自動儲存認證
git config --global credential.helper store

# 或使用更安全的方式（Windows）
git config --global credential.helper manager
```

---

### 問題 2: 合併衝突

```bash
# 1. 查看衝突文件
git status

# 2. 手動編輯衝突文件（解決 <<<<<<<, =======, >>>>>>> 標記）

# 3. 標記為已解決
git add <resolved-file>

# 4. 完成合併
git commit
```

---

### 問題 3: 不小心提交了敏感資訊

```bash
# 撤銷最後一次提交（保留變更）
git reset --soft HEAD~1

# 編輯文件移除敏感資訊

# 重新提交
git add .
git commit -m "docs: 更新文檔（移除敏感資訊）"
```

---

### 問題 4: 需要同步遠程最新變更

```bash
# 拉取最新變更
git pull github main

# 如果有衝突，解決後再推送
git push github main
```

---

## 📚 進階操作

### 儲藏變更（Stash）

```bash
# 暫存當前變更
git stash

# 查看所有 stash
git stash list

# 恢復最近的 stash
git stash pop

# 恢復特定 stash
git stash apply stash@{0}

# 刪除 stash
git stash drop stash@{0}
```

---

### Cherry-pick

```bash
# 將特定提交應用到當前分支
git cherry-pick <commit-hash>

# Cherry-pick 多個提交
git cherry-pick <commit1> <commit2>
```

---

### 標籤管理

```bash
# 創建標籤
git tag v2.1.0

# 創建帶註釋的標籤
git tag -a v2.1.0 -m "Release version 2.1.0"

# 推送標籤到遠程
git push github v2.1.0

# 推送所有標籤
git push github --tags

# 刪除本地標籤
git tag -d v2.1.0

# 刪除遠程標籤
git push github --delete v2.1.0
```

---

## 🎯 EEBot 專案特定命令

### 提交文檔變更

```bash
# 添加所有文檔變更
git add docs/

# 創建提交（使用專案格式）
git commit -m "docs: 新增 API 直接調用模式文檔

核心交付成果：
• 完整重構提案
• 工作日誌
• 快速參考手冊

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 推送到 GitHub
git push github main
```

---

### 檢查文檔大小

```bash
# 運行文檔大小檢查工具
python tools/check_doc_size.py

# Git 提交前會自動運行此檢查（pre-commit hook）
```

---

## 🔗 相關資源

### 官方文檔
- [Git 官方文檔](https://git-scm.com/doc)
- [GitHub 使用指南](https://docs.github.com/)

### EEBot 專案文檔
- [配置管理指南](./CONFIGURATION_MANAGEMENT_GUIDE.md)
- [開發指南](./CLAUDE_CODE_HANDOVER-1.md)
- [CHANGELOG](./CHANGELOG.md)

---

## ✅ 快速檢查清單

使用本文檔後，你應該能夠：

- [ ] 配置 Git 自動儲存認證
- [ ] 查看和管理遠程倉庫
- [ ] 創建和推送提交
- [ ] 查看提交歷史和變更
- [ ] 處理合併衝突
- [ ] 使用分支進行開發
- [ ] 解決常見的 Git 問題

---

**維護者**: wizard03 (with Claude Code CLI)
**專案**: EEBot (Gleipnir)
**最後更新**: 2025-12-04

---

**Happy Git! 🚀**
