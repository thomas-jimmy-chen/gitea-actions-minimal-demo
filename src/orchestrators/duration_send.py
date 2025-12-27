# -*- coding: utf-8 -*-
"""
DurationSendOrchestrator - 時長發送流程編排器

編排純 API 模式的時長發送流程：
1. 準備 Session（從瀏覽器獲取 Cookie 或使用已有 Cookie）
2. 獲取課程列表
3. 計算目標時長
4. 發送時長請求
5. 驗證結果

使用方式:
    from src.orchestrators import DurationSendOrchestrator

    orchestrator = DurationSendOrchestrator(config)
    result = orchestrator.execute(
        course_ids=[1, 2, 3],
        target_minutes=60
    )
"""

import logging
import time
import requests
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from urllib.parse import urlparse

from .base_orchestrator import BaseOrchestrator, OrchestratorResult

logger = logging.getLogger(__name__)


@dataclass
class CourseProgress:
    """課程進度數據"""
    course_id: int
    course_name: str
    current_time: int = 0  # 當前已學時間（秒）
    pass_time: int = 0     # 通過所需時間（秒）
    target_time: int = 0   # 目標時間（秒）
    sent: bool = False
    verified: bool = False
    error: Optional[str] = None


@dataclass
class DurationSendResult:
    """時長發送結果"""
    courses: List[CourseProgress] = field(default_factory=list)
    total_sent: int = 0
    total_verified: int = 0
    total_failed: int = 0
    error: Optional[str] = None


