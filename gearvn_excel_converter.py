import json
import pandas as pd
from datetime import datetime

def convert_gearvn_json_to_excel(json_filepath, excel_filepath):
    print(f"Bắt đầu đọc dữ liệu từ file: {json_filepath}...")
    
    # Đọc file JSON mẫu của bạn
    with open(json_filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    products = data.get('products', [])
    if not products:
        print("Không tìm thấy dữ liệu 'products' trong file JSON.")
        return
        
    print(f"Đã đọc được {len(products)} sản phẩm. Đang xử lý thành bảng Excel...")
    
    crawl_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_products = []
    
    for product in products:
        # Lấy các thông tin chung
        name = product.get('title', '')
        vendor = product.get('vendor', '')
        product_type = product.get('product_type', '')
        created_at = product.get('created_at', '')
        updated_at = product.get('updated_at', '')
        published_at = product.get('published_at', '')
        handle = product.get('handle', '')
        url = f"https://gearvn.com/products/{handle}" if handle else ""
        
        # Biến trạng thái tổng của toàn bộ sản phẩm
        product_available = product.get('available', False)
        
        variants = product.get('variants', [])
        for variant in variants:
            sku = variant.get('sku', '')
            price = variant.get('price', '0')
            old_price = variant.get('compare_at_price', '0')
            if not old_price or old_price == '0':
                old_price = price
            
            # Trạng thái available của từng biến thể
            variant_available = variant.get('available', product_available)
            
            # Gộp vào 1 hàng dữ liệu
            row = {
                "Đại lý": "GearVN",
                "Loại SP": product_type,
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
            
    # Chuyển đổi sang DataFrame của Pandas
    df = pd.DataFrame(all_products)
    
    # Xuất file Excel
    df.to_excel(excel_filepath, index=False, engine='openpyxl')
    
    print(f"✅ Thành công! Đã chuyển đổi {len(all_products)} dòng dữ liệu.")
    print(f"✅ File Excel đã được lưu tại: {excel_filepath}")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    input_file = "d:\\crawlVGA\\gearvn_sample.json"
    output_file = "d:\\crawlVGA\\GearVN_B2B_Report.xlsx"
    
    convert_gearvn_json_to_excel(input_file, output_file)
