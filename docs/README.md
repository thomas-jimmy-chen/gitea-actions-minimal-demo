# EEBot 项目文档索引

> **快速访问项目交接文档**

## 📚 文档列表

### 1. 修改历史与变更日志
📄 **[CHANGELOG.md](./CHANGELOG.md)**
- 完整的修改历史
- 最新功能和 Bug 修复
- 今日完成总结
- 版本历史

**适用于**: 所有人
**推荐优先级**: ⭐⭐⭐⭐⭐

---

### 2. AI 助手通用交接指南
📄 **[AI_ASSISTANT_GUIDE.md](./AI_ASSISTANT_GUIDE.md)**
- 项目完整概览
- 架构图表和文件树
- 常见任务指南
- 代码示例
- 故障排除

**适用于**: Claude Code CLI, Cursor, GitHub Copilot CLI, Cody, Tabnine 等所有 AI 编程助手
**推荐优先级**: ⭐⭐⭐⭐⭐

---

### 3. Claude Code CLI 专用指南
📄 **[CLAUDE_CODE_HANDOVER.md](./CLAUDE_CODE_HANDOVER.md)**
- Claude Code CLI 优化格式
- 快速开始指南
- 关键文件路径
- 禁止修改清单
- Claude 特定建议

**适用于**: Claude Code CLI
**推荐优先级**: ⭐⭐⭐⭐⭐ (对 Claude)

---

### 4. AI 助手快速读取指南 ✨ (NEW)
📄 **[AI助手快速读取交接文档.md](./AI助手快速讀取交接文檔.md)**
- 各种 AI 工具的提示词范例
- 按情境分类的快速指令
- AI 工具最佳实践（Claude Code, Cursor, Copilot 等）
- 验证 AI 是否正确读取文档
- 常见问题 FAQ

**适用于**: 所有 AI 助手（特别是新手）
**推荐优先级**: ⭐⭐⭐⭐⭐
**使用场景**: 每次开始新对话时参考

---

### 5. 每日工作日志 ✨ (NEW)
📄 **[DAILY_WORK_LOG_20251114.md](./DAILY_WORK_LOG_20251114.md)**
- 2025-01-14 完整工作记录（约 800 行）
- 考卷元素定位测试功能实作详细过程
- 技术讨论与决策（JSON vs SQLite, 执行策略, 匹配算法）
- 问题解决记录与测试结果
- 下一阶段规划（Phase 1-5，11-16 小时预估）
- 经验教训与改进建议

**适用于**: 开发者、项目维护者、AI 助手
**推荐优先级**: ⭐⭐⭐⭐ (了解最新开发进展)
**使用场景**: 查看详细开发过程、技术决策依据

---

### 6. 元素定位测试修改总结
📄 **[MODIFICATION_SUMMARY_20250114.md](./MODIFICATION_SUMMARY_20250114.md)**
- 考卷元素定位测试整合修改总结
- 修改目标与执行流程
- 代码修改详情（`exam_learning.py`）
- 输出文档格式说明
- 定位元素清单与验证方法
- 注意事项与后续步骤

**适用于**: 开发者、需要了解元素定位实现细节者
**推荐优先级**: ⭐⭐⭐ (技术实现参考)
**使用场景**: 理解元素定位测试的实现方式

---

### 7. 考试页面元素定位策略
📄 **[EXAM_PAGE_LOCATORS.md](./EXAM_PAGE_LOCATORS.md)**
- 考试页面 HTML 结构分析
- 元素定位策略（CSS Selector vs XPath）
- Selenium 代码示例
- 关键元素定位器清单
- 最佳实践与注意事项

**适用于**: 开发者、需要实现自动答题功能者
**推荐优先级**: ⭐⭐⭐⭐ (技术实现必读)
**使用场景**: 开发考试页面自动化功能

---

## 🚀 快速开始

### 给 AI 助手的指令

#### 🆕 最简单方式（推荐）
```
读取专案交接文档
```
**说明**: 详细的提示词范例请参考 **[AI助手快速读取交接文档.md](./AI助手快速讀取交接文檔.md)**

#### Claude Code CLI
```
@workspace 读取项目交接文档
或
请读取 D:\Dev\eebot\docs\CLAUDE_CODE_HANDOVER.md
```

#### Cursor
```
Ctrl+L: "读取 docs 目录的交接文档"
```

#### GitHub Copilot CLI
```bash
gh copilot explain "D:\Dev\eebot\docs"
```

---

## 📋 推荐阅读顺序

### 🔰 首次接触项目
1. ✅ **CHANGELOG.md** - 了解项目最新状态
2. ✅ **AI_ASSISTANT_GUIDE.md** (或 CLAUDE_CODE_HANDOVER.md) - 理解项目结构
3. ✅ `data/courses.json` - 查看配置格式
4. ✅ `src/scenarios/exam_learning.py` - 理解考试流程

### 🔧 需要修改代码
1. ✅ **CHANGELOG.md** - 查看最新修改
2. ✅ **AI_ASSISTANT_GUIDE.md** - 查看「禁止修改清单」
3. ✅ 相关源代码文件
4. ✅ **AI_ASSISTANT_GUIDE.md** - 参考「常见任务指南」

### 🐛 遇到问题
1. ✅ **CHANGELOG.md** - 查看「已知限制」
2. ✅ **AI_ASSISTANT_GUIDE.md** - 查看「故障排除」章节
3. ✅ **CLAUDE_CODE_HANDOVER.md** - 查看「问题排查」章节

