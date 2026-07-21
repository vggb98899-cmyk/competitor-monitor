"""eBay采集+加载：自动爬取outdoor-gear-dude并返回数据"""
import asyncio, json
from datetime import date
from pathlib import Path
from utils import logger

EBAY_STORE = "outdoor-gear-dude"
CACHE_FILE = Path(__file__).parent / "output" / "ebay_products.json"


async def crawl_ebay():
    """用Playwright采outdoor-gear-dude"""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel='chrome')
        page = await browser.new_page()
        
        await page.goto('https://www.google.com', timeout=15000, wait_until='domcontentloaded')
        await asyncio.sleep(2)
        
        await page.goto(f'https://www.ebay.com/str/{EBAY_STORE}', timeout=30000)
        await asyncio.sleep(5)
        
        title = await page.title()
        if 'Security' in title:
            logger.warning("eBay安全验证拦截，使用上次缓存")
            await browser.close()
            return None
        
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
                    items.push({title: text.substring(0, 100), price: price});
                });
                return items;
            }
        ''')
        await browser.close()
        
        if data:
            result = {"store": f"eBay-{EBAY_STORE}", "products": data, "count": len(data)}
            # 缓存到文件
            CACHE_FILE.parent.mkdir(exist_ok=True)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump([result], f, ensure_ascii=False, indent=2)
            return result
        return None


def load_ebay_data():
    """加载eBay数据（先尝试爬取，失败则用缓存）"""
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        result = asyncio.run(crawl_ebay())
        if result:
            logger.info(f"  📦 eBay实时采集: {result['count']} 个商品")
            return result['products']
    except Exception as e:
        logger.warning(f"eBay采集失败: {e}")
    
    # 降级：用缓存
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            stores = json.load(f)
        for s in stores:
            if s.get("store") == f"eBay-{EBAY_STORE}":
                logger.info(f"  📦 eBay使用缓存: {len(s['products'])} 个商品")
                return s['products']
    
    logger.warning("eBay无数据")
    return []
