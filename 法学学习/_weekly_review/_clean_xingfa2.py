#!/usr/bin/env python3
"""第二轮清理：修复刑法 MD 中的标题粘连和 OCR 残片"""

import re

INPUT = 'D:/ccuurroo/法学学习/_weekly_review/刑法总论_第一周总结.md'
OUTPUT = INPUT  # 原地覆盖

with open(INPUT, 'r', encoding='utf-8') as f:
    content = f.read()

# ── 修复：标题与正文粘连 ──
# ### 一、刑法的概念刑法是规定...  →  ### 一、刑法的概念\n\n刑法是规定...
def split_heading_body(text):
    """如果标题后直接跟正文（无换行），则分开"""
    lines = text.split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        # ### 一、XXX正文... 或 #### （一）XXX正文...
        m = re.match(r'^(#{2,4}\s+(?:[一二三四五六七八九十]+[、，]\s*)?(?:（[一二三四五六七八九十]+）)?)(\S.*)', stripped)
        if m:
            prefix = m.group(1)
            rest = m.group(2)
            heading_text = prefix.rstrip()
            # 检查 rest 是否以中文字符开始（说明正文粘连了）
            if rest and re.match(r'[一-鿿]', rest[0]):
                # 在标题和正文之间插入空行
                result.append(heading_text)
                result.append('')
                result.append(rest)
                continue
        result.append(stripped)
    return '\n'.join(result)

content = split_heading_body(content)

# ── 修复：被合并的简介/正文在标题行 ──
# ## 第二节 习近平法治思想习近平法治思想引领新时代 → ## 第二节 习近平法治思想引领新时代
content = content.replace('## 第二节 习近平法治思想习近平法治思想引领新时代',
                          '## 第二节 习近平法治思想引领新时代刑法学')

# ── 删除明确 OCR 垃圾行 ──
garbage_patterns = [
    r'^第\s*\d+\s*\{\}.*$',        # "第 1 {}七 LJ 汹沥 49"
    r'^等草尸.*$',                # "等草尸汒概说"
    r'^竺完.*$',                  # OCR 分隔线
    r'^[\-=\s\.一-]*[Tt]：.*$',   # OCR 分隔线
    r'^\d+\s*[）\)]\s*$',        # 孤立的编号
    r'^飞；.*$',                  # OCR 垃圾
    r'^@\s*习近平.*$',            # 脚注残留
    r'^CD\s+.*$',                # OCR 脚注标记
    r'^⑧\s*$',                   # 孤立注释
    r'^⑨\s*$',
    r'^⑩\s*$',
    r'^第\s*\d+\s*{}.*$',        # OCR 垃圾
]

lines = content.split('\n')
cleaned = []
for line in lines:
    s = line.strip()
    skip = False
    for pat in garbage_patterns:
        if re.match(pat, s):
            skip = True
            break
    if not skip:
        cleaned.append(line)

content = '\n'.join(cleaned)

# ── 修复重复的节标题 ──
# 删除连续重复的标题
lines = content.split('\n')
deduped = []
prev = ''
for line in lines:
    s = line.strip()
    if s.startswith('#') and s == prev:
        continue  # 跳过连续重复标题
    deduped.append(line)
    if s.startswith('#'):
        prev = s

content = '\n'.join(deduped)

# ── 修复已知 OCR 错误 ──
replacements = [
    ('## 第四节 刑法学的研究与学习方法 I 39', '## 第四节 刑法学的研究与学习方法'),
    ('## 第四节 学习', '## 第四节 刑法学的研究与学习方法'),
    ('# 第一章刑法概况', '# 第一章 刑法概说'),
    ('振⑨兴', '振兴'),
    ('中⑩大局', '中心大局'),
    ('飞）', '⑩'),
    ('贷', '。'),
    ('千是', '于是'),
    ('对千', '对于'),
    ('善千', '善于'),
    ('关千', '关于'),
    ('高质最', '高质量'),
    ('属千', '属于'),
]

for old, new in replacements:
    content = content.replace(old, new)

# ── 删除残留的脚注引文行 ──
lines = content.split('\n')
clean2 = []
for line in lines:
    s = line.strip()
    # 删除页码引用行 "CD 《马克思恩格斯全集..." 等
    if re.match(r'^(⑧|⑨|⑩|CD|@)\s*(习近平|《|［德］)', s):
        continue
    # 删除纯数字页码残留
    if re.match(r'^\d{1,3}$', s) and not s.startswith('0'):
        continue
    clean2.append(line)

content = '\n'.join(clean2)

# 移除多余连续空行
content = re.sub(r'\n{4,}', '\n\n\n', content)

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Second pass cleaning done: {OUTPUT}')
print(f'Size: {len(content)} chars')
