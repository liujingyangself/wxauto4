# wxauto4 - WeChat自动化工具

<p align="center">
  <img src="https://img.shields.io/badge/Version-0.0.1b1-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/WeChat-4.0.5-green.svg" alt="WeChat">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

wxauto4 是一个适用于微信4.0客户端的 Python 自动化库，提供微信自动化操作接口，包括消息发送、文件传输等功能。

## 重要声明

<font color='red'>**目前仅适用于微信 4.0.5 版本客户端**</font>

下载链接：[点击跳转](https://github.com/SiverKing/wechat4.0-windows-versions/releases)

> [!Warning]
> 请勿直接点击Download URL，找到相应版本，展开Assets点击exe下载


## 安装方式

### 使用 pip 安装（推荐）

```bash
pip install wxauto4
```
或者通过Github

```bash
pip install git+https://github.com/cluic/wxauto4.git
```

### 从源码安装

```bash
git clone https://github.com/cluic/wxauto4.git
cd wxauto4
pip install -e .
```

## 🚀 快速开始

```python
from wxauto4 import WeChat

# 创建微信实例
wx = WeChat()

# 发送消息
wx.SendMsg('你好，世界！', '好友昵称')

# 发送文件
wx.SendFiles(r'C:\path\to\file.txt', '好友昵称')

# 获取消息
messages = wx.GetAllMessage()
for msg in messages:
    print(msg.content)
```


## 文档

### 1. 获取微信实例

```python
from wxauto4 import WeChat

# 创建微信主窗口实例
wx = WeChat()
```

### 2. 发送消息 - SendMsg

```python
# 基础消息发送
wx.SendMsg('Hello!', '目标用户')
```

**参数说明：**
- `msg` (str): 消息内容
- `who` (str, optional): 发送对象，不指定则发送给当前聊天对象
- `clear` (bool, optional): 发送后是否清空编辑框，默认 True
- `at` (Union[str, List[str]], optional): @对象，支持字符串或列表
- `exact` (bool, optional): 是否精确匹配用户名，默认 False

### 3. 发送文件 - SendFiles

```python
# 发送单个文件
wx.SendFiles(r'C:\path\to\file.txt', '目标用户')

# 发送多个文件
files = [
    r'C:\path\to\file1.txt',
    r'C:\path\to\file2.jpg',
    r'C:\path\to\file3.pdf'
]
wx.SendFiles(files, '目标用户')

# 向当前聊天窗口发送文件
wx.SendFiles(r'C:\path\to\file.txt')
```

**参数说明：**
- `filepath` (str|list): 文件的绝对路径，支持单个文件或文件列表
- `who` (str, optional): 发送对象，不指定则发送给当前聊天对象
- `exact` (bool, optional): 是否精确匹配用户名，默认 False

### 4. 获取消息 - GetAllMessage

```python
# 获取当前聊天窗口的所有消息
all_messages = wx.GetAllMessage()
```

**返回值：**
- `List[Message]`: 消息列表，每个消息对象包含发送者、内容、时间、类型等信息

### 5. 监听消息 - AddListenChat

```python
def on_message(msg, chat):
    """消息回调函数"""
    print(f'收到来自 {chat} 的消息: {msg.content}', flush=True)
    
    # 自动回复
    if msg.content == 'hello':
        chat.SendMsg('Hello! 我是xxx')

# 添加消息监听
wx.AddListenChat('好友昵称', on_message)
```

**参数说明：**
- `who` (str|List[str]): 监听对象，支持单个或多个
- `callback` (Callable): 回调函数，接收 `(msg, chat)` 两个参数

### 6. 移除监听 - RemoveListenChat

```python
# 移除特定对象的监听
wx.RemoveListenChat('好友昵称')

# 停止所有监听
wx.StopListening()
```

### 7. 切换聊天窗口 - ChatWith

```python
# 切换到指定聊天窗口
wx.ChatWith('好友昵称')
```

**参数说明：**
- `who` (str): 要切换到的聊天对象
- `exact` (bool, optional): 是否精确匹配名称

### 8. 获取子窗口实例 - GetSubWindow

```python
# 获取指定聊天的子窗口
chat_window = wx.GetSubWindow('好友昵称')

# 通过子窗口发送消息（不会切换主窗口）
chat_window.SendMsg('这是通过子窗口发送的消息')

# 获取子窗口信息
info = chat_window.ChatInfo()
print(f'聊天对象: {info["chat_name"]}')

# 关闭子窗口
chat_window.Close()
```

### 9. 获取所有子窗口实例 - GetAllSubWindow

```python
# 获取所有打开的子窗口
all_windows = wx.GetAllSubWindow()

for window in all_windows:
    print(f'窗口: {window.who}')
    # 可以对每个窗口进行操作
    window.SendMsg('批量消息发送')
    
# 关闭所有子窗口
for window in all_windows:
    window.Close()
```

### 10. 停止监听 - StopListening

```python
# 停止所有消息监听
wx.StopListening()

# 程序结束前建议停止监听
try:
    wx.SendMsg('程序即将结束', '管理员')
finally:
    wx.StopListening()
```

---

**免责声明**: 本工具仅用于学习和研究目的，使用者应当遵守相关法律法规，作者不承担任何因使用本工具而产生的法律责任。