"""
竞品店铺清单

字段说明：
  - name: 店铺名称
  - url: 店铺首页URL
  - category: 主力品类
  - tier: core（主力）/ watch（观察）/ pending（待接入）
"""
STORES = [
    # ─── 主力（core）───
    {"name": "Naturehike",           "url": "https://www.naturehike.com",           "category": "户外装备",     "tier": "core"},
    {"name": "凯乐石",               "url": "https://kailasgear.com",               "category": "户外服装鞋类", "tier": "core"},
    {"name": "Gossamer Gear",        "url": "https://www.gossamergear.com",         "category": "超轻户外装备", "tier": "core"},
    {"name": "Cotopaxi",             "url": "https://www.cotopaxi.com",             "category": "户外背包服装", "tier": "core"},
    {"name": "Black Diamond",        "url": "https://www.blackdiamondequipment.com","category": "攀岩装备",     "tier": "core"},

    # ─── 观察（watch）───
    {"name": "Ruffwear",             "url": "https://www.ruffwear.com",             "category": "宠物户外装备", "tier": "watch"},
    {"name": "Jackery",              "url": "https://www.jackery.com",              "category": "户外电源",     "tier": "watch"},
    {"name": "Yoeleo",               "url": "https://www.yoeleo.com",               "category": "自行车配件",   "tier": "watch"},
]

# 待接入（WAF防护过不去，等条件成熟）
PENDING_STORES = [
    {"name": "Snow Peak",            "url": "https://www.snowpeak.com",             "category": "户外装备",     "tier": "pending"},
    {"name": "Zpacks",               "url": "https://www.zpacks.com",               "category": "户外背包",     "tier": "pending"},
]
