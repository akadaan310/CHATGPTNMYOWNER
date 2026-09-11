# -*- coding: utf-8 -*-
"""Inject data bundles into their templates."""
import os
def inject(tpl, data, out, token):
    t=open(tpl,encoding='utf-8').read()
    d=open(data,encoding='utf-8').read().replace('</script>','<\\/script>')
    open(out,'w',encoding='utf-8').write(t.replace(token,d))
    print(f'  {out}  {os.path.getsize(out)/1e6:.2f} MB')
print('build:')
inject('app.html','bundle.json','mirtal.html','__BUNDLE__')
inject('awwal.html','awwal.json','rukub.html','__DATA__')
inject('majra.html','majra.json','navigator.html','__DATA__')

def chunks(data, out_dir, parts=1):
    """majra.json → gzip → base64 → d0.txt … dN.txt, what vercel/index.html fetches."""
    import gzip, base64
    b = base64.b64encode(gzip.compress(open(data, 'rb').read(), 9, mtime=0)).decode('ascii')
    n = -(-len(b) // parts)
    for i in range(parts):
        p = os.path.join(out_dir, f'd{i}.txt')
        open(p, 'w').write(b[i * n:(i + 1) * n])
        print(f'  {p}  {os.path.getsize(p)/1e6:.2f} MB')

chunks('majra.json', 'vercel')
