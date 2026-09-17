import httpx
import urllib3
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
urllib3.disable_warnings()

domains = [
    "https://tinhocngoisao.com",
    "https://apshop.vn",
    "https://memoryzone.com.vn",
    "https://xgear.net",
    "https://hangchinhhieu.vn",
    "https://thegioigear.vn",
    "https://sintech.vn",
    "https://nguyentanpc.com",
    "https://maytinhthanhcong.vn",
    "https://vuongluan.vn",
    "https://bpstore.vn",
    "https://tinviettien.vn",
    "https://tanhungphatit.vn"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("Đang quét nhanh (tối đa 1250 sản phẩm mới nhất mỗi shop) để kiểm tra lượng VGA...")
print("-" * 70)

for url in domains:
    vga_count = 0
    page = 1
    max_pages = 5 # Quét 5 trang đầu tiên (1250 sản phẩm) để test nhanh
    
    while page <= max_pages:
        api_url = f"{url}/collections/all/products.json?limit=250&page={page}"
        try:
            r = httpx.get(api_url, headers=headers, verify=False, timeout=10, follow_redirects=True)
            if r.status_code != 200:
                break
                
            data = r.json()
            products = data.get('products', [])
            if not products:
                break
                
            for product in products:
                title = product.get('title', '').lower()
                product_type = product.get('product_type', '').lower()
                
                is_vga = False
                
                if 'vga' in product_type or 'card màn hình' in product_type:
                    is_vga = True
                if 'card màn hình' in title or 'vga ' in title:
                    is_vga = True
                    
                blacklist = ['cáp', 'dây', 'laptop', 'màn hình văn phòng', 'màn hình gaming', 
                             'thùng máy', 'nguồn', 'pc', 'máy bộ', 'mainboard', 'cpu']
                
                for word in blacklist:
                    if word in title:
                        is_vga = False
                        break
                        
                if is_vga:
                    vga_count += 1
                    
            page += 1
        except Exception:
            break
            
    if vga_count > 0:
        print(f"✅ {url:<30} : Có bán VGA (Tìm thấy {vga_count} mã trong {page-1} trang đầu)")
    else:
        print(f"⚠️ {url:<30} : KHÔNG THẤY VGA trong {page-1} trang đầu (Có thể không bán hoặc nằm ở trang sâu hơn)")

print("-" * 70)
print("Hoàn tất kiểm tra!")
