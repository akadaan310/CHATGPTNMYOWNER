# -*- coding: utf-8 -*-
"""Build the embedded data bundle for المِرْتَال."""
import sys, json, math
sys.path.insert(0,'/home/claude/retl')
from corpus import Corpus
from sabab import SababIndex
from generate import Generator
SC='/tmp/claude-0/-home-claude/092f1e73-6422-5ef9-9c35-46685f42aa9b/scratchpad/'

NAMES = """الفاتحة|Al-Fātiḥah;البقرة|Al-Baqarah;آل عمران|Āl ʿImrān;النساء|An-Nisāʾ;المائدة|Al-Māʾidah;
الأنعام|Al-Anʿām;الأعراف|Al-Aʿrāf;الأنفال|Al-Anfāl;التوبة|At-Tawbah;يونس|Yūnus;هود|Hūd;يوسف|Yūsuf;
الرعد|Ar-Raʿd;إبراهيم|Ibrāhīm;الحجر|Al-Ḥijr;النحل|An-Naḥl;الإسراء|Al-Isrāʾ;الكهف|Al-Kahf;مريم|Maryam;
طه|Ṭā Hā;الأنبياء|Al-Anbiyāʾ;الحج|Al-Ḥajj;المؤمنون|Al-Muʾminūn;النور|An-Nūr;الفرقان|Al-Furqān;
الشعراء|Ash-Shuʿarāʾ;النمل|An-Naml;القصص|Al-Qaṣaṣ;العنكبوت|Al-ʿAnkabūt;الروم|Ar-Rūm;لقمان|Luqmān;
السجدة|As-Sajdah;الأحزاب|Al-Aḥzāb;سبأ|Sabaʾ;فاطر|Fāṭir;يس|Yā Sīn;الصافات|Aṣ-Ṣāffāt;ص|Ṣād;الزمر|Az-Zumar;
غافر|Ghāfir;فصلت|Fuṣṣilat;الشورى|Ash-Shūrā;الزخرف|Az-Zukhruf;الدخان|Ad-Dukhān;الجاثية|Al-Jāthiyah;
الأحقاف|Al-Aḥqāf;محمد|Muḥammad;الفتح|Al-Fatḥ;الحجرات|Al-Ḥujurāt;ق|Qāf;الذاريات|Adh-Dhāriyāt;الطور|Aṭ-Ṭūr;
النجم|An-Najm;القمر|Al-Qamar;الرحمن|Ar-Raḥmān;الواقعة|Al-Wāqiʿah;الحديد|Al-Ḥadīd;المجادلة|Al-Mujādilah;
الحشر|Al-Ḥashr;الممتحنة|Al-Mumtaḥanah;الصف|Aṣ-Ṣaff;الجمعة|Al-Jumuʿah;المنافقون|Al-Munāfiqūn;
التغابن|At-Taghābun;الطلاق|Aṭ-Ṭalāq;التحريم|At-Taḥrīm;الملك|Al-Mulk;القلم|Al-Qalam;الحاقة|Al-Ḥāqqah;
المعارج|Al-Maʿārij;نوح|Nūḥ;الجن|Al-Jinn;المزمل|Al-Muzzammil;المدثر|Al-Muddaththir;القيامة|Al-Qiyāmah;
الإنسان|Al-Insān;المرسلات|Al-Mursalāt;النبأ|An-Nabaʾ;النازعات|An-Nāziʿāt;عبس|ʿAbasa;التكوير|At-Takwīr;
الانفطار|Al-Infiṭār;المطففين|Al-Muṭaffifīn;الانشقاق|Al-Inshiqāq;البروج|Al-Burūj;الطارق|Aṭ-Ṭāriq;
الأعلى|Al-Aʿlā;الغاشية|Al-Ghāshiyah;الفجر|Al-Fajr;البلد|Al-Balad;الشمس|Ash-Shams;الليل|Al-Layl;
الضحى|Aḍ-Ḍuḥā;الشرح|Ash-Sharḥ;التين|At-Tīn;العلق|Al-ʿAlaq;القدر|Al-Qadr;البينة|Al-Bayyinah;
الزلزلة|Az-Zalzalah;العاديات|Al-ʿĀdiyāt;القارعة|Al-Qāriʿah;التكاثر|At-Takāthur;العصر|Al-ʿAṣr;
الهمزة|Al-Humazah;الفيل|Al-Fīl;قريش|Quraysh;الماعون|Al-Māʿūn;الكوثر|Al-Kawthar;الكافرون|Al-Kāfirūn;
النصر|An-Naṣr;المسد|Al-Masad;الإخلاص|Al-Ikhlāṣ;الفلق|Al-Falaq;الناس|An-Nās"""
NAMES=[x.strip().split('|') for x in NAMES.replace('\n','').split(';') if x.strip()]
assert len(NAMES)==114, len(NAMES)

