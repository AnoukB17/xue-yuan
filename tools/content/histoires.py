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
EXTRA = {1: {'安娜', '米饭'}, 2: {'上海'}, 5: {'云南', '老王'}, 6: {'小李', '小林'}}  # 米饭 : aussi le nom du chat de l'histoire 1-3

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

STORIES[3] = [
 ('3-demenagement', '搬家', 'Le déménagement', 'Un nouveau logement près du travail, et des amis pour porter les cartons.',
  [('上个月，我们搬家了。', 'Shàng gè yuè, wǒmen bānjiā le.', 'Le mois dernier, nous avons déménagé.'),
   ('新家在一个很安静的小区里，旁边有一个公园。', 'Xīn jiā zài yí gè hěn ānjìng de xiǎoqū li, pángbiān yǒu yí gè gōngyuán.', 'Le nouveau logement est dans une résidence très calme, avec un parc à côté.'),
   ('以前的房子离公司很远，我每天要坐一个多小时的车。', 'Yǐqián de fángzi lí gōngsī hěn yuǎn, wǒ měi tiān yào zuò yí gè duō xiǎoshí de chē.', 'L\'ancien logement était loin du bureau, je passais chaque jour plus d\'une heure dans les transports.'),
   ('现在走路只要五分钟。', 'Xiànzài zǒulù zhǐ yào wǔ fēnzhōng.', 'Maintenant, il me suffit de cinq minutes à pied.'),
   ('搬家那天，朋友们都来帮忙。', 'Bānjiā nà tiān, péngyoumen dōu lái bāngmáng.', 'Le jour du déménagement, tous mes amis sont venus aider.'),
   ('我们把桌子、椅子和很多箱子搬上了楼。', 'Wǒmen bǎ zhuōzi, yǐzi hé hěn duō xiāngzi bānshangle lóu.', 'Nous avons monté à l\'étage les tables, les chaises et beaucoup de cartons.'),
   ('大家都很累，可是都很高兴。', 'Dàjiā dōu hěn lèi, kěshì dōu hěn gāoxìng.', 'Tout le monde était fatigué, mais content.'),
   ('晚上，我请大家吃饭，谢谢他们的帮助。', 'Wǎnshang, wǒ qǐng dàjiā chī fàn, xièxie tāmen de bāngzhù.', 'Le soir, je les ai invités à dîner pour les remercier de leur aide.'),
   ('现在我非常喜欢我的新家。', 'Xiànzài wǒ fēicháng xǐhuan wǒ de xīn jiā.', 'Maintenant, j\'adore mon nouveau chez-moi.')],
  [('Pourquoi le nouveau logement est-il pratique ?', ['Il est près du travail', 'Il est très grand', 'Il est bon marché']),
   ('Qui a aidé au déménagement ?', ['Les amis', 'Les parents', 'Personne']),
   ('Qu\'y a-t-il à côté du nouveau logement ?', ['Un parc', 'Une gare', 'Un hôpital'])]),
 ('3-examen', '汉语考试', 'L\'examen de chinois', 'Des révisions, un bon conseil du professeur et le jour J.',
  [('下个星期我要参加汉语考试。', 'Xià gè xīngqī wǒ yào cānjiā Hànyǔ kǎoshì.', 'La semaine prochaine, je passe un examen de chinois.'),
   ('为了准备考试，我每天晚上都复习两个小时。', 'Wèile zhǔnbèi kǎoshì, wǒ měi tiān wǎnshang dōu fùxí liǎng gè xiǎoshí.', 'Pour le préparer, je révise deux heures tous les soirs.'),
   ('我觉得听和说最难。', 'Wǒ juéde tīng hé shuō zuì nán.', 'Je trouve que l\'écoute et l\'oral sont le plus difficile.'),
   ('老师告诉我：“你要多听多说，不要怕说错。”', 'Lǎoshī gàosu wǒ: “Nǐ yào duō tīng duō shuō, búyào pà shuōcuò.”', 'Le professeur m\'a dit : « Écoute et parle beaucoup, n\'aie pas peur de te tromper. »'),
   ('所以我每天都跟中国朋友聊天儿。', 'Suǒyǐ wǒ měi tiān dōu gēn Zhōngguó péngyou liáotiānr.', 'Alors je discute tous les jours avec des amis chinois.'),
   ('考试那天，我很早就到了。', 'Kǎoshì nà tiān, wǒ hěn zǎo jiù dào le.', 'Le jour de l\'examen, je suis arrivé très tôt.'),
   ('题不太难，我都做完了。', 'Tí bú tài nán, wǒ dōu zuòwán le.', 'Les questions n\'étaient pas trop difficiles, j\'ai tout terminé.'),
   ('一个月以后，老师说我考得很好！', 'Yí gè yuè yǐhòu, lǎoshī shuō wǒ kǎo de hěn hǎo!', 'Un mois plus tard, le professeur m\'a dit que j\'avais très bien réussi !')],
  [('Combien de temps révise-t-il chaque soir ?', ['Deux heures', 'Une heure', 'Trois heures']),
   ('Quel conseil donne le professeur ?', ['Écouter et parler beaucoup', 'Lire beaucoup de livres', 'Se coucher tôt']),
   ('Quel est le résultat ?', ['Il a très bien réussi', 'Il a échoué', 'Il ne le sait pas encore'])]),
 ('3-panda', '大熊猫', 'Les pandas', 'Une visite au zoo pour voir les pandas géants.',
  [('大熊猫是中国的动物，很多人都喜欢它们。', 'Dàxióngmāo shì Zhōngguó de dòngwù, hěn duō rén dōu xǐhuan tāmen.', 'Le panda géant est un animal de Chine, beaucoup de gens l\'adorent.'),
   ('它们的身体是黑色和白色的。', 'Tāmen de shēntǐ shì hēisè hé báisè de.', 'Leur corps est noir et blanc.'),
   ('大熊猫每天要吃很多东西，还要睡很长时间。', 'Dàxióngmāo měi tiān yào chī hěn duō dōngxi, hái yào shuì hěn cháng shíjiān.', 'Les pandas mangent beaucoup chaque jour, et dorment longtemps.'),
   ('上个周末，我和姐姐去动物园看大熊猫。', 'Shàng gè zhōumò, wǒ hé jiějie qù dòngwùyuán kàn dàxióngmāo.', 'Le week-end dernier, ma grande sœur et moi sommes allées voir les pandas au zoo.'),
   ('动物园里的人特别多，我们等了很长时间。', 'Dòngwùyuán li de rén tèbié duō, wǒmen děngle hěn cháng shíjiān.', 'Il y avait énormément de monde au zoo, nous avons attendu longtemps.'),
   ('终于看到了！一只大熊猫正在树上睡觉。', 'Zhōngyú kàndào le! Yì zhī dàxióngmāo zhèngzài shù shang shuìjiào.', 'Enfin ! Un panda dormait dans un arbre.'),
   ('还有一只在地上吃东西。', 'Hái yǒu yì zhī zài dìshang chī dōngxi.', 'Un autre mangeait par terre.'),
   ('姐姐照了很多照片，说下次还要再来。', 'Jiějie zhàole hěn duō zhàopiàn, shuō xià cì hái yào zài lái.', 'Ma sœur a pris plein de photos et a dit qu\'elle voulait revenir.')],
  [('Où sont-elles allées ?', ['Au zoo', 'Au parc', 'À la montagne']),
   ('Que faisait l\'un des pandas ?', ['Il dormait dans un arbre', 'Il jouait avec un ballon', 'Il nageait']),
   ('Qui a pris des photos ?', ['La grande sœur', 'Un gardien', 'Personne'])]),
]

