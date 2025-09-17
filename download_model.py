#!/usr/bin/env python3
"""
下载ChatGLM-6B模型脚本
"""

import os
from transformers import AutoTokenizer, AutoModel

def download_chatglm_model():
    """下载ChatGLM-6B模型"""

    model_name = "THUDM/chatglm-6b"
    save_path = "/fast/zwj/ChatGLM-6B/weights"

    print(f"开始下载ChatGLM-6B模型到: {save_path}")
    print("这可能需要几分钟时间，请耐心等待...")

    try:
        # 创建目录
        os.makedirs(save_path, exist_ok=True)

        # 下载tokenizer
        print("正在下载tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            cache_dir=save_path
        )
        tokenizer.save_pretrained(save_path)

        # 下载模型
        print("正在下载模型权重...")
        model = AutoModel.from_pretrained(
            model_name,
            trust_remote_code=True,
            cache_dir=save_path
        )
        model.save_pretrained(save_path)

        print(f"✅ 模型下载完成！保存在: {save_path}")
        return True

    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False

if __name__ == "__main__":
    download_chatglm_model()