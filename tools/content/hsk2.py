# -*- coding: utf-8 -*-
"""Source du contenu HSK 2 de Xué Yuán : unités thématiques et phrases d'exemple.

Lancer :  python3 tools/content/hsk2.py
  1. vérifie que chaque mot HSK 2 de l'appli est dans une seule unité ;
  2. vérifie que chaque phrase n'emploie que le vocabulaire officiel HSK 1-2 (HSK 2.0) ;
  3. compare le pinyin, caractère par caractère, au dictionnaire pypinyin ;
  4. écrit data/sentences-hsk2.json et le bloc des unités dans index.html.

Toutes les phrases sont À FAIRE RELIRE PAR UN NATIF (voir A-RELIRE.md).
Convention de pinyin de l'appli : tons d'origine, sauf 一 et 不 notés tels qu'on les prononce
(yí gè, bú shì) ; le changement 3 + 3 n'est pas noté ; ton neutre sans accent.
"""
import json, re, sys, os, unicodedata
from pypinyin import pinyin, Style

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')

# id, titre, description, mots (dans l'ordre d'apprentissage), phrases modèles, astuce
UNITS = [
 ('2a', 'La famille et les présentations', 'Frères et sœurs, mari et enfants, présenter quelqu\'un poliment.',
  '哥哥 姐姐 弟弟 妹妹 丈夫 孩子 男人 女人 您 姓 介绍 大家 它',
  [('我来介绍一下，这是我姐姐。', 'Wǒ lái jièshào yíxià, zhè shì wǒ jiějie.', 'Je te présente : voici ma grande sœur.'),
   ('您贵姓？——我姓王。', 'Nín guì xìng? — Wǒ xìng Wáng.', 'Quel est votre nom de famille ? — Je m\'appelle Wang.'),
   ('你有哥哥吗？——没有，我有一个妹妹。', 'Nǐ yǒu gēge ma? — Méiyǒu, wǒ yǒu yí gè mèimei.', 'Tu as un grand frère ? — Non, j\'ai une petite sœur.')],
  'Le chinois distingue l\'aîné du cadet : 哥哥 grand frère, 弟弟 petit frère, 姐姐 grande sœur, 妹妹 petite sœur. 您 est le « vous » de politesse pour une seule personne. 它 remplace un animal ou une chose.'),
 ('2b', 'Le temps qui passe', 'Les moments de la journée, la durée, ce qu\'on a déjà fait.',
  '早上 晚上 小时 时间 去年 生日 起床 上班 已经 正在 开始 完 每 第一 次',
  [('你每天几点起床？', 'Nǐ měi tiān jǐ diǎn qǐchuáng?', 'À quelle heure te lèves-tu chaque jour ?'),
   ('我已经工作三年了。', 'Wǒ yǐjīng gōngzuò sān nián le.', 'Je travaille déjà depuis trois ans.'),
   ('这是我第一次来中国。', 'Zhè shì wǒ dì-yī cì lái Zhōngguó.', 'C\'est la première fois que je viens en Chine.')],
  '正在 + verbe = être en train de : 他正在看书. Le nombre de fois se place après le verbe : 看了两次, « vu deux fois ». 完 après un verbe dit que l\'action est finie : 吃完, 看完.'),
 ('2c', 'Faire des achats', 'Les prix, les couleurs, demander une réduction.',
  '卖 贵 便宜 百 千 两 件 颜色 白 黑 红 手表 手机 新 票',
  [('这个多少钱？', 'Zhège duōshao qián?', 'Combien coûte ceci ?'),
   ('太贵了，能便宜一点儿吗？', 'Tài guì le, néng piányi yìdiǎnr ma?', 'C\'est trop cher, vous pouvez baisser un peu ?'),
   ('我要这件红的。', 'Wǒ yào zhè jiàn hóng de.', 'Je prends celui-ci, le rouge.')],
  'Devant un classificateur, 二 devient 两 : 两本书, 两点. Adjectif + 的 remplace un nom déjà connu : 红的 « le rouge », 新的 « le neuf ».'),
 ('2d', 'À table', 'Commander, dire ce qu\'on aime manger et boire, offrir.',
  '好吃 鸡蛋 羊肉 鱼 牛奶 咖啡 西瓜 服务员 要 送 给',
  [('你想吃什么？——我要鱼和米饭。', 'Nǐ xiǎng chī shénme? — Wǒ yào yú hé mǐfàn.', 'Qu\'est-ce que tu veux manger ? — Du poisson et du riz.'),
   ('这个菜真好吃！', 'Zhège cài zhēn hǎochī!', 'Ce plat est vraiment délicieux !'),
   ('我请你喝咖啡吧。', 'Wǒ qǐng nǐ hē kāfēi ba.', 'Je t\'offre un café.')],
  '要 a deux sens : « vouloir » (我要咖啡, je veux un café) et « aller » pour un futur proche (明天要下雨, il va pleuvoir demain). 给 + personne + verbe = faire quelque chose pour quelqu\'un : 给妈妈打电话.'),
 ('2e', 'Se déplacer et s\'orienter', 'Loin, près, à gauche, à droite : trouver son chemin et voyager.',
  '路 离 远 近 左边 右边 外 出 进 门 走 到 从 火车站 机场 公共汽车 宾馆 房间',
  [('请问，火车站怎么走？', 'Qǐngwèn, huǒchēzhàn zěnme zǒu?', 'Excusez-moi, comment va-t-on à la gare ?'),
   ('我家离这儿不远。', 'Wǒ jiā lí zhèr bù yuǎn.', 'Ma maison n\'est pas loin d\'ici.'),
   ('宾馆就在火车站的右边。', 'Bīnguǎn jiù zài huǒchēzhàn de yòubian.', 'L\'hôtel est juste à droite de la gare.')],
  '离 mesure la distance entre deux lieux : A 离 B 很近, « A est près de B ». 从 A 到 B = de A à B. Le lieu se place avant le verbe : 在学校学习, « étudier à l\'école ».'),
 ('2f', 'Loisirs et sport', 'Chanter, danser, nager, voyager : parler de ce qu\'on aime faire.',
  '唱歌 跳舞 游泳 跑步 打篮球 踢足球 运动 旅游 玩 一起 笑 快乐',
  [('你喜欢什么运动？——我喜欢游泳。', 'Nǐ xǐhuan shénme yùndòng? — Wǒ xǐhuan yóuyǒng.', 'Quel sport aimes-tu ? — J\'aime nager.'),
   ('我们一起去打篮球吧！', 'Wǒmen yìqǐ qù dǎ lánqiú ba!', 'Allons jouer au basket ensemble !'),
   ('她跳舞跳得很好。', 'Tā tiàowǔ tiào de hěn hǎo.', 'Elle danse très bien.')],
  'Pour juger une action, on répète le verbe puis 得 + appréciation : 她唱歌唱得很好, « elle chante bien ». 吧 en fin de phrase fait une proposition : 我们去游泳吧, « allons nager ».'),
 ('2g', 'Santé et météo', 'Être malade ou fatigué, se reposer, le temps qu\'il fait.',
  '身体 生病 药 累 休息 眼睛 晴 阴 雪 洗 忙',
  [('你身体怎么样？——很好，谢谢。', 'Nǐ shēntǐ zěnmeyàng? — Hěn hǎo, xièxie.', 'Comment va ta santé ? — Très bien, merci.'),
   ('我生病了，要去医院。', 'Wǒ shēngbìng le, yào qù yīyuàn.', 'Je suis malade, je dois aller à l\'hôpital.'),
   ('明天天气怎么样？——是晴天。', 'Míngtiān tiānqì zěnmeyàng? — Shì qíngtiān.', 'Quel temps fera-t-il demain ? — Beau temps.')],
  '了 en fin de phrase annonce un changement : 下雪了, « (ça y est) il neige » ; 我累了, « je suis fatigué (maintenant) ». On « mange » ses médicaments : 吃药 = prendre des médicaments.'),
 ('2h', 'École et travail', 'Les cours, les examens, poser une question, demander de l\'aide.',
  '教室 课 考试 题 问题 问 懂 知道 意思 报纸 公司 准备 帮助 告诉 找 事情',
  [('老师，这个字是什么意思？', 'Lǎoshī, zhège zì shì shénme yìsi?', 'Professeur, que veut dire ce caractère ?'),
   ('对不起，我没听懂，请再说一次。', 'Duìbuqǐ, wǒ méi tīngdǒng, qǐng zài shuō yí cì.', 'Pardon, je n\'ai pas compris, pouvez-vous répéter ?'),
   ('明天有考试，你准备好了吗？', 'Míngtiān yǒu kǎoshì, nǐ zhǔnbèi hǎo le ma?', 'Il y a un examen demain, tu es prêt ?')],
  'Un verbe peut être suivi de son résultat : 听 (écouter) + 懂 (comprendre) = 听懂, « comprendre à l\'oral » ; 准备 + 好 = être prêt. Au passé, on nie avec 没 : 我没听懂, « je n\'ai pas compris ».'),
 ('2i', 'Décrire et comparer', 'Plus grand, plus vite, le meilleur : comparer et juger.',
  '比 长 高 快 慢 最 非常 真 错 穿 着 得',
  [('我比你高。', 'Wǒ bǐ nǐ gāo.', 'Je suis plus grand que toi.'),
   ('你汉语说得真好！', 'Nǐ Hànyǔ shuō de zhēn hǎo!', 'Tu parles vraiment bien chinois !'),
   ('请说慢一点儿。', 'Qǐng shuō màn yìdiǎnr.', 'Parlez un peu plus lentement, s\'il vous plaît.')],
  'Pour comparer : A 比 B + adjectif, sans 很 : 今天比昨天冷 (et non 比昨天很冷). 着 après un verbe décrit un état qui dure : 门开着, « la porte est ouverte ».'),
 ('2j', 'Relier ses idées', 'Parce que, donc, mais, peut-être : construire des phrases plus longues.',
  '因为 所以 但是 可能 可以 觉得 希望 为什么 就 还 也 再 别 吧 让 等',
  [('你为什么学习汉语？——因为我想去中国工作。', 'Nǐ wèi shénme xuéxí Hànyǔ? — Yīnwèi wǒ xiǎng qù Zhōngguó gōngzuò.', 'Pourquoi apprends-tu le chinois ? — Parce que je veux travailler en Chine.'),
   ('我觉得这个电影很有意思。', 'Wǒ juéde zhège diànyǐng hěn yǒu yìsi.', 'Je trouve ce film très intéressant.'),
   ('我们明天再见吧。', 'Wǒmen míngtiān zài jiàn ba.', 'On se revoit demain.')],
  '因为… 所以… vont souvent ensemble : 因为下雨，所以我没去. 还 = « encore » pour une action qui continue (他还在睡觉) ; 再 = « de nouveau » pour une action à venir (明天再来).'),
]

