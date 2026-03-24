@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo.
echo 🚀 Jack叔叔视频下载器 - 自动安装脚本
echo =====================================
echo.

REM 检查Python是否安装
echo 🔍 检查Python安装状态...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或不在PATH中
    echo 💡 正在尝试从Microsoft Store安装Python...
    start ms-windows-store://pdp/?productid=9NRWMJP3717K
    echo 📱 请在Microsoft Store中安装Python后重新运行此脚本
    pause
    exit /b 1
) else (
    echo ✅ Python已安装
)

REM 检查pip
echo 🔍 检查pip...
python -m pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip不可用
    echo 💡 正在尝试安装pip...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo ❌ pip安装失败
        pause
        exit /b 1
    )
) else (
    echo ✅ pip可用
)

REM 运行Python自动安装脚本
echo 🚀 运行自动安装程序...
python auto_install.py

if %errorlevel% neq 0 (
    echo ❌ 自动安装失败
    pause
    exit /b 1
)

echo.
echo 🎉 安装完成！现在可以运行start.bat启动程序
echo.
pause