"""测试Playwright采集eBay数据"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel='chrome')
        
        print("[测试] Outdoor Gear Dude 商品数据...")
        page = await browser.new_page()
        await page.goto('https://www.ebay.com/str/outdoor-gear-dude', timeout=20000)
        await page.wait_for_timeout(3000)
        
        data = await page.evaluate('''
            () => {
                // 先看什么选择器有效
                const tests = {
                    's-item': document.querySelectorAll('.s-item').length,
                    'li[data-view]': document.querySelectorAll('li[data-view]').length,
                    'a[href*="/itm/"]': document.querySelectorAll('a[href*="/itm/"]').length,
                    '.gallery-item': document.querySelectorAll('.gallery-item').length,
                    'li[id^="item"]': document.querySelectorAll('li[id^="item"]').length,
                };
                
                // 用有效选择器提取数据
                let items = [];
                document.querySelectorAll('a[href*="/itm/"]').forEach(a => {
                    const text = a.innerText.trim();
                    if (text && text.length > 5) {
                        items.push({title: text.substring(0,80)});
                    }
                });
                
                return {selector_tests: tests, items: items.slice(0,8)};
            }
        ''')
        
        print("  选择器测试:")
        for sel, count in data['selector_tests'].items():
            print(f"    {sel}: {count}")
        print(f"\n  商品标题示例:")
        for i, item in enumerate(data['items'], 1):
            print(f"    {i}. {item['title']}")
        
        # 找更多店铺
        print(f"\n[测试] 更多户外店铺...")
        stores = ["outdoor-gear-dude", "sierratradingpost", "campmor", "outdoor-products"]
        for s in stores:
            try:
                pg = await browser.new_page()
                await pg.goto(f'https://www.ebay.com/str/{s}', timeout=15000)
                await pg.wait_for_timeout(2000)
                title = await pg.title()
                ok = 'Security' not in title and 'Error' not in title
                print(f"  {'✅' if ok else '❌'} {s:25s} | {title[:50]}")
                await pg.close()
            except:
                print(f"  ❌ {s:25s} | 访问失败")
        
        await browser.close()

asyncio.run(main())