STORIES[4] = [
 ('4-achats', '网购的烦恼', 'Les tracas des achats en ligne', 'Pratique, rapide… sauf quand le pull ne ressemble pas à la photo.',
  [('现在越来越多的人喜欢在网上购物。', 'Xiànzài yuè lái yuè duō de rén xǐhuan zài wǎng shang gòuwù.', 'De plus en plus de gens aiment acheter en ligne.'),
   ('我也是，衣服、零食，甚至水果都在网上买。', 'Wǒ yě shì, yīfu, língshí, shènzhì shuǐguǒ dōu zài wǎng shang mǎi.', 'Moi aussi : vêtements, en-cas, et même les fruits, j\'achète tout en ligne.'),
   ('网购又方便又便宜，快递第二天就能送到。', 'Wǎnggòu yòu fāngbiàn yòu piányi, kuàidì dì-èr tiān jiù néng sòngdào.', 'C\'est pratique et bon marché, et le colis arrive dès le lendemain.'),
   ('不过，网购也有不少麻烦。', 'Búguò, wǎnggòu yě yǒu bù shǎo máfan.', 'Mais les achats en ligne ont aussi pas mal d\'inconvénients.'),
   ('上个月我买了一件毛衣，照片上看起来很好看。', 'Shàng gè yuè wǒ mǎile yí jiàn máoyī, zhàopiàn shang kàn qǐlái hěn hǎokàn.', 'Le mois dernier, j\'ai acheté un pull qui avait l\'air très joli en photo.'),
   ('可是收到以后，我发现颜色和照片完全不一样。', 'Kěshì shōudào yǐhòu, wǒ fāxiàn yánsè hé zhàopiàn wánquán bù yíyàng.', 'Mais en le recevant, j\'ai vu que la couleur était complètement différente.'),
   ('而且衣服太小了，我穿不了。', 'Érqiě yīfu tài xiǎo le, wǒ chuān bu liǎo.', 'En plus, il était trop petit, impossible de le porter.'),
   ('我只好把毛衣送回去，钱过了两个星期才回来。', 'Wǒ zhǐhǎo bǎ máoyī sòng huíqù, qián guòle liǎng gè xīngqī cái huílái.', 'J\'ai dû renvoyer le pull, et je n\'ai été remboursé que deux semaines plus tard.'),
   ('从此，我买衣服以前，一定先看看别人怎么说。', 'Cóngcǐ, wǒ mǎi yīfu yǐqián, yídìng xiān kànkan biérén zěnme shuō.', 'Depuis, avant d\'acheter un vêtement, je regarde toujours d\'abord ce qu\'en disent les autres.')],
  [('Quels avantages cite-t-il ?', ['C\'est pratique et bon marché', 'La qualité est toujours bonne', 'On peut essayer avant']),
   ('Quel était le problème du pull ?', ['Mauvaise couleur et trop petit', 'Trop cher', 'Jamais livré']),
   ('Que fait-il désormais ?', ['Il lit d\'abord l\'avis des autres', 'Il n\'achète plus en ligne', 'Il achète en magasin'])]),
 ('4-entretien', '第一次面试', 'Mon premier entretien', 'Le stress, une question imprévue… et une réponse honnête.',
  [('大学毕业以后，我开始找工作。', 'Dàxué bìyè yǐhòu, wǒ kāishǐ zhǎo gōngzuò.', 'Après mes études, j\'ai commencé à chercher du travail.'),
   ('我给很多公司发了邮件。', 'Wǒ gěi hěn duō gōngsī fāle yóujiàn.', 'J\'ai envoyé des e-mails à beaucoup d\'entreprises.'),
   ('终于，一家公司请我去面试。', 'Zhōngyú, yì jiā gōngsī qǐng wǒ qù miànshì.', 'Enfin, une entreprise m\'a invité à un entretien.'),
   ('面试前一天晚上，我紧张得睡不着。', 'Miànshì qián yì tiān wǎnshang, wǒ jǐnzhāng de shuì bu zháo.', 'La veille au soir, j\'étais si nerveux que je n\'arrivais pas à dormir.'),
   ('第二天，我穿上最好的衣服，提前半个小时到了公司。', 'Dì-èr tiān, wǒ chuānshang zuì hǎo de yīfu, tíqián bàn gè xiǎoshí dàole gōngsī.', 'Le lendemain, j\'ai mis mes plus beaux vêtements et je suis arrivé une demi-heure en avance.'),
   ('经理问了我很多问题，比如为什么想来这家公司。', 'Jīnglǐ wènle wǒ hěn duō wèntí, bǐrú wèishénme xiǎng lái zhè jiā gōngsī.', 'Le responsable m\'a posé beaucoup de questions, par exemple pourquoi je voulais travailler chez eux.'),
   ('可是有一个问题，我完全没想到。', 'Kěshì yǒu yí gè wèntí, wǒ wánquán méi xiǎngdào.', 'Mais il y a eu une question à laquelle je ne m\'attendais pas du tout.'),
   ('我说：“这个问题我不太清楚，但是我愿意学习。”', 'Wǒ shuō: “Zhège wèntí wǒ bú tài qīngchu, dànshì wǒ yuànyì xuéxí.”', 'J\'ai répondu : « Je ne connais pas bien ce sujet, mais je suis prêt à apprendre. »'),
   ('一个星期以后，公司给我打电话：我得到了这个工作！', 'Yí gè xīngqī yǐhòu, gōngsī gěi wǒ dǎ diànhuà: wǒ dédàole zhège gōngzuò!', 'Une semaine plus tard, l\'entreprise m\'a appelé : j\'avais le poste !')],
  [('Comment se sentait-il la veille ?', ['Si nerveux qu\'il ne dormait pas', 'Très détendu', 'Malade']),
   ('Comment a-t-il répondu à la question imprévue ?', ['Honnêtement, en disant qu\'il voulait apprendre', 'Il a inventé une réponse', 'Il n\'a rien dit']),
   ('Quel est le résultat ?', ['Il a obtenu le poste', 'Il a été refusé', 'Il attend encore'])]),
 ('4-nouvel-an', '回老家过年', 'Rentrer pour le Nouvel An', 'Un billet difficile à obtenir, un train bondé, et la joie de retrouver sa famille.',
  [('每年过年，很多人都要回老家。', 'Měi nián guònián, hěn duō rén dōu yào huí lǎojiā.', 'Chaque Nouvel An, beaucoup de gens rentrent dans leur ville natale.'),
   ('火车票非常难买，我提前一个月就在网上订了票。', 'Huǒchēpiào fēicháng nán mǎi, wǒ tíqián yí gè yuè jiù zài wǎng shang dìngle piào.', 'Les billets de train sont très difficiles à obtenir : j\'ai réservé en ligne un mois à l\'avance.'),
   ('火车上到处都是人，有的人一直站着。', 'Huǒchē shang dàochù dōu shì rén, yǒu de rén yìzhí zhànzhe.', 'Il y avait du monde partout dans le train, certains sont restés debout tout le trajet.'),
   ('虽然路上很累，但是一想到能见到家人，我就很高兴。', 'Suīrán lù shang hěn lèi, dànshì yì xiǎngdào néng jiàndào jiārén, wǒ jiù hěn gāoxìng.', 'Le voyage était fatigant, mais dès que je pensais à ma famille, j\'étais heureux.'),
   ('到家的时候，妈妈已经做好了一桌子菜。', 'Dào jiā de shíhou, māma yǐjīng zuòhǎole yì zhuōzi cài.', 'Quand je suis arrivé, maman avait déjà préparé une table pleine de plats.'),
   ('爷爷奶奶给了我一个红包，祝我新年快乐。', 'Yéye nǎinai gěile wǒ yí gè hóngbāo, zhù wǒ xīnnián kuàilè.', 'Mes grands-parents m\'ont donné une enveloppe rouge et m\'ont souhaité une bonne année.'),
   ('晚上，全家人一边吃饭，一边看电视节目。', 'Wǎnshang, quán jiā rén yìbiān chī fàn, yìbiān kàn diànshì jiémù.', 'Le soir, toute la famille a dîné en regardant les émissions de télévision.'),
   ('十二点的时候，大家互相说“新年好”。', 'Shí\'èr diǎn de shíhou, dàjiā hùxiāng shuō “xīnnián hǎo”.', 'À minuit, tout le monde s\'est souhaité « bonne année ».'),
   ('对我来说，这是一年中最幸福的时候。', 'Duì wǒ lái shuō, zhè shì yì nián zhōng zuì xìngfú de shíhou.', 'Pour moi, c\'est le moment le plus heureux de l\'année.')],
  [('Comment a-t-il obtenu son billet ?', ['Il l\'a réservé en ligne un mois avant', 'Il l\'a acheté à la gare', 'Un ami le lui a donné']),
   ('Qu\'ont donné les grands-parents ?', ['Une enveloppe rouge', 'Un livre', 'Des vêtements']),
   ('Que fait la famille le soir ?', ['Elle dîne en regardant la télévision', 'Elle va au restaurant', 'Elle se couche tôt'])]),
]

