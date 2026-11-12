# -*- coding: utf-8 -*-
"""Extrait les listes officielles du programme du nouvel HSK (« HSK 考试大纲 », CLEC, publié en 2025-11, en vigueur en 2026-07).

Source : https://www.chinesetest.cn/ → « Examination Syllabus » (新版HSK考试大纲, PDF de 406 pages).
Usage : pdftotext -layout syllabus.pdf syllabus.txt ; python3 tools/content/parse-syllabus.py syllabus.txt
Écrit tools/content/hsk30-vocabulaire.tsv (n°, niveau, mot, pinyin, catégorie) et hsk30-grammaire.txt dans le dossier courant (texte brut, non versionné
du « 语法大纲 », niveau par niveau).
"""
import os, re, sys
txt = open(sys.argv[1], encoding='utf8').read().split('\n')
OUT = os.path.dirname(__file__)
start = max(i for i, l in enumerate(txt) if '词汇大纲' in l)
end = max(i for i, l in enumerate(txt) if '汉字大纲' in l)
rows = []
for l in txt[start:end]:
    m = re.match(r'^\s*(\d+)\s{2,}(\S+)\s{2,}(\S+)\s{2,}(.+?)\s*$', l)
    if not m: continue
    n, lvl, word, rest = m.groups()
    parts = re.split(r'\s{2,}', rest)
    py, pos = parts[0], ' '.join(parts[1:])
    lv = re.match(r'(\d|7—9)', lvl).group(1)
    rows.append((int(n), lvl, re.sub(r'\d+$', '', word), word, py, pos))
with open(os.path.join(OUT, 'hsk30-vocabulaire.tsv'), 'w', encoding='utf8') as f:
    f.write('# Vocabulaire officiel du nouvel HSK (HSK 考试大纲, CLEC, 2025-11). Colonnes : n°, niveau (« 1（4） » = niveau 1, autre sens au niveau 4), mot, mot avec indice de sens, pinyin, catégorie\n')
    for r in rows: f.write('\t'.join(map(str, r)) + '\n')
g0 = max(i for i, l in enumerate(txt) if '语法大纲' in l)
open('hsk30-grammaire.txt', 'w', encoding='utf8').write('\n'.join(l for l in txt[g0:] if l.strip()) + '\n')
import collections
c = collections.Counter(re.match(r'(\d|7—9)', r[1]).group(1) for r in rows)
print(len(rows), 'entrées ;', 'par niveau :', dict(sorted(c.items())), '; numéros', rows[0][0], '→', rows[-1][0])
