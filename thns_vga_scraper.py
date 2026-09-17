import httpx
import pandas as pd
from datetime import datetime
import time
import urllib3
urllib3.disable_warnings()

def crawl_thns_vga():
    print("Bắt đầu cào dữ liệu VGA từ Tin Học Ngôi Sao (Bộ lọc siêu nghiêm ngặt)...")
    
    crawl_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    base_url = "https://tinhocngoisao.com/collections/all/products.json"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    all_products = []
    page = 1
    
    # Cào toàn bộ trang để không bỏ sót hàng cũ
    while True:
        print(f"Đang gọi API kéo dữ liệu Trang {page}...")
        url = f"{base_url}?limit=250&page={page}"
        
        try:
            response = httpx.get(url, headers=headers, follow_redirects=True, verify=False, timeout=15)
            
            if response.status_code != 200:
                print(f"Lỗi API ở trang {page}: {response.status_code}")
                break
                
            data = response.json()
            products = data.get('products', [])
            
            if not products:
                print("Đã lấy hết dữ liệu!")
                break
                
            for product in products:
                title = product.get('title', '').lower()
                product_type = product.get('product_type', '').lower()
                
                is_vga = False
                
                # Mở rộng bộ lọc: Ưu tiên Product Type chứa VGA hoặc title chứa "card màn hình", "vga "
                if 'vga' in product_type or 'card màn hình' in product_type:
                    is_vga = True
                    
                if 'card màn hình' in title or 'vga ' in title:
                    is_vga = True

                    
                # BỘ LỌC LOẠI TRỪ (Blacklist) để loại rác
                blacklist = ['cáp', 'dây', 'laptop', 'màn hình văn phòng', 'màn hình gaming', 
                             'thùng máy', 'nguồn', 'pc', 'máy bộ', 'mainboard', 'cpu']
                
                for word in blacklist:
                    if word in title:
                        is_vga = False
                        break
                
                if not is_vga:
                    continue
                    
                name = product.get('title', '')
                vendor = product.get('vendor', '')
                created_at = product.get('created_at', '')
                updated_at = product.get('updated_at', '')
                published_at = product.get('published_at', '')
                
                handle = product.get('handle', '')
                product_url = f"https://tinhocngoisao.com/products/{handle}" if handle else ""
                
                product_available = product.get('available', False)
                
                variants = product.get('variants', [])
                for variant in variants:
                    sku = variant.get('sku', '')
                    price = variant.get('price', '0')
                    old_price = variant.get('compare_at_price', '0')
                    
                    if old_price is None or old_price == '0' or old_price == 0:
                        old_price = price
                    
                    variant_available = variant.get('available', product_available)
                    
                    row = {
                        "Đại lý": "Tin Học Ngôi Sao",
                        "Hãng": vendor,
                        "Mã SKU": sku,
                        "Tên sản phẩm": name,
                        "Giá bán": float(price) if price else 0,
                        "Giá gốc": float(old_price) if old_price else 0,
                        "Còn hàng": "Có" if variant_available else "Không",
                        "Ngày Crawl Data": crawl_date,
                        "Ngày tạo": created_at,
                        "Ngày cập nhật": updated_at,
                        "Ngày xuất bản": published_at,
                        "Link sản phẩm": product_url
                    }
                    all_products.append(row)
                    
            page += 1
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Lỗi kết nối: {e}")
            break
            
    if all_products:
        df = pd.DataFrame(all_products)
        excel_file = 'd:\\crawlVGA\\THNS_VGA_Report_Clean.xlsx'
        df.to_excel(excel_file, index=False, engine='openpyxl')
        
        print(f"\n✅ Thành công! Đã cào được {len(all_products)} mã VGA SẠCH từ Tin Học Ngôi Sao.")
        print(f"✅ Đã lưu kết quả vào file Excel: {excel_file}")
    else:
        print("\n❌ Thất bại: Không lấy được dữ liệu nào.")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    crawl_thns_vga()
