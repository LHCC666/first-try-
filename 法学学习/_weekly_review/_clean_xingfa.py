#!/usr/bin/env python3
"""清理刑法课本 PDF 提取文本，重建高质量 Markdown"""

import re, os

BASE = os.path.dirname(os.path.abspath(__file__))
EXTRACT_DIR = os.path.join(BASE, '_textbook_extracts')
OUTPUT_MD = os.path.join(BASE, '刑法总论_第一周总结.md')

# ── OCR 常见错误修正表 ──
OCR_FIXES = [
    # 标题级修正
    ('第＝节', '第二节'),
    ('同法概说', '刑法概说'),
    ('荆法概说', '刑法概说'),
    ('庄法学', '刑法学'),
    ('开历去的指写思想、根据与江务', '刑法的指导思想、根据与任务'),
    ('保陀人权原仄', '保障人权原则'),
    ('弓；，顶祈脰气中', '习近平法治思想引领新时代'),
    ('庄法学的研究与学习方法', '刑法学的研究与学习方法'),
    ('学习万汰', '刑法学的研究与学习方法'),
    ('犯罪构戍', '犯罪构成'),

    # 常见字符错误
    ('同法', '刑法'),
    ('千是', '于是'),
    ('对千', '对于'),
    ('善千', '善于'),
    ('关千', '关于'),
    ('高质最', '高质量'),
    ('仇', '⑧'),
    ('复', '⑨'),
    ('心', '⑩'),

    # 标点
    ('“ ', ' "'),
    (' ”', '" '),
    ('＇', '"'),

    # 残留注释标记
    ('[1]', ''),
    ('[2]', ''),
    ('[3]', ''),
    ('[4]', ''),
    ('[5]', ''),
    ('[6]', ''),
    ('[7]', ''),
    ('[8]', ''),
    ('[9]', ''),
    ('[10]', ''),
    ('[11]', ''),
    ('[12]', ''),
    ('[13]', ''),
    ('[14]', ''),
    ('[15]', ''),
    ('[16]', ''),
    ('[17]', ''),
    ('[18]', ''),
    ('[19]', ''),
    ('[20]', ''),
]

def clean_line(line):
    """清理单行文本"""
    # 移除 [PDF第XX页]
    line = re.sub(r'\[PDF第\d+页\]', '', line)
    # 移除行首纯页码（如单独的 "36"、"52"）
    if re.match(r'^\d{1,3}$', line.strip()):
        return ''
    # 移除页脚残片
    if re.match(r'^[\-=\s\.一-鿿]*[Tt]：.*$', line.strip()):
        return ''
    if re.match(r'^竺完.*$', line.strip()):
        return ''
    # 应用 OCR 修正
    for old, new in OCR_FIXES:
        line = line.replace(old, new)
    return line


def read_and_clean(filepath):
    """读取并清理提取文件"""
    lines = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            cleaned = clean_line(line)
            if cleaned.strip():
                lines.append(cleaned.rstrip())
    return lines


def merge_broken_paragraphs(lines):
    """合并被换行打断的段落"""
    merged = []
    buf = ''
    for line in lines:
        s = line.strip()
        # 标题行不合并
        if s.startswith('第') and ('章' in s or '节' in s):
            if buf:
                merged.append(buf)
                buf = ''
            merged.append(s)
            continue
        if re.match(r'^[（(][一二三四五六七八九十]+[）)]', s):
            if buf:
                merged.append(buf)
                buf = ''
            merged.append(s)
            continue
        if re.match(r'^\d+[\.\、]', s):
            if buf:
                merged.append(buf)
                buf = ''
            merged.append(s)
            continue

        # 句号、引号结尾 → 段落结束
        if s.endswith('。') or s.endswith('」') or s.endswith('）') or s.endswith(')') or s.endswith('"'):
            buf += s
            merged.append(buf)
            buf = ''
        elif s.endswith('；') or s.endswith('，') or s.endswith('：') or s.endswith('、'):
            buf += s
        else:
            buf += s

    if buf:
        merged.append(buf)

    return merged


def identify_heading(line):
    """识别标题层级
    返回: (level, text) 或 None
    level: 'chapter', 'section', 'subsection', 'subsubsection'
    """
    s = line.strip()

    # 章
    m = re.match(r'^第([一二三四五六七八九十]+)章\s*(.+)', s)
    if m:
        return ('chapter', s)

    # 节
    m = re.match(r'^第([一二三四五六七八九十]+)节\s*(.+)', s)
    if m:
        return ('section', s)

    # 小节（一、二、三）
    m = re.match(r'^([一二三四五六七八九十])[、，]\s*(.+)', s)
    if m:
        return ('subsection', s)

    # 细目（（一）（二））
    m = re.match(r'^[（(]([一二三四五六七八九十]+)[）)]\s*(.+)', s)
    if m:
        return ('subsubsection', s)

    return None


def build_markdown(all_lines):
    """将清理后的文本重建为 Markdown"""
    md_lines = []

    # 标题
    md_lines.append('# 刑法总论 · 第一周知识点总结')
    md_lines.append('')
    md_lines.append('> 马工程《刑法学（第二版）》上册 | 2026年6月1日—6日 | 内容基于课本原文')
    md_lines.append('')
    md_lines.append('---')
    md_lines.append('')

    current_chapter = None
    current_section = None
    current_subsection = None

    for line in all_lines:
        s = line.strip()
        if not s:
            continue

        heading = identify_heading(s)

        if heading:
            level, text = heading

            if level == 'chapter':
                md_lines.append('')
                md_lines.append(f'# {text}')
                md_lines.append('')
                current_chapter = text
                current_section = None
                current_subsection = None

            elif level == 'section':
                md_lines.append('')
                md_lines.append(f'## {text}')
                md_lines.append('')
                current_section = text
                current_subsection = None

            elif level == 'subsection':
                md_lines.append('')
                md_lines.append(f'### {text}')
                md_lines.append('')
                current_subsection = text

            elif level == 'subsubsection':
                md_lines.append('')
                md_lines.append(f'#### {text}')
                md_lines.append('')

        else:
            # 普通段落
            # 跳过明显是 OCR 碎片的行
            if len(s) < 4 and not s.startswith('第'):
                continue
            # 跳过纯页码
            if re.match(r'^\d+$', s):
                continue

            md_lines.append(s)
            md_lines.append('')

    return '\n'.join(md_lines)


def main():
    # 刑法各章提取文件
    files = [
        '刑法_第1章_刑法概说.txt',
        '刑法_第2章_刑法基本原则.txt',
        '刑法_第3章_刑法的效力.txt',
        '刑法_第4章_犯罪概念与犯罪构成.txt',
        '刑法_第5章_犯罪客体.txt',
        '刑法_第6章_犯罪客观方面.txt',
    ]

    all_lines = []
    for fname in files:
        fpath = os.path.join(EXTRACT_DIR, fname)
        if os.path.exists(fpath):
            print(f'读取: {fname}')
            lines = read_and_clean(fpath)
            all_lines.extend(lines)

    print(f'清理后共 {len(all_lines)} 行')

    # 合并断行
    merged = merge_broken_paragraphs(all_lines)
    print(f'合并后共 {len(merged)} 段')

    # 生成 MD
    md_content = build_markdown(merged)

    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f'✅ 已生成: {OUTPUT_MD}')
    print(f'   文件大小: {os.path.getsize(OUTPUT_MD)} bytes')


if __name__ == '__main__':
    main()