---

## 📊 文档统计

| 文档 | 大小 | 行数 | 最后更新 |
|------|------|------|----------|
| CHANGELOG.md | ~50 KB | ~1,000 行 | 2025-01-14 |
| AI_ASSISTANT_GUIDE.md | ~75 KB | ~1,320 行 | 2025-01-14 |
| CLAUDE_CODE_HANDOVER.md | ~45 KB | ~840 行 | 2025-01-14 |
| AI助手快速读取交接文档.md | ~22 KB | ~560 行 | 2025-01-14 |
| DAILY_WORK_LOG_20251114.md | ~55 KB | ~800 行 | 2025-01-14 |
| MODIFICATION_SUMMARY_20250114.md | ~18 KB | ~327 行 | 2025-01-14 |
| EXAM_PAGE_LOCATORS.md | ~15 KB | ~280 行 | 2025-01-14 |

---

## 🎯 关键信息快速查找

### 如何让 AI 读取交接文档？✨
→ **AI助手快速读取交接文档.md** - 提示词范例大全

### 如何添加新课程？
→ **AI_ASSISTANT_GUIDE.md** - Task 1 章节

### 如何添加新考试？
→ **AI_ASSISTANT_GUIDE.md** - Task 2 章节

### 自动答题功能的规划是什么？✨
→ **AI_ASSISTANT_GUIDE.md** - "Planned Features: Auto-Answer System" 章节
→ **CLAUDE_CODE_HANDOVER.md** - "规划中功能：自动答题系统" 章节
→ **CHANGELOG.md** - [2025-01-14] 条目

### 考试流程为什么失败？
→ **AI_ASSISTANT_GUIDE.md** - Issue 4 & 5 章节
→ **CHANGELOG.md** - 修复记录章节

### 哪些文件不能修改？
→ **AI_ASSISTANT_GUIDE.md** - "DO NOT MODIFY" 章节
→ **CLAUDE_CODE_HANDOVER.md** - "禁止修改清单" 章节

### 最新的修改是什么？
→ **CHANGELOG.md** - 修复记录 & 今日完成总结

### 如何定位考试页面的题目和选项？✨
→ **EXAM_PAGE_LOCATORS.md** - 元素定位策略详细说明
→ **MODIFICATION_SUMMARY_20250114.md** - 实现细节与代码示例

### 元素定位测试是如何实现的？✨
→ **MODIFICATION_SUMMARY_20250114.md** - 完整修改总结
→ **DAILY_WORK_LOG_20251114.md** - 开发过程记录
→ `src/scenarios/exam_learning.py` - 源代码实现

### JSON vs SQLite 性能对比结果是什么？✨
→ **DAILY_WORK_LOG_20251114.md** - 讨论 1: 题库存储方案性能对比
→ **CHANGELOG.md** - [2025-01-14] 技术讨论章节

### 自动答题的执行策略是什么？✨
→ **DAILY_WORK_LOG_20251114.md** - 讨论 2: 自动答题执行策略
→ **CHANGELOG.md** - [2025-01-14] 三阶段执行策略

### 今日完成了哪些工作？✨
→ **DAILY_WORK_LOG_20251114.md** - 完整工作时间线（6 大任务）
→ **CHANGELOG.md** - [2025-01-14] 实作摘要

---

## 💡 提示

### 给 AI 助手
- 使用 `@workspace` 或 `@file` 快速索引文档
- 优先阅读 CHANGELOG.md 了解最新状态
- 修改代码前先查看「禁止修改清单」

### 给人类开发者
- 所有文档都是 Markdown 格式，可用任何文本编辑器打开
- 推荐使用支持 Markdown 预览的编辑器（VS Code, Typora 等）
- 文档包含大量代码示例，可直接复制使用

---

## 📞 联系方式

**项目维护者**: wizard03
**最后更新**: 2025-01-14
**文档版本**: 1.4

---

## 🔗 相关链接

- **主程序入口**: `../main.py`
- **交互菜单**: `../menu.py`
- **课程配置**: `../data/courses.json`
- **考试页面操作**: `../src/pages/exam_detail_page.py`
- **考试流程场景**: `../src/scenarios/exam_learning.py`
- **元素定位测试脚本**: `../test_exam_locators.py` (独立测试参考)

---

**快速命令**:
```bash
# 查看所有文档
ls D:\Dev\eebot\docs\

# 阅读主要文档
cat D:\Dev\eebot\docs\CHANGELOG.md
cat D:\Dev\eebot\docs\AI_ASSISTANT_GUIDE.md
cat D:\Dev\eebot\docs\CLAUDE_CODE_HANDOVER.md

# 🆕 查看 AI 读取指南（推荐新手阅读）
cat D:\Dev\eebot\docs\AI助手快速讀取交接文檔.md

# ✨ 查看最新开发记录（2025-01-14）
cat D:\Dev\eebot\docs\DAILY_WORK_LOG_20251114.md
cat D:\Dev\eebot\docs\MODIFICATION_SUMMARY_20250114.md
cat D:\Dev\eebot\docs\EXAM_PAGE_LOCATORS.md

# 查看测试输出结果
cat D:\Dev\eebot\logs\exam_locator_test_20251114_*.txt
```
