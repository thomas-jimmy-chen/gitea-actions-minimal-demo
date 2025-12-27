# -*- coding: utf-8 -*-
"""
Scroll Utilities for EEBot.

Provides multi-strategy scrolling functions for handling various page layouts
including modals, locked body elements, and lazy-loaded content.

Usage:
    from src.utils.scroll_utils import scroll_to_bottom_multi_strategy

    scroll_count = scroll_to_bottom_multi_strategy(
        driver,
        max_scrolls=10,
        wait_time=2.0,
        exam_page=True
    )
"""

import time
import logging
from typing import Any, Dict, Optional, List

logger = logging.getLogger(__name__)


# Modal selectors for various UI frameworks
MODAL_SELECTORS: List[str] = [
    # 考試頁面 Modal（基於 Burp Suite 分析）
    '.reveal-modal:not([style*="display: none"])',
    '.popup-area:not([style*="display: none"])',
    # 通用 Modal 選擇器
    '.modal', '.modal-dialog', '.modal-content', '.modal-body',
    '.dialog', '.popup', '.overlay-content',
    '[role="dialog"]', '[role="alertdialog"]',
    '.ant-modal', '.el-dialog', '.MuiDialog-root',
    '.v-dialog', '.chakra-modal__content'
]

# Scroll container selectors
SCROLL_CONTAINER_SELECTORS: List[str] = [
    # 考試頁面專用（基於 Burp Suite 分析）
    '.fullscreen-right', '.activity-content-box', '.exam-subjects',
    '.submission-list.exam-area', '.sync-scroll',
    # 通用選擇器
    '.main-container', '.content-wrapper', '.scroll-container',
    '.app-content', '.page-content', '[class*="scroll"]',
    'main', '#main', '#content', '.container'
]


def _get_scroll_environment(driver: Any) -> Dict[str, Any]:
    """
    Detect the scroll environment of the current page.

    This function analyzes the page to determine:
    - If the body is locked (overflow: hidden)
    - If there's an active modal with scrollable content
    - What scroll container should be used

    Args:
        driver: Selenium WebDriver instance

    Returns:
        Dictionary containing scroll environment info
    """
    modal_selectors_js = ', '.join([f"'{s}'" for s in MODAL_SELECTORS])
    container_selectors_js = ', '.join([f"'{s}'" for s in SCROLL_CONTAINER_SELECTORS])

    js_code = f"""
        var bodyH = document.body.scrollHeight;
        var docH = document.documentElement.scrollHeight;
        var viewH = window.innerHeight;

        // 策略 1: 檢測 body 是否被鎖住
        var bodyOverflow = getComputedStyle(document.body).overflow;
        var htmlOverflow = getComputedStyle(document.documentElement).overflow;
        var isBodyLocked = (bodyOverflow === 'hidden' || htmlOverflow === 'hidden');

        // 策略 2: 檢測 Modal/Dialog（雙滾動條問題）
        var modalSelectors = [{modal_selectors_js}];
        var activeModal = null;
        var modalScrollContainer = null;
        for (var i = 0; i < modalSelectors.length; i++) {{
            var modal = document.querySelector(modalSelectors[i]);
            if (modal && modal.offsetParent !== null) {{
                activeModal = modalSelectors[i];
                // 找 Modal 內可滾動的容器
                var innerContainers = modal.querySelectorAll('*');
                for (var j = 0; j < innerContainers.length; j++) {{
                    var inner = innerContainers[j];
                    if (inner.scrollHeight > inner.clientHeight + 10) {{
                        var style = getComputedStyle(inner);
                        if (style.overflowY === 'auto' || style.overflowY === 'scroll') {{
                            modalScrollContainer = inner;
                            break;
                        }}
                    }}
                }}
                break;
            }}
        }}

        // 策略 3: 尋找一般滾動容器（含考試頁面專用選擇器）
        var containers = [{container_selectors_js}];
        var scrollContainer = null;
        if (!activeModal) {{
            for (var i = 0; i < containers.length; i++) {{
                var el = document.querySelector(containers[i]);
                if (el && el.scrollHeight > el.clientHeight) {{
                    scrollContainer = containers[i];
                    break;
                }}
            }}
        }}

        return {{
            bodyHeight: bodyH,
            docHeight: docH,
            viewHeight: viewH,
            isBodyLocked: isBodyLocked,
            bodyOverflow: bodyOverflow,
            activeModal: activeModal,
            hasModalScroll: modalScrollContainer !== null,
            scrollContainer: scrollContainer
        }};
    """

    try:
        return driver.execute_script(js_code)
    except Exception as e:
        logger.warning("Failed to get scroll environment: %s", e)
        return {
            'bodyHeight': 0,
            'docHeight': 0,
            'viewHeight': 0,
            'isBodyLocked': False,
            'activeModal': None,
            'hasModalScroll': False,
            'scrollContainer': None
        }


def _scroll_modal(driver: Any, modal_selector: str) -> None:
    """Scroll inside a modal dialog."""
    driver.execute_script(f"""
        var modal = document.querySelector('{modal_selector}');
        if (modal) {{
            var scrollables = modal.querySelectorAll('*');
            for (var i = 0; i < scrollables.length; i++) {{
                var el = scrollables[i];
                if (el.scrollHeight > el.clientHeight + 10) {{
                    var style = getComputedStyle(el);
                    if (style.overflowY === 'auto' || style.overflowY === 'scroll') {{
                        el.scrollTop = el.scrollHeight;
                        break;
                    }}
                }}
            }}
        }}
    """)


def _scroll_container(driver: Any, container_selector: str) -> None:
    """Scroll a specific container element."""
    driver.execute_script(f"""
        var el = document.querySelector('{container_selector}');
        if (el) el.scrollTop = el.scrollHeight;
    """)


