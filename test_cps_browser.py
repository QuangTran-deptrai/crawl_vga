import asyncio
from playwright.async_api import async_playwright
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def crawl_cellphones_laptop():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        await page.goto("https://cellphones.com.vn/laptop.html", wait_until="domcontentloaded")
        
        # CellphoneS uses class .product-info
        await page.wait_for_selector(".product-info", timeout=15000)
        
        products = await page.evaluate("""() => {
            let items = document.querySelectorAll('.product-info');
            let results = [];
            items.forEach(item => {
                let nameEl = item.querySelector('.product__name h3');
                let priceEl = item.querySelector('.product__price--show');
                let oldPriceEl = item.querySelector('.product__price--through');
                
                if (nameEl) {
                    results.push({
                        name: nameEl.innerText.trim(),
                        price: priceEl ? priceEl.innerText.replace(/\\D/g, '') : 0,
                        old_price: oldPriceEl ? oldPriceEl.innerText.replace(/\\D/g, '') : 0,
                    });
                }
            });
            return results;
        }""")
        
        await browser.close()
        
        with open('d:\\crawlVGA\\cps_laptop_test.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(crawl_cellphones_laptop())
