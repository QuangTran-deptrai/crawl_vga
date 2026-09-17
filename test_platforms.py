import httpx
import urllib3
import sys

sys.stdout.reconfigure(encoding='utf-8')
urllib3.disable_warnings()

domains = [
    'https://tinviettien.vn',
    'https://tanhungphatit.vn',
    'https://philong.com.vn',
    'https://quangninhcomputer.vn'
]

print('Đang phân tích nền tảng của 4 Web này...')

for url in domains:
    print(f'\\n=> Checking {url}')
    try:
        # Check Haravan JSON
        r_json = httpx.get(f'{url}/collections/all/products.json?limit=1', verify=False, timeout=5, follow_redirects=True)
        if r_json.status_code == 200 and 'products' in r_json.text:
            print('  ✅ Platform: Haravan (Có JSON API)')
            continue
            
        # Check Homepage HTML
        r_html = httpx.get(url, verify=False, timeout=10, follow_redirects=True)
        html = r_html.text.lower()
        
        platforms = []
        if 'bizweb' in html or 'sapo' in html:
            platforms.append('Sapo Web')
        if 'haravan' in html:
            platforms.append('Haravan (nhưng chặn JSON)')
        if 'wp-content' in html or 'wordpress' in html or 'woocommerce' in html:
            platforms.append('WordPress / WooCommerce')
        if 'next.js' in html or '__next' in html:
            platforms.append('Next.js')
        if 'opencart' in html:
            platforms.append('OpenCart')
            
        if platforms:
            print(f'  [INFO] Platform: {", ".join(platforms)}')
        else:
            print('  [INFO] Platform: Custom Code / PHP / ASP.NET (Không phổ biến)')
            
    except Exception as e:
        print(f'  [ERROR] Lỗi kết nối: {e}')
