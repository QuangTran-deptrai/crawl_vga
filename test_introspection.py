import httpx
query = """
query {
    __type(name: "ProductGeneral") {
        name
        fields {
            name
            type {
                name
                kind
            }
        }
    }
}
"""
r = httpx.post('https://api.cellphones.com.vn/v2/graphql/query', json={'query': query}, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
print(r.text)
