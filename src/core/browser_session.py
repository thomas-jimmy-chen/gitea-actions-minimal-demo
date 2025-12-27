# -*- coding: utf-8 -*-
"""
BrowserSession - 統一的瀏覽器會話管理器

提供上下文管理器模式的瀏覽器會話管理，統一初始化和清理流程。

Usage:
    from src.core.browser_session import BrowserSession

    with BrowserSession(config) as session:
        session.login()
        session.goto_my_courses()
        # 執行操作...
    # 自動清理資源
"""

import logging
from typing import Any, Optional, List
from contextlib import contextmanager
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class SessionConfig:
    """會話配置資料類"""
    use_proxy: bool = False
    interceptors: List[Any] = field(default_factory=list)
    auto_login: bool = True
    goto_my_courses: bool = False


class BrowserSession:
    """
    瀏覽器會話管理器。

    提供統一的瀏覽器初始化、登入、頁面導航和資源清理功能。
    支援上下文管理器模式 (with 語句) 自動管理資源生命週期。

    Attributes:
        config: 應用配置物件
        driver: WebDriver 實例
        login_page: LoginPage 實例
        course_list_page: CourseListPage 實例
        proxy: ProxyManager 實例（如果啟用）

    Example:
        # 基本用法
        with BrowserSession(config) as session:
            if session.login():
                session.goto_my_courses()
                # 執行操作...

        # 帶 Proxy 的用法
        with BrowserSession(config, use_proxy=True, interceptors=[...]) as session:
            session.login()
            # 攔截器會自動處理請求...
    """

    def __init__(
        self,
        config: Any,
        use_proxy: bool = False,
        interceptors: Optional[List[Any]] = None,
        auto_login: bool = False,
        goto_my_courses: bool = False
    ):
        """
        初始化 BrowserSession。

        Args:
            config: 應用配置物件
            use_proxy: 是否啟用代理 (MitmProxy)
            interceptors: 代理攔截器列表
            auto_login: 進入時是否自動登入
            goto_my_courses: 登入後是否自動前往我的課程
        """
        self.config = config
        self.session_config = SessionConfig(
            use_proxy=use_proxy,
            interceptors=interceptors or [],
            auto_login=auto_login,
            goto_my_courses=goto_my_courses
        )

        # 將在 __enter__ 中初始化
        self.driver_manager = None
        self.cookie_manager = None
        self.proxy = None
        self.driver = None
        self.login_page = None
        self.course_list_page = None

        self._is_initialized = False
        self._login_success = False

    def _get_config_value(self, key: str, default: Any = None) -> Any:
        """從配置中取得值。"""
        if hasattr(self.config, 'get') and callable(self.config.get):
            return self.config.get(key, default)
        return getattr(self.config, key, default)

    def _initialize(self) -> None:
        """初始化所有組件。"""
        # 延遲導入以避免循環依賴
        from src.core.driver_manager import DriverManager
        from src.core.cookie_manager import CookieManager
        from src.pages.login_page import LoginPage
        from src.pages.course_list_page import CourseListPage

        logger.info("初始化 BrowserSession (proxy=%s)", self.session_config.use_proxy)

        # 建立核心管理器
        self.driver_manager = DriverManager(self.config)
        self.cookie_manager = CookieManager(
            self._get_config_value('cookies_file')
        )

        # 啟動 Proxy（如果需要）
        if self.session_config.use_proxy and self.session_config.interceptors:
            from src.core.proxy_manager import ProxyManager
            self.proxy = ProxyManager(
                self.config,
                interceptors=self.session_config.interceptors
            )
            self.proxy.start()
            logger.info("Proxy 已啟動")

        # 建立 WebDriver
        self.driver = self.driver_manager.create_driver(
            use_proxy=self.session_config.use_proxy
        )

        # 建立頁面物件
        self.login_page = LoginPage(self.driver, self.cookie_manager)
        self.course_list_page = CourseListPage(self.driver)

        self._is_initialized = True
        logger.info("BrowserSession 初始化完成")

    def _cleanup(self) -> None:
        """清理所有資源。"""
        logger.info("清理 BrowserSession 資源")

        # 關閉 WebDriver
        if self.driver:
            try:
                self.driver.quit()
                logger.debug("WebDriver 已關閉")
            except Exception as e:
                logger.warning("關閉 WebDriver 時發生錯誤: %s", e)
            self.driver = None

        # 停止 Proxy
        if self.proxy:
            try:
                self.proxy.stop()
                logger.debug("Proxy 已停止")
            except Exception as e:
                logger.warning("停止 Proxy 時發生錯誤: %s", e)
            self.proxy = None

        self._is_initialized = False
        logger.info("BrowserSession 資源已清理")

    def __enter__(self) -> 'BrowserSession':
        """進入上下文管理器。"""
        self._initialize()

        # 自動登入（如果配置）
        if self.session_config.auto_login:
            self._login_success = self.login()

            # 自動前往我的課程（如果配置且登入成功）
            if self._login_success and self.session_config.goto_my_courses:
                self.goto_my_courses()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """離開上下文管理器。"""
        self._cleanup()
        # 不抑制異常，返回 None 或 False

    def login(self, max_retries: int = 3) -> bool:
        """
        執行登入。

        Args:
            max_retries: 最大重試次數

        Returns:
            登入是否成功
        """
        if not self._is_initialized:
            raise RuntimeError("BrowserSession 尚未初始化")

        username = self._get_config_value('user_name')
        password = self._get_config_value('password')
        target_url = self._get_config_value('target_http')

        for attempt in range(max_retries):
            success = self.login_page.auto_login(
                username=username,
                password=password,
                url=target_url
            )

            if success:
                self._login_success = True
                logger.info("登入成功 (嘗試次數: %d)", attempt + 1)
                return True

            if attempt < max_retries - 1:
                logger.warning("登入失敗，重試中 (%d/%d)", attempt + 1, max_retries)
                self.login_page.goto(target_url)

        logger.error("登入失敗，已達最大重試次數")
        return False

    def goto_my_courses(self) -> None:
        """前往我的課程頁面。"""
        if not self._is_initialized:
            raise RuntimeError("BrowserSession 尚未初始化")

        self.course_list_page.goto_my_courses()
        logger.info("已前往我的課程頁面")

    def is_logged_in(self) -> bool:
        """檢查是否已登入。"""
        return self._login_success

    def restart_with_proxy(
        self,
        interceptors: Optional[List[Any]] = None
    ) -> 'BrowserSession':
        """
        重啟會話並啟用 Proxy。

        此方法會關閉當前瀏覽器，然後使用 Proxy 重新啟動。
        這對於需要在中途啟用攔截器的場景很有用。

        Args:
            interceptors: 新的攔截器列表

        Returns:
            self，支援鏈式調用
        """
        logger.info("重啟會話並啟用 Proxy")

        # 關閉當前 driver
        if self.driver:
            self.driver.quit()
            self.driver = None

        # 更新配置
        self.session_config.use_proxy = True
        if interceptors:
            self.session_config.interceptors = interceptors

        # 延遲導入
        from src.core.proxy_manager import ProxyManager
        from src.pages.login_page import LoginPage
        from src.pages.course_list_page import CourseListPage

        # 啟動 Proxy
        if self.session_config.interceptors:
            self.proxy = ProxyManager(
                self.config,
                interceptors=self.session_config.interceptors
            )
            self.proxy.start()

        # 建立新的 driver
        self.driver = self.driver_manager.create_driver(use_proxy=True)

        # 重建頁面物件
        self.login_page = LoginPage(self.driver, self.cookie_manager)
        self.course_list_page = CourseListPage(self.driver)

        self._login_success = False
        logger.info("會話已重啟（Proxy 模式）")

        return self

    def restart_without_proxy(self) -> 'BrowserSession':
        """
        重啟會話並禁用 Proxy。

        Returns:
            self，支援鏈式調用
        """
        logger.info("重啟會話並禁用 Proxy")

        # 關閉當前 driver
        if self.driver:
            self.driver.quit()
            self.driver = None

        # 停止 Proxy
        if self.proxy:
            self.proxy.stop()
            self.proxy = None

        # 更新配置
        self.session_config.use_proxy = False

        # 延遲導入
        from src.pages.login_page import LoginPage
        from src.pages.course_list_page import CourseListPage

        # 建立新的 driver
        self.driver = self.driver_manager.create_driver(use_proxy=False)

        # 重建頁面物件
        self.login_page = LoginPage(self.driver, self.cookie_manager)
        self.course_list_page = CourseListPage(self.driver)

        self._login_success = False
        logger.info("會話已重啟（無 Proxy 模式）")

        return self

    @property
    def is_proxy_enabled(self) -> bool:
        """檢查 Proxy 是否啟用。"""
        return self.session_config.use_proxy and self.proxy is not None

    def get_current_url(self) -> str:
        """取得當前頁面 URL。"""
        if self.driver:
            return self.driver.current_url
        return ""

    def save_cookies(self) -> None:
        """儲存當前 cookies。"""
        if self.driver and self.cookie_manager:
            cookies = self.driver.get_cookies()
            self.cookie_manager.save(cookies)
            logger.info("Cookies 已儲存")


@contextmanager
def browser_session(
    config: Any,
    use_proxy: bool = False,
    interceptors: Optional[List[Any]] = None
):
    """
    瀏覽器會話的函數式上下文管理器。

    Args:
        config: 應用配置
        use_proxy: 是否啟用代理
        interceptors: 代理攔截器列表

    Yields:
        BrowserSession 實例

    Example:
        with browser_session(config, use_proxy=True) as session:
            session.login()
            # 操作...
    """
    session = BrowserSession(config, use_proxy, interceptors)
    try:
        session._initialize()
        yield session
    finally:
        session._cleanup()
