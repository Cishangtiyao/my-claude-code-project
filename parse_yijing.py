#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析周易卦爻辞文本文件，生成JavaScript数据结构
"""

import re
import json

def parse_yijing(filename):
    # 64卦的正确卦名（从HTML中的hexagramData提取）
    hexagram_names = {
        1: '乾', 2: '坤', 3: '屯', 4: '蒙', 5: '需', 6: '讼', 7: '师', 8: '比',
        9: '小畜', 10: '履', 11: '泰', 12: '否', 13: '同人', 14: '大有', 15: '谦', 16: '豫',
        17: '随', 18: '蛊', 19: '临', 20: '观', 21: '噬嗑', 22: '贲', 23: '剥', 24: '复',
        25: '无妄', 26: '大畜', 27: '颐', 28: '大过', 29: '坎', 30: '离', 31: '咸', 32: '恒',
        33: '遁', 34: '大壮', 35: '晋', 36: '明夷', 37: '家人', 38: '睽', 39: '蹇', 40: '解',
        41: '损', 42: '益', 43: '夬', 44: '姤', 45: '萃', 46: '升', 47: '困', 48: '井',
        49: '革', 50: '鼎', 51: '震', 52: '艮', 53: '渐', 54: '归妹', 55: '丰', 56: '旅',
        57: '巽', 58: '兑', 59: '涣', 60: '节', 61: '中孚', 62: '小过', 63: '既济', 64: '未济'
    }

    with open(filename, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f.readlines()]

    hexagrams = []
    current_hexagram = None
    current_yao = None
    i = 0

    while i < len(lines):
        line = lines[i]

        # 匹配卦的开始：数字 + 卦名 + 卦辞
        # 排除爻辞行（以"初九"、"初六"等开头）和传文行
        match = re.match(r'^(\d+)\.?\s+\u3000*(.+)$', line)
        is_yao_line = re.match(r'^(初[九六]|[九六][二三四五]|上[九六]|用[九六])', line)
        if match and '《' not in line and not is_yao_line:
            # 保存上一卦
            if current_hexagram:
                hexagrams.append(current_hexagram)

            number = int(match.group(1))
            rest = match.group(2).strip()

            # 使用预定义的卦名
            name = hexagram_names.get(number, '')

            # 提取卦辞：去掉开头的卦名部分
            if rest.startswith(name):
                guaci = rest[len(name):].lstrip('，、 ')
            else:
                # 如果无法匹配，尝试按逗号分割
                if '，' in rest:
                    guaci = rest.split('，', 1)[1]
                else:
                    guaci = rest

            current_hexagram = {
                'number': number,
                'name': name,
                'guaci': guaci,
                'tuan': '',
                'daxiang': '',
                'yaos': []
            }
            current_yao = None
            i += 1
            continue

        # 匹配《彖》曰
        if '《彖》曰：' in line:
            tuan_text = line.split('《彖》曰：')[1]
            if current_hexagram:
                current_hexagram['tuan'] = tuan_text
            i += 1
            continue

        # 匹配大象传（第一个《象》曰）
        # 需要区分大象和小象
        if '《象》曰：' in line and current_hexagram and not current_hexagram['daxiang']:
            xiang_text = line.split('《象》曰：')[1]
            current_hexagram['daxiang'] = xiang_text
            i += 1
            continue

        # 匹配爻辞：初九、初六、九二、六二等
        yao_match = re.match(r'^(初[九六]|[九六][二三四五]|上[九六]|用[九六])，(.+)$', line)
        if yao_match:
            yao_name = yao_match.group(1)
            yao_text = yao_match.group(2)
            current_yao = {
                'name': yao_name,
                'text': yao_text,
                'xiang': ''
            }
            if current_hexagram:
                current_hexagram['yaos'].append(current_yao)
            i += 1
            continue

        # 匹配小象传（爻的《象》曰）
        if '《象》曰：' in line and current_yao:
            xiaoxiang_text = line.split('《象》曰：')[1]
            current_yao['xiang'] = xiaoxiang_text
            i += 1
            continue

        i += 1

    # 添加最后一卦
    if current_hexagram:
        hexagrams.append(current_hexagram)

    return hexagrams

def generate_javascript(hexagrams):
    """生成JavaScript代码"""
    js_code = "// 周易64卦完整数据（卦辞、爻辞、彖传、象传）\n"
    js_code += "const yijingTexts = {\n"

    for gua in hexagrams:
        js_code += f"  {gua['number']}: {{\n"
        js_code += f"    name: '{gua['name']}',\n"
        js_code += f"    guaci: '{gua['guaci']}',\n"
        js_code += f"    tuan: '{gua['tuan']}',\n"
        js_code += f"    daxiang: '{gua['daxiang']}',\n"
        js_code += f"    yaos: [\n"

        for yao in gua['yaos']:
            js_code += f"      {{ name: '{yao['name']}', text: '{yao['text']}', xiang: '{yao['xiang']}' }},\n"

        js_code += f"    ]\n"
        js_code += f"  }},\n"

    js_code += "};\n"
    return js_code

if __name__ == '__main__':
    hexagrams = parse_yijing('周易卦爻辞.txt')

    print(f"成功解析 {len(hexagrams)} 卦")

    # 生成JavaScript代码
    js_code = generate_javascript(hexagrams)

    # 保存到文件
    with open('yijing_data.js', 'w', encoding='utf-8') as f:
        f.write(js_code)

    print("JavaScript数据已保存到 yijing_data.js")

    # 输出第一卦作为示例
    print("\n第一卦示例：")
    print(json.dumps(hexagrams[0], ensure_ascii=False, indent=2))
