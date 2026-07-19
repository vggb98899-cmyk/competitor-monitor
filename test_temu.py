"""测试Playwright访问Temu"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel='chrome')
        page = await browser.new_page()
        
        print("访问Temu搜索...")
        await page.goto('https://www.temu.com/search?q=camping', timeout=30000)
        await page.wait_for_timeout(5000)
        
        title = await page.title()
        print(f"标题: {title}")
        
        # 找商品
        data = await page.evaluate('''
            () => {
                const items = [];
                document.querySelectorAll('a[href*="/goods/"]').forEach(a => {
                    const text = (a.innerText || '').trim();
                    if (text && text.length > 3) items.push(text.substring(0, 60));
                });
                return {
                    links_count: document.querySelectorAll('a[href*="/goods/"]').length,
                    samples: items.slice(0, 5),
                    body_size: document.body.innerText.length
                };
            }
        ''')
        print(f"商品链接数: {data['links_count']}")
        print(f"页面文字量: {data['body_size']}字符")
        if data['samples']:
            print(f"示例: {data['samples']}")
        else:
            print("没有找到商品")
        
        await browser.close()

asyncio.run(main())
