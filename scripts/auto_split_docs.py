#!/usr/bin/env python3
"""
自動文檔分割工具 - Auto Document Splitter
用於自動偵測並分割大型 Markdown 文檔為 AI 友善的可讀取大小

功能：
1. 偵測文件大小並估算 token 數量
2. 自動識別章節邊界（## 或更高階標題）
3. 智能選擇最佳分割點
4. 生成分割文件和導航索引
5. 輸出驗證報告

使用範例：
    python scripts/auto_split_docs.py docs/CLAUDE_CODE_HANDOVER-2.md
    python scripts/auto_split_docs.py docs/CLAUDE_CODE_HANDOVER-2.md --max-tokens 20000
    python scripts/auto_split_docs.py docs/CLAUDE_CODE_HANDOVER-2.md --dry-run
"""

import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import json


@dataclass
class Chapter:
    """章節資訊"""
    level: int  # 標題層級 (1-6)
    title: str  # 章節標題
    line_start: int  # 起始行號
    line_end: int  # 結束行號
    content: List[str]  # 內容行
    estimated_tokens: int  # 估算 token 數


@dataclass
class SplitPoint:
    """分割點資訊"""
    line_number: int  # 分割行號
    chapter_title: str  # 該點的章節標題
    before_tokens: int  # 之前的累計 token
    after_tokens: int  # 之後的累計 token
    score: float  # 分割點品質分數（0-100）


@dataclass
class SplitSegment:
    """分割段落資訊"""
    segment_id: str  # 段落 ID (如 "2A", "2B")
    line_start: int  # 起始行號
    line_end: int  # 結束行號
    estimated_tokens: int  # 估算 token 數
    chapters: List[str]  # 包含的章節標題
    output_file: str  # 輸出檔案名稱


class TokenEstimator:
    """Token 數量估算器"""

    # Token 估算係數
    CHINESE_CHAR_RATIO = 2.5  # 中文字元約 2.5 tokens/字
    ENGLISH_WORD_RATIO = 1.3  # 英文單字約 1.3 tokens/字
    CODE_CHAR_RATIO = 1.5  # 程式碼約 1.5 tokens/字

    @staticmethod
    def estimate_line_tokens(line: str) -> int:
        """估算單行的 token 數量"""
        # 程式碼區塊（``` 包圍）
        if line.strip().startswith('```'):
            return 2

        # 統計字元類型
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', line))
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', line))
        code_chars = len(re.findall(r'[{}()\[\]<>.,;:\'"`]', line))

        # 計算 tokens
        tokens = 0
        tokens += chinese_chars * TokenEstimator.CHINESE_CHAR_RATIO
        tokens += english_words * TokenEstimator.ENGLISH_WORD_RATIO
        tokens += code_chars * TokenEstimator.CODE_CHAR_RATIO

        # 基礎 token（每行至少 1 token）
        return max(1, int(tokens))

    @staticmethod
    def estimate_tokens(lines: List[str]) -> int:
        """估算多行的總 token 數量"""
        return sum(TokenEstimator.estimate_line_tokens(line) for line in lines)


class ChapterParser:
    """章節解析器"""

    @staticmethod
    def parse_chapters(lines: List[str]) -> List[Chapter]:
        """解析文檔中的所有章節"""
        chapters = []
        current_chapter = None

        for i, line in enumerate(lines):
            # 檢測標題（# 開頭）
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if heading_match:
                # 結束上一個章節
                if current_chapter:
                    current_chapter.line_end = i - 1
                    current_chapter.estimated_tokens = TokenEstimator.estimate_tokens(
                        current_chapter.content
                    )
                    chapters.append(current_chapter)

                # 開始新章節
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                current_chapter = Chapter(
                    level=level,
                    title=title,
                    line_start=i,
                    line_end=i,
                    content=[line],
                    estimated_tokens=0
                )
            elif current_chapter:
                current_chapter.content.append(line)

        # 處理最後一個章節
        if current_chapter:
            current_chapter.line_end = len(lines) - 1
            current_chapter.estimated_tokens = TokenEstimator.estimate_tokens(
                current_chapter.content
            )
            chapters.append(current_chapter)

        return chapters


