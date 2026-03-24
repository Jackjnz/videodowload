#!/bin/bash
# -*- coding: utf-8 -*-

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}🚀 Jack叔叔视频下载器 - 自动安装脚本${NC}"
echo "====================================="
echo ""

# 检查操作系统
OS=$(uname -s)
echo -e "${BLUE}🔍 检测到操作系统: ${OS}${NC}"

# 检查Python3
echo -e "${BLUE}🔍 检查Python3安装状态...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python3已安装: ${PYTHON_VERSION}${NC}"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        echo -e "${GREEN}✅ Python3已安装: ${PYTHON_VERSION}${NC}"
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Python版本过低，需要Python 3.6+${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Python3未安装${NC}"
    
    if [[ "$OS" == "Darwin" ]]; then
        echo -e "${YELLOW}💡 正在尝试安装Python3...${NC}"
        
        # 检查是否有brew
        if command -v brew &> /dev/null; then
            echo -e "${BLUE}📦 使用Homebrew安装Python3...${NC}"
            brew install python3
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Python3安装成功${NC}"
                PYTHON_CMD="python3"
            else
                echo -e "${RED}❌ Python3安装失败${NC}"
                exit 1
            fi
        else
            echo -e "${YELLOW}💡 请先安装Homebrew:${NC}"
            echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            echo -e "${YELLOW}然后重新运行此脚本${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}💡 请手动安装Python3:${NC}"
        echo "sudo apt update && sudo apt install python3 python3-pip  # Ubuntu/Debian"
        echo "sudo yum install python3 python3-pip  # CentOS/RHEL"
        exit 1
    fi
fi

# 检查pip
echo -e "${BLUE}🔍 检查pip...${NC}"
if $PYTHON_CMD -m pip --version &> /dev/null; then
    echo -e "${GREEN}✅ pip可用${NC}"
else
    echo -e "${RED}❌ pip不可用${NC}"
    echo -e "${BLUE}💡 正在尝试安装pip...${NC}"
    
    if [[ "$OS" == "Darwin" ]]; then
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        $PYTHON_CMD get-pip.py
        rm get-pip.py
    else
        sudo apt install python3-pip  # Ubuntu/Debian
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ pip安装成功${NC}"
    else
        echo -e "${RED}❌ pip安装失败${NC}"
        exit 1
    fi
fi

# 运行Python自动安装脚本
echo -e "${BLUE}🚀 运行自动安装程序...${NC}"
$PYTHON_CMD auto_install.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 安装完成！现在可以运行start.sh启动程序${NC}"
    echo ""
    
    # 给脚本添加执行权限
    chmod +x start.sh
    echo -e "${BLUE}💡 提示：运行 ./start.sh 启动程序${NC}"
else
    echo -e "${RED}❌ 自动安装失败${NC}"
    exit 1
fi