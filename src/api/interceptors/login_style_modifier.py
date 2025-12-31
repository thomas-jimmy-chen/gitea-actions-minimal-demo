"""
登入頁面樣式修改攔截器

功能：
1. 修改 username/password/captcha 欄位的背景色為淺紅色
2. Focus 時外框變成亮紅色
3. 在 username 上方加入 OCR 提示文字
4. 在驗證碼下方加入 OCR 提示文字
5. 姓名替換: 陳偉鳴 → 陳〇〇 (使用 U+3007 國字零)

使用方式:
    mitmdump -s src/api/interceptors/login_style_modifier.py
"""
import re

from mitmproxy import http


class LoginStyleModifier:
    """修改登入頁面樣式 + 姓名替換"""

    @staticmethod
    def _mask_name(name: str) -> str:
        """遮蔽姓名：保留第一個字，其餘用〇替換

        例如：陳偉鳴 → 陳〇〇、李四 → 李〇、司馬相如 → 司〇〇〇
        """
        if not name or len(name) < 1:
            return name
        first_char = name[0]
        masked = first_char + '〇' * (len(name) - 1)  # U+3007 國字零
        return masked

    def __init__(self):
        # OCR 提示文字
        self.ocr_message = "***驗證碼自動 OCR 中***"

        # 姓名替換設定 (從 Burp Suite 分析得到)
        # 規則：保留第一個字，其餘用〇替換
        self.original_name = "陳偉鳴"
        self.replacement_name = self._mask_name(self.original_name)

        # 自定義 CSS 樣式
        self.custom_css = """
<style id="eebot-custom-style">
/* 輸入欄位 - 淺紅色背景 */
#user_name,
#password,
input[name="captcha_code"] {
    background-color: #ffebee !important;  /* 淺紅色背景 */
    border: 2px solid #e57373 !important;  /* 紅色邊框 */
    transition: all 0.3s ease !important;
}

/* Focus 時 - 亮紅色外框 */
#user_name:focus,
#password:focus,
input[name="captcha_code"]:focus {
    background-color: #ffcdd2 !important;  /* 稍深的淺紅色 */
    border-color: #f44336 !important;      /* 亮紅色邊框 */
    box-shadow: 0 0 8px rgba(244, 67, 54, 0.6) !important;  /* 紅色光暈 */
    outline: none !important;
}

/* OCR 提示文字樣式 */
.eebot-ocr-notice {
    text-align: center;
    color: #d32f2f;
    font-weight: bold;
    font-size: 14px;
    padding: 8px;
    margin: 5px 0;
    background: linear-gradient(90deg, transparent, #ffcdd2, transparent);
    animation: eebot-blink 1.5s ease-in-out infinite;
}

@keyframes eebot-blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* 驗證碼區塊下方的提示 */
.captcha-verification {
    position: relative;
}
</style>
"""

        # username 上方的提示 HTML
        self.username_notice = f'''
<div class="eebot-ocr-notice" id="eebot-notice-top">{self.ocr_message}</div>
'''

        # 驗證碼下方的提示 HTML
        self.captcha_notice = f'''
<div class="eebot-ocr-notice" id="eebot-notice-bottom">{self.ocr_message}</div>
'''

    def response(self, flow: http.HTTPFlow):
        """攔截並修改響應"""
        # 只處理 elearn.post.gov.tw
        if "elearn.post.gov.tw" not in flow.request.host:
            return

        # 只處理 HTML 響應
        content_type = flow.response.headers.get("content-type", "")
        if "text/html" not in content_type:
            return

        try:
            body = flow.response.get_text()
        except Exception:
            return

        modified = False

        # ============================================================
        # 1. 姓名替換 (所有 HTML 頁面)
        # ============================================================
        if self.original_name in body:
            body = body.replace(self.original_name, self.replacement_name)
            modified = True
            print(f"[LoginStyleModifier] 姓名已替換: {flow.request.path}")

        # ============================================================
        # 2. 登入頁面專用樣式 (只在 /login 頁面)
        # ============================================================
        if "/login" in flow.request.path:
            # 2.1 在 </head> 前注入自定義 CSS
            if "</head>" in body:
                body = body.replace("</head>", f"{self.custom_css}</head>")
                modified = True

            # 2.2 在 username 欄位的容器前加入 OCR 提示
            pattern = r'(<div class="login-tip"[^>]*>.*?</div>)\s*\n\s*(<div class="wrapper-input-tag-with-icon">)'
            match = re.search(pattern, body, re.DOTALL)
            if match:
                body = re.sub(
                    pattern,
                    rf'\1\n{self.username_notice}\2',
                    body,
                    count=1,
                    flags=re.DOTALL
                )
                modified = True

            # 2.3 在驗證碼區塊後加入 OCR 提示
            captcha_pattern = r'(</div>\s*\n\s*</div>\s*\n)\s*(<div class="find-password">)'
            match2 = re.search(captcha_pattern, body)
            if match2:
                body = re.sub(
                    captcha_pattern,
                    rf'\1{self.captcha_notice}\n    \2',
                    body,
                    count=1
                )
                modified = True

            if modified:
                print(f"[LoginStyleModifier] 登入頁面樣式已修改: {flow.request.path}")

        # 更新響應
        if modified:
            flow.response.set_text(body)


addons = [LoginStyleModifier()]
