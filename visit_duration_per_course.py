#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
VisitDurationInterceptor - 訪問時長攔截器（按課程自訂版）
支援每個課程獨立設定時長修改規則
"""

import json
from typing import Dict, Optional
from mitmproxy import http


class VisitDurationInterceptor:
    """攔截並修改訪問時長的 API 請求（支援按課程自訂）"""

    def __init__(
        self,
        course_config: Dict[str, Dict] = None,
        default_increase: int = 9000,
        mode: str = "multiplier"  # "multiplier", "increase", "minimum"
    ):
        """
        初始化攔截器

        Args:
            course_config: 課程配置字典，格式：
                {
                    "course_id": {
                        "multiplier": 10,        # 倍數模式
                        "increase": 5000,        # 增加模式
                        "minimum": 3600          # 最小值模式
                    }
                }
            default_increase: 預設增加值（當課程未設定時）
            mode: 優先使用的模式 ("multiplier", "increase", "minimum")
        """
        self.course_config = course_config or {}
        self.default_increase = default_increase
        self.mode = mode

    def request(self, flow: http.HTTPFlow):
        """
        攔截 HTTP 請求

        Args:
            flow: mitmproxy 的 HTTP 流物件
        """
        # 只處理時長提交 API
        if "/statistics/api/user-visits" not in flow.request.url:
            return

        try:
            # 解析請求 payload
            payload = json.loads(flow.request.get_text(strict=False) or "{}")

            # 檢查必要欄位
            if "visit_duration" not in payload:
                return

            # 獲取課程識別資訊
            course_id = str(payload.get("course_id", ""))
            course_code = payload.get("course_code", "")
            course_name = payload.get("course_name", "unknown")

            # 獲取原始時長
            original = int(payload["visit_duration"])

            # 計算新時長
            new_duration = self._calculate_duration(
                original, course_id, course_code
            )

            # 修改 visit_duration
            payload["visit_duration"] = new_duration

            # 更新請求內容
            flow.request.set_text(json.dumps(payload))

            # 輸出日誌
            print(f"[Interceptor] 課程: {course_name} (ID: {course_id})")
            print(f"[Interceptor] 時長修改: {original}秒 -> {new_duration}秒 "
                  f"(+{new_duration - original}秒)")

        except json.JSONDecodeError as e:
            print(f"[Interceptor] JSON 解析錯誤: {e}")
        except Exception as e:
            print(f"[Interceptor] 未預期錯誤: {e}")

    def _calculate_duration(
        self,
        original: int,
        course_id: str,
        course_code: str
    ) -> int:
        """
        計算新的時長值

        Args:
            original: 原始時長（秒）
            course_id: 課程 ID
            course_code: 課程代碼

        Returns:
            int: 新的時長值（秒）
        """
        # 嘗試使用 course_id 查找配置
        config = self.course_config.get(course_id)

        # 如果找不到，嘗試使用 course_code
        if not config and course_code:
            config = self.course_config.get(course_code)

        # 如果都找不到，使用預設增加值
        if not config:
            return original + self.default_increase

        # 根據模式計算新時長
        if self.mode == "multiplier" and "multiplier" in config:
            # 倍數模式
            multiplier = config["multiplier"]
            return original * multiplier

        elif self.mode == "increase" and "increase" in config:
            # 固定增加模式
            increase = config["increase"]
            return original + increase

        elif self.mode == "minimum" and "minimum" in config:
            # 最小值模式
            minimum = config["minimum"]
            return max(original, minimum)

        # 回退到預設增加值
        return original + self.default_increase

    @classmethod
    def from_courses_json(cls, courses_json_path: str, mode: str = "multiplier"):
        """
        從 courses.json 檔案載入配置

        Args:
            courses_json_path: courses.json 的路徑
            mode: 優先使用的模式

        Returns:
            VisitDurationInterceptor: 攔截器實例
        """
        try:
            with open(courses_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            course_config = {}
            for course in data.get("courses", []):
                course_id = str(course.get("course_id", ""))
                if not course_id:
                    continue

                # 提取時長相關配置
                config = {}
                if "visit_duration_multiplier" in course:
                    config["multiplier"] = course["visit_duration_multiplier"]
                if "visit_duration_increase" in course:
                    config["increase"] = course["visit_duration_increase"]
                if "min_visit_duration" in course:
                    config["minimum"] = course["min_visit_duration"]

                if config:
                    course_config[course_id] = config

            return cls(course_config=course_config, mode=mode)

        except Exception as e:
            print(f"[Interceptor] 載入配置失敗: {e}")
            return cls()

    def __repr__(self) -> str:
        return (f"VisitDurationInterceptor(mode={self.mode}, "
                f"courses={len(self.course_config)}, "
                f"default={self.default_increase}s)")


# ==================== 使用範例 ====================

if __name__ == "__main__":
    # 範例 1: 手動配置
    config = {
        "365": {"multiplier": 10, "increase": 5000, "minimum": 3600},
        "367": {"multiplier": 5, "increase": 3000, "minimum": 1800},
        "452": {"multiplier": 20, "increase": 10000, "minimum": 7200},
    }

    interceptor = VisitDurationInterceptor(
        course_config=config,
        mode="multiplier"  # 使用倍數模式
    )

    print(interceptor)
    print("\n測試計算：")
    print(f"課程 365，原始 100 秒 -> {interceptor._calculate_duration(100, '365', '')} 秒")
    print(f"課程 367，原始 100 秒 -> {interceptor._calculate_duration(100, '367', '')} 秒")
    print(f"課程 999（未設定），原始 100 秒 -> {interceptor._calculate_duration(100, '999', '')} 秒")

    # 範例 2: 從 courses.json 載入
    # interceptor = VisitDurationInterceptor.from_courses_json(
    #     "data/courses.json",
    #     mode="multiplier"
    # )

addons = [
    VisitDurationInterceptor.from_courses_json(
        "data/courses.json",
        mode="multiplier"
    )
]
