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
    """聊天消息解析器"""
    
    def __init__(self, ocr: OCRRecognizer):
        self.ocr = ocr
        self.use_easyocr = ocr.use_easyocr
    
    def parse_messages(self, image: Image.Image) -> List[dict]:
        """解析聊天截图中的消息"""
        processed_image = self.ocr.preprocess_image(image)
        ocr_results = self.ocr.recognize(processed_image)
        
        if not ocr_results:
            return []
        
        messages = []
        image_width = image.size[0]
        
        for item in ocr_results:
            text = item["text"].strip()
            if not text:
                continue
            
            bbox = item["bbox"]
            
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
        """获取最新的对方消息"""
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