STORIES[5] = [
 ('5-livreur', '送外卖的老王', 'Lao Wang, livreur de repas', 'Une livraison sous l\'orage et un geste qui touche une cliente.',
  [('老王是一名送外卖的。', 'Lǎo Wáng shì yì míng sòng wàimài de.', 'Lao Wang est livreur de repas.'),
   ('他每天早上八点开始工作，晚上十点才回家。', 'Tā měi tiān zǎoshang bā diǎn kāishǐ gōngzuò, wǎnshang shí diǎn cái huí jiā.', 'Il commence à huit heures du matin et ne rentre qu\'à dix heures du soir.'),
   ('不管刮风还是下雨，他都骑着电动车在城市里到处跑。', 'Bùguǎn guā fēng háishi xià yǔ, tā dōu qízhe diàndòngchē zài chéngshì li dàochù pǎo.', 'Qu\'il vente ou qu\'il pleuve, il sillonne la ville sur son scooter électrique.'),
   ('有一天，他送外卖的时候，突然下起了暴雨。', 'Yǒu yì tiān, tā sòng wàimài de shíhou, tūrán xià qǐle bàoyǔ.', 'Un jour, pendant une livraison, un violent orage a éclaté.'),
   ('他担心饭菜凉了，就把自己的衣服盖在了盒饭上。', 'Tā dānxīn fàncài liáng le, jiù bǎ zìjǐ de yīfu gài zài le héfàn shang.', 'De peur que le repas refroidisse, il l\'a couvert avec son propre vêtement.'),
   ('到了顾客家，他全身都湿了。', 'Dàole gùkè jiā, tā quánshēn dōu shī le.', 'En arrivant chez la cliente, il était trempé de la tête aux pieds.'),
   ('顾客打开门，看到他的样子，非常感动。', 'Gùkè dǎkāi mén, kàndào tā de yàngzi, fēicháng gǎndòng.', 'La cliente a ouvert la porte et, en le voyant ainsi, a été très émue.'),
   ('她连忙让老王进来，还给他倒了一杯热茶。', 'Tā liánmáng ràng Lǎo Wáng jìnlái, hái gěi tā dàole yì bēi rè chá.', 'Elle l\'a vite fait entrer et lui a servi une tasse de thé chaud.'),
   ('后来，她在网上给老王写了很长的好评。', 'Hòulái, tā zài wǎng shang gěi Lǎo Wáng xiěle hěn cháng de hǎopíng.', 'Ensuite, elle lui a laissé un long avis très positif en ligne.'),
   ('老王说：“这份工作虽然很辛苦，但是被人理解的感觉真好。”', 'Lǎo Wáng shuō: “Zhè fèn gōngzuò suīrán hěn xīnkǔ, dànshì bèi rén lǐjiě de gǎnjué zhēn hǎo.”', 'Lao Wang dit : « Ce travail est dur, mais être compris, ça fait vraiment du bien. »')],
  [('À quelle heure Lao Wang rentre-t-il chez lui ?', ['À dix heures du soir', 'À six heures du soir', 'À midi']),
   ('Qu\'a-t-il fait pendant l\'orage ?', ['Il a couvert le repas avec son vêtement', 'Il s\'est abrité sous un pont', 'Il a fait demi-tour']),
   ('Comment la cliente l\'a-t-elle remercié ?', ['Un thé chaud et un avis positif', 'Un gros pourboire', 'Elle n\'a rien fait'])]),
 ('5-yunnan', '在云南迷路', 'Perdus au Yunnan', 'Plus de réseau, la nuit qui tombe… et un vieil homme serviable.',
  [('去年夏天，我和两个朋友去云南旅行。', 'Qùnián xiàtiān, wǒ hé liǎng gè péngyou qù Yúnnán lǚxíng.', 'L\'été dernier, je suis partie au Yunnan avec deux amis.'),
   ('我们没有参加旅行团，而是自己安排路线。', 'Wǒmen méiyǒu cānjiā lǚxíngtuán, ér shì zìjǐ ānpái lùxiàn.', 'Nous n\'étions pas en voyage organisé : nous avions préparé notre itinéraire nous-mêmes.'),
   ('有一天，我们想去山里的一个小村子。', 'Yǒu yì tiān, wǒmen xiǎng qù shān li de yí gè xiǎo cūnzi.', 'Un jour, nous voulions aller dans un petit village de montagne.'),
   ('没想到，手机突然没有信号了，地图也打不开。', 'Méi xiǎngdào, shǒujī tūrán méiyǒu xìnhào le, dìtú yě dǎ bu kāi.', 'Mais soudain, plus de réseau, et la carte ne s\'ouvrait plus.'),
   ('天渐渐暗了，我们开始着急了。', 'Tiān jiànjiàn àn le, wǒmen kāishǐ zháojí le.', 'Il commençait à faire sombre, nous nous sommes inquiétés.'),
   ('这时候，一位老人赶着几头牛从山上下来。', 'Zhè shíhou, yí wèi lǎorén gǎnzhe jǐ tóu niú cóng shān shang xiàlái.', 'C\'est alors qu\'un vieil homme est descendu de la montagne avec quelques vaches.'),
   ('虽然他的话我们听不太懂，但是他很热心地给我们指路。', 'Suīrán tā de huà wǒmen tīng bu tài dǒng, dànshì tā hěn rèxīn de gěi wǒmen zhǐ lù.', 'Nous ne comprenions pas bien ce qu\'il disait, mais il nous a indiqué le chemin avec beaucoup de gentillesse.'),
   ('最后，他亲自带我们走到了村子里。', 'Zuìhòu, tā qīnzì dài wǒmen zǒudàole cūnzi li.', 'Finalement, il nous a conduits lui-même jusqu\'au village.'),
   ('村里的人请我们吃了一顿非常好吃的晚饭。', 'Cūn li de rén qǐng wǒmen chīle yí dùn fēicháng hǎochī de wǎnfàn.', 'Les villageois nous ont offert un dîner délicieux.'),
   ('这次迷路反而变成了我们旅行中最难忘的经历。', 'Zhè cì mílù fǎn\'ér biànchéngle wǒmen lǚxíng zhōng zuì nánwàng de jīnglì.', 'Nous être perdus est finalement devenu le meilleur souvenir du voyage.')],
  [('Pourquoi se sont-ils perdus ?', ['Le téléphone n\'avait plus de réseau', 'Ils n\'avaient pas de carte', 'Le guide était parti']),
   ('Qui les a aidés ?', ['Un vieil homme avec ses vaches', 'Un policier', 'Un autre touriste']),
   ('Que pensent-ils de cette aventure ?', ['C\'est leur meilleur souvenir', 'C\'était un mauvais moment', 'Ils ne s\'en souviennent pas'])]),
 ('5-grand-mere', '奶奶学手机', 'Grand-mère et le smartphone', 'À 75 ans, grand-mère apprend à se servir d\'un smartphone.',
  [('奶奶今年七十五岁，以前从来不用手机。', 'Nǎinai jīnnián qīshíwǔ suì, yǐqián cónglái bú yòng shǒujī.', 'Grand-mère a 75 ans et ne s\'était jamais servie d\'un téléphone portable.'),
   ('去年，我们给她买了一部智能手机。', 'Qùnián, wǒmen gěi tā mǎile yí bù zhìnéng shǒujī.', 'L\'an dernier, nous lui avons acheté un smartphone.'),
   ('刚开始，奶奶觉得太复杂了，总说自己学不会。', 'Gāng kāishǐ, nǎinai juéde tài fùzá le, zǒng shuō zìjǐ xué bu huì.', 'Au début, elle trouvait ça trop compliqué et disait toujours qu\'elle n\'y arriverait pas.'),
   ('我耐心地教她怎么打视频电话、怎么拍照。', 'Wǒ nàixīn de jiāo tā zěnme dǎ shìpín diànhuà, zěnme pāizhào.', 'Je lui ai patiemment appris à passer des appels vidéo et à prendre des photos.'),
   ('她把每一步都写在本子上，每天练习。', 'Tā bǎ měi yí bù dōu xiě zài běnzi shang, měi tiān liànxí.', 'Elle notait chaque étape dans un carnet et s\'entraînait tous les jours.'),
   ('一个月以后，奶奶居然学会了在网上买菜。', 'Yí gè yuè yǐhòu, nǎinai jūrán xuéhuìle zài wǎng shang mǎi cài.', 'Un mois plus tard, à notre grande surprise, elle faisait ses courses en ligne.'),
   ('现在她每天都给在外地工作的孙女发消息。', 'Xiànzài tā měi tiān dōu gěi zài wàidì gōngzuò de sūnnǚ fā xiāoxi.', 'Aujourd\'hui, elle envoie chaque jour des messages à sa petite-fille qui travaille dans une autre ville.'),
   ('有时候她还会发一些有意思的表情，让我们哈哈大笑。', 'Yǒushíhou tā hái huì fā yìxiē yǒu yìsi de biǎoqíng, ràng wǒmen hāhā dà xiào.', 'Parfois, elle envoie même des émojis amusants qui nous font éclater de rire.'),
   ('奶奶常说：“活到老，学到老。”', 'Nǎinai cháng shuō: “Huó dào lǎo, xué dào lǎo.”', 'Grand-mère dit souvent : « On apprend à tout âge. »')],
  [('Pourquoi grand-mère pensait-elle ne pas y arriver ?', ['Elle trouvait ça trop compliqué', 'Elle n\'avait pas le temps', 'Le téléphone était cassé']),
   ('Comment a-t-elle appris ?', ['En notant chaque étape et en s\'entraînant', 'En suivant un cours', 'Toute seule, sans aide']),
   ('Que fait-elle maintenant ?', ['Elle envoie des messages à sa petite-fille', 'Elle a rendu le téléphone', 'Elle ne l\'utilise que pour appeler'])]),
]

