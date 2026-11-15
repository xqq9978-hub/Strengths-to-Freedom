"""Brief visible conclusions; full quotes have one canonical location in the appendix."""
from render_boundary import e,plain

def proof(data):
    b=data.get('boundary_analysis',{})
    refs=b.get('personal_evidence_refs',[])
    def links(ids):
        from urllib.parse import quote
        return ' · '.join(f'<a class="evidence-link" href="#ev-{e(quote(i,safe=""))}">查看经历依据</a>' for i in ids)
    gaps=''
    for g in b.get('gap_analysis',[]):
        gaps+=f'<li><b>{e(g.get("capability","待核验能力"))}</b><br>目标要求：{e(g.get("market_requirement","尚未核对"))}<br>验证：{e(g.get("verification_task","待确定"))}<br>{links(g.get("personal_evidence_refs",[]))}</li>'
    index={x['id']:x for x in data['evidence_index']}
    market=[]
    for label,key in [('现职责','current_role_range'),('目标职责','target_role_range')]:
        r=b.get(key,{})
        for ref in r.get('source_refs',[]):
            x=index.get(ref)
            if not x:continue
            market.append(f'<li><b>{label} · {e(x.get("publisher") or "来源")}</b><br>{e(" · ".join(str(x.get(k) or "待核验") for k in ("region","role","access_date","basis")))}<br>可比性：{e(r.get("comparability_note") or "尚未核对")}<br>{links([ref])}</li>')
    note='薪酬资料：已列出实际来源与匹配局限。' if market else '薪酬资料：尚未取得可比岗位样本；当前不据此判断真实收入上限。'
    expanded=''
    if gaps:expanded+=f'<details><summary>展开职责差距与验证</summary><ul class="reference-list">{gaps}</ul></details>'
    if market:expanded+=f'<details><summary>查看薪酬样本与可比性</summary><ul class="reference-list">{"".join(market)}</ul></details>'
    limit=b.get('limitations') or ['实际机会、个人贡献和生活容量变化时需重估。']
    expanded+=f'<details><summary>适用边界与尚缺资料</summary><p class="reader-note">{e(plain(limit))}</p></details>'
    return f'<div class="boundary-proof"><p class="reader-note">{e(note)}</p><div class="report-details">{expanded}</div></div>'
