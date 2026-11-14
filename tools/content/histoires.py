# -*- coding: utf-8 -*-
"""Histoires graduées de Xué Yuán : courts textes par niveau du nouvel HSK (programme 2025), écrits pour l'appli.

python3 -I tools/content/histoires.py relire 1    → contrôles + docs/histoires/hsk1.md (à relire)
python3 -I tools/content/histoires.py integrer 1  → contrôles + data/histoires.json (après accord)

Contrôles (mêmes outils que les fiches de grammaire) : chaque phrase n'emploie que des mots officiels du niveau ou des
niveaux inférieurs (plus EXTRA : prénoms, noms propres) ; pinyin comparé au dictionnaire ; 6 phrases au moins ;
2 questions de compréhension au moins, avec 3 choix distincts. Le vocabulaire de chaque histoire est affiché par
l'appli à partir de la liste de mots (pas de saisie à la main).
Toutes les histoires sont À FAIRE RELIRE PAR UN NATIF.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hsk2 import segment, check_pinyin
from grammaire import official_vocab, EXTRA as GEXTRA

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
EXTRA = {1: {'安娜', '米饭'}}  # 米饭 : aussi le nom du chat de l'histoire 1-3

# id, titre chinois, titre français, résumé, lignes [(zh, pinyin, fr)], questions [(question, [bonne, autre, autre])]
STORIES = {1: [
 ('1-journee', '安娜的一天', 'La journée d\'Anna', 'Une journée ordinaire d\'étudiante, du lever au coucher.',
  [('安娜是学生。', 'Ānnà shì xuésheng.', 'Anna est étudiante.'),
   ('她早上七点起床。', 'Tā zǎoshang qī diǎn qǐchuáng.', 'Elle se lève à sept heures du matin.'),
   ('她喝一杯茶，吃一点儿米饭。', 'Tā hē yì bēi chá, chī yìdiǎnr mǐfàn.', 'Elle boit une tasse de thé et mange un peu de riz.'),
   ('八点，她坐车去学校。', 'Bā diǎn, tā zuò chē qù xuéxiào.', 'À huit heures, elle prend le bus pour aller à l\'école.'),
   ('她在学校学习汉语。', 'Tā zài xuéxiào xuéxí Hànyǔ.', 'À l\'école, elle étudie le chinois.'),
   ('中午，她和同学在饭店吃饭。', 'Zhōngwǔ, tā hé tóngxué zài fàndiàn chī fàn.', 'À midi, elle déjeune au restaurant avec des camarades.'),
   ('下午五点，她回家。', 'Xiàwǔ wǔ diǎn, tā huí jiā.', 'À cinq heures de l\'après-midi, elle rentre à la maison.'),
   ('晚上，她看书，也看电视。', 'Wǎnshang, tā kàn shū, yě kàn diànshì.', 'Le soir, elle lit et regarde aussi la télévision.'),
   ('十一点，她睡觉了。', 'Shíyī diǎn, tā shuìjiào le.', 'À onze heures, elle va se coucher.')],
  [('À quelle heure Anna se lève-t-elle ?', ['À sept heures', 'À huit heures', 'À onze heures']),
   ('Que fait-elle à l\'école ?', ['Elle étudie le chinois', 'Elle regarde la télévision', 'Elle boit du thé']),
   ('Où déjeune-t-elle ?', ['Au restaurant, avec des camarades', 'À la maison', 'À l\'école, seule'])]),
 ('1-restaurant', '在饭店', 'Au restaurant', 'Petit Wang et sa petite amie commandent à manger et demandent l\'addition.',
  [('今天是星期六。', 'Jīntiān shì xīngqīliù.', 'Aujourd\'hui, c\'est samedi.'),
   ('小王和他的女朋友去饭店吃饭。', 'Xiǎo Wáng hé tā de nǚpéngyou qù fàndiàn chī fàn.', 'Petit Wang et sa petite amie vont manger au restaurant.'),
   ('小王问：“你想吃什么？”', 'Xiǎo Wáng wèn: “Nǐ xiǎng chī shénme?”', 'Petit Wang demande : « Qu\'est-ce que tu veux manger ? »'),
   ('女朋友说：“我想吃米饭和菜。”', 'Nǚpéngyou shuō: “Wǒ xiǎng chī mǐfàn hé cài.”', 'Sa petite amie répond : « Je voudrais du riz et des plats. »'),
   ('小王说：“我也想吃。我们还要两杯茶。”', 'Xiǎo Wáng shuō: “Wǒ yě xiǎng chī. Wǒmen hái yào liǎng bēi chá.”', 'Petit Wang dit : « Moi aussi. Et nous prendrons deux tasses de thé. »'),
   ('菜很好吃，茶也很好喝。', 'Cài hěn hǎochī, chá yě hěn hǎohē.', 'Les plats sont délicieux, et le thé est très bon.'),
   ('吃好了，小王问：“多少钱？”', 'Chīhǎo le, Xiǎo Wáng wèn: “Duōshao qián?”', 'Le repas fini, Petit Wang demande : « Combien ça coûte ? »'),
   ('“八十五块。”', '“Bāshíwǔ kuài.”', '« Quatre-vingt-cinq yuans. »')],
  [('Quel jour sommes-nous ?', ['Samedi', 'Lundi', 'Dimanche']),
   ('Que boivent-ils ?', ['Du thé', 'De l\'eau', 'Du lait']),
   ('Combien paient-ils ?', ['85 yuans', '58 yuans', '80 yuans'])]),
 ('1-chat', '小猫在哪儿？', 'Où est le chat ?', 'Le petit chat de la maison a disparu… mais pas très loin.',
  [('我家有一只小猫。', 'Wǒ jiā yǒu yì zhī xiǎo māo.', 'Nous avons un petit chat à la maison.'),
   ('它叫“米饭”。', 'Tā jiào “Mǐfàn”.', 'Il s\'appelle « Riz ».'),
   ('今天早上，我没看见米饭。', 'Jīntiān zǎoshang, wǒ méi kànjiàn Mǐfàn.', 'Ce matin, je n\'ai pas vu Riz.'),
   ('米饭在哪儿？', 'Mǐfàn zài nǎr?', 'Où est Riz ?'),
   ('它不在桌子下，也不在椅子上。', 'Tā bú zài zhuōzi xià, yě bú zài yǐzi shang.', 'Il n\'est pas sous la table, ni sur la chaise.'),
   ('妈妈说：“你看，它在你的衣服里！”', 'Māma shuō: “Nǐ kàn, tā zài nǐ de yīfu li!”', 'Maman dit : « Regarde, il est dans tes vêtements ! »'),
   ('米饭在我的衣服里睡觉呢。', 'Mǐfàn zài wǒ de yīfu li shuìjiào ne.', 'Riz est en train de dormir dans mes vêtements.')],
  [('Comment s\'appelle le chat ?', ['Riz (米饭)', 'Thé (茶)', 'Petit Wang']),
   ('Où était le chat ?', ['Dans les vêtements', 'Sous la table', 'Sur la chaise'])]),
]}

def check(level):
    vocab = official_vocab(level) | GEXTRA.get(level, set()) | EXTRA.get(level, set())
    problems = []
    for sid, tz, tf, d, lines, qs in STORIES[level]:
        if len(lines) < 6: problems.append(f'{sid} : {len(lines)} phrases (6 au moins)')
        if len(qs) < 2: problems.append(f'{sid} : {len(qs)} question(s)')
        for zh, py, fr in [(tz, None, None)] + list(lines):
            bad = [w for w, ok in segment(zh, vocab) if not ok]
            if bad: problems.append(f'{sid} : hors niveau {level} dans « {zh} » : {" ".join(bad)}')
            if py:
                for e in check_pinyin(zh, py): problems.append(f'{sid} : pinyin de « {zh} » : {e}')
        for q, o in qs:
            if len(set(o)) != 3: problems.append(f'{sid} : choix en double dans « {q} »')
    return problems

def relire(level):
    st = STORIES[level]
    L = [f'# Histoires graduées du HSK {level} : {len(st)} histoires à relire', '',
         f'Textes écrits pour l\'appli. Contrôles automatiques : chaque phrase n\'emploie que des mots officiels '
         f'{"du niveau 1" if level == 1 else f"des niveaux 1 à {level}"} du nouvel HSK (programme 2025), plus quelques noms propres ; pinyin comparé au dictionnaire.',
         '', 'Textes, traductions et questions : proposés par Claude, **à faire relire par un natif**.', '',
         f'Pour valider : dis « histoires HSK {level} OK », ou indique ce qu\'il faut corriger.', '']
    for k, (sid, tz, tf, d, lines, qs) in enumerate(st, 1):
        L += [f'## {k}. {tz} : {tf}', '', f'*{d}*', '']
        L += [f'{zh}  ' for zh, py, fr in lines] + ['']
        L += ['<details><summary>Pinyin et traduction</summary>', '']
        L += [f'- {zh} *{py}* — {fr}' for zh, py, fr in lines] + ['', '</details>', '', '**Questions** (bonne réponse en gras)', '']
        L += [f'- {q} → **{o[0]}** / {o[1]} / {o[2]}' for q, o in qs] + ['']
    c = check(level)
    L += ['## Contrôles automatiques', ''] + ([f'- {x}' for x in c] or ['- Aucune phrase hors niveau ; pinyin conforme.'])
    os.makedirs(os.path.join(ROOT, 'docs', 'histoires'), exist_ok=True)
    open(os.path.join(ROOT, 'docs', 'histoires', f'hsk{level}.md'), 'w', encoding='utf8').write('\n'.join(L) + '\n')
    print(f'{len(st)} histoires, {len(c)} problème(s) → docs/histoires/hsk{level}.md'); [print('  ' + x) for x in c]

def integrer(level):
    c = check(level)
    if c: print('Refusé :', *c, sep='\n  '); sys.exit(1)
    path = os.path.join(ROOT, 'data', 'histoires.json')
    data = json.load(open(path, encoding='utf8')) if os.path.exists(path) else {}
    data[str(level)] = [{'id': s[0], 'tz': s[1], 'tf': s[2], 'd': s[3], 'l': [list(x) for x in s[4]], 'q': [[q, o] for q, o in s[5]]} for s in STORIES[level]]
    json.dump(data, open(path, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    print(f'{len(STORIES[level])} histoires du HSK {level} → data/histoires.json')

if __name__ == '__main__':
    {'relire': relire, 'integrer': integrer}[sys.argv[1]](int(sys.argv[2]))
