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
EXTRA = {1: {'安娜', '米饭'}, 2: {'上海'}}  # 米饭 : aussi le nom du chat de l'histoire 1-3

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

STORIES[2] = [
 ('2-anniversaire', '妹妹的生日', 'L\'anniversaire de ma petite sœur', 'Toute la famille prépare une fête pour la petite sœur.',
  [('今天是妹妹的生日。', 'Jīntiān shì mèimei de shēngrì.', 'Aujourd\'hui, c\'est l\'anniversaire de ma petite sœur.'),
   ('妈妈很早就起床了，开始做饭。', 'Māma hěn zǎo jiù qǐchuáng le, kāishǐ zuò fàn.', 'Maman s\'est levée très tôt pour commencer à cuisiner.'),
   ('爸爸去商店给妹妹买了一件红色的衣服。', 'Bàba qù shāngdiàn gěi mèimei mǎile yí jiàn hóngsè de yīfu.', 'Papa est allé au magasin acheter un vêtement rouge pour ma petite sœur.'),
   ('我送给她一本书，书里有很多好看的画。', 'Wǒ sònggěi tā yì běn shū, shū li yǒu hěn duō hǎokàn de huà.', 'Je lui ai offert un livre plein de jolis dessins.'),
   ('晚上，妹妹的同学也来了。', 'Wǎnshang, mèimei de tóngxué yě lái le.', 'Le soir, les camarades de ma sœur sont venus aussi.'),
   ('大家一起唱歌、跳舞，玩得很快乐。', 'Dàjiā yìqǐ chàng gē, tiàowǔ, wán de hěn kuàilè.', 'Tout le monde a chanté et dansé ensemble, on s\'est bien amusés.'),
   ('妹妹笑着说：“这是我最快乐的生日！”', 'Mèimei xiàozhe shuō: “Zhè shì wǒ zuì kuàilè de shēngrì!”', 'Ma sœur a dit en souriant : « C\'est mon plus bel anniversaire ! »')],
  [('Qu\'a offert le père ?', ['Un vêtement rouge', 'Un livre', 'Un gâteau']),
   ('Qui est venu le soir ?', ['Les camarades de la petite sœur', 'Les grands-parents', 'Personne']),
   ('Qu\'ont-ils fait ensemble ?', ['Chanté et dansé', 'Regardé un film', 'Fait du sport'])]),
 ('2-malade', '我生病了', 'Je suis malade', 'Un matin difficile, un coup de fil au professeur et une visite chez le médecin.',
  [('昨天晚上我觉得很累，眼睛也很累。', 'Zuótiān wǎnshang wǒ juéde hěn lèi, yǎnjing yě hěn lèi.', 'Hier soir, je me sentais très fatigué, j\'avais aussi les yeux fatigués.'),
   ('今天早上起床的时候，我身体很不好。', 'Jīntiān zǎoshang qǐchuáng de shíhou, wǒ shēntǐ hěn bù hǎo.', 'Ce matin, au lever, je me sentais très mal.'),
   ('我给老师打电话说：“老师，我生病了，今天不能去上课。”', 'Wǒ gěi lǎoshī dǎ diànhuà shuō: “Lǎoshī, wǒ shēngbìng le, jīntiān bù néng qù shàngkè.”', 'J\'ai appelé le professeur : « Je suis malade, je ne peux pas venir en cours aujourd\'hui. »'),
   ('老师说：“你快去医院看看吧。”', 'Lǎoshī shuō: “Nǐ kuài qù yīyuàn kànkan ba.”', 'Le professeur m\'a dit : « Va vite consulter à l\'hôpital. »'),
   ('医生让我吃药，多喝水，多休息。', 'Yīshēng ràng wǒ chī yào, duō hē shuǐ, duō xiūxi.', 'Le médecin m\'a dit de prendre des médicaments, de boire beaucoup d\'eau et de me reposer.'),
   ('回到家，我吃了药，就去睡觉了。', 'Huídào jiā, wǒ chīle yào, jiù qù shuìjiào le.', 'Rentré à la maison, j\'ai pris mes médicaments et je suis allé me coucher.'),
   ('第二天，我的身体已经好了。', 'Dì-èr tiān, wǒ de shēntǐ yǐjīng hǎo le.', 'Le lendemain, j\'étais déjà guéri.')],
  [('Qui appelle-t-il le matin ?', ['Son professeur', 'Le médecin', 'Sa mère']),
   ('Que lui conseille le médecin ?', ['Des médicaments, de l\'eau et du repos', 'D\'aller en cours', 'De faire du sport']),
   ('Comment va-t-il le lendemain ?', ['Il est guéri', 'Il est encore malade', 'Il est à l\'hôpital'])]),
 ('2-pekin', '去北京旅游', 'Voyage à Pékin', 'Un court séjour à Pékin, entre bons plats et neige.',
  [('我和朋友想去北京旅游。', 'Wǒ hé péngyou xiǎng qù Běijīng lǚyóu.', 'Mon ami et moi voulons faire un voyage à Pékin.'),
   ('我们坐飞机去，从上海到北京要两个小时。', 'Wǒmen zuò fēijī qù, cóng Shànghǎi dào Běijīng yào liǎng gè xiǎoshí.', 'Nous y allons en avion : de Shanghai à Pékin, il faut deux heures.'),
   ('到了北京，我们住在朋友家里。', 'Dàole Běijīng, wǒmen zhù zài péngyou jiā li.', 'Arrivés à Pékin, nous logeons chez un ami.'),
   ('他家离火车站很近，但是房间有点儿小。', 'Tā jiā lí huǒchēzhàn hěn jìn, dànshì fángjiān yǒudiǎnr xiǎo.', 'Sa maison est tout près de la gare, mais la chambre est un peu petite.'),
   ('第一天，我们去吃了北京的菜，非常好吃。', 'Dì-yī tiān, wǒmen qù chīle Běijīng de cài, fēicháng hǎochī.', 'Le premier jour, nous sommes allés goûter la cuisine de Pékin : délicieux.'),
   ('第二天下雪了，外面很冷。', 'Dì-èr tiān xià xuě le, wàimiàn hěn lěng.', 'Le deuxième jour, il a neigé et il faisait très froid dehors.'),
   ('但是北京下雪的时候非常漂亮！', 'Dànshì Běijīng xià xuě de shíhou fēicháng piàoliang!', 'Mais Pékin sous la neige, c\'est magnifique !'),
   ('我们玩得很快乐，还想再来。', 'Wǒmen wán de hěn kuàilè, hái xiǎng zài lái.', 'Nous nous sommes bien amusés et nous voulons revenir.')],
  [('Comment vont-ils à Pékin ?', ['En avion', 'En train', 'En voiture']),
   ('Quel est le défaut du logement ?', ['La chambre est un peu petite', 'C\'est loin de la gare', 'C\'est trop cher']),
   ('Quel temps fait-il le deuxième jour ?', ['Il neige', 'Il pleut', 'Il fait chaud'])]),
]

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
