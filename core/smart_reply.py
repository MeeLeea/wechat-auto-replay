# -*- coding: utf-8 -*-
"""
智能回复模块 - 集成大语言模型API
支持 OpenAI、智谱AI、通义千问等
"""

import os
import json
from typing import Optional
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """LLM提供商基类"""
    
    @abstractmethod
    def generate_reply(self, message: str, context: list = None) -> Optional[str]:
        """生成回复"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", base_url: str = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or "https://api.openai.com/v1"
        self.system_prompt = "你是一个友好的聊天助手，请用简短、自然、口语化的方式回复消息，回复不超过50个字。"
    
    def generate_reply(self, message: str, context: list = None) -> Optional[str]:
        try:
            import openai
            
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # 添加上下文
            if context:
                for msg in context[-5:]:  # 最多保留5条历史
                    messages.append({"role": msg["role"], "content": msg["content"]})
            
            messages.append({"role": "user", "content": message})
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            return None


class ZhipuProvider(LLMProvider):
    """智谱AI API (GLM-4)"""
    
    def __init__(self, api_key: str, model: str = "glm-4-flash", base_url: str = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.system_prompt = "你是一个友好的聊天助手，请用简短自然、口语化的方式回复消息，回复不超过50个字。"
    
    def generate_reply(self, message: str, context: list = None) -> Optional[str]:
        try:
            import zhipuai
            
            client = zhipuai.ZhipuAI(api_key=self.api_key)
            
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if context:
                for msg in context[-5:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
            
            messages.append({"role": "user", "content": message})
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"智谱AI API调用失败: {e}")
            return None


class QwenProvider(LLMProvider):
    """通义千问 API"""
    
    def __init__(self, api_key: str, model: str = "qwen-turbo"):
        self.api_key = api_key
        self.model = model
        self.system_prompt = "你是一个友好的聊天助手，请用简短、自然、口语化的方式回复消息，回复不超过50个字。"
    
    def generate_reply(self, message: str, context: list = None) -> Optional[str]:
        try:
            import dashscope
            from dashscope import Generation
            
            dashscope.api_key = self.api_key
            
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if context:
                for msg in context[-5:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
            
            messages.append({"role": "user", "content": message})
            
            response = Generation.call(
                model=self.model,
                messages=messages,
                max_tokens=100,
                temperature=0.7
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content.strip()
            else:
                print(f"通义千问API错误: {response.code} - {response.message}")
                return None
        
        except Exception as e:
            print(f"通义千问API调用失败: {e}")
            return None


class DeepSeekProvider(LLMProvider):
    """DeepSeek API / 硅基流动"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat", base_url: str = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url if base_url else "https://api.deepseek.com/v1"
        self.system_prompt = "你是一个友好的聊天助手，请用简短自然、口语化的方式回复消息，回复不超过50个字。"
    
    def generate_reply(self, message: str, context: list = None) -> Optional[str]:
        try:
            import openai
            
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if context:
                for msg in context[-5:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
            
            messages.append({"role": "user", "content": message})
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
            return None


class SmartReplyEngine:
    """智能回复引擎"""
    
    def __init__(self, config_file: str = "llm_config.json"):
        self.provider: Optional[LLMProvider] = None
        self.context: list = []  # 对话上下文
        self.max_context = 10    # 最大上下文数量
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        config_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), self.config_file)
        if not os.path.exists(config_file_path):
            config_file_path = self.config_file
            if not os.path.exists(config_file_path):
                print(f"配置文件 {self.config_file} 不存在，请先配置")
                return
        
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            provider_type = config.get("provider", "").lower()
            api_key = config.get("api_key", "")
            model = config.get("model", "")
            base_url = config.get("base_url", "")
            
            if not api_key:
                print("未配置API Key")
                return
            
            if provider_type == "openai":
                self.provider = OpenAIProvider(api_key, model or "gpt-3.5-turbo", base_url)
            elif provider_type == "zhipu":
                self.provider = ZhipuProvider(api_key, model or "glm-4-flash", base_url)
            elif provider_type == "qwen":
                self.provider = QwenProvider(api_key, model or "qwen-turbo")
            elif provider_type == "deepseek":
                self.provider = DeepSeekProvider(api_key, model or "deepseek-chat", base_url)
            else:
                print(f"不支持的提供商: {provider_type}")
                return
            
            print(f"已加载 {provider_type} 智能回复引擎")
        
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def generate_reply(self, message: str) -> Optional[str]:
        """生成智能回复"""
        if not self.provider:
            return None
        
        reply = self.provider.generate_reply(message, self.context)
        
        if reply:
            # 更新上下文
            self.context.append({"role": "user", "content": message})
            self.context.append({"role": "assistant", "content": reply})
            
            # 限制上下文长度
            if len(self.context) > self.max_context * 2:
                self.context = self.context[-self.max_context * 2:]
        
        return reply
    
    def clear_context(self):
        """清空对话上下文"""
        self.context = []


# 使用示例
if __name__ == "__main__":
    # 测试智能回复
    engine = SmartReplyEngine()
    
    if engine.provider:
        test_messages = [
            "今天天气怎么样？",
            "我最近压力好大，不知道该怎么办",
            "有什么好电影推荐吗？"
        ]
        
        for msg in test_messages:
            print(f"\n用户: {msg}")
            reply = engine.generate_reply(msg)
            print(f"助手: {reply}")
    else:
        print("请先配置 llm_config.json")