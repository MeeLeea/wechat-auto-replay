# -*- coding: utf-8 -*-
"""
配置校准工具
用于调整截图区域和输入框位置
"""

import sys
import time
from PIL import Image, ImageDraw, ImageFont

from core import WeChatWindowCapture
from core import config


def draw_grid_on_image(image: Image.Image, grid_size: int = 50) -> Image.Image:
    """在图片上绘制网格"""
    draw = ImageDraw.Draw(image)
    width, height = image.size
    
    # 绘制垂直线
    for x in range(0, width, grid_size):
        draw.line([(x, 0), (x, height)], fill=(255, 0, 0), width=1)
    
    # 绘制水平线
    for y in range(0, height, grid_size):
        draw.line([(0, y), (width, y)], fill=(255, 0, 0), width=1)
    
    # 添加坐标标注
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
    
    for x in range(0, width, grid_size * 2):
        for y in range(0, height, grid_size * 2):
            draw.text((x + 5, y + 5), f"({x},{y})", fill=(255, 0, 0), font=font)
    
    return image


def draw_chat_area(image: Image.Image) -> Image.Image:
    """在图片上标记聊天区域"""
    draw = ImageDraw.Draw(image)
    width, height = image.size
    
    # 计算聊天区域
    chat_left = config.CHAT_AREA["left_offset"]
    chat_top = config.CHAT_AREA["top_offset"]
    chat_right = width - config.CHAT_AREA["right_offset"]
    chat_bottom = height - config.CHAT_AREA["bottom_offset"]
    
    # 绘制矩形框
    draw.rectangle(
        [(chat_left, chat_top), (chat_right, chat_bottom)],
        outline=(0, 255, 0),
        width=3
    )
    
    # 添加标签
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    draw.text((chat_left + 5, chat_top + 5), "聊天区域", fill=(0, 255, 0), font=font)
    
    # 绘制输入框位置
    input_x = config.INPUT_BOX["left_offset"] + int(width * config.INPUT_BOX["width_ratio"] / 2)
    input_y = height - config.INPUT_BOX["bottom_offset"]
    
    # 绘制十字标记
    cross_size = 20
    draw.line([(input_x - cross_size, input_y), (input_x + cross_size, input_y)], fill=(0, 0, 255), width=2)
    draw.line([(input_x, input_y - cross_size), (input_x, input_y + cross_size)], fill=(0, 0, 255), width=2)
    draw.text((input_x + 10, input_y - 20), "输入框", fill=(0, 0, 255), font=font)
    
    return image


def main():
    """主函数"""
    print("=" * 50)
    print("配置校准工具")
    print("=" * 50)
    
    capture = WeChatWindowCapture()
    
    # 查找微信窗口
    if not capture.find_wechat_window():
        print("错误：未找到微信窗口，请确保微信已打开")
        return
    
    window_info = capture.get_window_info()
    print(f"找到微信窗口: {window_info['title']}")
    print(f"窗口大小: {window_info['width']} x {window_info['height']}")
    
    # 将微信窗口置于前台
    print("\n正在将微信窗口置于前台...")
    capture.bring_to_front()
    time.sleep(1)
    
    # 截取完整窗口
    print("\n正在截取微信窗口...")
    screenshot = capture.capture_window()
    if not screenshot:
        print("截图失败")
        return
    
    # 保存原始截图
    screenshot.save("calibrate_full.png")
    print("已保存原始截图: calibrate_full.png")
    
    # 绘制网格
    print("\n正在生成带网格的截图...")
    grid_image = draw_grid_on_image(screenshot.copy())
    grid_image.save("calibrate_grid.png")
    print("已保存网格截图: calibrate_grid.png")
    
    # 绘制当前配置的区域
    print("\n正在标记当前配置区域...")
    marked_image = draw_chat_area(screenshot.copy())
    marked_image.save("calibrate_marked.png")
    print("已保存标记截图: calibrate_marked.png")
    
    # 显示当前配置
    print("\n" + "=" * 50)
    print("当前配置:")
    print("=" * 50)
    print(f"聊天区域左边距: {config.CHAT_AREA['left_offset']}")
    print(f"聊天区域上边距: {config.CHAT_AREA['top_offset']}")
    print(f"聊天区域右边距: {config.CHAT_AREA['right_offset']}")
    print(f"聊天区域下边距: {config.CHAT_AREA['bottom_offset']}")
    print(f"输入框左边距: {config.INPUT_BOX['left_offset']}")
    print(f"输入框底部偏移: {config.INPUT_BOX['bottom_offset']}")
    print(f"输入框宽度比例: {config.INPUT_BOX['width_ratio']}")
    
    print("\n" + "=" * 50)
    print("校准步骤:")
    print("=" * 50)
    print("1. 打开 calibrate_grid.png 查看网格坐标")
    print("2. 打开 calibrate_marked.png 查看当前标记的区域")
    print("3. 根据网格坐标，调整 config.py 中的配置值")
    print("4. 重新运行此脚本验证")
    print("\n提示:")
    print("- 聊天区域应该只包含消息内容区域")
    print("- 输入框标记应该在输入框中心位置")
    print("- 绿色框是聊天区域，蓝色十字是输入框位置")


if __name__ == "__main__":
    main()