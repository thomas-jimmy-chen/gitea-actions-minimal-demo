#!/usr/bin/env python3
"""
Burp Suite 捕獲檔案分析工具

用途: 解析 Burp Suite XML 匯出檔案，提取 HTTP 請求/響應資訊

使用方式:
    python scripts/analyze_burp_capture.py <burp_export.txt>
    python scripts/analyze_burp_capture.py <burp_export.txt> --html
    python scripts/analyze_burp_capture.py <burp_export.txt> --json

輸出:
    - 請求列表摘要
    - HTML 內容（--html 選項）
    - JSON 響應（--json 選項）

專案: EEBot v2.3.9 (代號: AliCorn 天角獸)
建立: 2025-12-27
"""

import xml.etree.ElementTree as ET
import base64
import json
import sys
import argparse
from pathlib import Path


def parse_burp_file(file_path: str) -> list:
    """解析 Burp Suite XML 匯出檔案"""
    tree = ET.parse(file_path)
    root = tree.getroot()
    items = root.findall('item')

    results = []
    for i, item in enumerate(items, 1):
        entry = {
            'index': i,
            'time': item.findtext('time', 'N/A'),
            'url': item.findtext('url', 'N/A'),
            'method': item.findtext('method', 'N/A'),
            'status': item.findtext('status', 'N/A'),
            'mime': item.findtext('mimetype', 'N/A'),
            'length': item.findtext('responselength', '0'),
        }

        # Decode response
        resp_elem = item.find('response')
        if resp_elem is not None and resp_elem.text:
            try:
                resp_bytes = base64.b64decode(resp_elem.text)
                entry['response_raw'] = resp_bytes
            except Exception:
                entry['response_raw'] = None
        else:
            entry['response_raw'] = None

        results.append(entry)

    return results


def print_summary(results: list):
    """列印請求摘要"""
    print(f'=== Burp Suite 捕獲分析 ===')
    print(f'總請求數: {len(results)}')
    print()

    for r in results:
        print(f'[{r["index"]:02d}] {r["time"]}')
        url_short = r["url"][:80] + '...' if len(r["url"]) > 80 else r["url"]
        print(f'     {r["method"]} {url_short}')
        print(f'     Status: {r["status"]} | Type: {r["mime"]} | Size: {r["length"]}')
        print()


def extract_html(results: list, output_path: str = None):
    """提取 HTML 內容"""
    for r in results:
        if r['mime'] == 'HTML' and r['response_raw']:
            resp_text = r['response_raw'].decode('utf-8', errors='ignore')

            # Find HTML start
            html_start = resp_text.find('<!DOCTYPE')
            if html_start == -1:
                html_start = resp_text.find('<html')

            if html_start != -1:
                html_content = resp_text[html_start:]

                if output_path:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print(f'HTML 已保存到: {output_path}')
                else:
                    print(f'=== HTML Content ({len(html_content)} chars) ===')
                    print(html_content[:2000])
                    print('...')
                return


def extract_json_responses(results: list):
    """提取所有 JSON 響應"""
    print('=== JSON Responses ===')
    print()

    for r in results:
        if r['mime'] == 'JSON' and r['response_raw']:
            resp_text = r['response_raw'].decode('utf-8', errors='ignore')

            # Find JSON start
            json_start = resp_text.find('{')
            if json_start != -1:
                json_str = resp_text[json_start:]
                try:
                    data = json.loads(json_str)
                    print(f'[{r["index"]:02d}] {r["url"].split("?")[0][-50:]}')
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                    print('...')
                    print()
                except json.JSONDecodeError:
                    print(f'[{r["index"]:02d}] JSON parse error')
                    print()


def analyze_scroll_containers(results: list):
    """分析 HTML 中的滾動容器"""
    import re

    for r in results:
        if r['mime'] == 'HTML' and r['response_raw']:
            html = r['response_raw'].decode('utf-8', errors='ignore')

            print('=== 滾動容器分析 ===')
            print()

            # Find scroll-related classes
            patterns = [
                ('fullscreen-right', '.fullscreen-right'),
                ('activity-content-box', '.activity-content-box'),
                ('exam-subjects', '.exam-subjects'),
                ('sync-scroll', '.sync-scroll'),
                ('reveal-modal', '.reveal-modal'),
                ('popup-area', '.popup-area'),
            ]

            for name, selector in patterns:
                count = html.count(name)
                if count > 0:
                    print(f'{selector}: {count} 個')

            return


def main():
    parser = argparse.ArgumentParser(
        description='Burp Suite 捕獲檔案分析工具'
    )
    parser.add_argument('file', help='Burp Suite XML 匯出檔案')
    parser.add_argument('--html', action='store_true', help='提取 HTML 內容')
    parser.add_argument('--html-output', help='HTML 輸出檔案路徑')
    parser.add_argument('--json', action='store_true', help='顯示 JSON 響應')
    parser.add_argument('--scroll', action='store_true', help='分析滾動容器')

    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f'錯誤: 檔案不存在 - {args.file}')
        sys.exit(1)

    results = parse_burp_file(args.file)

    if args.html:
        extract_html(results, args.html_output)
    elif args.json:
        extract_json_responses(results)
    elif args.scroll:
        analyze_scroll_containers(results)
    else:
        print_summary(results)


if __name__ == '__main__':
    main()
