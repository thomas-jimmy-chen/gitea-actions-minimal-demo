# EEBot - AI Assistant Handover Guide - 索引

> **注意**: 本文檔因檔案過大已分段，請選擇對應章節閱讀。
>
> 📚 **文檔分段規則**: 請參考 [DOCUMENT_SEGMENTATION_RULES.md](./DOCUMENT_SEGMENTATION_RULES.md)

**文檔版本**: 1.4
**最後更新**: 2025-01-17 (分段處理: 2025-11-27)
**項目版本**: 2.0.3
**項目代號**: **Gleipnir** (格萊普尼爾 / 縛狼鎖)
**維護者**: wizard03

---

## 📑 分段導航

### [第 1 段: 基礎架構、配置與使用指南](./AI_ASSISTANT_GUIDE-1.md)

**內容概要**:
- 🔗 Project Codename: Gleipnir
- 🎯 Quick Project Overview
- 🆕 Latest Updates Summary
- 📁 Project Structure (Tree View)
- 🏗️ Architecture Diagram
- 📝 Core Configuration: courses.json
- 🔧 How It Works
- 🚀 Usage Guide
- 📖 Code Examples
- 📋 Common Tasks & How-To
- 🚫 DO NOT MODIFY - Protected Files
- 🔍 Quick File Locator
- 📅 Modification History
- 🛠️ Development Guidelines
- 🐛 Troubleshooting
- 💡 Tips for AI Assistants
- 🎯 Implemented Features: Auto-Answer System (Phase 2)

**統計**: ~1,520 行，~48 KB，~13,300 tokens

---

### [第 2 段: 最新更新與功能詳解](./AI_ASSISTANT_GUIDE-2.md)

**內容概要**:
- ⭐ NEW: Screenshot Timing Fix (2025-01-17)
- ⭐ NEW: One-Click Auto-Execution (2025-01-17)
- ⭐ NEW: Cross-Platform Font Support (2025-01-17)
- ⭐ Smart Recommendation Bug Fix (2025-11-16 Evening)
- ⭐ NEW: Option-Based Matching Logic (2025-11-16 Morning)
- 🎯 Smart Mode: Per-Course Auto-Answer (Updated 2025-11-15)
- 📞 Support & Resources
- ✅ Pre-Modification Checklist

**統計**: ~1,033 行，~32 KB，~8,900 tokens

---

## 📊 文檔統計

| 項目 | 數值 |
|------|------|
| **原始總行數** | 2,554 行 |
| **原始總大小** | 80.6 KB |
| **原始 Token 數** | 22,307 tokens ❌ (超過 25,000 限制) |
| **分段數** | 2 段 |
| **分段後狀態** | ✅ 每段都在 20,000 tokens 以內 |

---

## 🔗 快速連結

### 從頭閱讀
- 📘 [開始閱讀第 1 段](./AI_ASSISTANT_GUIDE-1.md) - 基礎架構、配置與使用指南

### 跳轉到特定主題

