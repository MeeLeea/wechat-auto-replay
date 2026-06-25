# 微信自动回复工具

基于视觉识别（截图+OCR）的微信自动回复工具。

## ⚠️ 免责声明

本工具仅供学习和研究目的使用。使用本工具可能违反微信服务条款，存在账号被封禁的风险。请自行承担使用风险。

## 功能特点

- 通过截图和OCR识别聊天内容
- **智能回复（DeepSeek大语言模型）**
- 支持EasyOCR和Tesseract两种OCR引擎
- 可配置检测间隔和回复延迟

## 环境要求

- Python 3.8+
- Windows系统
- 微信PC版

## 安装步骤

### 1. 安装Python依赖

```bash
cd wechat_auto_reply
pip install -r requirements.txt
```

### 2. 安装OCR引擎

**方式一：EasyOCR（推荐）**
```bash
pip install easyocr
```
首次运行时会自动下载模型文件。

**方式二：Tesseract OCR**
1. 下载安装 Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. 安装中文语言包
3. 将Tesseract添加到系统PATH

### 3. 安装pyperclip（剪贴板支持）

```bash
pip install pyperclip
```

## 配置说明

### config.py - 主配置文件

```python
# 聊天区域配置（需要根据实际微信窗口调整）
CHAT_AREA = {
    "left_offset": 280,      # 聊天区域左边距
    "top_offset": 80,        # 聊天区域上边距
    "right_offset": 20,      # 聊天区域右边距
    "bottom_offset": 150,    # 聊天区域下边距
}

# 输入框位置配置
INPUT_BOX = {
    "left_offset": 300,
    "bottom_offset": 30,
    "width_ratio": 0.6,
}

# 检测配置
AUTO_REPLY_CONFIG = {
    "interval": 2,           # 检测间隔（秒）
    "reply_delay": 1,        # 回复延迟（秒）
}
```

### reply_rules.json - 回复规则

```json
{
    "rules": [
        {
            "keywords": ["你好", "hi"],
            "replies": ["你好呀！", "嗨~"],
            "match_type": "contains",
            "enabled": true
        }
    ],
    "default_reply": "收到~",
    "no_reply_patterns": ["[图片]", "[语音]"]
}
```

**匹配类型 (match_type):**
- `exact`: 完全匹配
- `contains`: 包含匹配
- `startswith`: 前缀匹配
- `endswith`: 后缀匹配
- `regex`: 正则表达式匹配

## 使用方法

### 1. 调整配置

首次使用前，需要根据您的微信窗口大小调整 `config.py` 中的区域配置：

```bash
# 运行测试脚本，获取窗口信息
python window_capture.py
```

这会生成两张截图：
- `wechat_screenshot.png` - 完整微信窗口
- `chat_area.png` - 聊天区域

根据截图调整 `config.py` 中的偏移值。

### 2. 配置DeepSeek API

1. 获取API Key：
   - 访问 https://platform.deepseek.com
   - 注册账号（新用户有免费额度）
   - 创建API Key

2. 编辑 `llm_config.json`，将 `YOUR_API_KEY_HERE` 替换为您的API Key：

```json
{
    "provider": "deepseek",
    "api_key": "sk-xxxxxxxxxxxxxxxx",
    "model": "deepseek-chat"
}
```

3. 安装依赖：
```bash
pip install openai
```

### 3. 运行程序

```bash
python auto_reply.py
```

### 4. 紧急停止

- 按 `Ctrl+C` 停止
- 或将鼠标移动到屏幕左上角（pyautogui的failsafe功能）

## 项目结构

```
wechat_auto_reply/
├── config.py           # 配置文件
├── requirements.txt    # Python依赖
├── window_capture.py   # 窗口捕获模块
├── ocr_recognizer.py  # OCR识别模块
├── auto_reply.py      # 主程序
└── reply_rules.json   # 回复规则
```

## 注意事项

1. **窗口可见性**：微信窗口必须保持可见，不能被其他窗口遮挡
2. **OCR准确率**：中文识别可能存在误差，建议在 `reply_rules.json` 中使用简短关键词
3. **回复延迟**：设置适当的回复延迟，避免过于频繁的操作
4. **隐私保护**：截图会临时保存在内存中，不会持久化存储

## 常见问题

### Q: OCR识别不准确怎么办？
A: 
- 尝试调整 `config.py` 中的聊天区域配置
- 增加图像预处理（调整对比度、锐度）
- 使用EasyOCR替代Tesseract

### Q: 找不到微信窗口？
A: 
- 确保微信已打开
- 检查窗口标题是否包含"微信"字样
- 可能需要调整 `config.py` 中的 `WECHAT_WINDOW_TITLE`

### Q: 点击位置不准确？
A: 
- 运行 `window_capture.py` 查看截图
- 调整 `INPUT_BOX` 配置中的偏移值

## 许可证

MIT License