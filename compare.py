import json
import httpx
import sys

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

url_template = 'https://tinhocngoisao.com/collections/card-man-hinh/products.json?limit=250&page={}'
collection_prods = []
for page in range(1, 10):
    r = httpx.get(url_template.format(page), verify=False, timeout=5, follow_redirects=True)
    products = r.json().get('products', [])
    if not products:
        break
    collection_prods.extend(products)

with open('thns_vga_filtered.json', 'r', encoding='utf-8') as f:
    filtered_prods = json.load(f)

collection_handles = {p['handle'] for p in collection_prods}
filtered_handles = {p['handle'] for p in filtered_prods}

diff = collection_handles - filtered_handles
print(f"Products in collection but not in filtered (diff: {len(diff)}):")
for p in collection_prods:
    if p['handle'] in diff:
        print(f"- {p['title']} | {p['handle']}")

with open('thns_vga_collection_true.json', 'w', encoding='utf-8') as f:
    json.dump(collection_prods, f, ensure_ascii=False, indent=2)
print("Saved all 152 to thns_vga_collection_true.json")
