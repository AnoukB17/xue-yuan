# -*- coding: utf-8 -*-
"""Vocabulaire de Xué Yuán : source unique data/vocab.json → liste de mots générée dans index.html.

Lancer : python3 tools/build-vocab.py            (après toute modification de data/vocab.json)
         python3 tools/build-vocab.py --report   (écrit aussi docs/couverture.md)

data/vocab.json : une entrée par sens, dans l'ordre d'apprentissage de l'appli :
  h    caractères simplifiés            p   pinyin (convention de l'appli : 一 et 不 notés tels qu'on les prononce)
  fr   traduction française             app niveau où l'appli l'enseigne : celui du nouvel HSK (1-6) s'il existe, sinon app20
  app20 niveau où l'appli l'enseignait avant le passage au nouvel HSK (HSK 2.0, 1 à 4)
  hsk2 niveau officiel HSK 2.0 (1-6)    hsk3 niveau du nouvel HSK (1-6, 7 = niveaux 7-9), programme officiel 2025
  freq rang de fréquence (1 = le plus courant, SUBTLEX-CH)    cl classificateurs usuels (CC-CEDICT)
  pos  catégories grammaticales (codes ICTCLAS : n nom, v verbe, a adjectif, d adverbe, q classificateur…)
Le français et le pinyin sont la référence de l'appli. Niveau du nouvel HSK : liste officielle du programme « HSK 考试大纲 »
(CLEC, publié en 2025-11, en vigueur en 2026-07), extraite dans tools/content/hsk30-vocabulaire.tsv (parse-syllabus.py).
Niveau HSK 2.0, fréquence, catégories et classificateurs : tools/content/hsk-reference.json (voir build-reference.py).
"""
import json, os, re, sys, unicodedata
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'content'))
from themes import THEMES  # thèmes de l'écran « Listes » (tools/content/themes.py)
ROOT = os.path.join(os.path.dirname(__file__), '..')
VOCAB = os.path.join(ROOT, 'data', 'vocab.json')
REF = json.load(open(os.path.join(ROOT, 'tools', 'content', 'hsk-reference.json'), encoding='utf8'))
HTML = os.path.join(ROOT, 'index.html')
# Liste officielle 2025 : niveau le plus bas de chaque mot (un mot peut avoir plusieurs sens à des niveaux différents)
OFFICIAL = {}
for line in open(os.path.join(ROOT, 'tools', 'content', 'hsk30-vocabulaire.tsv'), encoding='utf8'):
    if line.startswith('#'): continue
    n, lvl, word, *_ = line.rstrip('\n').split('\t')
    lv = 7 if lvl.startswith('7') else int(lvl[0])
    OFFICIAL[word] = min(lv, OFFICIAL.get(word, 9))

def bare(p):  # pinyin sans tons ni espaces, pour retrouver la bonne lecture
    return ''.join(c for c in unicodedata.normalize('NFD', p.lower()) if unicodedata.category(c) != 'Mn' and c.isalpha()).replace('ü', 'u')

def migrate_from_html():  # une seule fois : lit l'ancien bloc RAW de index.html
    html = open(HTML, encoding='utf8').read()
    blocks = {int(k): v for k, v in re.findall(r"(?:^|\n)(?:RAW\[)?(\d)(?:\] =|:) `(.*?)`", html, re.S)}
    rows = []
    for lvl in (1, 2, 3, 4):
        for line in blocks[lvl].split('\n'):
            h, p, f = line.split('|'); rows.append({'h': h, 'p': p, 'fr': f, 'app': lvl})
    return rows

def enrich(rows):
    missing = []
    for r in rows:
        r.setdefault('app20', r['app'])
        ref = REF.get(r['h'])
        if not ref: missing.append(r['h']); r.update(hsk2=None, hsk3=OFFICIAL.get(r['h']), freq=None, pos=[], cl=[]); continue
        rd = next((x for x in ref['r'] if bare(x['y']) == bare(r['p'])), ref['r'][0] if ref['r'] else {'c': []})
        r.update(hsk2=ref['o'], hsk3=OFFICIAL.get(r['h']), freq=ref['q'], pos=ref['pos'], cl=rd['c'][:2] if 'n' in ref['pos'] else [])
    for r in rows: r['app'] = r['hsk3'] if r.get('hsk3') and 1 <= r['hsk3'] <= 6 else r['app20']
    return missing

SPLIT = 5  # les mots enseignés à partir de ce niveau vont dans data/vocab-avance.json, chargé après le premier affichage

def compact(r):
    # Ligne compacte : [caractères, pinyin, français, niveau appli, niveau 3.0, niveau 2.0, fréquence, classificateurs, thème]
    return [r['h'], r['p'], r['fr'], r['app'], r['hsk3'] or 0, r['hsk2'] or 0, r['freq'] or 99999, ''.join(r['cl']), r.get('th', 'idees')]

def sense_ids(rows):  # même règle que l'appli : 1er sens = caractères seuls, suivants = caractères#n
    n, out = {}, []
    for r in rows:
        n[r['h']] = n.get(r['h'], 0) + 1; out.append(r['h'] if n[r['h']] == 1 else f"{r['h']}#{n[r['h']]}")
    return out

