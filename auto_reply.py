# -*- coding: utf-8 -*-
"""
自动回复核心模块
"""

import time
import argparse
import pyautogui
import pyperclip

from core import config
from core import WeChatWindowCapture
from core import OCRRecognizer, ChatMessageParser
from core import ReplyModeRegistry


class WeChatAutoReply:
    """微信自动回复主类"""
    
    def __init__(self, mode: str = "normal"):
        self.capture = WeChatWindowCapture()
        self.ocr = OCRRecognizer()
        self.parser = ChatMessageParser(self.ocr)
        
        # 加载回复模式
        self.mode = mode
        self.reply_mode = ReplyModeRegistry.get(mode)
        if not self.reply_mode:
            print(f"错误：未找到模式 '{mode}'")
            available = ReplyModeRegistry.list_modes()
            print(f"可用模式: {', '.join(available)}")
            return
        
        print(f"已加载回复模式: {self.reply_mode.description}")
        
        self.running = False
        self.last_message = ""
        self.last_reply = ""
        
        # 安全设置：pyautogui在操作前会有短暂暂停
        pyautogui.PAUSE = 0.5
        pyautogui.FAILSAFE = True  # 移动鼠标到左上角可中止程序
    
    def start(self):
        """启动自动回复"""
        print("=" * 50)
        print("微信自动回复工具")
        print("=" * 50)
        print("提示：将鼠标移动到屏幕左上角可紧急停止程序")
        print("=" * 50)
        
        # 查找微信窗口
        if not self.capture.find_wechat_window():
            print("错误：未找到微信窗口，请确保微信已打开")
            return
        
        window_info = self.capture.get_window_info()
        print(f"找到微信窗口: {window_info['title']}")
        print(f"窗口大小: {window_info['width']} x {window_info['height']}")
        
        # 将微信窗口置于前台
        print("正在将微信窗口置于前台...")
        self.capture.bring_to_front()
        time.sleep(1)
        
        self.running = True
        interval = config.AUTO_REPLY_CONFIG["interval"]
        
        print(f"\n开始监控，检测间隔: {interval}秒")
        print("按 Ctrl+C 停止\n")
        
        try:
            while self.running:
                self._check_and_reply()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n用户中断，停止监控")
            self.running = False
    
    def _check_and_reply(self):
        """检查并回复消息"""
        try:
            # 截取聊天区域
            chat_image = self.capture.capture_chat_area()
            if not chat_image:
                print("警告：无法截取聊天区域")
                return
            
            # 解析消息
            messages = self.parser.parse_messages(chat_image)
            if not messages:
                return
            
            # 获取最新的对方消息
            latest_msg = self.parser.get_latest_other_message(messages)
            if not latest_msg:
                return
            
            msg_text = latest_msg["text"].strip()
            
            # 检查是否是新消息（与上次不同）
            if msg_text == self.last_message:
                return  # 消息未变化，跳过
            
            self.last_message = msg_text
            print(f"\n收到新消息: {msg_text}")
            
            # 生成回复
            reply = self.reply_mode.get_reply(msg_text)
            
            if not reply:
                print("生成回复失败")
                return
            
            print(f"回复: {reply}")
            
            # 避免重复回复相同内容
            if reply == self.last_reply:
                print("避免重复回复，跳过")
                return
            
            print(f"准备回复: {reply}")
            
            # 发送回复
            self._send_reply(reply)
            self.last_reply = reply
            
        except Exception as e:
            print(f"处理消息时出错: {e}")
    
    def _send_reply(self, message: str):
        """
        发送回复消息
        
        Args:
            message: 要发送的消息
        """
        if len(message) > config.AUTO_REPLY_CONFIG["max_reply_length"]:
            print(f"警告：消息过长 ({len(message)} 字符)，将被截断")
            message = message[:config.AUTO_REPLY_CONFIG["max_reply_length"]]
        
        # 获取输入框位置
        input_pos = self.capture.get_input_box_position()
        if not input_pos:
            print("错误：无法获取输入框位置")
            return
        
        # 延迟
        reply_delay = config.AUTO_REPLY_CONFIG["reply_delay"]
        if reply_delay > 0:
            time.sleep(reply_delay)
        
        try:
            # 点击输入框
            pyautogui.click(input_pos[0], input_pos[1])
            time.sleep(0.3)
            
            # 使用剪贴板输入（支持中文）
            pyperclip.copy(message)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)
            
            # 发送消息（Enter键）
            pyautogui.press('enter')
            
            print("消息已发送")
            
        except Exception as e:
            print(f"发送消息失败: {e}")
    
    def stop(self):
        """停止自动回复"""
        self.running = False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="微信自动回复工具")
    parser.add_argument(
        "-m", "--mode",
        type=str,
        default="normal",
        help="回复模式: normal(智能回复), counter(怼人模式)"
    )
    parser.add_argument(
        "-a", "--anger",
        action="store_true",
        help="启用怼人模式 (等同于 --mode counter)"
    )
    args = parser.parse_args()
    
    mode = "counter" if args.anger else args.mode
    
    auto_reply = WeChatAutoReply(mode=mode)
    if auto_reply.reply_mode:
        auto_reply.start()


if __name__ == "__main__":
    main()