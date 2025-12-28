# -*- coding: utf-8 -*-
"""
EEBot 統一錯誤處理模組

提供統一的錯誤處理機制，包含：
- 錯誤 Log 檔案記錄
- 系統截圖（如果 driver 可用）
- 格式化錯誤訊息輸出

使用方式:
    from src.utils.error_handler import handle_error
    from src.exceptions import EEBotError

    try:
        orchestrator.execute()
    except EEBotError as e:
        handle_error(e, driver=driver, context="執行 h2", is_known=True)
    except Exception as e:
        handle_error(e, driver=driver, context="執行 h2", is_known=False)
"""

import traceback
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def handle_error(
    e: Exception,
    driver: Any = None,
    context: str = "",
    is_known: bool = False
) -> Dict[str, Optional[str]]:
    """
    統一處理所有錯誤（已知 + 未預期）

    Args:
        e: 異常對象
        driver: WebDriver 實例（可選，用於截圖）
        context: 錯誤發生的上下文描述
        is_known: 是否為已知的專案異常（EEBotError 子類）

    Returns:
        dict: 包含 log_path, screenshot_path, timestamp 的字典

    Example:
        try:
            # 業務邏輯
            ...
        except EEBotError as e:
            handle_error(e, driver=driver, context="執行任務", is_known=True)
        except Exception as e:
            handle_error(e, driver=driver, context="執行任務", is_known=False)
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    error_dir = Path('reports/errors')
    error_dir.mkdir(parents=True, exist_ok=True)

    error_type = "known" if is_known else "unexpected"
    error_label = "錯誤" if is_known else "未預期錯誤"

    # 1. 錯誤 Log 檔
    log_path = error_dir / f'error_{error_type}_{timestamp}.log'
    try:
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f'{"="*60}\n')
            f.write(f'EEBot 錯誤報告\n')
            f.write(f'{"="*60}\n\n')
            f.write(f'時間: {datetime.now().isoformat()}\n')
            f.write(f'類型: {"已知錯誤" if is_known else "未預期錯誤"}\n')
            f.write(f'上下文: {context}\n')
            f.write(f'錯誤類型: {e.__class__.__name__}\n')
            f.write(f'錯誤訊息: {e}\n')
            f.write(f'\n{"="*60}\n')
            f.write(f'完整 Traceback:\n')
            f.write(f'{"="*60}\n\n')
            f.write(traceback.format_exc())
            f.write(f'\n{"="*60}\n')
            f.write(f'請聯繫專案工程師處理\n')
            f.write(f'{"="*60}\n')
    except Exception as log_error:
        logger.warning("無法寫入錯誤 Log: %s", log_error)
        log_path = None

    # 2. 系統截圖（如果 driver 可用）
    screenshot_path = None
    if driver:
        try:
            screenshot_path = error_dir / f'error_{error_type}_{timestamp}.png'
            driver.save_screenshot(str(screenshot_path))
            logger.info("錯誤截圖已保存: %s", screenshot_path)
        except Exception as screenshot_error:
            logger.warning("無法保存錯誤截圖: %s", screenshot_error)
            screenshot_path = None

    # 3. 顯示訊息
    print(f'\n{"="*60}')
    print(f'[{error_label}] {e.__class__.__name__}')
    print(f'{"="*60}')
    print(f'訊息: {e}')
    if context:
        print(f'上下文: {context}')
    print(f'-' * 60)
    if log_path:
        print(f'錯誤 Log: {log_path}')
    if screenshot_path and screenshot_path.exists():
        print(f'錯誤截圖: {screenshot_path}')
    print(f'-' * 60)
    print('請聯繫專案工程師處理')
    print(f'{"="*60}\n')

    # 4. 記錄到 logger
    if is_known:
        logger.error("[%s] %s: %s", context, e.__class__.__name__, e)
    else:
        logger.exception("[%s] 未預期錯誤", context)

    return {
        'log_path': str(log_path) if log_path else None,
        'screenshot_path': str(screenshot_path) if screenshot_path else None,
        'timestamp': timestamp,
        'error_type': error_type,
        'error_class': e.__class__.__name__,
        'error_message': str(e)
    }


def create_error_context(
    phase: str = "",
    item_name: str = "",
    item_type: str = ""
) -> str:
    """
    創建錯誤上下文描述

    Args:
        phase: 執行階段
        item_name: 項目名稱
        item_type: 項目類型（course/exam）

    Returns:
        str: 格式化的上下文描述
    """
    parts = []
    if phase:
        parts.append(f"階段: {phase}")
    if item_type:
        parts.append(f"類型: {item_type}")
    if item_name:
        parts.append(f"項目: {item_name}")

    return " | ".join(parts) if parts else "未指定上下文"


# =============================================================================
# 導出
# =============================================================================

__all__ = [
    'handle_error',
    'create_error_context',
]
