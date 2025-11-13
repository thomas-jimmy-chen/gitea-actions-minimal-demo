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

## 🚀 快速开始

### 给 AI 助手的指令

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
| CHANGELOG.md | ~12 KB | ~310 行 | 2025-01-13 |
| AI_ASSISTANT_GUIDE.md | ~35 KB | ~850 行 | 2025-01-13 |
| CLAUDE_CODE_HANDOVER.md | ~25 KB | ~520 行 | 2025-01-13 |

---

## 🎯 关键信息快速查找

### 如何添加新课程？
→ **AI_ASSISTANT_GUIDE.md** - Task 1 章节

### 如何添加新考试？
→ **AI_ASSISTANT_GUIDE.md** - Task 2 章节

### 考试流程为什么失败？
→ **AI_ASSISTANT_GUIDE.md** - Issue 4 & 5 章节
→ **CHANGELOG.md** - 修复记录章节

### 哪些文件不能修改？
→ **AI_ASSISTANT_GUIDE.md** - "DO NOT MODIFY" 章节
→ **CLAUDE_CODE_HANDOVER.md** - "禁止修改清单" 章节

### 最新的修改是什么？
→ **CHANGELOG.md** - 修复记录 & 今日完成总结

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
**最后更新**: 2025-01-13
**文档版本**: 1.2

---

## 🔗 相关链接

- **主程序入口**: `../main.py`
- **交互菜单**: `../menu.py`
- **课程配置**: `../data/courses.json`
- **考试页面操作**: `../src/pages/exam_detail_page.py`
- **考试流程场景**: `../src/scenarios/exam_learning.py`

---

**快速命令**:
```bash
# 查看所有文档
ls D:\Dev\eebot\docs\

# 阅读主要文档
cat D:\Dev\eebot\docs\CHANGELOG.md
cat D:\Dev\eebot\docs\AI_ASSISTANT_GUIDE.md
cat D:\Dev\eebot\docs\CLAUDE_CODE_HANDOVER.md
```
