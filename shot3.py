from playwright.sync_api import sync_playwright
import pathlib
u='file://'+str(pathlib.Path('rukub.html').resolve())
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    pg=b.new_page(viewport={'width':430,'height':932}, device_scale_factor=2)
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(u); pg.wait_for_timeout(1800)
    pg.screenshot(path='o1.png')                      # سُكُون
    pg.locator('#sukun').click(); pg.wait_for_timeout(9000)
    pg.screenshot(path='o2.png')                      # انجراء mid-course
    # jump to wijha
    pg.wait_for_timeout(14000)
    pg.screenshot(path='o3.png')
    print('stage:', pg.locator('#stage-name').inner_text())
    print('panels:', pg.locator('.panel').count(), 'nodes:', pg.locator('.node').count())
    print('js errors:', errs[:3])
    b.close()
