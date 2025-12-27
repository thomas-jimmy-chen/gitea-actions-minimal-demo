#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
CourseSelectionMenu - 課程選擇互動選單
用於 Stage 2，讓用戶選擇要批量發送時長的課程
"""

import json


class CourseSelectionMenu:
    """互動式課程選擇選單"""

    def __init__(self, courses_data: list):
        """
        初始化選單

        Args:
            courses_data: 課程數據列表 [
                {
                    "api_course_id": "465",
                    "program_name": "課程計畫名稱",
                    "course_code": "901011114",
                    "course_name": "子課程名稱",
                    "required_minutes": 100,
                    "payload": {...}
                },
                ...
            ]
        """
        self.courses = courses_data
        self.selected = set()  # 已選課程的索引集合

    def display_menu(self):
        """顯示選單"""
        print('\n' + '=' * 70)
        print('  批量處理 - 課程/考試選擇')
        print('=' * 70)
        print(f'\n掃描到 {len(self.courses)} 個項目：\n')

        for i, item in enumerate(self.courses, 1):
            status = '✅ 已選' if (i - 1) in self.selected else '⬜ 未選'
            program_name = item.get('program_name', '未知課程')
            item_type = item.get('item_type', 'course')

            if item_type == 'exam':
                # 顯示考試信息
                exam_name = item.get('exam_name', '未知')
                print(f'  [{i}] {program_name[:55]}')
                print(f'      └─ 📝 測驗: {exam_name[:40]} | 狀態: {status}')
            else:
                # 顯示課程信息
                course_id = item.get('api_course_id', 'N/A')
                course_code = item.get('course_code', 'N/A')
                required_minutes = item.get('required_minutes', 0)
                print(f'  [{i}] {program_name[:55]}')
                print(f'      └─ 📚 課程: ID {course_id} | 子課程: {course_code} | 需要: {required_minutes} 分鐘 | 狀態: {status}')

        # 顯示統計信息
        selected_count = len(self.selected)
        selected_courses = [self.courses[i] for i in self.selected if self.courses[i].get('item_type', 'course') == 'course']
        selected_exams = [self.courses[i] for i in self.selected if self.courses[i].get('item_type') == 'exam']
        total_minutes = sum(
            self.courses[i].get('required_minutes', 0)
            for i in self.selected
        )

        print('\n' + '-' * 70)
        print(f'已選: {selected_count}/{len(self.courses)} 個項目 ({len(selected_courses)} 課程, {len(selected_exams)} 測驗)')
        if selected_count > 0 and total_minutes > 0:
            print(f'總時長: {total_minutes} 分鐘 ({total_minutes / 60:.1f} 小時)')
        print('-' * 70)

    def display_help(self):
        """顯示幫助信息"""
        print('\n' + '=' * 70)
        print('  操作說明')
        print('=' * 70)
        print('\n可用指令：')
        print('  [數字]       選擇/取消選擇單個課程（例如：1, 5, 12）')
        print('  [數字列表]   選擇多個課程（例如：1,2,3 或 1 2 3）')
        print('  all          選擇所有課程')
        print('  clear        清空所有選擇')
        print('  v            查看已選課程詳情')
        print('  h            顯示此幫助信息')
        print('  s            開始執行（發送時長）')
        print('  r            重新顯示選單')
        print('  q            退出')
        print('=' * 70)

    def display_selected_details(self):
        """顯示已選課程/考試的詳細信息"""
        if not self.selected:
            print('\n尚未選擇任何項目')
            return

        print('\n' + '=' * 70)
        print('  已選項目詳情')
        print('=' * 70)

        for idx, i in enumerate(sorted(self.selected), 1):
            item = self.courses[i]
            item_type = item.get('item_type', 'course')

            print(f'\n[{idx}] {item.get("program_name", "未知課程")}')

            if item_type == 'exam':
                # 顯示考試詳情
                print(f'    類型: 📝 測驗')
                print(f'    考試名稱: {item.get("exam_name", "未知")[:60]}')
            else:
                # 顯示課程詳情
                print(f'    類型: 📚 課程')
                print(f'    主課程 ID: {item.get("api_course_id", "N/A")}')
                print(f'    子課程 ID: {item.get("course_code", "N/A")}')
                print(f'    子課程名稱: {item.get("course_name", "未知")[:60]}')
                print(f'    需要時長: {item.get("required_minutes", 0)} 分鐘')
                print(f'    Payload 欄位數: {len(item.get("payload", {}))}')

        # 統計
        selected_courses = [self.courses[i] for i in self.selected if self.courses[i].get('item_type', 'course') == 'course']
        selected_exams = [self.courses[i] for i in self.selected if self.courses[i].get('item_type') == 'exam']
        total_minutes = sum(
            self.courses[i].get('required_minutes', 0)
            for i in self.selected
        )

        print('\n' + '-' * 70)
        print(f'總計: {len(self.selected)} 個項目 ({len(selected_courses)} 課程, {len(selected_exams)} 測驗)')
        if total_minutes > 0:
            print(f'總時長: {total_minutes} 分鐘 ({total_minutes / 60:.1f} 小時)')
        print('=' * 70)

    def parse_input(self, user_input: str) -> tuple:
        """
        解析用戶輸入

        Args:
            user_input: 用戶輸入字符串

        Returns:
            tuple: (action, data)
                - action: 'toggle' | 'all' | 'clear' | 'view' | 'help' | 'start' | 'refresh' | 'quit' | 'invalid'
                - data: 根據 action 不同而不同
        """
        user_input = user_input.strip().lower()

        if not user_input:
            return ('invalid', '請輸入指令')

        # 特殊指令
        if user_input == 'all':
            return ('all', None)
        elif user_input == 'clear':
            return ('clear', None)
        elif user_input == 'v':
            return ('view', None)
        elif user_input == 'h':
            return ('help', None)
        elif user_input == 's':
            return ('start', None)
        elif user_input == 'r':
            return ('refresh', None)
        elif user_input == 'q':
            return ('quit', None)

        # 解析數字（單個或多個）
        # 支持格式：1, 1,2,3, 1 2 3
        numbers = []

        # 嘗試以逗號分隔
        if ',' in user_input:
            parts = user_input.split(',')
        else:
            # 以空格分隔
            parts = user_input.split()

        for part in parts:
            part = part.strip()
            if part.isdigit():
                num = int(part)
                if 1 <= num <= len(self.courses):
                    numbers.append(num - 1)  # 轉換為 0-based 索引
                else:
                    return ('invalid', f'數字 {num} 超出範圍（1-{len(self.courses)}）')
            elif part:
                return ('invalid', f'無效的輸入: {part}')

        if numbers:
            return ('toggle', numbers)

        return ('invalid', '無效的指令')

    def toggle_selection(self, indices: list):
        """
        切換課程選擇狀態

        Args:
            indices: 課程索引列表（0-based）
        """
        for idx in indices:
            if idx in self.selected:
                self.selected.remove(idx)
                print(f'  ✓ 取消選擇: {self.courses[idx].get("program_name", "未知")[:50]}')
            else:
                self.selected.add(idx)
                print(f'  ✓ 已選擇: {self.courses[idx].get("program_name", "未知")[:50]}')

    def select_all(self):
        """選擇所有課程"""
        self.selected = set(range(len(self.courses)))
        print(f'\n✓ 已選擇所有 {len(self.courses)} 個課程')

    def clear_all(self):
        """清空所有選擇"""
        self.selected.clear()
        print('\n✓ 已清空所有選擇')

    def get_selected_courses(self) -> list:
        """
        獲取已選課程列表

        Returns:
            list: 已選課程數據列表
        """
        return [self.courses[i] for i in sorted(self.selected)]

    def run(self) -> list:
        """
        運行互動選單

        Returns:
            list: 用戶選擇的課程列表，如果取消則返回 None
        """
        self.display_help()

        while True:
            self.display_menu()

            user_input = input('\n請輸入指令 (h 查看幫助): ').strip()

            action, data = self.parse_input(user_input)

            if action == 'toggle':
                self.toggle_selection(data)

            elif action == 'all':
                self.select_all()

            elif action == 'clear':
                self.clear_all()

            elif action == 'view':
                self.display_selected_details()
                input('\n按 Enter 繼續...')

            elif action == 'help':
                self.display_help()

            elif action == 'start':
                if not self.selected:
                    print('\n⚠️  尚未選擇任何課程，請先選擇')
                    continue

                # 確認
                self.display_selected_details()
                confirm = input('\n確定要執行嗎？(y/n): ').strip().lower()
                if confirm == 'y':
                    return self.get_selected_courses()
                else:
                    print('\n已取消執行')

            elif action == 'refresh':
                continue

            elif action == 'quit':
                print('\n已退出選單')
                return None

            elif action == 'invalid':
                print(f'\n⚠️  {data}')
