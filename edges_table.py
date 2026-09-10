# -*- coding: utf-8 -*-
"""Precompute the edge field for every āyah so the navigator can produce
scrolls live from whatever the reader is treading."""
import sys, json, os
sys.path.insert(0,'/home/claude/retl')
from corpus import Corpus
from sabab import SababIndex
from generate import Generator
SC='/tmp/claude-0/-home-claude/092f1e73-6422-5ef9-9c35-46685f42aa9b/scratchpad/'
C=Corpus(SC+'quran-morphology.txt'); S=SababIndex(C); g=Generator(C,S)

TIER={'مُجَاوِر':0,'جِوَار':1,'سُورَة':2,'عُبُور':3}
SABAB={'تجاور مصحفي':0,'جِوَار':1,'صيغة مشتركة':2,'تكرار لفظي (جذر)':3,
       'تكرار لفظي (لفظ)':4,'اشتمال حرفي':5}
E={}
for (s,a) in sorted(C.aya_words):
    ws=C.aya_words[(s,a)]
    sp=(s,a,ws[0],ws[min(len(ws),5)-1])
    rows=[]
    for t,name,ev,bits,ty,score,tier in g.edges(sp)[:6]:
        rows.append([t[0],t[1],round(score,1),round(bits,1),
                     TIER.get(tier,2),SABAB.get(name,2),ev[:30],
                     0 if ty=='نصّي' else 1])
    if rows: E[f"{s}:{a}"]=rows
json.dump(E, open('/home/claude/retl/edges.json','w',encoding='utf-8'),
          ensure_ascii=False, separators=(',',':'))
print('edges.json', round(os.path.getsize('/home/claude/retl/edges.json')/1e6,2),'MB ·',
      len(E),'āyāt ·', sum(len(v) for v in E.values()),'edges')
from collections import Counter
c=Counter(r[4] for v in E.values() for r in v); n=sum(c.values())
inv={v:k for k,v in TIER.items()}
print('  field mix:', ' · '.join(f"{inv[k]} {100*v/n:.0f}%" for k,v in c.most_common()))
