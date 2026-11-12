# -*- coding: utf-8 -*-
"""Paquets de traductions : relecture puis intégration.

python3 tools/content/paquet.py relire tools/content/paquet-01-fr.tsv
    → docs/paquets/paquet-01.md : tableau à relire (n°, mot, pinyin et catégorie officiels, traduction, note) + contrôles
python3 tools/content/paquet.py integrer tools/content/paquet-01-fr.tsv
    → ajoute les mots à data/vocab.json (seulement après accord), puis lancer tools/build-vocab.py

Le pinyin et la catégorie viennent toujours de la liste officielle (tools/content/hsk30-vocabulaire.tsv) : seule la
traduction française est rédigée à la main. Les mots marqués « ? » sont à faire relire en priorité par un natif.
"""
import json, os, re, sys
ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
OFF = {}
for line in open(os.path.join(ROOT, 'tools', 'content', 'hsk30-vocabulaire.tsv'), encoding='utf8'):
    if line.startswith('#'): continue
    n, lvl, word, word_idx, py, *pos = line.rstrip('\n').split('\t')
    OFF[int(n)] = {'n': int(n), 'lvl': lvl, 'lv': 7 if lvl.startswith('7') else int(lvl[0]), 'h': word, 'p': py.replace('’', "'"), 'pos': pos[0] if pos else ''}

def load(path):
    items = []
    for line in open(path, encoding='utf8'):
        if line.startswith('#') or not line.strip(): continue
        n, fr, *note = line.rstrip('\n').split('\t')
        o = OFF[int(n)]; items.append({**o, 'fr': fr.strip(), 'note': (note[0] if note else '').strip()})
    return items

def checks(items):
    vocab = json.load(open(os.path.join(ROOT, 'data', 'vocab.json'), encoding='utf8'))
    have = {r['h'] for r in vocab}
    out = []
    dup = [i['h'] for i in items if i['h'] in have]
    if dup: out.append(f'Déjà dans l\'appli : {" ".join(dup)}')
    empty = [str(i['n']) for i in items if not i['fr']]
    if empty: out.append(f'Sans traduction : {" ".join(empty)}')
    return out

def relire(path):
    items = load(path); name = os.path.basename(path).replace('-fr.tsv', '')
    doubt = [i for i in items if i['note'].startswith('?')]
    lv = sorted({i['lv'] for i in items})
    lines = [f'# {name.replace("-", " ").capitalize()} : {len(items)} mots du niveau {", ".join(map(str, lv))} du nouvel HSK', '',
             'Pinyin et catégorie : liste officielle du programme 2025 (HSK 考试大纲, CLEC). Traductions : proposées par Claude, **à faire relire par un natif**.',
             f'Les {len(doubt)} lignes marquées ⚠ sont à vérifier en priorité.', '',
             'Pour valider : dis « paquet OK », ou indique les numéros à corriger avec la bonne traduction.', '',
             '| N° | Mot | Pinyin | Catégorie | Traduction proposée | Note |', '|---|---|---|---|---|---|']
    for i in items:
        note = i['note'].lstrip('? ').strip()
        lines.append(f"| {i['n']} | {i['h']} | {i['p']} | {i['pos']} | {i['fr']} | {'⚠ ' if i['note'].startswith('?') else ''}{note} |")
    c = checks(items)
    lines += ['', '## Contrôles automatiques', ''] + ([f'- {x}' for x in c] or ['- Aucun doublon avec l\'appli, aucune traduction vide.'])
    os.makedirs(os.path.join(ROOT, 'docs', 'paquets'), exist_ok=True)
    out = os.path.join(ROOT, 'docs', 'paquets', f'{name}.md')
    open(out, 'w', encoding='utf8').write('\n'.join(lines) + '\n')
    print(f'{len(items)} mots, {len(doubt)} à vérifier en priorité → {out}'); [print('  ' + x) for x in c]

def integrer(path):
    items = load(path)
    c = checks(items)
    if c: print('Refusé :', *c, sep='\n  '); sys.exit(1)
    vocab = json.load(open(os.path.join(ROOT, 'data', 'vocab.json'), encoding='utf8'))
    for i in items: vocab.append({'h': i['h'], 'p': i['p'], 'fr': i['fr'], 'app': i['lv'], 'n': i['n']})
    json.dump(vocab, open(os.path.join(ROOT, 'data', 'vocab.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=0)
    print(f'{len(items)} mots ajoutés à data/vocab.json : lancer python3 tools/build-vocab.py --report')

if __name__ == '__main__':
    {'relire': relire, 'integrer': integrer}[sys.argv[1]](sys.argv[2])
