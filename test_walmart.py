"""测试Playwright访问Walmart"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel='chrome')
        page = await browser.new_page()
        
        print("访问Walmart...")
        await page.goto('https://www.walmart.com/search?q=camping+tent', timeout=30000)
        await page.wait_for_timeout(5000)
        
        title = await page.title()
        print(f"标题: {title}")
        
        # 找商品
        items = await page.evaluate('''
            () => {
                // 找商品标题和价格
                const titles = [];
                document.querySelectorAll('[data-automation-id="product-title"], .w_iUH7, .w_DQUh').forEach(el => {
                    const t = (el.innerText || '').trim();
                    if (t && t.length > 3) titles.push(t.substring(0, 60));
                });
                
                // 找所有可能的商品容器
                const containers = {
                    'product-title': document.querySelectorAll('[data-automation-id="product-title"]').length,
                    'w_iUH7': document.querySelectorAll('.w_iUH7').length,
                    'price': document.querySelectorAll('[data-automation-id="product-price"]').length,
                    'a[href*="/ip/"]': document.querySelectorAll('a[href*="/ip/"]').length,
                };
                
                return {containers, titles: titles.slice(0, 5)};
            }
        ''')
        
        print(f"选择器匹配:")
        for sel, count in items['containers'].items():
            print(f"  {sel}: {count}")
        print(f"标题示例: {items['titles']}")
        
        await browser.close()

asyncio.run(main())
