from playwright.sync_api import sync_playwright
from pathlib import Path
p=Path(__file__).resolve().parent.parent
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/local/bin/chromium',headless=True,args=['--no-sandbox'])
 for name in ['虚构演示-未知收入','虚构测试-完整数字']:
  page=browser.new_page(viewport={'width':1440,'height':900},reduced_motion='reduce'); errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto((p/'examples'/f'{name}.html').as_uri());page.wait_for_timeout(800)
  assert page.locator('#visionTitle').inner_text()=='时间自主'
  page.locator('#cloud .word').nth(1).click();page.locator('#setPriority').click();assert '持续学习' in page.locator('#priorityStatus').inner_text()
  page.locator('[data-go="1"]').click();page.wait_for_timeout(500);assert '持续学习' in page.locator('#startGoalText').text_content()
  page.locator('[data-start-node="1"]').click();assert '3小时' in page.locator('#drawerContent').inner_text();page.locator('#drawerClose').click()
  page.locator('[data-go="2"]').click();page.wait_for_timeout(500);page.locator('[data-profile-view="strength"]').click();assert '信息转译线索' in page.locator('#dimTitle').inner_text();page.locator('[data-frag-index]').nth(1).click();assert '复杂信息' in page.locator('#drawerContent').inner_text();page.locator('#drawerClose').click()
  page.locator('[data-go="3"]').click();page.wait_for_timeout(500);page.locator('#curvePathButtons [data-route="C"]').click();assert 'AI学习资料实验' in page.locator('#pathName').inner_text()
  f=page.frame_locator('#incomeFrame');page.wait_for_timeout(300);print(name,'iframe text',f.locator('body').inner_text()[:350].replace('\n',' | '))
  f.locator('[data-line=\"B\"]').dispatch_event('click');page.wait_for_timeout(300);assert '相邻教育岗位' in page.locator('#pathName').inner_text();page.locator('#curvePathButtons [data-route=\"C\"]').click();page.locator('#goJourney').click();page.wait_for_timeout(500);assert 'AI学习资料实验' in page.locator('#stageRoute').inner_text();page.locator('#checkpoints button').nth(1).click();assert '潜在读者' in page.locator('#stageTitle').inner_text();page.locator('[data-decision="调整"]').click();assert '暂记' in page.locator('#decisionNote').inner_text();page.locator('#planDetails').click();assert '第一步' in page.locator('#drawerContent').inner_text();page.locator('#drawerClose').click()
  page.screenshot(path=f'/data/v040/{name}-screen5.png');assert not errors,errors
  alltext=page.locator('body').inner_text()+' '+f.locator('body').inner_text();assert not any(x in alltext for x in ['葡萄牙','投影客户','15万','现岗分销商经营深化']), alltext
  print(name,'PASS')
  page.close()
 browser.close()
