#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书下载助手
解决小红书Cookie和访问问题
"""

import os
import subprocess
import json
import re
import time
from base_helper import run_download_command

class XiaohongshuHelper:
    def __init__(self):
        self.cookie_file = "xiaohongshu_cookies.txt"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def get_download_command(self, url, quality='1080p', output_dir=None):
        """
        生成小红书下载命令
        """
        if not output_dir:
            output_dir = os.path.expanduser("~/Downloads")
        
        # 基础命令
        cmd = [
            'yt-dlp',
            '--no-check-certificate',
            '--user-agent', self.headers['User-Agent'],
            '--referer', 'https://www.xiaohongshu.com/',
            '--add-header', 'Accept:' + self.headers['Accept'],
            '--add-header', 'Accept-Language:' + self.headers['Accept-Language'],
        ]
        
        # 质量设置 - 小红书通常只有一个质量，但保留此逻辑
        quality_map = {
            '1080p': 'best',
            '720p': 'best',
            '480p': 'best',
            'audio': 'bestaudio'
        }
        
        format_str = quality_map.get(quality, 'best')
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
    
    def download_video(self, url, quality='1080p', output_dir=None, progress_callback=None):
        """
        下载小红书视频，尝试多种Cookie方法
        """
        base_cmd, cookie_methods = self.get_download_command(url, quality, output_dir)
        
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

def main():
    """测试函数"""
    helper = XiaohongshuHelper()
    
    # 测试URL (示例)
    test_url = "https://www.xiaohongshu.com/explore/..."
    
    print("🚀 尝试下载...")
    # success, message = helper.download_video(test_url)
    # print(f"结果: {message}")

if __name__ == "__main__":
    main()