C=Corpus(SC+'quran-morphology.txt'); S=SababIndex(C); g=Generator(C,S)
q=json.load(open(SC+'t_quran.json',encoding='utf-8'))
TEXT=[]; 
for i in range(1,115):
    vs=sorted(q[str(i)], key=lambda v:v['verse'])
    TEXT.append([v['text'] for v in vs])

# verses where word-splitting disagrees with the morphology → whole-verse fallback
BAD=[]
for si,vs in enumerate(TEXT,1):
    for ai,t in enumerate(vs,1):
        n=len([x for x in t.replace('۞','').split() if x.strip()])
        if n!=len(C.aya_words.get((si,ai),[])): BAD.append(f"{si}:{ai}")

def path(F):
    """A فرقان → citation-only JSON. رتلة is a sequence of citations, so that is all we store."""
    return dict(a=list(F['anchor']),
                e=[[n,ev[:52],round(b,1),ty] for n,ev,b,ty in F['edges']],
                r=[[role,[list(sp) for sp in ret]] for role,ret in F['retlat']],
                w=round(F['bits'],1))

def tarteel(seed,n):
    return [path(F) for F in g.tarteel(seed,n)]

# ---------------- مَرَاتِل : one ترتيل per sūrah ----------------
maratil={}
for s in range(1,115):
    seed=[(s,a,1,min(3,len(C.aya_words[(s,a)]))) for a in range(1,min(6,len(TEXT[s-1])+1))]
    maratil[str(s)]=tarteel(seed,3)

# ---------------- الحُرُوف الحُكَمَاء : four constellations ----------------
FW=S.fawatih
def openers(suras): return [(s,1,1,1) for s in suras]
huruf=[
 dict(k='ubur', ar='العُبُور', en='The Crossings',
      note='الجَمْعُ لا يَجوزُ إلا مُثبَتًا — of all 91 pairs of clusters, only two unions are themselves attested.',
      sub='المر = الم ∪ الر · المص = الم ∪ ص',
      suras=[13,7], t=tarteel([(13,1,1,4),(7,1,1,1),(30,1,1,1)],3)),
 dict(k='alm', ar='أُسْرَةُ الٓمٓ', en='The Alif-Lām-Mīm Family',
      note='Six sūrahs open on one cluster. Each continuation is a different destination from the same node.',
      sub='٢ · ٣ · ٢٩ · ٣٠ · ٣١ · ٣٢',
      suras=FW['الم'], t=tarteel(openers(FW['الم']),4)),
 dict(k='alr', ar='أُسْرَةُ الٓرٰ', en='The Alif-Lām-Rā Family',
      note='Five sūrahs — and المر sits embedded among them at 13, between 12 and 14, where the two families cross.',
      sub='١٠ · ١١ · ١٢ · [١٣] · ١٤ · ١٥',
      suras=FW['الر'], t=tarteel(openers(FW['الر']),4)),
 dict(k='hm', ar='أُسْرَةُ حٰمٓ', en='The Ḥā-Mīm Family',
      note='Seven consecutive sūrahs — the longest unbroken run of one cluster in the muṣḥaf. At 42 the opening doubles: حم then عسق.',
      sub='٤٠ → ٤٦ · عسق at ٤٢',
      suras=FW['حم'], t=tarteel(openers(FW['حم']),4)),
]

# ---------------- السِّيَر : seeded on the name-lemma alone ----------------
SEEDS=[('مُوسَى','Mūsā'),('إِبْراهِيم','Ibrāhīm'),('فِرْعَوْن','Firʿawn'),('نُوح','Nūḥ'),
       ('مَرْيَم','Maryam'),('يُوسُف','Yūsuf'),('لُوط','Lūṭ'),('عِيسَى','ʿĪsā'),
       ('يَعْقُوب','Yaʿqūb'),('شُعَيْب','Shuʿayb'),('هُود','Hūd'),('زَكَرِيّا','Zakariyyā'),
       ('يَحْيَى','Yaḥyā'),('يُونُس','Yūnus'),('إِدْرِيس','Idrīs'),('إِلْياس','Ilyās')]
siyar=[]
for lem,tr in SEEDS:
    hits=sorted(S.by_lem.get(lem,[]))
    if not hits: continue
    siyar.append(dict(ar=lem, tr=tr, n=len(hits),
                      suras=sorted({h[0] for h in hits}),
                      t=tarteel([(s,a,w,w) for (s,a,w) in hits],3)))

BUNDLE=dict(names=NAMES, text=TEXT, bad=BAD, fawatih=FW,
            maratil=maratil, huruf=huruf, siyar=siyar,
            N=len(S.words))
json.dump(BUNDLE, open('/home/claude/retl/bundle.json','w',encoding='utf-8'),
          ensure_ascii=False, separators=(',',':'))
import os
print('bundle.json', round(os.path.getsize('/home/claude/retl/bundle.json')/1e6,2),'MB')
print('maratil:',len(maratil),' huruf:',len(huruf),' siyar:',len(siyar),' fallback verses:',len(BAD))
