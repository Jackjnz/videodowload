# 🎬 Jack叔叔视频下载器 v2.4

## 📁 目录结构

```
releases/
├── v2.4-Mac/          # Mac版本
│   ├── video-downloader.py
│   ├── start.sh
│   └── README.md
│
├── v2.4-Windows/      # Windows版本
│   ├── video-downloader.py
│   ├── start.bat
│   ├── install.bat
│   ├── fix-errors.bat
│   └── README.md
│
└── README.md          # 本文档
```

## 🖥️ 选择您的系统版本

### 🍎 Mac用户
请进入 **`v2.4-Mac`** 目录

### 🪟 Windows用户
请进入 **`v2.4-Windows`** 目录

## ✨ v2.4 新功能

- 🎮 **完整任务控制**
  - 取消/停止下载
  - 删除任务
  - 重试失败任务
  - 历史记录管理

- 📥 **字幕下载**
  - 自动下载英文/中文字幕
  - 字幕嵌入视频文件

- 🚀 **其他改进**
  - 单文件设计，便于维护
  - 优化的错误处理
  - 更好的跨平台支持

## 📋 系统要求

- Python 3.7 或更高版本
- 稳定的网络连接
- Mac: macOS 10.15 或更高
- Windows: Windows 10/11（推荐）

## 🌐 支持的网站

支持 1000+ 视频网站，包括但不限于：
- YouTube
- Bilibili (B站)
- 抖音 (Douyin)
- Twitter/X
- Instagram
- Facebook
- Vimeo
- 以及更多...

## ⚖️ 使用须知

本软件基于开源项目 yt-dlp，仅供个人学习使用。请遵守相关网站的服务条款，仅下载您有权限访问的内容。

## 🆘 获取帮助

如遇问题，请查看各平台目录中的 README.md 文件，其中包含详细的使用说明和故障排除指南。

---

**版本**: v2.4  
**更新日期**: 2025-08-08  
**作者**: Jack叔叔

---

## 🎨 界面功能说明

### 🔥 主要功能
- **📥 当前队列**：正在下载的视频列表
- **📋 下载历史**：已下载的视频记录
- **🔄 重新下载**：可以重新下载喜欢的视频
- **📋 复制地址**：快速复制视频链接

### 🎛️ 画质选择
- **8K/4320p**：超高清，文件很大，需要好网络
- **4K/2160p**：高清，适合大屏幕
- **2K/1440p**：高清，文件适中
- **1080p**：推荐选择，画质好文件不太大
- **720p**：标清，文件较小
- **480p**：低清，文件很小
- **仅音频**：只下载声音，不要画面

---

## 🌐 支持的网站

✅ **主流视频网站都支持**：
- YouTube（油管）
- 哔哩哔哩（B站）
- 抖音 / TikTok
- 快手
- 微博视频
- 小红书视频
- 其他大部分视频网站

---

## ❓ 常见问题（小白必看）

### Q1: 双击启动文件没反应？
**A**: 
- **Windows**：右键 → "以管理员身份运行"
- **Mac**：右键 → "打开"，然后点"打开"确认

### Q2: 提示没有Python？
**A**: 不用担心！
- **Windows**：程序会提示你去微软商店安装Python
- **Mac**：系统一般都有，如果没有会提示安装

### Q3: 下载失败怎么办？
**A**: 
1. 检查网络连接
2. 确认视频链接正确
3. 尝试选择较低画质
4. 点击"重试"按钮

### Q4: 下载的视频在哪里？
**A**: 
- 在你电脑的"下载"文件夹里
- 文件名就是视频的标题

### Q5: 可以同时下载多个视频吗？
**A**: 
- 可以！最多5个队列，3个同时下载
- 添加多个链接会自动排队

### Q6: 下载速度慢怎么办？
**A**: 
- 检查网络速度
- 选择较低画质
- 耐心等待，不要重复点击

---

## 🛡️ 安全提示

### ✅ 完全安全
- 不会修改你的系统
- 不会收集个人信息
- 只在本地电脑运行
- 开源透明，可放心使用

### 🚫 注意事项
- 只下载你有权限下载的视频
- 不要下载受版权保护的内容
- 下载的视频仅供个人使用

---

## 🆘 遇到问题怎么办？

### 1. 重启解决90%问题
- 关闭程序
- 重新双击启动文件
- 等待浏览器打开

### 2. 检查网络
- 确保能正常上网
- 尝试访问视频网站

### 3. 检查文件完整性
- 确认 `venv` 文件夹存在
- 确认完整复制了整个目录
- 不要只复制 `Jack叔叔视频下载器极简版` 子文件夹

### 4. 重新安装
- 删除整个文件夹
- 重新复制新的完整文件夹（包含venv）
- 重新启动

### 5. 查看错误信息
- 程序窗口会显示错误原因
- 根据提示操作

---

## 💡 使用技巧

