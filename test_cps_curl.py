import httpx
import json

headers = {
    'accept': 'application/json',
    'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
    'content-type': 'application/json',
    'origin': 'https://cellphones.com.vn',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36',
    'x-client-type': 'web'
}

# Sửa lỗi dính chữ trong phần filter_price (từ from:0to:167000000 thành from:0, to:167000000)
query = """
query GetProductsByCateId{
    products(
        filter: {
            static: {
                categories: ["380"],
                excluded:{
                    categories: []
                },
                province_id: 30,
                stock: {
                    from: 0
                },
                company_stock_id: [46, 56, 152, 4920],
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
            attributes
            sku
            doc_quyen
            manufacturer
            url_key
            url_path
            categories{
                categoryId
                name
                uri
            }
            review{
                total_count
                average_rating
            }
        },
        filterable{
            allow_cart_types
            is_installment
            stock_available_id
            company_stock_id
            stock
            filter {
                id
                Label
            }
            is_parent
            price
            prices
            special_price
            promotion_information
            thumbnail
            promotion_pack
            sticker
            flash_sale_types
            is_new_arrival
            display_root_price
            display_price
            default_bundle_discount {
                pricing_summaries
            }
            promotion_info
            delivery_badge
        }
    }
}
"""

json_data = {
    'query': query,
    'variables': {},
}

def fetch_data():
    print("Gửi request lên API CellphoneS...")
    response = httpx.post('https://api.cellphones.com.vn/v2/graphql/query', headers=headers, json=json_data, verify=False)
    
    if response.status_code == 200:
        data = response.json()
        products = data.get('data', {}).get('products', [])
        print(f"Thành công! Lấy được {len(products)} sản phẩm.")
        
        # Lưu vào file JSON
        with open('d:\\crawlVGA\\cps_curl_result.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print("Đã lưu kết quả cào được vào file cps_curl_result.json!")
    else:
        print(f"Lỗi rồi! Status code: {response.status_code}")
        print(response.text)

if __name__ == '__main__':
    # Đặt encoding cho stdout để không lỗi trên Windows
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    fetch_data()
