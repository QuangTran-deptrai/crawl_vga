import httpx
import json
import urllib3
import sys

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
urllib3.disable_warnings()

def fetch_all_raw_json():
    print("🚀 Bắt đầu tải TOÀN BỘ dữ liệu JSON thô từ Tin Học Ngôi Sao...")
    url_base = 'https://tinhocngoisao.com/collections/all/products.json'
    
    all_products = []
    page = 1
    
    while True:
        api_url = f"{url_base}?limit=250&page={page}"
        print(f"📥 Đang kéo Trang {page}...")
        
        try:
            r = httpx.get(api_url, verify=False, timeout=15, follow_redirects=True)
            if r.status_code != 200:
                print(f"Lỗi HTTP: {r.status_code}")
                break
                
            data = r.json()
            products = data.get('products', [])
            
            if not products:
                print(f"✅ Đã tải hết kho dữ liệu tại trang {page-1}")
                break
                
            all_products.extend(products)
            page += 1
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            break
            
    print(f"\n✅ Đã kéo tổng cộng {len(all_products)} sản phẩm.")
    
    output_file = 'd:\\crawlVGA\\thns_raw_all.json'
    print(f"💾 Đang lưu dữ liệu vào {output_file} (Có thể mất vài giây vì file rất lớn)...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)
        
    print("🎉 Đã lưu thành công!")

if __name__ == "__main__":
    fetch_all_raw_json()
