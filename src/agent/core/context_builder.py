"""上下文构建器 — 智能窗口 + 自动摘要。"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from model.factory import chat_model
from utils.logger_handler import logger


SUMMARY_PROMPT = """请用30字以内总结以下对话的核心内容：

{conversation}

总结:"""


class ContextBuilder:
    """构建注入 Agent 的上下文窗口。

    策略:
    - 最近 8 条完整保留
    - 更早的消息压缩为摘要
    - 超过 15 条触发摘要
    """

    MAX_RECENT = 8
    SUMMARY_TRIGGER = 15

    def build(self, messages: list[dict]) -> list[dict]:
        if len(messages) <= self.SUMMARY_TRIGGER:
            return messages[-self.MAX_RECENT:]

        # 早期消息 → 摘要
        early = messages[:-self.MAX_RECENT]
        summary = self._generate_summary(early)

        result = [{
            "role": "system",
            "content": f"[对话历史摘要] {summary}",
        }]
        result.extend(messages[-self.MAX_RECENT:])
        return result

    def _generate_summary(self, messages: list[dict]) -> str:
        """调用 LLM 生成摘要，失败时回退到关键词提取。"""
        conversation = "\n".join(
            f"{'用户' if m['role'] == 'user' else '助手'}: {m['content'][:100]}"
            for m in messages
        )
        try:
            prompt = SUMMARY_PROMPT.format(conversation=conversation)
            result = chat_model.invoke(prompt)
            return result.content.strip()[:100]
        except Exception as e:
            logger.warning(f"[ContextBuilder] 摘要生成失败: {e}")
            # 回退：取用户消息的关键词
            topics = [
                m["content"][:30]
                for m in messages
                if m["role"] == "user" and len(m["content"]) < 30
            ]
            return "；".join(topics[:5]) if topics else "历史对话"