STORIES[6] = [
 ('6-potager', '阳台上的菜园', 'Un potager sur le balcon', 'Des débuts difficiles, de la persévérance, et une récolte à partager.',
  [('在大城市里，很多年轻人都向往田园生活。', 'Zài dà chéngshì li, hěn duō niánqīngrén dōu xiàngwǎng tiányuán shēnghuó.', 'En ville, beaucoup de jeunes rêvent d\'une vie à la campagne.'),
   ('我的邻居小李就是其中之一。', 'Wǒ de línjū Xiǎo Lǐ jiù shì qízhōng zhī yī.', 'Ma voisine, Petite Li, en fait partie.'),
   ('她在阳台上种了番茄、辣椒和黄瓜。', 'Tā zài yángtái shang zhòngle fānqié, làjiāo hé huángguā.', 'Elle a planté des tomates, des piments et des concombres sur son balcon.'),
   ('刚开始的时候，菜总是长不好，叶子也一片片地变黄。', 'Gāng kāishǐ de shíhou, cài zǒngshì zhǎng bu hǎo, yèzi yě yí piàn piàn de biàn huáng.', 'Au début, les plants poussaient mal et les feuilles jaunissaient une à une.'),
   ('她并没有放弃，而是在网上查资料，向有经验的人请教。', 'Tā bìng méiyǒu fàngqì, ér shì zài wǎng shang chá zīliào, xiàng yǒu jīngyàn de rén qǐngjiào.', 'Elle n\'a pas abandonné : elle s\'est documentée en ligne et a demandé conseil à des gens expérimentés.'),
   ('慢慢地，她掌握了浇水的规律。', 'Mànmàn de, tā zhǎngwòle jiāo shuǐ de guīlǜ.', 'Peu à peu, elle a compris le bon rythme d\'arrosage.'),
   ('到了夏天，阳台上居然结满了果实。', 'Dàole xiàtiān, yángtái shang jūrán jiēmǎnle guǒshí.', 'L\'été venu, le balcon était, contre toute attente, couvert de fruits.'),
   ('她把吃不完的菜分享给邻居们，大家都夸她能干。', 'Tā bǎ chī bu wán de cài fēnxiǎng gěi línjūmen, dàjiā dōu kuā tā nénggàn.', 'Elle a partagé avec les voisins ce qu\'elle ne pouvait pas manger, et tout le monde l\'a félicitée.'),
   ('小李说，种菜不仅让她吃上了新鲜的蔬菜，更让她学会了耐心。', 'Xiǎo Lǐ shuō, zhòng cài bùjǐn ràng tā chīshangle xīnxiān de shūcài, gèng ràng tā xuéhuìle nàixīn.', 'Petite Li dit que le jardinage lui a apporté des légumes frais, mais surtout de la patience.'),
   ('在忙碌的城市生活中，这一小片绿色给了她很多安慰。', 'Zài mánglù de chéngshì shēnghuó zhōng, zhè yì xiǎo piàn lǜsè gěile tā hěn duō ānwèi.', 'Dans l\'agitation de la ville, ce petit coin de verdure lui apporte beaucoup de réconfort.')],
  [('Quel problème a-t-elle eu au début ?', ['Les plants poussaient mal', 'Elle n\'avait pas de graines', 'Ses voisins se plaignaient']),
   ('Qu\'a-t-elle fait pour réussir ?', ['Elle s\'est documentée et a demandé conseil', 'Elle a abandonné puis recommencé', 'Elle a acheté des plants déjà grands']),
   ('Que lui a surtout appris le jardinage ?', ['La patience', 'La cuisine', 'Le commerce'])]),
 ('6-ia', '人工智能来了', 'L\'intelligence artificielle arrive au bureau', 'La peur d\'être remplacé, puis un nouvel équilibre.',
  [('最近，我们公司开始使用人工智能来处理日常工作。', 'Zuìjìn, wǒmen gōngsī kāishǐ shǐyòng réngōng zhìnéng lái chǔlǐ rìcháng gōngzuò.', 'Récemment, mon entreprise a commencé à utiliser l\'intelligence artificielle pour les tâches quotidiennes.'),
   ('它能在几分钟里翻译一份文件，还能自动回复客户的邮件。', 'Tā néng zài jǐ fēnzhōng li fānyì yí fèn wénjiàn, hái néng zìdòng huífù kèhù de yóujiàn.', 'Elle traduit un document en quelques minutes et répond automatiquement aux e-mails des clients.'),
   ('一开始，不少同事担心自己会被机器取代。', 'Yì kāishǐ, bù shǎo tóngshì dānxīn zìjǐ huì bèi jīqì qǔdài.', 'Au début, beaucoup de collègues avaient peur d\'être remplacés par la machine.'),
   ('有人甚至开始偷偷地找新工作。', 'Yǒu rén shènzhì kāishǐ tōutōu de zhǎo xīn gōngzuò.', 'Certains ont même commencé à chercher un autre emploi en cachette.'),
   ('然而，经理在会上明确地表示，公司引进这项技术，是为了提高效率，而不是减少员工。', 'Rán\'ér, jīnglǐ zài huì shang míngquè de biǎoshì, gōngsī yǐnjìn zhè xiàng jìshù, shì wèile tígāo xiàolǜ, ér bú shì jiǎnshǎo yuángōng.', 'Mais en réunion, le directeur a clairement dit que l\'entreprise adoptait cette technologie pour gagner en efficacité, pas pour réduire le personnel.'),
   ('果然，几个月以后，大家从重复的工作中解放了出来。', 'Guǒrán, jǐ gè yuè yǐhòu, dàjiā cóng chóngfù de gōngzuò zhōng jiěfàngle chūlái.', 'Et en effet, quelques mois plus tard, tout le monde était libéré des tâches répétitives.'),
   ('我们有了更多的时间去思考和创新。', 'Wǒmen yǒule gèng duō de shíjiān qù sīkǎo hé chuàngxīn.', 'Nous avons plus de temps pour réfléchir et innover.'),
   ('当然，人工智能也不是什么都会，它偶尔也会犯一些可笑的错误。', 'Dāngrán, réngōng zhìnéng yě bú shì shénme dōu huì, tā ǒu\'ěr yě huì fàn yìxiē kěxiào de cuòwù.', 'Bien sûr, l\'IA ne sait pas tout faire : il lui arrive de commettre des erreurs ridicules.'),
   ('所以，最终做决定的还是人。', 'Suǒyǐ, zuìzhōng zuò juédìng de háishi rén.', 'C\'est donc toujours l\'humain qui prend la décision finale.')],
  [('De quoi les collègues avaient-ils peur ?', ['D\'être remplacés par la machine', 'De devoir travailler plus', 'De perdre leurs données']),
   ('Pourquoi l\'entreprise utilise-t-elle l\'IA selon le directeur ?', ['Pour gagner en efficacité', 'Pour réduire le personnel', 'Pour économiser l\'électricité']),
   ('Qui prend la décision finale ?', ['Les humains', 'L\'IA', 'Les clients'])]),
 ('6-lettre', '一封没寄出的信', 'Une lettre jamais envoyée', 'Une vieille dispute, une lettre retrouvée, et une amitié qui renaît.',
  [('整理房间的时候，我发现了一封旧信。', 'Zhěnglǐ fángjiān de shíhou, wǒ fāxiànle yì fēng jiù xìn.', 'En rangeant ma chambre, j\'ai trouvé une vieille lettre.'),
   ('信是十年前我写给高中同学小林的，却一直没有寄出去。', 'Xìn shì shí nián qián wǒ xiě gěi gāozhōng tóngxué Xiǎo Lín de, què yìzhí méiyǒu jì chūqù.', 'Je l\'avais écrite il y a dix ans à Petite Lin, une camarade de lycée, mais je ne l\'avais jamais envoyée.'),
   ('那时我们因为一件小事吵了架，彼此都不肯先道歉。', 'Nà shí wǒmen yīnwèi yí jiàn xiǎo shì chǎole jià, bǐcǐ dōu bù kěn xiān dàoqiàn.', 'À l\'époque, nous nous étions disputées pour une bêtise, et aucune ne voulait s\'excuser la première.'),
   ('后来大家各自上了大学，渐渐失去了联系。', 'Hòulái dàjiā gèzì shàngle dàxué, jiànjiàn shīqùle liánxì.', 'Puis chacune est partie à l\'université, et nous nous sommes peu à peu perdues de vue.'),
   ('读着信上的话，我不禁笑了，心里却有些难过。', 'Dúzhe xìn shang de huà, wǒ bùjīn xiào le, xīn li què yǒuxiē nánguò.', 'En relisant la lettre, je n\'ai pas pu m\'empêcher de sourire, mais j\'avais un peu de peine.'),
   ('犹豫了很长时间，我终于在网上找到了她的联系方式。', 'Yóuyùle hěn cháng shíjiān, wǒ zhōngyú zài wǎng shang zhǎodàole tā de liánxì fāngshì.', 'Après avoir longtemps hésité, j\'ai fini par trouver ses coordonnées en ligne.'),
   ('我把信拍成照片发给了她，并且写了一句：“对不起，迟到了十年。”', 'Wǒ bǎ xìn pāi chéng zhàopiàn fā gěi le tā, bìngqiě xiěle yí jù: “Duìbuqǐ, chídàole shí nián.”', 'Je lui ai envoyé la lettre en photo, avec un mot : « Pardon, avec dix ans de retard. »'),
   ('没想到，她很快就回复了：“我也一直想对你说这句话。”', 'Méi xiǎngdào, tā hěn kuài jiù huífù le: “Wǒ yě yìzhí xiǎng duì nǐ shuō zhè jù huà.”', 'À ma surprise, elle a vite répondu : « Moi aussi, je voulais te dire ça depuis toujours. »'),
   ('下个月，我们约好在老地方见面。', 'Xià gè yuè, wǒmen yuēhǎo zài lǎo dìfang jiànmiàn.', 'Le mois prochain, nous nous retrouvons à notre endroit habituel.'),
   ('原来，有些友情并不会因为时间而消失。', 'Yuánlái, yǒuxiē yǒuqíng bìng bú huì yīnwèi shíjiān ér xiāoshī.', 'Certaines amitiés, finalement, ne disparaissent pas avec le temps.')],
  [('Pourquoi s\'étaient-elles disputées ?', ['Pour une bêtise', 'Pour de l\'argent', 'À cause d\'un garçon']),
   ('Comment a-t-elle envoyé la lettre ?', ['En photo, en ligne', 'Par la poste', 'En main propre']),
   ('Comment a réagi son amie ?', ['Elle voulait aussi s\'excuser', 'Elle n\'a pas répondu', 'Elle était fâchée'])]),
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
