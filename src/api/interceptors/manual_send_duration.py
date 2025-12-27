#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
ManualSendDurationInterceptor - 手動發送時長攔截器
模仿 Burpsuite Repeater 的功能，手刻封包並發送
"""

import json
import queue
from mitmproxy import http, ctx
from typing import Optional


class ManualSendDurationInterceptor:
    """手動構造並發送時長請求（像 Burpsuite Repeater）"""

    def __init__(self, course_duration_map: dict = None, use_target_mode: bool = False):
        """初始化攔截器

        Args:
            course_duration_map: 課程 ID 到時長的映射（秒）
                - 如果 use_target_mode=False: 時長增加值（增量模式）
                - 如果 use_target_mode=True: 目標總時長（目標模式）
            use_target_mode: 是否使用目標模式（直接設定總時長，而非增加）
        """
        # 使用 queue 來接收待發送的請求
        self.send_queue = queue.Queue()
        self.base_url = None
        self.session_headers = None  # 從真實請求中學習 headers
        self.payload_template = None  # 從真實請求中學習完整 payload 結構
        self.course_duration_map = course_duration_map or {}
        self.use_target_mode = use_target_mode

        # ✨ 新增：Payload 捕獲功能（用於 h 選項 1 的 Stage 2）
        self.captured_payloads = {}  # {course_id: payload}

        print("[ManualSend] 攔截器已初始化")
        print(f"  模式: {'目標總時長' if use_target_mode else '增量'} 模式")
        print(f"  課程配置: {len(self.course_duration_map)} 個")
        print(f"  Payload 捕獲: 已啟用")

    def request(self, flow: http.HTTPFlow):
        """
        攔截真實請求，學習 headers 和 cookies
        然後阻止原請求，改為發送手刻的增強版封包
        """
        if flow.request.path == "/statistics/api/user-visits":
            try:
                # 第一次攔截：學習瀏覽器特徵和完整 payload 結構
                if not self.session_headers or not self.payload_template:
                    self.session_headers = dict(flow.request.headers)
                    self.base_url = f"{flow.request.scheme}://{flow.request.host}:{flow.request.port}"

                    # ✨ 學習完整 payload 結構
                    payload = json.loads(flow.request.get_text(strict=False) or "{}")
                    self.payload_template = payload.copy()

                    print(f"[ManualSend] ✅ 已學習瀏覽器特徵和 Payload 結構")
                    print(f"  Base URL: {self.base_url}")
                    print(f"  Headers 數量: {len(self.session_headers)}")
                    print(f"  Payload 欄位數量: {len(self.payload_template)}")
                    print(f"  Payload 欄位: {', '.join(self.payload_template.keys())}")
                    # 第一次讓原請求通過，之後才開始手刻
                    return

                # 從原請求中提取信息
                payload = json.loads(flow.request.get_text(strict=False) or "{}")
                if not self._is_valid_payload(payload):
                    return

                # ✨ 關鍵：使用 course_id（主課程ID）來匹配配置
                course_id = str(payload["course_id"])
                course_code = str(payload["course_code"])
                course_name = payload["course_name"]
                original_duration = int(payload["visit_duration"])

                # ✨ 新增：捕獲 payload（用於 Stage 2 建立課程列表）
                if course_id not in self.captured_payloads:
                    self.captured_payloads[course_id] = payload.copy()
                    print(f"\n[ManualSend] ✅ 已捕獲 Payload")
                    print(f"  主課程 ID: {course_id}")
                    print(f"  子課程 ID: {course_code}")
                    print(f"  課程名稱: {course_name[:50]}...")
                    print(f"  已捕獲課程總數: {len(self.captured_payloads)}")

                # 檢查是否需要修改時長
                print(f"\n[ManualSend] 攔截到請求")
                print(f"  主課程 ID (course_id): {course_id}")
                print(f"  子課程 ID (course_code): {course_code}")
                print(f"  原始時長: {original_duration}秒 ({original_duration/60:.2f}分鐘)")

                # ✨ 檢查是否有配置（使用主課程 ID）
                if course_id in self.course_duration_map:
                    configured_value = self.course_duration_map[course_id]

                    if self.use_target_mode:
                        # 目標模式：直接設定為目標總時長
                        new_duration = configured_value
                        print(f"  ✓ 使用主課程 ID {course_id} 的配置（目標模式）")
                        print(f"  → 原始時長: {original_duration}秒 ({original_duration/60:.2f}分鐘)")
                        print(f"  → 目標時長: {new_duration}秒 ({new_duration/60:.2f}分鐘)")
                        print(f"  → 差異: {new_duration - original_duration:+d}秒 ({(new_duration - original_duration)/60:+.1f}分鐘)")
                    else:
                        # 增量模式：在原始時長基礎上增加
                        new_duration = original_duration + configured_value
                        print(f"  ✓ 使用主課程 ID {course_id} 的配置（增量模式）")
                        print(f"  → 原始時長: {original_duration}秒 ({original_duration/60:.2f}分鐘)")
                        print(f"  → 增加時長: +{configured_value}秒 (+{configured_value/60:.1f}分鐘)")
                        print(f"  → 新時長: {new_duration}秒 ({new_duration/60:.2f}分鐘)")

                    # ✨ 修改原請求的 payload（不需要手刻新請求）
                    payload["visit_duration"] = new_duration

                    # 更新時間戳（讓請求更真實）
                    if "visit_start_from" in payload:
                        from datetime import datetime
                        payload["visit_start_from"] = datetime.now().strftime("%Y/%m/%dT%H:%M:%S")

                    # 更新請求內容
                    flow.request.set_text(json.dumps(payload))

                    print(f"  ✓ 已修改原請求並放行（完整 payload，{len(payload)} 個欄位）")

                else:
                    print(f"  → 主課程 {course_id} 無配置，放行原請求")

            except Exception as e:
                print(f"[ManualSend] 錯誤: {e}")
                import traceback
                traceback.print_exc()

    def running(self):
        """
        MitmProxy 運行時持續檢查 queue
        如果有待發送的請求，就構造並發送
        """
        while not self.send_queue.empty():
            try:
                request_info = self.send_queue.get_nowait()
                self._send_crafted_request(request_info)
            except queue.Empty:
                break
            except Exception as e:
                print(f"[ManualSend] 處理隊列錯誤: {e}")

    def _send_crafted_request(self, request_info: dict):
        """
        手刻封包並發送（核心功能）

        這個方法完全手動構造 HTTP 請求，像 Burpsuite 一樣

        Args:
            request_info: {
                'course_code': '910008114',
                'course_name': '課程名稱',
                'visit_duration': 6000000,  # 毫秒
                'count': 1  # 發送次數
            }
        """
        if not self.base_url or not self.session_headers:
            print("[ManualSend] ⚠️  尚未學習到瀏覽器特徵，請先訪問課程頁面")
            return

        course_code = request_info['course_code']
        course_name = request_info['course_name']
        visit_duration = request_info['visit_duration']
        count = request_info.get('count', 1)

        print(f"\n[ManualSend] 手刻封包準備發送")
        print(f"  課程 ID (course_code): {course_code}")
        print(f"  課程名稱: {course_name[:40]}...")
        print(f"  時長: {visit_duration}ms ({visit_duration/1000:.1f}秒)")
        print(f"  發送次數: {count}")

        # ✨ 使用完整的 payload 模板（從真實請求學習）
        if self.payload_template:
            payload = self.payload_template.copy()
            # 只修改需要改變的欄位
            payload["visit_duration"] = visit_duration
            # 更新時間戳（如果有）
            if "visit_start_from" in payload:
                from datetime import datetime
                payload["visit_start_from"] = datetime.now().strftime("%Y/%m/%dT%H:%M:%S")
            print(f"  ✅ 使用完整 Payload 模板（{len(payload)} 個欄位）")
        else:
            # 備用方案：如果沒有學習到模板，使用簡化版本
            payload = {
                "course_code": course_code,
                "course_name": course_name,
                "visit_duration": visit_duration
            }
            print(f"  ⚠️  使用簡化 Payload（{len(payload)} 個欄位）")

        # 發送多次
        for i in range(count):
            try:
                # === 核心：手刻封包 ===
                # 使用 http.Request.make() 完全手動構造
                req = http.Request.make(
                    method="POST",
                    url=f"{self.base_url}/statistics/api/user-visits",
                    headers=self.session_headers.copy(),  # 使用學習到的瀏覽器 headers
                    content=json.dumps(payload).encode('utf-8')
                )

                # 創建 flow
                flow = http.HTTPFlow(
                    client_conn=None,
                    server_conn=None
                )
                flow.request = req

                # 發送請求
                ctx.master.commands.call("replay.client", [flow])

                print(f"  ✓ 已發送第 {i+1}/{count} 個封包")

            except Exception as e:
                print(f"  ✗ 發送第 {i+1} 個封包失敗: {e}")
                import traceback
                traceback.print_exc()

    def queue_request(self, course_code: str, course_name: str, visit_duration: int, count: int = 1):
        """
        添加待發送的請求到隊列

        從外部 Python 代碼調用這個方法來發送請求

        Args:
            course_code: 課程 ID
            course_name: 課程名稱
            visit_duration: 訪問時長（毫秒）
            count: 發送次數
        """
        request_info = {
            'course_code': course_code,
            'course_name': course_name,
            'visit_duration': visit_duration,
            'count': count
        }
        self.send_queue.put(request_info)
        print(f"[ManualSend] 已加入發送隊列: 課程 {course_code}, 時長 {visit_duration}ms, 次數 {count}")

    def send_now(self, course_code: str, course_name: str, duration_seconds: int, count: int = 1):
        """
        立即構造並發送請求（便捷方法）

        Args:
            course_code: 課程 ID
            course_name: 課程名稱
            duration_seconds: 時長（秒）
            count: 發送次數
        """
        visit_duration_ms = duration_seconds * 1000

        request_info = {
            'course_code': course_code,
            'course_name': course_name,
            'visit_duration': visit_duration_ms,
            'count': count
        }

        self._send_crafted_request(request_info)

    def add_course(self, course_id: str, duration_seconds: int):
        """動態添加課程配置"""
        self.course_duration_map[str(course_id)] = duration_seconds
        print(f"[ManualSend] 添加課程配置: {course_id} -> +{duration_seconds}秒 ({duration_seconds/60:.1f}分鐘)")

    def get_captured_payloads(self) -> dict:
        """
        獲取所有已捕獲的 payloads（用於 h 選項 1 的 Stage 2）

        Returns:
            dict: {course_id: payload}
        """
        return self.captured_payloads.copy()

    def _is_valid_payload(self, payload: dict) -> bool:
        """驗證 payload 是否包含必要欄位"""
        required_keys = ("course_code", "course_name", "visit_duration")
        return all(k in payload for k in required_keys)

    def __repr__(self) -> str:
        return f"ManualSendDurationInterceptor(learned={'Yes' if self.session_headers else 'No'}, captured={len(self.captured_payloads)})"
