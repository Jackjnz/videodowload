#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载助手基类
提供共享的下载命令执行和进度解析功能
"""

import subprocess
import re


class DownloadResult:
    """统一的命令执行结果"""
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def run_download_command(cmd, progress_callback=None):
    """
    执行下载命令并解析进度

    Args:
        cmd: 命令列表
        progress_callback: 进度回调函数，接收 (progress, speed) 参数

    Returns:
        DownloadResult
    """
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        universal_newlines=True
    )

    stdout_lines = []
    progress_pattern = re.compile(r'(\d+\.?\d*)%')
    speed_pattern = re.compile(r'at\s+([\d.]+\s*\w+/s)')

    for line in iter(process.stdout.readline, ''):
        stdout_lines.append(line)

        if progress_callback:
            match = progress_pattern.search(line)
            if match:
                progress = float(match.group(1))
                speed_match = speed_pattern.search(line)
                speed = speed_match.group(1) if speed_match else None
                progress_callback(progress, speed)

    process.wait()
    stderr_output = process.stderr.read()

    return DownloadResult(
        process.returncode,
        ''.join(stdout_lines),
        stderr_output
    )
