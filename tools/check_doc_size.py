#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文檔大小檢測工具 (Document Size Checker)

功能：
1. 自動檢測文檔大小（行數、檔案大小、Token 估算）
2. 根據 DOCUMENT_SEGMENTATION_RULES.md 判斷是否需要分段
3. 生成詳細的檢測報告

作者：wizard03 (with Claude Code CLI)
創建日期：2025-11-27
版本：1.0
"""

import os
import sys
import glob
from pathlib import Path
from typing import Dict, List, Tuple

# ============================================================================
# 常數定義
# ============================================================================

# 分段閾值（根據 DOCUMENT_SEGMENTATION_RULES.md）
THRESHOLDS = {
    "tokens": 20000,  # ≥ 20,000 tokens
    "bytes": 60 * 1024,  # ≥ 60 KB (61,440 bytes)
    "lines": 2000  # ≥ 2,000 行
}

# Token 估算係數（粗略估算：1 token ≈ 3.5 bytes 中文，4 bytes 英文）
TOKEN_ESTIMATE_RATIO = 3.7  # 平均值

# 需要檢查的文檔目錄
DOC_DIRECTORIES = ["docs"]

# 需要檢查的文件類型
FILE_PATTERNS = ["*.md"]

# 排除的文件（不需要檢查）
EXCLUDED_FILES = {
    "README.md",  # 簡要說明，通常較短
    "LICENSE",  # 授權條款
    "LICENSE.md",
    ".gitignore",
}

# 排除的文件名模式（使用通配符）
EXCLUDED_PATTERNS = [
    "CHANGELOG_archive_*.md",  # 歸檔文件不需要再次檢查
    "DAILY_WORK_LOG_*.md",  # 工作日誌使用獨立規則
]

# ============================================================================
# 工具函數
# ============================================================================

def get_file_stats(file_path: str) -> Dict[str, int]:
    """
    獲取文件統計信息

    Args:
        file_path: 文件路徑

    Returns:
        包含統計信息的字典：
        - lines: 行數
        - bytes: 檔案大小（bytes）
        - tokens_estimate: Token 估算值
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.count('\n') + 1
            byte_size = len(content.encode('utf-8'))
            tokens_estimate = int(byte_size / TOKEN_ESTIMATE_RATIO)

        return {
            "lines": lines,
            "bytes": byte_size,
            "tokens_estimate": tokens_estimate
        }
    except Exception as e:
        print(f"[WARNING] 無法讀取文件 {file_path}: {e}")
        return {"lines": 0, "bytes": 0, "tokens_estimate": 0}


def should_segment(stats: Dict[str, int]) -> Tuple[bool, List[str]]:
    """
    判斷是否需要分段

    Args:
        stats: 文件統計信息

    Returns:
        (是否需要分段, 超過閾值的指標列表)
    """
    exceeded = []

    if stats["tokens_estimate"] >= THRESHOLDS["tokens"]:
        exceeded.append(f"Token 數量: {stats['tokens_estimate']:,} >= {THRESHOLDS['tokens']:,}")

    if stats["bytes"] >= THRESHOLDS["bytes"]:
        kb = stats["bytes"] / 1024
        threshold_kb = THRESHOLDS["bytes"] / 1024
        exceeded.append(f"檔案大小: {kb:.1f} KB >= {threshold_kb:.0f} KB")

    if stats["lines"] >= THRESHOLDS["lines"]:
        exceeded.append(f"行數: {stats['lines']:,} >= {THRESHOLDS['lines']:,}")

    return (len(exceeded) > 0, exceeded)


def is_excluded(file_path: str) -> bool:
    """
    判斷文件是否應該被排除

    Args:
        file_path: 文件路徑

    Returns:
        是否應該排除
    """
    file_name = os.path.basename(file_path)

    # 檢查完全匹配
    if file_name in EXCLUDED_FILES:
        return True

    # 檢查模式匹配
    for pattern in EXCLUDED_PATTERNS:
        if glob.fnmatch.fnmatch(file_name, pattern):
            return True

    return False


def format_size(bytes_size: int) -> str:
    """
    格式化檔案大小

    Args:
        bytes_size: 檔案大小（bytes）

    Returns:
        格式化的字串（KB 或 MB）
    """
    if bytes_size < 1024 * 1024:  # < 1 MB
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.2f} MB"


