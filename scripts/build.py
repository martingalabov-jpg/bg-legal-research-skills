#!/usr/bin/env python3
"""Rebuild the generated map file in skills/ and the upload zips in dist/.
Usage: python3 -I scripts/build.py [data/lex-map.json] [data/apis-map.json]"""
import json, sys, re, os, zipfile
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(H, 'data')
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else f'{R}/lex-map.json'))
a = json.load(open(sys.argv[2] if len(sys.argv) > 2 else f'{R}/apis-map.json'))
COURTS = {'const':'КС; Съд на ЕС','citizens':'ВАС и адм. съдилища; ЕСПЧ','criminal':'ВКС НК (ТР на ОСНК); ЕСПЧ','civil':'ВКС ГК (ТР на ОСГК/ОСГТК); Съд на ЕС','family':'ВКС ГК; ЕСПЧ','ip':'ВКС ТК/ГК; ВАС (марки, патенти); Съд на ЕС','judiciary':'ВКС; ЕСПЧ','commercial':'ВКС ТК (ТР на ОСТК); КЗК; Съд на ЕС','finance':'ВКС ТК; ВАС; Съд на ЕС','tax':'ВАС и адм. съдилища; Съд на ЕС','labor':'ВКС ГК (трудови спорове); ВАС (осигуряване)','admin':'ВАС и адм. съдилища; КС','territory':'ВАС и адм. съдилища; ВКС (вещни спорове)','environment':'ВАС; Съд на ЕС','agri':'ВАС; Съд на ЕС','health':'ВАС; ВКС (медицинска отговорност)','education':'ВАС; КС','transport':'ВАС; ВКС НК (транспортни престъпления); Съд на ЕС','security':'ВАС; ВКС НК; ЕСПЧ','intl':'КС; Съд на ЕС; ЕСПЧ'}
clean = lambda n: re.sub(r'\s*\((загл|изм|доп)[^)]*\)', '', n).strip()
by = {b['key']: {'label': b['label'], 'codes': [], 'laws': [], 'prac': []} for b in d['branches']}
for x in d['acts']: by[x['b']]['codes' if x['type'] == 'code' else 'laws'].append(x)
for p in d['practice']: by[p['b']]['prac'].append(p)
out = ['# Правна карта на България по отрасли', '', f'Източници: справочникът на lex.bg (кодекси и закони) и дървото на АПИС Уеб, {a["captured"]}. Линковете водят към актуалния консолидиран текст в lex.bg. Пътищата „В АПИС“ изискват абонамент.', '', '## Съдържание']
out += [f'- {v["label"]} (`{k}`)' for k, v in by.items()] + ['']
for k, v in by.items():
    out += [f'## {v["label"]}', f'Ключ: `{k}` · Меродавни съдилища: {COURTS[k]}', '']
    if v['codes']: out += ['**Кодекси:**'] + [f'- [{clean(x["name"])}](https://lex.bg/laws/ldoc/{x["id"]})' for x in sorted(v['codes'], key=lambda x: x['name'])]
    if v['laws']: out += ['**Закони:**'] + [f'- [{clean(x["name"])}](https://lex.bg/laws/ldoc/{x["id"]})' for x in sorted(v['laws'], key=lambda x: x['name'])]
    if a['branches'].get(k): out += ['**В АПИС:**'] + [f'- {x["p"]}' + (f' — {x["i"]}' if x['i'] else '') for x in a['branches'][k]]
    if v['prac']: out += [f'**Анализи в news.lex.bg** ({len(v["prac"])}, последни 8):'] + [f'- [{p["t"]}]({p["u"]})' for p in v['prac'][:8]]
    out.append('')
for target in ['bg-legal-map', 'bg-legal-research']:
    open(f'{H}/skills/{target}/references/bg-legal-map.md', 'w').write('\n'.join(out))
os.makedirs(f'{H}/dist', exist_ok=True)
for s in ['bg-legal-research', 'bg-legal-map', 'bg-legislation-search', 'bg-court-decisions-search']:
    with zipfile.ZipFile(f'{H}/dist/{s}.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(f'{H}/skills/{s}'):
            for f in files:
                full = os.path.join(root, f); z.write(full, os.path.relpath(full, f'{H}/skills'))
print('built', len('\n'.join(out)), 'chars + 4 zips in dist/')
