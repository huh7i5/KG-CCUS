#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将UIE格式的CCUS数据转换为SPN4RE兼容格式
"""

import json
import os

def convert_uie_to_spn4re(input_file, output_file):
    """将UIE格式转换为SPN4RE格式"""

    # 读取UIE格式数据
    uie_data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                uie_data.append(json.loads(line))

    print(f"📊 加载了 {len(uie_data)} 条UIE数据")

    # 转换为SPN4RE格式
    spn4re_data = []

    for item in uie_data:
        sent_id = item.get('id', 0)
        sent_text = item.get('sentText', '')
        relation_mentions = item.get('relationMentions', [])

        converted_relations = []

        for relation_mention in relation_mentions:
            for entity_type, entities_list in relation_mention.items():
                if not isinstance(entities_list, list):
                    continue

                for entity_data in entities_list:
                    if not isinstance(entity_data, dict):
                        continue

                    # 提取主实体
                    entity_text = entity_data.get('text', '').strip()
                    if not entity_text:
                        continue

                    # 提取关系
                    relations_dict = entity_data.get('relations', {})
                    for rel_type, rel_entities in relations_dict.items():
                        if not isinstance(rel_entities, list):
                            continue

                        for rel_entity_data in rel_entities:
                            if not isinstance(rel_entity_data, dict):
                                continue

                            rel_entity_text = rel_entity_data.get('text', '').strip()
                            if not rel_entity_text:
                                continue

                            # 创建SPN4RE格式的关系
                            spn4re_relation = {
                                'em1Text': entity_text,
                                'em2Text': rel_entity_text,
                                'label': rel_type,
                                'em1Start': entity_data.get('start', 0),
                                'em1End': entity_data.get('end', 0),
                                'em2Start': rel_entity_data.get('start', 0),
                                'em2End': rel_entity_data.get('end', 0)
                            }
                            converted_relations.append(spn4re_relation)

        # 创建SPN4RE格式的数据项
        if converted_relations:  # 只保留有关系的数据
            spn4re_item = {
                'id': sent_id,
                'sentText': sent_text,
                'relationMentions': converted_relations
            }
            spn4re_data.append(spn4re_item)

    # 保存转换后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in spn4re_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✅ 转换完成！")
    print(f"📈 转换统计:")
    print(f"   - 输入数据: {len(uie_data)} 条")
    print(f"   - 输出数据: {len(spn4re_data)} 条")

    # 统计关系数量
    total_relations = sum(len(item['relationMentions']) for item in spn4re_data)
    print(f"   - 总关系数: {total_relations} 个")

    if spn4re_data:
        avg_relations = total_relations / len(spn4re_data)
        print(f"   - 平均关系数: {avg_relations:.2f} 个/句")

    return spn4re_data

def main():
    """主函数"""
    input_file = "data/ccus_v1/base.json"
    output_file = "data/ccus_v1/base_spn4re.json"

    print("🚀 开始转换UIE格式为SPN4RE格式...")

    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        return

    # 执行转换
    convert_uie_to_spn4re(input_file, output_file)

    print(f"📁 转换后文件保存为: {output_file}")

if __name__ == "__main__":
    main()