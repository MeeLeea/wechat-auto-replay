# -*- coding: utf-8 -*-
"""
OCR文字识别模块
支持EasyOCR和Tesseract两种引擎
"""

from PIL import Image
from typing import List, Optional
import numpy as np


class OCRRecognizer:
    """OCR识别器"""
    
    def __init__(self):
        self.reader = None
        self.use_easyocr = False
        self._init_ocr()
    
    def _init_ocr(self):
        """初始化OCR引擎"""
        # 优先尝试EasyOCR
        try:
            import easyocr
            print("正在初始化EasyOCR引擎（首次运行会下载模型，请耐心等待）...")
            self.reader = easyocr.Reader(
                ["ch_sim", "en"],
                gpu=False
            )
            self.use_easyocr = True
            print("EasyOCR初始化完成")
            return
        except ImportError:
            print("EasyOCR未安装")
        except Exception as e:
            print(f"EasyOCR初始化失败: {e}")
        
        # 尝试使用Tesseract
        try:
            import pytesseract
            # 检查Tesseract是否可用
            version = pytesseract.get_tesseract_version()
            self.reader = pytesseract
            self.use_easyocr = False
            print(f"使用Tesseract OCR引擎 (版本: {version})")
            return
        except ImportError:
            print("Tesseract未安装")
        except Exception as e:
            print(f"Tesseract不可用: {e}")
        
        # 尝试Windows自带OCR
        try:
            import uiautomation as auto
            print("使用Windows OCR引擎")
            self.use_windows_ocr = True
            self.reader = auto
            return
        except ImportError:
            pass
        
        print("\n" + "=" * 50)
        print("错误：未检测到任何OCR引擎！")
        print("请安装以下任一OCR工具：")
        print("")
        print("方案1：安装EasyOCR（推荐）")
        print("  pip install easyocr")
        print("")
        print("方案2：安装Tesseract + pytesseract")
        print("  1. 下载: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  2. 安装中文语言包")
        print("  3. pip install pytesseract")
        print("")
        print("方案3：安装Windows OCR依赖")
        print("  pip install uiautomation")
        print("=" * 50)
        
        self.reader = None
    
    def recognize(self, image: Image.Image) -> List[dict]:
        """识别图片中的文字"""
        if not self.reader:
            print("错误：OCR引擎未初始化")
            return []
        
        results = []
        
        try:
            if self.use_easyocr:
                img_array = np.array(image)
                raw_results = self.reader.readtext(img_array)
                
                for item in raw_results:
                    bbox, text, confidence = item
                    if text.strip():
                        results.append({
                            "text": text,
                            "bbox": bbox,
                            "confidence": confidence
                        })
            else:
                # 使用Tesseract
                import pytesseract
                
                data = pytesseract.image_to_data(
                    image,
                    lang="chi_sim+eng",
                    output_type=pytesseract.Output.DICT
                )
                
                n_boxes = len(data['text'])
                for i in range(n_boxes):
                    if int(data['conf'][i]) > 0:
                        text = data['text'][i].strip()
                        if text:
                            results.append({
                                "text": text,
                                "bbox": [
                                    (data['left'][i], data['top'][i]),
                                    (data['left'][i] + data['width'][i], data['top'][i]),
                                    (data['left'][i] + data['width'][i], data['top'][i] + data['height'][i]),
                                    (data['left'][i], data['top'][i] + data['height'][i])
                                ],
                                "confidence": float(data['conf'][i]) / 100
                            })
        
        except Exception as e:
            print(f"OCR识别错误: {e}")
        
        return results
    
    def recognize_text_only(self, image: Image.Image) -> str:
        """只返回识别的文字文本"""
        results = self.recognize(image)
        texts = [item["text"] for item in results if item["text"].strip()]
        return "\n".join(texts)
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """图像预处理，提高OCR准确率"""
        from PIL import ImageEnhance
        
        if image.mode != 'L':
            image = image.convert('L')
        
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        return image


