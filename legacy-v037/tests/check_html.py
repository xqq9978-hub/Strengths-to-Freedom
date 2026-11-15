"""Generate six reports and inspect both scripts and escaped data without a browser."""
from pathlib import Path
from html.parser import HTMLParser
import copy,json,re,subprocess,sys,tempfile

ROOT=Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from render_report import render

class Scan(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.inner=''
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='iframe':self.inner=a['srcdoc']

with tempfile.TemporaryDirectory() as tmp:
    for name in ['sales','student','developer','freelancer','support','explicit-zero']:
        data=json.loads((ROOT/'tests'/f'{name}.json').read_text())
        doc=render(data,Path(tmp)/name).read_text()
        s=Scan();s.feed(doc)
        assert len(s.ids)==len(set(s.ids))
        assert s.ids.index('future')<s.ids.index('incomeBoundary')<s.ids.index('profile')<s.ids.index('valueMap')<s.ids.index('journey')
        assert all(x in s.ids for x in ['incomeFrame','stageButtons','stageText','strengthDetails'])
        assert not re.search(r'__[A-Z_]+__',doc)
        for label,content in [('outer',doc),('inner',s.inner)]:
            scripts='\n'.join(b for a,b in re.findall(r'<script([^>]*)>(.*?)</script>',content,re.S) if 'application/json' not in a)
            js=Path(tmp)/f'{name}-{label}.js';js.write_text(scripts)
            subprocess.run(['node','--check',str(js)],check=True,capture_output=True)
        assert '先探索三条路径如何发挥你的优势' not in doc
        print('PASS standalone HTML and both script syntaxes: '+name)
    data=json.loads((ROOT/'tests/sales.json').read_text())
    data['user_profile']['stage']['value']='</script><script>alert("escape")</script>'
    doc=render(data,Path(tmp)/'escaped').read_text()
    assert '</script><script>alert("escape")</script>' not in doc
    assert '\\u003c/script\\u003e' in doc
    data['income_scenarios'][0]['name']='<img src=x onerror=alert(1)>'
    scan=Scan();scan.feed(render(data,Path(tmp)/'escaped-path').read_text())
    assert '<img src=x onerror=alert(1)>' not in scan.inner
    print('PASS embedded JSON and route-name escaping')