# Deux phrases par mot : (chinois, pinyin, français)
S = {
 '哥哥': [('我哥哥在北京工作。', 'Wǒ gēge zài Běijīng gōngzuò.', 'Mon grand frère travaille à Pékin.'),
         ('你有哥哥吗？', 'Nǐ yǒu gēge ma?', 'Tu as un grand frère ?')],
 '姐姐': [('我姐姐是医生。', 'Wǒ jiějie shì yīshēng.', 'Ma grande sœur est médecin.'),
         ('她姐姐很喜欢唱歌。', 'Tā jiějie hěn xǐhuan chànggē.', 'Sa grande sœur adore chanter.')],
 '弟弟': [('我弟弟十岁了。', 'Wǒ dìdi shí suì le.', 'Mon petit frère a dix ans.'),
         ('弟弟在睡觉，别说话。', 'Dìdi zài shuìjiào, bié shuōhuà.', 'Mon petit frère dort, ne parle pas.')],
 '妹妹': [('我妹妹是学生。', 'Wǒ mèimei shì xuésheng.', 'Ma petite sœur est élève.'),
         ('妹妹很喜欢猫。', 'Mèimei hěn xǐhuan māo.', 'Ma petite sœur adore les chats.')],
 '丈夫': [('她丈夫是老师。', 'Tā zhàngfu shì lǎoshī.', 'Son mari est professeur.'),
         ('我丈夫每天做中国菜。', 'Wǒ zhàngfu měi tiān zuò Zhōngguó cài.', 'Mon mari fait de la cuisine chinoise tous les jours.')],
 '孩子': [('你有几个孩子？', 'Nǐ yǒu jǐ gè háizi?', 'Combien d\'enfants as-tu ?'),
         ('孩子们在学校里玩。', 'Háizimen zài xuéxiào li wán.', 'Les enfants jouent à l\'école.')],
 '男人': [('那个男人是我的老师。', 'Nàge nánrén shì wǒ de lǎoshī.', 'Cet homme est mon professeur.'),
         ('这个男人很高。', 'Zhège nánrén hěn gāo.', 'Cet homme est très grand.')],
 '女人': [('那个女人是谁？', 'Nàge nǚrén shì shéi?', 'Qui est cette femme ?'),
         ('那个女人在商店工作。', 'Nàge nǚrén zài shāngdiàn gōngzuò.', 'Cette femme travaille dans un magasin.')],
 '您': [('您好！您叫什么名字？', 'Nín hǎo! Nín jiào shénme míngzi?', 'Bonjour ! Comment vous appelez-vous ?'),
       ('老师，您明天来吗？', 'Lǎoshī, nín míngtiān lái ma?', 'Professeur, vous venez demain ?')],
 '姓': [('您贵姓？——我姓王。', 'Nín guì xìng? — Wǒ xìng Wáng.', 'Quel est votre nom de famille ? — Je m\'appelle Wang.'),
       ('他姓什么？', 'Tā xìng shénme?', 'Quel est son nom de famille ?')],
 '介绍': [('我来介绍一下，这是我朋友安娜。', 'Wǒ lái jièshào yíxià, zhè shì wǒ péngyou Ānnà.', 'Je vous présente mon amie Anna.'),
         ('请你介绍一下你的家。', 'Qǐng nǐ jièshào yíxià nǐ de jiā.', 'Présente-nous ta famille, s\'il te plaît.')],
 '大家': [('大家好！', 'Dàjiā hǎo!', 'Bonjour à tous !'),
         ('大家都喜欢她。', 'Dàjiā dōu xǐhuan tā.', 'Tout le monde l\'aime bien.')],
 '它': [('这是我的猫，它很漂亮。', 'Zhè shì wǒ de māo, tā hěn piàoliang.', 'C\'est mon chat, il est très beau.'),
       ('我的狗很小，它两岁了。', 'Wǒ de gǒu hěn xiǎo, tā liǎng suì le.', 'Mon chien est petit, il a deux ans.')],

 '早上': [('我早上六点起床。', 'Wǒ zǎoshang liù diǎn qǐchuáng.', 'Je me lève à six heures du matin.'),
         ('早上好！', 'Zǎoshang hǎo!', 'Bonjour ! (le matin)')],
 '晚上': [('晚上我们去看电影吧。', 'Wǎnshang wǒmen qù kàn diànyǐng ba.', 'Allons voir un film ce soir.'),
         ('我每天晚上十一点睡觉。', 'Wǒ měi tiān wǎnshang shíyī diǎn shuìjiào.', 'Je me couche à onze heures tous les soirs.')],
 '小时': [('我每天工作八个小时。', 'Wǒ měi tiān gōngzuò bā gè xiǎoshí.', 'Je travaille huit heures par jour.'),
         ('坐飞机去中国要几个小时？', 'Zuò fēijī qù Zhōngguó yào jǐ gè xiǎoshí?', 'Combien d\'heures faut-il pour aller en Chine en avion ?')],
 '时间': [('你明天有时间吗？', 'Nǐ míngtiān yǒu shíjiān ma?', 'Tu as du temps demain ?'),
         ('现在没有时间了，我们快走吧。', 'Xiànzài méiyǒu shíjiān le, wǒmen kuài zǒu ba.', 'On n\'a plus le temps, partons vite.')],
 '去年': [('去年我去了中国。', 'Qùnián wǒ qùle Zhōngguó.', 'L\'an dernier, je suis allé en Chine.'),
         ('他去年开始学习汉语。', 'Tā qùnián kāishǐ xuéxí Hànyǔ.', 'Il a commencé le chinois l\'an dernier.')],
 '生日': [('你的生日是几月几号？', 'Nǐ de shēngrì shì jǐ yuè jǐ hào?', 'Quelle est la date de ton anniversaire ?'),
         ('明天是我妈妈的生日。', 'Míngtiān shì wǒ māma de shēngrì.', 'Demain, c\'est l\'anniversaire de ma mère.')],
 '起床': [('你每天几点起床？', 'Nǐ měi tiān jǐ diǎn qǐchuáng?', 'À quelle heure te lèves-tu chaque jour ?'),
         ('快起床！已经八点了。', 'Kuài qǐchuáng! Yǐjīng bā diǎn le.', 'Lève-toi vite ! Il est déjà huit heures.')],
 '上班': [('我爸爸坐公共汽车去上班。', 'Wǒ bàba zuò gōnggòng qìchē qù shàngbān.', 'Mon père va au travail en bus.'),
         ('你几点上班？', 'Nǐ jǐ diǎn shàngbān?', 'À quelle heure commences-tu le travail ?')],
 '已经': [('他已经回家了。', 'Tā yǐjīng huí jiā le.', 'Il est déjà rentré.'),
         ('我已经学习汉语一年了。', 'Wǒ yǐjīng xuéxí Hànyǔ yì nián le.', 'J\'apprends le chinois depuis déjà un an.')],
 '正在': [('他正在打电话。', 'Tā zhèngzài dǎ diànhuà.', 'Il est en train de téléphoner.'),
         ('你来的时候，我正在看书。', 'Nǐ lái de shíhou, wǒ zhèngzài kàn shū.', 'Quand tu es arrivé, j\'étais en train de lire.')],
 '开始': [('电影几点开始？', 'Diànyǐng jǐ diǎn kāishǐ?', 'À quelle heure commence le film ?'),
         ('我们开始上课吧。', 'Wǒmen kāishǐ shàngkè ba.', 'Commençons le cours.')],
 '完': [('你看完这本书了吗？', 'Nǐ kànwán zhè běn shū le ma?', 'Tu as fini de lire ce livre ?'),
       ('我吃完了，谢谢。', 'Wǒ chīwán le, xièxie.', 'J\'ai fini de manger, merci.')],
 '每': [('他每天都跑步。', 'Tā měi tiān dōu pǎobù.', 'Il court tous les jours.'),
       ('每个星期六我都去游泳。', 'Měi gè xīngqīliù wǒ dōu qù yóuyǒng.', 'Tous les samedis, je vais nager.')],
 '第一': [('这是我第一次来北京。', 'Zhè shì wǒ dì-yī cì lái Běijīng.', 'C\'est la première fois que je viens à Pékin.'),
         ('她考试考了第一。', 'Tā kǎoshì kǎole dì-yī.', 'Elle est arrivée première à l\'examen.')],
 '次': [('这个电影我看了两次。', 'Zhège diànyǐng wǒ kànle liǎng cì.', 'J\'ai vu ce film deux fois.'),
       ('请你再说一次。', 'Qǐng nǐ zài shuō yí cì.', 'Peux-tu le redire encore une fois ?')],

 '卖': [('这个商店卖什么？', 'Zhège shāngdiàn mài shénme?', 'Qu\'est-ce que ce magasin vend ?'),
       ('苹果怎么卖？', 'Píngguǒ zěnme mài?', 'Combien coûtent les pommes ?')],
 '贵': [('这件衣服太贵了！', 'Zhè jiàn yīfu tài guì le!', 'Ce vêtement est trop cher !'),
       ('北京的东西贵吗？', 'Běijīng de dōngxi guì ma?', 'Les choses sont chères à Pékin ?')],
 '便宜': [('这个手机很便宜。', 'Zhège shǒujī hěn piányi.', 'Ce portable est très bon marché.'),
         ('能便宜一点儿吗？', 'Néng piányi yìdiǎnr ma?', 'Vous pouvez faire un peu moins cher ?')],
 '百': [('这本书一百块。', 'Zhè běn shū yìbǎi kuài.', 'Ce livre coûte cent yuans.'),
       ('我们学校有五百个学生。', 'Wǒmen xuéxiào yǒu wǔbǎi gè xuésheng.', 'Notre école compte cinq cents élèves.')],
 '千': [('这个电脑三千块钱。', 'Zhège diànnǎo sānqiān kuài qián.', 'Cet ordinateur coûte trois mille yuans.'),
       ('一千块太贵了。', 'Yìqiān kuài tài guì le.', 'Mille yuans, c\'est trop cher.')],
 '两': [('我买了两本书。', 'Wǒ mǎile liǎng běn shū.', 'J\'ai acheté deux livres.'),
       ('现在两点。', 'Xiànzài liǎng diǎn.', 'Il est deux heures.')],
 '件': [('我想买一件衣服。', 'Wǒ xiǎng mǎi yí jiàn yīfu.', 'Je voudrais acheter un vêtement.'),
       ('这件事情我知道了。', 'Zhè jiàn shìqing wǒ zhīdào le.', 'Je suis au courant de cette affaire.')],
 '颜色': [('你喜欢什么颜色？', 'Nǐ xǐhuan shénme yánsè?', 'Quelle couleur aimes-tu ?'),
         ('这个颜色很漂亮。', 'Zhège yánsè hěn piàoliang.', 'Cette couleur est très jolie.')],
 '白': [('我想买那件白衣服。', 'Wǒ xiǎng mǎi nà jiàn bái yīfu.', 'Je voudrais acheter ce vêtement blanc, là-bas.'),
       ('他的猫是白的。', 'Tā de māo shì bái de.', 'Son chat est blanc.')],
 '黑': [('我喜欢黑颜色。', 'Wǒ xǐhuan hēi yánsè.', 'J\'aime le noir.'),
       ('天黑了，我们回家吧。', 'Tiān hēi le, wǒmen huí jiā ba.', 'Il fait nuit, rentrons.')],
 '红': [('她穿着一件红衣服。', 'Tā chuānzhe yí jiàn hóng yīfu.', 'Elle porte un vêtement rouge.'),
       ('中国人很喜欢红颜色。', 'Zhōngguó rén hěn xǐhuan hóng yánsè.', 'Les Chinois aiment beaucoup le rouge.')],
 '手表': [('这是我爸爸送我的手表。', 'Zhè shì wǒ bàba sòng wǒ de shǒubiǎo.', 'C\'est la montre que mon père m\'a offerte.'),
         ('我的手表在哪儿？', 'Wǒ de shǒubiǎo zài nǎr?', 'Où est ma montre ?')],
 '手机': [('你的手机号是多少？', 'Nǐ de shǒujī hào shì duōshao?', 'Quel est ton numéro de portable ?'),
         ('我的手机是新的。', 'Wǒ de shǒujī shì xīn de.', 'Mon portable est neuf.')],
 '新': [('这是我的新朋友。', 'Zhè shì wǒ de xīn péngyou.', 'C\'est mon nouvel ami.'),
       ('我想买一个新电脑。', 'Wǒ xiǎng mǎi yí gè xīn diànnǎo.', 'Je voudrais acheter un nouvel ordinateur.')],
 '票': [('我买了两张电影票。', 'Wǒ mǎile liǎng zhāng diànyǐng piào.', 'J\'ai acheté deux billets de cinéma.'),
       ('飞机票贵不贵？', 'Fēijī piào guì bu guì?', 'Les billets d\'avion sont chers ?')],

 '好吃': [('妈妈做的菜很好吃。', 'Māma zuò de cài hěn hǎochī.', 'Les plats que fait maman sont délicieux.'),
         ('这个饭店的菜好吃吗？', 'Zhège fàndiàn de cài hǎochī ma?', 'Les plats de ce restaurant sont bons ?')],
 '鸡蛋': [('我早上吃了两个鸡蛋。', 'Wǒ zǎoshang chīle liǎng gè jīdàn.', 'J\'ai mangé deux œufs ce matin.'),
         ('你要几个鸡蛋？', 'Nǐ yào jǐ gè jīdàn?', 'Il te faut combien d\'œufs ?')],
 '羊肉': [('你吃羊肉吗？', 'Nǐ chī yángròu ma?', 'Tu manges du mouton ?'),
         ('我不喜欢吃羊肉。', 'Wǒ bù xǐhuan chī yángròu.', 'Je n\'aime pas le mouton.')],
 '鱼': [('我们晚上吃鱼吧。', 'Wǒmen wǎnshang chī yú ba.', 'Mangeons du poisson ce soir.'),
       ('这个饭店的鱼很好吃。', 'Zhège fàndiàn de yú hěn hǎochī.', 'Le poisson de ce restaurant est délicieux.')],
 '牛奶': [('孩子每天都要喝牛奶。', 'Háizi měi tiān dōu yào hē niúnǎi.', 'Les enfants doivent boire du lait tous les jours.'),
         ('我早上喝牛奶。', 'Wǒ zǎoshang hē niúnǎi.', 'Le matin, je bois du lait.')],
 '咖啡': [('我想喝咖啡。', 'Wǒ xiǎng hē kāfēi.', 'J\'ai envie d\'un café.'),
         ('晚上别喝咖啡！', 'Wǎnshang bié hē kāfēi!', 'Ne bois pas de café le soir !')],
 '西瓜': [('天气热的时候，我喜欢吃西瓜。', 'Tiānqì rè de shíhou, wǒ xǐhuan chī xīguā.', 'Quand il fait chaud, j\'aime manger de la pastèque.'),
         ('这个西瓜很大。', 'Zhège xīguā hěn dà.', 'Cette pastèque est très grosse.')],
 '服务员': [('服务员，我们要米饭。', 'Fúwùyuán, wǒmen yào mǐfàn.', 'S\'il vous plaît ! Nous voudrions du riz.'),
           ('这个饭店的服务员很好。', 'Zhège fàndiàn de fúwùyuán hěn hǎo.', 'Les serveurs de ce restaurant sont très gentils.')],
 '要': [('你要喝什么？', 'Nǐ yào hē shénme?', 'Que veux-tu boire ?'),
       ('明天要下雨。', 'Míngtiān yào xiàyǔ.', 'Il va pleuvoir demain.')],
 '送': [('这是我送你的。', 'Zhè shì wǒ sòng nǐ de.', 'C\'est pour toi, je te l\'offre.'),
       ('我送你去机场。', 'Wǒ sòng nǐ qù jīchǎng.', 'Je t\'accompagne à l\'aéroport.')],
 '给': [('请给我看看。', 'Qǐng gěi wǒ kànkan.', 'Montre-moi, s\'il te plaît.'),
       ('我给妈妈打电话。', 'Wǒ gěi māma dǎ diànhuà.', 'Je téléphone à ma mère.')],

 '路': [('去火车站坐几路公共汽车？', 'Qù huǒchēzhàn zuò jǐ lù gōnggòng qìchē?', 'Quel bus faut-il prendre pour aller à la gare ?'),
       ('我在路上了。', 'Wǒ zài lù shang le.', 'Je suis en route.')],
 '离': [('我家离学校很近。', 'Wǒ jiā lí xuéxiào hěn jìn.', 'Ma maison est tout près de l\'école.'),
       ('机场离这儿远吗？', 'Jīchǎng lí zhèr yuǎn ma?', 'L\'aéroport est loin d\'ici ?')],
 '远': [('医院不远，走路去吧。', 'Yīyuàn bù yuǎn, zǒulù qù ba.', 'L\'hôpital n\'est pas loin, allons-y à pied.'),
       ('他家离这儿很远。', 'Tā jiā lí zhèr hěn yuǎn.', 'Sa maison est très loin d\'ici.')],
 '近': [('商店很近，就在前面。', 'Shāngdiàn hěn jìn, jiù zài qiánmiàn.', 'Le magasin est tout près, juste devant.'),
       ('宾馆离机场很近。', 'Bīnguǎn lí jīchǎng hěn jìn.', 'L\'hôtel est tout près de l\'aéroport.')],
 '左边': [('医院在商店的左边。', 'Yīyuàn zài shāngdiàn de zuǒbian.', 'L\'hôpital est à gauche du magasin.'),
         ('坐在我左边的是我同学。', 'Zuò zài wǒ zuǒbian de shì wǒ tóngxué.', 'Celui qui est assis à ma gauche est mon camarade.')],
 '右边': [('火车站的右边有一个饭店。', 'Huǒchēzhàn de yòubian yǒu yí gè fàndiàn.', 'À droite de la gare, il y a un restaurant.'),
         ('我的书在右边的桌子上。', 'Wǒ de shū zài yòubian de zhuōzi shang.', 'Mon livre est sur la table de droite.')],
 '外': [('门外有一个人。', 'Mén wài yǒu yí gè rén.', 'Il y a quelqu\'un devant la porte.'),
       ('学校外有很多商店。', 'Xuéxiào wài yǒu hěn duō shāngdiàn.', 'Il y a beaucoup de magasins autour de l\'école.')],
 '出': [('他出去了，不在家。', 'Tā chūqu le, bú zài jiā.', 'Il est sorti, il n\'est pas à la maison.'),
       ('我们几点出门？', 'Wǒmen jǐ diǎn chūmén?', 'À quelle heure on sort ?')],
 '进': [('请进！', 'Qǐng jìn!', 'Entrez !'),
       ('他进了教室。', 'Tā jìnle jiàoshì.', 'Il est entré dans la salle de classe.')],
 '门': [('请开门。', 'Qǐng kāi mén.', 'Ouvrez la porte, s\'il vous plaît.'),
       ('商店的门开了。', 'Shāngdiàn de mén kāi le.', 'La porte du magasin s\'est ouverte.')],
 '走': [('我们走吧！', 'Wǒmen zǒu ba!', 'Allons-y !'),
       ('从这儿走到火车站要十分钟。', 'Cóng zhèr zǒu dào huǒchēzhàn yào shí fēnzhōng.', 'D\'ici à la gare, il faut dix minutes à pied.')],
 '到': [('你什么时候到北京？', 'Nǐ shénme shíhou dào Běijīng?', 'Quand arrives-tu à Pékin ?'),
       ('我到家了。', 'Wǒ dào jiā le.', 'Je suis arrivé à la maison.')],
 '从': [('我从中国来。', 'Wǒ cóng Zhōngguó lái.', 'Je viens de Chine.'),
       ('从我家到学校很近。', 'Cóng wǒ jiā dào xuéxiào hěn jìn.', 'De chez moi à l\'école, c\'est tout près.')],
 '火车站': [('火车站在哪儿？', 'Huǒchēzhàn zài nǎr?', 'Où est la gare ?'),
           ('我们坐出租车去火车站吧。', 'Wǒmen zuò chūzūchē qù huǒchēzhàn ba.', 'Prenons un taxi pour la gare.')],
 '机场': [('他在机场等我。', 'Tā zài jīchǎng děng wǒ.', 'Il m\'attend à l\'aéroport.'),
         ('去机场要多长时间？', 'Qù jīchǎng yào duō cháng shíjiān?', 'Combien de temps faut-il pour aller à l\'aéroport ?')],
 '公共汽车': [('我每天坐公共汽车去学校。', 'Wǒ měi tiān zuò gōnggòng qìchē qù xuéxiào.', 'Je vais à l\'école en bus tous les jours.'),
             ('公共汽车来了！', 'Gōnggòng qìchē lái le!', 'Le bus arrive !')],
 '宾馆': [('我们住在火车站旁边的宾馆。', 'Wǒmen zhù zài huǒchēzhàn pángbiān de bīnguǎn.', 'Nous logeons à l\'hôtel à côté de la gare.'),
         ('这个宾馆很便宜。', 'Zhège bīnguǎn hěn piányi.', 'Cet hôtel est très bon marché.')],
 '房间': [('我的房间很小。', 'Wǒ de fángjiān hěn xiǎo.', 'Ma chambre est très petite.'),
         ('你的房间号是多少？', 'Nǐ de fángjiān hào shì duōshao?', 'Quel est ton numéro de chambre ?')],

 '唱歌': [('她唱歌唱得很好。', 'Tā chànggē chàng de hěn hǎo.', 'Elle chante très bien.'),
         ('我们去唱歌吧！', 'Wǒmen qù chànggē ba!', 'Allons chanter (au karaoké) !')],
 '跳舞': [('你会跳舞吗？', 'Nǐ huì tiàowǔ ma?', 'Tu sais danser ?'),
         ('她每个星期六都去跳舞。', 'Tā měi gè xīngqīliù dōu qù tiàowǔ.', 'Elle va danser tous les samedis.')],
 '游泳': [('我不会游泳。', 'Wǒ bú huì yóuyǒng.', 'Je ne sais pas nager.'),
         ('天气很热，我们去游泳吧。', 'Tiānqì hěn rè, wǒmen qù yóuyǒng ba.', 'Il fait chaud, allons nager.')],
 '跑步': [('我每天早上跑步。', 'Wǒ měi tiān zǎoshang pǎobù.', 'Je cours tous les matins.'),
         ('跑步是很好的运动。', 'Pǎobù shì hěn hǎo de yùndòng.', 'Courir, c\'est un très bon sport.')],
 '打篮球': [('他很喜欢打篮球。', 'Tā hěn xǐhuan dǎ lánqiú.', 'Il adore jouer au basket.'),
           ('下午我们一起去打篮球吧。', 'Xiàwǔ wǒmen yìqǐ qù dǎ lánqiú ba.', 'Allons jouer au basket ensemble cet après-midi.')],
 '踢足球': [('我儿子每个星期天都踢足球。', 'Wǒ érzi měi gè xīngqītiān dōu tī zúqiú.', 'Mon fils joue au foot tous les dimanches.'),
           ('他们在学校踢足球。', 'Tāmen zài xuéxiào tī zúqiú.', 'Ils jouent au foot à l\'école.')],
 '运动': [('你喜欢什么运动？', 'Nǐ xǐhuan shénme yùndòng?', 'Quel sport aimes-tu ?'),
         ('多运动，身体好。', 'Duō yùndòng, shēntǐ hǎo.', 'Bouge plus, tu seras en forme.')],
 '旅游': [('我想去中国旅游。', 'Wǒ xiǎng qù Zhōngguó lǚyóu.', 'Je voudrais faire un voyage en Chine.'),
         ('去年我们去北京旅游了。', 'Qùnián wǒmen qù Běijīng lǚyóu le.', 'L\'an dernier, nous avons fait un voyage à Pékin.')],
 '玩': [('我们去朋友家玩吧。', 'Wǒmen qù péngyou jiā wán ba.', 'Allons nous amuser chez des amis.'),
       ('你在北京玩得怎么样？', 'Nǐ zài Běijīng wán de zěnmeyàng?', 'Tu t\'es bien amusé à Pékin ?')],
 '一起': [('我们一起去吧！', 'Wǒmen yìqǐ qù ba!', 'Allons-y ensemble !'),
         ('我和朋友一起学习汉语。', 'Wǒ hé péngyou yìqǐ xuéxí Hànyǔ.', 'J\'apprends le chinois avec un ami.')],
 '笑': [('她笑了。', 'Tā xiào le.', 'Elle a souri.'),
       ('你笑什么？', 'Nǐ xiào shénme?', 'Pourquoi tu ris ?')],
 '快乐': [('生日快乐！', 'Shēngrì kuàilè!', 'Joyeux anniversaire !'),
         ('我希望你每天都快乐。', 'Wǒ xīwàng nǐ měi tiān dōu kuàilè.', 'J\'espère que tu seras heureux chaque jour.')],

 '身体': [('你身体怎么样？', 'Nǐ shēntǐ zěnmeyàng?', 'Comment va ta santé ?'),
         ('我爸爸身体很好。', 'Wǒ bàba shēntǐ hěn hǎo.', 'Mon père est en bonne santé.')],
 '生病': [('他生病了，今天没来上课。', 'Tā shēngbìng le, jīntiān méi lái shàngkè.', 'Il est malade, il n\'est pas venu en cours aujourd\'hui.'),
         ('生病了要去医院。', 'Shēngbìng le yào qù yīyuàn.', 'Quand on est malade, il faut aller à l\'hôpital.')],
 '药': [('医生给了我一些药。', 'Yīshēng gěile wǒ yìxiē yào.', 'Le médecin m\'a donné des médicaments.'),
       ('你吃药了吗？', 'Nǐ chī yào le ma?', 'Tu as pris tes médicaments ?')],
 '累': [('我今天很累。', 'Wǒ jīntiān hěn lèi.', 'Je suis très fatigué aujourd\'hui.'),
       ('工作了一天，累了吧？', 'Gōngzuòle yì tiān, lèi le ba?', 'Après une journée de travail, tu dois être fatigué ?')],
 '休息': [('你累了，休息一下吧。', 'Nǐ lèi le, xiūxi yíxià ba.', 'Tu es fatigué, repose-toi un peu.'),
         ('星期天我在家休息。', 'Xīngqītiān wǒ zài jiā xiūxi.', 'Le dimanche, je me repose à la maison.')],
 '眼睛': [('她的眼睛很漂亮。', 'Tā de yǎnjing hěn piàoliang.', 'Elle a de très beaux yeux.'),
         ('看书太多，眼睛累了。', 'Kàn shū tài duō, yǎnjing lèi le.', 'J\'ai trop lu, j\'ai les yeux fatigués.')],
 '晴': [('今天是晴天。', 'Jīntiān shì qíngtiān.', 'Il fait beau aujourd\'hui.'),
       ('明天晴，不会下雨。', 'Míngtiān qíng, bú huì xiàyǔ.', 'Demain, il fera beau, il ne pleuvra pas.')],
 '阴': [('今天是阴天。', 'Jīntiān shì yīntiān.', 'Le temps est couvert aujourd\'hui.'),
       ('上午晴，下午阴。', 'Shàngwǔ qíng, xiàwǔ yīn.', 'Beau le matin, couvert l\'après-midi.')],
 '雪': [('下雪了！', 'Xià xuě le!', 'Il neige !'),
       ('我第一次看见雪。', 'Wǒ dì-yī cì kànjiàn xuě.', 'C\'est la première fois que je vois de la neige.')],
 '洗': [('我去洗衣服。', 'Wǒ qù xǐ yīfu.', 'Je vais laver des vêtements.'),
       ('我要洗一下杯子。', 'Wǒ yào xǐ yíxià bēizi.', 'Je dois laver le verre.')],
 '忙': [('你现在忙吗？', 'Nǐ xiànzài máng ma?', 'Tu es occupé en ce moment ?'),
       ('他工作很忙。', 'Tā gōngzuò hěn máng.', 'Il est très pris par son travail.')],

 '教室': [('老师在教室里。', 'Lǎoshī zài jiàoshì li.', 'Le professeur est dans la salle de classe.'),
         ('这个教室很大。', 'Zhège jiàoshì hěn dà.', 'Cette salle de classe est très grande.')],
 '课': [('今天上午有汉语课。', 'Jīntiān shàngwǔ yǒu Hànyǔ kè.', 'Ce matin, il y a cours de chinois.'),
       ('下课了！', 'Xià kè le!', 'Le cours est fini !')],
 '考试': [('明天有考试，我要准备一下。', 'Míngtiān yǒu kǎoshì, wǒ yào zhǔnbèi yíxià.', 'Il y a un examen demain, je dois me préparer.'),
         ('你考试考得怎么样？', 'Nǐ kǎoshì kǎo de zěnmeyàng?', 'Comment s\'est passé ton examen ?')],
 '题': [('这个题我不会。', 'Zhège tí wǒ bú huì.', 'Je ne sais pas faire cet exercice.'),
       ('考试有十个题。', 'Kǎoshì yǒu shí gè tí.', 'L\'examen comporte dix questions.')],
 '问题': [('我有一个问题。', 'Wǒ yǒu yí gè wèntí.', 'J\'ai une question.'),
         ('没问题！', 'Méi wèntí!', 'Pas de problème !')],
 '问': [('我可以问你一个问题吗？', 'Wǒ kěyǐ wèn nǐ yí gè wèntí ma?', 'Je peux te poser une question ?'),
       ('你去问老师吧。', 'Nǐ qù wèn lǎoshī ba.', 'Va demander au professeur.')],
 '懂': [('你懂我的意思吗？', 'Nǐ dǒng wǒ de yìsi ma?', 'Tu comprends ce que je veux dire ?'),
       ('老师说的我都听懂了。', 'Lǎoshī shuō de wǒ dōu tīngdǒng le.', 'J\'ai compris tout ce que le professeur a dit.')],
 '知道': [('你知道他住在哪儿吗？', 'Nǐ zhīdào tā zhù zài nǎr ma?', 'Tu sais où il habite ?'),
         ('我不知道。', 'Wǒ bù zhīdào.', 'Je ne sais pas.')],
 '意思': [('这个字是什么意思？', 'Zhège zì shì shénme yìsi?', 'Que veut dire ce caractère ?'),
         ('这个电影很有意思。', 'Zhège diànyǐng hěn yǒu yìsi.', 'Ce film est très intéressant.')],
 '报纸': [('我爸爸每天早上看报纸。', 'Wǒ bàba měi tiān zǎoshang kàn bàozhǐ.', 'Mon père lit le journal tous les matins.'),
         ('今天的报纸在桌子上。', 'Jīntiān de bàozhǐ zài zhuōzi shang.', 'Le journal d\'aujourd\'hui est sur la table.')],
 '公司': [('你在哪个公司工作？', 'Nǐ zài nǎge gōngsī gōngzuò?', 'Dans quelle entreprise travailles-tu ?'),
         ('我们公司有一百个人。', 'Wǒmen gōngsī yǒu yìbǎi gè rén.', 'Notre entreprise compte cent personnes.')],
 '准备': [('你准备好了吗？', 'Nǐ zhǔnbèi hǎo le ma?', 'Tu es prêt ?'),
         ('我准备明天去北京。', 'Wǒ zhǔnbèi míngtiān qù Běijīng.', 'Je compte aller à Pékin demain.')],
 '帮助': [('谢谢你的帮助！', 'Xièxie nǐ de bāngzhù!', 'Merci pour ton aide !'),
         ('你能帮助我吗？', 'Nǐ néng bāngzhù wǒ ma?', 'Peux-tu m\'aider ?')],
 '告诉': [('请告诉我你的手机号。', 'Qǐng gàosu wǒ nǐ de shǒujī hào.', 'Donne-moi ton numéro de portable, s\'il te plaît.'),
         ('他没告诉我。', 'Tā méi gàosu wǒ.', 'Il ne me l\'a pas dit.')],
 '找': [('你在找什么？', 'Nǐ zài zhǎo shénme?', 'Qu\'est-ce que tu cherches ?'),
       ('我去找你吧。', 'Wǒ qù zhǎo nǐ ba.', 'Je passe te voir.')],
 '事情': [('你有什么事情？', 'Nǐ yǒu shénme shìqing?', 'Qu\'est-ce qu\'il y a ?'),
         ('我今天有很多事情要做。', 'Wǒ jīntiān yǒu hěn duō shìqing yào zuò.', 'J\'ai beaucoup de choses à faire aujourd\'hui.')],

 '比': [('我比我哥哥高。', 'Wǒ bǐ wǒ gēge gāo.', 'Je suis plus grand que mon grand frère.'),
       ('今天比昨天冷。', 'Jīntiān bǐ zuótiān lěng.', 'Il fait plus froid aujourd\'hui qu\'hier.')],
 '长': [('这个电影很长。', 'Zhège diànyǐng hěn cháng.', 'Ce film est très long.'),
       ('这件衣服太长了。', 'Zhè jiàn yīfu tài cháng le.', 'Ce vêtement est trop long.')],
 '高': [('他很高。', 'Tā hěn gāo.', 'Il est très grand.'),
       ('你多高？', 'Nǐ duō gāo?', 'Combien mesures-tu ?')],
 '快': [('他跑得很快。', 'Tā pǎo de hěn kuài.', 'Il court très vite.'),
       ('快走吧，要下雨了。', 'Kuài zǒu ba, yào xiàyǔ le.', 'Dépêchons-nous, il va pleuvoir.')],
 '慢': [('请说慢一点儿。', 'Qǐng shuō màn yìdiǎnr.', 'Parlez un peu plus lentement, s\'il vous plaît.'),
       ('我的手表慢了五分钟。', 'Wǒ de shǒubiǎo mànle wǔ fēnzhōng.', 'Ma montre retarde de cinq minutes.')],
 '最': [('你最喜欢什么水果？', 'Nǐ zuì xǐhuan shénme shuǐguǒ?', 'Quel est ton fruit préféré ?'),
       ('他是我们学校最高的学生。', 'Tā shì wǒmen xuéxiào zuì gāo de xuésheng.', 'C\'est l\'élève le plus grand de notre école.')],
 '非常': [('我非常喜欢北京。', 'Wǒ fēicháng xǐhuan Běijīng.', 'J\'aime énormément Pékin.'),
         ('今天天气非常好。', 'Jīntiān tiānqì fēicháng hǎo.', 'Il fait un temps magnifique aujourd\'hui.')],
 '真': [('你的汉语说得真好！', 'Nǐ de Hànyǔ shuō de zhēn hǎo!', 'Tu parles vraiment bien chinois !'),
       ('这个西瓜真大！', 'Zhège xīguā zhēn dà!', 'Cette pastèque est vraiment grosse !')],
 '错': [('对不起，我说错了。', 'Duìbuqǐ, wǒ shuōcuò le.', 'Pardon, je me suis trompé.'),
       ('这个字你写错了。', 'Zhège zì nǐ xiěcuò le.', 'Tu as mal écrit ce caractère.')],
 '穿': [('今天很冷，多穿一点儿衣服。', 'Jīntiān hěn lěng, duō chuān yìdiǎnr yīfu.', 'Il fait froid aujourd\'hui, couvre-toi bien.'),
       ('你穿这件衣服很漂亮。', 'Nǐ chuān zhè jiàn yīfu hěn piàoliang.', 'Ce vêtement te va très bien.')],
 '着': [('门开着。', 'Mén kāizhe.', 'La porte est ouverte.'),
       ('他笑着说：“你好！”', 'Tā xiàozhe shuō: “Nǐ hǎo!”', 'Il a dit « bonjour » en souriant.')],
 '得': [('她汉语说得很好。', 'Tā Hànyǔ shuō de hěn hǎo.', 'Elle parle très bien chinois.'),
       ('他跑得不快。', 'Tā pǎo de bú kuài.', 'Il ne court pas vite.')],

 '因为': [('因为下雨，所以我没去。', 'Yīnwèi xiàyǔ, suǒyǐ wǒ méi qù.', 'Comme il pleuvait, je n\'y suis pas allé.'),
         ('我很喜欢中国，因为中国菜很好吃。', 'Wǒ hěn xǐhuan Zhōngguó, yīnwèi Zhōngguó cài hěn hǎochī.', 'J\'aime beaucoup la Chine, parce que la cuisine chinoise est délicieuse.')],
 '所以': [('他生病了，所以没来。', 'Tā shēngbìng le, suǒyǐ méi lái.', 'Il est malade, c\'est pour ça qu\'il n\'est pas venu.'),
         ('我明天有考试，所以今天要准备。', 'Wǒ míngtiān yǒu kǎoshì, suǒyǐ jīntiān yào zhǔnbèi.', 'J\'ai un examen demain, donc je dois réviser aujourd\'hui.')],
 '但是': [('这件衣服很漂亮，但是太贵了。', 'Zhè jiàn yīfu hěn piàoliang, dànshì tài guì le.', 'Ce vêtement est très joli, mais trop cher.'),
         ('我想去，但是我没有时间。', 'Wǒ xiǎng qù, dànshì wǒ méiyǒu shíjiān.', 'J\'aimerais y aller, mais je n\'ai pas le temps.')],
 '可能': [('明天可能会下雨。', 'Míngtiān kěnéng huì xiàyǔ.', 'Il va peut-être pleuvoir demain.'),
         ('他可能不在家。', 'Tā kěnéng bú zài jiā.', 'Il n\'est peut-être pas chez lui.')],
 '可以': [('我可以坐这儿吗？', 'Wǒ kěyǐ zuò zhèr ma?', 'Je peux m\'asseoir ici ?'),
         ('你可以看我的书。', 'Nǐ kěyǐ kàn wǒ de shū.', 'Tu peux lire mon livre.')],
 '觉得': [('你觉得这个菜怎么样？', 'Nǐ juéde zhège cài zěnmeyàng?', 'Comment trouves-tu ce plat ?'),
         ('我觉得他汉语说得很好。', 'Wǒ juéde tā Hànyǔ shuō de hěn hǎo.', 'Je trouve qu\'il parle très bien chinois.')],
 '希望': [('我希望明天是晴天。', 'Wǒ xīwàng míngtiān shì qíngtiān.', 'J\'espère qu\'il fera beau demain.'),
         ('我希望能去中国学习汉语。', 'Wǒ xīwàng néng qù Zhōngguó xuéxí Hànyǔ.', 'J\'espère pouvoir aller étudier le chinois en Chine.')],
 '为什么': [('你为什么学习汉语？', 'Nǐ wèi shénme xuéxí Hànyǔ?', 'Pourquoi apprends-tu le chinois ?'),
           ('他为什么没来？', 'Tā wèi shénme méi lái?', 'Pourquoi n\'est-il pas venu ?')],
 '就': [('我家就在前面。', 'Wǒ jiā jiù zài qiánmiàn.', 'Ma maison est juste devant.'),
       ('他六点就起床了。', 'Tā liù diǎn jiù qǐchuáng le.', 'Il s\'est levé dès six heures.')],
 '还': [('他还在睡觉。', 'Tā hái zài shuìjiào.', 'Il dort encore.'),
       ('你还要什么？', 'Nǐ hái yào shénme?', 'Tu veux autre chose ?')],
 '也': [('我也是学生。', 'Wǒ yě shì xuésheng.', 'Moi aussi, je suis étudiant.'),
       ('他喜欢茶，也喜欢咖啡。', 'Tā xǐhuan chá, yě xǐhuan kāfēi.', 'Il aime le thé, et aussi le café.')],
 '再': [('我们明天再去吧。', 'Wǒmen míngtiān zài qù ba.', 'Allons-y plutôt demain.'),
       ('欢迎你再来！', 'Huānyíng nǐ zài lái!', 'Reviens quand tu veux !')],
 '别': [('别说话！', 'Bié shuōhuà!', 'Ne parle pas !'),
       ('天气很冷，别去游泳了。', 'Tiānqì hěn lěng, bié qù yóuyǒng le.', 'Il fait froid, ne va pas nager.')],
 '吧': [('我们走吧。', 'Wǒmen zǒu ba.', 'Allons-y.'),
       ('你是学生吧？', 'Nǐ shì xuésheng ba?', 'Tu es étudiant, je suppose ?')],
 '让': [('妈妈不让我看电视。', 'Māma bú ràng wǒ kàn diànshì.', 'Maman ne me laisse pas regarder la télé.'),
       ('老师让我们回家准备考试。', 'Lǎoshī ràng wǒmen huí jiā zhǔnbèi kǎoshì.', 'Le professeur nous a dit de rentrer réviser l\'examen.')],
 '等': [('请等一下。', 'Qǐng děng yíxià.', 'Attendez un instant, s\'il vous plaît.'),
       ('我在火车站等你。', 'Wǒ zài huǒchēzhàn děng nǐ.', 'Je t\'attends à la gare.')],
}

