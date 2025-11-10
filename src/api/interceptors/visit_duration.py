#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
VisitDurationInterceptor - 訪問時長攔截器
攔截並修改訪問時長的 API 請求
"""

import json
from mitmproxy import http


class VisitDurationInterceptor:
    """攔截並修改訪問時長的 API 請求"""

    def __init__(self, increase_duration: int = 9000):
        """
        初始化攔截器

        Args:
            increase_duration: 增加的訪問時長（毫秒），預設為 9000ms (9秒)
        """
        self.increase_duration = increase_duration

    def request(self, flow: http.HTTPFlow):
        """
        攔截 HTTP 請求

        Args:
            flow: mitmproxy 的 HTTP 流物件
        """
        # 只處理特定路徑的請求
        if flow.request.path == "/statistics/api/user-visits":
            try:
                # 解析請求 payload
                payload = json.loads(flow.request.get_text(strict=False) or "{}")

                # 驗證 payload 是否包含必要欄位
                if self._is_valid_payload(payload):
                    original = int(payload["visit_duration"])
                    new_duration = original + self.increase_duration

                    # 修改 visit_duration
                    payload["visit_duration"] = new_duration

                    # 更新請求內容
                    flow.request.set_text(json.dumps(payload))

                    print(f"[Interceptor] visit_duration modified: {original}ms -> {new_duration}ms")
                else:
                    print("[Interceptor] Payload validation failed, skipping...")

            except json.JSONDecodeError as e:
                print(f"[Interceptor] JSON decode error: {e}")
            except Exception as e:
                print(f"[Interceptor] Unexpected error: {e}")

    def _is_valid_payload(self, payload: dict) -> bool:
        """
        驗證 payload 是否包含必要欄位

        Args:
            payload: 請求的 payload

        Returns:
            bool: 是否有效
        """
        required_keys = ("course_code", "course_name", "visit_duration")
        return all(k in payload for k in required_keys)

    def __repr__(self) -> str:
        return f"VisitDurationInterceptor(increase={self.increase_duration}ms)"
