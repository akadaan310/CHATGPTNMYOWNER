# -*- coding: utf-8 -*-
"""Layers 3-4: the Furqān planner and the ترتيل planner."""
import math, sys
from collections import defaultdict
from corpus import Corpus
from sabab import SababIndex, NASSI, IDRAKI
import ops
from ops import Mode

# ---------------------------------------------------------------------------
# جَاذِبِيَّةُ الجِوَار — the gravity of the neighbourhood
#
# وَزْن (information) and قُرْب (proximity) are DIFFERENT quantities and must be
# scored apart. Adjacency has maximal raw bits — two candidates, 15.2 — precisely
# because it is the least surprising move available. Ranking on bits alone
# therefore teleports: only rare cross-sūrah formulas ever score highly.
#
# So a candidate is scored  دَرَجَة = وَزْن + قُرْب,  where قُرْب rewards staying
# home and taxes crossing. A crossing must be dense enough to pay its own toll.
# ---------------------------------------------------------------------------
ADJACENT   =  7.0    # same sūrah, |Δāyah| ≤ 1
NEAR_BASE  =  6.5    # same sūrah, within the neighbourhood
NEAR_DECAY =  0.35   # per āyah of distance
NEAR_SPAN  =  8      # how far the neighbourhood reaches
SAME_SURAH =  1.0    # same sūrah but beyond the neighbourhood
CROSSING   = -6.0    # العَتَبَة — the toll on leaving the sūrah
TAJAWUR_W  =  2.0    # adjacency tells you almost nothing; cap its وزن
CROSS_BAR  = 14.0    # العَتَبَة العُلْيَا — raw وزن a crossing must clear to be
                     # admitted at all. ~14 bits is a formula occurring in five
                     # places or fewer in the whole muṣḥaf. Below this the link is
                     # simply not specific enough to be worth leaving home for.

