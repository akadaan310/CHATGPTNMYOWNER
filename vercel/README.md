# vercel/ — static target

    index.html   the navigator, loading its corpus at boot
    d0.txt …     gzipped JSON, base64, split into PARTS chunks

Build with `python3 build.py` from the repo root, or regenerate a reduced
preview by filtering `majra.json` to a subset of sūrahs (see the `demo` key,
which the sūrah index honours).

## deploying

`vercel.json` at the repo root sets `outputDirectory` to this folder, so the
deployment root serves `index.html` and `d0.txt` sits beside it where the boot
loader fetches it. Without it Vercel serves the repo root, which has no
`index.html`, and the deployment URL answers 404.

Use the git path. Push this repo and point Vercel at it — the corpus is
several megabytes and must not be hand-carried through an inline file API;
a single mistyped base64 character fails the gzip CRC and the page will not
boot. Committed here so the built artefact is reproducible from source.

## charset

`<meta charset="utf-8">` is required. Without it a static host decodes the
inline 'ن' literal as Latin-1: every verse still renders, because the fetched
JSON decodes as UTF-8 by spec, but the lock silently refuses its own key.
