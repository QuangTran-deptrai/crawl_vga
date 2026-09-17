import httpx
import pandas as pd
from datetime import datetime
import time
import urllib3
import sys
import os

# Đảm bảo in tiếng Việt ra console không bị lỗi trên Windows
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
urllib3.disable_warnings()

def crawl_master_vga():
    print("🚀 Bắt đầu khởi động Master Scraper lấy dữ liệu từ các danh mục chuẩn...")
    
    crawl_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    shop_targets = [
        {"name": "APSHOP", "base_url": "https://apshop.vn", "api_url": "https://apshop.vn/collections/card-man-hinh/products.json", "platform": "haravan"},
        {"name": "TINHOCNGOISAO", "base_url": "https://tinhocngoisao.com", "api_url": "https://tinhocngoisao.com/collections/card-man-hinh/products.json", "platform": "haravan"},
        {"name": "MEMORYZONE", "base_url": "https://memoryzone.com.vn", "api_url": "https://memoryzone.com.vn/collections/vga/products.json", "platform": "sapo"},
        {"name": "XGEAR", "base_url": "https://xgear.net", "api_url": "https://xgear.net/collections/vga/products.json", "platform": "haravan"},
        {"name": "HANGCHINHHIEU", "base_url": "https://hangchinhhieu.vn", "api_url": "https://hangchinhhieu.vn/collections/card-man-hinh/products.json", "platform": "haravan"},
        {"name": "THEGIOIGEAR", "base_url": "https://thegioigear.vn", "api_url": "https://thegioigear.vn/collections/vga-card-mang-hinh/products.json", "platform": "haravan"},
        {"name": "SINTECH", "base_url": "https://sintech.vn", "api_url": "https://sintech.vn/collections/vga/products.json", "platform": "haravan"},
        {"name": "NGUYENTANPC", "base_url": "https://nguyentanpc.com", "api_url": "https://nguyentanpc.com/collections/vga-card-man-hinh/products.json", "platform": "haravan"},
        {"name": "VUONGLUAN", "base_url": "https://vuongluan.vn", "api_url": "https://vuongluan.vn/collections/vga-card-man-hinh/products.json", "platform": "haravan"},
        {"name": "BPSTORE", "base_url": "https://bpstore.vn", "api_url": "https://bpstore.vn/collections/vga-card-do-hoa/products.json", "platform": "haravan"},
        {"name": "TINVIETTIEN", "base_url": "https://tinviettien.vn", "api_url": "https://tinviettien.vn/collections/card-man-hinh-vga/products.json", "platform": "haravan"},
        {"name": "TANHUNGPHATIT", "base_url": "https://tanhungphatit.vn", "api_url": "https://tanhungphatit.vn/collections/vga-card-man-hinh/products.json", "platform": "haravan"}
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    all_products = []
    
    # Bộ lọc loại trừ (Blacklist) dùng để phòng hờ trường hợp shop gắn nhầm sản phẩm vào danh mục VGA
    blacklist = [
        'cáp', 'dây', 'laptop', 'màn hình văn phòng', 'màn hình gaming', 
        'thùng máy', 'nguồn', 'pc', 'máy bộ', 'mainboard', 'cpu', 'chuột', 'bàn phím',
        'đế tản nhiệt', 'quạt', 'fan', 'balo', 'túi chống sốc', 'tai nghe', 'loa'
    ]
    
    for shop in shop_targets:
        shop_name = shop['name']
        base_url = shop['base_url']
        base_api_url = shop['api_url']
        platform = shop.get('platform', 'haravan')
        
        print(f"\n=============================================")
        print(f"📥 Đang càn quét kho hàng của: {shop_name}")
        print(f"🔗 API Endpoint: {base_api_url}")
        print(f"=============================================")
        
        page = 1
        shop_vga_count = 0
        
        while True:
            # Gắn thêm param phân trang
            api_url = f"{base_api_url}?limit=250&page={page}"
            
            try:
                response = httpx.get(api_url, headers=headers, follow_redirects=True, verify=False, timeout=10)
                
                if response.status_code != 200:
                    print(f"  [!] Lỗi API ở trang {page}: {response.status_code} - Dừng quét shop này.")
                    break
                    
                try:
                    data = response.json()
                except Exception as e:
                    print(f"  [!] Lỗi parse JSON ở trang {page} (có thể API không hỗ trợ): {e}")
                    break
                    
                products = data.get('products', [])
                
                if not products:
                    print(f"  [+] Đã vét cạn kho hàng! Dừng ở trang {page-1}.")
                    break
                    
                for product in products:
                    title = (product.get('title') or product.get('name', '')).lower()
                    
                    is_vga = True
                        
                    for word in blacklist:
                        if f" {word} " in f" {title} " or title.startswith(f"{word} "):
                            is_vga = False
                            break
                    
                    if not is_vga:
                        continue
                        
                    # Trích xuất dữ liệu
                    name = product.get('title') or product.get('name', '')
                    vendor = product.get('vendor', '')
                    
                    # Xử lý ngày tháng - Sapo (Bizweb) không trả về ngày trong API collection
                    if platform == 'sapo':
                        created_at = 'Không hỗ trợ'
                        updated_at = 'Không hỗ trợ'
                        published_at = 'Không hỗ trợ'
                    else:
                        created_at = product.get('created_at') or product.get('created_on', '')
                        updated_at = product.get('updated_at') or product.get('modified_on', '')
                        published_at = product.get('published_at') or product.get('published_on', '')
                    
                    handle = product.get('handle') or product.get('alias', '')
                    url_path = product.get('url', '')
                    
                    if url_path:
                        product_url = f"{base_url}{url_path}" if url_path.startswith('/') else f"{base_url}/{url_path}"
                    else:
                        product_url = f"{base_url}/products/{handle}" if handle else ""
                    
                    product_available = product.get('available', False)
                    
                    # Giá ở cấp product (dùng làm fallback nếu variant.price = 0)
                    product_price = product.get('price', 0) or 0
                    product_compare = product.get('compare_at_price_max') or product.get('compare_at_price', 0) or 0
                    
                    variants = product.get('variants', [])
                    
                    # Một số API trả về variants rỗng nhưng có price ở ngoài (tuỳ nền tảng)
                    if not variants:
                        variants = [{'sku': '', 'price': product_price, 'compare_at_price': product_compare, 'available': product_available}]

                    for variant in variants:
                        # SKU: Haravan trả về None (Python None) hoặc chuỗi 'None' nếu shop không nhập
                        raw_sku = variant.get('sku')
                        sku = '' if (raw_sku is None or str(raw_sku).strip() == 'None') else str(raw_sku).strip()
                        
                        # Giá: Một số shop set price=0 cho sản phẩm "Liên hệ" hoặc chưa có giá
                        price = variant.get('price', 0) or 0
                        old_price = variant.get('compare_at_price', 0) or 0
                        
                        # Fallback: nếu variant.price = 0 nhưng product.price có giá trị -> dùng product.price
                        if float(price) == 0 and float(product_price) > 0:
                            price = product_price
                        if float(old_price) == 0 and float(product_compare) > 0:
                            old_price = product_compare
                        
                        # Nếu giá gốc vẫn = 0 thì set bằng giá bán (không giảm giá)
                        if float(old_price) == 0:
                            old_price = price
                        
                        variant_available = variant.get('available', product_available)
                        
                        row = {
                            "Đại lý": shop_name,
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
                        shop_vga_count += 1
                        
                print(f"  - Quét xong trang {page} (gom được {shop_vga_count} VGA tới hiện tại)")
                page += 1
                time.sleep(0.3) # Giãn cách để tránh bị ban IP
                
            except Exception as e:
                print(f"  [!] Lỗi kết nối: {e}")
                break
                
        print(f"✅ HOÀN TẤT SHOP {shop_name} - TỔNG CỘNG TÌM THẤY: {shop_vga_count} MÃ VGA")
        
        # Lưu Incremental (Lưu sau mỗi shop để tránh mất dữ liệu)
        if all_products:
            excel_file = 'd:\\crawlVGA\\Master_VGA_Report.xlsx'
            df_new = pd.DataFrame(all_products)
            
            # Đọc dữ liệu cũ nếu file đã tồn tại, rồi nối thêm dữ liệu mới
            if os.path.exists(excel_file):
                try:
                    df_old = pd.read_excel(excel_file, engine='openpyxl')
                    df_combined = pd.concat([df_old, df_new], ignore_index=True)
                except Exception:
                    df_combined = df_new
            else:
                df_combined = df_new
            
            df_combined.to_excel(excel_file, index=False, engine='openpyxl')
            print(f"  💾 Đã lưu tạm thời vào {excel_file} (tổng {len(df_combined)} dòng)")

    print(f"\n🚀 TỔNG KẾT CHIẾN DỊCH: ĐÃ CÀO ĐƯỢC {len(all_products)} MÃ VGA MỚI TRONG LẦN CHẠY NÀY!")
    
    if all_products:
        excel_file = 'd:\\crawlVGA\\Master_VGA_Report.xlsx'
        df_new = pd.DataFrame(all_products)
        
        # Đọc dữ liệu cũ nếu file đã tồn tại, rồi nối thêm dữ liệu mới
        if os.path.exists(excel_file):
            try:
                df_old = pd.read_excel(excel_file, engine='openpyxl')
                df_combined = pd.concat([df_old, df_new], ignore_index=True)
            except Exception:
                df_combined = df_new
        else:
            df_combined = df_new
        
        df_combined.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"💾 Dữ liệu đã lưu thành công vào: {excel_file}")
        print(f"📊 Tổng cộng trong file: {len(df_combined)} dòng")
        print(f"📅 Lần chạy này thêm: {len(all_products)} dòng mới")

if __name__ == "__main__":
    crawl_master_vga()
