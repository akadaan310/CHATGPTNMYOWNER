# vercel/ — static target

    index.html   the navigator, corpus inlined

Build with `python3 build.py` from the repo root. `stage()` copies the freshly
injected `navigator.html` here and prepends `<meta charset="utf-8">`.

## deploying

`vercel.json` at the repo root sets `outputDirectory` to this folder, so the
deployment root serves `index.html`. Without it Vercel serves the repo root,
which has no `index.html`, and the deployment URL answers 404.

This wiring post-dates the navigator it serves: the tree was reverted to
119df218, which predates any Vercel setup, and only these two files were kept
back so the deployment still resolves. Nothing else here is newer.

## charset

`<meta charset="utf-8">` is required and is **not** in `navigator.html` at this
revision, so `stage()` adds it. Without it a static host decodes the inline
Arabic as Latin-1.

## no chunking

The navigator at this revision inlines its corpus — one 8 MB `index.html`, no
`d0.txt` fetch at boot. The gzip/base64 chunking belonged to a later commit
that the revert removed; do not reintroduce it without also restoring the
boot-time loader that consumes it.
