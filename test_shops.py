import httpx
import sys

sys.stdout.reconfigure(encoding='utf-8')

shops = [
    'https://www.anphatpc.com.vn',
    'https://hacom.vn',
    'https://fptshop.com.vn',
    'https://nguyencongpc.vn',
    'https://www.phucanh.vn',
    'https://hoanghamobile.com',
    'https://dienmaycholon.vn'
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for shop in shops:
    try:
        r = httpx.get(shop, headers=headers, follow_redirects=True, verify=False, timeout=15)
        text = r.text.lower()
        
        is_haravan = 'haravan' in text or 'shopify' in text
        is_next = '__next_data__' in text
        is_nuxt = '__nuxt__' in text
        has_bizweb = 'bizweb' in text or 'sapo' in text
        
        if is_haravan: type_ = 'Haravan/Shopify'
        elif has_bizweb: type_ = 'Sapo/Bizweb (API)'
        elif is_next: type_ = 'Next.js'
        elif is_nuxt: type_ = 'Nuxt.js'
        else: type_ = 'Tu code/PHP/Custom'
        
        shop_name = shop.split('//')[1]
        print(f'{shop_name:<25} : {type_}')
    except Exception as e:
        print(f'{shop:<25} : Loi - {e}')
