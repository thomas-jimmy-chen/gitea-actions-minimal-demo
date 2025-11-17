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
from datetime import datetime
from multiprocessing import Process
from mitmproxy.options import Options as MitmOptions
from mitmproxy.tools.dump import DumpMaster
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
        self.process = None

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
        """配置並執行 MitmProxy"""
        opts = MitmOptions(listen_host=self.host, listen_port=self.port)
        master = DumpMaster(opts)

        # 加入攔截器
        for interceptor in self.interceptors:
            master.addons.add(interceptor)

        try:
            await master.run()
        except KeyboardInterrupt:
            master.shutdown()

    def _run(self):
        """在獨立 Process 中執行 MitmProxy"""
        if self.silent:
            self._silence_stdout()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._config())
        loop.close()

    def start(self):
        """啟動 MitmProxy"""
        if not self.silent:
            print(f"[INFO] Starting network monitoring on {self.host}:{self.port}")
        elif self.log_save:
            print("[INFO] Starting network monitoring in silent mode with logging...")
        else:
            print("[INFO] Starting network monitoring in silent mode...")

        self.process = Process(target=self._run)
        self.process.start()
        time.sleep(1)  # 等待 Proxy 啟動

        print('[INFO] Network monitoring started successfully')

    def stop(self):
        """停止 MitmProxy"""
        if self.process:
            try:
                self.process.terminate()
                self.process.join(timeout=5)

                if self.process.is_alive():
                    self.process.kill()

                print('[INFO] Network monitoring stopped')
            except Exception as e:
                print(f'[WARN] Error while stopping network monitoring: {e}')
            finally:
                self.process = None

    def is_running(self) -> bool:
        """
        檢查 Proxy 是否正在運行

        Returns:
            bool: 是否正在運行
        """
        return self.process is not None and self.process.is_alive()

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