### 🔥 高效下载
1. **批量下载**：一个完成后立即粘贴下一个
2. **选择合适画质**：1080p性价比最高
3. **稳定网络**：WiFi比手机热点稳定
4. **充足空间**：确保硬盘有足够空间

### 🎯 避免问题
1. **复制完整链接**：确保链接完整无缺
2. **不要关闭浏览器**：下载期间保持页面开启
3. **耐心等待**：高画质视频需要时间
4. **定期清理**：及时清理下载文件夹

---

## 🔧 技术说明

### 📦 依赖的开源工具
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)**：核心视频下载引擎，支持1000+网站
- **[Flask](https://github.com/pallets/flask)**：轻量级Web框架，提供用户界面
- **Python 3.x**：程序运行环境

### 📚 技术文档链接
- **[完整安装指南](安装指南.md)** - 从零开始的详细安装教程
- **[下载引擎命令参考](../下载工具大全.md)** - 软件使用的所有下载命令
- **[依赖包列表](requirements.txt)** - 所需的Python依赖包

### 🔧 快速安装
如果遇到依赖问题，可以使用自动安装：
- **Windows**: 双击运行 `auto_install.bat`
- **Mac**: 双击运行 `auto_install.sh`
- **手动安装**: `pip install -r requirements.txt`

### 📚 必要的Python库
- `flask`：Web界面框架
- `subprocess`：调用yt-dlp下载工具
- `threading`：多线程下载管理
- `json`：数据存储格式

### 📁 文件结构说明
```
视频下载/
├── venv/                    # Python虚拟环境（必需）
├── Jack叔叔视频下载器极简版/
│   ├── ultra-simple-downloader.py  # 主程序
│   ├── start.sh             # Mac启动脚本
│   ├── start.bat            # Windows启动脚本
│   └── README.md            # 使用说明
├── app_icon.icns           # 应用图标
└── 带图标DMG创建.sh        # DMG打包脚本
```

**⚠️ 重要提醒**：
- 必须完整复制整个目录，特别是 `venv` 文件夹
- `venv` 包含预安装的Flask等必需库
- 缺少 `venv` 会导致Flask模块找不到的错误

---

## 📞 版本信息

- **软件名称**：Jack叔叔视频下载器
- **版本**：极简版 v2.0
- **更新日期**：2025年7月13日
- **适用人群**：所有人，特别是电脑小白
- **设计理念**：让视频下载变得像用微信一样简单
- **核心技术**：基于yt-dlp + Flask的本地Web应用

---

## 🎉 开始使用吧！

**记住这三步**：
1. **双击启动** → 2. **粘贴链接** → 3. **点击下载**

就这么简单！享受你的视频下载之旅吧！📺✨

---

> **🔔 温馨提示**：首次使用会自动安装组件，请耐心等待。建议在WiFi环境下使用，体验更佳！
----------------
# 🛠️ Jack叔叔视频下载器 - 完整安装指南

## 📋 系统要求

### 🖥️ 支持的操作系统
- **Windows**: Windows 10 或更高版本
- **macOS**: macOS 10.14 或更高版本  
- **Linux**: Ubuntu 18.04+ / CentOS 7+ / 其他主流发行版

### 💾 系统要求
- **内存**: 至少 2GB RAM
- **硬盘空间**: 至少 1GB 可用空间
- **网络**: 稳定的互联网连接

---

## 🐍 第一步: 安装Python

### Windows系统

#### 方法1: 微软商店安装（推荐）
1. 打开 **Microsoft Store**
2. 搜索 **"Python"**
3. 选择 **"Python 3.11"** 或更高版本
4. 点击 **"获取"** 并等待安装完成

#### 方法2: 官网下载
1. 访问 [python.org](https://www.python.org/downloads/)
2. 下载 **Python 3.8+** 版本
3. 运行安装程序
4. **⚠️ 重要**: 勾选 **"Add Python to PATH"**
5. 点击 **"Install Now"**

#### 验证安装
```cmd
python --version
```
应该显示类似 `Python 3.11.x` 的版本信息

### macOS系统

#### 方法1: Homebrew安装（推荐）
```bash
# 1. 安装Homebrew（如果没有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安装Python
brew install python
```

#### 方法2: 官网下载
1. 访问 [python.org](https://www.python.org/downloads/)
2. 下载 **macOS** 版本
3. 运行 `.pkg` 安装程序
4. 按照提示完成安装

#### 验证安装
```bash
python3 --version
```
应该显示类似 `Python 3.11.x` 的版本信息

### Linux系统

#### Ubuntu/Debian
```bash
# 更新包列表
sudo apt update

# 安装Python和pip
sudo apt install python3 python3-pip python3-venv

# 验证安装
python3 --version
pip3 --version
```

#### CentOS/RHEL
```bash
# 安装Python
sudo yum install python3 python3-pip

# 或者使用dnf（较新系统）
sudo dnf install python3 python3-pip

# 验证安装
python3 --version
pip3 --version
```

---

## 📦 第二步: 验证pip包管理器

### Windows
```cmd
# 检查pip版本
pip --version

# 如果pip不存在，安装pip
python -m ensurepip --upgrade
```

### macOS/Linux
```bash
# 检查pip版本
pip3 --version

# 如果pip不存在，安装pip
python3 -m ensurepip --upgrade
```

---

## 🏠 第三步: 创建虚拟环境

虚拟环境是Python项目的独立环境，避免依赖冲突。

### Windows
```cmd
# 进入软件目录
cd "Jack叔叔视频下载器极简版"

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 激活后，命令提示符会显示 (venv)
```

### macOS/Linux
```bash
# 进入软件目录
cd "Jack叔叔视频下载器极简版"

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 激活后，命令提示符会显示 (venv)
```

---

## 🔧 第四步: 安装必要的Python包

### 自动安装（推荐）
```bash
# 确保虚拟环境已激活
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装所有依赖
pip install flask yt-dlp requests
```

### 手动验证安装
```bash
# 检查Flask
python -c "import flask; print('Flask版本:', flask.__version__)"

# 检查yt-dlp
yt-dlp --version

# 检查其他库
python -c "import subprocess, threading, json; print('标准库正常')"
```

---

## 🎯 第五步: 验证安装

### 1. 检查Python环境
```bash
# 激活虚拟环境后运行
python --version
pip list
```

应该看到类似输出：
```
Flask==2.3.3
yt-dlp==2023.x.x
requests==2.31.0
```

### 2. 测试软件启动
```bash
# Windows
start.bat

# macOS/Linux
./start.sh
```

如果看到类似输出，说明安装成功：
```
🎬 启动Jack叔叔视频下载器极简版 v2.0...
🔧 激活虚拟环境...
* Running on http://127.0.0.1:5000
```

---

## 🆘 常见问题解决

### ❌ 问题1: "python不是内部或外部命令"

**Windows解决方案**:
1. 重新安装Python，确保勾选 "Add Python to PATH"
2. 或手动添加到系统PATH环境变量

**验证**: 打开新的命令提示符，输入 `python --version`

### ❌ 问题2: "No module named 'flask'"

**解决方案**:
```bash
# 确保虚拟环境已激活
pip install flask

# 如果还是不行，尝试
pip install --upgrade flask
```

### ❌ 问题3: "yt-dlp command not found"

**解决方案**:
```bash
# 在虚拟环境中安装
pip install yt-dlp

# 或者使用python调用
python -m yt_dlp --version
```

### ❌ 问题4: Mac系统"Permission denied"

**解决方案**:
```bash
# 给启动脚本添加执行权限
chmod +x start.sh

# 或者
sudo ./start.sh
```

### ❌ 问题5: 端口5000被占用

**解决方案**:
```bash
# 查看端口占用
netstat -an | grep 5000

# 或者修改软件端口（编辑ultra-simple-downloader.py）
app.run(host='0.0.0.0', port=5001, debug=False)
```

---

## 🚀 快速安装脚本

### 全自动安装
我们提供了自动安装脚本，可以一键完成所有安装步骤：

**Windows**:
```cmd
# 双击运行
auto_install.bat

# 或命令行运行
auto_install.bat
```

**macOS/Linux**:
```bash
# 给脚本添加执行权限
chmod +x auto_install.sh

# 运行自动安装
./auto_install.sh
```

---

## 📁 安装后的文件结构

安装完成后，您的目录应该看起来像这样：

```
Jack叔叔视频下载器极简版/
├── venv/                          # 虚拟环境（重要！）
│   ├── Scripts/                   # Windows
│   ├── bin/                       # macOS/Linux
│   └── lib/                       # Python包
├── ultra-simple-downloader.py     # 主程序
├── start.bat                      # Windows启动脚本
├── start.sh                       # macOS/Linux启动脚本
├── auto_install.bat               # Windows自动安装
├── auto_install.sh                # macOS/Linux自动安装
├── auto_install.py                # 自动安装核心脚本
├── requirements.txt               # 依赖列表
├── README.md                      # 使用说明
├── 安装指南.md                    # 本文档
└── download_history.json          # 下载历史（自动创建）
```

---

## 🎉 安装完成！

### 启动软件
```bash
# Windows
start.bat

# macOS/Linux
./start.sh
```

### 使用软件
1. 启动后浏览器会自动打开
2. 访问 `http://localhost:5000`
3. 粘贴视频链接
4. 选择画质
5. 点击下载

### 🎯 重要提醒
- **始终在虚拟环境中运行软件**
- **不要删除venv文件夹**
- **遇到问题先查看本安装指南**

---

## 📞 获取帮助

如果按照本指南安装后仍有问题：

1. **检查系统要求**：确保系统满足最低要求
2. **重新安装**：删除venv文件夹，重新运行安装脚本
3. **查看错误日志**：运行时的错误信息通常会提示具体问题
4. **网络问题**：确保能正常访问GitHub和PyPI

---

**🎬 享受您的视频下载之旅！**
