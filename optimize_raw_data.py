#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCUS文本数据优化脚本
将短行合并为适合UIE抽取的长句，提高抽取质量和效率
"""

import re
import os

def clean_and_merge_text(input_file, output_file, min_length=80, max_length=300):
    """
    清理和合并文本数据

    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
        min_length: 最小句子长度
        max_length: 最大句子长度
    """

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cleaned_lines = []
    current_paragraph = ""

    for line in lines:
        line = line.strip()

        # 跳过无效行
        if should_skip_line(line):
            continue

        # 如果是段落分隔符或空行，保存当前段落
        if is_paragraph_separator(line):
            if current_paragraph and len(current_paragraph) >= min_length:
                cleaned_lines.append(current_paragraph)
            current_paragraph = ""
            continue

        # 累积当前段落
        if current_paragraph:
            # 智能连接：如果前一句以标点结尾，加句号分隔；否则直接连接
            if current_paragraph[-1] in '。！？；':
                current_paragraph += " " + line
            else:
                current_paragraph += line
        else:
            current_paragraph = line

        # 如果段落太长，截断保存
        if len(current_paragraph) >= max_length:
            # 寻找合适的断点（句号、感叹号等）
            break_point = find_break_point(current_paragraph, max_length)
            if break_point > min_length:
                cleaned_lines.append(current_paragraph[:break_point])
                current_paragraph = current_paragraph[break_point:].strip()

    # 处理最后一个段落
    if current_paragraph and len(current_paragraph) >= min_length:
        cleaned_lines.append(current_paragraph)

    # 保存清理后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in cleaned_lines:
            f.write(line + '\n')

    print(f"原始行数: {len(lines)}")
    print(f"清理后行数: {len(cleaned_lines)}")
    print(f"数据压缩率: {len(cleaned_lines)/len(lines)*100:.1f}%")

    # 统计行长度分布
    lengths = [len(line) for line in cleaned_lines]
    print(f"平均行长度: {sum(lengths)/len(lengths):.1f}")
    print(f"最短行长度: {min(lengths)}")
    print(f"最长行长度: {max(lengths)}")

    return cleaned_lines

def should_skip_line(line):
    """判断是否应该跳过这一行"""
    if not line:
        return True

    # 跳过无意义的行
    skip_patterns = [
        r'^=+$',  # 分隔符
        r'^-+$',  # 分隔符
        r'^文件:',  # 文件信息
        r'^处理时间:',  # 处理信息
        r'^文件大小:',  # 文件信息
        r'^总页数:',  # 页数信息
        r'^有文本页数:',  # 页数信息
        r'^提取方法:',  # 方法信息
        r'^=== 第 \d+ 页 ===$',  # 页码
        r'^第\d+页',  # 页码
        r'^\d+$',  # 纯数字
        r'^[A-Z\s]+$',  # 纯大写字母
        r'^GPU加速',  # 处理信息
        r'^生成时间:',  # 生成信息
        r'^源文件夹:',  # 文件夹信息
        r'^总文件数:',  # 文件数信息
        r'^处理编码:',  # 编码信息
    ]

    for pattern in skip_patterns:
        if re.match(pattern, line):
            return True

    # 跳过太短的行（除非包含重要信息）
    if len(line) < 10 and not contains_important_info(line):
        return True

    return False

def contains_important_info(line):
    """判断短行是否包含重要信息"""
    important_keywords = [
        'CCUS', 'CCS', 'CO2', '二氧化碳', '碳捕集', '碳封存', '碳利用',
        '技术', '成本', '效率', '政策', '项目', '企业', '行业',
        '投资', '经济', '环境', '安全', '风险'
    ]

    return any(keyword in line for keyword in important_keywords)

def is_paragraph_separator(line):
    """判断是否是段落分隔符"""
    separators = [
        '摘要：', '关键词：', '中图分类号：', '文献标志码：',
        '基金项目：', '作者简介：', '通信作者：', '引言', '结论'
    ]

    return any(sep in line for sep in separators)

def find_break_point(text, max_length):
    """在合适的位置找到断点"""
    if len(text) <= max_length:
        return len(text)

    # 优先在句号、感叹号、问号处断开
    for i in range(max_length, max_length//2, -1):
        if text[i] in '。！？':
            return i + 1

    # 其次在分号、逗号处断开
    for i in range(max_length, max_length//2, -1):
        if text[i] in '；，':
            return i + 1

    # 最后在空格处断开
    for i in range(max_length, max_length//2, -1):
        if text[i] == ' ':
            return i

    # 实在找不到合适位置就硬切
    return max_length

if __name__ == "__main__":
    input_file = "data/raw_data.txt"
    output_file = "data/raw_data_optimized.txt"

    print("🚀 开始优化CCUS文本数据...")

    cleaned_data = clean_and_merge_text(input_file, output_file)

    print("✅ 数据优化完成！")
    print(f"📁 优化后的文件保存为: {output_file}")
    print("\n📊 优化效果预览:")

    # 显示前5行示例
    for i, line in enumerate(cleaned_data[:5]):
        print(f"{i+1}. {line[:100]}{'...' if len(line) > 100 else ''}")

    print(f"\n💡 建议使用优化后的文件运行UIE抽取:")
    print(f"   python main.py --project=ccus_v1_optimized")