#!/usr/bin/env python3
"""lex.bg helper — title search across the act trees and full-text grep of one act.

  lexbg.py find "<query>" [--kinds laws,code,ords,regs,reg_laws]   # title search (cached 7 days)
  lexbg.py tree <kind>                                              # dump one tree as JSON lines
  lexbg.py text <ldoc-id> [--grep "<regex>"] [--article "40"] [--ctx 600]
lex.bg pages are windows-1251; its own site search is broken (returns nothing), so do not use it.
"""
import sys, re, json, html, os, time, argparse, urllib.request
UA = {'User-Agent': 'Mozilla/5.0'}
KINDS = ['code', 'laws', 'ords', 'regs', 'reg_laws']
CACHE = os.path.expanduser('~/.cache/lexbg'); os.makedirs(CACHE, exist_ok=True)

def get(url):
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
    return raw.decode('windows-1251', 'replace')

def clean(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', '', s))).strip()

def tree(kind):
    path = f'{CACHE}/{kind}.json'
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < 7 * 86400:
        return json.load(open(path))
    out = {}
    for p in range(0, 1000):
        t = get(f'https://lex.bg/laws/tree/{kind}' + (f'/{p}' if p else ''))
        before = len(out)
        for m in re.finditer(r'<a[^>]+href="[^"]*?/laws/ldoc/(-?\d+)"[^>]*>(.*?)</a>', t, re.S):
            i, name = m.group(1), clean(m.group(2))
            if i != '521957377' and name:
                out.setdefault(i, name)
        if len(out) == before or not re.search(r'>\s*(&gt;|>)\s*</a>', t):
            break
    res = [{'id': k, 'name': v, 'kind': kind, 'url': f'https://lex.bg/laws/ldoc/{k}'} for k, v in out.items()]
    json.dump(res, open(path, 'w'), ensure_ascii=False)
    return res

def norm(s):
    return s.lower().replace('ѝ', 'и')

def find(q, kinds):
    words = [w for w in norm(q).split() if len(w) > 2]
    stems = [w[:max(4, len(w) - 2)] for w in words]  # crude stemming: наредба/наредбата/наредби
    hits = []
    for k in kinds:
        for a in tree(k):
            n = norm(a['name'])
            score = sum(1 for s in stems if s in n)
            if score == len(stems) or (len(stems) > 2 and score >= len(stems) - 1):
                hits.append((score, a))
    hits.sort(key=lambda x: (-x[0], len(x[1]['name'])))
    for _, a in hits[:60]:
        print(f"[{a['kind']}] {a['name']}\n    {a['url']}")
    print(f'-- {len(hits)} hits' + (' (first 60 shown)' if len(hits) > 60 else ''))

def text(i, grep=None, article=None, ctx=600):
    t = get(f'https://lex.bg/laws/ldoc/{i}')
    t = re.sub(r'<(script|style).*?</\1>', '', t, flags=re.S)
    t = re.sub(r'<br\s*/?>|</p>|</div>', '\n', t)
    body = re.sub(r'[ \t]+', ' ', html.unescape(re.sub('<[^>]+>', '', t)))
    body = re.sub(r'\n\s*\n+', '\n', body)
    title = re.search(r'\n\s*((?:ЗАКОН|КОДЕКС|НАРЕДБА|ПРАВИЛНИК|КОНСТИТУЦИЯ)[^\n]{0,250})', body)
    print('#', title.group(1).strip() if title else i, f'— https://lex.bg/laws/ldoc/{i}')
    if article:
        m = re.search(rf'\n\s*Чл\.\s*{re.escape(article)}\.(.*?)(?=\n\s*Чл\.\s*\d|\Z)', body, re.S)
        print(('Чл. ' + article + '.' + m.group(1)).strip()[:6000] if m else f'Чл. {article} not found')
        return
    if grep:
        n = 0
        for m in re.finditer(grep, body, re.I):
            s = max(0, m.start() - ctx // 2)
            print('…' + body[s:m.end() + ctx // 2].replace('\n', ' ') + '…\n'); n += 1
            if n >= 15: print('-- more hits truncated'); break
        print(f'-- {n} hits'); return
    print(body[:8000])

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd'); ap.add_argument('arg')
    ap.add_argument('--kinds', default=','.join(KINDS)); ap.add_argument('--grep'); ap.add_argument('--article')
    ap.add_argument('--ctx', type=int, default=600)
    a = ap.parse_args()
    if a.cmd == 'find': find(a.arg, a.kinds.split(','))
    elif a.cmd == 'tree': [print(json.dumps(x, ensure_ascii=False)) for x in tree(a.arg)]
    elif a.cmd == 'text': text(a.arg, a.grep, a.article, a.ctx)
    else: sys.exit(__doc__)
