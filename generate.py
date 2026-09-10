# -*- coding: utf-8 -*-
"""Layers 3-4: the Furqān planner and the ترتيل planner."""
import math, sys
from collections import defaultdict
from corpus import Corpus
from sabab import SababIndex, NASSI, IDRAKI
import ops
from ops import Mode

class Generator:
    def __init__(self, C, S, min_bits=8.0):
        self.C, self.S = C, S
        self.N = len(S.words)
        self.min_bits = min_bits

    def w(self, n):  return math.log2(self.N/n) if n else 0.0

    # ---------- edges out of a span, typed + weighted ----------
    def edges(self, span, exclude_sura=None):
        s,a,w0,w1 = span
        cand = {}
        for w in range(w0, w1+1):
            k = (s,a,w)
            if k not in self.S.words: continue
            groups = [('اشتمال حرفي', self.S.ishtimal(k)),
                      ('صيغة مشتركة', self.S.sigha(k,3)),
                      ('تكرار لفظي (جذر)', self.S.takrar(k,True)),
                      ('تكرار لفظي (لفظ)', self.S.takrar(k,False))]
            for name, hits in groups:
                for t,typ,ev,cnt in hits:
                    bits = self.w(cnt)               # weight of THIS candidate's own set
                    if bits < self.min_bits: continue
                    if t[0] == s and t[1] == a: continue
                    if exclude_sura and t[0] in exclude_sura: continue
                    key = (t[0], t[1])
                    if key not in cand or bits > cand[key][3]:
                        cand[key] = (t, name, ev, bits, typ)
        return sorted(cand.values(), key=lambda x:-x[3])

    # ---------- render ----------
    def txt(self, sp):
        s,a,w0,w1 = sp
        return self.C.span_text(s,a,w0,w1)
    def cite(self, sp):
        s,a,w0,w1 = sp
        return f"{s}:{a}:{w0}" + (f"-{w1}" if w1>w0 else "")
    def render(self, retlah):
        return (' '.join(self.txt(sp) for sp in retlah),
                '⟨' + ', '.join(self.cite(sp) for sp in retlah) + '⟩')

    # ---------- the Furqān schema, closed by return to anchor ----------
    def furqan(self, anchor, established, mode=Mode.ISNAD, max_reach=2):
        s,a,w0,w1 = anchor
        R, edges_used, reached = [], [], []

        # 1) ابتداء — present the anchor
        R.append(('ابتداء', [anchor]))

        # 2) تفريق — the anchor carried into its own continuation, progressively
        nxt = (s, a+1)
        if nxt in self.C.aya_words:
            ws = self.C.aya_words[nxt]
            for cut in (1, min(3, len(ws))):
                if cut <= len(ws):
                    R.append(('تفريق', ops.hamal(anchor, (s, a+1, ws[0], ws[cut-1]))))

        # 3) توسّع — follow the heaviest grounded edges outward
        for t, name, ev, bits, typ in self.edges(anchor, exclude_sura={s})[:max_reach]:
            ts, ta, tw = t
            tws = self.C.aya_words[(ts,ta)]
            far = (ts, ta, tws[0], tws[min(len(tws),6)-1])
            R.append(('توسّع', ops.hamal(anchor, far)))
            edges_used.append((name, ev, bits, typ)); reached.append((ts,ta))

        # 4) رجوع — reverse the last reach back onto the anchor: closes the cycle
        if reached:
            R.append(('رجوع', ops.aks(R[-1][1])))          # عكس: far → anchor, closes the cycle
            far = R[-1][1][0]
            head = (far[0], far[1], far[2], far[2])        # far reduced to its opening word
            if head != anchor:
                R.append(('ضغط', [head, anchor]))          # the whole Furqān as one node-pair
        return dict(anchor=anchor, retlat=R, edges=edges_used, reached=reached,
                    bits=sum(e[2] for e in edges_used))

    # ---------- the ترتيل planner: progressive expansion of E ----------
    def tarteel(self, seed_spans, n):
        E = list(seed_spans)          # established coordinates
        seen_anchor, out = set(), []
        for k in range(n):
            best = None
            for sp in E:
                if sp in seen_anchor: continue
                b = sum(e[3] for e in self.edges(sp)[:2])
                # أصل التقديم: later Furqāns prefer anchors established by earlier ones
                if k > 0 and sp in seed_spans: b *= 0.6
                if best is None or b > best[0]: best = (b, sp)
            if best is None or best[0] == 0: break
            if not self.edges(best[1]): seen_anchor.add(best[1]); continue
            anchor = best[1]; seen_anchor.add(anchor)
            F = self.furqan(anchor, E)
            out.append(F)
            for (ts,ta) in F['reached']:                 # E grows
                tws = self.C.aya_words[(ts,ta)]
                E.append((ts,ta,tws[0],tws[min(len(tws),3)-1]))
        return out

def show(g, tarteel, title):
    print('═'*66); print(f'  تَرْتِيل — {title}'); print('═'*66)
    tot=0
    for i,F in enumerate(tarteel,1):
        print(f"\n── فُرْقَان {i} ── مَحْمِل: {g.txt(F['anchor'])}  [{g.cite(F['anchor'])}]")
        if F['edges']:
            for name,ev,bits,typ in F['edges']:
                print(f"   سبب: {name} · {ev[:44]} · {bits:.1f} bits · {typ}")
        tot += F['bits']
        for role, r in F['retlat']:
            t,c = g.render(r)
            print(f"   {role:<7} {t}")
            print(f"   {'':<7} {c}")
    print(f"\n  وزن التَّرْتِيل الكُلِّي: {tot:.1f} bits عبر {len(tarteel)} فرقانًا")

if __name__ == '__main__':
    C = Corpus('/tmp/claude-0/-home-claude/092f1e73-6422-5ef9-9c35-46685f42aa9b/scratchpad/quran-morphology.txt')
    S = SababIndex(C); g = Generator(C,S)
    seed = [(30,1,1,1)] + [(30,a,1,3) for a in (2,3,4)]
    show(g, g.tarteel(seed, 3), 'سُورَة الرُّوم  (n=3)')