# ---------- Vérifications ----------
def load_app_words(level):
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf8').read()
    if level == 1: m = re.search(r"^1: `(.*?)`", html, re.S | re.M)
    else: m = re.search(r"^%d: `(.*?)`" % level, html, re.S | re.M)
    return [l.split('|') for l in m.group(1).split('\n')]

def official():
    words = {1: set(), 2: set()}
    for line in open(os.path.join(os.path.dirname(__file__), 'hsk20-niveaux-1-2.txt'), encoding='utf8'):
        if line.startswith('#') or not line.strip(): continue
        k, w = line.rstrip('\n').split('\t'); words[int(k)].add(w)
    return words

NAMES = {'安娜', '王'}
# Constructions grammaticales régulières, faites de mots HSK 1-2 (pronom + 们, ce/là + 儿, quantité + unité…)
EXTRA = {'们', '这儿', '那儿', '哪儿', '一下', '一点儿', '天', '星期六', '星期天', '星期一', '星期日', '晴天', '阴天', '上课', '下课', '吃药',
         '走路', '出门', '出去', '请问', '十一', '二十', '五百', '三千', '一百', '一千', '几路', '房间号', '手机号', '天黑', '哪个', '这个', '那个', '一些',
         # Verbe répété devant 得 (唱歌唱得好) : 唱, 考, 跑 sont du niveau 1 du HSK 3.0 ; 跳 vient de 跳舞 (HSK 2)
         '唱', '考', '跑', '跳'}
