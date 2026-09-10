# -*- coding: utf-8 -*-
"""Data for الرُّكُوب — the onboarding. Only the verses actually cited travel with it."""
import sys, json, math
sys.path.insert(0,'/home/claude/retl')
from corpus import Corpus
from sabab import SababIndex
from generate import Generator
SC='/tmp/claude-0/-home-claude/092f1e73-6422-5ef9-9c35-46685f42aa9b/scratchpad/'
C=Corpus(SC+'quran-morphology.txt'); S=SababIndex(C); g=Generator(C,S); N=len(S.words)
q=json.load(open(SC+'t_quran.json',encoding='utf-8'))
DISP={}
for k,vs in q.items():
    for v in vs: DISP[(v['chapter'],v['verse'])]=v['text']
BITS=lambda n: round(math.log2(N/n),1)

NEED=set()
def need(s,a): NEED.add((s,a)); return [s,a]

# ---------- ١ الانْجِرَاء : the Basmalah's real branches ----------
BASM=[]
for w in C.aya_words[(1,1)]:
    opts=[]
    for t,name,ev,bits,ty in g.edges((1,1,w,w))[:4]:
        ts,ta,_=t
        wc=len(DISP[(ts,ta)].replace('۞','').split())
        opts.append(dict(to=need(ts,ta), span=[1,min(7,wc)], sabab=name,
                         ev=ev, bits=round(bits,1), ty=ty))
    BASM.append(dict(w=w, cite=f"1:1:{w}", opts=opts))
need(1,1)

# ---------- ٢ المِيقَات : الٓمٓ docks six times, then crosses ----------
def head(s,a,n=4):
    wc=len(DISP[(s,a)].replace('۞','').split())
    return dict(to=need(s,a), span=[1,min(n,wc)])
ALM=[head(s,2) for s in S.fawatih['الم']]
for s in S.fawatih['الم']: need(s,1)
CROSS=dict(alr=head(12,1,5), almr=head(13,1,4), alms=head(7,1,1))
need(12,1); need(13,1); need(7,1)

# ---------- ٣ الوِجْهَة ----------
WIJHA=[]
for lab,tr,lem in [
  ('مُسْلِمًا مُؤْمِنًا حَنِيفًا','the declared state','__default__'),
  ('يَا يَحْيَى','Yaḥyā','يَحْيَى'), ('يَا زَكَرِيَّا','Zakariyyā','زَكَرِيّا'),
  ('يَا دَاوُودُ','Dāwūd','داوُد'), ('بَنِي آدَم','Banī Ādam','آدَم'),
  ('يَا عِيسَى ابْنَ مَرْيَم','ʿĪsā ibn Maryam','عِيسَى'), ('يَا مَرْيَم','Maryam','مَرْيَم'),
  ('الإِنْسَان','al-Insān','إِنسان'), ('يَا أَيُّهَا النَّبِي','al-Nabī','نَبِيّ'),
  ('يَا مُوسَى','Mūsā','مُوسَى'), ('يَا أَيُّهَا النَّاس','al-Nās','ناس'),
  ('يَا أَيُّهَا الرُّسُل','al-Rusul','رَسُول'),
  ('يَا أَيُّهَا الَّذِينَ آمَنُوا','alladhīna āmanū','آمَنَ')]:
    if lem=='__default__':
        ks=set(S.by_lem.get('سَجَدَ',[]))|set(S.by_lem.get('خَلْق',[]))
    else:
        ks=set(S.by_lem.get(lem,[]))
    n=len(ks); b=BITS(n) if n else 0
    WIJHA.append(dict(ar=lab, tr=tr, n=n, bits=b,
                      suras=len({k[0] for k in ks}),
                      band=('wide' if b<9 else 'mid' if b<11.5 else 'narrow'),
                      default=(lem=='__default__')))

TEXT={f"{s}:{a}": DISP[(s,a)] for (s,a) in sorted(NEED)}
WORDS={k: len(v.replace('۞','').split()) for k,v in TEXT.items()}
json.dump(dict(basm=BASM, alm=ALM, cross=CROSS, wijha=WIJHA, text=TEXT, words=WORDS,
               fawatih={k:v for k,v in S.fawatih.items()}),
          open('/home/claude/retl/awwal.json','w',encoding='utf-8'),
          ensure_ascii=False, separators=(',',':'))
import os
print('awwal.json', os.path.getsize('/home/claude/retl/awwal.json'), 'bytes ·',
      len(TEXT),'verses carried')
for b in BASM:
    print(f"  {b['cite']}  {len(b['opts'])} options: " +
          ', '.join(f"{o['to'][0]}:{o['to'][1]}@{o['bits']}b" for o in b['opts']))
