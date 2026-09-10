# -*- coding: utf-8 -*-
"""Per-word INFORMATIONAL edges only.

قُرْب is a property of the coordinate, not of the word — the neighbourhood of
30:2 is the same whichever of its words you touch. So the client reconstructs
الجِوَار from structure and only وَزْن-bearing edges travel with the page."""
import sys, json, os, math
sys.path.insert(0,'/home/claude/retl')
from corpus import Corpus
from sabab import SababIndex
SC='/tmp/claude-0/-home-claude/092f1e73-6422-5ef9-9c35-46685f42aa9b/scratchpad/'
C=Corpus(SC+'quran-morphology.txt'); S=SababIndex(C); N=len(S.words)
W=lambda n: math.log2(N/n) if n else 0.0
SABAB={'صيغة مشتركة':2,'تكرار لفظي (جذر)':3,'تكرار لفظي (لفظ)':4,'اشتمال حرفي':5}
FLOOR=11.0          # word-level floor: a token must carry real information
TOP=3

out={}
for k in sorted(S.words):
    s,a,w = k
    cand={}
    for name,hits in [('اشتمال حرفي',S.ishtimal(k)),('صيغة مشتركة',S.sigha(k,4)),
                      ('تكرار لفظي (جذر)',S.takrar(k,True)),('تكرار لفظي (لفظ)',S.takrar(k,False))]:
        for t,typ,ev,cnt in hits:
            b=W(cnt)
            if b < FLOOR: continue
            if t[0]==s and t[1]==a: continue
            key=(t[0],t[1])
            if key not in cand or b>cand[key][2]:
                cand[key]=(t,name,b,ev,typ)
    rows=sorted(cand.values(), key=lambda x:-x[2])[:TOP]
    if rows:
        # nested by verse so the sura:aya prefix is written once, not per word
        out.setdefault(f"{s}:{a}",{})[str(w)]=[
            [r[0][0],r[0][1],round(r[2],1),SABAB.get(r[1],2),
             r[3].split(':')[-1][:20],0 if r[4]=='نصّي' else 1] for r in rows]
json.dump(out, open('/home/claude/retl/words.json','w',encoding='utf-8'),
          ensure_ascii=False, separators=(',',':'))
print('words.json', round(os.path.getsize('/home/claude/retl/words.json')/1e6,2),'MB')
print(f'  {len(out):,} of {len(S.words):,} words carry an informational edge '
      f'({100*len(out)/len(S.words):.0f}%)')
print(f'  {sum(len(v) for v in out.values()):,} edges')
