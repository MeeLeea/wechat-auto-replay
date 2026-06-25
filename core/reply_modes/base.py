# -*- coding: utf-8 -*-
"""
回复模式基类
"""

from abc import ABC, abstractmethod
from typing import Optional, List
import random


class ReplyMode(ABC):
    """回复模式基类"""
    
    name: str = "base"
    description: str = "基础回复模式"
    
    def __init__(self):
        self.replies: List[str] = []
        self._load_replies()
    
    @abstractmethod
    def _load_replies(self):
        """加载回复语句"""
        pass
    
    def get_reply(self, message: str = "") -> Optional[str]:
        """
        获取回复
        
        Args:
            message: 收到的消息（可选，用于上下文相关回复）
            
        Returns:
            回复内容
        """
        if not self.replies:
            return None
        return random.choice(self.replies)
    
    def get_random_reply(self) -> Optional[str]:
        """随机获取一条回复"""
        if not self.replies:
            return None
        return random.choice(self.replies)


class ReplyModeRegistry:
    """回复模式注册表"""
    
    _modes = {}
    
    @classmethod
    def register(cls, name: str, mode_class):
        """注册模式"""
        cls._modes[name] = mode_class
    
    @classmethod
    def get(cls, name: str) -> Optional[ReplyMode]:
        """获取模式实例"""
        mode_class = cls._modes.get(name)
        if mode_class:
            return mode_class()
        return None
    
    @classmethod
    def list_modes(cls):
        """列出所有可用模式"""
        return list(cls._modes.keys())
    
    @classmethod
    def get_description(cls, name: str) -> str:
        """获取模式描述"""
        mode_class = cls._modes.get(name)
        if mode_class:
            return mode_class.description
        return "未知模式"