class DocumentSplitter:
    """文檔分割器"""

    def __init__(self, max_tokens: int = 25000, min_tokens: int = 15000):
        self.max_tokens = max_tokens
        self.min_tokens = min_tokens

    def find_split_points(
        self,
        chapters: List[Chapter],
        total_tokens: int
    ) -> List[SplitPoint]:
        """找出最佳分割點"""

        # 如果不需要分割
        if total_tokens <= self.max_tokens:
            return []

        # 計算需要分成幾段
        num_segments = (total_tokens // self.max_tokens) + 1
        ideal_tokens_per_segment = total_tokens / num_segments

        split_points = []
        cumulative_tokens = 0
        last_split = 0

        for i, chapter in enumerate(chapters):
            cumulative_tokens += chapter.estimated_tokens

            # 只考慮二級標題（##）作為分割點
            if chapter.level != 2:
                continue

            # 計算分割品質分數
            tokens_before = cumulative_tokens
            tokens_after = total_tokens - cumulative_tokens

            # 分數計算：
            # 1. 與理想大小的接近程度（50%）
            # 2. 避免過小或過大的段落（30%）
            # 3. 段落大小平衡度（20%）

            ideal_diff = abs(tokens_before - ideal_tokens_per_segment * (len(split_points) + 1))
            ideal_score = max(0, 100 - (ideal_diff / ideal_tokens_per_segment * 100))

            size_score = 100
            if tokens_before < self.min_tokens or tokens_after < self.min_tokens:
                size_score = 0

            balance_score = 100 - abs(tokens_before - tokens_after) / total_tokens * 100

            total_score = ideal_score * 0.5 + size_score * 0.3 + balance_score * 0.2

            split_point = SplitPoint(
                line_number=chapter.line_start,
                chapter_title=chapter.title,
                before_tokens=tokens_before,
                after_tokens=tokens_after,
                score=total_score
            )

            split_points.append(split_point)

        # 選擇最佳分割點
        if not split_points:
            return []

        # 依分數排序並選擇最佳的幾個
        split_points.sort(key=lambda sp: sp.score, reverse=True)

        # 選擇需要的分割點數量
        num_splits = num_segments - 1
        best_splits = split_points[:num_splits]

        # 依行號排序
        best_splits.sort(key=lambda sp: sp.line_number)

        return best_splits

    def create_segments(
        self,
        lines: List[str],
        chapters: List[Chapter],
        split_points: List[SplitPoint],
        base_filename: str
    ) -> List[SplitSegment]:
        """創建分割段落"""

        segments = []
        segment_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

        # 提取基礎檔名和編號（如 CLAUDE_CODE_HANDOVER-2.md -> 2）
        base_match = re.match(r'(.+)-(\d+)(\.md)?$', base_filename)
        if base_match:
            base_name = base_match.group(1)
            base_number = base_match.group(2)
        else:
            base_name = Path(base_filename).stem
            base_number = ""

        # 定義段落邊界
        boundaries = [0] + [sp.line_number for sp in split_points] + [len(lines)]

        for i in range(len(boundaries) - 1):
            start = boundaries[i]
            end = boundaries[i + 1]

            segment_label = f"{base_number}{segment_labels[i]}" if base_number else segment_labels[i]
            segment_lines = lines[start:end]

            # 找出此段落包含的章節
            segment_chapters = [
                ch.title for ch in chapters
                if ch.line_start >= start and ch.line_end < end and ch.level == 2
            ]

            segment = SplitSegment(
                segment_id=segment_label,
                line_start=start + 1,  # 轉為 1-based
                line_end=end,
                estimated_tokens=TokenEstimator.estimate_tokens(segment_lines),
                chapters=segment_chapters,
                output_file=f"{base_name}-{segment_label}.md"
            )

            segments.append(segment)

        return segments


class IndexGenerator:
    """索引生成器"""

    @staticmethod
    def generate_index(
        segments: List[SplitSegment],
        original_file: str,
        total_lines: int,
        total_tokens: int
    ) -> str:
        """生成導航索引內容"""

        base_name = Path(original_file).stem

        index_content = f"""# {base_name} - 索引

> **📑 導航索引** - 本文檔已拆分為多個子段，以便 AI 助手順利讀取

---

## 📚 文檔結構

本段原文檔因篇幅過大（{total_lines:,} 行，{total_tokens:,} tokens），已拆分為以下 {len(segments)} 個子段：

"""

        # 為每個段落生成說明
        for i, segment in enumerate(segments):
            index_content += f"""### 📄 第 {segment.segment_id} 段

**檔案**: [{segment.output_file}](./{segment.output_file})

**行數**: {segment.line_start}-{segment.line_end} ({segment.line_end - segment.line_start + 1:,} 行)

**估算 Tokens**: ~{segment.estimated_tokens:,}

**包含章節**:
"""
            for chapter in segment.chapters[:5]:  # 只列出前 5 個章節
                index_content += f"- {chapter}\n"

            if len(segment.chapters) > 5:
                index_content += f"- (...還有 {len(segment.chapters) - 5} 個章節)\n"

            index_content += "\n"

        index_content += f"""---

## 🎯 閱讀建議

### 對於新接手的 AI 助手

**順序閱讀**:
"""
        for i, segment in enumerate(segments, 1):
            index_content += f"{i}. [{segment.output_file}](./{segment.output_file})\n"

        index_content += f"""
---

## 🔍 文檔統計

| 段落 | 行數 | Token 估算 | 狀態 |
|------|------|-----------|------|
"""

        for segment in segments:
            line_count = segment.line_end - segment.line_start + 1
            index_content += f"| {segment.segment_id} 段 | {line_count:,} 行 | ~{segment.estimated_tokens:,} | ✅ |\n"

        total_line_count = sum(seg.line_end - seg.line_start + 1 for seg in segments)
        index_content += f"| **總計** | **{total_line_count:,} 行** | **~{total_tokens:,}** | ✅ |\n"

        index_content += f"""
---

## 📌 重要提醒

**自動分割資訊**:
- 原文檔：{total_lines:,} 行，~{total_tokens:,} tokens
- Token 限制：25,000 tokens
- 分割段數：{len(segments)} 段
- 生成方式：自動化工具 (auto_split_docs.py)

---

*索引文檔 | 自動生成時間: {{timestamp}} | 工具: auto_split_docs.py*
"""

        return index_content

    @staticmethod
    def add_navigation_header(
        segment: SplitSegment,
        segments: List[SplitSegment],
        content: str,
        base_name: str
    ) -> str:
        """為段落添加導航標頭"""

        current_idx = segments.index(segment)

        # 生成導航資訊
        nav_header = f"""# {base_name} (第 {segment.segment_id} 段)

> **分段資訊**: 本文檔共 {len(segments)} 段
> - 📄 **當前**: 第 {segment.segment_id} 段
"""

        # 下一段連結
        if current_idx < len(segments) - 1:
            next_seg = segments[current_idx + 1]
            nav_header += f"> - ➡️ **下一段**: [{next_seg.output_file}](./{next_seg.output_file})\n"

        # 上一段連結
        if current_idx > 0:
            prev_seg = segments[current_idx - 1]
            nav_header += f"> - ⬅️ **上一段**: [{prev_seg.output_file}](./{prev_seg.output_file})\n"

        # 索引連結
        nav_header += f"> - 📑 **完整索引**: [返回索引](./{base_name}.md)\n"
        nav_header += "\n---\n\n"

        # 段落結尾
        footer = f"\n\n---\n\n**本段結束**\n\n"

        if current_idx < len(segments) - 1:
            next_seg = segments[current_idx + 1]
            footer += f"📍 **繼續閱讀**: [{next_seg.output_file}](./{next_seg.output_file})\n"

        footer += "\n---\n"

        return nav_header + content + footer


def safe_print(text: str = "") -> None:
    """安全的 print 函數，處理 Windows 編碼問題"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Windows CMD 不支援某些字元，移除 emoji 後重試
        import re
        # 移除 emoji 和特殊符號
        clean_text = re.sub(r'[^\x00-\x7F\u4e00-\u9fff]+', '', text)
        print(clean_text)


def analyze_document(file_path: Path) -> Dict:
    """分析文檔並返回詳細資訊"""

    safe_print(f"📖 正在分析文檔: {file_path.name}")
    safe_print("=" * 60)

    # 讀取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 基本資訊
    total_lines = len(lines)
    total_chars = sum(len(line) for line in lines)
    file_size_kb = file_path.stat().st_size / 1024

    safe_print(f"📄 基本資訊:")
    safe_print(f"   - 總行數: {total_lines:,} 行")
    safe_print(f"   - 總字元數: {total_chars:,} 字元")
    safe_print(f"   - 檔案大小: {file_size_kb:.2f} KB")

    # Token 估算
    total_tokens = TokenEstimator.estimate_tokens(lines)
    safe_print(f"   - 估算 Tokens: ~{total_tokens:,} tokens")

    # 章節解析
    chapters = ChapterParser.parse_chapters(lines)
    level_counts = {}
    for ch in chapters:
        level_counts[ch.level] = level_counts.get(ch.level, 0) + 1

    safe_print(f"\n📚 章節結構:")
    for level in sorted(level_counts.keys()):
        safe_print(f"   - Level {level} ({'#' * level}): {level_counts[level]} 個章節")

    # 判斷是否需要分割
    needs_split = total_tokens > 25000

    safe_print(f"\n🔍 分割需求:")
    if needs_split:
        safe_print(f"   ⚠️  需要分割 (超過 25,000 token 限制)")
        recommended_segments = (total_tokens // 20000) + 1
        safe_print(f"   📊 建議分割為: {recommended_segments} 段")
    else:
        safe_print(f"   ✅ 無需分割 (低於 25,000 token 限制)")

    return {
        'lines': lines,
        'total_lines': total_lines,
        'total_tokens': total_tokens,
        'chapters': chapters,
        'needs_split': needs_split,
        'file_size_kb': file_size_kb
    }


def perform_split(
    file_path: Path,
    analysis: Dict,
    max_tokens: int = 25000,
    dry_run: bool = False
) -> None:
    """執行文檔分割"""

    lines = analysis['lines']
    chapters = analysis['chapters']
    total_tokens = analysis['total_tokens']

    safe_print("\n" + "=" * 60)
    safe_print("🔪 開始分割程序")
    safe_print("=" * 60)

    # 創建分割器
    splitter = DocumentSplitter(max_tokens=max_tokens)

    # 尋找分割點
    safe_print("\n🎯 尋找最佳分割點...")
    split_points = splitter.find_split_points(chapters, total_tokens)

    if not split_points:
        safe_print("   ℹ️  無需分割或無法找到合適的分割點")
        return

    safe_print(f"   ✅ 找到 {len(split_points)} 個分割點:\n")
    for i, sp in enumerate(split_points, 1):
        safe_print(f"   {i}. 行 {sp.line_number}: {sp.chapter_title}")
        safe_print(f"      - 之前: ~{sp.before_tokens:,} tokens")
        safe_print(f"      - 之後: ~{sp.after_tokens:,} tokens")
        safe_print(f"      - 分數: {sp.score:.1f}/100")
        safe_print()

    # 創建段落
    safe_print("📝 創建分割段落...")
    base_filename = file_path.stem
    segments = splitter.create_segments(lines, chapters, split_points, base_filename)

    safe_print(f"   ✅ 創建 {len(segments)} 個段落:\n")
    for seg in segments:
        safe_print(f"   - {seg.segment_id} 段: {seg.output_file}")
        safe_print(f"     行數: {seg.line_start}-{seg.line_end} ({seg.line_end - seg.line_start + 1:,} 行)")
        safe_print(f"     Tokens: ~{seg.estimated_tokens:,}")
        safe_print(f"     章節數: {len(seg.chapters)}")
        safe_print()

    if dry_run:
        safe_print("🔍 Dry-run 模式 - 不寫入檔案")
        return

    # 生成文件
    safe_print("💾 寫入分割文件...")
    output_dir = file_path.parent

    for i, segment in enumerate(segments):
        output_path = output_dir / segment.output_file

        # 提取段落內容
        segment_lines = lines[segment.line_start - 1:segment.line_end]
        segment_content = ''.join(segment_lines)

        # 添加導航標頭
        content_with_nav = IndexGenerator.add_navigation_header(
            segment, segments, segment_content, base_filename
        )

        # 寫入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content_with_nav)

        safe_print(f"   ✅ {output_path.name} ({len(segment_lines):,} 行)")

    # 生成索引
    safe_print("\n📑 生成導航索引...")
    index_content = IndexGenerator.generate_index(
        segments, base_filename, analysis['total_lines'], total_tokens
    )

    # 替換時間戳
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    index_content = index_content.replace('{timestamp}', timestamp)

    # 寫入索引（覆蓋原文件）
    index_path = output_dir / f"{base_filename}.md"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)

    safe_print(f"   ✅ {index_path.name} (索引文件)")

    safe_print("\n" + "=" * 60)
    safe_print("✅ 分割完成！")
    safe_print("=" * 60)

    # 生成驗證報告
    safe_print("\n📋 驗證報告:")
    safe_print(f"   - 原始文件: {analysis['total_lines']:,} 行, ~{total_tokens:,} tokens")
    safe_print(f"   - 分割段數: {len(segments)} 段")
    safe_print(f"   - 輸出文件: {len(segments) + 1} 個 ({len(segments)} 段 + 1 索引)")
    safe_print(f"\n   請使用 AI 助手驗證以下文件可正常讀取:")
    for seg in segments:
        safe_print(f"   - {seg.output_file}")
    safe_print(f"   - {base_filename}.md (索引)")


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='自動文檔分割工具 - 將大型 Markdown 文檔分割為 AI 友善的大小',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  %(prog)s docs/CLAUDE_CODE_HANDOVER-2.md
  %(prog)s docs/CLAUDE_CODE_HANDOVER-2.md --max-tokens 20000
  %(prog)s docs/CLAUDE_CODE_HANDOVER-2.md --dry-run
  %(prog)s docs/CLAUDE_CODE_HANDOVER-2.md --analyze-only
        """
    )

    parser.add_argument(
        'file',
        type=str,
        help='要分割的 Markdown 文件路徑'
    )

    parser.add_argument(
        '--max-tokens',
        type=int,
        default=25000,
        help='每段的最大 token 數量 (預設: 25000)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='試運行模式 - 只分析不寫入文件'
    )

    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='僅分析文檔不執行分割'
    )

    args = parser.parse_args()

    # 檢查文件是否存在
    file_path = Path(args.file)
    if not file_path.exists():
        safe_print(f"❌ 錯誤: 文件不存在 - {file_path}")
        return 1

    if not file_path.suffix == '.md':
        safe_print(f"❌ 錯誤: 只支援 Markdown 文件 (.md)")
        return 1

    # 分析文檔
    analysis = analyze_document(file_path)

    # 如果只是分析，到此結束
    if args.analyze_only:
        safe_print("\n✅ 分析完成")
        return 0

    # 如果需要分割，執行分割
    if analysis['needs_split']:
        perform_split(file_path, analysis, args.max_tokens, args.dry_run)
    else:
        safe_print("\n✅ 文檔無需分割")

    return 0


if __name__ == '__main__':
    exit(main())
