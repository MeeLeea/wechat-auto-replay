# 微信自动回复工具

基于视觉识别（截图 + OCR）的微信 PC 版自动回复工具。通过屏幕截图获取聊天内容，OCR 识别文字，AI 生成回复后模拟键盘输入发送。

## ⚠️ 免责声明

本工具仅供学习和研究目的使用。使用本工具可能违反微信服务条款，存在账号被封禁的风险。请自行承担使用风险。

## 功能特点

- **视觉识别**：通过截图 + OCR 读取聊天内容，无需 Hook 微信进程
- **气泡颜色区分**：绿色气泡 = 自己发送（跳过），白色气泡 = 对方发送（回复），避免回复自己
- **多种回复模式**：
  - 智能回复模式：调用大语言模型生成自然回复
  - 怼人模式：130+ 条文明怼人 + 毒舌吐槽语句随机输出
- **多 LLM 提供商支持**：智谱 AI、DeepSeek、OpenAI、通义千问
- **多 OCR 引擎**：EasyOCR（推荐）、Tesseract、Windows OCR
- **校准工具**：可视化调整聊天区域和输入框位置
- **时间戳过滤**：自动过滤 "16:50"、"上午 10:30" 等时间标签

## 环境要求

- Python 3.8+
- Windows 系统
- 微信 PC 版
- 虚拟环境（推荐）

## 安装步骤

### 1. 创建虚拟环境（推荐）

```powershell
cd d:\work
python -m venv wechat_auto_reply\venv
```

激活虚拟环境：

```powershell
wechat_auto_reply\venv\Scripts\activate
```

### 2. 安装 Python 依赖

```powershell
cd d:\work\wechat_auto_reply
pip install -r requirements.txt
```

### 3. 安装智能回复依赖

根据使用的 LLM 提供商安装对应 SDK：

**智谱 AI（默认）**
```powershell
pip install zhipuai
```

**DeepSeek / OpenAI 兼容接口**
```powershell
pip install openai
```

**通义千问**
```powershell
pip install dashscope
```

### 4. OCR 引擎

程序会按以下顺序自动检测可用的 OCR 引擎，安装任一即可：

**方式一：EasyOCR（推荐，准确率高）**
```powershell
pip install easyocr
```
首次运行会自动下载中文模型，约 100MB，请耐心等待。

**方式二：Tesseract OCR**
1. 下载安装：https://github.com/UB-Mannheim/tesseract/wiki
2. 安装中文语言包（chi_sim）
3. 将 Tesseract 添加到系统 PATH
4. `pip install pytesseract`

**方式三：Windows 自带 OCR**
```powershell
pip install uiautomation
```

### 5. 剪贴板支持

```powershell
pip install pyperclip
```

## 配置说明

### llm_config.json - 大模型配置

```json
{
    "provider": "zhipu",
    "api_key": "你的API Key",
    "model": "glm-4-flash",
    "base_url": ""
}
```

**provider 可选值**：
- `zhipu` - 智谱 AI（GLM 系列）
- `deepseek` - DeepSeek
- `openai` - OpenAI 及兼容接口（如硅基流动等，需填 base_url）
- `qwen` - 通义千问

### config.py - 主配置文件

```python
# 微信窗口标题关键词
WECHAT_WINDOW_TITLE = "微信"

# 聊天区域（相对于微信窗口）
CHAT_AREA = {
    "left_offset": 500,      # 左边距（跳过联系人列表）
    "top_offset": 150,       # 上边距（跳过标题栏）
    "right_offset": 20,      # 右边距
    "bottom_offset": 300,    # 下边距（跳过输入框）
}

# 输入框位置
INPUT_BOX = {
    "left_offset": 450,      # 左边距
    "bottom_offset": 30,     # 距底部距离
    "width_ratio": 0.6,      # 宽度占窗口比例
}

# 自动回复参数
AUTO_REPLY_CONFIG = {
    "interval": 2,           # 检测间隔（秒）
    "reply_delay": 1,        # 回复延迟（秒）
    "max_reply_length": 200, # 最大回复长度
}
```

## 使用方法

### 1. 校准聊天区域（首次使用必做）

```powershell
venv\Scripts\python calibrate.py
```

运行后会生成 3 张截图：
- `calibrate_full.png` - 完整微信窗口
- `calibrate_grid.png` - 带坐标网格的截图
- `calibrate_marked.png` - 标记了当前聊天区域（绿框）和输入框（蓝十字）的截图

根据截图调整 `config.py` 中的偏移值，重新运行校准脚本验证。

### 2. 运行自动回复

**正常智能回复模式（默认）**
```powershell
venv\Scripts\python auto_reply.py
```

