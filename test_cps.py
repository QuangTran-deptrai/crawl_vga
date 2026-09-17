import httpx
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# Let's test a few common CellphoneS API structures
urls = [
    'https://api.cellphones.com.vn/v2/graphql',
    'https://api.cellphones.com.vn/v2/products/laptop',
    'https://api.cellphones.com.vn/v3/products/laptop',
    'https://cellphones.com.vn/api/catalog/products'
]

for u in urls:
    try:
        r = httpx.get(u, headers=headers, verify=False)
        print(f"{u}: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        print(f"{u}: Error {e}")
