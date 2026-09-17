import httpx
import json

url = "https://api.cellphones.com.vn/v2/graphql/query"

# Payload chuẩn hóa từ trình duyệt của người dùng
# Chú ý tôi đã sửa một chút chỗ 'filter_price' bị dính chữ (from:0to:167000000 -> from:0, to:167000000)
graphql_query = """
query GetProductsByCateId{
    products(
        filter: {
            static: {
                categories: ["380"],
                province_id: 30,
                stock: {
                   from: 0
                },
                filter_price: {from: 0, to: 167000000}
            },
            dynamic: {}
        },
        page: 1,
        size: 20,
        sort: [{view: desc}]
    )
    {
        general{
            product_id
            name
            sku
            url_path
        },
        filterable{
            stock
            price
            special_price
        }
    }
}
"""

payload = {
    "query": graphql_query,
    "variables": {}
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def test_cellphones_api():
    print("Đang gọi CellphoneS GraphQL API...")
    response = httpx.post(url, json=payload, headers=headers, verify=False)
    
    if response.status_code == 200:
        data = response.json()
        products = data.get('data', {}).get('products', [])
        
        print(f"Thành công! Lấy được {len(products)} sản phẩm.")
        
        # Lưu mẫu ra file để người dùng xem cấu trúc
        with open('d:\\crawlVGA\\cps_api_test.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print("Đã lưu vào cps_api_test.json")
    else:
        print(f"Lỗi: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_cellphones_api()
