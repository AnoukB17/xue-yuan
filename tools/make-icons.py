# -*- coding: utf-8 -*-
"""Icônes de l'application installable : le caractère 学 au pinceau (police Ma Shan Zheng, licence OFL),
blanc sur vermillon, légèrement incliné comme le logo de l'appli.

Usage : python3 tools/make-icons.py chemin/vers/MaShanZheng-Regular.ttf
(police : https://github.com/google/fonts/tree/main/ofl/mashanzheng)
Écrit icons/icon-192.png, icon-512.png, icon-maskable-512.png, apple-touch-icon.png, favicon-32.png
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

FONT = sys.argv[1]
OUT = os.path.join(os.path.dirname(__file__), '..', 'icons')
os.makedirs(OUT, exist_ok=True)
VERM = (214, 58, 32)        # --verm (mode clair)
WHITE = (255, 255, 255)

def icon(size, radius_ratio, glyph_ratio, path):
    S = size * 4  # dessin en grand puis réduction : bords plus nets
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if radius_ratio is None: d.rectangle([0, 0, S, S], fill=VERM)
    else: d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * radius_ratio), fill=VERM)
    font = ImageFont.truetype(FONT, int(S * glyph_ratio))
    g = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    bbox = gd.textbbox((0, 0), '学', font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    gd.text(((S - w) / 2 - bbox[0], (S - h) / 2 - bbox[1]), '学', font=font, fill=WHITE)
    g = g.rotate(6, resample=Image.BICUBIC, center=(S / 2, S / 2))  # même inclinaison que le logo (-6°)
    img.alpha_composite(g)
    img = img.resize((size, size), Image.LANCZOS)
    if radius_ratio is None: img = img.convert('RGB')  # icônes sans transparence (iOS, masquable)
    img.save(os.path.join(OUT, path), optimize=True)
    print(path, size, os.path.getsize(os.path.join(OUT, path)) // 1024, 'Ko')

icon(192, .22, .68, 'icon-192.png')
icon(512, .22, .68, 'icon-512.png')
icon(512, None, .52, 'icon-maskable-512.png')   # Android découpe un cercle : le caractère reste dans les 80 % du centre
icon(180, None, .66, 'apple-touch-icon.png')    # iOS arrondit lui-même les coins
icon(32, .22, .74, 'favicon-32.png')
