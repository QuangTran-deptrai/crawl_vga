import httpx
query = """
query GetProductsByCateId{
    products(
        filter: {static: {categories: ["380"], province_id: 30, stock: {from: 0}, filter_price: {from:0, to:167000000}}, dynamic: {}},
        page: 1, size: 1, sort: [{view: desc}]
    ) {
        general {
            product_id
            name
            created_at
            updated_at
        }
    }
}
"""
r = httpx.post('https://api.cellphones.com.vn/v2/graphql/query', json={'query': query}, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
print(r.text)
