import re, json, urllib.request, html, sys
UA={'User-Agent':'Mozilla/5.0'}
def get(u, enc='windows-1251'):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read().decode(enc,'replace')
def crawl(kind):
    out={}; 
    for p in range(0,300):
        t=get(f'https://lex.bg/laws/tree/{kind}'+(f'/{p}' if p else ''))
        before=len(out)
        for m in re.finditer(r'<a[^>]+href="[^"]*?/laws/ldoc/(-?\d+)"[^>]*>(.*?)</a>',t,re.S):
            i,name=m.group(1),re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',m.group(2)))).strip()
            if i=='521957377' or not name: continue
            out.setdefault(i,name)
        if len(out)==before or not re.search(r'>\s*&gt;\s*</a>|>\s*>\s*</a>',t): break
    return [{'id':k,'name':v} for k,v in out.items()]
res={k:crawl(k) for k in ['code','laws']}
# practice
cats={'civil':'%d0%b3%d1%80%d0%b0%d0%b6%d0%b4%d0%b0%d0%bd%d1%81%d0%ba%d0%be-%d0%bf%d1%80%d0%b0%d0%b2%d0%be','criminal':'%d0%bd%d0%b0%d0%ba%d0%b0%d0%b7%d0%b0%d1%82%d0%b5%d0%bb%d0%bd%d0%be-%d0%bf%d1%80%d0%b0%d0%b2%d0%be','admin':'%d0%b0%d0%b4%d0%bc%d0%b8%d0%bd%d0%b8%d1%81%d1%82%d1%80%d0%b0%d1%82%d0%b8%d0%b2%d0%bd%d0%be-%d0%bf%d1%80%d0%b0%d0%b2%d0%be','constitutional':'constitutional-law'}
pub={}
for k,slug in cats.items():
    base=f'https://news.lex.bg/category/analysis/{slug}/'
    items=[];seen=set();pages=1
    for p in range(1,60):
        try: t=get(base+(f'page/{p}/' if p>1 else ''),'utf-8')
        except Exception as e: break
        if p==1:
            pages=max([1]+[int(x) for x in re.findall(r'/page/(\d+)/',t)])
        n0=len(items)
        for m in re.finditer(r'<h[23][^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',t,re.S):
            u,ti=m.group(1),re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',m.group(2)))).strip()
            if 'category' in u or len(ti)<15 or u in seen: continue
            seen.add(u); items.append({'t':ti,'u':u})
        if p>=pages or len(items)==n0: break
    pub[k]={'pages':pages,'items':items}
res['pub']=pub
json.dump(res,open(sys.argv[1],'w'),ensure_ascii=False,indent=0)
print({k:len(v) for k,v in res.items() if k!='pub'},{k:(v['pages'],len(v['items'])) for k,v in pub.items()})
