#!/usr/bin/env python3
"""
修复JSON响应问题 - 清理节点名称中的特殊字符
"""

import json
import re
import os

def clean_text_for_json(text):
    """清理文本以确保JSON序列化安全"""
    if not isinstance(text, str):
        return text

    # 移除或替换问题字符
    text = text.replace('\n', ' ')  # 换行符替换为空格
    text = text.replace('\r', ' ')  # 回车符替换为空格
    text = text.replace('\t', ' ')  # 制表符替换为空格
    text = text.replace('"', "'")   # 双引号替换为单引号
    text = text.replace('\\', '/')  # 反斜杠替换为正斜杠

    # 移除控制字符
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

    # 压缩多个空格为单个空格
    text = re.sub(r'\s+', ' ', text)

    # 移除首尾空格
    text = text.strip()

    # 限制长度避免过长的实体名
    if len(text) > 200:
        text = text[:197] + "..."

    return text

def fix_data_json():
    """修复data.json文件中的特殊字符问题"""

    data_path = "/root/KnowledgeGraph/KnowledgeGraph-based-on-Raw-text-A27/data/data.json"

    if not os.path.exists(data_path):
        print(f"❌ Data file not found: {data_path}")
        return False

    try:
        print("🔧 Loading and fixing data.json...")
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 清理节点名称
        if 'nodes' in data:
            for node in data['nodes']:
                if 'name' in node:
                    old_name = node['name']
                    node['name'] = clean_text_for_json(old_name)
                    if old_name != node['name']:
                        print(f"  📝 Fixed node: {old_name[:50]}... -> {node['name'][:50]}...")

        # 清理边信息
        if 'links' in data:
            for link in data['links']:
                if 'name' in link:
                    link['name'] = clean_text_for_json(link['name'])

        # 清理句子信息
        if 'sents' in data:
            if isinstance(data['sents'], list):
                for i, sent in enumerate(data['sents']):
                    if isinstance(sent, str):
                        data['sents'][i] = clean_text_for_json(sent)
            elif isinstance(data['sents'], dict):
                for key, sent in data['sents'].items():
                    if isinstance(sent, str):
                        data['sents'][key] = clean_text_for_json(sent)

        # 保存修复后的文件
        backup_path = data_path + ".backup"
        if not os.path.exists(backup_path):
            print(f"💾 Creating backup: {backup_path}")
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"💾 Saving fixed data.json...")
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print("✅ Data.json fixed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error fixing data.json: {e}")
        return False

if __name__ == "__main__":
    fix_data_json()