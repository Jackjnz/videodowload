@echo off
chcp 65001 > nul
echo 🎬 启动Jack叔叔视频下载器极简版 v2.0...
echo 🌐 将自动在浏览器中打开
echo 🚀 新功能: 智能队列、实时进度、历史记录
echo.

REM 检查依赖是否完整
echo 🔍 检查依赖...
set NEED_INSTALL=false

REM 检查虚拟环境
if not exist "..\venv" (
    if not exist "venv" (
        echo ❌ 虚拟环境未找到
        set NEED_INSTALL=true
    )
)

REM 检查Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装
    set NEED_INSTALL=true
)

REM 如果需要安装，运行自动安装脚本
if "%NEED_INSTALL%"=="true" (
    echo 🚀 正在运行自动安装程序...
    if exist "auto_install.bat" (
        call auto_install.bat
        if %errorlevel% neq 0 (
            echo ❌ 自动安装失败，请手动安装依赖
            pause
            exit /b 1
        )
    ) else (
        echo ❌ 自动安装脚本不存在，请手动安装依赖
        pause
        exit /b 1
    )
)

REM 检查并激活虚拟环境
if exist "..\venv\Scripts\activate.bat" (
    echo 🔧 激活虚拟环境...
    call ..\venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo 🔧 激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo ❌ 虚拟环境仍然未找到
    pause
    exit /b 1
)

python ultra-simple-downloader.py
pause