def split(rows):
    core = [r for r in rows if r['app'] < SPLIT]; adv = [r for r in rows if r['app'] >= SPLIT]
    # L'appli numérote les sens dans l'ordre core puis avancé : ces identifiants (clés de la progression) ne doivent pas changer
    full = dict(zip(map(id, rows), sense_ids(rows)))
    if [full[id(r)] for r in core + adv] != sense_ids(core + adv):
        sys.exit('Découpage impossible : il changerait l\'identifiant d\'un sens (un mot à plusieurs sens a son premier sens au niveau ' + str(SPLIT) + ' ou plus).')
    return core, adv

def js_block(rows):
    data = [compact(r) for r in rows]
    # Les données sont embarquées comme chaîne JSON lue par JSON.parse : le moteur JavaScript l'analyse bien plus vite
    # qu'un grand tableau littéral (recommandation de l'équipe V8 pour les données de plus de 10 Ko). Une ligne par mot.
    esc = lambda t: t.replace('\\', '\\\\').replace("'", "\\'").replace('</', '<\\/')  # chaîne JS entre apostrophes
    body = ',\\\n'.join(esc(json.dumps(d, ensure_ascii=False, separators=(',', ':'))) for d in data)  # \ en fin de ligne : continuation
    return ('// <vocab> (généré par tools/build-vocab.py depuis data/vocab.json : ne pas modifier à la main)\n'
            "const VOCAB = JSON.parse('[\\\n" + body + "]');\n"
            'const THEMES = ' + json.dumps([list(t) for t in THEMES], ensure_ascii=False) + ';\n// </vocab>')

def report(rows):
    lines = ['# Couverture du vocabulaire HSK', '', 'Généré par `tools/build-vocab.py --report`. Un mot est « couvert » s\'il a une traduction française dans `data/vocab.json`.', '']
    have = {r['h'] for r in rows}
    for sys_key, name, levels in (('n', 'Nouvel HSK, programme officiel 2025 (référence de l\'appli)', range(1, 8)), ('o', 'HSK 2.0', range(1, 7))):
        lines += [f'## {name}', '', '| Niveau | Mots du niveau | Couverts | Cumul couvert / cumul officiel | Manquants (les plus fréquents) |', '|---|---|---|---|---|']
        cum = cumhave = 0
        for lv in levels:
            pool = OFFICIAL.items() if sys_key == 'n' else ((w, v['o']) for w, v in REF.items())
            ws = sorted((w for w, l in pool if l == lv), key=lambda w: (REF.get(w) or {}).get('q') or 99999)
            got = [w for w in ws if w in have]; cum += len(ws); cumhave += len(got)
            miss = [w for w in ws if w not in have][:12]
            lab = '7-9' if lv == 7 else str(lv)
            lines.append(f'| {lab} | {len(ws)} | {len(got)} ({round(100 * len(got) / max(1, len(ws)))} %) | {cumhave} / {cum} ({round(100 * cumhave / max(1, cum))} %) | {" ".join(miss)} |')
        lines.append('')
    os.makedirs(os.path.join(ROOT, 'docs'), exist_ok=True)
    open(os.path.join(ROOT, 'docs', 'couverture.md'), 'w', encoding='utf8').write('\n'.join(lines) + '\n')
    print('Écrit docs/couverture.md')

def main():
    rows = json.load(open(VOCAB, encoding='utf8')) if os.path.exists(VOCAB) else migrate_from_html()
    missing = enrich(rows)
    if missing: print('Absents des listes officielles (gardés, sans niveau officiel) :', ' '.join(missing))
    json.dump(rows, open(VOCAB, 'w', encoding='utf8'), ensure_ascii=False, indent=0)
    html = open(HTML, encoding='utf8').read()
    core, adv = split(rows)
    block = js_block(core)
    json.dump([compact(r) for r in adv], open(os.path.join(ROOT, 'data', 'vocab-avance.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    if '// <vocab>' in html: html = re.sub(r'// <vocab>.*?// </vocab>', lambda m: block, html, flags=re.S)
    else:  # première fois : remplace l'ancien bloc RAW
        start = html.index('const RAW = {'); end = html.index('const WORDS = [];')
        html = html[:start] + block + '\n' + html[end:]
    open(HTML, 'w', encoding='utf8').write(html)
    print(f'{len(rows)} sens → data/vocab.json ; {len(core)} dans index.html (niveaux 1 à {SPLIT - 1}), {len(adv)} dans data/vocab-avance.json')
    # Liste officielle des niveaux 1 à 6 (programme 2025) pour l'écran « Listes » : [n°, niveau, mot, pinyin], ordre officiel
    off = []
    for line in open(os.path.join(ROOT, 'tools', 'content', 'hsk30-vocabulaire.tsv'), encoding='utf8'):
        if line.startswith('#'): continue
        n, lvl, word, _, py, *_ = line.rstrip('\n').split('\t')
        if lvl[0] in '123456': off.append([int(n), int(lvl[0]), word, py.replace('’', "'")])
    json.dump(off, open(os.path.join(ROOT, 'data', 'hsk-officiel.json'), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    print(f'{len(off)} mots officiels (niveaux 1-6) → data/hsk-officiel.json')
    if '--report' in sys.argv: report(rows)

if __name__ == '__main__': main()