def _scroll_window(driver: Any) -> None:
    """Scroll the main window."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def _scroll_by_viewport(driver: Any) -> None:
    """Scroll by viewport height (incremental scroll)."""
    viewport_height = driver.execute_script("return window.innerHeight")
    driver.execute_script(f"window.scrollBy(0, {viewport_height});")


def _scroll_into_view_last(driver: Any) -> None:
    """Scroll to the last element in the body."""
    driver.execute_script("""
        var lastElement = document.body.lastElementChild;
        if (lastElement) {
            lastElement.scrollIntoView({behavior: 'instant', block: 'end'});
        }
    """)


def _get_page_height(driver: Any) -> int:
    """Get the maximum page height."""
    return driver.execute_script("""
        return Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight
        );
    """)


def scroll_to_bottom_multi_strategy(
    driver: Any,
    max_scrolls: int = 10,
    wait_time: float = 2.0,
    exam_page: bool = False
) -> int:
    """
    Scroll to page bottom using multiple strategies for different page types.

    This function handles various page layouts including:
    - Standard pages with normal scrolling
    - Pages with body overflow:hidden (locked body)
    - Modal dialogs with internal scrolling
    - Lazy-loaded content that needs time to render

    Strategies used:
    1. Detect if body is locked (overflow: hidden)
    2. Detect active modals with scrollable content
    3. Find scroll containers (exam pages, general containers)
    4. scrollTo - direct window scroll
    5. scrollBy - incremental scroll for lazy loading
    6. scrollIntoView - element-based scroll
    7. Height stabilization check

    Args:
        driver: Selenium WebDriver instance
        max_scrolls: Maximum number of scroll attempts (default: 10)
        wait_time: Base wait time between scrolls in seconds (default: 2.0)
        exam_page: Whether this is an exam page (enables exam-specific selectors)

    Returns:
        Number of scroll iterations performed

    Example:
        # Basic usage
        scroll_count = scroll_to_bottom_multi_strategy(driver)

        # For exam pages with more patience
        scroll_count = scroll_to_bottom_multi_strategy(
            driver,
            max_scrolls=15,
            wait_time=2.5,
            exam_page=True
        )
    """
    scroll_count = 0

    # Get scroll environment info
    scroll_info = _get_scroll_environment(driver)

    body_h = scroll_info.get('bodyHeight', 0)
    doc_h = scroll_info.get('docHeight', 0)
    is_body_locked = scroll_info.get('isBodyLocked', False)
    active_modal = scroll_info.get('activeModal')
    has_modal_scroll = scroll_info.get('hasModalScroll', False)
    container = scroll_info.get('scrollContainer')

    # Log environment detection for debugging
    logger.debug(
        "Scroll env: body_locked=%s, modal=%s, container=%s",
        is_body_locked, active_modal, container
    )

    # Determine initial height
    last_height = max(body_h, doc_h)

    for i in range(max_scrolls):
        # Strategy 4: Choose scroll method based on environment
        if active_modal and has_modal_scroll:
            # Modal with internal scroll container
            _scroll_modal(driver, active_modal)
        elif is_body_locked and container:
            # Body is locked but has alternative container
            _scroll_container(driver, container)
        elif container:
            # Has specific scroll container
            _scroll_container(driver, container)
            # Also try window scroll as backup (dual strategy)
            if not is_body_locked:
                _scroll_window(driver)
        else:
            # Default: scroll window
            _scroll_window(driver)

        scroll_count += 1
        time.sleep(wait_time * 0.4)

        # Strategy 5: Incremental scroll (triggers lazy load)
        if not is_body_locked:
            _scroll_by_viewport(driver)
        time.sleep(wait_time * 0.3)

        # Strategy 6: Scroll last element into view
        _scroll_into_view_last(driver)
        time.sleep(wait_time * 0.3)

        # Strategy 7: Check height stabilization
        new_height = _get_page_height(driver)

        if new_height == last_height:
            # Height unchanged, confirm once more
            time.sleep(0.5)
            confirm_height = _get_page_height(driver)
            if confirm_height == new_height:
                # Two consecutive same heights = loading complete
                logger.debug("Scroll complete after %d iterations", scroll_count)
                break
            last_height = confirm_height
        else:
            last_height = new_height

    # Final confirmation: execute all strategies once more
    if not is_body_locked:
        _scroll_window(driver)
        time.sleep(0.3)
        driver.execute_script("window.scrollBy(0, 100);")
        time.sleep(0.3)
    _scroll_into_view_last(driver)
    time.sleep(0.4)

    return scroll_count


def scroll_to_element(
    driver: Any,
    element: Any,
    block: str = 'center',
    behavior: str = 'smooth'
) -> None:
    """
    Scroll an element into view.

    Args:
        driver: Selenium WebDriver instance
        element: WebElement to scroll into view
        block: Vertical alignment ('start', 'center', 'end')
        behavior: Scroll behavior ('auto', 'smooth', 'instant')
    """
    driver.execute_script(
        f"arguments[0].scrollIntoView({{behavior: '{behavior}', block: '{block}'}});",
        element
    )


def scroll_to_top(driver: Any) -> None:
    """Scroll to the top of the page."""
    driver.execute_script("window.scrollTo(0, 0);")


def get_scroll_position(driver: Any) -> Dict[str, int]:
    """
    Get current scroll position.

    Returns:
        Dictionary with 'x' and 'y' scroll positions
    """
    return driver.execute_script("""
        return {
            x: window.pageXOffset || document.documentElement.scrollLeft,
            y: window.pageYOffset || document.documentElement.scrollTop
        };
    """)
