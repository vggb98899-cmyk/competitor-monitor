"""从outdoor-gear-dude页面找更多弱防护店铺 + 批量测试"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel='chrome')
        page = await browser.new_page()
        
        # 先访问google
        await page.goto('https://www.google.com', timeout=15000)
        await asyncio.sleep(2)
        
        # 访问outdoor-gear-dude
        await page.goto('https://www.ebay.com/str/outdoor-gear-dude', timeout=30000)
        await asyncio.sleep(4)
        
        # 找页面上的其他卖家链接
        stores_found = await page.evaluate('''
            () => {
                const stores = new Set();
                // 找所有链接里包含 "ebay.com/str/" 的
                document.querySelectorAll('a[href*="/str/"]').forEach(a => {
                    const href = a.getAttribute('href') || '';
                    const match = href.match(/\\/str\\/([^\\/?#]+)/);
                    if (match && match[1] !== 'outdoor-gear-dude') {
                        stores.add(match[1]);
                    }
                });
                return Array.from(stores);
            }
        ''')
        
        print(f"在outdoor-gear-dude页面找到其他店铺: {stores_found}")
        
        # 再试一些真正的小卖家（个人卖家名风格）
        small_sellers = [
            "wilderness-outdoor",
            "trailside-adventures", 
            "outdoor-enthusiast-store",
            "camping-gear-outlet",
            "hike-and-paddle",
            "bushcraft-supply",
            "adventure-essentials",
            "trail-ready-gear",
            "peak-outdoor-supply",
            "nature-bound-gear",
        ]
        
        all_to_test = list(stores_found) + small_sellers
        print(f"\n共 {len(all_to_test)} 家待测试\n")
        
        results = []
        for s in all_to_test:
            try:
                pg = await browser.new_page()
                await pg.goto('https://www.google.com', timeout=10000)
                await asyncio.sleep(1)
                await pg.goto(f'https://www.ebay.com/str/{s}', timeout=15000)
                await asyncio.sleep(3)
                
                title = await pg.title()
                if 'Security' not in title and 'Error' not in title:
                    items = await pg.evaluate('() => document.querySelectorAll("a[href*=\'/itm/\']").length')
                    print(f'✅ {s:35s} | 商品: {items}')
                    if items > 0:
                        results.append((s, items))
                else:
                    print(f'❌ {s:35s} | {title[:40]}')
                await pg.close()
            except:
                print(f'❌ {s:35s} | 访问失败')
            await asyncio.sleep(3)
        
        await browser.close()
        
        print(f"\n✅ 可用的:")
        for s, c in results:
            print(f"   {s}: {c}个商品")

asyncio.run(main())
