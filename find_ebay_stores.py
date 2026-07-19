"""批量测eBay店铺，找能访问的户外店"""
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

# 一批户外小卖家（防护一般比大店弱）
STORES = [
    "outdoor-gear-dude",         # ✅ 已验证
    "geartrade",                 # 之前标题为空
    "trailspace",                # 新
    "camp-saver",                # 新
    "optoutside",                # 新
    "adventure-gear",            # 新
    "wilderness-trails",         # 新
    "mountain-man-outdoor",      # 新
    "trail-creek-outfitters",    # 新
    "northwest-outdoor",         # 新
    "summit-crest-outdoors",     # 新
    "rocky-mountain-outdoor",    # 新
]

async def main():
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel='chrome')
        
        for store in STORES:
            page = await browser.new_page()
            try:
                await page.goto('https://www.google.com', timeout=10000)
                await asyncio.sleep(2)
                
                await page.goto(f'https://www.ebay.com/str/{store}', timeout=20000)
                await asyncio.sleep(3)
                
                title = await page.title()
                if 'Security' not in title and 'Error' not in title:
                    # 数商品
                    items = await page.evaluate('() => document.querySelectorAll("a[href*=\'/itm/\']").length')
                    print(f'✅ {store:30s} | {title[:40]:40s} | 商品: {items}')
                    if items > 0:
                        results.append({"store": store, "title": title, "count": items})
                else:
                    print(f'❌ {store:30s} | {title[:40]}')
            except Exception as e:
                print(f'❌ {store:30s} | {type(e).__name__}')
            finally:
                await page.close()
            
            await asyncio.sleep(3)  # 间隔
        
        await browser.close()
    
    print(f"\n✅ 可用的户外店铺: {len(results)} 家")
    for r in results:
        print(f"   {r['store']}: {r['count']}个商品")

asyncio.run(main())
