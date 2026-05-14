"""内容安全过滤。"""

import re

BLOCKED_PATTERNS = [
    re.compile(r"<\s*script", re.IGNORECASE),
    re.compile(r"DROP\s+TABLE", re.IGNORECASE),
    re.compile(r"DELETE\s+FROM", re.IGNORECASE),
    re.compile(r"UNION\s+SELECT", re.IGNORECASE),
    re.compile(r"1\s*=\s*1", re.IGNORECASE),
]

SENSITIVE_CATEGORIES: dict[str, list[str]] = {
    "违规": [],
}


class ContentFilter:
    """内容过滤：注入攻击检测 + 敏感词过滤。"""

    @classmethod
    def filter_input(cls, text: str) -> tuple[bool, str | None]:
        """过滤用户输入。返回 (通过, 拒绝原因)。"""
        for pattern in BLOCKED_PATTERNS:
            if pattern.search(text):
                return False, "输入包含不安全内容"

        for category, words in SENSITIVE_CATEGORIES.items():
            for word in words:
                if word in text:
                    return False, f"输入包含{category}内容"

        return True, None

    @classmethod
    def filter_output(cls, text: str) -> str:
        """过滤模型输出（脱敏）。"""
        for words in SENSITIVE_CATEGORIES.values():
            for word in words:
                text = text.replace(word, "***")
        return text