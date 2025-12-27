#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
PayloadCaptureInterceptor - Payload 捕獲攔截器
用於 Stage 1 掃描，捕獲每個課程的完整 payload 結構
"""

import json
from mitmproxy import http


class PayloadCaptureInterceptor:
    """捕獲並保存每個課程的完整 payload"""

    def __init__(self):
        """初始化攔截器"""
        self.captured_payloads = {}  # {course_id: payload}
        self.capture_enabled = True

        print("[PayloadCapture] 攔截器已初始化")
        print("  模式: 捕獲完整 Payload")

    def request(self, flow: http.HTTPFlow):
        """
        攔截 user-visits 請求並捕獲完整 payload
        """
        if not self.capture_enabled:
            return

        if flow.request.path == "/statistics/api/user-visits":
            try:
                # 解析 payload
                payload = json.loads(flow.request.get_text(strict=False) or "{}")

                if not self._is_valid_payload(payload):
                    return

                # 提取關鍵信息
                course_id = str(payload.get("course_id", ""))
                course_code = str(payload.get("course_code", ""))
                course_name = payload.get("course_name", "")

                if not course_id:
                    return

                # 保存完整 payload（使用子課程 ID 作為 key 以支持多子課程）
                # 修復：原來使用 course_id，導致同一課程計畫下的多個子課程只能捕獲第一個
                # 現在使用 course_code（子課程 ID）作為 key
                if course_code not in self.captured_payloads:
                    self.captured_payloads[course_code] = payload.copy()

                    print(f"\n[PayloadCapture] ✅ 已捕獲 Payload")
                    print(f"  主課程 ID: {course_id}")
                    print(f"  子課程 ID: {course_code}")
                    print(f"  課程名稱: {course_name[:50]}...")
                    print(f"  Payload 欄位數: {len(payload)}")
                    print(f"  已捕獲課程總數: {len(self.captured_payloads)}")

                # 放行原請求（不修改）

            except Exception as e:
                print(f"[PayloadCapture] 錯誤: {e}")
                import traceback
                traceback.print_exc()

    def _is_valid_payload(self, payload: dict) -> bool:
        """驗證 payload 是否包含必要欄位"""
        required_keys = ("course_id", "course_code", "course_name", "visit_duration")
        return all(k in payload for k in required_keys)

    def get_captured_payloads(self) -> dict:
        """
        獲取所有已捕獲的 payloads

        Returns:
            dict: {course_id: payload}
        """
        return self.captured_payloads.copy()

    def get_payload_by_course_id(self, course_id: str) -> dict:
        """
        根據主課程 ID 獲取 payload

        Args:
            course_id: 主課程 ID

        Returns:
            dict: payload 或 None
        """
        return self.captured_payloads.get(str(course_id))

    def clear_captured_payloads(self):
        """清空已捕獲的 payloads"""
        self.captured_payloads = {}
        print("[PayloadCapture] 已清空捕獲的 Payloads")

    def enable_capture(self):
        """啟用捕獲"""
        self.capture_enabled = True
        print("[PayloadCapture] 捕獲已啟用")

    def disable_capture(self):
        """停用捕獲"""
        self.capture_enabled = False
        print("[PayloadCapture] 捕獲已停用")

    def __repr__(self) -> str:
        return f"PayloadCaptureInterceptor(captured={len(self.captured_payloads)})"
