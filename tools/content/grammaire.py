# -*- coding: utf-8 -*-
"""Fiches de grammaire de Xué Yuán, d'après la liste officielle de grammaire du nouvel HSK
(HSK 考试大纲, CLEC, programme 2025, « 语法大纲 »). Les fiches sont rédigées pour l'appli (pas de copie du
document) : chacune cite les points officiels qu'elle couvre.

python3 -I tools/content/grammaire.py relire 1    → contrôles + docs/grammaire/hsk1.md (à relire)
python3 -I tools/content/grammaire.py integrer 1  → contrôles + data/grammaire.json (après accord)

Contrôles : chaque phrase (exemples, questions et choix) n'emploie que des mots officiels du niveau ou
des niveaux inférieurs (plus EXTRA) ; le pinyin est comparé au dictionnaire pypinyin ; chaque fiche a
2 exemples et 2 questions ; tous les points officiels du niveau sont couverts.
Toutes les fiches sont À FAIRE RELIRE PAR UN NATIF.
Convention de pinyin : tons d'origine, sauf 一 et 不 notés tels qu'on les prononce ; ton neutre sans accent.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hsk2 import segment, check_pinyin  # mêmes contrôles que les unités HSK 2

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')

# Points de la liste officielle du niveau 1, regroupés (repère → intitulé officiel abrégé)
OFFICIAL = {1: {
  'préfixes 小—、第—': 'Morphèmes', 'suffixes —们、—边': 'Morphèmes', 'noms de lieu 上下里外前后': 'Noms',
  'verbes modaux 会能想要可以': 'Verbes', 'verbes séparables': 'Verbes', 'pronoms interrogatifs': 'Pronoms',
  'pronoms personnels': 'Pronoms', 'pronoms démonstratifs': 'Pronoms', 'nombres': 'Nombres',
  'classificateurs': 'Classificateurs', 'classificateurs de temps': 'Classificateurs',
  'adverbes de degré': 'Adverbes', '都1': 'Adverbes', '在、正在': 'Adverbes', '再1': 'Adverbes', '还1、也': 'Adverbes',
  'négation 不、没（有）、不要': 'Adverbes', 'préposition 在': 'Prépositions', 'prépositions 和、对': 'Prépositions',
  'conjonction 和2': 'Conjonctions', '的1': 'Particules', '了1': 'Particules', 'particules 吧、了2、吗、呢': 'Particules',
  'interjection 喂': 'Interjections', 'types de groupes': 'Groupes de mots', 'fonctions dans la phrase': 'Phrase',
  'complément de fréquence': 'Phrase', 'phrases à prédicat verbal, adjectival, nominal ; phrases sans sujet': 'Types de phrases',
  'questions oui/non, questions ouvertes, questions affirmatif-négatif': 'Types de phrases',
  'phrases impératives et exclamatives': 'Types de phrases', 'phrase en 是1': 'Phrases particulières',
  'phrase en 有1': 'Phrases particulières', 'phrases d\'existence 1': 'Phrases particulières',
  'verbes en série 1': 'Phrases particulières', 'double complément 1': 'Phrases particulières',
  'phrases coordonnées avec 也、还': 'Phrases complexes', 'aspect accompli (了1)': 'Aspect', 'changement (了2)': 'Aspect',
  'action en cours': 'Aspect', 'expression des sommes d\'argent': 'Expressions', 'ordinaux 第': 'Expressions',
  'dates, jours de la semaine, heures': 'Expressions'}}

# Mots admis en plus du vocabulaire officiel : prénoms, ville, et mots cités par la liste de grammaire elle-même
EXTRA = {1: {'安娜', '王', '小王', '北京', '杯', '没', '一杯', '两杯', '三点', '八点', '十二', '二十', '一百', '两百', '三十', '五十',
             '十五', '十八', '二零二六', '十一', '星期六', '星期一', '星期三', '星期天', '这个', '那个', '哪个', '一个', '一下', '多大'}}

# id, titre, structure, explication, points officiels couverts, exemples [(zh, py, fr)], questions [(phrase à trou, sens, [bonne, autre, autre])]
SHEETS = {1: [
 ('1-shi', 'Être : 是', 'A 是 B · A 不是 B',
  '是 relie deux noms : « A est B ». Il ne s\'emploie pas devant un adjectif (on dit 我很好, pas 我是好). La négation est toujours 不是.',
  ['phrase en 是1', 'phrases à prédicat verbal, adjectival, nominal ; phrases sans sujet'],
  [('我是学生。', 'Wǒ shì xuésheng.', 'Je suis étudiant.'),
   ('他不是老师，他是医生。', 'Tā bú shì lǎoshī, tā shì yīshēng.', 'Il n\'est pas professeur, il est médecin.')],
  [('她___我妈妈。', 'C\'est ma mère.', ['是', '有', '在']),
   ('我___是中国人。', 'Je ne suis pas chinois.', ['不', '没', '很'])]),
 ('1-you', 'Avoir : 有 et 没有', 'A 有 B · A 没有 B',
  '有 exprime la possession : « A a B ». Sa négation est toujours 没有 (jamais 不有).',
  ['phrase en 有1', 'négation 不、没（有）、不要'],
  [('我有一个哥哥。', 'Wǒ yǒu yí gè gēge.', 'J\'ai un grand frère.'),
   ('他没有电脑。', 'Tā méiyǒu diànnǎo.', 'Il n\'a pas d\'ordinateur.')],
  [('你___中文书吗？', 'As-tu des livres en chinois ?', ['有', '是', '在']),
   ('我___有猫。', 'Je n\'ai pas de chat.', ['没', '不', '很'])]),
 ('1-ma', 'Questions avec 吗', 'phrase + 吗 ?',
  'On ajoute 吗 à la fin d\'une phrase affirmative pour en faire une question fermée (réponse oui ou non). L\'ordre des mots ne change pas.',
  ['particules 吧、了2、吗、呢', 'questions oui/non, questions ouvertes, questions affirmatif-négatif'],
  [('你是老师吗？', 'Nǐ shì lǎoshī ma?', 'Es-tu professeur ?'),
   ('你喜欢喝茶吗？——喜欢。', 'Nǐ xǐhuan hē chá ma? — Xǐhuan.', 'Tu aimes boire du thé ? — Oui.')],
  [('你认识他___？', 'Tu le connais ?', ['吗', '的', '是']),
   ('他是你朋友吗？——___，他是我哥哥。', 'C\'est ton ami ? — Non, c\'est mon grand frère.', ['不是', '没有', '不要'])]),
 ('1-qui', 'Questions ouvertes : qui, quoi, où…', '谁 · 什么 · 哪 / 哪儿 · 几 · 多少 · 怎么 · 怎么样',
  'Le mot interrogatif se place là où se trouverait la réponse, sans changer l\'ordre de la phrase, et sans 吗. 几 sert pour les petits nombres (moins de 10) et demande un classificateur ; 多少 pour les grands nombres. 怎么 demande « comment (faire) », 怎么样 « comment est-ce, qu\'en penses-tu ».',
  ['pronoms interrogatifs', 'questions oui/non, questions ouvertes, questions affirmatif-négatif'],
  [('你叫什么名字？', 'Nǐ jiào shénme míngzi?', 'Comment t\'appelles-tu ?'),
   ('你家有几个人？', 'Nǐ jiā yǒu jǐ gè rén?', 'Combien de personnes y a-t-il dans ta famille ?')],
  [('他是___？——他是我朋友。', 'Qui est-ce ? — C\'est mon ami.', ['谁', '哪', '几']),
   ('你去___？——我去学校。', 'Où vas-tu ? — Je vais à l\'école.', ['哪儿', '什么', '怎么'])]),
 ('1-a-bu-a', 'Questions « oui ou non » : 去不去', 'verbe + 不 + verbe ?',
  'On pose une question en juxtaposant la forme positive et la forme négative du verbe ou de l\'adjectif : 是不是, 去不去, 好不好. Pas de 吗 dans ce cas. Avec 有, on dit 有没有.',
  ['questions oui/non, questions ouvertes, questions affirmatif-négatif'],
  [('你是不是学生？', 'Nǐ shì bu shì xuésheng?', 'Es-tu étudiant ou pas ?'),
   ('明天你来不来？', 'Míngtiān nǐ lái bu lái?', 'Tu viens demain ou pas ?')],
  [('你有___有中文名字？', 'As-tu un nom chinois ?', ['没', '不', '很']),
   ('这个菜好不好吃___', 'Ce plat est-il bon ?', ['？', '吗？', '吧？'])]),
 ('1-ne', 'La particule 呢', 'nom + 呢 ? · phrase + 呢',
  '呢 a trois emplois au niveau 1 : « et toi ? » (你呢？) pour renvoyer la question ; « où est… ? » (我的书呢？) ; et en fin de phrase, avec 在 ou 正在, pour souligner qu\'une action est en cours (他在看书呢).',
  ['particules 吧、了2、吗、呢', 'action en cours'],
  [('我很好，你呢？', 'Wǒ hěn hǎo, nǐ ne?', 'Je vais bien, et toi ?'),
   ('妈妈呢？——她在睡觉呢。', 'Māma ne? — Tā zài shuìjiào ne.', 'Où est maman ? — Elle dort.')],
  [('我是北京人，你___？', 'Je suis de Pékin, et toi ?', ['呢', '吗', '吧']),
   ('我的手机___？', 'Où est mon téléphone ?', ['呢', '吗', '了'])]),
 ('1-ba', 'Proposer avec 吧', 'phrase + 吧',
  '吧 en fin de phrase adoucit : il transforme un ordre en proposition (« allons… », « fais donc… ») ou demande une confirmation (« c\'est bien ça ? »).',
  ['particules 吧、了2、吗、呢', 'phrases impératives et exclamatives'],
  [('我们去吃饭吧！', 'Wǒmen qù chī fàn ba!', 'Allons manger !'),
   ('你是安娜吧？', 'Nǐ shì Ānnà ba?', 'Tu es Anna, c\'est ça ?')],
  [('太晚了，我们回家___。', 'Il est tard, rentrons.', ['吧', '吗', '呢']),
   ('你是新同学___？', 'Tu es le nouveau camarade, c\'est ça ?', ['吧', '了', '的'])]),
 ('1-pronoms', 'Les pronoms personnels et 们', '我 · 你 · 您 · 他 / 她 / 它 + 们',
  '们 met les pronoms au pluriel : 我们, 你们, 他们. 您 est le « vous » de politesse pour une seule personne. 他, 她 et 它 se prononcent tous tā ; 它 désigne un animal ou une chose. 大家 = « tout le monde ».',
  ['pronoms personnels', 'suffixes —们、—边'],
  [('我们是同学。', 'Wǒmen shì tóngxué.', 'Nous sommes camarades de classe.'),
   ('大家好！', 'Dàjiā hǎo!', 'Bonjour à tous !')],
  [('老师，___好！', 'Bonjour, professeur ! (poli)', ['您', '你们', '它']),
   ('我有一只猫，___很漂亮。', 'J\'ai un chat, il est très beau.', ['它', '她们', '我们'])]),
 ('1-demo', 'Ce, ces : 这 et 那', '这 / 那 (+ classificateur) + nom · 这儿 · 那儿 · 这些 · 有的',
  '这 = ceci, proche ; 那 = cela, éloigné. Devant un nom, on ajoute normalement un classificateur : 这个人, 那本书. 这儿 / 这里 = ici, 那儿 / 那里 = là-bas. 这些 / 那些 = ces… (pluriel). 有的 / 有些 = certains.',
  ['pronoms démonstratifs'],
  [('这是我的书，那是他的书。', 'Zhè shì wǒ de shū, nà shì tā de shū.', 'Ceci est mon livre, cela est son livre.'),
   ('这些苹果很好吃。', 'Zhèxiē píngguǒ hěn hǎochī.', 'Ces pommes sont délicieuses.')],
  [('___个人是谁？', 'Qui est cette personne-là ?', ['那', '哪', '这儿']),
   ('我在___，你在哪儿？', 'Je suis ici, et toi où es-tu ?', ['这儿', '这些', '这个'])]),
 ('1-nombres', 'Compter : 一 à 千, 二 et 两', '数字 · 两 + classificateur',
  'Les nombres se construisent comme on les dit : 十一 (10 + 1), 二十 (2 × 10), 一百, 一千. 零 marque un zéro au milieu : 一百零五. Devant un classificateur, « deux » se dit 两 et non 二 : 两个人, 两点. 半 = demi : 一个半小时.',
  ['nombres'],
  [('我们学校有三十个老师。', 'Wǒmen xuéxiào yǒu sānshí gè lǎoshī.', 'Il y a trente professeurs dans notre école.'),
   ('我有两个妹妹。', 'Wǒ yǒu liǎng gè mèimei.', 'J\'ai deux petites sœurs.')],
  [('我要___杯茶。', 'Je voudrais deux tasses de thé.', ['两', '二', '第二']),
   ('他今年___岁。', 'Il a dix-huit ans cette année.', ['十八', '八十', '一八'])]),
 ('1-classif', 'Les classificateurs', 'nombre / 这 / 那 + classificateur + nom',
  'Entre un nombre (ou 这, 那, 几) et un nom, le chinois place toujours un classificateur. 个 est le plus courant ; 本 pour les livres, 口 pour les membres d\'une famille, 家 pour les magasins et entreprises, 件 pour les vêtements du haut et les affaires, 只 pour beaucoup d\'animaux, 块 et 元 pour l\'argent. Un récipient peut servir de classificateur : 一杯水.',
  ['classificateurs', 'types de groupes'],
  [('我买了三本书。', 'Wǒ mǎile sān běn shū.', 'J\'ai acheté trois livres.'),
   ('他家有四口人。', 'Tā jiā yǒu sì kǒu rén.', 'Il y a quatre personnes dans sa famille.')],
  [('这___衣服很漂亮。', 'Ce vêtement est très joli.', ['件', '本', '口']),
   ('那儿有一___狗。', 'Il y a un chien là-bas.', ['只', '本', '家'])]),
 ('1-argent', 'Les prix', '数字 + 块 / 元 · 多少钱？',
  'À l\'oral, on compte en 块 (kuài) ; à l\'écrit et sur les étiquettes, en 元 (yuán). On demande le prix avec 多少钱 ?',
  ['expression des sommes d\'argent', 'classificateurs'],
  [('这个多少钱？——十五块。', 'Zhège duōshao qián? — Shíwǔ kuài.', 'Combien coûte ceci ? — Quinze yuans.'),
   ('一杯茶二十元。', 'Yì bēi chá èrshí yuán.', 'Une tasse de thé coûte vingt yuans.')],
  [('这本书多少___？', 'Combien coûte ce livre ?', ['钱', '本', '个']),
   ('苹果五___一个。', 'Les pommes sont à cinq yuans pièce.', ['块', '本', '口'])]),
 ('1-date', 'Dates, jours et heures', 'année + 月 + 日 / 号 · 星期 + numéro · 点 + 分',
  'On va du plus grand au plus petit : année, mois, jour, puis heure. Les mois se comptent : 一月 (janvier) à 十二月 ; les jours de la semaine aussi : 星期一 (lundi) à 星期六, puis 星期天 / 星期日. 号 est le jour du mois à l\'oral (日 à l\'écrit). L\'heure : 八点 (8 h), 八点十分 (8 h 10), 八点半 (8 h 30). Pour l\'âge : 岁.',
  ['dates, jours de la semaine, heures', 'classificateurs de temps', 'phrases à prédicat verbal, adjectival, nominal ; phrases sans sujet'],
  [('今天三月十五号，星期三。', 'Jīntiān sān yuè shíwǔ hào, xīngqīsān.', 'Aujourd\'hui, c\'est le 15 mars, mercredi.'),
   ('现在几点？——八点半。', 'Xiànzài jǐ diǎn? — Bā diǎn bàn.', 'Quelle heure est-il ? — Huit heures et demie.')],
  [('明天是星期___？', 'Quel jour sommes-nous demain ?', ['几', '什么', '多少']),
   ('我们三___见。', 'On se voit à trois heures.', ['点', '岁', '号'])]),
 ('1-nompredicat', 'Phrases sans verbe : 今天星期一', 'sujet + date / âge / prix',
  'Pour une date, une heure, un âge ou un prix, le chinois peut se passer de verbe : le nom sert directement de prédicat. Mais à la forme négative, il faut 不是.',
  ['phrases à prédicat verbal, adjectival, nominal ; phrases sans sujet', 'fonctions dans la phrase'],
  [('我今年二十岁。', 'Wǒ jīnnián èrshí suì.', 'J\'ai vingt ans cette année.'),
   ('今天不是星期六。', 'Jīntiān bú shì xīngqīliù.', 'Aujourd\'hui, ce n\'est pas samedi.')],
  [('你今年多大？——我___岁。', 'Quel âge as-tu ? — J\'ai dix-huit ans.', ['十八', '十八个', '是十八个']),
   ('明天___星期天。', 'Demain, ce n\'est pas dimanche.', ['不是', '没', '不'])]),
 ('1-xiao-di', 'Préfixes 小 et 第', '小 + nom de famille · 第 + nombre',
  '小 devant un nom de famille donne un appel familier pour une personne plus jeune : 小王. 第 devant un nombre forme un ordinal : 第一 (premier), 第二 (deuxième).',
  ['préfixes 小—、第—', 'ordinaux 第'],
  [('小王，你好！', 'Xiǎo Wáng, nǐ hǎo!', 'Salut, Petit Wang !'),
   ('这是我的第一本中文书。', 'Zhè shì wǒ de dì yī běn Zhōngwén shū.', 'C\'est mon premier livre en chinois.')],
  [('他是___一个来的。', 'C\'est lui qui est arrivé le premier.', ['第', '小', '几']),
   ('___王是我的同学。', 'Petit Wang est mon camarade.', ['小', '第', '大'])]),
 ('1-de', 'La particule 的', 'nom / pronom / adjectif + 的 + nom',
  '的 relie un déterminant au nom qu\'il précise, toujours placé avant : 我的书 (mon livre), 妈妈的朋友 (l\'amie de maman), 漂亮的衣服 (de beaux vêtements). Avec la famille proche ou un groupe, on l\'omet souvent : 我妈妈, 我们学校.',
  ['的1', 'fonctions dans la phrase', 'types de groupes'],
  [('这是我的手机。', 'Zhè shì wǒ de shǒujī.', 'C\'est mon téléphone.'),
   ('她是我妈妈的朋友。', 'Tā shì wǒ māma de péngyou.', 'C\'est une amie de ma mère.')],
  [('这是谁___书？', 'À qui est ce livre ?', ['的', '了', '吗']),
   ('那是我___。', 'C\'est le mien.', ['的', '了', '呢'])]),
 ('1-degre', 'Adjectifs et degré : 很, 太, 非常…', '(sujet) + 很 / 非常 / 太…了 / 真 / 有点儿 + adjectif',
  'Un adjectif peut servir directement de prédicat, sans 是 : 天气很冷. 很 y est souvent presque vide de sens (« il fait froid »). 非常 = très ; 太…了 = trop, ou « vraiment » dans une exclamation ; 真 = vraiment ; 有点儿 = un peu (souvent pour une gêne).',
  ['adverbes de degré', 'phrases à prédicat verbal, adjectival, nominal ; phrases sans sujet', 'phrases impératives et exclamatives'],
  [('今天非常冷。', 'Jīntiān fēicháng lěng.', 'Il fait très froid aujourd\'hui.'),
   ('这个菜太好吃了！', 'Zhège cài tài hǎochī le!', 'Ce plat est vraiment délicieux !')],
  [('我___高兴。', 'Je suis content.', ['很', '是', '的']),
   ('这件衣服___点儿贵。', 'Ce vêtement est un peu cher.', ['有', '是', '很'])]),
 ('1-dou-ye', 'Aussi, tous : 也, 都, 还', 'sujet + 也 / 都 / 还 + verbe',
  'Ces adverbes se placent toujours avant le verbe, jamais en début de phrase. 也 = aussi ; 都 = tous, tout (il reprend ce qui précède) ; avec les deux, l\'ordre est 也都. 还 = encore, en plus. 也 et 还 relient aussi deux propositions : « …, et aussi… ».',
  ['都1', '还1、也', 'phrases coordonnées avec 也、还'],
  [('我们都是学生。', 'Wǒmen dōu shì xuésheng.', 'Nous sommes tous étudiants.'),
   ('我喜欢喝茶，也喜欢喝水。', 'Wǒ xǐhuan hē chá, yě xǐhuan hē shuǐ.', 'J\'aime boire du thé, et j\'aime aussi boire de l\'eau.')],
  [('他是老师，我___是老师。', 'Il est professeur, et moi aussi.', ['也', '都', '和']),
   ('我爸爸、妈妈___是医生。', 'Mon père et ma mère sont tous deux médecins.', ['都', '和', '的'])]),
 ('1-neg', 'Dire non : 不, 没（有）, 不要', '不 + verbe / adjectif · 没（有） + verbe · 不要 + verbe',
  '不 nie le présent, le futur, l\'habitude ou un adjectif : 我不去. 没（有） nie une action passée ou qui n\'a pas eu lieu, et le verbe 有 : 我没去. 不要 + verbe interdit : « ne… pas ! ».',
  ['négation 不、没（有）、不要', 'phrases impératives et exclamatives'],
  [('我明天不去学校。', 'Wǒ míngtiān bú qù xuéxiào.', 'Je ne vais pas à l\'école demain.'),
   ('昨天我没去学校。', 'Zuótiān wǒ méi qù xuéxiào.', 'Hier, je ne suis pas allé à l\'école.')],
  [('上课了，___说话！', 'Le cours commence, ne parlez pas !', ['不要', '没有', '没']),
   ('他昨天___来。', 'Il n\'est pas venu hier.', ['没', '不', '不要'])]),
 ('1-modaux', 'Pouvoir, vouloir : 会, 能, 可以, 想, 要', 'sujet + verbe modal + verbe',
  '会 = savoir faire (appris) ; 能 = pouvoir (capacité, circonstances) ; 可以 = avoir la permission ; 想 = avoir envie de ; 要 = vouloir, devoir, ou « aller » (futur proche). La négation se met devant le modal : 不会, 不能, 不想.',
  ['verbes modaux 会能想要可以'],
  [('我会说汉语。', 'Wǒ huì shuō Hànyǔ.', 'Je sais parler chinois.'),
   ('我可以坐这儿吗？', 'Wǒ kěyǐ zuò zhèr ma?', 'Je peux m\'asseoir ici ?')],
  [('我___去中国。', 'J\'ai envie d\'aller en Chine.', ['想', '是', '的']),
   ('你___写汉字吗？', 'Sais-tu écrire les caractères chinois ?', ['会', '是', '了'])]),
 ('1-zai', 'Où et quand : 在', 'sujet + 在 + lieu + verbe',
  '在 + lieu indique où l\'on se trouve (我在家) ou, placé avant le verbe, où se passe l\'action (我在学校学习). En chinois, le lieu et le moment se placent avant le verbe, jamais après.',
  ['préposition 在', 'fonctions dans la phrase', 'types de groupes'],
  [('我在家看电视。', 'Wǒ zài jiā kàn diànshì.', 'Je regarde la télé à la maison.'),
   ('他明天在学校吗？', 'Tā míngtiān zài xuéxiào ma?', 'Sera-t-il à l\'école demain ?')],
  [('我___商店买东西。', 'J\'achète des choses au magasin.', ['在', '是', '有']),
   ('我们___上课。', 'Nous avons cours demain à l\'école.', ['明天在学校', '在学校明天', '上课明天'])]),
 ('1-progressif', 'Être en train de : 在, 正在, 呢', 'sujet + 在 / 正在 + verbe (+ 呢)',
  '在 ou 正在 avant le verbe disent qu\'une action est en cours. On peut ajouter 呢 en fin de phrase, ou n\'utiliser que 呢 à l\'oral.',
  ['在、正在', 'action en cours', 'particules 吧、了2、吗、呢'],
  [('他正在打电话。', 'Tā zhèngzài dǎ diànhuà.', 'Il est en train de téléphoner.'),
   ('妈妈在做饭呢。', 'Māma zài zuò fàn ne.', 'Maman est en train de faire à manger.')],
  [('你在做什么？——我___看书。', 'Que fais-tu ? — Je suis en train de lire.', ['在', '了', '是']),
   ('他们在吃饭___。', 'Ils sont en train de manger.', ['呢', '的', '是'])]),
 ('1-fangwei', 'Devant, derrière, dedans : les noms de lieu', 'nom + 上 / 下 / 里 / 外 / 前 / 后（边）',
  'Pour situer, on ajoute après le nom un mot de position : 桌子上 (sur la table), 家里 (à la maison), 学校前边 (devant l\'école). 边 se colle à ces mots : 上边, 里边, 前边.',
  ['noms de lieu 上下里外前后', 'suffixes —们、—边', 'types de groupes'],
  [('书在桌子上。', 'Shū zài zhuōzi shang.', 'Le livre est sur la table.'),
   ('医院在学校后边。', 'Yīyuàn zài xuéxiào hòubian.', 'L\'hôpital est derrière l\'école.')],
  [('猫在椅子___。', 'Le chat est sous la chaise.', ['下', '下午', '前天']),
   ('杯子里___水。', 'Il y a de l\'eau dans le verre.', ['有', '是', '在'])]),
 ('1-existence', 'Il y a… : lieu + 有 / 是', 'lieu + 有 + nombre + classificateur + nom · lieu + 是 + nom',
  'Pour dire ce qui se trouve à un endroit, on commence par le lieu : 桌子上有一本书 (« sur la table, il y a un livre »). Avec 是, on identifie ce qui occupe l\'endroit : 学校前边是商店 (« devant l\'école, c\'est un magasin »).',
  ['phrases d\'existence 1'],
  [('我家前边有一个商店。', 'Wǒ jiā qiánbian yǒu yí gè shāngdiàn.', 'Il y a un magasin devant chez moi.'),
   ('医院后边是学校。', 'Yīyuàn hòubian shì xuéxiào.', 'Derrière l\'hôpital, c\'est l\'école.')],
  [('桌子上___三本书。', 'Il y a trois livres sur la table.', ['有', '在', '个']),
   ('___有很多人。', 'Il y a beaucoup de monde dans le magasin.', ['商店里', '在商店', '商店是'])]),
 ('1-he-dui', 'Avec, pour : 和 et 对', 'A 和 B · 和 + personne + verbe · 对 + personne + adjectif / verbe',
  '和 relie deux noms : 我和你 (toi et moi) ; il ne relie pas deux verbes ou deux phrases. Avant un verbe, 和 + personne = « avec » : 我和朋友去. 对 + personne = « envers, pour » : 老师对我很好.',
  ['prépositions 和、对', 'conjonction 和2'],
  [('我和妈妈去商店。', 'Wǒ hé māma qù shāngdiàn.', 'Je vais au magasin avec maman.'),
   ('他对我们很好。', 'Tā duì wǒmen hěn hǎo.', 'Il est très gentil avec nous.')],
  [('我爸爸___妈妈都是老师。', 'Mon père et ma mère sont professeurs.', ['和', '对', '也']),
   ('老师___学生说话。', 'Le professeur parle aux élèves.', ['对', '是', '的'])]),
 ('1-le1', 'Action accomplie : 了 après le verbe', 'verbe + 了 (+ quantité + objet)',
  '了 juste après le verbe indique que l\'action est accomplie : 我买了一本书. L\'objet porte souvent une quantité. La négation n\'utilise pas 了 mais 没（有）: 我没买.',
  ['了1', 'aspect accompli (了1)'],
  [('我喝了两杯茶。', 'Wǒ hēle liǎng bēi chá.', 'J\'ai bu deux tasses de thé.'),
   ('昨天我看了一个电影。', 'Zuótiān wǒ kànle yí gè diànyǐng.', 'Hier, j\'ai vu un film.')],
  [('他买___三个苹果。', 'Il a acheté trois pommes.', ['了', '呢', '吗']),
   ('我昨天___去商店。', 'Je ne suis pas allé au magasin hier.', ['没', '不', '了'])]),
 ('1-le2', 'Changement de situation : 了 en fin de phrase', 'phrase + 了',
  '了 en fin de phrase signale un changement ou une situation nouvelle : 下雨了 (il s\'est mis à pleuvoir), 我会说汉语了 (« maintenant je sais parler chinois »). Une phrase peut n\'avoir aucun sujet : 下雨了！',
  ['particules 吧、了2、吗、呢', 'changement (了2)', 'phrases à prédicat verbal, adjectival, nominal ; phrases sans sujet'],
  [('下雨了！', 'Xià yǔ le!', 'Il pleut ! (il s\'est mis à pleuvoir)'),
   ('我现在会写汉字了。', 'Wǒ xiànzài huì xiě Hànzì le.', 'Maintenant, je sais écrire les caractères.')],
  [('八点___，我们去学校吧。', 'Il est déjà huit heures, allons à l\'école.', ['了', '呢', '的']),
   ('他今年二十岁___。', 'Il a (maintenant) vingt ans cette année.', ['了', '吗', '呢'])]),
 ('1-zai-encore', 'Encore une fois : 再', '再 + verbe',
  '再 = « encore, de nouveau » pour une action à venir : 再见 (« au revoir », litt. « se revoir »), 请再说一下.',
  ['再1'],
  [('请你再说一下。', 'Qǐng nǐ zài shuō yíxià.', 'Peux-tu le redire, s\'il te plaît ?'),
   ('明天再来吧。', 'Míngtiān zài lái ba.', 'Reviens demain.')],
  [('我们明天___见！', 'À demain !', ['再', '还', '也']),
   ('这个菜很好吃，我想___吃一点儿。', 'Ce plat est délicieux, j\'en reprendrais bien un peu.', ['再', '在', '都'])]),
 ('1-liheci', 'Verbes séparables : 睡觉, 上课…', 'verbe + (了 / quantité…) + objet',
  'Certains verbes sont faits d\'un verbe et de son objet : 睡觉 (dormir), 上课 (aller en cours), 说话 (parler), 看病 (consulter un médecin), 上班, 下班, 生病. On peut glisser des mots entre les deux : 睡了一个小时觉 ; ils ne prennent pas d\'objet supplémentaire.',
  ['verbes séparables'],
  [('我十一点睡觉。', 'Wǒ shíyī diǎn shuìjiào.', 'Je me couche à onze heures.'),
   ('他生病了，去医院看病。', 'Tā shēngbìng le, qù yīyuàn kànbìng.', 'Il est malade, il va consulter à l\'hôpital.')],
  [('我们八点___课。', 'Nous commençons les cours à huit heures.', ['上', '下', '去']),
   ('他生病了，去医院___。', 'Il est malade, il va consulter à l\'hôpital.', ['看病', '病看', '看医院'])]),
 ('1-liandong', 'Deux verbes à la suite', 'sujet + verbe 1 (+ objet) + verbe 2 (+ objet)',
  'Le chinois enchaîne deux verbes sans mot de liaison. Le second exprime souvent le but du premier : 去商店买东西 (aller au magasin pour acheter des choses). Le premier peut aussi être le moyen : 坐飞机去北京 (aller à Pékin en avion).',
  ['verbes en série 1'],
  [('我去商店买东西。', 'Wǒ qù shāngdiàn mǎi dōngxi.', 'Je vais au magasin acheter des choses.'),
   ('他坐出租车去医院。', 'Tā zuò chūzūchē qù yīyuàn.', 'Il va à l\'hôpital en taxi.')],
  [('我们去饭店___。', 'Nous allons manger au restaurant.', ['吃饭', '在吃饭', '吃饭去']),
   ('她___去学校。', 'Elle va à l\'école en voiture.', ['坐车', '车坐', '在车'])]),
 ('1-double', 'Deux compléments : 给你一本书', 'sujet + verbe + personne + chose',
  'Avec des verbes comme 给 (donner) ou 问 (demander), la personne vient d\'abord, puis la chose : 我给你一本书 (je te donne un livre), 我问老师一个问题 (je pose une question au professeur).',
  ['double complément 1'],
  [('妈妈给我一个苹果。', 'Māma gěi wǒ yí gè píngguǒ.', 'Maman me donne une pomme.'),
   ('我想问你一个问题。', 'Wǒ xiǎng wèn nǐ yí gè wèntí.', 'Je voudrais te poser une question.')],
  [('请___我一杯水。', 'Donne-moi un verre d\'eau, s\'il te plaît.', ['给', '是', '在']),
   ('学生问___一个问题。', 'L\'élève pose une question au professeur.', ['老师', '的老师', '老师的'])]),
 ('1-yixia', 'Un petit peu : 一下', 'verbe + 一下',
  'Après un verbe, 一下 indique une action brève ou adoucit une demande : 看一下 (jeter un œil), 等一下 (attendre un instant). C\'est le complément de fréquence du niveau 1.',
  ['complément de fréquence'],
  [('我看一下。', 'Wǒ kàn yíxià.', 'Je jette un œil.'),
   ('请你来一下。', 'Qǐng nǐ lái yíxià.', 'Viens un instant, s\'il te plaît.')],
  [('你听___，这是什么？', 'Écoute un peu : qu\'est-ce que c\'est ?', ['一下', '一个', '一点儿']),
   ('我想___一下这本书。', 'Je voudrais regarder un peu ce livre.', ['看', '看了', '在看'])]),
 ('1-imperatif', 'Demander, s\'exclamer, appeler', '请 + verbe · 不要 + verbe · 太…了！ · 喂',
  'Pour demander poliment : 请 + verbe (请坐, asseyez-vous). Pour interdire : 不要 + verbe. Pour s\'exclamer : 太…了 ! ou 真… ! 喂 sert à appeler quelqu\'un ou à décrocher le téléphone (on dit souvent wéi au téléphone).',
  ['phrases impératives et exclamatives', 'interjection 喂'],
  [('请喝茶。', 'Qǐng hē chá.', 'Prenez du thé, je vous en prie.'),
   ('喂，你好！我是小王。', 'Wèi, nǐ hǎo! Wǒ shì Xiǎo Wáng.', 'Allô, bonjour ! C\'est Petit Wang.')],
  [('___坐！', 'Asseyez-vous, je vous prie !', ['请', '谢谢', '对不起']),
   ('这个电影___好看了！', 'Ce film est vraiment génial !', ['太', '很', '有点儿'])]),
 ('1-ordre', 'L\'ordre des mots', 'sujet + moment + lieu + verbe + objet',
  'L\'ordre de base est sujet + verbe + objet, comme en français. Mais tout ce qui précise le verbe (moment, lieu, manière, adverbes) se place AVANT lui : 我明天在家看书. Le moment peut aussi ouvrir la phrase : 明天我在家看书. Ce qui précise un nom se place avant le nom.',
  ['fonctions dans la phrase', 'types de groupes'],
  [('我明天在家看书。', 'Wǒ míngtiān zài jiā kàn shū.', 'Demain, je lis à la maison.'),
   ('他今天早上在家喝茶。', 'Tā jīntiān zǎoshang zài jiā hē chá.', 'Ce matin, il boit du thé à la maison.')],
  [('我___学汉语。', 'J\'étudie le chinois à l\'école.', ['在学校', '学校在', '在学校里在']),
   ('___我去北京。', 'Je vais à Pékin demain.', ['明天', '在明天', '明天了'])]),
]}

import grammaire_hsk2 as _g2
OFFICIAL[2] = {p: '' for p in _g2.OFFICIAL}
SHEETS[2] = _g2.SHEETS
EXTRA[2] = EXTRA[1] | _g2.EXTRA
import grammaire_hsk3 as _g3
OFFICIAL[3] = {p: '' for p in _g3.OFFICIAL}
SHEETS[3] = _g3.SHEETS
EXTRA[3] = EXTRA[2] | _g3.EXTRA
import grammaire_hsk4 as _g4
OFFICIAL[4] = {p: '' for p in _g4.OFFICIAL}
SHEETS[4] = _g4.SHEETS
EXTRA[4] = EXTRA[3] | _g4.EXTRA
import grammaire_hsk5 as _g5
OFFICIAL[5] = {p: '' for p in _g5.OFFICIAL}
SHEETS[5] = _g5.SHEETS
EXTRA[5] = EXTRA[4] | _g5.EXTRA

def official_vocab(level):
    out = set()
    for line in open(os.path.join(ROOT, 'tools', 'content', 'hsk30-vocabulaire.tsv'), encoding='utf8'):
        if line.startswith('#'): continue
        n, lvl, w, *_ = line.split('\t')
        if not lvl.startswith('7') and int(lvl[0]) <= level: out.add(w)
    return out

def check(level):
    vocab = official_vocab(level) | EXTRA.get(level, set())
    sheets = SHEETS[level]; problems = []
    ids = [s[0] for s in sheets]
    if len(set(ids)) != len(ids): problems.append('identifiants en double')
    covered = {p for s in sheets for p in s[4]}
    for p in OFFICIAL[level]:
        if p not in covered: problems.append(f'point officiel non couvert : {p}')
    for p in covered - set(OFFICIAL[level]): problems.append(f'point inconnu : {p}')
    for sid, title, struct, expl, pts, ex, qs in sheets:
        if len(ex) != 2 or len(qs) != 2: problems.append(f'{sid} : {len(ex)} exemples, {len(qs)} questions')
        texts = [zh for zh, py, fr in ex] + [q.replace('___', opts[0]) for q, fr, opts in qs] + [opts[0] for q, fr, opts in qs]
        chars = {c for w in vocab for c in w}
        for q, fr, opts in qs:  # les mauvais choix peuvent être des formes fautives : on vérifie seulement leurs caractères
            bad = [c for o in opts[1:] for c in o if '\u4e00' <= c <= '\u9fff' and c not in chars]
            if bad: problems.append(f'{sid} : caractère hors niveau {level} dans les choix de « {q} » : {" ".join(bad)}')
        for t in texts:
            bad = [w for w, ok in segment(t, vocab) if not ok]
            if bad: problems.append(f'{sid} : hors niveau {level} dans « {t} » : {" ".join(bad)}')
        for zh, py, fr in ex:
            for e in check_pinyin(zh, py): problems.append(f'{sid} : pinyin de « {zh} » : {e}')
        for q, fr, opts in qs:
            if '___' not in q: problems.append(f'{sid} : pas de trou dans « {q} »')
            if len(set(opts)) != 3: problems.append(f'{sid} : choix en double dans « {q} »')
    return problems

def relire(level):
    sheets = SHEETS[level]
    L = [f'# Grammaire du HSK {level} : {len(sheets)} fiches à relire', '',
         f'Source : liste officielle de grammaire du nouvel HSK (HSK 考试大纲, CLEC, programme 2025), niveau {level}. '
         f'Les {len(OFFICIAL[level])} points officiels du niveau sont regroupés en {len(sheets)} fiches rédigées pour l\'appli ; '
         'chaque fiche indique les points qu\'elle couvre.', '',
         'Explications, exemples et questions : proposés par Claude, **à faire relire par un natif**. '
         f'Contrôles automatiques : chaque phrase n\'emploie que des mots officiels {"du niveau 1" if level == 1 else f"des niveaux 1 à {level}"} ; pinyin comparé au dictionnaire.', '',
         'Pour valider : dis « grammaire HSK ' + str(level) + ' OK », ou indique les fiches à corriger.', '']
    for k, (sid, title, struct, expl, pts, ex, qs) in enumerate(sheets, 1):
        L += [f'## {k}. {title}', '', f'**Structure :** {struct}', '', expl, '',
              '**Exemples**', ''] + [f'- {zh} *{py}* — {fr}' for zh, py, fr in ex] + ['', '**Questions** (bonne réponse en gras)', '']
        L += [f'- {q} ({fr}) → **{o[0]}** / {o[1]} / {o[2]}' for q, fr, o in qs]
        L += ['', f'<sub>Points officiels : {" · ".join(pts)}</sub>', '']
    c = check(level)
    L += ['## Contrôles automatiques', ''] + ([f'- {x}' for x in c] or ['- Tous les points officiels sont couverts ; aucune phrase hors niveau ; pinyin conforme.'])
    os.makedirs(os.path.join(ROOT, 'docs', 'grammaire'), exist_ok=True)
    out = os.path.join(ROOT, 'docs', 'grammaire', f'hsk{level}.md')
    open(out, 'w', encoding='utf8').write('\n'.join(L) + '\n')
    print(f'{len(sheets)} fiches, {len(c)} problème(s) → docs/grammaire/hsk{level}.md'); [print('  ' + x) for x in c]
    return c

def integrer(level):
    c = check(level)
    if c: print('Refusé :', *c, sep='\n  '); sys.exit(1)
    path = os.path.join(ROOT, 'data', 'grammaire.json')
    data = json.load(open(path, encoding='utf8')) if os.path.exists(path) else {}
    data[str(level)] = [{'id': s[0], 't': s[1], 's': s[2], 'x': s[3], 'pts': s[4], 'ex': [list(e) for e in s[5]], 'q': [[q, fr, o] for q, fr, o in s[6]]} for s in SHEETS[level]]
    json.dump(data, open(path, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    print(f'{len(SHEETS[level])} fiches du HSK {level} → data/grammaire.json')

if __name__ == '__main__':
    {'relire': relire, 'integrer': integrer}[sys.argv[1]](int(sys.argv[2]))
