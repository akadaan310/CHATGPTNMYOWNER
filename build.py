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

def stage(src, out):
    """navigator.html → the deployment root. `<meta charset>` is prepended because
    the template omits it, and a static host would decode the Arabic as Latin-1."""
    h=open(src,encoding='utf-8').read()
    open(out,'w',encoding='utf-8').write('<meta charset="utf-8">\n'+h)
    print(f'  {out}  {os.path.getsize(out)/1e6:.2f} MB')

stage('navigator.html','vercel/index.html')
