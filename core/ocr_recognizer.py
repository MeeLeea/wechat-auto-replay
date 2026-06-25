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
        
        # 微信气泡颜色阈值
        # 白色气泡（对方消息）：RGB接近 (255, 255, 255)
        # 绿色气泡（自己消息）：RGB接近 (95, 180, 75) 或 (149, 237, 105)
        self.white_threshold = 200  # RGB平均值大于此值认为是白色
        self.green_min_r = 50       # 绿色气泡R值范围
        self.green_max_r = 180
        self.green_min_g = 150      # 绿色气泡G值较高
        self.green_max_g = 250
        self.green_min_b = 50       # 绿色气泡B值范围
        self.green_max_b = 150
    
    def _detect_bubble_color(self, image: Image.Image, bbox) -> str:
        """
        检测气泡背景颜色
        
        Args:
            image: 原始图片
            bbox: 文字边界框
            
        Returns:
            "other" - 白色气泡（对方消息）
            "self" - 绿色气泡（自己消息）
            "unknown" - 无法判断
        """
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        img_array = np.array(image)
        
        # 获取边界框坐标
        if self.use_easyocr:
            # EasyOCR bbox: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            x_coords = [int(point[0]) for point in bbox]
            y_coords = [int(point[1]) for point in bbox]
            min_x = min(x_coords)
            max_x = max(x_coords)
            min_y = min(y_coords)
            max_y = max(y_coords)
        else:
            # Tesseract bbox: [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]
            min_x = int(bbox[0][0])
            max_x = int(bbox[1][0])
            min_y = int(bbox[0][1])
            max_y = int(bbox[2][1])
        
        # 扩展区域以包含气泡背景（向左扩展更多，因为气泡在文字左侧）
        padding_left = 30
        padding_right = 10
        padding_top = 15
        padding_bottom = 15
        
        # 确保坐标在图片范围内
        img_height, img_width = img_array.shape[:2]
        left = max(0, min_x - padding_left)
        right = min(img_width, max_x + padding_right)
        top = max(0, min_y - padding_top)
        bottom = min(img_height, max_y + padding_bottom)
        
        if right <= left or bottom <= top:
            return "unknown"
        
        # 提取气泡区域
        bubble_region = img_array[top:bottom, left:right]
        
        if bubble_region.size == 0:
            return "unknown"
        
        # 计算区域内的主要颜色
        # 排除文字区域（取边缘像素）
        edge_pixels = []
        
        # 取左侧边缘像素（气泡背景）
        if left + 5 < right:
            left_edge = bubble_region[:, :5]
            edge_pixels.extend(left_edge.reshape(-1, 3).tolist())
        
        # 取顶部边缘像素
        if top + 5 < bottom:
            top_edge = bubble_region[:5, :]
            edge_pixels.extend(top_edge.reshape(-1, 3).tolist())
        
        if not edge_pixels:
            # 如果没有边缘像素，取整个区域的平均颜色
            avg_color = np.mean(bubble_region.reshape(-1, 3), axis=0)
        else:
            avg_color = np.mean(edge_pixels, axis=0)
        
        r, g, b = avg_color
        
        # 判断颜色类型
        # 白色气泡：RGB都接近255
        avg_rgb = (r + g + b) / 3
        if avg_rgb > self.white_threshold:
            return "other"
        
        # 绿色气泡：G值高，R和B值较低
        if (self.green_min_r <= r <= self.green_max_r and
            self.green_min_g <= g <= self.green_max_g and
            self.green_min_b <= b <= self.green_max_b and
            g > r and g > b):
            return "self"
        
        # 如果G值明显高于R和B，也可能是绿色
        if g > r + 30 and g > b + 30:
            return "self"
        
        return "unknown"
    
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
