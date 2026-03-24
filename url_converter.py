#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URL格式转换器
处理各种不同格式的视频URL，转换为yt-dlp可识别的格式
"""

import re
import urllib.parse

class URLConverter:
    def __init__(self):
        self.supported_sites = {
            'douyin': self.convert_douyin_url,
            'bilibili': self.convert_bilibili_url,
            'youtube': self.convert_youtube_url,
            'tiktok': self.convert_tiktok_url
        }
    
    def detect_site(self, url):
        """检测URL来源网站"""
        if 'douyin.com' in url:
            return 'douyin'
        elif 'bilibili.com' in url:
            return 'bilibili'
        elif 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'tiktok.com' in url:
            return 'tiktok'
        else:
            return 'unknown'
    
    def convert_douyin_url(self, url):
        """转换抖音URL格式"""
        # 处理精选页面URL: https://www.douyin.com/jingxuan/film?modal_id=xxx
        if 'jingxuan' in url and 'modal_id=' in url:
            # 提取modal_id
            modal_id_match = re.search(r'modal_id=(\d+)', url)
            if modal_id_match:
                modal_id = modal_id_match.group(1)
                # 转换为标准抖音视频URL
                return f"https://www.douyin.com/video/{modal_id}"
        
        # 处理其他抖音URL格式
        patterns = [
            (r'https://www\.douyin\.com/user/[^/]+\?modal_id=(\d+)', 
             r'https://www.douyin.com/video/\1'),
            (r'https://www\.douyin\.com/discover\?modal_id=(\d+)', 
             r'https://www.douyin.com/video/\1'),
            (r'https://www\.douyin\.com/.*modal_id=(\d+)', 
             r'https://www.douyin.com/video/\1'),
        ]
        
        for pattern, replacement in patterns:
            match = re.search(pattern, url)
            if match:
                return re.sub(pattern, replacement, url)
        
        # 如果已经是标准格式，直接返回
        if '/video/' in url:
            return url
        
        return url
    
    def convert_bilibili_url(self, url):
        """转换B站URL格式"""
        # B站URL通常格式良好，但处理一些特殊情况
        if 'bilibili.com' in url:
            # 移除不必要的参数
            parsed = urllib.parse.urlparse(url)
            if parsed.query:
                # 保留重要参数，移除追踪参数
                query_params = urllib.parse.parse_qs(parsed.query)
                important_params = {}
                for key in ['p', 'part', 't', 'time']:
                    if key in query_params:
                        important_params[key] = query_params[key][0]
                
                if important_params:
                    new_query = urllib.parse.urlencode(important_params)
                    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
                else:
                    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        return url
    
    def convert_youtube_url(self, url):
        """转换YouTube URL格式"""
        # YouTube URL格式通常良好
        return url
    
    def convert_tiktok_url(self, url):
        """转换TikTok URL格式"""
        # TikTok URL格式通常良好
        return url
    
    def convert_url(self, url):
        """主要转换函数"""
        if not url or not url.startswith('http'):
            return url
        
        site = self.detect_site(url)
        
        if site in self.supported_sites:
            try:
                converted_url = self.supported_sites[site](url)
                if converted_url != url:
                    print(f"🔄 URL已转换: {url} -> {converted_url}")
                return converted_url
            except Exception as e:
                print(f"⚠️ URL转换失败: {e}")
                return url
        
        return url
    
    def is_supported_url(self, url):
        """检查URL是否被支持"""
        site = self.detect_site(url)
        return site != 'unknown'
    
    def get_download_command(self, url, quality='1080'):
        """获取下载命令"""
        converted_url = self.convert_url(url)
        site = self.detect_site(converted_url)
        
        commands = {
            'douyin': f'yt-dlp "{converted_url}"',
            'bilibili': f'yt-dlp -f "best[height<={quality}]" "{converted_url}"',
            'youtube': f'yt-dlp -f "best[height<={quality}][ext=mp4]" "{converted_url}"',
            'tiktok': f'yt-dlp "{converted_url}"'
        }
        
        return commands.get(site, f'yt-dlp "{converted_url}"')

def main():
    """测试函数"""
    converter = URLConverter()
    
    test_urls = [
        "https://www.douyin.com/jingxuan/film?modal_id=7521430870104870207",
        "https://www.douyin.com/user/123456789?modal_id=7521430870104870207",
        "https://www.douyin.com/video/7521430870104870207",
        "https://www.bilibili.com/video/BV1234567890?p=1&t=60",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.tiktok.com/@user/video/1234567890"
    ]
    
    for url in test_urls:
        print(f"\n原始URL: {url}")
        converted = converter.convert_url(url)
        print(f"转换后: {converted}")
        print(f"下载命令: {converter.get_download_command(converted)}")
        print("-" * 60)

if __name__ == "__main__":
    main()