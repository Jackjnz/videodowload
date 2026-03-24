#!/usr/bin/env python3
"""
Jack叔叔视频下载器 - 极简版 v2.6
类似Downie的最简设计，Web界面，一键打包
"""

import subprocess
import threading
import os
import sys
import time
import json
import uuid
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

# 导入URL转换器和抖音助手
try:
    from url_converter import URLConverter
except ImportError:
    URLConverter = None

try:
    from douyin_helper import DouyinHelper
except ImportError:
    DouyinHelper = None

try:
    from xiaohongshu_helper import XiaohongshuHelper
except ImportError:
    XiaohongshuHelper = None

app = Flask(__name__)

class UltraSimpleDownloader:
    def __init__(self):
        self.download_folder = os.path.expanduser("~/Downloads")
        self.download_queue = []  # 当前下载队列 (最多5个)
        self.download_history = []  # 下载历史 (最多20个)
        self.active_downloads = 0  # 当前活跃下载数
        self.max_concurrent = 3  # 最大并发下载数
        self.max_queue = 5  # 最大队列长度
        self.max_history = 20  # 最大历史记录数
        self.history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "download_history.json")
        self.load_history()
        self.is_downloading = False  # 保持向后兼容
        self.active_processes = {}  # item_id -> subprocess.Popen，用于取消时终止进程
        self._lock = threading.Lock()  # 线程安全锁
        self._cookie_browser = None  # 缓存可用的 cookie 浏览器（'chrome'/'safari'/False）

        # 初始化URL转换器和抖音助手
        self.url_converter = URLConverter() if URLConverter else None
        self.douyin_helper = DouyinHelper() if DouyinHelper else None
        self.xiaohongshu_helper = XiaohongshuHelper() if XiaohongshuHelper else None
        
    def download_video(self, url, quality="1080p", progress_callback=None, item_id=None):
        """下载视频"""
        # 使用URL转换器处理URL
        if self.url_converter:
            url = self.url_converter.convert_url(url)
        
        # 检查是否为抖音URL，使用专门的抖音助手
        if 'douyin.com' in url and self.douyin_helper:
            return self.douyin_helper.download_douyin_video(url, quality, self.download_folder, progress_callback)

        # 检查是否为小红书URL，使用专门的小红书助手
        if 'xiaohongshu.com' in url and self.xiaohongshu_helper:
            return self.xiaohongshu_helper.download_video(url, quality, self.download_folder, progress_callback)
        
        # 优化的格式字符串，支持更高分辨率
        format_map = {
            "8K/4320p": "(bestvideo[height<=4320]+bestaudio/best[height<=4320])",
            "4K/2160p": "(bestvideo[height<=2160]+bestaudio/best[height<=2160])",
            "2K/1440p": "(bestvideo[height<=1440]+bestaudio/best[height<=1440])", 
            "1080p": "(bestvideo[height<=1080]+bestaudio/best[height<=1080])",
            "720p": "(bestvideo[height<=720]+bestaudio/best[height<=720])",
            "480p": "(bestvideo[height<=480]+bestaudio/best[height<=480])",
            "audio": "bestaudio/best"
        }
        
        format_str = format_map.get(quality, "(bestvideo[height<=1080]+bestaudio/best[height<=1080])")
        
        # 使用时间戳避免文件名冲突
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        cmd = [
            "yt-dlp",
            "--ignore-config",
            "--no-check-certificate",
            "--js-runtimes", "node",
            "-f", format_str,
            "-o", f"{self.download_folder}/%(title)s_{timestamp}.%(ext)s",
            "--merge-output-format", "mp4",
            "--prefer-free-formats",
            "--newline",  # 每个进度更新都在新一行
        ]

        # YouTube 需要 tv client 来绕过 PO Token 要求
        if 'youtube.com' in url or 'youtu.be' in url:
            cmd += ["--extractor-args", "youtube:player_client=tv"]

        cmd.append(url)
        
        # 智能 cookie 策略：缓存上次成功的浏览器，避免每次串行尝试
        if self._cookie_browser is None:
            # 首次：依次尝试 chrome → safari → 无cookie
            for browser in ['chrome', 'safari']:
                try:
                    result = self._run_with_progress(cmd + ["--cookies-from-browser", browser], progress_callback, item_id)
                    if result.returncode == 0:
                        self._cookie_browser = browser
                        print(f"✅ Cookie 缓存: 使用 {browser}")
                        return True, ""
                except Exception:
                    continue
            # 都失败了，不用 cookie
            self._cookie_browser = False
            result = self._run_with_progress(cmd, progress_callback, item_id)
        elif self._cookie_browser:
            # 已缓存浏览器
            try:
                result = self._run_with_progress(cmd + ["--cookies-from-browser", self._cookie_browser], progress_callback, item_id)
            except Exception:
                result = self._run_with_progress(cmd, progress_callback, item_id)
        else:
            # 缓存了"无cookie"
            result = self._run_with_progress(cmd, progress_callback, item_id)

        return result.returncode == 0, result.stderr if result.stderr else "下载失败"
    
    def _run_with_progress(self, cmd, progress_callback, item_id=None):
        """运行命令并解析进度"""
        import re

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, universal_newlines=True)

        # 保存进程引用，用于取消时终止
        if item_id:
            self.active_processes[item_id] = process

        # 用于解析进度的正则表达式
        progress_pattern = re.compile(r'(\d+\.?\d*)%')
        speed_pattern = re.compile(r'at\s+([\d.]+\s*\w+/s)')

        output = []
        for line in iter(process.stdout.readline, ''):
            output.append(line)

            # 解析进度和速度
            if progress_callback:
                match = progress_pattern.search(line)
                if match:
                    progress = float(match.group(1))
                    speed_match = speed_pattern.search(line)
                    speed = speed_match.group(1) if speed_match else None
                    progress_callback(progress, speed)

        process.wait()

        # 清理进程引用
        if item_id and item_id in self.active_processes:
            del self.active_processes[item_id]

        # 模拟 subprocess.run 的返回结果
        class Result:
            def __init__(self, returncode, stdout, stderr):
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr

        return Result(process.returncode, ''.join(output), ''.join(output))
    
    def load_history(self):
        """加载历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.download_history = json.load(f)
        except Exception as e:
            print(f"加载历史记录失败: {e}")
            self.download_history = []
    
    def save_history(self):
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.download_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
    
    def add_to_history(self, item):
        """添加到历史记录"""
        # 检查是否已存在
        for i, h in enumerate(self.download_history):
            if h['url'] == item['url']:
                self.download_history[i] = item
                self.save_history()
                return
        
        # 添加新记录
        self.download_history.insert(0, item)
        
        # 保持最大记录数
        if len(self.download_history) > self.max_history:
            self.download_history = self.download_history[:self.max_history]
        
        self.save_history()
    
    def add_to_queue(self, url, quality, allow_duplicate=False):
        """添加到下载队列"""
        with self._lock:
            # 检查队列是否已满
            if len(self.download_queue) >= self.max_queue:
                return False, "下载队列已满，请等待当前下载完成"

            # 检查是否已在队列中（只在非重复模式下检查）
            if not allow_duplicate:
                for item in self.download_queue:
                    if item['url'] == url:
                        return False, "该视频已在下载队列中"

            # 创建下载项
            item = {
                'id': str(uuid.uuid4()),
                'url': url,
                'quality': quality,
                'status': 'waiting',
                'title': '',
                'progress': 0,
                'speed': '',
                'added_time': datetime.now().isoformat(),
                'error': ''
            }

            self.download_queue.append(item)

        # 如果没有达到并发限制，立即开始下载
        if self.active_downloads < self.max_concurrent:
            self.start_next_download()

        return True, "已添加到下载队列"
    
    def start_next_download(self):
        """开始下一个下载"""
        if self.active_downloads >= self.max_concurrent:
            return
        
        # 找到下一个等待的任务
        for item in self.download_queue:
            if item['status'] == 'waiting':
                self.start_download_task(item)
                break
    
    def start_download_task(self, item):
        """开始下载任务"""
        item['status'] = 'downloading'
        self.active_downloads += 1
        
        def download_thread():
            try:
                # 获取视频标题
                if item['status'] != 'cancelled':
                    item['title'] = self.get_video_title(item['url']) or item['url'][:50] + "..."
                
                # 检查是否被取消
                if item['status'] == 'cancelled':
                    item['status'] = 'failed'
                    item['error'] = '用户取消下载'
                else:
                    # 下载视频，传入进度回调
                    def update_progress(progress, speed=None):
                        if item['status'] != 'cancelled':
                            item['progress'] = progress
                            if speed:
                                item['speed'] = speed

                    success, message = self.download_video(item['url'], item['quality'], update_progress, item['id'])
                    
                    if success:
                        item['status'] = 'completed'
                        item['progress'] = 100
                    else:
                        item['status'] = 'failed'
                        item['error'] = message
                
                # 添加到历史记录
                history_item = {
                    'id': item['id'],
                    'url': item['url'],
                    'quality': item['quality'],
                    'title': item['title'],
                    'status': item['status'],
                    'download_time': datetime.now().isoformat(),
                    'error': item.get('error', '')
                }
                self.add_to_history(history_item)
                
                # 从队列中移除
                self.download_queue = [i for i in self.download_queue if i['id'] != item['id']]
                
                self.active_downloads -= 1
                
                # 开始下一个下载
                self.start_next_download()
                
            except Exception as e:
                item['status'] = 'failed'
                item['error'] = str(e)
                self.active_downloads -= 1
                self.start_next_download()
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def get_video_title(self, url):
        """获取视频标题"""
        try:
            cmd = [
                "yt-dlp", "--ignore-config", "--js-runtimes", "node",
                "--cookies-from-browser", "chrome",
                "--get-title", url
            ]
            if 'youtube.com' in url or 'youtu.be' in url:
                cmd = cmd[:-1] + ["--extractor-args", "youtube:player_client=tv", url]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)

            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            print(f"⚠️ 获取标题失败: {e}")
        return ""
    
    def remove_from_queue(self, item_id):
        """从队列中移除"""
        for item in self.download_queue:
            if item['id'] == item_id:
                if item['status'] == 'waiting':
                    self.download_queue.remove(item)
                    return True, "已从队列中移除"
                elif item['status'] == 'downloading':
                    item['status'] = 'cancelled'
                    # 终止 yt-dlp 子进程
                    process = self.active_processes.get(item_id)
                    if process:
                        try:
                            process.terminate()
                        except Exception:
                            pass
                    return True, "下载已取消"
        return False, "无法移除该项目"
    
    def retry_from_history(self, item_id):
        """从历史记录重试"""
        for item in self.download_history:
            if item['id'] == item_id:
                # 允许重复，因为这是重新下载
                return self.add_to_queue(item['url'], item['quality'], allow_duplicate=True)
        return False, "历史记录中未找到该项目"
    
    def remove_from_history(self, item_id):
        """从历史记录中删除项目"""
        for i, item in enumerate(self.download_history):
            if item['id'] == item_id:
                self.download_history.pop(i)
                self.save_history()
                return True, "已从历史记录中删除"
        return False, "历史记录中未找到该项目"
    
    def clear_history(self):
        """清空所有历史记录"""
        self.download_history = []
        self.save_history()
        return True, "已清空所有历史记录"
    
    def get_status(self):
        """获取当前状态"""
        return {
            'queue': self.download_queue,
            'history': self.download_history,
            'active_downloads': self.active_downloads,
            'queue_slots': self.max_queue - len(self.download_queue)
        }

downloader = UltraSimpleDownloader()

# 极简HTML模板
TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jack叔叔视频下载器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            max-width: 800px;
            width: 100%;
            text-align: center;
        }
        
        .title {
            color: #333;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 30px;
        }
        
        .input-group {
            margin-bottom: 25px;
        }
        
        .input-group label {
            display: block;
            color: #666;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .url-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e8ed;
            border-radius: 12px;
            font-size: 16px;
            transition: border-color 0.3s;
            resize: vertical;
            font-family: inherit;
        }
        
        .url-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .quality-select {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e8ed;
            border-radius: 12px;
            font-size: 16px;
            background: white;
            cursor: pointer;
        }
        
        .download-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 18px 40px;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
            margin-top: 10px;
        }
        
        .download-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .download-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            font-weight: 500;
            display: none;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .status.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .spinner {
            display: none;
            margin: 20px auto;
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .help {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 14px;
            line-height: 1.6;
        }
        
        .queue-history {
            margin-top: 30px;
            display: flex;
            gap: 20px;
            justify-content: space-between;
        }
        
        .queue-section, .history-section {
            flex: 1;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: left;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .queue-item, .history-item {
            background: white;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .item-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
            font-size: 14px;
        }
        
        .item-meta {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }
        
        .item-actions {
            display: flex;
            gap: 5px;
            justify-content: flex-end;
        }
        
        .btn-small {
            padding: 4px 8px;
            font-size: 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .btn-remove {
            background: #dc3545;
            color: white;
        }
        
        .btn-remove:hover {
            background: #c82333;
        }
        
        .btn-retry {
            background: #007bff;
            color: white;
        }
        
        .btn-retry:hover {
            background: #0056b3;
        }
        
        .btn-cancel {
            background: #ffc107;
            color: #212529;
        }
        
        .btn-cancel:hover {
            background: #e0a800;
        }
        
        .btn-copy {
            background: #28a745;
            color: white;
        }
        
        .btn-copy:hover {
            background: #1e7e34;
        }
        
        .btn-redownload {
            background: #17a2b8;
            color: white;
        }
        
        .btn-redownload:hover {
            background: #138496;
        }
        
        .btn-delete {
            background: #dc3545;
            color: white;
        }
        
        .btn-delete:hover {
            background: #c82333;
        }
        
        .btn-clear-all {
            background: #6c757d;
            color: white;
            font-size: 10px;
            padding: 2px 6px;
        }
        
        .btn-clear-all:hover {
            background: #5a6268;
        }
        
        .status-badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status-waiting {
            background: #ffeaa7;
            color: #d63031;
        }
        
        .status-downloading {
            background: #74b9ff;
            color: #0984e3;
        }
        
        .status-completed {
            background: #00b894;
            color: white;
        }
        
        .status-failed {
            background: #d63031;
            color: white;
        }
        
        .status-cancelled {
            background: #6c757d;
            color: white;
        }
        
        .empty-state {
            text-align: center;
            color: #999;
            font-style: italic;
            padding: 20px;
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background-color: #e9ecef;
            border-radius: 3px;
            margin: 5px 0;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #007bff, #28a745);
            transition: width 0.3s ease;
            border-radius: 3px;
        }
        
        .progress-text {
            font-size: 11px;
            color: #666;
            margin-top: 2px;
        }
        
        @media (max-width: 768px) {
            .queue-history {
                flex-direction: column;
            }
        }
        
        @media (max-width: 480px) {
            .container {
                padding: 30px 20px;
            }

            .title {
                font-size: 24px;
            }
        }

        @media (prefers-color-scheme: dark) {
            body {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            }
            .container {
                background: #1e1e2e;
                color: #cdd6f4;
            }
            .title { color: #cdd6f4; }
            .url-input, .quality-select {
                background: #313244;
                border-color: #45475a;
                color: #cdd6f4;
            }
            .url-input:focus { border-color: #89b4fa; }
            .queue-section, .history-section { background: #181825; }
            .section-title { color: #cdd6f4; }
            .queue-item, .history-item {
                background: #313244;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            .item-title { color: #cdd6f4; }
            .item-meta { color: #a6adc8; }
            .help { color: #a6adc8; border-top-color: #45475a; }
            .input-group label { color: #a6adc8; }
            .empty-state { color: #6c7086; }
            .progress-text { color: #a6adc8; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">🎬 Jack叔叔视频下载器 <span style="font-size:14px;color:#999;font-weight:400;">v2.6</span></h1>
        
        <div class="input-group">
            <label for="url">视频链接（支持多行粘贴，每行一个链接）</label>
            <textarea id="url" class="url-input" rows="3" placeholder="粘贴YouTube、B站等视频链接...&#10;支持多行粘贴批量下载"></textarea>
        </div>
        
        <div class="input-group">
            <label for="quality">画质选择</label>
            <select id="quality" class="quality-select">
                <option value="8K/4320p">8K/4320p (至尊超清)</option>
                <option value="4K/2160p">4K/2160p (超高清)</option>
                <option value="2K/1440p">2K/1440p (高清)</option>
                <option value="1080p" selected>1080p (推荐)</option>
                <option value="720p">720p</option>
                <option value="480p">480p</option>
                <option value="audio">仅音频</option>
            </select>
        </div>
        
        <button id="downloadBtn" class="download-btn" onclick="startDownload()">
            开始下载
        </button>
        
        <div id="spinner" class="spinner"></div>
        <div id="status" class="status"></div>
        
        <div class="queue-history">
            <div class="queue-section">
                <div class="section-title">📥 当前队列 (0/5)</div>
                <div id="queue-list" class="empty-state">暂无下载任务</div>
            </div>
            
            <div class="history-section">
                <div class="section-title">
                    📋 下载历史 (0/20)
                    <button class="btn-small btn-clear-all" onclick="clearAllHistory()" style="float: right; margin-left: 10px;">清空全部</button>
                </div>
                <div id="history-list" class="empty-state">暂无历史记录</div>
            </div>
        </div>
        
        <div class="help">
            <strong>💡 使用提示:</strong><br>
            • 支持 YouTube、B站、抖音等主流网站<br>
            • 首次使用会自动安装必要组件<br>
            • 下载文件保存在 Downloads 文件夹<br>
            • 遇到问题请检查网络连接<br>
            • <button onclick="checkDouyinHelp()" style="background:none;border:none;color:#007bff;cursor:pointer;text-decoration:underline;">抖音下载问题？点击获取帮助</button>
        </div>
        
        <!-- 抖音帮助弹窗 -->
        <div id="douyinHelpModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:1000;">
            <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); background:white; padding:30px; border-radius:10px; max-width:600px; max-height:80vh; overflow-y:auto;">
                <h3>🔧 抖音下载解决方案</h3>
                <div id="douyinHelpContent"></div>
                <div style="margin-top:20px;">
                    <button onclick="extractDouyinCookie('chrome')" style="margin-right:10px; padding:8px 16px; background:#007bff; color:white; border:none; border-radius:5px;">从Chrome提取Cookie</button>
                    <button onclick="extractDouyinCookie('safari')" style="margin-right:10px; padding:8px 16px; background:#007bff; color:white; border:none; border-radius:5px;">从Safari提取Cookie</button>
                    <button onclick="extractDouyinCookie('firefox')" style="margin-right:10px; padding:8px 16px; background:#007bff; color:white; border:none; border-radius:5px;">从Firefox提取Cookie</button>
                    <button onclick="closeDouyinHelp()" style="padding:8px 16px; background:#6c757d; color:white; border:none; border-radius:5px;">关闭</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = `status ${type}`;
            status.style.display = 'block';
        }
        
        function hideStatus() {
            document.getElementById('status').style.display = 'none';
        }
        
        function showSpinner() {
            document.getElementById('spinner').style.display = 'block';
        }
        
        function hideSpinner() {
            document.getElementById('spinner').style.display = 'none';
        }
        
        function startDownload() {
            const rawInput = document.getElementById('url').value.trim();
            const quality = document.getElementById('quality').value;
            const btn = document.getElementById('downloadBtn');

            if (!rawInput) {
                showStatus('请输入视频链接', 'error');
                return;
            }

            // 支持多行批量粘贴
            const urls = rawInput.split(/[\\n\\r]+/).map(u => u.trim()).filter(u => u && u.startsWith('http'));

            if (urls.length === 0) {
                showStatus('请输入有效的视频链接（以 http 开头）', 'error');
                return;
            }

            btn.disabled = true;
            btn.textContent = '添加中...';
            showSpinner();
            hideStatus();

            // 逐个添加
            const promises = urls.map(url =>
                fetch('/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url, quality: quality })
                }).then(r => r.json())
            );

            Promise.all(promises).then(results => {
                btn.disabled = false;
                btn.textContent = '开始下载';
                hideSpinner();

                const successes = results.filter(r => r.success).length;
                const failures = results.filter(r => !r.success);

                if (successes > 0) {
                    document.getElementById('url').value = '';
                    if (failures.length > 0) {
                        showStatus(`✅ 已添加 ${successes} 个，${failures.length} 个失败: ${failures[0].message}`, 'info');
                    } else {
                        showStatus(`✅ 已添加 ${successes} 个到下载队列`, 'success');
                    }
                    updateQueueAndHistory();
                } else {
                    showStatus('❌ 添加失败: ' + results[0].message, 'error');
                }
            }).catch(error => {
                btn.disabled = false;
                btn.textContent = '开始下载';
                hideSpinner();
                showStatus('❌ 添加失败: ' + error, 'error');
            });
        }
        
        // 状态缓存，避免重复请求
        let lastQueueState = null;
        let lastHistoryState = null;
        
        function updateQueueAndHistory() {
            // 更新队列
            fetch('/queue')
                .then(response => response.json())
                .then(data => {
                    const currentState = JSON.stringify(data);
                    if (currentState !== lastQueueState) {
                        updateQueueDisplay(data);
                        lastQueueState = currentState;
                    }
                })
                .catch(error => console.error('更新队列失败:', error));
            
            // 更新历史
            fetch('/history')
                .then(response => response.json())
                .then(data => {
                    const currentState = JSON.stringify(data.history);
                    if (currentState !== lastHistoryState) {
                        checkForNewCompletions(data.history);
                        updateHistoryDisplay(data.history);
                        lastHistoryState = currentState;
                    }
                })
                .catch(error => console.error('更新历史失败:', error));
        }
        
        function updateQueueDisplay(data) {
            const queueList = document.getElementById('queue-list');
            const queueTitle = document.querySelector('.queue-section .section-title');
            
            queueTitle.textContent = `📥 当前队列 (${data.queue.length}/${data.queue_slots + data.queue.length})`;
            
            // 检查是否有正在下载的任务
            const hasDownloading = data.queue.some(item => item.status === 'downloading');
            
            // 只有在真正有下载任务时才开启快速更新
            if (hasDownloading) {
                startProgressUpdates();
            } else {
                // 没有正在下载的任务时切换到慢速模式
                stopProgressUpdates();
            }
            
            if (data.queue.length === 0) {
                queueList.innerHTML = '<div class="empty-state">暂无下载任务</div>';
                return;
            }
            
            queueList.innerHTML = data.queue.map(item => `
                <div class="queue-item">
                    <div class="item-title">${item.title || '获取标题中...'}</div>
                    <div class="item-meta">
                        <span class="status-badge status-${item.status}">${getStatusText(item.status)}</span>
                        <span>${item.quality}</span>
                    </div>
                    ${item.status === 'downloading' ? `
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${item.progress || 0}%"></div>
                        </div>
                        <div class="progress-text">${Math.round(item.progress || 0)}%${item.speed ? ' · ' + item.speed : ''}</div>
                    ` : ''}
                    ${item.error ? `<div style="color: red; font-size: 12px;">${item.error}</div>` : ''}
                    <div class="item-actions">
                        ${item.status === 'waiting' ? `<button class="btn-small btn-remove" onclick="removeFromQueue('${item.id}')">删除</button>` : ''}
                        ${item.status === 'downloading' ? `<button class="btn-small btn-cancel" onclick="cancelDownload('${item.id}')">取消</button>` : ''}
                        ${item.status === 'failed' ? `<button class="btn-small btn-remove" onclick="removeFromQueue('${item.id}')">删除</button>` : ''}
                        ${item.status === 'failed' ? `<button class="btn-small btn-retry" onclick="retryFromQueue('${item.id}')">重试</button>` : ''}
                    </div>
                </div>
            `).join('');
        }
        
        function updateHistoryDisplay(history) {
            const historyList = document.getElementById('history-list');
            const historyTitle = document.querySelector('.history-section .section-title');
            
            // 保持清空全部按钮
            const clearButton = historyTitle.querySelector('.btn-clear-all');
            historyTitle.innerHTML = `📋 下载历史 (${history.length}/20)`;
            if (clearButton) {
                historyTitle.appendChild(clearButton);
            } else {
                historyTitle.innerHTML += '<button class="btn-small btn-clear-all" onclick="clearAllHistory()" style="float: right; margin-left: 10px;">清空全部</button>';
            }
            
            if (history.length === 0) {
                historyList.innerHTML = '<div class="empty-state">暂无历史记录</div>';
                return;
            }
            
            historyList.innerHTML = history.slice(0, 10).map(item => `
                <div class="history-item">
                    <div class="item-title">${item.title || 'Unknown'}</div>
                    <div class="item-meta">
                        <span class="status-badge status-${item.status}">${getStatusText(item.status)}</span>
                        <span>${item.quality}</span>
                        <span>${formatDate(item.download_time)}</span>
                    </div>
                    ${item.error ? `<div style="color: red; font-size: 12px;">${item.error}</div>` : ''}
                    <div class="item-actions">
                        <button class="btn-small btn-copy" onclick="copyUrl('${item.id}')">复制地址</button>
                        ${item.status === 'failed' || item.status === 'cancelled' ? `<button class="btn-small btn-retry" onclick="retryDownload('${item.id}')">重试</button>` : ''}
                        ${item.status === 'completed' ? `<button class="btn-small btn-redownload" onclick="retryDownload('${item.id}')">重新下载</button>` : ''}
                        <button class="btn-small btn-delete" onclick="deleteHistoryItem('${item.id}')">删除</button>
                    </div>
                </div>
            `).join('');
        }
        
        function getStatusText(status) {
            const statusMap = {
                'waiting': '等待中',
                'downloading': '下载中',
                'completed': '已完成',
                'failed': '失败',
                'cancelled': '已取消'
            };
            return statusMap[status] || status;
        }
        
        function formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleString('zh-CN', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        
        function removeFromQueue(id) {
            fetch('/remove', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id: id })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateQueueAndHistory();
                } else {
                    showStatus('移除失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showStatus('移除失败: ' + error, 'error');
            });
        }
        
        function retryDownload(id) {
            // 检查是否是重复下载
            if (confirm('该视频已下载过，确定要重新下载吗？\\n\\n选择确定：重新下载\\n选择取消：删除历史记录')) {
                fetch('/retry', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ id: id })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showStatus('✅ 已重新添加到下载队列', 'success');
                        updateQueueAndHistory();
                    } else {
                        showStatus('重试失败: ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    showStatus('重试失败: ' + error, 'error');
                });
            } else {
                deleteHistoryItem(id);
            }
        }

        function retryFromQueue(id) {
            fetch('/remove', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id: id, action: 'retry' })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStatus('✅ 已重新添加到下载队列', 'success');
                    updateQueueAndHistory();
                } else {
                    showStatus('重试失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showStatus('重试失败: ' + error, 'error');
            });
        }
        
        function cancelDownload(id) {
            fetch('/remove', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id: id })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStatus('✅ 下载已取消', 'success');
                    updateQueueAndHistory();
                } else {
                    showStatus('取消失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showStatus('取消失败: ' + error, 'error');
            });
        }
        
        function copyUrl(id) {
            fetch('/copy_url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id: id })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 复制到剪贴板
                    navigator.clipboard.writeText(data.url).then(() => {
                        showStatus('✅ 地址已复制到剪贴板', 'success');
                    }).catch(() => {
                        // 降级方案：显示地址让用户手动复制
                        prompt('复制下面的地址:', data.url);
                    });
                } else {
                    showStatus('复制失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showStatus('复制失败: ' + error, 'error');
            });
        }
        
        function deleteHistoryItem(id) {
            if (!confirm('确定要删除这个历史记录吗？')) {
                return;
            }
            
            fetch('/delete_history', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id: id })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStatus('✅ 已删除历史记录', 'success');
                    updateQueueAndHistory();
                } else {
                    showStatus('删除失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showStatus('删除失败: ' + error, 'error');
            });
        }
        
        function clearAllHistory() {
            if (!confirm('确定要清空所有历史记录吗？此操作不可恢复！')) {
                return;
            }
            
            fetch('/clear_history', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStatus('✅ 已清空所有历史记录', 'success');
                    updateQueueAndHistory();
                } else {
                    showStatus('清空失败: ' + data.message, 'error');
                }
            })
            .catch(error => {
                showStatus('清空失败: ' + error, 'error');
            });
        }
        
        // Ctrl+Enter 下载（textarea 里普通回车是换行）
        document.getElementById('url').addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                startDownload();
            }
        });

        // 请求通知权限
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }

        // 跟踪已知完成项，用于检测新完成
        let knownCompletedIds = new Set();
        function checkForNewCompletions(history) {
            if (!('Notification' in window) || Notification.permission !== 'granted') return;
            for (const item of history) {
                if (item.status === 'completed' && !knownCompletedIds.has(item.id)) {
                    knownCompletedIds.add(item.id);
                    new Notification('下载完成', {
                        body: item.title || '视频下载完成',
                        icon: '🎬'
                    });
                }
            }
            // 也记录非completed的，避免旧历史触发通知
            for (const item of history) {
                knownCompletedIds.add(item.id);
            }
        }
        
        // 智能轮询系统全局变量
        let baseUpdateInterval = null;
        let progressUpdateInterval = null;
        let currentUpdateFrequency = null; // null, 'slow', 'fast'

        function startSlowUpdates() {
            if (currentUpdateFrequency === 'slow') return; // 已经是慢速模式，不重复设置
            
            if (baseUpdateInterval) clearInterval(baseUpdateInterval);
            if (progressUpdateInterval) clearInterval(progressUpdateInterval);
            
            // 每30秒更新一次（无下载任务时）
            baseUpdateInterval = setInterval(updateQueueAndHistory, 30000);
            currentUpdateFrequency = 'slow';
            console.log('✨ 切换到慢速模式: 30秒更新');
        }
        
        function startFastUpdates() {
            if (currentUpdateFrequency === 'fast') return; // 已经是快速模式，不重复设置
            
            if (baseUpdateInterval) clearInterval(baseUpdateInterval);
            if (progressUpdateInterval) clearInterval(progressUpdateInterval);
            
            // 每2秒更新一次（有下载任务时）
            progressUpdateInterval = setInterval(updateQueueAndHistory, 2000);
            currentUpdateFrequency = 'fast';
            console.log('⚡ 切换到快速模式: 2秒更新');
        }
        
        function startProgressUpdates() {
            if (currentUpdateFrequency !== 'fast') {
                startFastUpdates();
            }
        }
        
        function stopProgressUpdates() {
            if (currentUpdateFrequency !== 'slow') {
                startSlowUpdates();
            }
        }
        
        // 抖音帮助相关函数
        function checkDouyinHelp() {
            fetch('/douyin_help')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        let content = `
                            <div style="margin-bottom:15px;">
                                <strong>状态:</strong> ${data.status}<br>
                                <strong>访问状态:</strong> ${data.accessible ? '✅ 正常' : '❌ 需要处理'}
                            </div>
                            <div style="background:#f8f9fa; padding:15px; border-radius:5px; font-family:monospace; font-size:14px; line-height:1.5;">
                                ${data.solutions.join('<br>')}
                            </div>
                        `;
                        document.getElementById('douyinHelpContent').innerHTML = content;
                        document.getElementById('douyinHelpModal').style.display = 'block';
                    } else {
                        showStatus('获取抖音帮助失败: ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    showStatus('获取抖音帮助失败: ' + error, 'error');
                });
        }
        
        function extractDouyinCookie(browser) {
            showStatus('正在从' + browser + '提取Cookie...', 'info');
            
            fetch('/douyin_cookie', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    browser: browser
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStatus('✅ ' + data.message, 'success');
                    closeDouyinHelp();
                } else {
                    showStatus('❌ ' + data.message, 'error');
                }
            })
            .catch(error => {
                showStatus('提取Cookie失败: ' + error, 'error');
            });
        }
        
        function closeDouyinHelp() {
            document.getElementById('douyinHelpModal').style.display = 'none';
        }
        
        // 页面加载完成后检查yt-dlp和更新队列历史
        window.onload = function() {
            fetch('/check')
                .then(response => response.json())
                .then(data => {
                    if (!data.ready) {
                        showStatus('⚠️ 首次使用需要安装下载组件，请稍候...', 'info');
                    }
                });
            
            // 初始化队列和历史显示
            updateQueueAndHistory();
            
            // 默认开始慢速更新
            startSlowUpdates();
            
            // 页面可见性检测，如果页面不可见则停止更新
            document.addEventListener('visibilitychange', function() {
                if (document.hidden) {
                    // 页面隐藏时停止所有更新
                    if (baseUpdateInterval) clearInterval(baseUpdateInterval);
                    if (progressUpdateInterval) clearInterval(progressUpdateInterval);
                    console.log('😴 页面隐藏，停止轮询');
                } else {
                    // 页面显示时恢复更新
                    console.log('😊 页面显示，恢复轮询');
                    updateQueueAndHistory(); // 立即更新一次
                    startSlowUpdates(); // 恢复慢速模式
                }
            });
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE)

@app.route('/check')
def check():
    """检查yt-dlp是否可用"""
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        return jsonify({"ready": True})
    except Exception:
        return jsonify({"ready": False})

@app.route('/download', methods=['POST'])
def download():
    """添加视频到下载队列"""
    data = request.json
    url = data.get('url', '').strip()
    quality = data.get('quality', '1080p')
    
    if not url:
        return jsonify({"success": False, "message": "URL不能为空"})
    
    success, message = downloader.add_to_queue(url, quality)
    return jsonify({"success": success, "message": message})

@app.route('/queue')
def get_queue():
    """获取当前下载队列"""
    return jsonify(downloader.get_status())

@app.route('/history')
def get_history():
    """获取下载历史"""
    return jsonify({"history": downloader.download_history})

@app.route('/remove', methods=['POST'])
def remove_from_queue():
    """从队列中移除项目"""
    data = request.json
    item_id = data.get('id')
    action = data.get('action', 'remove')
    
    if not item_id:
        return jsonify({"success": False, "message": "ID不能为空"})
    
    if action == 'retry':
        # 先移除失败的项目，然后重新添加
        for item in downloader.download_queue:
            if item['id'] == item_id and item['status'] == 'failed':
                success, message = downloader.add_to_queue(item['url'], item['quality'], allow_duplicate=True)
                if success:
                    downloader.download_queue = [i for i in downloader.download_queue if i['id'] != item_id]
                    return jsonify({"success": True, "message": "已重新添加到队列"})
                else:
                    return jsonify({"success": False, "message": message})
        return jsonify({"success": False, "message": "队列中未找到失败的项目"})
    else:
        success, message = downloader.remove_from_queue(item_id)
        return jsonify({"success": success, "message": message})

@app.route('/retry', methods=['POST'])
def retry_download():
    """重新下载历史记录中的项目"""
    data = request.json
    item_id = data.get('id')
    
    if not item_id:
        return jsonify({"success": False, "message": "ID不能为空"})
    
    success, message = downloader.retry_from_history(item_id)
    return jsonify({"success": success, "message": message})

@app.route('/copy_url', methods=['POST'])
def copy_url():
    """获取历史记录中项目的URL用于复制"""
    data = request.json
    item_id = data.get('id')
    
    if not item_id:
        return jsonify({"success": False, "message": "ID不能为空"})
    
    for item in downloader.download_history:
        if item['id'] == item_id:
            return jsonify({"success": True, "url": item['url']})
    
    return jsonify({"success": False, "message": "历史记录中未找到该项目"})

@app.route('/delete_history', methods=['POST'])
def delete_history():
    """从历史记录中删除项目"""
    data = request.json
    item_id = data.get('id')
    
    if not item_id:
        return jsonify({"success": False, "message": "ID不能为空"})
    
    success, message = downloader.remove_from_history(item_id)
    return jsonify({"success": success, "message": message})

@app.route('/clear_history', methods=['POST'])
def clear_all_history():
    """清空所有历史记录"""
    success, message = downloader.clear_history()
    return jsonify({"success": success, "message": message})

@app.route('/douyin_help', methods=['GET'])
def douyin_help():
    """获取抖音下载帮助信息"""
    if not downloader.douyin_helper:
        return jsonify({"success": False, "message": "抖音助手未初始化"})
    
    # 检查抖音访问状态
    accessible, status_message = downloader.douyin_helper.check_douyin_access()
    
    return jsonify({
        "success": True,
        "accessible": accessible,
        "status": status_message,
        "solutions": downloader.douyin_helper.get_solution_steps()
    })

@app.route('/douyin_cookie', methods=['POST'])
def douyin_cookie():
    """从浏览器提取抖音Cookie"""
    if not downloader.douyin_helper:
        return jsonify({"success": False, "message": "抖音助手未初始化"})
    
    data = request.json
    browser = data.get('browser', 'chrome')
    
    success = downloader.douyin_helper.save_cookies_from_browser(browser)
    
    if success:
        return jsonify({"success": True, "message": f"成功从{browser}提取Cookie"})
    else:
        return jsonify({"success": False, "message": f"从{browser}提取Cookie失败"})

def check_and_install_yt_dlp():
    """检查并安装yt-dlp，启动时自动更新"""
    try:
        result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True, check=True)
        current_version = result.stdout.strip()
        print(f"✅ yt-dlp 已就绪 (v{current_version})")

        # 后台自动更新，不阻塞启动
        def auto_update():
            try:
                print("🔄 检查 yt-dlp 更新...")
                up = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--user", "--upgrade", "yt-dlp"],
                    capture_output=True, text=True, timeout=60
                )
                if up.returncode == 0:
                    new_result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
                    new_version = new_result.stdout.strip()
                    if new_version != current_version:
                        print(f"✅ yt-dlp 已更新: v{current_version} → v{new_version}")
                    else:
                        print(f"✅ yt-dlp 已是最新版本 (v{current_version})")
                else:
                    print("⚠️ yt-dlp 自动更新失败，继续使用当前版本")
            except Exception as e:
                print(f"⚠️ yt-dlp 自动更新异常: {e}")

        threading.Thread(target=auto_update, daemon=True).start()
        return True
    except FileNotFoundError:
        print("📦 正在安装 yt-dlp...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "yt-dlp"])
            print("✅ yt-dlp 安装完成!")
            return True
        except Exception as e:
            print(f"❌ 安装失败: {e}")
            return False

def cleanup():
    """清理所有活跃的下载进程"""
    for item_id, process in list(downloader.active_processes.items()):
        try:
            process.terminate()
            print(f"🛑 已终止下载进程: {item_id[:8]}...")
        except Exception:
            pass
    downloader.active_processes.clear()

def main():
    import signal

    print("\n🎬 Jack叔叔视频下载器 - v2.6")
    print("=" * 50)

    # 检查依赖
    if not check_and_install_yt_dlp():
        print("❌ 无法安装必要组件，程序退出")
        return

    print("🚀 正在启动服务...")
    print("📁 下载文件夹:", downloader.download_folder)

    # 获取可用端口并自动打开浏览器
    import socket
    import webbrowser
    import time
    import threading

    def find_free_port():
        for port in range(5000, 5010):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('127.0.0.1', port))
                    return port
                except OSError:
                    continue
        return 5000

    port = find_free_port()

    def open_browser():
        time.sleep(2)  # 等待服务器启动
        webbrowser.open(f'http://127.0.0.1:{port}')

    # 在后台线程中打开浏览器
    threading.Thread(target=open_browser, daemon=True).start()

    # 注册退出信号处理
    def signal_handler(sig, frame):
        print("\n🛑 正在退出...")
        cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"🌐 服务已启动: http://127.0.0.1:{port}")

    try:
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()