class ChatMessageParser:
    """聊天消息解析器 - 根据气泡颜色区分消息来源"""
    
    def __init__(self, ocr: OCRRecognizer):
        self.ocr = ocr
        self.use_easyocr = ocr.use_easyocr
        
        # 微信绿色气泡颜色参考值 (149, 237, 105)
        # 判定条件：G 通道值高且明显大于 R 和 B
        self.green_g_min = 140            # 绿色 G 通道最小值
        self.green_dominance = 20          # G 比 R/B 大于此值才认定为绿色
    
    def _detect_bubble_color(self, image: Image.Image, bbox) -> str:
        """
        检测气泡背景颜色
        
        通过统计文字区域周围的颜色像素来判断：
        - 存在大量绿色像素 -> 自己发送（绿色气泡）
        - 几乎无绿色像素 -> 对方发送（白色气泡）
        """
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        img_array = np.array(image)
        img_height, img_width = img_array.shape[:2]
        
        # 获取文本区域坐标
        if self.use_easyocr:
            x_coords = [int(point[0]) for point in bbox]
            y_coords = [int(point[1]) for point in bbox]
            min_x, max_x = min(x_coords), max(x_coords)
            min_y, max_y = min(y_coords), max(y_coords)
        else:
            min_x = int(bbox[0][0])
            max_x = int(bbox[1][0])
            min_y = int(bbox[0][1])
            max_y = int(bbox[2][1])
        
        text_width = max_x - min_x
        text_height = max_y - min_y
        
        if text_width <= 0 or text_height <= 0:
            return "unknown"
        
        # 扩大采样区域 - 关键是要包含气泡背景
        # 绿色气泡的 padding 通常在左侧较大
        # 使用较大的 padding 确保能采到气泡颜色
        padding_h = max(40, int(text_height * 1.2))
        padding_v = max(15, int(text_height * 0.5))
        
        left = max(0, min_x - padding_h)
        right = min(img_width, max_x + 20)
        top = max(0, min_y - padding_v)
        bottom = min(img_height, max_y + padding_v)
        
        if right <= left or bottom <= top:
            return "unknown"
        
        # 提取气泡区域
        bubble_region = img_array[top:bottom, left:right]
        
        if bubble_region.size == 0:
            return "unknown"
        
        # 分离RGB通道，统计颜色
        r = bubble_region[:, :, 0].astype(int)
        g = bubble_region[:, :, 1].astype(int)
        b = bubble_region[:, :, 2].astype(int)
        
        # 统计绿色像素（绿色气泡特征：G值高且大于R和B）
        # 微信绿色: 大约 (149, 237, 105)
        green_mask = (
            (g >= self.green_g_min) &
            (g > r + self.green_dominance) &
            (g > b + self.green_dominance)
        )
        green_count = int(np.sum(green_mask))
        
        total = bubble_region.shape[0] * bubble_region.shape[1]
        green_ratio = green_count / total if total > 0 else 0
        
        # 决策：区域内有足够多的绿色像素 -> 自己发送
        if green_ratio > 0.15:
            return "self"
        
        # 否则认为是对方发送的（白色气泡）
        return "other"
    
    def _is_time_label(self, text: str) -> bool:
        """
        判断是否为时间标签（如 "16:50", "上午 10:30"）
        时间标签不是消息，需要过滤
        """
        import re
        cleaned = text.strip()
        # 匹配 HH:MM 格式
        if re.match(r"^\d{1,2}:\d{2}$", cleaned):
            return True
        # 匹配 "上午/下午/早上/晚上 HH:MM" 格式
        if re.match(r"^(上午|下午|早上|晚上|凌晨|清晨)\s*\d{1,2}:\d{2}$", cleaned):
            return True
        # 匹配 "昨天/今天 HH:MM" 格式
        if re.match(r"^(昨天|今天|前天|周一|周二|周三|周四|周五|周六|周日)\s*\d{1,2}:\d{2}$", cleaned):
            return True
        return False

    def parse_messages(self, image: Image.Image) -> List[dict]:
        """
        解析聊天截图中的消息
        
        根据气泡颜色判断消息来源：
        - 白色气泡：对方发送的消息
        - 绿色气泡：自己发送的消息
        """
        # 保留原始RGB图片用于颜色检测
        original_image = image.copy()
        if original_image.mode != 'RGB':
            original_image = original_image.convert('RGB')
        
        # 使用预处理图片进行OCR
        processed_image = self.ocr.preprocess_image(image)
        ocr_results = self.ocr.recognize(processed_image)
        
        if not ocr_results:
            return []
        
        messages = []
        
        for item in ocr_results:
            text = item["text"].strip()
            if not text:
                continue
            
            # 过滤时间标签
            if self._is_time_label(text):
                continue
            
            bbox = item["bbox"]
            
            # 根据气泡颜色判断发送者
            sender = self._detect_bubble_color(original_image, bbox)
            
            # 如果颜色判断失败，使用位置作为备用判断
            if sender == "unknown":
                image_width = image.size[0]
                if self.use_easyocr:
                    x_coords = [point[0] for point in bbox]
                    center_x = sum(x_coords) / len(x_coords)
                else:
                    center_x = (bbox[0][0] + bbox[1][0]) / 2
                sender = "other" if center_x < image_width * 0.5 else "self"
            
            messages.append({
                "sender": sender,
                "text": text,
                "bbox": bbox,
                "confidence": item.get("confidence", 1.0)
            })
        
        return messages
    
    def get_latest_other_message(self, messages: List[dict]) -> Optional[dict]:
        """获取最新的对方消息（白色气泡）"""
        other_messages = [m for m in messages if m["sender"] == "other"]
        if other_messages:
            return other_messages[-1]
        return None


if __name__ == "__main__":
    ocr = OCRRecognizer()
    
    if not ocr.reader:
        print("OCR引擎未就绪，请安装OCR工具")
    else:
        print("OCR引擎就绪")
