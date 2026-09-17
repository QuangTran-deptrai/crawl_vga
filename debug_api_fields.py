import httpx
import urllib3
import sys
import json

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
urllib3.disable_warnings()

shops = [
    ("APSHOP", "https://apshop.vn/collections/card-man-hinh/products.json?limit=1"),
    ("MEMORYZONE", "https://memoryzone.com.vn/collections/vga/products.json?limit=1"),
    ("XGEAR", "https://xgear.net/collections/vga/products.json?limit=1"),
    ("HANGCHINHHIEU", "https://hangchinhhieu.vn/collections/card-man-hinh/products.json?limit=1"),
    ("THEGIOIGEAR", "https://thegioigear.vn/collections/vga-card-mang-hinh/products.json?limit=1"),
    ("SINTECH", "https://sintech.vn/collections/vga/products.json?limit=1"),
    ("NGUYENTANPC", "https://nguyentanpc.com/collections/vga-card-man-hinh/products.json?limit=1"),
    ("VUONGLUAN", "https://vuongluan.vn/collections/vga-card-man-hinh/products.json?limit=1"),
    ("BPSTORE", "https://bpstore.vn/collections/vga-card-do-hoa/products.json?limit=1"),
    ("TANHUNGPHATIT", "https://tanhungphatit.vn/collections/vga-card-man-hinh/products.json?limit=1"),
    ("TINHOCNGOISAO", "https://tinhocngoisao.com/collections/card-man-hinh/products.json?limit=1"),
]

for name, url in shops:
    print(f"\n{'='*60}")
    print(f"SHOP: {name}")
    print(f"{'='*60}")
    try:
        r = httpx.get(url, verify=False, timeout=10, follow_redirects=True)
        data = r.json()
        products = data.get('products', [])
        if not products:
            print("  NO PRODUCTS FOUND")
            continue
        p = products[0]
        
        # Product-level fields
        print(f"  Product keys: {list(p.keys())}")
        print(f"  title/name: {p.get('title') or p.get('name', 'N/A')}")
        print(f"  handle/alias: {p.get('handle') or p.get('alias', 'N/A')}")
        print(f"  vendor: {p.get('vendor', 'N/A')}")
        print(f"  created_at: {p.get('created_at', 'N/A')}")
        print(f"  updated_at: {p.get('updated_at', 'N/A')}")
        print(f"  published_at: {p.get('published_at', 'N/A')}")
        print(f"  created_on: {p.get('created_on', 'N/A')}")
        print(f"  modified_on: {p.get('modified_on', 'N/A')}")
        print(f"  published_on: {p.get('published_on', 'N/A')}")
        print(f"  url: {p.get('url', 'N/A')}")
        print(f"  price (product level): {p.get('price', 'N/A')}")
        print(f"  available: {p.get('available', 'N/A')}")
        
        # Variant-level fields
        variants = p.get('variants', [])
        if variants:
            v = variants[0]
            print(f"\n  Variant keys: {list(v.keys())}")
            print(f"  variant.sku: '{v.get('sku', 'N/A')}'")
            print(f"  variant.price: {v.get('price', 'N/A')}")
            print(f"  variant.compare_at_price: {v.get('compare_at_price', 'N/A')}")
            print(f"  variant.available: {v.get('available', 'N/A')}")
        else:
            print(f"\n  NO VARIANTS FOUND")
            print(f"  product.price: {p.get('price', 'N/A')}")
            print(f"  product.compare_at_price: {p.get('compare_at_price', 'N/A')}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\nDone!")
