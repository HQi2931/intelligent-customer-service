"""输入校验护栏。"""

MAX_QUERY_LENGTH = 2000
FORBIDDEN_PATTERNS = [
    "<script",
    "DROP TABLE",
]


class InputValidator:
    """用户输入校验器。"""

    @staticmethod
    def validate_query(query: str) -> tuple[bool, str | None]:
        """
        验证用户查询。

        返回:
        (is_valid, error_message)
        """
        if not query or not query.strip():
            return False, "查询内容不能为空"

        if len(query) > MAX_QUERY_LENGTH:
            return False, f"查询内容超过最大长度 {MAX_QUERY_LENGTH}"

        lower = query.lower()
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.lower() in lower:
                return False, "查询包含不允许的内容"

        return True, None
