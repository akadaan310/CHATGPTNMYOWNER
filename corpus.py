# -*- coding: utf-8 -*-
"""Layer 0: the corpus index.  موضع is addressable at segment granularity."""
import re, unicodedata
from collections import defaultdict, namedtuple

DIAC = re.compile(r'[ؐ-ًؚ-ٰٟۖ-ۭـ]')
def rasm(s):
    """Strip diacritics -> consonantal skeleton. Normalise alif variants."""
    s = DIAC.sub('', s)
    s = s.replace('ٱ','ا').replace('أ','ا').replace('إ','ا')
    s = s.replace('آ','ا').replace('ى','ي').replace('ة','ه')
    return s

Seg = namedtuple('Seg','sura aya word seg form pos feats root lem rasm')

class Corpus:
    def __init__(self, path):
        self.segs = []                      # ordered list of Seg
        self.by_coord = {}                  # (s,a,w,g) -> Seg
        self.by_lem   = defaultdict(list)
        self.by_root  = defaultdict(list)
        self.by_rasm  = defaultdict(list)
        self.inl      = []                  # fawātiḥ segments
        self.aya_words = defaultdict(list)  # (s,a) -> [word indices]
        for line in open(path, encoding='utf-8'):
            line = line.rstrip('\n')
            if not line or '\t' not in line: continue
            loc, form, pos, feats = (line.split('\t') + ['','',''])[:4]
            p = loc.split(':')
            if len(p) != 4: continue
            s,a,w,g = map(int, p)
            root = lem = None
            for f in feats.split('|'):
                if f.startswith('ROOT:'): root = f[5:]
                elif f.startswith('LEM:'): lem = f[4:]
            sg = Seg(s,a,w,g,form,pos,feats,root,lem,rasm(form))
            self.segs.append(sg)
            self.by_coord[(s,a,w,g)] = sg
            if lem:  self.by_lem[lem].append(sg)
            if root: self.by_root[root].append(sg)
            self.by_rasm[sg.rasm].append(sg)
            if 'INL' in feats: self.inl.append(sg)
            if g == 1: self.aya_words[(s,a)].append(w)

    # ---- word-level view (a word = its concatenated segments) ----
    def word_text(self, s,a,w):
        return ''.join(x.form for x in self.segs
                       if x.sura==s and x.aya==a and x.word==w)

    def aya_text(self, s,a):
        return ' '.join(self.word_text(s,a,w) for w in self.aya_words[(s,a)])

    def span_text(self, s,a,w0,w1):
        return ' '.join(self.word_text(s,a,w) for w in range(w0,w1+1))

if __name__ == '__main__':
    import sys
    C = Corpus(sys.argv[1])
    print('segments:', len(C.segs))
    print('fawātiḥ tokens:', len(C.inl))
    print('30:1 ->', C.aya_text(30,1), '|', C.aya_text(30,2))
    print('13:1 ->', C.aya_text(13,1)[:60])
