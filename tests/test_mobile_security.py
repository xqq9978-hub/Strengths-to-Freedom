import json,sys,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
p=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(p/'scripts'));from render_report import render
base=json.loads((p/'examples/虚构演示-未知收入.json').read_text());base['vision']['words'][0]['title']='</script><script>window.PWNED=1</script>';base['strengths']=[]
with tempfile.NamedTemporaryFile(mode='w',suffix='.html',encoding='utf8',delete=False) as f:f.write(render(base));name=f.name
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/local/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':390,'height':844},reduced_motion='reduce');errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(Path(name).as_uri());page.wait_for_timeout(300)
 assert page.evaluate('window.PWNED') is None;assert '<script>' in page.locator('#visionTitle').inner_text()
 page.locator('[data-dot="2"]').click(force=True);page.wait_for_timeout(500);page.locator('[data-profile-view="strength"]').click();assert '待发现' in page.locator('#dimTitle').inner_text()
 page.locator('[data-dot="3"]').click(force=True);page.wait_for_timeout(500);fr=page.frame_locator('#incomeFrame');assert fr.locator('[data-view="curve"]').is_disabled();assert '金额待定' in fr.locator('#final-number').inner_text();assert fr.locator('#final-unit').inner_text()=='万元/年'
 page.locator('[data-dot="4"]').click(force=True);page.wait_for_timeout(500);page.screenshot(path=str(p/'tests/mobile-preview.png'));assert not errors,errors;print('移动端、未知值、零优势与脚本注入测试：通过');b.close()
Path(name).unlink()
