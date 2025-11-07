#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析周易卦爻辞文本文件，生成JavaScript数据结构
"""

import re
import json

def parse_yijing(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f.readlines()]

    hexagrams = []
    current_hexagram = None
    current_yao = None
    i = 0

    while i < len(lines):
        line = lines[i]

        # 匹配卦的开始：数字 + 卦名 + 卦辞
        # 例如：1   乾，元亨利貞。
        # 特殊处理"師貞"这种情况，卦名只是"師"
        match = re.match(r'^(\d+)\.?\s+\u3000*(.+)$', line)
        if match and '《' not in line and '象' not in line and '初' not in line:
            # 保存上一卦
            if current_hexagram:
                hexagrams.append(current_hexagram)

            number = int(match.group(1))
            rest = match.group(2).strip()

            # 分离卦名和卦辞
            # 通常格式：卦名，卦辞
            if '，' in rest:
                parts = rest.split('，', 1)
                name = parts[0].strip()
                # 处理"師貞"这种情况
                if len(name) > 1 and name[-1] in ['貞', '亨']:
                    # 可能是卦名+卦辞连在一起
                    name = name[0] if len(name) == 2 else name
                guaci = parts[1].strip() if len(parts) > 1 else ''
            else:
                name = rest
                guaci = ''

            current_hexagram = {
                'number': number,
                'name': name,
                'guaci': rest.split('，', 1)[1] if '，' in rest else rest,
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
