"""Playwright访问Google Shopping"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel='chrome')
        page = await browser.new_page()
        
        print("访问Google Shopping...")
        await page.goto(
            'https://www.google.com/search?q=yoga+mat+camping+outdoor&tbm=shop',
            timeout=30000
        )
        await page.wait_for_timeout(3000)
        
        title = await page.title()
        print(f"标题: {title}")
        
        # 提取商品
        data = await page.evaluate('''
            () => {
                const items = [];
                const cards = document.querySelectorAll('.sh-dlr__list-result, [data-docid]');
                cards.forEach(card => {
                    const title = card.querySelector('.sh-dlr__title, .tAxDx');
                    const price = card.querySelector('.kHxwFf, .a8Pemb, [aria-label*="$"]');
                    const store = card.querySelector('.sh-dlr__store, .aULzUe, .HRLxBb');
                    if (title) {
                        items.push({
                            title: (title.innerText || '').trim().substring(0, 60),
                            price: price ? (price.innerText || '').trim() : '',
                            store: store ? (store.innerText || '').trim() : '',
                            source: 'Google Shopping'
                        });
                    }
                });
                return items;
            }
        ''')
        
        print(f"商品数: {len(data)}")
        for d in data[:5]:
            print(f"  {d['title'][:50]} | {d['price'][:20]} | {d['store'][:20]}")
        
        if not data:
            # 备用：直接打印页面文字
            text = await page.evaluate('() => document.body.innerText.substring(0, 1000)')
            print(f"\n页面文字:\n{text[:500]}")
        
        await browser.close()

asyncio.run(main())
