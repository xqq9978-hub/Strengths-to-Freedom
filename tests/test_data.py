import json,sys,copy,tempfile
from pathlib import Path
p=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(p/'scripts'))
from render_report import validate,render
base=json.loads((p/'examples/虚构演示-未知收入.json').read_text());assert validate(base)
def reject(mut):
 d=copy.deepcopy(base);mut(d)
 try:validate(d)
 except ValueError:return
 raise AssertionError('validator accepted invalid data')
reject(lambda d:d['paths'][0]['annual'][1].update(value=200,basis='猜测',evidence_refs=['U1']))
reject(lambda d:d['paths'][0]['annual'][0].update(value=100,basis='假设',evidence_refs=['U1']))
reject(lambda d:d['paths'][0]['plan'][0].update(day=7))
reject(lambda d:d['strengths'][0].update(evidence_refs=['不存在']))
reject(lambda d:d['evidence'][0].update(url='javascript:alert(1)'))
d=copy.deepcopy(base);d['vision']['words'][0]['title']='</script><script>window.PWNED=1</script>';s=render(d);assert '</script><script>window.PWNED=1</script>' not in s
print('数据与转义校验：通过；收入无依据、基线不一致、错误节点及无效引用均被拒绝。')
