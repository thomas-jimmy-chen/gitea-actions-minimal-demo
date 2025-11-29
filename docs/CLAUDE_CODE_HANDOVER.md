# EEBot - Claude Code CLI 交接文檔 - 索引

> **注意**: 本文檔因檔案過大已分段，請選擇對應章節閱讀。
>
> 📚 **文檔分段規則**: 請參考 [DOCUMENT_SEGMENTATION_RULES.md](./DOCUMENT_SEGMENTATION_RULES.md)

**文檔版本**: 2.0
**最後更新**: 2025-11-24（分段處理 + 課程配置優化討論 + 工作日誌規範化）
**項目版本**: 2.0.5
**項目代號**: **Gleipnir** (格萊普尼爾 / 縛狼鎖)
**維護者**: wizard03

---

## 📑 分段導航

### [第 1 段: 基礎架構與使用指南](./CLAUDE_CODE_HANDOVER-1.md)

**內容概要**:
- 🔗 項目代號：Gleipnir
- 🎯 快速開始 (Quick Start for Claude)
- 📖 項目概述
  - 項目資訊
  - 架構模式
  - 工作原理
  - ⭐ 最新功能 (v2.0.5 - 穩定性與配置優化)
- 🏗️ 項目架構
  - 分層架構圖
  - 目錄結構
- 🔧 核心概念
  - 課程配置 (courses.json)
  - 執行流程
  - MitmProxy 機制
- 📝 常見任務指南
  - 添加新課程
  - 添加新考試
  - 修改考試流程
  - 新增新類型的流程
- 🚫 禁止修改清單
- 📋 文檔管理規則
  - CHANGELOG.md 拆分策略
  - 工作日誌檔名規範
- 🔍 關鍵代碼索引
- 💡 Claude Code 特定建議
- 📞 問題排查

**統計**: ~1,005 行，~12,000 tokens

---

### [第 2 段: 進階功能詳解](./CLAUDE_CODE_HANDOVER-2.md)

**內容概要**:
- 🎯 已完成功能：自動答題系統 (Phase 2)
  - 功能概述
  - 題庫資料
  - 考試頁面元素分析
  - 資料庫方案評估
  - 新增檔案架構
  - 核心模組設計
  - 匹配策略
  - SQLite 資料表設計
  - 實作階段規劃
  - 配置選項
  - 風險評估
  - 成功標準
  - ✅ 實作完成總結
- 🚀 智能模式：按課程啟用自動答題 (2025-11-15 更新)
  - 變更概述
  - 配置變更
  - 工作流程變更
  - 技術實作細節
  - 主程式簡化
  - 重要 Bug 修復
  - 測試結果
  - 使用範例
  - 向後相容性
  - 遷移指南
  - 最佳實踐
  - 問題排查
- 🎨 GUI 開發計畫 (2025-11-24 規劃)
  - 概述
  - 技術方案
  - 架構設計
  - 主要功能模組
  - Linux 跨平台支援
- 📚 延伸閱讀
- 📅 最新工作日誌

**統計**: ~1,154 行，~14,900 tokens

---

## 📊 文檔統計

| 項目 | 數值 |
|------|------|
| **原始總行數** | 2,159 行 |
| **原始總大小** | 63.6 KB |
| **原始 Token 數** | 26,923 tokens ❌ (超過 25,000 限制) |
| **分段數** | 2 段 |
| **分段後狀態** | ✅ 每段都在 20,000 tokens 以內 |

---

## 🔗 快速連結

### 從頭閱讀
- 📘 [開始閱讀第 1 段](./CLAUDE_CODE_HANDOVER-1.md) - 基礎架構與使用指南

### 跳轉到特定主題

