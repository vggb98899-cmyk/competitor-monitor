"""读取eBay数据并整合到日报"""
import json
from pathlib import Path

def load_ebay_data():
    """读取ebay采集结果"""
    filepath = Path(__file__).parent / "output" / "ebay_products.json"
    if not filepath.exists():
        return []
    
    with open(filepath, "r", encoding="utf-8") as f:
        stores = json.load(f)
    
    result = []
    for store in stores:
        for p in store.get("products", []):
            price = p.get("price", "").replace("$", "").strip()
            result.append({
                "title": p.get("title", ""),
                "price": price,
                "category": "户外装备",
                "status": "在售",
                "store": f"eBay-{store['store']}",
                "rating": "",
                "handle": "",
            })
    return result
