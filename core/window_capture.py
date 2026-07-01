# -*- coding: utf-8 -*-
"""
窗口定位和截图模块
"""

import pyautogui
import win32gui
import win32con
import win32process
from PIL import Image
from typing import Optional, Tuple
from . import config


class WeChatWindowCapture:
    """微信窗口捕获类"""
    
    def __init__(self):
        self.hwnd: Optional[int] = None
        self.window_rect: Optional[Tuple[int, int, int, int]] = None
        
    def find_wechat_window(self) -> bool:
        """查找微信窗口"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if config.WECHAT_WINDOW_TITLE in title:
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        
        if windows:
            self.hwnd = windows[0]
            self._update_window_rect()
            return True
        return False
    
    def _update_window_rect(self):
        """更新窗口位置信息"""
        if self.hwnd:
            self.window_rect = win32gui.GetWindowRect(self.hwnd)
    
    def bring_to_front(self):
        """将微信窗口置于前台"""
        if self.hwnd:
            try:
                win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(self.hwnd)
            except Exception as e:
                print(f"无法将窗口置于前台: {e}")
    
    def capture_window(self) -> Optional[Image.Image]:
        """截取微信窗口"""
        if not self.hwnd:
            if not self.find_wechat_window():
                print("未找到微信窗口")
                return None
        
        self._update_window_rect()
        
        if not self.window_rect:
            return None
        
        left, top, right, bottom = self.window_rect
        width = right - left
        height = bottom - top
        
        # 截取窗口区域
        try:
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            return screenshot
        except Exception as e:
            print(f"截图失败: {e}")
            return None
    
    def capture_chat_area(self) -> Optional[Image.Image]:
        """截取聊天消息区域"""
        full_screenshot = self.capture_window()
        if not full_screenshot or not self.window_rect:
            return None
        
        left, top, right, bottom = self.window_rect
        width = right - left
        height = bottom - top
        
        # 计算聊天区域
        chat_left = config.CHAT_AREA["left_offset"]
        chat_top = config.CHAT_AREA["top_offset"]
        chat_right = width - config.CHAT_AREA["right_offset"]
        chat_bottom = height - config.CHAT_AREA["bottom_offset"]
        
        # 裁剪聊天区域
        try:
            chat_area = full_screenshot.crop((chat_left, chat_top, chat_right, chat_bottom))
            return chat_area
        except Exception as e:
            print(f"裁剪聊天区域失败: {e}")
            return None
    
    def get_input_box_position(self) -> Optional[Tuple[int, int]]:
        """获取输入框位置（屏幕坐标）"""
        if not self.window_rect:
            return None
        
        left, top, right, bottom = self.window_rect
        width = right - left
        height = bottom - top
        
        # 计算输入框中心位置
        input_x = left + config.INPUT_BOX["left_offset"] + int(width * config.INPUT_BOX["width_ratio"] / 2)
        input_y = bottom - config.INPUT_BOX["bottom_offset"]
        
        return (input_x, input_y)
    
    def get_window_info(self) -> dict:
        """获取窗口信息"""
        if not self.hwnd:
            return {}
        
        self._update_window_rect()
        
        if not self.window_rect:
            return {}
        
        left, top, right, bottom = self.window_rect
        return {
            "hwnd": self.hwnd,
            "title": win32gui.GetWindowText(self.hwnd),
            "rect": self.window_rect,
            "width": right - left,
            "height": bottom - top,
        }


if __name__ == "__main__":
    # 测试代码
    capture = WeChatWindowCapture()
    if capture.find_wechat_window():
        info = capture.get_window_info()
        print(f"找到微信窗口: {info}")
        
        # 测试截图
        screenshot = capture.capture_window()
        if screenshot:
            screenshot.save("wechat_screenshot.png")
            print("截图已保存为 wechat_screenshot.png")
        
        # 测试聊天区域截图
        chat_area = capture.capture_chat_area()
        if chat_area:
            chat_area.save("chat_area.png")
            print("聊天区域截图已保存为 chat_area.png")
    else:
        print("未找到微信窗口，请确保微信已打开")