def check_single_file(file_path: str) -> Dict:
    """
    檢查單個文件

    Args:
        file_path: 文件路徑

    Returns:
        檢查結果字典
    """
    stats = get_file_stats(file_path)
    needs_segment, exceeded = should_segment(stats)

    return {
        "path": file_path,
        "stats": stats,
        "needs_segment": needs_segment,
        "exceeded": exceeded
    }


def scan_documents() -> List[Dict]:
    """
    掃描所有文檔

    Returns:
        檢查結果列表
    """
    results = []

    for directory in DOC_DIRECTORIES:
        if not os.path.exists(directory):
            print(f"[WARNING] 目錄不存在: {directory}")
            continue

        for pattern in FILE_PATTERNS:
            file_pattern = os.path.join(directory, "**", pattern)
            for file_path in glob.glob(file_pattern, recursive=True):
                if is_excluded(file_path):
                    continue

                result = check_single_file(file_path)
                results.append(result)

    return results


# ============================================================================
# 報告生成
# ============================================================================

def print_report(results: List[Dict]):
    """
    輸出檢測報告

    Args:
        results: 檢查結果列表
    """
    print("=" * 100)
    print("[INFO] EEBot 文檔大小檢測報告")
    print("=" * 100)
    print()

    # 統計
    total_files = len(results)
    needs_segment = [r for r in results if r["needs_segment"]]
    ok_files = total_files - len(needs_segment)

    print(f"[統計] 總文檔數: {total_files}")
    print(f"[OK] 正常文檔: {ok_files}")
    print(f"[WARNING] 需要分段: {len(needs_segment)}")
    print()
    print("=" * 100)
    print()

    # 詳細結果
    if len(needs_segment) > 0:
        print("[WARNING] 以下文檔超過閾值，建議分段:")
        print("-" * 100)
        for result in needs_segment:
            rel_path = os.path.relpath(result["path"])
            stats = result["stats"]

            print(f"\n[FILE] {rel_path}")
            print(f"   行數: {stats['lines']:,} 行")
            print(f"   大小: {format_size(stats['bytes'])}")
            print(f"   Token (估算): {stats['tokens_estimate']:,}")
            print(f"   超過閾值:")
            for exceeded in result["exceeded"]:
                print(f"      * {exceeded}")
        print()
        print("=" * 100)
        print()

    # 正常文檔
    if ok_files > 0:
        print("[OK] 以下文檔大小正常:")
        print("-" * 100)
        for result in results:
            if not result["needs_segment"]:
                rel_path = os.path.relpath(result["path"])
                stats = result["stats"]
                print(f"   {rel_path:60s} | {stats['lines']:>6,} 行 | {format_size(stats['bytes']):>10s} | {stats['tokens_estimate']:>7,} tokens")
        print()
        print("=" * 100)
        print()

    # 建議
    if len(needs_segment) > 0:
        print("[建議操作]:")
        print("-" * 100)
        print("1. 對於超過閾值的文檔，請參考 DOCUMENT_SEGMENTATION_RULES.md 執行分段")
        print("2. CHANGELOG.md 應使用歸檔策略（舊版本移至 changelogs/CHANGELOG_archive_YYYY.md）")
        print("3. 工作日誌使用獨立分段規則（>= 500 行或 >= 20 KB）")
        print("4. 分段後記得更新相關文檔索引")
        print()
        print("=" * 100)


# ============================================================================
# 主程式
# ============================================================================

def main():
    """主程式入口"""
    print()
    print("[INFO] 開始掃描文檔...")
    print()

    # 切換到專案根目錄
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # 上一層目錄
    os.chdir(project_root)

    # 掃描文檔
    results = scan_documents()

    if len(results) == 0:
        print("[WARNING] 未找到任何文檔")
        return 1

    # 輸出報告
    print_report(results)

    # 檢查是否有需要分段的文檔
    needs_segment = [r for r in results if r["needs_segment"]]
    if len(needs_segment) > 0:
        print()
        print(f"[WARNING] 發現 {len(needs_segment)} 個文檔需要分段處理")
        return 1
    else:
        print()
        print("[OK] 所有文檔大小正常")
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[INFO] 用戶中斷")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n[ERROR] 錯誤：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
