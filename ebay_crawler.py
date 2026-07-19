"""eBay采集模块：供main.py调用"""
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

def crawl_ebay() -> list[dict]:
    """同步入口：采eBay店铺，返回商品列表"""
    return asyncio.run(_crawl_all())

async def _crawl_all():
    store = "outdoor-gear-dude"
    print(f"\n  🤖 eBay采集: {store}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel='chrome')
        page = await browser.new_page()
        
        try:
            await page.goto('https://www.google.com', timeout=15000)
            await asyncio.sleep(2)
            
            await page.goto(f'https://www.ebay.com/str/{store}', timeout=30000)
            await asyncio.sleep(4)
            
            title = await page.title()
            if 'Security' in title:
                print(f"  ❌ eBay被拦截")
                return []
            
            data = await page.evaluate('''
                () => {
                    const items = [];
                    const seen = new Set();
                    document.querySelectorAll('a[href*="/itm/"]').forEach(a => {
                        const text = (a.innerText || '').trim();
                        if (text.length < 5 || seen.has(text)) return;
                        seen.add(text);
                        let price = '';
                        let parent = a.closest('div,li,td,section');
                        if (parent) {
                            let el = parent.querySelector('[class*="price"], [class*="Price"], .s-item__price');
                            if (el) price = el.innerText.trim();
                        }
                        items.push({title: text.substring(0,100), price: price});
                    });
                    return items;
                }
            ''')
            
            if data:
                print(f"  ✅ eBay: {len(data)} 个商品")
                return [{
                    "title": d["title"], "price": d["price"].replace("$","").strip(),
                    "category": "户外装备", "status": "在售",
                    "store": "eBay-outdoor-gear-dude", "rating": "", "handle": "",
                } for d in data]
            return []
        except Exception as e:
            print(f"  ❌ eBay采集失败: {type(e).__name__}")
            return []
        finally:
            await browser.close()
