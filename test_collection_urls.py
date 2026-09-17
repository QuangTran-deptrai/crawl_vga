import httpx
import urllib3
import sys

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
urllib3.disable_warnings()

targets = [
    ("APShop", "https://apshop.vn/collections/card-man-hinh"),
    ("THNS", "https://tinhocngoisao.com/collections/card-man-hinh"),
    ("MemoryZone", "https://memoryzone.com.vn/vga"),
    ("Xgear", "https://xgear.net/collections/vga"),
    ("HangChinhHieu", "https://hangchinhhieu.vn/collections/card-man-hinh"),
    ("TheGioiGear", "https://thegioigear.vn/collections/vga-card-mang-hinh"),
    ("Sintech", "https://sintech.vn/collections/vga"),
    ("NguyenTanPC", "https://nguyentanpc.com/collections/vga-card-man-hinh"),
    ("VuongLuan", "https://vuongluan.vn/collections/vga-card-man-hinh"),
    ("BPStore", "https://bpstore.vn/collections/vga-card-do-hoa"),
    ("TinVietTien", "https://tinviettien.vn/card-man-hinh-vga"), # removed .html to test json
    ("TanHungPhatIT", "https://tanhungphatit.vn/collections/vga-card-man-hinh"),
]

for name, base_url in targets:
    if base_url.endswith('.html'):
        base_url = base_url.replace('.html', '')
    
    # Try different suffixes just in case
    suffixes = ['/products.json?limit=5', '.json?limit=5', '/products.json']
    found = False
    
    # Wait, for Haravan, if url is /collections/xyz, the API is /collections/xyz/products.json
    # If URL is /vga, the API might be /vga/products.json or /collections/vga/products.json
    # Bizweb/Sapo usually has /xyz.json
    
    test_urls = [
        f"{base_url}/products.json?limit=5", # Haravan standard
        f"{base_url}.json?limit=5", # Some Bizweb/Sapo endpoints
    ]
    
    for url in test_urls:
        try:
            r = httpx.get(url, verify=False, timeout=5, follow_redirects=True)
            if r.status_code == 200:
                data = r.json()
                products = data.get('products', [])
                if products:
                    print(f"✅ {name:<15}: SUCCESS ({len(products)} products found) -> {url}")
                    found = True
                    break
        except Exception:
            pass
            
    if not found:
        print(f"❌ {name:<15}: FAILED to fetch API for {base_url}")
