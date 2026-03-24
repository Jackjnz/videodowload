#!/bin/bash
# Jack叔叔视频下载器 - 极简版启动脚本

cd "$(dirname "$0")"

echo "🎬 启动Jack叔叔视频下载器极简版 v2.0..."
echo "🌐 将自动在浏览器中打开"
echo "🚀 新功能: 智能队列、实时进度、历史记录"
echo ""

# 检查依赖是否完整
echo "🔍 检查依赖..."
NEED_INSTALL=false

# 检查虚拟环境
if [ ! -d "../venv" ] && [ ! -d "venv" ]; then
    echo "❌ 虚拟环境未找到"
    NEED_INSTALL=true
fi

# 检查Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python未安装"
    NEED_INSTALL=true
fi

# 如果需要安装，运行自动安装脚本
if [ "$NEED_INSTALL" = true ]; then
    echo "🚀 正在运行自动安装程序..."
    if [ -f "auto_install.sh" ]; then
        chmod +x auto_install.sh
        ./auto_install.sh
        if [ $? -ne 0 ]; then
            echo "❌ 自动安装失败，请手动安装依赖"
            exit 1
        fi
    else
        echo "❌ 自动安装脚本不存在，请手动安装依赖"
        exit 1
    fi
fi

# 检查并激活虚拟环境
if [ -d "../venv" ]; then
    echo "🔧 激活虚拟环境..."
    source ../venv/bin/activate
elif [ -d "venv" ]; then
    echo "🔧 激活虚拟环境..."
    source venv/bin/activate
else
    echo "❌ 虚拟环境仍然未找到"
    exit 1
fi

# 启动应用（已内置自动打开浏览器功能）
python3 ultra-simple-downloader.py

echo ""
echo "✅ 浏览器将自动打开，或手动访问显示的地址"
echo ""
echo "💡 使用 Ctrl+C 退出程序"

# 等待用户退出
wait