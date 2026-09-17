import httpx
import pandas as pd
from datetime import datetime
import time

def crawl_gearvn_vga():
    print("Bắt đầu cào dữ liệu VGA từ GearVN (qua Haravan API)...")
    
    crawl_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # URL chuẩn của Haravan để lấy danh sách sản phẩm trong 1 danh mục
    # Danh mục VGA của GearVN có handle là "vga-card-man-hinh"
    base_url = "https://gearvn.com/collections/vga-card-man-hinh/products.json"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    all_products = []
    page = 1
    
    while True:
        print(f"Đang gọi API Haravan kéo dữ liệu Trang {page}...")
        url = f"{base_url}?limit=250&page={page}"
        
        try:
            response = httpx.get(url, headers=headers, follow_redirects=True, verify=False, timeout=15)
            
            if response.status_code != 200:
                print(f"Lỗi API ở trang {page}: {response.status_code}")
                # GearVN hiện tại đang chặn API này (báo lỗi 404) vì họ mới update hệ thống bảo mật Next.js.
                # Nếu bạn chạy ra lỗi 404, nghĩa là cách này đã bị GearVN khóa (nhưng vẫn xài tốt cho Tin Học Ngôi Sao, APShop...).
                break
                
            data = response.json()
            products = data.get('products', [])
            
            if not products:
                print("Đã lấy hết dữ liệu!")
                break
                
            for product in products:
                # Trích xuất các trường thông tin cơ bản
                name = product.get('title', '')
                vendor = product.get('vendor', '')
                created_at = product.get('created_at', '')
                updated_at = product.get('updated_at', '')
                published_at = product.get('published_at', '')
                
                handle = product.get('handle', '')
                product_url = f"https://gearvn.com/products/{handle}" if handle else ""
                
                # Duyệt qua các biến thể (để lấy giá và tình trạng)
                variants = product.get('variants', [])
                for variant in variants:
                    sku = variant.get('sku', '')
                    price = variant.get('price', '0')
                    old_price = variant.get('compare_at_price', '0')
                    
                    if old_price is None or old_price == '0' or old_price == 0:
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
                        "Ngày Crawl Data": crawl_date,
                        "Ngày tạo": created_at,
                        "Ngày cập nhật": updated_at,
                        "Ngày xuất bản": published_at,
                        "Link sản phẩm": product_url
                    }
                    all_products.append(row)
                    
            page += 1
            time.sleep(1) # Chống block
            
        except Exception as e:
            print(f"Lỗi kết nối: {e}")
            break
            
    if all_products:
        df = pd.DataFrame(all_products)
        excel_file = 'd:\\crawlVGA\\GearVN_VGA_Report.xlsx'
        df.to_excel(excel_file, index=False, engine='openpyxl')
        
        print(f"\n✅ Thành công! Đã cào được tổng cộng {len(all_products)} mã VGA.")
        print(f"✅ Đã lưu kết quả vào file Excel: {excel_file}")
    else:
        print("\n❌ Thất bại: Không lấy được dữ liệu nào. Có khả năng API products.json của GearVN đã bị khóa chặt.")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    crawl_gearvn_vga()
