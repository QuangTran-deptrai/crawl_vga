import asyncio
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright
import time

async def scrape_gearvn_vga():
    print("Khởi động trình duyệt Playwright để cào GearVN (Next.js)...")
    
    url = "https://gearvn.com/collections/vga-card-man-hinh"
    crawl_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    all_products = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Chặn hình ảnh để tải trang nhanh hơn
        await page.route("**/*.{png,jpg,jpeg,webp,svg,gif}", lambda route: route.abort())
        
        print(f"Đang truy cập: {url}")
        await page.goto(url, wait_until="networkidle")
        
        # Cuộn trang để load hết dữ liệu (Next.js thường dùng lazy load hoặc infinite scroll)
        for i in range(5):
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(1000)
            
        # Lấy tất cả các thẻ chứa thông tin sản phẩm (GearVN Next.js structure)
        # Bằng cách tìm tất cả thẻ <a> trỏ tới /products/
        product_elements = await page.query_selector_all('a[href^="/products/"]')
        
        print(f"Tìm thấy {len(product_elements)} link sản phẩm trên trang đầu tiên.")
        
        seen_links = set()
        
        for element in product_elements:
            link_path = await element.get_attribute('href')
            if not link_path or link_path in seen_links:
                continue
                
            seen_links.add(link_path)
            full_link = f"https://gearvn.com{link_path}"
            
            # Lấy text bên trong thẻ a (thường chứa tên và giá)
            # Hoặc đi ngược lên parent để lấy thông tin chi tiết
            # Vì DOM của Next.js GearVN khá phức tạp, ta sẽ thử extract trực tiếp từ text
            text_content = await element.inner_text()
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            
            if len(lines) < 2:
                # Có thể đây chỉ là thẻ a bọc cái hình ảnh, ta phải tìm thẻ cha
                parent = await element.evaluate_handle('el => el.parentElement.parentElement')
                text_content = await parent.inner_text()
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                
            if len(lines) >= 2:
                # Thông thường cấu trúc text sẽ là: [Tên sản phẩm, Giá bán, Giá gốc (nếu có)]
                name = lines[0]
                price_str = lines[1]
                
                # Làm sạch giá
                price = ''.join(filter(str.isdigit, price_str))
                price = float(price) if price else 0
                
                old_price = price
                if len(lines) > 2:
                    old_price_str = lines[2]
                    old_price_clean = ''.join(filter(str.isdigit, old_price_str))
                    if old_price_clean:
                        old_price = float(old_price_clean)
                
                row = {
                    "Đại lý": "GearVN",
                    "Hãng": "N/A", # DOM scrape khó lấy hãng chuẩn
                    "Mã SKU": link_path.replace('/products/', ''),
                    "Tên sản phẩm": name,
                    "Giá bán": price,
                    "Giá gốc": old_price,
                    "Còn hàng": "Có", # Tạm thời giả định là có hàng trên web
                    "Ngày tạo": "N/A",
                    "Ngày cập nhật": "N/A",
                    "Ngày xuất bản": "N/A",
                    "Ngày Crawl Data": crawl_date,
                    "Link sản phẩm": full_link
                }
                all_products.append(row)
                
        await browser.close()
        
    df = pd.DataFrame(all_products)
    excel_file = 'd:\\crawlVGA\\GearVN_VGA_Playwright_Report.xlsx'
    df.to_excel(excel_file, index=False, engine='openpyxl')
    
    print(f"\nThành công! Đã cào được {len(all_products)} card màn hình.")
    print(f"Đã lưu kết quả vào file Excel: {excel_file}")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    asyncio.run(scrape_gearvn_vga())
