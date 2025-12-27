#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
CourseSpecificDurationInterceptor - 課程特定時長攔截器
根據不同的課程 ID 設置不同的時長增加值
"""

import json
from mitmproxy import http


class CourseSpecificDurationInterceptor:
    """攔截並根據課程 ID 修改訪問時長的 API 請求"""

    def __init__(self, course_duration_map: dict = None):
        """
        初始化攔截器

        Args:
            course_duration_map: 課程 ID 到時長增加值的映射
                格式: {
                    'course_id': duration_in_seconds,
                    '465': 6000,  # 6000 秒 = 100 分鐘
                    '452': 4800,  # 4800 秒 = 80 分鐘
                }
        """
        self.course_duration_map = course_duration_map or {}
        print(f"[CourseSpecificDurationInterceptor] 初始化，共 {len(self.course_duration_map)} 個課程配置")
        for course_id, duration_seconds in self.course_duration_map.items():
            duration_minutes = duration_seconds / 60
            print(f"  課程 {course_id}: +{duration_seconds} 秒 ({duration_minutes:.1f} 分鐘)")

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
                    course_code = str(payload["course_code"])
                    original_duration = int(payload["visit_duration"])

                    # 檢查是否有此課程的配置
                    if course_code in self.course_duration_map:
                        # 獲取要增加的時長（秒）
                        increase_seconds = self.course_duration_map[course_code]
                        # 轉換為毫秒
                        increase_milliseconds = increase_seconds * 1000

                        # 計算新的時長
                        new_duration = original_duration + increase_milliseconds

                        # 修改 visit_duration
                        payload["visit_duration"] = new_duration

                        # 更新請求內容
                        flow.request.set_text(json.dumps(payload))

                        print(f"[Interceptor] 課程 {course_code} ({payload.get('course_name', 'Unknown')[:40]}...)")
                        print(f"             原始時長: {original_duration}ms ({original_duration/1000:.1f}秒)")
                        print(f"             增加時長: +{increase_milliseconds}ms (+{increase_seconds}秒 = +{increase_seconds/60:.1f}分鐘)")
                        print(f"             新時長: {new_duration}ms ({new_duration/1000:.1f}秒)")
                    else:
                        print(f"[Interceptor] 課程 {course_code} 無配置，跳過修改")
                        print(f"             原始時長: {original_duration}ms")

                else:
                    print("[Interceptor] Payload 驗證失敗，跳過...")

            except json.JSONDecodeError as e:
                print(f"[Interceptor] JSON 解析錯誤: {e}")
            except Exception as e:
                print(f"[Interceptor] 未預期的錯誤: {e}")
                import traceback
                traceback.print_exc()

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

    def add_course(self, course_id: str, duration_seconds: int):
        """
        添加課程配置

        Args:
            course_id: 課程 ID
            duration_seconds: 要增加的時長（秒）
        """
        self.course_duration_map[str(course_id)] = duration_seconds
        print(f"[Interceptor] 添加課程配置: {course_id} -> +{duration_seconds}秒 ({duration_seconds/60:.1f}分鐘)")

    def remove_course(self, course_id: str):
        """
        移除課程配置

        Args:
            course_id: 課程 ID
        """
        if str(course_id) in self.course_duration_map:
            del self.course_duration_map[str(course_id)]
            print(f"[Interceptor] 移除課程配置: {course_id}")

    def clear(self):
        """清空所有課程配置"""
        self.course_duration_map.clear()
        print("[Interceptor] 清空所有課程配置")

    def __repr__(self) -> str:
        return f"CourseSpecificDurationInterceptor(courses={len(self.course_duration_map)})"