class Generator:
    def __init__(self, C, S, min_bits=8.0, min_score=8.0):
        self.C, self.S = C, S
        self.N = len(S.words)
        self.min_bits = min_bits      # floor on raw information
        self.min_score = min_score    # floor on وزن + قرب

    def w(self, n):  return math.log2(self.N/n) if n else 0.0

    def qurb(self, src, dst):
        """قُرْب — proximity score between two coordinates."""
        if src[0] != dst[0]:
            return CROSSING, 'عُبُور'
        d = abs(src[1] - dst[1])
        if d <= 1:          return ADJACENT, 'مُجَاوِر'
        if d <= NEAR_SPAN:  return NEAR_BASE - NEAR_DECAY*d, 'جِوَار'
        return SAME_SURAH, 'سُورَة'

    # ---------- edges out of a span: scored by وزن + قرب ----------
    def edges(self, span, scope='any', exclude=None):
        """scope 'local'  — stay inside the sūrah
           scope 'cross'  — leave it, paying العَتَبَة
           scope 'any'    — both, ranked together"""
        s,a,w0,w1 = span
        cand = {}
        def offer(t, name, ev, bits, typ, informational=True):
            if t[0] == s and t[1] == a: return
            if exclude and (t[0],t[1]) in exclude: return
            cross = t[0] != s
            if scope == 'local' and cross: return
            if scope == 'cross' and not cross: return
            q, tier = self.qurb((s,a), t)
            score = bits + q
            if informational and bits < self.min_bits: return
            if score < self.min_score: return
            key = (t[0], t[1])
            if key not in cand or score > cand[key][5]:
                cand[key] = (t, name, ev, bits, typ, score, tier)

        for w in range(w0, w1+1):
            k = (s,a,w)
            if k not in self.S.words: continue
            # الجِوَار first — the verse before and the verse after are always candidates
            for t,typ,ev,cnt in self.S.tajawur(k):
                offer((t[0],t[1],t[2]), 'تجاور مصحفي', 'الآية المجاورة',
                      TAJAWUR_W, typ, informational=False)
            for name, hits in [('اشتمال حرفي', self.S.ishtimal(k)),
                               ('صيغة مشتركة', self.S.sigha(k,4)),
                               ('تكرار لفظي (جذر)', self.S.takrar(k,True)),
                               ('تكرار لفظي (لفظ)', self.S.takrar(k,False))]:
                for t,typ,ev,cnt in hits:
                    offer(t, name, ev, self.w(cnt), typ)

        # every same-sūrah āyah within the neighbourhood is reachable by جوار alone
        if scope in ('any','local'):
            for d in range(2, NEAR_SPAN+1):
                for aa in (a-d, a+d):
                    if (s,aa) in self.C.aya_words:
                        offer((s,aa,1), 'جِوَار', f'±{d} آية', TAJAWUR_W+1.0, NASSI,
                              informational=False)
        return sorted(cand.values(), key=lambda x:-x[5])

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
    def furqan(self, anchor, established, mode=Mode.ISNAD, max_reach=2,
               allow_cross=True, exclude=None):
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

        # 3) توسّع — the neighbourhood is mapped first; a crossing is only
        #    offered once the local field above threshold is spent.
        # Before the walk has earned it, the sūrah is the whole world. After that,
        # a crossing competes on score — it does not queue behind the locals. It
        # simply has to be dense enough to outrank a somewhat weak جِوَار after
        # paying العَتَبَة, which takes roughly 14 raw bits.
        picks = self.edges(anchor, scope='local', exclude=exclude)[:max_reach]
        if allow_cross:
            # A qualifying crossing is never crowded out by the neighbourhood —
            # it takes a reserved slot, so an undeniable link is always an event.
            cross = [e for e in self.edges(anchor, scope='cross', exclude=exclude)
                     if e[3] >= CROSS_BAR]
            if cross:
                picks = picks[:max_reach-1] + [cross[0]]
        for t, name, ev, bits, typ, score, tier in picks:
            ts, ta, tw = t
            tws = self.C.aya_words[(ts,ta)]
            far = (ts, ta, tws[0], tws[min(len(tws),6)-1])
            R.append(('توسّع', ops.hamal(anchor, far)))
            edges_used.append((name, ev, bits, typ, round(score,1), tier))
            reached.append((ts,ta))

        # 4) رجوع — reverse the last reach back onto the anchor: closes the cycle
        if reached:
            R.append(('رجوع', ops.aks(R[-1][1])))          # عكس: far → anchor, closes the cycle
            far = R[-1][1][0]
            head = (far[0], far[1], far[2], far[2])        # far reduced to its opening word
            if head != anchor:
                R.append(('ضغط', [head, anchor]))          # the whole Furqān as one node-pair
        return dict(anchor=anchor, retlat=R, edges=edges_used, reached=reached,
                    bits=sum(e[2] for e in edges_used),
                    score=sum(e[4] for e in edges_used))

    # ---------- the ترتيل planner: progressive expansion of E ----------
    def tarteel(self, seed_spans, n, local_first=2, cooldown=3):
        """local_first — how many فرقانًا must stay home before crossing opens.
        cooldown   — after a crossing, how many فرقانًا must re-ground locally
                     before another is permitted.

        The bar on وزن decides whether a crossing is ADMISSIBLE; the cooldown
        decides whether it is TIMELY. Without the second, a leap stops being an
        event: 14-bit formulas are common enough that one fires every فرقان."""
        E = list(seed_spans)          # established coordinates
        seen_anchor, spent, out = set(), set(), []
        for sp in seed_spans: spent.add((sp[0],sp[1]))
        last_cross = -99
        for k in range(n):
            allow_cross = (k >= local_first) and (k - last_cross >= cooldown)
            best = None
            for sp in E:
                if (sp[0],sp[1]) in seen_anchor: continue
                # already-reached coordinates are consumed: the neighbourhood
                # genuinely depletes, and a crossing becomes the move that is left
                b = sum(e[5] for e in self.edges(
                        sp, scope='local', exclude=spent)[:2])
                if allow_cross:
                    # an anchor carrying an undeniable crossing becomes attractive
                    top = [e for e in self.edges(sp, scope='cross', exclude=spent)
                           if e[3] >= CROSS_BAR]
                    if top: b += top[0][3]
                # أصل التقديم: later Furqāns prefer anchors established by earlier ones
                if k > 0 and sp in seed_spans: b *= 0.6
                if best is None or b > best[0]: best = (b, sp)
            if best is None or best[0] == 0:
                if not allow_cross: continue      # nothing local left; try crossing
                break
            anchor = best[1]; seen_anchor.add((anchor[0],anchor[1]))
            F = self.furqan(anchor, E, allow_cross=allow_cross, exclude=spent)
            if not F['edges']: continue
            out.append(F)
            if any(e[5]=='عُبُور' for e in F['edges']): last_cross = k
            for (ts,ta) in F['reached']:                 # E grows, and is consumed
                spent.add((ts,ta))
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
