# -*- coding: utf-8 -*-
"""
配置文件 - 微信自动回复工具
"""

# 微信窗口标题关键词
WECHAT_WINDOW_TITLE = "微信"

# 截图区域配置（相对于微信窗口）
CHAT_AREA = {
    "left_offset": 500,      # 聊天区域左边距（跳过联系人列表）
    "top_offset": 150,        # 聊天区域上边距（跳过标题栏）
    "right_offset": 20,      # 聊天区域右边距
    "bottom_offset": 300,    # 聊天区域下边距（跳过输入框）
}

# 输入框位置配置
INPUT_BOX = {
    "left_offset": 450,      # 输入框左边距
    "bottom_offset": 30,     # 输入框距底部距离
    "width_ratio": 0.6,      # 输入框宽度占窗口宽度比例
}

# 自动回复配置
AUTO_REPLY_CONFIG = {
    "enabled": True,
    "interval": 2,           # 检测间隔（秒）
    "reply_delay": 1,        # 回复延迟（秒）
    "max_reply_length": 200, # 最大回复长度
}