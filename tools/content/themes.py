# -*- coding: utf-8 -*-
"""Classe chaque mot de data/vocab.json dans un thème (champ « th »), pour l'écran « Listes » de l'appli.

Ordre de décision : 1. corrections à la main (FIX) ; 2. mots-outils d'après la catégorie officielle (pronoms, prépositions,
conjonctions, particules, interjections) ; 3. mots-clés de la traduction française, thème par thème ; 4. catégorie
grammaticale (adjectif → « Décrire », verbe → « Actions », sinon « Idées et société »).
Lancer : python3 tools/content/themes.py   (écrit le champ th, puis docs/themes.md pour relecture)
"""
import json, os, re, unicodedata
ROOT = os.path.join(os.path.dirname(__file__), '..', '..')

# clé, nom affiché, caractère emblème
THEMES = [
    ('nombres', 'Nombres et quantités', '数'), ('temps', 'Temps, dates et heures', '时'), ('personnes', 'Famille et personnes', '人'),
    ('corps', 'Corps et santé', '身'), ('nourriture', 'Nourriture et boissons', '食'), ('maison', 'Maison, pièces et objets', '家'),
    ('vetements', 'Vêtements', '衣'), ('couleurs', 'Couleurs', '色'), ('ville', 'Lieux, ville et pays', '城'),
    ('transports', 'Transports et voyages', '车'), ('ecole', 'École et études', '学'), ('travail', 'Travail et métiers', '工'),
    ('argent', 'Argent et achats', '钱'), ('loisirs', 'Loisirs, sport et culture', '玩'), ('nature', 'Météo, nature et animaux', '天'),
    ('emotions', 'Sentiments et caractère', '心'), ('communication', 'Langue et communication', '话'), ('position', 'Position et direction', '方'),
    ('description', 'Décrire (adjectifs)', '形'), ('actions', 'Actions (verbes)', '动'), ('outils', 'Mots-outils de la grammaire', '的'),
    ('idees', 'Idées et société', '思'),
]
KW = {  # mots-clés (sans accents), cherchés en mot entier dans la traduction française
 'couleurs': 'rouge blanc noir vert bleu jaune gris rose couleur',
 'personnes': 'papa maman pere mere fils fille frere soeur enfant enfants mari femme homme ami amie copain copine grand-pere grand-mere oncle tante famille voisin monsieur madame mademoiselle invite parent parents bebe jeune personne personnes gens',
 'nombres': 'deux trois quatre cinq six sept huit neuf dix cent mille zero moitie chiffre nombre combien quelques premier fois kilogramme kilometre metre paire quantite double classificateur',
 'nourriture': 'manger boire riz the cafe lait oeuf oeufs viande mouton poisson fruit pomme pasteque banane legume plat plats repas dejeuner diner petit-dejeuner nouilles raviolis gateau gateaux pain biere jus soupe sucre sel bonbon chocolat faim soif delicieux baguettes bol assiette verre menu gout epice sucre acide amer boisson biscuit raisin tomate canard brioche en-cas cuisiner cuisine eau mineral',
 'corps': 'corps tete oeil yeux nez bouche oreille main pied jambe bras visage cheveux ventre dent dents sante malade maladie medecin hopital medicament medicaments fievre rhume tousser piqure infirmier docteur sueur peau mal',
 'vetements': 'vetement vetements chemise pantalon jupe chaussures chaussettes chapeau lunettes habiller',
 'maison': 'maison chambre piece salon salle toilettes porte fenetre table chaise lit canape refrigerateur lampe cle meubles ascenseur etage miroir serviette poubelle dentifrice climatisation boite sac parapluie valise bouteille stylo appareil ordinateur television radio cuillere couteau tasse journal',
 'transports': 'voiture taxi bus train avion velo bateau metro gare aeroport billet conduire voyage voyager passeport visa autoroute station embouteillage vol embarquement decoller atterrir touristique tourisme route',
 'ville': 'magasin supermarche restaurant hotel banque poste parc rue ville cinema librairie batiment pont ambassade quartier banlieue campagne pays capitale province chine pekin monde asie endroit lieu adresse yangzi muraille fleuve',
 'ecole': 'ecole eleve eleves etudiant etudiante etudier apprendre cours classe professeur examen devoirs livre cahier carnet dictionnaire caractere crayon gomme exercice reviser lecon universite diplome grammaire phrase lire ecrire bibliotheque tableau semestre college lycee primaire ecolier',
 'travail': 'travail travailler bureau entreprise collegue directeur reunion salaire metier profession policier avocat journaliste chauffeur serveur vendeur recruter postuler affaires deplacement acteur ecrivain guide',
 'argent': 'argent yuan yuans prix cher marche acheter vendre payer credit monnaie depenser remise gratuit riche pauvre economiser liquide centime',
 'loisirs': 'jouer sport basket foot nager courir danser chanter chanson musique film jeu piano tennis ping-pong badminton kung-fu fete photo photographier loisir passe-temps spectacle opera roman internet amuser promener vacances match competition karaoke',
 'nature': 'meteo pluie pleuvoir neige vent soleil nuage ensoleille nuageux couvert chaud froid saison printemps ete automne hiver arbre fleur herbe foret montagne riviere mer ocean lune etoile ciel terre animal animaux chien chat cheval oiseau panda tigre plante feuille climat temperature environnement pollution',
 'emotions': 'content heureux triste aimer amour peur inquieter fache fâcher emu excite decu fier timide serieux intelligent gentil patient paresseux courageux honnete sentiment humeur joie sourire rire pleurer esperer regretter surpris confiant stress calme mignon desole',
 'communication': 'dire parler demander repondre appeler telephoner telephone message sms lettre e-mail langue chinois mot expliquer raconter discuter bavarder presenter saluer bonjour merci pardon revoir allo site information nouvelle publicite',
 'temps': 'heure heures minute seconde jour semaine mois annee an matin matinee midi apres-midi soir nuit aujourd hier demain maintenant moment tot tard bientot deja date anniversaire week-end dimanche lundi siecle avenir passe age temps journee',
 'position': 'devant derriere gauche droite dessus dessous dans dehors interieur exterieur cote milieu nord sud est ouest face pres loin ici la-bas direction autour',
}
OUTILS_POS = ('代', '介', '连', '助', '叹', '前缀', '后缀', '拟声')
# Corrections à la main (mot ou identifiant de sens → thème), après relecture de docs/themes.md
FIX = {
 # deuxième relecture
 '号码': 'communication', '火': 'nature', '加油站': 'transports', '交通': 'transports', '景色': 'nature', '空气': 'nature', '普通话': 'communication',
 '孙子': 'personnes', '师傅': 'travail', '硕士': 'ecole', '教育': 'ecole', '奖金': 'travail', '文章': 'communication', '杂志': 'communication', '信封': 'communication',
 '座位': 'transports', '作者': 'travail', '左右': 'nombres', '自然': 'nature', '笑话': 'loisirs', '光': 'nature', '性别': 'personnes', '房东': 'maison', '顾客': 'argent',
 '观众': 'loisirs', '知识': 'ecole', '专业': 'ecole', '毛': 'argent', '秒': 'temps', '页': 'ecole', '快乐': 'emotions', '开心': 'emotions', '累': 'corps', '饱': 'nourriture',
 '困': 'corps', '讨厌': 'emotions', '幸福': 'emotions', '烦恼': 'emotions', '紧张': 'emotions', '所有': 'outils', '完全': 'outils', '实在': 'outils', '正好': 'outils',
 '暂时': 'outils', '相反': 'outils', '流利': 'communication', '得#2': 'actions', '重': 'description', '永远': 'temps', '咱们': 'personnes', '自己': 'personnes',
 '满意': 'emotions', '收入': 'argent', '购物': 'argent', '存': 'argent', '等#2': 'outils', '活动': 'loisirs', '研究': 'ecole', '翻译': 'communication', '对话': 'communication',
 '道歉': 'communication', '感谢': 'communication', '开玩笑': 'communication', '占线': 'communication', '联系': 'communication', '打印': 'travail', '复印': 'travail', '减肥': 'corps',
 # relecture du premier tri
 '黄河': 'ville', '黑板': 'ecole', '白': 'couleurs', '博士': 'ecole', '干杯': 'nourriture', '抱': 'actions', '提': 'actions', '厨房': 'maison', '脏': 'description', '咸': 'nourriture',
 '教室': 'ecole', '报纸': 'communication', '关键': 'idees', '重点': 'idees', '日记': 'idees', '寄': 'communication', '京剧': 'loisirs', '开': 'actions', '站': 'actions',
 '锻炼': 'loisirs', '脾气': 'emotions', '性格': 'emotions', '表格': 'idees', '丰富': 'description', '可怜': 'emotions', '行': 'outils', '爬山': 'loisirs',
 '差不多': 'outils', '可能': 'outils', '明白': 'actions', '一定': 'outils', '小心': 'actions', '一般': 'outils', '生气': 'emotions', '特别': 'outils', '突然': 'outils',
 '长#2': 'actions', '本来': 'outils', '成功': 'actions', '大概': 'outils', '感兴趣': 'emotions', '久': 'temps', '请': 'communication', '比': 'outils', '姓': 'personnes',
 '比较': 'outils', '变化': 'idees', '根据': 'outils', '欢迎': 'communication', '别人': 'personnes', '还#2': 'actions', '上午': 'temps', '以前': 'temps', '最后': 'temps',
 '最近': 'temps', '当时': 'temps', '成绩': 'ecole', '数学': 'ecole', '答案': 'ecole', '地图': 'transports', '个子': 'corps', '节目': 'loisirs', '新闻': 'communication',
 '传真': 'communication', '国籍': 'personnes', '一': 'nombres', '坐': 'actions', '穿': 'vetements', '把': 'outils', '帮忙': 'actions', '请假': 'travail', '洗澡': 'actions',
 '乘坐': 'transports', '只': 'outils', '种': 'nombres', '一会儿': 'temps', '分': 'nombres', '角': 'argent', '米': 'nombres', '元': 'argent', '段': 'nombres',
 '密码': 'communication', '底': 'temps', '加班': 'travail', '年级': 'ecole', '历史': 'idees', '同时': 'temps', '后来': 'temps', '刚才': 'temps', '过去': 'temps',
 '他': 'personnes', '她': 'personnes', '我': 'personnes', '你': 'personnes', '您': 'personnes', '我们': 'personnes', '大家': 'personnes', '它': 'outils',
 '谁': 'outils', '人': 'personnes', '先生': 'personnes', '小姐': 'personnes', '同学': 'ecole', '老师': 'ecole', '学生': 'ecole', '医生': 'corps',
 '喂': 'communication', '谢谢': 'communication', '再见': 'communication', '对不起': 'communication', '没关系': 'communication', '不客气': 'communication',
 '个': 'nombres', '本': 'nombres', '块': 'argent', '岁': 'temps', '点': 'temps', '号': 'temps', '分钟': 'temps', '小时': 'temps', '刻': 'temps', '半': 'nombres',
 '多少': 'nombres', '几': 'nombres', '两': 'nombres', '第一': 'nombres', '每': 'nombres', '些': 'nombres', '次': 'nombres', '件': 'nombres', '张': 'nombres',
 '条': 'nombres', '双': 'nombres', '只#2': 'nombres', '位': 'nombres', '辆': 'nombres', '层': 'maison', '楼': 'ville', '东': 'position', '西': 'position',
 '南': 'position', '北': 'position', '上': 'position', '下': 'position', '里': 'position', '外': 'position', '前面': 'position', '后面': 'position',
 '左边': 'position', '右边': 'position', '旁边': 'position', '中间': 'position', '附近': 'position', '对面': 'position', '周围': 'position', '远': 'position', '近': 'position', '离': 'position',
 '水': 'nourriture', '茶': 'nourriture', '菜': 'nourriture', '饭店': 'ville', '中国': 'ville', '北京': 'ville', '汉语': 'communication', '中文': 'communication', '字': 'ecole',
 '电脑': 'maison', '电视': 'maison', '手机': 'communication', '手表': 'maison', '杯子': 'maison', '东西': 'maison', '桌子': 'maison', '椅子': 'maison',
 '天气': 'nature', '下雨': 'nature', '冷': 'nature', '热': 'nature', '晴': 'nature', '阴': 'nature', '雪': 'nature', '猫': 'nature', '狗': 'nature',
 '书': 'ecole', '读': 'ecole', '写': 'ecole', '学习': 'ecole', '学校': 'ecole', '工作': 'travail', '医院': 'corps', '商店': 'ville', '出租车': 'transports', '飞机': 'transports',
 '买': 'argent', '钱': 'argent', '贵': 'argent', '便宜': 'argent', '卖': 'argent', '票': 'transports',
 '爱': 'emotions', '喜欢': 'emotions', '高兴': 'emotions', '想': 'actions', '会': 'actions', '能': 'actions', '可以': 'actions', '要': 'actions',
 '打电话': 'communication', '说': 'communication', '叫': 'communication', '名字': 'personnes', '认识': 'personnes', '家': 'maison',
 '是': 'outils', '有': 'outils', '在': 'outils', '的': 'outils', '了': 'outils', '吗': 'outils', '呢': 'outils', '吧': 'outils', '和': 'outils', '都': 'outils', '很': 'outils', '太': 'outils', '不': 'outils', '没有': 'outils',
 '这': 'outils', '那': 'outils', '哪': 'outils', '哪儿': 'outils', '什么': 'outils', '怎么': 'outils', '怎么样': 'outils', '为什么': 'outils',
}

