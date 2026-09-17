import json

def main():
    print("Reading thns_raw_all.json...")
    with open('thns_raw_all.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    products = data.get('products', data) if isinstance(data, dict) else data
    
    # Filter products where handle contains 'card-man-hinh'
    filtered_products = [
        p for p in products 
        if 'card-man-hinh' in p.get('handle', '').lower()
    ]
    
    output_file = 'thns_vga_filtered.json'
    print(f"Found {len(filtered_products)} products matching handle 'card-man-hinh'.")
    print(f"Writing to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_products, f, ensure_ascii=False, indent=2)
        
    print("Done!")

if __name__ == '__main__':
    main()
