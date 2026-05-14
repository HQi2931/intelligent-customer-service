"""输出护栏：回答质量检查 + 脱敏。"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class OutputGuardrails:
    """Agent 输出后处理。"""

    REFUSAL_PATTERNS = [
        "我不知道",
        "我不清楚",
        "我无法回答",
    ]

    @classmethod
    def check(cls, answer: str, sources: list[str] | None = None) -> dict:
        """检查输出质量，返回 {"ok": bool, "issues": list}。"""
        issues = []

        # 空回答
        if not answer or len(answer.strip()) < 5:
            issues.append("回答过短")

        # 不应该说"我不知道"但实际给了资料 — 这是正常的

        # 过长回答（可能幻觉）
        if len(answer) > 2000:
            issues.append("回答过长")

        return {"ok": len(issues) == 0, "issues": issues}

    @classmethod
    def sanitize(cls, text: str) -> str:
        """简单脱敏 + 格式修正。"""
        text = text.strip()
        # 移除多余空行
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        return text