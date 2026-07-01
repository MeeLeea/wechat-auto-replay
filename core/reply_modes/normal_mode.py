# -*- coding: utf-8 -*-
"""
正常智能回复模式
"""

from .base import ReplyMode, ReplyModeRegistry
from ..smart_reply import SmartReplyEngine


class NormalMode(ReplyMode):
    """正常智能回复模式 - 使用大模型"""
    
    name = "normal"
    description = "正常智能回复模式：使用AI生成自然友好的回复"
    
    def _load_replies(self):
        self.replies = []
        self.engine = None
        try:
            self.engine = SmartReplyEngine()
        except Exception:
            pass
    
    def get_reply(self, message: str = "") -> str:
        """使用AI生成回复"""
        if self.engine and self.engine.provider:
            reply = self.engine.generate_reply(message)
            if reply:
                return reply
        return "收到~"


ReplyModeRegistry.register("normal", NormalMode)
