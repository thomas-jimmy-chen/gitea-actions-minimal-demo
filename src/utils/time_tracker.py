#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
TimeTracker - 時間追蹤工具
記錄程式執行各階段、各課程/考試的時間統計
Created: 2025-01-17
"""

import time
import os
from datetime import datetime, timedelta
from typing import Dict, Optional


class TimeTracker:
    """時間追蹤器 - 記錄程式執行的所有時間統計"""

    def __init__(self):
        """初始化時間追蹤器"""
        self.program_start_time = None
        self.program_end_time = None

        # 階段時間記錄 {phase_name: {'start': time, 'end': time, 'duration': seconds}}
        self.phases = {}
        self.current_phase = None

        # 課程時間記錄 {course_name: {'start': time, 'end': time, 'duration': seconds, 'delays': total_delay}}
        self.courses = {}
        self.current_course = None

        # 考試時間記錄 {exam_name: {'start': time, 'end': time, 'duration': seconds, 'delays': total_delay}}
        self.exams = {}
        self.current_exam = None

        # 延遲時間累計
        self.total_delays = 0.0

        # 使用者輸入等待時間記錄
        self.user_input_waits = []  # [{'description': str, 'duration': float, 'timestamp': float}]
        self.total_user_wait = 0.0
        self._user_wait_start = None

    def start_program(self):
        """開始記錄整個程式的執行時間"""
        self.program_start_time = time.time()
        print(f'\n[時間追蹤] 程式開始執行 - {self._format_timestamp(self.program_start_time)}')

    def end_program(self):
        """結束記錄整個程式的執行時間"""
        self.program_end_time = time.time()
        print(f'\n[時間追蹤] 程式執行結束 - {self._format_timestamp(self.program_end_time)}')

    def start_phase(self, phase_name: str):
        """
        開始記錄階段時間

        Args:
            phase_name: 階段名稱（例如：初始化、登入、課程執行、考試執行等）
        """
        # 如果有進行中的階段，先結束它
        if self.current_phase:
            self.end_phase(self.current_phase)

        self.current_phase = phase_name
        self.phases[phase_name] = {
            'start': time.time(),
            'end': None,
            'duration': 0
        }
        print(f'\n[階段開始] {phase_name}')

    def end_phase(self, phase_name: str):
        """
        結束記錄階段時間

        Args:
            phase_name: 階段名稱
        """
        if phase_name in self.phases and self.phases[phase_name]['end'] is None:
            self.phases[phase_name]['end'] = time.time()
            self.phases[phase_name]['duration'] = (
                self.phases[phase_name]['end'] - self.phases[phase_name]['start']
            )
            duration_str = self._format_duration(self.phases[phase_name]['duration'])
            print(f'[階段結束] {phase_name} - 耗時: {duration_str}')

            if self.current_phase == phase_name:
                self.current_phase = None

    def start_course(self, course_name: str, program_name: str = ''):
        """
        開始記錄課程時間

        Args:
            course_name: 課程名稱（小章節）
            program_name: 課程計畫名稱（大章節）
        """
        full_name = f'{program_name} > {course_name}' if program_name else course_name

        self.current_course = full_name
        self.courses[full_name] = {
            'start': time.time(),
            'end': None,
            'duration': 0,
            'delays': 0,
            'program_name': program_name,
            'course_name': course_name
        }
        print(f'\n  [課程開始] {course_name}')

    def end_course(self, course_name: str = None):
        """
        結束記錄課程時間

        Args:
            course_name: 課程名稱（可選，預設使用 current_course）
        """
        target_name = course_name if course_name else self.current_course

        if target_name and target_name in self.courses and self.courses[target_name]['end'] is None:
            self.courses[target_name]['end'] = time.time()
            self.courses[target_name]['duration'] = (
                self.courses[target_name]['end'] - self.courses[target_name]['start']
            )

            course_info = self.courses[target_name]
            net_duration = course_info['duration'] - course_info['delays']
            duration_str = self._format_duration(course_info['duration'])
            delay_str = self._format_duration(course_info['delays'])
            net_str = self._format_duration(net_duration)

            print(f'  [課程結束] {course_info["course_name"]} - '
                  f'總時間: {duration_str} (執行: {net_str} + 延遲: {delay_str})')

            if self.current_course == target_name:
                self.current_course = None

    def start_exam(self, exam_name: str, program_name: str = ''):
        """
        開始記錄考試時間

        Args:
            exam_name: 考試名稱
            program_name: 課程計畫名稱（大章節）
        """
        full_name = f'{program_name} > {exam_name}' if program_name else exam_name

        self.current_exam = full_name
        self.exams[full_name] = {
            'start': time.time(),
            'end': None,
            'duration': 0,
            'delays': 0,
            'program_name': program_name,
            'exam_name': exam_name
        }
        print(f'\n  [考試開始] {exam_name}')

    def end_exam(self, exam_name: str = None):
        """
        結束記錄考試時間

        Args:
            exam_name: 考試名稱（可選，預設使用 current_exam）
        """
        target_name = exam_name if exam_name else self.current_exam

        if target_name and target_name in self.exams and self.exams[target_name]['end'] is None:
            self.exams[target_name]['end'] = time.time()
            self.exams[target_name]['duration'] = (
                self.exams[target_name]['end'] - self.exams[target_name]['start']
            )

            exam_info = self.exams[target_name]
            net_duration = exam_info['duration'] - exam_info['delays']
            duration_str = self._format_duration(exam_info['duration'])
            delay_str = self._format_duration(exam_info['delays'])
            net_str = self._format_duration(net_duration)

            print(f'  [考試結束] {exam_info["exam_name"]} - '
                  f'總時間: {duration_str} (執行: {net_str} + 延遲: {delay_str})')

            if self.current_exam == target_name:
                self.current_exam = None

    def record_delay(self, delay_seconds: float, description: str = ''):
        """
        記錄延遲時間

        Args:
            delay_seconds: 延遲秒數
            description: 延遲描述
        """
        self.total_delays += delay_seconds

        # 記錄到當前課程或考試
        if self.current_course and self.current_course in self.courses:
            self.courses[self.current_course]['delays'] += delay_seconds
        elif self.current_exam and self.current_exam in self.exams:
            self.exams[self.current_exam]['delays'] += delay_seconds

    def start_user_wait(self, description: str = '等待使用者輸入'):
        """
        開始記錄使用者輸入等待時間

        Args:
            description: 等待描述
        """
        self._user_wait_start = time.time()
        self._user_wait_description = description

    def end_user_wait(self):
        """結束記錄使用者輸入等待時間"""
        if self._user_wait_start:
            duration = time.time() - self._user_wait_start
            self.user_input_waits.append({
                'description': self._user_wait_description,
                'duration': duration,
                'timestamp': self._user_wait_start
            })
            self.total_user_wait += duration
            print(f'  [使用者輸入] {self._user_wait_description} - 等待時間: {self._format_duration(duration)}')
            self._user_wait_start = None
            self._user_wait_description = None

    def get_program_stats(self) -> Dict:
        """
        獲取課程計畫統計（按大章節分組）

        Returns:
            Dict: {program_name: {'courses': [...], 'total_duration': seconds, 'total_delays': seconds}}
        """
        program_stats = {}

        # 統計課程
        for full_name, info in self.courses.items():
            if info['end'] is None:
                continue

            program_name = info['program_name'] or '未分類'

            if program_name not in program_stats:
                program_stats[program_name] = {
                    'courses': [],
                    'exams': [],
                    'total_duration': 0,
                    'total_delays': 0
                }

            program_stats[program_name]['courses'].append({
                'name': info['course_name'],
                'duration': info['duration'],
                'delays': info['delays']
            })
            program_stats[program_name]['total_duration'] += info['duration']
            program_stats[program_name]['total_delays'] += info['delays']

        # 統計考試
        for full_name, info in self.exams.items():
            if info['end'] is None:
                continue

            program_name = info['program_name'] or '未分類'

            if program_name not in program_stats:
                program_stats[program_name] = {
                    'courses': [],
                    'exams': [],
                    'total_duration': 0,
                    'total_delays': 0
                }

            program_stats[program_name]['exams'].append({
                'name': info['exam_name'],
                'duration': info['duration'],
                'delays': info['delays']
            })
            program_stats[program_name]['total_duration'] += info['duration']
            program_stats[program_name]['total_delays'] += info['delays']

        return program_stats

    def print_report(self, save_to_file: bool = True, report_dir: str = 'reports'):
        """
        打印完整的時間統計報告

        Args:
            save_to_file: 是否保存到文件（預設為 True）
            report_dir: 報告保存目錄（預設為 'reports'）
        """
        if not self.program_start_time:
            print('[時間統計] 無記錄資料')
            return

        # 結束程式計時（如果尚未結束）
        if not self.program_end_time:
            self.end_program()

        # 結束未完成的階段
        if self.current_phase:
            self.end_phase(self.current_phase)

        total_duration = self.program_end_time - self.program_start_time

        print('\n' + '=' * 80)
        print('                        📊 時間統計報告 📊')
        print('=' * 80)

        # 1. 程式總執行時間
        print(f'\n【程式執行時間】')
        print(f'  開始時間: {self._format_timestamp(self.program_start_time)}')
        print(f'  結束時間: {self._format_timestamp(self.program_end_time)}')
        print(f'  總執行時間: {self._format_duration(total_duration)}')
        print(f'  總延遲時間: {self._format_duration(self.total_delays)}')
        print(f'  使用者等待: {self._format_duration(self.total_user_wait)}')
        net_time = total_duration - self.total_delays - self.total_user_wait
        print(f'  淨執行時間: {self._format_duration(net_time)}')

        # 2. 各階段執行時間
        if self.phases:
            print(f'\n【階段執行時間】')
            print(f'  {"階段名稱":<30} {"執行時間":>15} {"佔比":>10}')
            print(f'  {"-" * 58}')

            for phase_name, info in self.phases.items():
                if info['end'] is None:
                    continue
                duration_str = self._format_duration(info['duration'])
                percentage = (info['duration'] / total_duration * 100) if total_duration > 0 else 0
                print(f'  {phase_name:<30} {duration_str:>15} {percentage:>9.1f}%')

        # 3. 課程計畫統計（大章節）
        program_stats = self.get_program_stats()

        if program_stats:
            print(f'\n【課程計畫統計】（大章節）')

            for program_name, stats in sorted(program_stats.items()):
                total_items = len(stats['courses']) + len(stats['exams'])
                duration_str = self._format_duration(stats['total_duration'])
                delay_str = self._format_duration(stats['total_delays'])
                net_duration = stats['total_duration'] - stats['total_delays']
                net_str = self._format_duration(net_duration)

                print(f'\n  📚 {program_name}')
                print(f'     項目數: {total_items} (課程: {len(stats["courses"])}, 考試: {len(stats["exams"])})')
                print(f'     總時間: {duration_str} (執行: {net_str} + 延遲: {delay_str})')

                # 顯示課程明細
                if stats['courses']:
                    print(f'     📖 課程明細:')
                    for course in stats['courses']:
                        course_duration = self._format_duration(course['duration'])
                        course_delay = self._format_duration(course['delays'])
                        course_net = self._format_duration(course['duration'] - course['delays'])
                        print(f'        • {course["name"]:<40} {course_duration:>12} '
                              f'(執行: {course_net} + 延遲: {course_delay})')

                # 顯示考試明細
                if stats['exams']:
                    print(f'     📝 考試明細:')
                    for exam in stats['exams']:
                        exam_duration = self._format_duration(exam['duration'])
                        exam_delay = self._format_duration(exam['delays'])
                        exam_net = self._format_duration(exam['duration'] - exam['delays'])
                        print(f'        • {exam["name"]:<40} {exam_duration:>12} '
                              f'(執行: {exam_net} + 延遲: {exam_delay})')

        # 4. 使用者輸入等待統計
        if self.user_input_waits:
            print(f'\n【使用者輸入等待統計】')
            print(f'  {"等待描述":<40} {"等待時間":>15} {"時間戳":>20}')
            print(f'  {"-" * 78}')

            for wait in self.user_input_waits:
                duration_str = self._format_duration(wait['duration'])
                timestamp_str = self._format_timestamp(wait['timestamp'])
                print(f'  {wait["description"]:<40} {duration_str:>15} {timestamp_str:>20}')

            print(f'  {"-" * 78}')
            print(f'  {"總計":< 40} {self._format_duration(self.total_user_wait):>15}')

        # 5. 總結
        print(f'\n【總結】')
        total_courses = sum(1 for info in self.courses.values() if info['end'] is not None)
        total_exams = sum(1 for info in self.exams.values() if info['end'] is not None)
        total_items = total_courses + total_exams

        print(f'  完成項目總數: {total_items} (課程: {total_courses}, 考試: {total_exams})')
        print(f'  平均每項時間: {self._format_duration(total_duration / total_items if total_items > 0 else 0)}')
        print(f'  延遲時間佔比: {(self.total_delays / total_duration * 100) if total_duration > 0 else 0:.1f}%')
        print(f'  使用者等待佔比: {(self.total_user_wait / total_duration * 100) if total_duration > 0 else 0:.1f}%')
        net_time = total_duration - self.total_delays - self.total_user_wait
        print(f'  純執行時間佔比: {(net_time / total_duration * 100) if total_duration > 0 else 0:.1f}%')

        print('\n' + '=' * 80)

        # 保存報告到文件
        if save_to_file:
            report_file = self._save_report_to_file(report_dir)
            if report_file:
                print(f'\n📄 時間統計報告已保存: {report_file}')

    def _format_timestamp(self, timestamp: float) -> str:
        """
        格式化時間戳

        Args:
            timestamp: Unix 時間戳

        Returns:
            str: 格式化的時間字串
        """
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def _format_duration(self, seconds: float) -> str:
        """
        格式化時長

        Args:
            seconds: 秒數

        Returns:
            str: 格式化的時長字串（例如：1h 23m 45s）
        """
        if seconds < 0:
            return '0s'

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        parts = []
        if hours > 0:
            parts.append(f'{hours}h')
        if minutes > 0:
            parts.append(f'{minutes}m')
        if secs > 0 or not parts:
            parts.append(f'{secs}s')

        return ' '.join(parts)

    def _save_report_to_file(self, report_dir: str) -> Optional[str]:
        """
        保存報告到文件

        Args:
            report_dir: 報告保存目錄

        Returns:
            Optional[str]: 報告文件路徑，失敗則返回 None
        """
        try:
            # 創建報告目錄
            os.makedirs(report_dir, exist_ok=True)

            # 生成報告文件名（包含時間戳）
            timestamp = datetime.fromtimestamp(self.program_start_time).strftime('%Y%m%d_%H%M%S')
            report_file = os.path.join(report_dir, f'time_report_{timestamp}.md')

            # 生成 Markdown 報告內容
            report_content = self._generate_markdown_report()

            # 寫入文件
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)

            return report_file

        except Exception as e:
            print(f'  ⚠️  保存報告失敗: {e}')
            return None

    def _generate_markdown_report(self) -> str:
        """
        生成 Markdown 格式的報告

        Returns:
            str: Markdown 報告內容
        """
        if not self.program_start_time or not self.program_end_time:
            return "# 時間統計報告\n\n無記錄資料\n"

        total_duration = self.program_end_time - self.program_start_time
        net_time = total_duration - self.total_delays - self.total_user_wait

        lines = []
        lines.append("# 📊 EEBot 時間統計報告\n")
        lines.append(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append("---\n")

        # 1. 程式執行時間
        lines.append("## 1. 程式執行時間\n")
        lines.append("| 項目 | 時間 |")
        lines.append("|------|------|")
        lines.append(f"| 開始時間 | {self._format_timestamp(self.program_start_time)} |")
        lines.append(f"| 結束時間 | {self._format_timestamp(self.program_end_time)} |")
        lines.append(f"| **總執行時間** | **{self._format_duration(total_duration)}** |")
        lines.append(f"| 總延遲時間 | {self._format_duration(self.total_delays)} |")
        lines.append(f"| 使用者等待 | {self._format_duration(self.total_user_wait)} |")
        lines.append(f"| **淨執行時間** | **{self._format_duration(net_time)}** |")
        lines.append("")

        # 2. 階段執行時間
        if self.phases:
            lines.append("## 2. 階段執行時間\n")
            lines.append("| 階段名稱 | 執行時間 | 佔比 |")
            lines.append("|----------|----------|------|")

            for phase_name, info in self.phases.items():
                if info['end'] is None:
                    continue
                duration_str = self._format_duration(info['duration'])
                percentage = (info['duration'] / total_duration * 100) if total_duration > 0 else 0
                lines.append(f"| {phase_name} | {duration_str} | {percentage:.1f}% |")
            lines.append("")

        # 3. 課程計畫統計
        program_stats = self.get_program_stats()

        if program_stats:
            lines.append("## 3. 課程計畫統計（大章節）\n")

            for program_name, stats in sorted(program_stats.items()):
                total_items = len(stats['courses']) + len(stats['exams'])
                duration_str = self._format_duration(stats['total_duration'])
                delay_str = self._format_duration(stats['total_delays'])
                net_duration = stats['total_duration'] - stats['total_delays']
                net_str = self._format_duration(net_duration)

                lines.append(f"### 📚 {program_name}\n")
                lines.append(f"- **項目數**: {total_items} (課程: {len(stats['courses'])}, 考試: {len(stats['exams'])})")
                lines.append(f"- **總時間**: {duration_str}")
                lines.append(f"- **執行時間**: {net_str}")
                lines.append(f"- **延遲時間**: {delay_str}\n")

                # 課程明細
                if stats['courses']:
                    lines.append("#### 📖 課程明細\n")
                    lines.append("| 課程名稱 | 總時間 | 執行時間 | 延遲時間 |")
                    lines.append("|----------|--------|----------|----------|")

                    for course in stats['courses']:
                        course_duration = self._format_duration(course['duration'])
                        course_delay = self._format_duration(course['delays'])
                        course_net = self._format_duration(course['duration'] - course['delays'])
                        lines.append(f"| {course['name']} | {course_duration} | {course_net} | {course_delay} |")
                    lines.append("")

                # 考試明細
                if stats['exams']:
                    lines.append("#### 📝 考試明細\n")
                    lines.append("| 考試名稱 | 總時間 | 執行時間 | 延遲時間 |")
                    lines.append("|----------|--------|----------|----------|")

                    for exam in stats['exams']:
                        exam_duration = self._format_duration(exam['duration'])
                        exam_delay = self._format_duration(exam['delays'])
                        exam_net = self._format_duration(exam['duration'] - exam['delays'])
                        lines.append(f"| {exam['name']} | {exam_duration} | {exam_net} | {exam_delay} |")
                    lines.append("")

        # 4. 使用者輸入等待統計
        if self.user_input_waits:
            lines.append("## 4. 使用者輸入等待統計\n")
            lines.append("| 等待描述 | 等待時間 | 時間戳 |")
            lines.append("|----------|----------|--------|")

            for wait in self.user_input_waits:
                duration_str = self._format_duration(wait['duration'])
                timestamp_str = self._format_timestamp(wait['timestamp'])
                lines.append(f"| {wait['description']} | {duration_str} | {timestamp_str} |")

            lines.append("")
            lines.append(f"**總計**: {self._format_duration(self.total_user_wait)}\n")

        # 5. 總結
        lines.append("## 5. 總結\n")
        total_courses = sum(1 for info in self.courses.values() if info['end'] is not None)
        total_exams = sum(1 for info in self.exams.values() if info['end'] is not None)
        total_items = total_courses + total_exams

        lines.append(f"- **完成項目總數**: {total_items} (課程: {total_courses}, 考試: {total_exams})")
        lines.append(f"- **平均每項時間**: {self._format_duration(total_duration / total_items if total_items > 0 else 0)}")
        lines.append(f"- **延遲時間佔比**: {(self.total_delays / total_duration * 100) if total_duration > 0 else 0:.1f}%")
        lines.append(f"- **使用者等待佔比**: {(self.total_user_wait / total_duration * 100) if total_duration > 0 else 0:.1f}%")
        lines.append(f"- **純執行時間佔比**: {(net_time / total_duration * 100) if total_duration > 0 else 0:.1f}%")
        lines.append("")

        lines.append("---")
        lines.append(f"\n*報告由 EEBot TimeTracker 自動生成於 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        return "\n".join(lines)

    def __repr__(self) -> str:
        """字串表示"""
        courses_count = len([c for c in self.courses.values() if c['end'] is not None])
        exams_count = len([e for e in self.exams.values() if e['end'] is not None])
        return f"TimeTracker(courses={courses_count}, exams={exams_count}, phases={len(self.phases)})"