**怼人模式**
```powershell
venv\Scripts\python auto_reply.py --anger
# 或
venv\Scripts\python auto_reply.py -a
# 或
venv\Scripts\python auto_reply.py --mode counter
```

**查看所有可用模式**
```powershell
venv\Scripts\python auto_reply.py --help
```

### 3. 紧急停止

- 按 `Ctrl + C` 停止程序
- 或将鼠标快速移到屏幕左上角（pyautogui 安全机制）

## 项目结构

```
wechat_auto_reply/
├── auto_reply.py              # 主程序入口
├── calibrate.py               # 配置校准工具
├── config.py                  # （已迁移到 core/，保留向后兼容）
├── requirements.txt           # Python 依赖
├── llm_config.json            # 大模型 API 配置
├── README.md                  # 说明文档
└── core/                      # 核心功能包
    ├── __init__.py            # 包导出
    ├── config.py              # 配置文件
    ├── window_capture.py      # 窗口定位与截图
    ├── ocr_recognizer.py      # OCR 识别 + 气泡颜色检测
    ├── smart_reply.py         # 智能回复引擎（多 LLM 提供商）
    └── reply_modes/           # 回复模式包
        ├── __init__.py
        ├── base.py            # 回复模式基类 + 注册表
        ├── normal_mode.py     # 正常智能回复模式
        └── counter_mode.py    # 怼人模式（文明怼人 + 毒舌吐槽）
```

## 核心原理

### 气泡颜色检测

微信聊天界面中：
- **绿色气泡**（RGB 约 149, 237, 105）：自己发送的消息
- **白色气泡**（RGB 约 255, 255, 255）：对方发送的消息

程序通过统计 OCR 文字框周围像素的绿色占比来判断消息来源：
- 绿色像素占比 > 15% → 自己发送 → 跳过
- 否则 → 对方发送 → 需要回复

这有效避免了回复自己消息的死循环。

### 回复模式扩展

新增回复模式只需在 `core/reply_modes/` 下新建一个文件，继承 `ReplyMode` 基类并注册：

```python
from .base import ReplyMode, ReplyModeRegistry

class MyMode(ReplyMode):
    name = "my_mode"
    description = "我的自定义模式"
    
    def _load_replies(self):
        self.replies = ["回复1", "回复2"]
    
    def get_reply(self, message: str = "") -> str:
        # 可重写此方法实现自定义逻辑
        return super().get_reply(message)

ReplyModeRegistry.register("my_mode", MyMode)
```

然后通过 `--mode my_mode` 参数即可使用。

## 注意事项

1. **窗口可见性**：微信窗口必须保持可见，不能被其他窗口完全遮挡
2. **OCR 准确率**：识别可能存在误差，尤其是字体较小时
3. **回复频率**：设置合理的检测间隔和回复延迟，避免操作过快被风控
4. **气泡颜色**：如果使用了微信自定义皮肤，气泡颜色可能变化，需调整 `ocr_recognizer.py` 中的颜色阈值
5. **调试输出**：运行时会打印每条 OCR 结果及其判定（`self` / `other`），方便排查问题

## 常见问题

### Q: 提示 OCR 引擎未初始化？
A: 请确保已安装至少一种 OCR 引擎。推荐安装 EasyOCR：`pip install easyocr`

### Q: 找不到微信窗口？
A:
- 确保微信 PC 版已打开并登录
- 检查窗口标题是否包含"微信"字样
- 可修改 `config.py` 中的 `WECHAT_WINDOW_TITLE` 匹配你的窗口标题

### Q: 回复了自己发的消息？
A:
- 检查气泡颜色检测是否正常，运行时观察控制台 `[OCR]` 输出
- 如果使用了非默认微信皮肤，绿色气泡颜色可能不同，需调整 `ChatMessageParser` 中的 `green_g_min` 和 `green_dominance` 参数
- 确保聊天区域配置正确，没有截到太多白色背景

### Q: OCR 识别不准 / 乱码？
A:
- 运行 `calibrate.py` 确认聊天区域是否正确
- 尝试调大聊天区域，确保气泡完整显示
- 使用 EasyOCR 替代 Tesseract（准确率更高）
- 确保微信字体大小适中

### Q: 点击输入框位置不对？
A: 运行 `calibrate.py`，查看 `calibrate_marked.png` 中蓝色十字的位置，调整 `INPUT_BOX` 配置。

### Q: 智能回复调用失败？
A:
- 检查 `llm_config.json` 中的 API Key 是否正确
- 确认对应 SDK 已安装（智谱需要 `pip install zhipuai`）
- 查看控制台错误信息，确认是密钥错误、网络问题还是模型名称错误

## 许可证

MIT License
