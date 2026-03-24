#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动检测和安装依赖工具脚本
Auto-detect and install required tools
"""

import os
import sys
import subprocess
import platform
import urllib.request
import shutil
from pathlib import Path

class AutoInstaller:
    def __init__(self):
        self.system = platform.system()
        self.python_version = sys.version_info
        self.required_packages = ['flask', 'requests']
        self.required_tools = ['yt-dlp', 'ffmpeg']
        
    def check_python_version(self):
        """检查Python版本"""
        print("🔍 检查Python版本...")
        if self.python_version < (3, 6):
            print("❌ Python版本过低，需要Python 3.6+")
            print("📥 请访问 https://www.python.org/downloads/ 下载最新版本")
            return False
        print(f"✅ Python版本: {sys.version}")
        return True
    
    def check_pip(self):
        """检查pip是否可用"""
        print("🔍 检查pip...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                         check=True, capture_output=True)
            print("✅ pip可用")
            return True
        except subprocess.CalledProcessError:
            print("❌ pip不可用")
            return False
    
    def check_package(self, package_name):
        """检查Python包是否已安装"""
        try:
            __import__(package_name)
            print(f"✅ {package_name} 已安装")
            return True
        except ImportError:
            print(f"❌ {package_name} 未安装")
            return False
    
    def install_package(self, package_name):
        """安装Python包"""
        print(f"📦 正在安装 {package_name}...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package_name], 
                         check=True)
            print(f"✅ {package_name} 安装成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ {package_name} 安装失败: {e}")
            return False
    
    def check_command(self, command):
        """检查命令是否可用"""
        return shutil.which(command) is not None
    
    def install_yt_dlp(self):
        """安装yt-dlp"""
        print("📦 正在安装yt-dlp...")
        try:
            # 尝试pip安装
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'yt-dlp'], 
                         check=True)
            print("✅ yt-dlp 安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ yt-dlp pip安装失败，尝试直接下载...")
            return self.download_yt_dlp()
    
    def download_yt_dlp(self):
        """直接下载yt-dlp可执行文件"""
        try:
            if self.system == "Windows":
                url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
                filename = "yt-dlp.exe"
            else:
                url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
                filename = "yt-dlp"
            
            print(f"📥 正在下载 {filename}...")
            urllib.request.urlretrieve(url, filename)
            
            if self.system != "Windows":
                os.chmod(filename, 0o755)
            
            print(f"✅ {filename} 下载成功")
            return True
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            return False
    
    def install_ffmpeg_windows(self):
        """Windows系统安装ffmpeg"""
        print("📦 正在为Windows安装ffmpeg...")
        try:
            # 检查是否有winget
            if self.check_command('winget'):
                subprocess.run(['winget', 'install', 'ffmpeg'], check=True)
                print("✅ ffmpeg 通过winget安装成功")
                return True
            else:
                print("💡 请手动安装ffmpeg:")
                print("1. 访问 https://ffmpeg.org/download.html")
                print("2. 下载Windows版本")
                print("3. 解压到程序目录")
                return False
        except subprocess.CalledProcessError:
            print("❌ ffmpeg 安装失败")
            return False
    
    def install_ffmpeg_mac(self):
        """Mac系统安装ffmpeg"""
        print("📦 正在为Mac安装ffmpeg...")
        try:
            # 检查是否有brew
            if self.check_command('brew'):
                subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
                print("✅ ffmpeg 通过brew安装成功")
                return True
            else:
                print("💡 请先安装Homebrew:")
                print('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
                return False
        except subprocess.CalledProcessError:
            print("❌ ffmpeg 安装失败")
            return False
    
    def install_ffmpeg(self):
        """安装ffmpeg"""
        if self.system == "Windows":
            return self.install_ffmpeg_windows()
        elif self.system == "Darwin":
            return self.install_ffmpeg_mac()
        else:
            print("💡 请手动安装ffmpeg:")
            print("sudo apt install ffmpeg  # Ubuntu/Debian")
            print("sudo yum install ffmpeg  # CentOS/RHEL")
            return False
    
    def create_venv(self):
        """创建虚拟环境"""
        venv_path = Path("venv")
        if venv_path.exists():
            print("✅ 虚拟环境已存在")
            return True
        
        print("📦 创建虚拟环境...")
        try:
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
            print("✅ 虚拟环境创建成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 虚拟环境创建失败: {e}")
            return False
    
    def get_venv_python(self):
        """获取虚拟环境的Python路径"""
        if self.system == "Windows":
            return str(Path("venv") / "Scripts" / "python.exe")
        else:
            return str(Path("venv") / "bin" / "python")
    
    def install_packages_in_venv(self):
        """在虚拟环境中安装包"""
        venv_python = self.get_venv_python()
        
        # 检查是否存在requirements.txt
        if os.path.exists('requirements.txt'):
            print("📦 从requirements.txt安装依赖...")
            try:
                subprocess.run([venv_python, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                             check=True)
                print("✅ 所有依赖安装成功")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ 从requirements.txt安装失败: {e}")
                print("🔄 尝试单独安装每个包...")
        
        # 如果requirements.txt不存在或安装失败，则单独安装
        for package in self.required_packages:
            print(f"📦 在虚拟环境中安装 {package}...")
            try:
                subprocess.run([venv_python, '-m', 'pip', 'install', package], 
                             check=True)
                print(f"✅ {package} 安装成功")
            except subprocess.CalledProcessError as e:
                print(f"❌ {package} 安装失败: {e}")
                return False
        
        # 安装yt-dlp到虚拟环境
        print("📦 在虚拟环境中安装yt-dlp...")
        try:
            subprocess.run([venv_python, '-m', 'pip', 'install', 'yt-dlp'], 
                         check=True)
            print("✅ yt-dlp 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ yt-dlp 安装失败: {e}")
            return False
        
        return True
    
    def run_auto_install(self):
        """运行自动安装流程"""
        print("🚀 开始自动检测和安装依赖...")
        print("=" * 50)
        
        # 检查Python版本
        if not self.check_python_version():
            return False
        
        # 检查pip
        if not self.check_pip():
            print("💡 请先安装pip")
            return False
        
        # 创建虚拟环境
        if not self.create_venv():
            return False
        
        # 在虚拟环境中安装包
        if not self.install_packages_in_venv():
            return False
        
        # 检查并安装ffmpeg
        if not self.check_command('ffmpeg'):
            print("❌ ffmpeg 未安装")
            self.install_ffmpeg()
        else:
            print("✅ ffmpeg 已安装")
        
        print("=" * 50)
        print("🎉 自动安装完成！")
        print("💡 现在可以运行启动脚本了")
        
        return True

def main():
    """主函数"""
    installer = AutoInstaller()
    
    try:
        success = installer.run_auto_install()
        if success:
            print("\n✅ 所有依赖安装完成，可以开始使用了！")
        else:
            print("\n❌ 安装过程中出现问题，请检查错误信息")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断安装")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 安装过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()