def fold(s): return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn').replace('œ', 'oe').replace('’', "'")
WORD = {k: set(v.split()) for k, v in KW.items()}

def official_pos():
    pos = {}
    for line in open(os.path.join(ROOT, 'tools', 'content', 'hsk30-vocabulaire.tsv'), encoding='utf8'):
        if line.startswith('#'): continue
        c = line.rstrip('\n').split('\t')
        pos.setdefault(c[2], (c[5] if len(c) > 5 else '').replace('（', '').replace('）', ''))
    return pos

def theme(r, pos, sid):
    if sid in FIX: return FIX[sid]
    if r['h'] in FIX and sid == r['h']: return FIX[r['h']]
    p = pos.get(r['h'], '')
    first = p.split('、')[0] if p else ''
    if first in OUTILS_POS or (first == '副' and len(r['h']) <= 2): return 'outils'
    if first in ('数', '量', '数量'): return 'nombres'
    fr = fold(r['fr'])
    tokens = set(re.findall(r"[a-z0-9-]+", fr.split('(')[0])) | set(re.findall(r"[a-z0-9-]+", fr))
    head = set(re.findall(r"[a-z0-9-]+", re.split(r'[;,(]', fr)[0]))
    for key, *_ in THEMES:  # le sens principal d'abord, puis toute la traduction
        if key in WORD and head & WORD[key]: return key
    for key, *_ in THEMES:
        if key in WORD and tokens & WORD[key]: return key
    if first == '形' or 'a' in r.get('pos', [])[:1]: return 'description'
    if first == '动' or 'v' in r.get('pos', [])[:1]: return 'actions'
    return 'idees'

