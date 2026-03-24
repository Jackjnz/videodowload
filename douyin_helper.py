#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音下载助手
解决抖音Cookie和访问问题
"""

import os
import subprocess
import json
import re
import time
from pathlib import Path
from base_helper import run_download_command

class DouyinHelper:
    def __init__(self):
        self.cookie_file = "douyin_cookies.txt"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def get_douyin_download_command(self, url, quality='1080p', output_dir=None):
        """
        生成抖音下载命令
        """
        if not output_dir:
            output_dir = os.path.expanduser("~/Downloads")
        
        # 基础命令
        cmd = [
            'yt-dlp',
            '--no-check-certificate',
            '--user-agent', self.headers['User-Agent'],
            '--referer', 'https://www.douyin.com/',
            '--add-header', 'Accept:' + self.headers['Accept'],
            '--add-header', 'Accept-Language:' + self.headers['Accept-Language'],
        ]
        
        # 质量设置
        quality_map = {
            '1080p': 'best[height<=1080]',
            '720p': 'best[height<=720]',
            '480p': 'best[height<=480]',
            'audio': 'bestaudio'
        }
        
        format_str = quality_map.get(quality, 'best[height<=1080]')
        cmd.extend(['-f', format_str])
        
        # 输出设置
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        cmd.extend(['-o', f'{output_dir}/%(title)s_{timestamp}.%(ext)s'])
        
        # Cookie处理 - 按成功率排序
        cookie_methods = [
            # 方法1: Chrome/Edge (成功率最高)
            ['--cookies-from-browser', 'chrome'],
            ['--cookies-from-browser', 'edge'],
            
            # 方法2: Safari (macOS用户)
            ['--cookies-from-browser', 'safari'],
            
            # 方法3: Firefox (独立引擎)
            ['--cookies-from-browser', 'firefox'],
            
            # 方法4: 其他浏览器
            ['--cookies-from-browser', 'chromium'],
            ['--cookies-from-browser', 'opera'],
            ['--cookies-from-browser', 'brave'],
            
            # 方法5: 使用保存的Cookie文件
            ['--cookies', self.cookie_file] if os.path.exists(self.cookie_file) else None,
            
            # 方法6: 无Cookie尝试
            []
        ]
        
        # 过滤掉None值
        cookie_methods = [method for method in cookie_methods if method is not None]
        
        return cmd, cookie_methods
    
    def download_douyin_video(self, url, quality='1080p', output_dir=None, progress_callback=None):
        """
        下载抖音视频，尝试多种Cookie方法
        """
        base_cmd, cookie_methods = self.get_douyin_download_command(url, quality, output_dir)
        
        for i, cookie_method in enumerate(cookie_methods):
            print(f"🔄 尝试方法 {i+1}/{len(cookie_methods)}: {cookie_method if cookie_method else '无Cookie'}")
            
            # 构建完整命令
            cmd = base_cmd + cookie_method + [url]
            
            try:
                # 执行下载
                result = self._run_download_command(cmd, progress_callback)
                
                if result.returncode == 0:
                    print(f"✅ 下载成功 (方法 {i+1})")
                    return True, "下载成功"
                else:
                    print(f"❌ 方法 {i+1} 失败: {result.stderr}")
                    
            except Exception as e:
                print(f"❌ 方法 {i+1} 异常: {e}")
                continue
        
        # 所有方法都失败
        return False, "所有下载方法都失败，可能需要手动获取Cookie"
    
    def _run_download_command(self, cmd, progress_callback=None):
        """执行下载命令"""
        return run_download_command(cmd, progress_callback)
    
    def save_cookies_from_browser(self, browser='chrome'):
        """
        从浏览器提取Cookie并保存
        """
        try:
            # 使用yt-dlp提取Cookie
            cmd = [
                'yt-dlp',
                '--cookies-from-browser', browser,
                '--print-to-file', '%(cookies)s', self.cookie_file,
                '--no-download',
                'https://www.douyin.com'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ 成功从{browser}提取Cookie")
                return True
            else:
                print(f"❌ 从{browser}提取Cookie失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 提取Cookie异常: {e}")
            return False
    
    def get_douyin_info(self, url):
        """
        获取抖音视频信息
        """
        try:
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                '--user-agent', self.headers['User-Agent'],
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                return {
                    'title': info.get('title', ''),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', ''),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'formats': len(info.get('formats', []))
                }
            else:
                return None
                
        except Exception as e:
            print(f"获取视频信息失败: {e}")
            return None
    
    def check_douyin_access(self):
        """
        检查抖音访问状态
        """
        try:
            test_url = "https://www.douyin.com/video/7000000000000000000"  # 测试URL
            cmd = [
                'yt-dlp',
                '--no-download',
                '--get-title',
                '--user-agent', self.headers['User-Agent'],
                test_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if "Fresh cookies" in result.stderr:
                return False, "需要新的Cookie"
            elif result.returncode == 0:
                return True, "访问正常"
            else:
                return False, "访问失败"
                
        except Exception as e:
            return False, f"检查失败: {e}"
    
    def get_solution_steps(self):
        """
        获取解决方案步骤
        """
        return [
            "🔧 抖音下载解决方案:",
            "",
            "方法1: 自动提取Cookie",
            "• 打开抖音网页版 (douyin.com)",
            "• 登录您的抖音账号",
            "• 程序会自动从浏览器提取Cookie",
            "",
            "方法2: 手动获取Cookie",
            "• 在浏览器中打开抖音网页",
            "• 按F12打开开发者工具",
            "• 刷新页面，在Network选项卡找到请求",
            "• 复制Cookie值到程序中",
            "",
            "方法3: 尝试不同的视频链接",
            "• 有些视频可能需要登录才能访问",
            "• 尝试其他公开的抖音视频",
            "",
            "💡 提示:",
            "• 确保网络连接稳定",
            "• 尝试使用VPN或代理",
            "• 有些视频可能有地区限制"
        ]

def main():
    """测试函数"""
    helper = DouyinHelper()
    
    # 测试URL
    test_url = "https://www.douyin.com/video/7521430870104870207"
    
    print("🔍 检查抖音访问状态...")
    accessible, message = helper.check_douyin_access()
    print(f"状态: {message}")
    
    if not accessible:
        print("\n".join(helper.get_solution_steps()))
        return
    
    print("\n📋 获取视频信息...")
    info = helper.get_douyin_info(test_url)
    if info:
        print(f"标题: {info['title']}")
        print(f"时长: {info['duration']}秒")
        print(f"上传者: {info['uploader']}")
    
    print("\n🚀 尝试下载...")
    success, message = helper.download_douyin_video(test_url)
    print(f"结果: {message}")

if __name__ == "__main__":
    main()