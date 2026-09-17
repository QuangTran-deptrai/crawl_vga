import httpx
import sys
import io
import re
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def clean_price(price_str):
    if not price_str:
        return 0
    cleaned = re.sub(r'[^\d]', '', price_str)
    return int(cleaned) if cleaned else 0

for page in [1]:
    r = httpx.get(f'https://gearvn.com/collections/vga-card-man-hinh?page={page}', verify=False, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    cards = soup.select('a.product-card')
    print(f'Page {page}: Found', len(cards), 'product cards')
    for card in cards:
        product_url = "https://gearvn.com" + card.get('href', '')
        name_el = card.find('p')
        name = name_el.text.strip() if name_el else "Unknown"
        
        # Prices
        prices = [clean_price(s.text) for s in card.select('span') if 'đ' in s.text or '₫' in s.text]
        # Or look at specific classes
        line_through = card.select_one('.line-through')
        flash_price = card.select_one('.text-\\[var\\(--color-flash-price-sale\\)\\]')
        # Wait, bs4 css selector might struggle with escaped classes. Let's just find spans with text containing 'đ' and clean them.
        price_spans = card.find_all('span', string=re.compile(r'đ|₫', re.IGNORECASE))
        if not price_spans:
             price_spans = card.find_all('span', string=re.compile(r'[0-9\.]+₫?đ?'))
        
        all_prices = [clean_price(span.text) for span in price_spans if clean_price(span.text) > 1000]
        
        if len(all_prices) == 0:
            original_price = 0
            discount_price = 0
        elif len(all_prices) == 1:
            original_price = all_prices[0]
            discount_price = all_prices[0]
        else:
            # Usually [old_price, new_price] but we can just take max and min
            original_price = max(all_prices)
            discount_price = min(all_prices)
            
        print(f"Name: {name} | Price: {discount_price} | Old: {original_price} | URL: {product_url}")