**基礎架構**（第 1 段）:
- [項目代號 Gleipnir](./CLAUDE_CODE_HANDOVER-1.md#項目代號gleipnir-格萊普尼爾)
- [快速開始](./CLAUDE_CODE_HANDOVER-1.md#快速開始-quick-start-for-claude)
- [最新功能 v2.0.5](./CLAUDE_CODE_HANDOVER-1.md#最新功能-2025-11-17)
- [項目架構](./CLAUDE_CODE_HANDOVER-1.md#項目架構)
- [核心概念](./CLAUDE_CODE_HANDOVER-1.md#核心概念)
- [常見任務指南](./CLAUDE_CODE_HANDOVER-1.md#常見任務指南)
- [禁止修改清單](./CLAUDE_CODE_HANDOVER-1.md#禁止修改清單)
- [文檔管理規則](./CLAUDE_CODE_HANDOVER-1.md#文檔管理規則)

**進階功能**（第 2 段）:
- [自動答題系統](./CLAUDE_CODE_HANDOVER-2.md#已完成功能自動答題系統-phase-2)
- [智能模式](./CLAUDE_CODE_HANDOVER-2.md#智能模式按課程啟用自動答題-2025-11-15-更新)
- [GUI 開發計畫](./CLAUDE_CODE_HANDOVER-2.md#gui-開發計畫-2025-11-24-規劃)
- [延伸閱讀](./CLAUDE_CODE_HANDOVER-2.md#延伸閱讀)
- [最新工作日誌](./CLAUDE_CODE_HANDOVER-2.md#最新工作日誌)

---

## 📚 相關文檔

### 主要文檔
- 📖 [AI_ASSISTANT_GUIDE.md](./AI_ASSISTANT_GUIDE.md) - 通用 AI 助手指南
- 📋 [CHANGELOG.md](./CHANGELOG.md) - 最新版本變更記錄
- 📐 [DOCUMENT_SEGMENTATION_RULES.md](./DOCUMENT_SEGMENTATION_RULES.md) - 文檔分段規則
- 📱 [ANDROID_HYBRID_ARCHITECTURE_EVALUATION.md](./ANDROID_HYBRID_ARCHITECTURE_EVALUATION.md) - Android 混合架構評估報告

### 歷史文檔
- 📦 [changelogs/CHANGELOG_archive_2025.md](./changelogs/CHANGELOG_archive_2025.md) - 2025 年歷史版本

### 最新工作日誌
- 🗓️ [DAILY_WORK_LOG_202511242300.md](./DAILY_WORK_LOG_202511242300.md) - 文檔分段規則建立與執行
- 🗓️ [DAILY_WORK_LOG_202511242157.md](./DAILY_WORK_LOG_202511242157.md) - 課程配置優化討論
- 🗓️ [DAILY_WORK_LOG_20251117.md](./DAILY_WORK_LOG_20251117.md) - 穩定性與配置優化 (v2.0.5)
- 🗓️ [DAILY_WORK_LOG_20251116.md](./DAILY_WORK_LOG_20251116.md) - 安全性增強與智能推薦修復
- 🗓️ [DAILY_WORK_LOG_20251115.md](./DAILY_WORK_LOG_20251115.md) - 自動答題系統完整實作

---

## 🎯 推薦閱讀順序

### 對於新手開發者:
1. [第 1 段](./CLAUDE_CODE_HANDOVER-1.md) - 完整閱讀基礎架構
2. [CHANGELOG.md](./CHANGELOG.md) - 了解最新變更
3. [第 2 段](./CLAUDE_CODE_HANDOVER-2.md) - 深入了解進階功能

### 對於維護開發者:
1. [文檔管理規則](./CLAUDE_CODE_HANDOVER-1.md#文檔管理規則) - 了解文檔規範
2. [最新功能 v2.0.5](./CLAUDE_CODE_HANDOVER-1.md#最新功能-2025-11-17) - 掌握最新變更
3. [禁止修改清單](./CLAUDE_CODE_HANDOVER-1.md#禁止修改清單) - 避免破壞核心功能

### 對於 AI 助手:
1. [快速開始](./CLAUDE_CODE_HANDOVER-1.md#快速開始-quick-start-for-claude) - Claude Code 特定建議
2. [常見任務指南](./CLAUDE_CODE_HANDOVER-1.md#常見任務指南) - 快速上手常見操作
3. [問題排查](./CLAUDE_CODE_HANDOVER-1.md#問題排查) - 解決常見問題

---

## 📝 分段歷史

| 日期 | 操作 | 說明 |
|------|------|------|
| 2025-11-24 | 初次分段 | 原始檔案 2,159 行，26,923 tokens，超過 Read 工具限制 |
| 2025-11-24 | 建立規則 | 制定統一文檔分段規則 ([DOCUMENT_SEGMENTATION_RULES.md](./DOCUMENT_SEGMENTATION_RULES.md)) |
| 2025-11-24 | 完成分段 | 分為 2 段，每段添加導航連結 |

---

## 💡 使用提示

### 對於 Claude Code CLI 用戶:
```bash
# 快速閱讀整份文檔
cat docs/CLAUDE_CODE_HANDOVER-1.md docs/CLAUDE_CODE_HANDOVER-2.md

# 或使用 Read 工具分別讀取
# Read(docs/CLAUDE_CODE_HANDOVER-1.md)
# Read(docs/CLAUDE_CODE_HANDOVER-2.md)
```

### 對於其他 AI 助手:
- 使用 `@file` 或 `@doc` 指令時，請分別引用分段檔案
- 需要完整上下文時，依序閱讀第 1 段和第 2 段

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

*索引建立日期: 2025-11-24 | 專案版本: 2.0.5 | 專案代號: Gleipnir*

---

**Happy Coding! 🚀**

*This project was enhanced with AI assistance (Claude Code CLI)*
