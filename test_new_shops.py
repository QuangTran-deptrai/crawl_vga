import httpx
import urllib3
import sys
sys.stdout.reconfigure(encoding='utf-8')
urllib3.disable_warnings()

domains = [
    "https://thegioigear.vn",
    "https://sintech.vn",
    "https://nguyentanpc.com",
    "https://maytinhthanhcong.vn",
    "https://tinviettien.vn",
    "https://tanhungphatpc.vn",
    "https://vuongluan.vn",
    "https://bpstore.vn",
    "https://quangninhcomputer.com",
    "https://suplo-laptop.myharavan.com", 
    "https://showroom123.com",
    "https://philong.com.vn"
]

print("Đang kiểm tra các shop mới xem có dùng Haravan không...")
for url in domains:
    test_url = f"{url}/collections/all/products.json?limit=1"
    try:
        r = httpx.get(test_url, verify=False, timeout=5, follow_redirects=True)
        if r.status_code == 200:
            try:
                data = r.json()
                if 'products' in data:
                    print(f"✅ {url:<35} : CHUẨN HARAVAN/SHOPIFY (Có JSON API)")
                else:
                    print(f"❌ {url:<35} : Trả về 200 nhưng không phải Haravan JSON")
            except:
                print(f"❌ {url:<35} : Trả về 200 nhưng không phải JSON")
        else:
            print(f"❌ {url:<35} : KHÔNG PHẢI Haravan (Lỗi {r.status_code})")
    except Exception as e:
        print(f"❌ {url:<35} : Lỗi kết nối hoặc sai Domain")
