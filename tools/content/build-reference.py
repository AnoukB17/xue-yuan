# -*- coding: utf-8 -*-
"""Extrait une référence allégée des listes HSK officielles, pour tools/build-vocab.py.

Source : github.com/drkameleon/complete-hsk-vocabulary (licence MIT, © 2026 Yanis Zafirópulos), fichier complete.json :
listes officielles HSK 2.0 (niveaux 1-6) et HSK 3.0 (niveaux 1-6 et 7-9), fréquence d'après SUBTLEX-CH,
pinyin, catégories et classificateurs d'après CC-CEDICT (CC BY-SA 4.0).

Usage : python3 tools/content/build-reference.py chemin/vers/complete.json
Écrit tools/content/hsk-reference.json : {mot: {"n": niveau 3.0 (7 = 7-9), "o": niveau 2.0, "q": rang de fréquence,
"pos": [catégories], "r": [{"y": pinyin, "c": [classificateurs], "en": [3 sens anglais]}]}}
"""
import json, os, sys

src = json.load(open(sys.argv[1], encoding='utf8'))
out = {}
for e in src:
    lv = e.get('l', [])
    n = min([int(x[1]) for x in lv if x.startswith('n')] or [0]) or None
    o = min([int(x[1]) for x in lv if x.startswith('o')] or [0]) or None
    if not (n or o): continue
    readings = []
    for f in e.get('f', []):
        y = f['i']['y']
        if y[:1].isupper() and len(e['f']) > 1: continue  # nom propre (« surname Hua ») : ignoré s'il y a d'autres lectures
        if f['t'] != e['s'] and any(r['y'] == y for r in readings): continue  # variante graphique de la même lecture
        readings.append({'y': y, 'c': f.get('c', [])[:3], 'en': [m for m in f.get('m', []) if not m.startswith(('variant of', 'old variant'))][:3]})
    out[e['s']] = {'n': n, 'o': o, 'q': e.get('q'), 'pos': e.get('p', []), 'r': readings}
path = os.path.join(os.path.dirname(__file__), 'hsk-reference.json')
json.dump(out, open(path, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print(f'{len(out)} mots → {path} ({os.path.getsize(path) // 1024} Ko)')
