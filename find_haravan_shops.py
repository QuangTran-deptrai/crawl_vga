import httpx
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Danh sách các đại lý IT / Công nghệ tiềm năng tại Việt Nam
shops = [
    'https://apshop.vn',
    'https://hangchinhhieu.vn',
    'https://laptop88.vn',
    'https://mega.com.vn',
    'https://thinkpro.vn',
    'https://maccenter.vn',
    'https://zshop.vn',
    'https://minhancomputer.com',
    'https://hacom.vn', # thử lại cho chắc
    'https://npcshop.vn',
    'https://tranglinh.vn',
    'https://tandoanh.vn',
    'https://khanhthao.vn',
    'https://hoangtuan.vn'
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print("Đang quét tìm các đại lý dùng Haravan (Cửa sau API products.json)...\n")

haravan_shops = []

for shop in shops:
    try:
        # Haravan & Shopify thường mở API ở /collections/all/products.json hoặc /products.json
        api_url = f"{shop}/collections/all/products.json"
        
        r = httpx.get(api_url, headers=headers, follow_redirects=True, verify=False, timeout=10)
        
        if r.status_code == 200 and 'products' in r.text:
            print(f"✅ {shop:<25} : CHUẨN HARAVAN/SHOPIFY (Có JSON API)")
            haravan_shops.append(shop)
        else:
            # Thử thêm link /products.json cho chắc ăn
            api_url_2 = f"{shop}/products.json"
            r2 = httpx.get(api_url_2, headers=headers, follow_redirects=True, verify=False, timeout=10)
            if r2.status_code == 200 and 'products' in r2.text:
                 print(f"✅ {shop:<25} : CHUẨN HARAVAN/SHOPIFY (Có JSON API)")
                 haravan_shops.append(shop)
            else:
                 print(f"❌ {shop:<25} : KHÔNG PHẢI Haravan (Lỗi {r.status_code})")
    except Exception as e:
        print(f"⚠️ {shop:<25} : LỖI TRUY CẬP ({e})")

print(f"\nTổng kết: Tìm thấy {len(haravan_shops)} đại lý dùng Haravan!")
