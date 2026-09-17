import httpx
import re
import json

r = httpx.get('https://cellphones.com.vn/laptop.html', follow_redirects=True, verify=False, headers={'User-Agent':'Mozilla/5.0'})

# Try Nuxt 3 format first (application/json)
match_nuxt3 = re.search(r'<script id="__NUXT_DATA__" type="application/json">(.*?)</script>', r.text, re.DOTALL)
if match_nuxt3:
    print("Found Nuxt 3 data")
    data = json.loads(match_nuxt3.group(1))
    with open('d:\\crawlVGA\\cellphones_sample.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved to cellphones_sample.json")
else:
    # Try Nuxt 2 format
    match_nuxt2 = re.search(r'window\.__NUXT__=(.*?);</script>', r.text, re.DOTALL)
    if match_nuxt2:
        print("Found Nuxt 2 data")
        # Nuxt 2 is JS code, we'll just save it as text to inspect
        with open('d:\\crawlVGA\\cellphones_sample.js', 'w', encoding='utf-8') as f:
            f.write(match_nuxt2.group(1))
        print("Saved to cellphones_sample.js")
    else:
        print("No Nuxt data found. Checking for standard JSON API.")
        # Sometimes CPS has a public JSON API for products
