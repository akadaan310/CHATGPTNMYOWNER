# -*- coding: utf-8 -*-
"""Layer 1: the سبب index — one deterministic candidate generator per cause type.
Every edge produced is typed (نصّي | إدراكي) and carries its evidence."""
from collections import defaultdict
from corpus import rasm

NASSI, IDRAKI = 'نصّي', 'إدراكي'

class SababIndex:
    def __init__(self, C, ngram_max=4):
        self.C = C
        # ---- word-level table: (s,a,w) -> (rasm, [pos...], [lem...], [root...])
        self.words = {}
        wl = defaultdict(list)
        for sg in C.segs: wl[(sg.sura,sg.aya,sg.word)].append(sg)
        for k,segs in wl.items():
            self.words[k] = dict(
                rasm = ''.join(x.rasm for x in segs),
                pos  = [x.pos for x in segs],
                lem  = [x.lem for x in segs if x.lem],
                root = [x.root for x in segs if x.root],
                inl  = any('INL' in x.feats for x in segs))
        self.order = sorted(self.words)                      # muṣḥaf order
        self.pos_ix = {k:i for i,k in enumerate(self.order)}
        self.pos_of = {k:v for k,v in self.words.items()}
        # ---- inverted indexes ----
        self.by_lem, self.by_root = defaultdict(set), defaultdict(set)
        for k,v in self.words.items():
            for l in v['lem']:  self.by_lem[l].add(k)
            for r in v['root']: self.by_root[r].add(k)
        # ---- n-gram (formula) index over rasm word sequences ----
        self.ngrams = defaultdict(set)
        by_aya = defaultdict(list)
        for k in self.order: by_aya[(k[0],k[1])].append(k)
        for aya, keys in by_aya.items():
            forms = [self.words[k]['rasm'] for k in keys]
            for n in range(2, ngram_max+1):
                for i in range(len(forms)-n+1):
                    self.ngrams[' '.join(forms[i:i+n])].add(keys[i]+(n,))
        # ---- fawātiḥ table ----
        self.fawatih = {}
        for k,v in self.words.items():
            if v['inl']:
                self.fawatih.setdefault(v['rasm'], []).append(k[0])

    # ============ the six سبب generators ============

    def tajawur(self, k):
        """تجاور مصحفي — muṣḥaf adjacency."""
        i = self.pos_ix[k]
        out=[]
        for j in (i-1, i+1):
            if 0 <= j < len(self.order):
                out.append((self.order[j], NASSI, 'adjacent'))
        return out

    def takrar(self, k, use_root=False):
        """تكرار لفظي — same lemma (or root) elsewhere."""
        v = self.words[k]; out=[]
        keys = v['root'] if use_root else v['lem']
        idx  = self.by_root if use_root else self.by_lem
        for key in keys:
            for t in idx[key]:
                if t != k: out.append((t, NASSI, f"{'root' if use_root else 'lem'}:{key}"))
        return out

    def ishtimal(self, k):
        """اشتمال حرفي — letter-set containment between fawātiḥ clusters."""
        v = self.words[k]
        if not v['inl']: return []
        me = set(v['rasm']); out=[]
        for other, suras in self.fawatih.items():
            if other == v['rasm']: continue
            os_ = set(other)
            rel = ('⊂' if me < os_ else '⊃' if me > os_ else None)
            if rel:
                for s in suras:
                    out.append(((s,1,1), NASSI, f"{v['rasm']} {rel} {other}"))
        return out

    def sigha(self, k, n=3):
        """صيغة مشتركة — the same n-word formula occurring elsewhere."""
        i = self.pos_ix[k]; out=[]
        for nn in range(n, 1, -1):
            seq = self.order[i:i+nn]
            if len(seq) < nn or len({(x[0],x[1]) for x in seq}) != 1: continue
            key = ' '.join(self.words[x]['rasm'] for x in seq)
            for hit in self.ngrams.get(key, ()):
                t = hit[:3]
                if t != k: out.append((t, NASSI, f"formula[{nn}]:{key}"))
            if out: break
        return out

    def tamathul(self, k, n=3):
        """تماثل تركيبي — same POS pattern (structural parallelism)."""
        i = self.pos_ix[k]
        seq = self.order[i:i+n]
        if len(seq) < n: return []
        pat = tuple(tuple(self.words[x]['pos']) for x in seq)
        out=[]
        for j in range(len(self.order)-n+1):
            cand = self.order[j:j+n]
            if len({(x[0],x[1]) for x in cand}) != 1: continue
            if tuple(tuple(self.words[x]['pos']) for x in cand) == pat and cand[0]!=k:
                out.append((cand[0], NASSI, 'pos-pattern'))
        return out

    def tajanus(self, k, maxd=1):
        """تجانس صوتي — consonantal-skeleton resonance.  PERCEPTUAL: not settled
        by the text alone, so it is typed إدراكي and must be declared."""
        v = self.words[k]['rasm']; out=[]
        if len(v) < 3: return []
        for t,w in self.words.items():
            if t == k: continue
            u = w['rasm']
            if abs(len(u)-len(v)) > maxd: continue
            if u == v: continue
            # subsequence-containment on the skeleton
            if _lev(u,v) <= maxd:
                out.append((t, IDRAKI, f"rasm~{v}/{u}"))
        return out

def _lev(a,b):
    if a==b: return 0
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1):
            cur.append(min(prev[j]+1, cur[j-1]+1, prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]
