# المِرْتَال — al-Mirtāl

The instrument of tarteel. A Qur'an navigator built on a formal system of
recitational navigation: رَتْلًا وَتَرْتِيلًا.

## the governing constraint

> ما نَفِدَتْ كَلِمَاتُ اللَّه

Nothing stands between one رتلة and the next but the text itself. Citations,
role labels and weights are **apparatus** — they sit in the margin, never in the
line. No gloss, no commentary, no human speech is ever placed between verses.

This is the method of the pre-textual compilers: raw text stacked against raw
text, distant coordinates stitched into one continuous layer, the text left to
interpret itself through unmediated proximity.

## layout

    corpus.py       Layer 0  segment-addressable muṣḥaf
    sabab.py        Layer 1  six سبب generators, typed نصّي | منقول | إدراكي
    ops.py          Layer 2  operator algebra over citation-sequences
    generate.py     Layers 3-4  Furqān planner + ترتيل planner
    bundle.py       builds the embedded data bundle
    app.html        المِرْتَال — the navigator (4 modes)
    onboard.html    the onboarding architecture proposal
    doc.html        رَتْلًا وَتَرْتِيلًا — the formalism

## build

    python3 bundle.py          # → bundle.json
    python3 build.py           # → mirtal.html, awwal.html
