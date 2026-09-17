import httpx
import re

r = httpx.get('https://www.thegioididong.com/laptop', follow_redirects=True, verify=False, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
# Search for product item wrappers
items = re.findall(r'<li class="item.*?</li>', r.text, re.DOTALL | re.IGNORECASE)
print(f"Found {len(items)} product HTML items on first load.")

# Check for any massive JSON block
json_blocks = re.findall(r'<script type="application/json">(.*?)</script>', r.text, re.DOTALL)
print(f"Found {len(json_blocks)} JSON script blocks.")
