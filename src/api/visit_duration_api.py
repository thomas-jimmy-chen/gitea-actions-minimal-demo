#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
VisitDurationAPI - 訪問時長 API 直接調用模組
透過 API 直接發送訪問時長，無需使用 MitmProxy 攔截
"""

import requests
import json
from datetime import datetime
from typing import Dict, Optional
import urllib3

from src.constants import is_http_success

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class VisitDurationAPI:
    """訪問時長 API 直接調用類"""

    def __init__(self, base_url: str, session_cookie: Dict[str, str], user_info: Dict[str, str]):
        """
        初始化

        Args:
            base_url: 基礎 URL (e.g., https://elearn.post.gov.tw)
            session_cookie: Session Cookie 字典 (e.g., {'session': 'V2-...'})
            user_info: 用戶資訊字典，包含:
                - user_id: 用戶 ID
                - user_no: 員工編號
                - user_name: 用戶姓名
                - org_id: 組織 ID (通常為 "1")
                - org_name: 組織名稱 (通常為 "郵政ｅ大學")
                - dep_id: 部門 ID
                - dep_name: 部門名稱
                - dep_code: 部門代碼
        """
        self.base_url = base_url.rstrip('/')
        self.session_cookie = session_cookie
        self.user_info = user_info
        self.api_url = f"{self.base_url}/statistics/api/user-visits"

    def send_visit_duration(
        self,
        visit_duration: int,
        course_id: Optional[str] = None,
        course_code: Optional[str] = None,
        course_name: Optional[str] = None,
        activity_id: Optional[str] = None,
        activity_type: Optional[str] = None
    ) -> bool:
        """
        發送訪問時長到伺服器

        Args:
            visit_duration: 訪問時長（秒）
            course_id: 課程 ID（可選）
            course_code: 課程代碼（可選）
            course_name: 課程名稱（可選）
            activity_id: 活動 ID（可選）
            activity_type: 活動類型（可選，如 'scorm'）

        Returns:
            bool: 是否成功（狀態碼 204）
        """
        # 構建請求 payload
        payload = {
            # 必需欄位
            "user_id": self.user_info['user_id'],
            "org_id": self.user_info.get('org_id', '1'),
            "visit_duration": visit_duration,
            "is_teacher": False,
            "browser": "chrome",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "visit_start_from": self._get_current_timestamp(),
            "org_name": self.user_info.get('org_name', '郵政ｅ大學'),
            "user_no": self.user_info['user_no'],
            "user_name": self.user_info['user_name'],
            "dep_id": self.user_info['dep_id'],
            "dep_name": self.user_info['dep_name'],
            "dep_code": self.user_info['dep_code'],
        }

        # 添加可選欄位
        if course_id:
            payload['course_id'] = course_id
        if course_code:
            payload['course_code'] = course_code
        if course_name:
            payload['course_name'] = course_name
        if activity_id:
            payload['activity_id'] = activity_id
        if activity_type:
            payload['activity_type'] = activity_type

        # 添加 master_course_id（通常為 0）
        if course_id:
            payload['master_course_id'] = 0

        # ✨ 動態設置 Referer（基於 Burp Suite 分析）
        if course_id:
            referer = f'{self.base_url}/course/{course_id}/content'
        else:
            referer = f'{self.base_url}/user/courses'

        # HTTP Headers（100% 符合真實請求 - 基於 Burp Suite 完整分析）
        headers = {
            'Content-Type': 'text/plain;charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Origin': self.base_url,
            'Referer': referer,
            'Sec-Ch-Ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Dest': 'empty',
            'Dnt': '1',
        }

        try:
            # 發送 POST 請求
            response = requests.post(
                self.api_url,
                cookies=self.session_cookie,
                headers=headers,
                json=payload,
                verify=False,
                timeout=30
            )

            # 204 No Content 表示成功
            if response.status_code == 204:
                print(f'  ✓ API 調用成功 (Referer: {referer}, 時長: {visit_duration}秒 = {visit_duration/60:.1f}分鐘)')

                # 🔑 關鍵：發送 announcement 檢查使時長生效
                self.trigger_announcement_check(course_id=course_id)

                return True
            else:
                print(f'  ✗ API 調用失敗，狀態碼: {response.status_code}')
                return False

        except requests.exceptions.RequestException as e:
            print(f'  ✗ 發送訪問時長失敗: {e}')
            return False

    def get_current_duration(self, course_id: str) -> Optional[float]:
        """
        查詢當前課程的累積訪問時長

        Args:
            course_id: 課程 ID

        Returns:
            float: 累積訪問時長（秒），如果失敗則返回 None
        """
        user_id = self.user_info['user_id']
        metrics_url = f"{self.base_url}/statistics/api/courses/{course_id}/users/{user_id}/user-visits/metrics"

        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
        }

        try:
            response = requests.get(
                metrics_url,
                cookies=self.session_cookie,
                headers=headers,
                verify=False,
                timeout=30
            )

            if is_http_success(response.status_code):
                data = response.json()
                return float(data.get('sum', 0))
            else:
                print(f'[WARNING] 查詢時長失敗，狀態碼: {response.status_code}')
                return None

        except requests.exceptions.RequestException as e:
            print(f'[ERROR] 查詢訪問時長失敗: {e}')
            return None

    def trigger_announcement_check(self, course_id: Optional[str] = None) -> bool:
        """
        觸發 announcement 檢查（關鍵：使時長生效）

        根據 Burp Suite 分析，發送時長後必須調用此 API 才能使時長生效。
        此請求會觸發伺服器端的 session 更新或時長記錄確認。

        Args:
            course_id: 課程 ID（用於設置正確的 Referer）

        Returns:
            bool: 是否成功（狀態碼 200）
        """
        url = f'{self.base_url}/api/announcement'

        # 動態設置 Referer（與發送時長時保持一致）
        if course_id:
            referer = f'{self.base_url}/course/{course_id}/content'
        else:
            referer = f'{self.base_url}/user/courses'

        # HTTP Headers（100% 符合真實請求）
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': referer,
            'Sec-Ch-Ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',  # 注意：這裡是 cors，不是 no-cors
            'Sec-Fetch-Dest': 'empty',
            'Dnt': '1',
        }

        try:
            # 發送 GET 請求
            response = requests.get(
                url,
                cookies=self.session_cookie,
                headers=headers,
                verify=False,
                timeout=10
            )

            from src.constants import is_http_success

            # 2xx 狀態碼表示成功
            if is_http_success(response.status_code):
                print(f'  ✓ Announcement 檢查成功 - 時長已生效')
                return True
            else:
                print(f'  ✗ Announcement 檢查失敗，狀態碼: {response.status_code}')
                return False

        except requests.exceptions.RequestException as e:
            print(f'  ✗ Announcement 檢查失敗: {e}')
            return False

    def _get_current_timestamp(self) -> str:
        """
        獲取當前時間戳（格式: YYYY/MM/DDTHH:MM:SS）

        Returns:
            str: 格式化的時間戳
        """
        now = datetime.now()
        return now.strftime('%Y/%m/%dT%H:%M:%S')

    @staticmethod
    def extract_user_info_from_cookies(driver) -> Optional[Dict[str, str]]:
        """
        從 WebDriver 中提取用戶資訊（透過多種方法嘗試）

        Args:
            driver: Selenium WebDriver 實例

        Returns:
            Dict[str, str]: 用戶資訊字典，如果失敗則返回 None
        """

        # 方法 1: 嘗試從 localStorage 提取
        try:
            print('  [嘗試 1/4] 從 localStorage 提取用戶資訊...')
            script = """
            try {
                var userData = localStorage.getItem('user') || localStorage.getItem('currentUser');
                if (userData) {
                    return JSON.parse(userData);
                }
                return null;
            } catch(e) {
                return null;
            }
            """
            user_data = driver.execute_script(script)
            if user_data and all(user_data.get(f) for f in ['id', 'no', 'name']):
                return {
                    'user_id': str(user_data.get('id')),
                    'user_no': str(user_data.get('no')),
                    'user_name': str(user_data.get('name')),
                    'org_id': '1',
                    'org_name': '郵政ｅ大學',
                    'dep_id': str(user_data.get('dep_id', user_data.get('department_id', ''))),
                    'dep_name': str(user_data.get('dep_name', user_data.get('department_name', ''))),
                    'dep_code': str(user_data.get('dep_code', user_data.get('department_code', '')))
                }
        except Exception as e:
            print(f'    ✗ localStorage 方法失敗: {e}')

        # 方法 2: 嘗試從頁面 data attributes 提取
        try:
            print('  [嘗試 2/4] 從頁面 data attributes 提取...')
            script = """
            try {
                var userElement = document.querySelector('[data-user-id]') ||
                                  document.querySelector('[data-current-user]') ||
                                  document.querySelector('.user-info');
                if (userElement) {
                    return {
                        user_id: userElement.getAttribute('data-user-id') || userElement.dataset.userId,
                        user_no: userElement.getAttribute('data-user-no') || userElement.dataset.userNo,
                        user_name: userElement.getAttribute('data-user-name') || userElement.dataset.userName,
                        dep_id: userElement.getAttribute('data-dep-id') || userElement.dataset.depId,
                        dep_name: userElement.getAttribute('data-dep-name') || userElement.dataset.depName,
                        dep_code: userElement.getAttribute('data-dep-code') || userElement.dataset.depCode
                    };
                }
                return null;
            } catch(e) {
                return null;
            }
            """
            user_data = driver.execute_script(script)
            if user_data and all(user_data.get(f) for f in ['user_id', 'user_no', 'user_name']):
                user_data['org_id'] = '1'
                user_data['org_name'] = '郵政ｅ大學'
                return user_data
        except Exception as e:
            print(f'    ✗ data attributes 方法失敗: {e}')

        # 方法 3: 嘗試從頁面 meta tags 或隱藏欄位提取
        try:
            print('  [嘗試 3/4] 從頁面 meta/hidden fields 提取...')
            script = """
            try {
                return {
                    user_id: document.querySelector('meta[name="user-id"]')?.content ||
                             document.querySelector('input[name="user_id"]')?.value,
                    user_no: document.querySelector('meta[name="user-no"]')?.content ||
                             document.querySelector('input[name="user_no"]')?.value,
                    user_name: document.querySelector('meta[name="user-name"]')?.content ||
                               document.querySelector('input[name="user_name"]')?.value ||
                               document.querySelector('.user-name')?.textContent?.trim(),
                    dep_id: document.querySelector('meta[name="dep-id"]')?.content ||
                            document.querySelector('input[name="dep_id"]')?.value,
                    dep_name: document.querySelector('meta[name="dep-name"]')?.content ||
                              document.querySelector('input[name="dep_name"]')?.value,
                    dep_code: document.querySelector('meta[name="dep-code"]')?.content ||
                              document.querySelector('input[name="dep_code"]')?.value
                };
            } catch(e) {
                return null;
            }
            """
            user_data = driver.execute_script(script)
            if user_data and all(user_data.get(f) for f in ['user_id', 'user_no', 'user_name']):
                user_data['org_id'] = '1'
                user_data['org_name'] = '郵政ｅ大學'
                return user_data
        except Exception as e:
            print(f'    ✗ meta/hidden 方法失敗: {e}')

        # 方法 4: 嘗試從 Angular scope 提取（如果使用 Angular）
        try:
            print('  [嘗試 4/4] 從 Angular scope 提取...')
            script = """
            try {
                var scope = angular.element(document.body).scope();
                if (scope && scope.currentUser) {
                    return {
                        user_id: scope.currentUser.id,
                        user_no: scope.currentUser.no,
                        user_name: scope.currentUser.name,
                        dep_id: scope.currentUser.dep_id,
                        dep_name: scope.currentUser.dep_name,
                        dep_code: scope.currentUser.dep_code
                    };
                }
                return null;
            } catch(e) {
                return null;
            }
            """
            user_data = driver.execute_script(script)
            if user_data and all(user_data.get(f) for f in ['user_id', 'user_no', 'user_name']):
                user_data['org_id'] = '1'
                user_data['org_name'] = '郵政ｅ大學'
                return user_data
        except Exception as e:
            print(f'    ✗ Angular scope 方法失敗: {e}')

        print('  ✗ 所有方法都無法提取用戶資訊')
        return None

    @staticmethod
    def get_user_info_from_api(base_url: str, session_cookie: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        從 API 獲取用戶資訊

        Args:
            base_url: 基礎 URL
            session_cookie: Session Cookie 字典

        Returns:
            Dict[str, str]: 用戶資訊字典，如果失敗則返回 None
        """
        try:
            # 嘗試常見的用戶資訊 API 端點
            endpoints = [
                '/api/user/info',
                '/api/me',
                '/api/user/profile',
                '/api/user',
            ]

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            }

            for endpoint in endpoints:
                try:
                    api_url = f"{base_url.rstrip('/')}{endpoint}"
                    response = requests.get(
                        api_url,
                        cookies=session_cookie,
                        headers=headers,
                        verify=False,
                        timeout=10
                    )

                    if is_http_success(response.status_code):
                        data = response.json()
                        # 嘗試從回應中提取用戶資訊
                        if isinstance(data, dict):
                            user_info = {
                                'user_id': str(data.get('id', data.get('user_id', ''))),
                                'user_no': str(data.get('no', data.get('user_no', data.get('employee_no', '')))),
                                'user_name': str(data.get('name', data.get('user_name', data.get('username', '')))),
                                'org_id': '1',
                                'org_name': '郵政ｅ大學',
                                'dep_id': str(data.get('dep_id', data.get('department_id', ''))),
                                'dep_name': str(data.get('dep_name', data.get('department_name', ''))),
                                'dep_code': str(data.get('dep_code', data.get('department_code', '')))
                            }

                            # 驗證必需欄位
                            if all(user_info.get(f) for f in ['user_id', 'user_no', 'user_name']):
                                print(f'  ✓ 從 API {endpoint} 成功獲取用戶資訊')
                                return user_info

                except requests.exceptions.RequestException:
                    continue

            print('  ✗ 所有 API 端點都無法獲取用戶資訊')
            return None

        except Exception as e:
            print(f'  ✗ API 獲取用戶資訊失敗: {e}')
            return None

    def send_visit_duration_in_batches(
        self,
        total_duration: int,
        max_batch_size: int = 3600,
        course_id: Optional[str] = None,
        course_code: Optional[str] = None,
        course_name: Optional[str] = None,
        activity_id: Optional[str] = None,
        activity_type: Optional[str] = None,
        delay_between_batches: int = 2
    ) -> Dict[str, any]:
        """
        分批發送訪問時長（每次最多 max_batch_size 秒）

        Args:
            total_duration: 總時長（秒）
            max_batch_size: 每批最大時長（秒），默認 3600 秒（60分鐘）
            course_id: 課程 ID
            course_code: 課程代碼
            course_name: 課程名稱
            activity_id: 活動 ID
            activity_type: 活動類型
            delay_between_batches: 批次之間的延遲（秒），默認 2 秒

        Returns:
            Dict: {
                'success': bool,
                'total_duration': int,
                'batches': int,
                'successful_batches': int,
                'failed_batches': int,
                'details': List[Dict]
            }
        """
        import time

        # 計算需要分幾批
        batches = []
        remaining = total_duration

        while remaining > 0:
            batch_size = min(remaining, max_batch_size)
            batches.append(batch_size)
            remaining -= batch_size

        print(f'\n  📦 分批發送策略:')
        print(f'     總時長: {total_duration} 秒 ({total_duration/60:.1f} 分鐘)')
        print(f'     分為 {len(batches)} 批: {[f"{b}秒({b/60:.0f}分)" for b in batches]}')

        # 執行發送
        results = {
            'success': True,
            'total_duration': total_duration,
            'batches': len(batches),
            'successful_batches': 0,
            'failed_batches': 0,
            'details': []
        }

        for i, batch_size in enumerate(batches, 1):
            print(f'\n  [{i}/{len(batches)}] 發送 {batch_size} 秒 ({batch_size/60:.1f} 分鐘)...')

            success = self.send_visit_duration(
                visit_duration=batch_size,
                course_id=course_id,
                course_code=course_code,
                course_name=course_name,
                activity_id=activity_id,
                activity_type=activity_type
            )

            batch_result = {
                'batch_number': i,
                'duration': batch_size,
                'success': success
            }
            results['details'].append(batch_result)

            if success:
                results['successful_batches'] += 1
                print(f'     ✓ 批次 {i} 發送成功')
            else:
                results['failed_batches'] += 1
                results['success'] = False
                print(f'     ✗ 批次 {i} 發送失敗')

            # 如果不是最後一批，等待一段時間
            if i < len(batches):
                print(f'     ⏳ 等待 {delay_between_batches} 秒...')
                time.sleep(delay_between_batches)

        # 總結
        print(f'\n  📊 發送總結:')
        print(f'     成功: {results["successful_batches"]}/{results["batches"]} 批')
        if results['failed_batches'] > 0:
            print(f'     失敗: {results["failed_batches"]} 批')

        return results

    def __repr__(self) -> str:
        return f"VisitDurationAPI(base_url={self.base_url}, user={self.user_info.get('user_name', 'Unknown')})"
