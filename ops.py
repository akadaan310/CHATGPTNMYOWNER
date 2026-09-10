# -*- coding: utf-8 -*-
"""Layer 2: the operator algebra.  All operations act on citation-sequences.
A Span is (sura, aya, w0, w1); a Retlah is an ordered list of Spans."""

NASSI, IDRAKI = 'نصّي', 'إدراكي'

class Mode:                      # مقام
    ISNAD   = 'إسناد'            # citational  — إسقاط forbidden
    TAWJIH  = 'توجيه'            # orienting   — إسقاط permitted

# ---------- أفعال (acts) ----------
def hamal(a, b):      return [a, b]                      # الحَمْل   carry across a stop
def wasl(r1, r2):     return list(r1) + list(r2)         # الوَصْل   stitch
def aks(r):           return list(reversed(r))           # العَكْس   reverse attachment
def daght(rs):        return [rs[0][0], rs[-1][-1]]      # الضَّغْط  compress a path
def ihata(r, sp):     return [sp] + list(r) + [sp]       # الإحَاطَة enclose by repetition

def fasl(sp, at):                                        # الفَصْل   split a span
    s,a,w0,w1 = sp
    assert w0 <= at < w1, 'split point must lie inside the span'
    return [(s,a,w0,at), (s,a,at+1,w1)]

def isqat(sp, drop_w, mode):                             # الإسْقَاط scoped omission
    """Admissible only in مقام التوجيه — the constraint adopted for Furqān 3."""
    if mode != Mode.TAWJIH:
        raise ValueError('الإسقاط ممنوع في مقام الإسناد')
    s,a,w0,w1 = sp
    return [(s,a,w,w) for w in range(w0,w1+1) if w != drop_w]

def jam(cluster_a, cluster_b, fawatih):                  # الجَمْع  union of fawātiḥ
    """Admissible ONLY if the union is itself attested as a cluster in the muṣḥaf.
    الجَمْعُ لا يَجوزُ إلا إذا كان المَجموعُ مُثبَتًا في النَّصّ."""
    u = set(cluster_a) | set(cluster_b)
    for r, suras in fawatih.items():
        if set(r) == u:
            return r, suras
    return None, []