PUNCT = set('，。？！：、“”…—；（）· ')

def segment(text, vocab):
    out, i = [], 0
    while i < len(text):
        if text[i] in PUNCT or text[i].isascii(): i += 1; continue
        for n in (4, 3, 2, 1):
            t = text[i:i + n]
            if t in vocab or t in NAMES: out.append((t, True)); i += n; break
        else: out.append((text[i], False)); i += 1
    return out

VOW = 'aeiouüvāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ'
SYL = re.compile(r'(?:zh|ch|sh|[bpmfdtnlgkhjqxrzcsyw])?[%s]+(?:ngr?(?![%s])|nr?(?![%s])|r(?![%s]))?' % (VOW, VOW, VOW, VOW), re.I)  # nr / ngr : 儿化 (yìdiǎnr)
def syllables(py):
    return [m.group(0).lower() for tok in re.split(r"[\s'’\-]+", re.sub(r'[,.?!:;“”"—…()]', ' ', py)) for m in SYL.finditer(tok)]
def strip_tone(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').replace('ü', 'u')

def check_pinyin(zh, py):
    chars = [c for c in zh if '㐀' <= c <= '鿿']
    syl = syllables(py); out = []; j = 0
    for k, c in enumerate(chars):
        if c == '儿' and j > 0 and syl[j - 1].endswith('r') and strip_tone(syl[j - 1]) != 'er': continue  # 儿化 : nǎr, zhèr, yìdiǎnr
        if j >= len(syl): out.append(f'{c} : syllabe manquante'); break
        s = syl[j]; j += 1
        refs = {x for x in pinyin(c, style=Style.TONE, heteronym=True)[0]}
        bare = strip_tone(s)
        if c == '儿' and bare == 'r': continue
        if bare.rstrip('r') != bare and c != '儿' and k + 1 < len(chars) and chars[k + 1] == '儿': s = s[:-1]; bare = bare[:-1]
        if s in refs: continue
        if bare in {strip_tone(r) for r in refs} and (s == bare or c in '一不'): continue  # ton neutre, ou 一 / 不 prononcés
        out.append(f'{c} : « {s} » ≠ dictionnaire ({"/".join(sorted(refs))})')
    if j < len(syl): out.append(f'{len(syl) - j} syllabe(s) en trop')
    return out

def main():
    l1, l2 = load_app_words(1), load_app_words(2)
    off = official()
    vocab = {w[0] for w in l1} | {w[0] for w in l2} | off[1] | off[2] | EXTRA
    hsk2 = [w[0] for w in l2]
    problems = 0
    # 1. Chaque mot HSK 2 dans une seule unité
    seen = {}
    for uid, *_ , words, g, tip in [(u[0], u[1], u[2], u[3], u[4], u[5]) for u in UNITS]:
        for w in words.split():
            if w in seen: print(f'Mot en double : {w} ({seen[w]} et {uid})'); problems += 1
            seen[w] = uid
    missing = [w for w in hsk2 if w not in seen]; extra = [w for w in seen if w not in hsk2]
    if missing: print('Mots HSK 2 sans unité :', ' '.join(missing)); problems += 1
    if extra: print('Mots dans une unité mais pas dans la liste HSK 2 :', ' '.join(extra)); problems += 1
    # 2 et 3. Phrases : présence du mot, vocabulaire, pinyin
    all_sents = [(w, s) for w in seen for s in S.get(w, [])] + [(u[0], s) for u in UNITS for s in u[4]]
    for w in seen:
        if len(S.get(w, [])) != 2: print(f'{w} : {len(S.get(w, []))} phrase(s) au lieu de 2'); problems += 1
    for w, (zh, py, fr) in all_sents:
        if w in seen and not w.startswith('2') and w not in zh: print(f'{w} absent de « {zh} »'); problems += 1
        bad = [t for t, ok in segment(zh, vocab) if not ok]
        if bad: print(f'Hors HSK 1-2 dans « {zh} » : {" ".join(bad)}'); problems += 1
        for e in check_pinyin(zh, py): print(f'Pinyin de « {zh} » : {e}'); problems += 1
    n = sum(len(v) for v in S.values())
    print(f'\n{len(UNITS)} unités, {len(seen)} mots, {n} phrases d\'exemple + {sum(len(u[4]) for u in UNITS)} phrases modèles : {problems} problème(s)')
    if problems and '--force' not in sys.argv: sys.exit(1)
    # 4. Fichiers de l'appli
    ids = {w[0]: w[0] for w in l2}  # en HSK 2, l'identifiant d'un sens = ses caractères (premier sens)
    data = {ids[w]: [list(s) for s in S[w]] for w in seen}
    path = os.path.join(ROOT, 'data', 'sentences-hsk2.json')
    json.dump(data, open(path, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    js = ',\n'.join("  {id:%s, l:2, t:%s, d:%s, w:%s,\n   g:%s,\n   tip:%s}" % (json.dumps(u[0]), json.dumps(u[1], ensure_ascii=False), json.dumps(u[2], ensure_ascii=False), json.dumps(u[3], ensure_ascii=False), json.dumps([list(x) for x in u[4]], ensure_ascii=False), json.dumps(u[5], ensure_ascii=False)) for u in UNITS)
    html_path = os.path.join(ROOT, 'index.html'); html = open(html_path, encoding='utf8').read()
    block = '// <hsk2-unites> (généré par tools/content/hsk2.py : ne pas modifier à la main)\nLESSONS.push(\n' + js + '\n);\n// </hsk2-unites>'
    html, k = re.subn(r'// <hsk2-unites>.*?// </hsk2-unites>', lambda m: block, html, flags=re.S)
    if not k: print('Repère <hsk2-unites> introuvable dans index.html'); sys.exit(1)
    open(html_path, 'w', encoding='utf8').write(html)
    print(f'Écrit : data/sentences-hsk2.json ({os.path.getsize(path) // 1024} Ko) et le bloc des unités dans index.html')

if __name__ == '__main__': main()