def main():
    path = os.path.join(ROOT, 'data', 'vocab.json')
    rows = json.load(open(path, encoding='utf8')); pos = official_pos(); seen = {}
    for r in rows:
        seen[r['h']] = seen.get(r['h'], 0) + 1
        sid = r['h'] if seen[r['h']] == 1 else f"{r['h']}#{seen[r['h']]}"
        r['th'] = theme(r, pos, sid)
    json.dump(rows, open(path, 'w', encoding='utf8'), ensure_ascii=False, indent=0)
    by = {}
    for r in rows: by.setdefault(r['th'], []).append(r)
    lines = ['# Thèmes du vocabulaire (relecture)', '', 'Généré par `tools/content/themes.py`. Corriger un classement : ajouter le mot dans FIX.', '']
    for key, name, g in THEMES:
        ws = by.get(key, [])
        lines += [f'## {name} ({len(ws)})', '', ' · '.join(f"{w['h']} {w['fr'].split(';')[0].split(',')[0]}" for w in ws), '']
    open(os.path.join(ROOT, 'docs', 'themes.md'), 'w', encoding='utf8').write('\n'.join(lines) + '\n')
    print(' · '.join(f"{name.split(' ')[0]} {len(by.get(k, []))}" for k, name, g in THEMES))

if __name__ == '__main__': main()
