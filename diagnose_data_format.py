#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断base.json数据格式问题
"""

import json
import sys

def diagnose_data_format(file_path):
    """诊断数据格式问题"""

    print(f"🔍 诊断文件: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"📊 总共有 {len(lines)} 行数据")

    for i, line in enumerate(lines):
        try:
            data = json.loads(line.strip())

            # 检查基本字段
            if 'id' not in data:
                print(f"❌ 第{i+1}行缺少id字段")
                continue

            if 'sentText' not in data:
                print(f"❌ 第{i+1}行缺少sentText字段")
                continue

            if 'relationMentions' not in data:
                print(f"❌ 第{i+1}行缺少relationMentions字段")
                continue

            # 检查relationMentions格式
            relations = data['relationMentions']
            for j, relation in enumerate(relations):
                if not isinstance(relation, dict):
                    print(f"❌ 第{i+1}行第{j+1}个关系不是字典格式: {relation}")
                    continue

                required_fields = ['em1Text', 'em2Text', 'label']
                for field in required_fields:
                    if field not in relation:
                        print(f"❌ 第{i+1}行第{j+1}个关系缺少{field}字段: {relation}")
                        break
                else:
                    # 检查字段值
                    if not relation['em1Text'] or not relation['em2Text']:
                        print(f"⚠️ 第{i+1}行第{j+1}个关系有空实体: {relation}")

            if i == 0:
                print(f"✅ 第{i+1}行格式正确，示例:")
                print(f"   ID: {data['id']}")
                print(f"   文本长度: {len(data['sentText'])}")
                print(f"   关系数量: {len(data['relationMentions'])}")
                if data['relationMentions']:
                    print(f"   首个关系: {data['relationMentions'][0]}")

        except json.JSONDecodeError as e:
            print(f"❌ 第{i+1}行JSON解析失败: {e}")
        except Exception as e:
            print(f"❌ 第{i+1}行处理失败: {e}")

    print("🔍 诊断完成")

if __name__ == "__main__":
    file_path = "data/ccus_v1/base.json"
    diagnose_data_format(file_path)