"""
竞品店铺清单

字段说明：
  - name: 店铺名称
  - url: 店铺首页URL
  - category: 主力品类
  - is_key: 是否主力店
"""
STORES = [
    {"name": "Naturehike",    "url": "https://www.naturehike.com",     "category": "户外装备",     "is_key": True},
    {"name": "Snow Peak",     "url": "https://www.snowpeak.com",       "category": "户外装备",     "is_key": True},
    {"name": "凯乐石",        "url": "https://kailasgear.com",         "category": "户外装备",     "is_key": True},
    {"name": "Zpacks",        "url": "https://www.zpacks.com",         "category": "户外背包",     "is_key": False},
    {"name": "Gossamer Gear", "url": "https://www.gossamergear.com",   "category": "超轻户外装备", "is_key": False},
    {"name": "Ruffwear",      "url": "https://www.ruffwear.com",       "category": "宠物户外装备", "is_key": False},
    {"name": "Jackery",       "url": "https://www.jackery.com",        "category": "户外电源",     "is_key": False},
    {"name": "Yoeleo",        "url": "https://www.yoeleo.com",         "category": "自行车配件",   "is_key": False},
]