**基礎架構**（第 1 段）:
- [Project Codename: Gleipnir](./AI_ASSISTANT_GUIDE-1.md#-project-codename-gleipnir)
- [Quick Project Overview](./AI_ASSISTANT_GUIDE-1.md#-quick-project-overview)
- [Project Structure](./AI_ASSISTANT_GUIDE-1.md#-project-structure-tree-view)
- [Architecture Diagram](./AI_ASSISTANT_GUIDE-1.md#-architecture-diagram)
- [Core Configuration](./AI_ASSISTANT_GUIDE-1.md#-core-configuration-coursesjson)
- [How It Works](./AI_ASSISTANT_GUIDE-1.md#-how-it-works)
- [Usage Guide](./AI_ASSISTANT_GUIDE-1.md#-usage-guide)
- [Common Tasks](./AI_ASSISTANT_GUIDE-1.md#-common-tasks--how-to)
- [Protected Files](./AI_ASSISTANT_GUIDE-1.md#-do-not-modify---protected-files)
- [Auto-Answer System](./AI_ASSISTANT_GUIDE-1.md#-implemented-features-auto-answer-system-phase-2)

**最新更新**（第 2 段）:
- [Screenshot Timing Fix](./AI_ASSISTANT_GUIDE-2.md#-new-screenshot-timing-fix-2025-01-17)
- [One-Click Auto-Execution](./AI_ASSISTANT_GUIDE-2.md#-new-one-click-auto-execution-2025-01-17)
- [Cross-Platform Font Support](./AI_ASSISTANT_GUIDE-2.md#-new-cross-platform-font-support-2025-01-17)
- [Smart Mode](./AI_ASSISTANT_GUIDE-2.md#-smart-mode-per-course-auto-answer-updated-2025-11-15)

---

## 📚 相關文檔

### 主要文檔
- 📖 [CLAUDE_CODE_HANDOVER.md](./CLAUDE_CODE_HANDOVER.md) - Claude Code CLI 專用交接文檔
- 📋 [CHANGELOG.md](./CHANGELOG.md) - 最新版本變更記錄
- 📐 [DOCUMENT_SEGMENTATION_RULES.md](./DOCUMENT_SEGMENTATION_RULES.md) - 文檔分段規則

---

## 🎯 推薦閱讀順序

### 對於新手開發者:
1. [第 1 段](./AI_ASSISTANT_GUIDE-1.md) - 完整閱讀基礎架構
2. [CHANGELOG.md](./CHANGELOG.md) - 了解最新變更
3. [第 2 段](./AI_ASSISTANT_GUIDE-2.md) - 深入了解最新功能

### 對於維護開發者:
1. [第 2 段](./AI_ASSISTANT_GUIDE-2.md) - 直接查看最新更新
2. [Protected Files](./AI_ASSISTANT_GUIDE-1.md#-do-not-modify---protected-files) - 避免破壞核心功能
3. [Development Guidelines](./AI_ASSISTANT_GUIDE-1.md#-development-guidelines) - 遵循開發規範

### 對於 AI 助手:
1. [Quick Project Overview](./AI_ASSISTANT_GUIDE-1.md#-quick-project-overview) - 快速了解專案
2. [Tips for AI Assistants](./AI_ASSISTANT_GUIDE-1.md#-tips-for-ai-assistants) - AI 專用建議
3. [Common Tasks](./AI_ASSISTANT_GUIDE-1.md#-common-tasks--how-to) - 快速上手常見操作

---

## 📝 分段歷史

| 日期 | 操作 | 說明 |
|------|------|------|
| 2025-11-27 | 初次分段 | 原始檔案 2,554 行，22,307 tokens，超過 Read 工具限制 |
| 2025-11-27 | 完成分段 | 分為 2 段，每段添加導航連結 |

---

## 🔄 維護指南

### 何時需要重新分段?

當任一分段檔案符合以下條件時：
- ✅ Token 數量 ≥ 20,000
- ✅ 檔案大小 ≥ 60 KB
- ✅ 行數 ≥ 2,000

### 如何更新分段?

1. 編輯對應的分段檔案
2. 若新增內容導致超過閾值，執行重新分段
3. 更新本索引檔案的內容概要
4. 更新相關文檔的索引連結

詳細規則請參考: [DOCUMENT_SEGMENTATION_RULES.md](./DOCUMENT_SEGMENTATION_RULES.md)

---

## 💡 使用提示

### 對於 Claude Code CLI 用戶:
```bash
# 快速閱讀整份文檔
cat docs/AI_ASSISTANT_GUIDE-1.md docs/AI_ASSISTANT_GUIDE-2.md

# 或使用 Read 工具分別讀取
# Read(docs/AI_ASSISTANT_GUIDE-1.md)
# Read(docs/AI_ASSISTANT_GUIDE-2.md)
```

### 對於其他 AI 助手:
- 使用 `@file` 或 `@doc` 指令時，請分別引用分段檔案
- 需要完整上下文時，依序閱讀第 1 段和第 2 段

---

*索引建立日期: 2025-11-27 | 專案版本: 2.0.3 | 專案代號: Gleipnir*

---

**Happy Coding! 🚀**

*This project was enhanced with AI assistance (Claude Code CLI)*
