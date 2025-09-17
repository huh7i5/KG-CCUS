#!/usr/bin/env python3
"""
下载ChatGLM-6B模型脚本 - 稳定版本
"""

import os
import subprocess
from huggingface_hub import snapshot_download

def download_chatglm_model():
    """使用huggingface_hub下载ChatGLM-6B模型"""

    model_name = "THUDM/chatglm-6b"
    save_path = "/fast/zwj/ChatGLM-6B/weights"

    print(f"开始下载ChatGLM-6B模型到: {save_path}")
    print("使用 huggingface_hub.snapshot_download 方法...")

    try:
        # 创建目录
        os.makedirs(save_path, exist_ok=True)

        # 使用snapshot_download下载整个模型
        print("正在下载模型文件...")
        snapshot_download(
            repo_id=model_name,
            local_dir=save_path,
            local_dir_use_symlinks=False,
            resume_download=True
        )

        print(f"✅ 模型下载完成！保存在: {save_path}")

        # 验证下载的文件
        files = os.listdir(save_path)
        print(f"下载的文件: {files}")

        return True

    except Exception as e:
        print(f"❌ 下载失败: {e}")
        print("尝试使用git lfs方法...")
        return download_with_git_lfs()

def download_with_git_lfs():
    """使用git lfs下载模型"""

    save_path = "/fast/zwj/ChatGLM-6B/weights"

    try:
        # 清空目录
        if os.path.exists(save_path):
            subprocess.run(["rm", "-rf", save_path], check=True)

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # 使用git clone下载
        cmd = [
            "git", "clone",
            "https://huggingface.co/THUDM/chatglm-6b",
            save_path
        ]

        print("使用git clone下载模型...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

        if result.returncode == 0:
            print(f"✅ 模型下载完成！保存在: {save_path}")
            return True
        else:
            print(f"❌ Git clone失败: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Git下载失败: {e}")
        return False

if __name__ == "__main__":
    success = download_chatglm_model()
    if not success:
        print("所有下载方法都失败了，请检查网络连接或手动下载模型")