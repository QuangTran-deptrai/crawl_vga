import httpx
import re
import json

r = httpx.get('https://phongvu.vn/c/laptop', follow_redirects=True, verify=False)
match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r.text, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    # Extract only the products to keep the file clean
    products = data['props']['pageProps'].get('serverProducts', [])
    with open('d:\\crawlVGA\\phongvu_laptop_sample.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print("Done generating phongvu_laptop_sample.json")
else:
    print("No NEXT DATA found")
