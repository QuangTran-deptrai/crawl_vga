import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def intercept_cps_api():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        def check_request(request):
            # Lọc các request có thể chứa dữ liệu sản phẩm
            if request.method == "POST" and "graphql" in request.url:
                if request.post_data and "cps_category_products" in request.post_data or "filter" in request.post_data:
                    print(f"\n[POTENTIAL PRODUCT API] {request.method} {request.url}")
                    print(f"Payload: {request.post_data}")
            elif request.method == "POST" and "product" in request.url.lower():
                print(f"\n[POTENTIAL PRODUCT API] {request.method} {request.url}")
                print(f"Payload: {request.post_data}")

        page.on("request", lambda request: check_request(request))
        
        await page.goto("https://cellphones.com.vn/laptop.html", wait_until="domcontentloaded")
        
        try:
            button = await page.wait_for_selector(".btn-show-more", timeout=10000)
            if button:
                print("\nClicking 'Xem thêm' để kích hoạt API load data...")
                # Scroll to button
                await button.scroll_into_view_if_needed()
                await page.evaluate("document.querySelector('.btn-show-more').click()")
                await page.wait_for_timeout(5000) # Đợi 5 giây để bắt các API bắn ra
        except Exception as e:
            print("Không thấy nút xem thêm:", e)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(intercept_cps_api())
