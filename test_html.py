import httpx
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

r = httpx.get('https://gearvn.com/collections/vga-card-man-hinh', verify=False, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')

items = soup.select('.pro-loop')
for item in items[:3]:
    name = item.select_one('.pro-name a')
    price = item.select_one('.pro-price')
    old_price = item.select_one('.pro-price-del')
    
    title = name.text.strip() if name else 'N/A'
    link = name['href'] if name else 'N/A'
    p = price.text.strip() if price else 'N/A'
    op = old_price.text.strip() if old_price else 'N/A'
    
    print(f"Title: {title}")
    print(f"Link: {link}")
    print(f"Price: {p} | Old Price: {op}")
    print("-" * 20)