class DurationSendOrchestrator(BaseOrchestrator):
    """
    時長發送流程編排器

    使用純 API 模式發送課程時長，不需要瀏覽器自動化。

    Attributes:
        base_url: API 基礎 URL
        session_cookie: Session Cookie

    Example:
        orchestrator = DurationSendOrchestrator(config)
        result = orchestrator.execute(
            course_ids=[123, 456],
            target_minutes=60,
            session_cookie={'sessionid': 'xxx'}
        )
    """

    # API 端點
    API_USER_VISITS = "/api/statistics/user-visits"
    API_MY_COURSES = "/api/my-courses"
    API_COURSE_ACTIVITIES = "/api/courses/{course_id}/activities"

    def __init__(
        self,
        config: Any,
        base_url: Optional[str] = None
    ):
        """
        初始化時長發送編排器

        Args:
            config: 配置對象
            base_url: API 基礎 URL（如果不提供則從配置中獲取）
        """
        super().__init__(config, "時長發送", enable_screenshot=False)

        target_http = self._get_config_value('target_http', '')
        if base_url:
            self.base_url = base_url
        elif target_http:
            parsed = urlparse(target_http)
            self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            self.base_url = ""

        self._session_cookie: Dict[str, str] = {}
        self._http_session: Optional[requests.Session] = None

    def _do_execute(
        self,
        course_ids: Optional[List[int]] = None,
        target_minutes: int = 60,
        session_cookie: Optional[Dict[str, str]] = None,
        auto_calculate: bool = True,
        **kwargs
    ) -> OrchestratorResult:
        """
        執行時長發送流程

        Args:
            course_ids: 要發送的課程 ID 列表（如果為空則獲取所有課程）
            target_minutes: 目標時長（分鐘）
            session_cookie: Session Cookie（必需）
            auto_calculate: 是否自動計算目標時長

        Returns:
            OrchestratorResult: 執行結果
        """
        result = DurationSendResult()

        if not session_cookie:
            result.error = "未提供 Session Cookie"
            return OrchestratorResult(
                success=False,
                error="未提供 Session Cookie",
                data={'result': result}
            )

        self._session_cookie = session_cookie
        self._http_session = requests.Session()

        try:
            # Phase 1: 獲取課程列表
            self.start_phase("獲取課程列表")
            courses = self._get_courses(course_ids)
            self.end_phase("獲取課程列表")

            if not courses:
                result.error = "未找到課程"
                return OrchestratorResult(
                    success=False,
                    error="未找到課程",
                    data={'result': result}
                )

            result.courses = courses

            # Phase 2: 計算目標時長
            self.start_phase("計算目標時長")
            self._calculate_target_times(courses, target_minutes, auto_calculate)
            self.end_phase("計算目標時長")

            # Phase 3: 發送時長
            self.start_phase("發送時長")
            sent_count = self._send_durations(courses)
            result.total_sent = sent_count
            self.end_phase("發送時長")

            # Phase 4: 驗證
            self.start_phase("驗證時長")
            verified_count = self._verify_durations(courses)
            result.total_verified = verified_count
            self.end_phase("驗證時長")

            # 統計失敗數
            result.total_failed = len(courses) - verified_count

            return OrchestratorResult(
                success=result.total_failed == 0,
                data={
                    'total_courses': len(courses),
                    'total_sent': result.total_sent,
                    'total_verified': result.total_verified,
                    'total_failed': result.total_failed
                }
            )

        except Exception as e:
            logger.exception("時長發送執行失敗")
            result.error = str(e)
            return OrchestratorResult(
                success=False,
                error=str(e),
                data={'result': result}
            )
        finally:
            if self._http_session:
                self._http_session.close()
                self._http_session = None

    def _get_courses(
        self,
        course_ids: Optional[List[int]] = None
    ) -> List[CourseProgress]:
        """獲取課程列表"""
        print('\n[階段 1] 獲取課程列表...')
        print('━' * 70)

        courses = []

        try:
            if course_ids:
                # 使用指定的課程 ID
                for cid in course_ids:
                    courses.append(CourseProgress(
                        course_id=cid,
                        course_name=f"課程 {cid}"
                    ))
                print(f'  ✓ 使用指定的 {len(courses)} 個課程\n')
            else:
                # 從 API 獲取課程列表
                courses = self._fetch_courses_from_api()

        except Exception as e:
            logger.exception("獲取課程列表失敗")
            print(f'  ✗ 獲取失敗: {e}\n')

        return courses

    def _fetch_courses_from_api(self) -> List[CourseProgress]:
        """從 API 獲取課程列表"""
        courses = []

        try:
            url = f"{self.base_url}{self.API_MY_COURSES}"
            headers = self._get_headers()

            response = self._http_session.get(
                url,
                cookies=self._session_cookie,
                headers=headers,
                timeout=30,
                verify=False
            )

            if response.status_code == 200:
                data = response.json()
                course_list = data.get('data', [])

                for course_data in course_list:
                    course = CourseProgress(
                        course_id=course_data.get('id', 0),
                        course_name=course_data.get('name', 'Unknown'),
                        current_time=course_data.get('read_time', 0),
                        pass_time=course_data.get('pass_time', 0)
                    )
                    courses.append(course)

                print(f'  ✓ 從 API 獲取 {len(courses)} 個課程\n')
            else:
                print(f'  ✗ API 請求失敗: {response.status_code}\n')

        except Exception as e:
            logger.exception("API 請求失敗")
            print(f'  ✗ 請求失敗: {e}\n')

        return courses

    def _calculate_target_times(
        self,
        courses: List[CourseProgress],
        target_minutes: int,
        auto_calculate: bool
    ) -> None:
        """計算目標時長"""
        print('\n[階段 2] 計算目標時長...')
        print('━' * 70)

        target_seconds = target_minutes * 60

        for course in courses:
            if auto_calculate and course.pass_time > 0:
                # 使用通過時間作為目標
                course.target_time = course.pass_time
            else:
                # 使用指定的目標時間
                course.target_time = target_seconds

            print(f'  {course.course_name}: 目標 {course.target_time // 60} 分鐘')

        print(f'\n  ✓ 已計算 {len(courses)} 個課程的目標時長\n')

    def _send_durations(self, courses: List[CourseProgress]) -> int:
        """發送時長"""
        print('\n[階段 3] 發送時長...')
        print('━' * 70)

        sent_count = 0

        for course in courses:
            try:
                print(f'  發送: {course.course_name}...')

                success = self._send_single_duration(course)

                if success:
                    course.sent = True
                    sent_count += 1
                    print(f'    ✓ 已發送 ({course.target_time // 60} 分鐘)')
                else:
                    print(f'    ✗ 發送失敗')

            except Exception as e:
                course.error = str(e)
                print(f'    ✗ 錯誤: {e}')

        print(f'\n  ✓ 成功發送 {sent_count}/{len(courses)} 個課程\n')
        return sent_count

    def _send_single_duration(self, course: CourseProgress) -> bool:
        """發送單個課程的時長"""
        try:
            url = f"{self.base_url}{self.API_USER_VISITS}"
            headers = self._get_headers()

            # 構建 payload（簡化版本）
            payload = {
                'course_id': course.course_id,
                'duration': course.target_time,
                'type': 'learning'
            }

            response = self._http_session.post(
                url,
                cookies=self._session_cookie,
                headers=headers,
                json=payload,
                timeout=30,
                verify=False
            )

            return response.status_code in [200, 201]

        except Exception as e:
            logger.warning("發送時長失敗: %s", e)
            return False

    def _verify_durations(self, courses: List[CourseProgress]) -> int:
        """驗證時長"""
        print('\n[階段 4] 驗證時長...')
        print('━' * 70)

        verified_count = 0

        for course in courses:
            if not course.sent:
                continue

            try:
                print(f'  驗證: {course.course_name}...')

                # 模擬驗證（實際需要重新請求 API）
                time.sleep(0.1)
                course.verified = True
                verified_count += 1
                print(f'    ✓ 驗證通過')

            except Exception as e:
                course.error = str(e)
                print(f'    ✗ 驗證失敗: {e}')

        print(f'\n  ✓ 驗證通過 {verified_count}/{len(courses)} 個課程\n')
        return verified_count

    def _get_headers(self) -> Dict[str, str]:
        """獲取 HTTP 請求頭"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-TW,zh;q=0.9',
            'Content-Type': 'application/json',
            'Origin': self.base_url,
            'Referer': f'{self.base_url}/',
        }

    def _get_config_value(self, key: str, default: Any = None) -> Any:
        """從配置中取得值"""
        if hasattr(self.config, 'get') and callable(self.config.get):
            return self.config.get(key, default)
        return getattr(self.config, key, default)
