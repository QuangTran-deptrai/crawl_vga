import httpx
import pandas as pd
from datetime import datetime
import time

def crawl_gearvn_laptops():
    print("Bắt đầu cào dữ liệu từ GearVN (Lọc riêng Laptop)...")
    
    crawl_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Lấy toàn bộ sản phẩm của GearVN, sau đó ta tự lọc ra Laptop
    base_url = "https://gearvn.com/collections/all/products.json"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    all_products = []
    page = 1
    
    # Cào khoảng 5 trang đầu để test, hoặc bạn có thể bỏ giới hạn page <= 5 để cào toàn bộ web
    while page <= 10:
        print(f"Đang kéo dữ liệu Trang {page}...")
        url = f"{base_url}?limit=250&page={page}"
        response = httpx.get(url, headers=headers, follow_redirects=True, verify=False, timeout=15)
        
        if response.status_code != 200:
            print(f"Lỗi truy cập trang {page}: {response.status_code}")
            break
            
        data = response.json()
        products = data.get('products', [])
        
        if not products:
            print("Đã lấy hết dữ liệu!")
            break
            
        for product in products:
            product_type = product.get('product_type', '')
            
            # Chỉ lấy các sản phẩm thuộc nhóm Laptop (hoặc Máy tính xách tay)
            if 'laptop' not in product_type.lower() and 'máy tính xách tay' not in product_type.lower():
                continue
                
            name = product.get('title', '')
            vendor = product.get('vendor', '')
            created_at = product.get('created_at', '')
            updated_at = product.get('updated_at', '')
            published_at = product.get('published_at', '')
            handle = product.get('handle', '')
            url = f"https://gearvn.com/products/{handle}" if handle else ""
            
            variants = product.get('variants', [])
            for variant in variants:
                sku = variant.get('sku', '')
                price = variant.get('price', '0')
                old_price = variant.get('compare_at_price', '0')
                if old_price is None or old_price == 0:
                    old_price = price
                
                variant_available = variant.get('available', False)
                
                row = {
                    "Đại lý": "GearVN",
                    "Hãng": vendor,
                    "Mã SKU": sku,
                    "Tên sản phẩm": name,
                    "Giá bán": float(price) if price else 0,
                    "Giá gốc": float(old_price) if old_price else 0,
                    "Còn hàng": "Có" if variant_available else "Không",
                    "Ngày tạo": created_at,
                    "Ngày cập nhật": updated_at,
                    "Ngày xuất bản": published_at,
                    "Ngày Crawl Data": crawl_date,
                    "Link sản phẩm": url
                }
                all_products.append(row)
                
        page += 1
        time.sleep(0.5)
        
    if not all_products:
        print("Không tìm thấy laptop nào (hoặc GearVN phân loại tên khác). Đang thử lưu 5 sản phẩm đầu tiên làm mẫu...")
        # Nếu không có Laptop, lưu tạm sản phẩm bất kỳ để xuất file
        for product in products[:5]:
            row = {
                    "Đại lý": "GearVN",
                    "Hãng": product.get('vendor', ''),
                    "Mã SKU": product.get('variants', [{}])[0].get('sku', ''),
                    "Tên sản phẩm": product.get('title', ''),
                    "Giá bán": float(product.get('variants', [{}])[0].get('price', 0)),
                    "Giá gốc": float(product.get('variants', [{}])[0].get('compare_at_price') or product.get('variants', [{}])[0].get('price', 0)),
                    "Còn hàng": "Có" if product.get('variants', [{}])[0].get('available') else "Không",
                    "Ngày tạo": product.get('created_at', ''),
                    "Ngày cập nhật": product.get('updated_at', ''),
                    "Ngày xuất bản": product.get('published_at', ''),
                    "Ngày Crawl Data": crawl_date,
                    "Link sản phẩm": f"https://gearvn.com/products/{product.get('handle', '')}"
                }
            all_products.append(row)
            
    df = pd.DataFrame(all_products)
    excel_file = 'd:\\crawlVGA\\GearVN_Laptop_B2B_Report.xlsx'
    df.to_excel(excel_file, index=False, engine='openpyxl')
    
    print(f"\nThành công! Đã cào được tổng cộng {len(all_products)} phân loại sản phẩm.")
    print(f"Đã lưu kết quả vào file Excel: {excel_file}")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    crawl_gearvn_laptops()
