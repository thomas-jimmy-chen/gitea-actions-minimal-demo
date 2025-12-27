#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
ProxyManager - MitmProxy 管理器
負責 MitmProxy 的啟動、配置與生命週期管理
"""

import os
import sys
import asyncio
import time
import socket
import threading
import logging
from datetime import datetime

# ============================================================================
# 版本歷史與修改記錄
# ============================================================================
# v2.0.1 (原始版本) - 使用 multiprocessing.Process
# - 在 Linux/macOS 下運行良好
# - 在 Windows + Python 3.13 下有兼容性問題（asyncio + multiprocessing）
#
# v2.0.2 (2025-12-06) - 改用 threading.Thread
# - 修復 Windows 兼容性問題
# - 保留原始 multiprocessing 代碼作為註解（見下方）
# ============================================================================

# ============================================================================
# [已註解] 原始 multiprocessing 版本（v2.0.1）
# ============================================================================
# from multiprocessing import Process
#
# 原始使用方式：
#   self.process = Process(target=self._run)
#   self.process.start()
#
# Windows 問題：
#   - multiprocessing 在 Windows 下使用 spawn 模式
#   - asyncio 事件循環無法正確在子進程中啟動
#   - 導致 MitmProxy 無法正常監聽端口
# ============================================================================

from mitmproxy.options import Options as MitmOptions
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.master import Master
from .config_loader import ConfigLoader


class ProxyManager:
    """管理 MitmProxy 的生命週期"""

    def __init__(self, config: ConfigLoader, interceptors: list = None):
        """
        初始化 Proxy 管理器

        Args:
            config: 配置載入器
            interceptors: 攔截器列表（addons）
        """
        self.host = config.get('listen_host', '127.0.0.1')
        self.port = config.get_int('listen_port', 8080)
        self.silent = config.get_bool('silent_mitm', False)
        self.log_save = config.get_bool('log_save', False)
        self.interceptors = interceptors or []

        # ============================================================================
        # v2.0.2: 改用 threading.Thread（原為 multiprocessing.Process）
        # ============================================================================
        self.thread = None  # v2.0.2: 使用 thread 代替 process
        # self.process = None  # v2.0.1: 原始版本使用 process

        # ✅ v2.0.7: 保存 master 引用以便優雅關閉
        self.master = None

    def _silence_stdout(self):
        """將標準輸出/錯誤重導向到檔案或 null"""
        sys.stdout.flush()
        sys.stderr.flush()

        if self.log_save:
            # 儲存到日誌檔案
            now = datetime.now().strftime("%Y%m%d%H%M%S")
            os.makedirs("log", exist_ok=True)
            log_file = os.path.join("log", f"mitm_{now}.log")
            f = open(log_file, 'w', encoding='utf-8')
            os.dup2(f.fileno(), 1)
            os.dup2(f.fileno(), 2)
        else:
            # 重導向到 null
            devnull = open(os.devnull, 'w')
            os.dup2(devnull.fileno(), 1)
            os.dup2(devnull.fileno(), 2)

    async def _config(self):
        """
        配置並執行 MitmProxy

        版本歷史：
        - v2.0.1: 無日誌配置（在 _run() 中使用 _silence_stdout()）
        - v2.0.2: 改用 Python logging 配置（threading 模式下不能重定向 stdout）
        - v2.0.3: 移除不支援的 MitmOptions 參數（termlog_verbosity, flow_detail, quiet）
        - v2.0.4: 嘗試使用 Master 類（失敗：Master 沒有 ProxyServer addon）
        - v2.0.5: 在線程內部重定向 stdout/stderr（失敗：sys.stdout 是全局的）
        - v2.0.6: 移除 DumpMaster 的輸出 addons（TermLog, Dumper）
        """
        # ============================================================================
        # v2.0.6: 使用 DumpMaster + 移除輸出相關的 addons
        # ============================================================================
        # 測試發現：
        # - Master 類沒有 ProxyServer addon，無法監聽端口
        # - DumpMaster 有 36 個 addons，其中 TermLog 和 Dumper 負責輸出
        # - 移除這兩個 addons 即可抑制輸出，同時保留所有其他功能
        # - 不需要重定向 stdout（避免影響主線程）

        # ✅ 關鍵修復：使用 mode 參數指定端口（避免端口衝突）
        # 根據 mitmproxy 文檔：https://docs.mitmproxy.org/stable/concepts/options/
        # mode 參數可以附加端口：regular@8080, regular@8081
        opts = MitmOptions(
            listen_host=self.host,
            listen_port=self.port,
            mode=[f"regular@{self.port}"]  # 在 mode 中明確指定端口
        )

        master = DumpMaster(opts)

        # ✅ v2.0.7: 保存 master 引用
        self.master = master

        # 靜默模式：移除輸出相關的 addons
        if self.silent:
            import warnings
            warnings.filterwarnings('ignore')

            # 移除 TermLog addon（終端日誌輸出）
            termlog_addon = None
            for addon in master.addons.chain:
                if type(addon).__name__ == 'TermLog':
                    termlog_addon = addon
                    break
            if termlog_addon:
                master.addons.remove(termlog_addon)

            # 移除 Dumper addon（流量轉儲輸出）
            dumper_addon = None
            for addon in master.addons.chain:
                if type(addon).__name__ == 'Dumper':
                    dumper_addon = addon
                    break
            if dumper_addon:
                master.addons.remove(dumper_addon)

        # 加入攔截器
        for interceptor in self.interceptors:
            master.addons.add(interceptor)

        try:
            await master.run()
        except KeyboardInterrupt:
            master.shutdown()

    def _run(self):
        """
        在獨立 Thread 中執行 MitmProxy

        版本歷史：
        - v2.0.1: 在獨立 Process 中執行（Windows 下有問題）
        - v2.0.2: 改為在獨立 Thread 中執行（修復 Windows 兼容性）
        - v2.0.5: 在線程內部重定向 stdout/stderr（失敗：sys.stdout 是全局的）
        - v2.0.6: 改為在 _config() 中移除輸出 addons（正確方法）
        - v2.0.10: 抑制 Windows asyncio 的 ConnectionResetError 警告
        """
        # ============================================================================
        # v2.0.10: 抑制 Windows asyncio ConnectionResetError 警告
        # ============================================================================
        # Windows 下 asyncio 的 IocpProactor 在連接快速關閉時會拋出 ConnectionResetError
        # 這不影響功能，只是日誌噪音，所以我們抑制這些警告
        import warnings
        warnings.filterwarnings('ignore', message='.*ConnectionResetError.*')
        warnings.filterwarnings('ignore', message='.*WinError 10054.*')

        # ============================================================================
        # v2.0.6: Threading 版本 + 移除輸出 addons
        # ============================================================================
        # 在 threading 模式下，我們不能修改 sys.stdout（它是全局的）
        # 正確的方法是在 _config() 中移除 DumpMaster 的輸出 addons (TermLog, Dumper)

        # 在當前線程中創建新的事件循環
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # ✅ 設置自定義異常處理器，抑制 ConnectionResetError
        def exception_handler(loop, context):
            """自定義異常處理器，抑制 Windows asyncio 的 ConnectionResetError"""
            exception = context.get('exception')
            if isinstance(exception, (ConnectionResetError, ConnectionAbortedError)):
                # 靜默處理連接重置錯誤（Windows asyncio 的已知問題）
                return
            # 其他異常仍然打印
            loop.default_exception_handler(context)

        loop.set_exception_handler(exception_handler)

        try:
            loop.run_until_complete(self._config())
        finally:
            loop.close()

        # ============================================================================
        # [已註解] v2.0.1: Multiprocessing 版本
        # ============================================================================
        # if self.silent:
        #     self._silence_stdout()  # 子進程中重定向 stdout
        #
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # loop.run_until_complete(self._config())
        # loop.close()
        # ============================================================================

    def _check_port_listening(self, max_retries: int = 10, retry_delay: float = 0.5) -> bool:
        """
        檢查端口是否正在監聽

        Args:
            max_retries: 最大重試次數
            retry_delay: 每次重試間隔（秒）

        Returns:
            bool: 端口是否可用
        """
        for attempt in range(max_retries):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex((self.host, self.port))
                    if result == 0:
                        return True
            except Exception:
                pass

            if attempt < max_retries - 1:
                time.sleep(retry_delay)

        return False

    def start(self):
        """
        啟動 MitmProxy

        版本歷史：
        - v2.0.1: 使用 multiprocessing.Process
        - v2.0.2: 改用 threading.Thread（修復 Windows 兼容性）
        """
        if not self.silent:
            print(f"[INFO] Starting network monitoring on {self.host}:{self.port}")
        elif self.log_save:
            print("[INFO] Starting network monitoring in silent mode with logging...")
        else:
            print("[INFO] Starting network monitoring in silent mode...")

        # ============================================================================
        # v2.0.2: Threading 版本（當前使用）
        # ============================================================================
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

        # ============================================================================
        # [已註解] v2.0.1: Multiprocessing 版本
        # ============================================================================
        # self.process = Process(target=self._run)
        # self.process.start()
        # ============================================================================

        # Windows 相容性修復：增加等待時間並檢查端口
        # 初始等待時間（從 1 秒增加到 3 秒）
        time.sleep(3)

        # 檢查端口是否正在監聽（最多等待 5 秒）
        if not self._check_port_listening(max_retries=10, retry_delay=0.5):
            print('[WARN] Network monitoring may not be ready (port not listening)')
            print(f'[WARN] Please check if port {self.port} is available')
        else:
            print('[INFO] Network monitoring started successfully')

    def stop(self):
        """
        停止 MitmProxy

        版本歷史：
        - v2.0.1: 使用 process.terminate() 和 process.kill()
        - v2.0.2: 改用 thread.join()（threading 無法強制終止）
        - v2.0.7: 添加 master.shutdown() 調用以優雅關閉 event loop
        - v2.0.8: 添加 0.5s 延遲讓 event loop 清理異步任務（修復 "Task was destroyed" 警告）
        - v2.0.9: 三重修復：warnings 抑制 + 1.5s 延遲 + 增加 join 超時（徹底解決 Windows IocpProactor 警告）
        """
        # ============================================================================
        # v2.0.7: Threading 版本 + 優雅關閉
        # ============================================================================
        if self.thread:
            try:
                # ✅ v2.0.7: 優雅關閉 mitmproxy master
                if self.master:
                    print('[INFO] Shutting down mitmproxy master...')
                    try:
                        # 方案 1: 抑制 asyncio 警告
                        import warnings
                        warnings.filterwarnings('ignore', message='.*Task was destroyed but it is pending.*')

                        # 方案 2: 觸發關閉
                        self.master.shutdown()

                        # 方案 3: 增加延遲讓 event loop 完成清理
                        # Windows 的 IocpProactor 需要更多時間處理 accept 任務取消
                        time.sleep(1.5)
                    except Exception as e:
                        print(f'[WARN] Error during master shutdown: {e}')

                # 等待線程終止
                self.thread.join(timeout=8)  # 增加超時時間以配合延長的等待

                if self.thread.is_alive():
                    print('[WARN] Network monitoring thread still running (will terminate with program)')
                else:
                    print('[INFO] Network monitoring stopped')

            except Exception as e:
                print(f'[WARN] Error while stopping network monitoring: {e}')
            finally:
                self.thread = None
                self.master = None

        # ============================================================================
        # [已註解] v2.0.1: Multiprocessing 版本
        # ============================================================================
        # if self.process:
        #     try:
        #         self.process.terminate()
        #         self.process.join(timeout=5)
        #
        #         if self.process.is_alive():
        #             self.process.kill()
        #
        #         print('[INFO] Network monitoring stopped')
        #     except Exception as e:
        #         print(f'[WARN] Error while stopping network monitoring: {e}')
        #     finally:
        #         self.process = None
        # ============================================================================

    def is_running(self) -> bool:
        """
        檢查 Proxy 是否正在運行

        版本歷史：
        - v2.0.1: 檢查 process.is_alive()
        - v2.0.2: 檢查 thread.is_alive()

        Returns:
            bool: 是否正在運行
        """
        # ============================================================================
        # v2.0.2: Threading 版本（當前使用）
        # ============================================================================
        return self.thread is not None and self.thread.is_alive()

        # ============================================================================
        # [已註解] v2.0.1: Multiprocessing 版本
        # ============================================================================
        # return self.process is not None and self.process.is_alive()
        # ============================================================================

    def __enter__(self):
        """Context manager 進入"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 退出"""
        self.stop()

    def __repr__(self) -> str:
        status = 'running' if self.is_running() else 'stopped'
        return f"ProxyManager(host='{self.host}', port={self.port}, status={status})"
