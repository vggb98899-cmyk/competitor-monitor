"""
38家Shopify店铺清单

字段说明：
  - name: 店铺名称（用于Excel报表）
  - url: 店铺首页URL
  - category: 主力品类
  - is_key: 是否主力店（True/False）
"""
STORES = [
    {"name": "Skims",               "url": "https://www.skims.com",               "category": "塑身内衣",   "is_key": True},
    {"name": "Allbirds",            "url": "https://www.allbirds.com",            "category": "环保鞋服",   "is_key": True},
    {"name": "Ruggable",            "url": "https://www.ruggable.com",            "category": "地毯",       "is_key": False},
    {"name": "Stanley 1913",        "url": "https://www.stanley1913.com",         "category": "保温杯",     "is_key": False},
    {"name": "Caraway Home",        "url": "https://www.carawayhome.com",         "category": "厨具",       "is_key": False},
    {"name": "From Our Place",      "url": "https://www.fromourplace.com",        "category": "厨具",       "is_key": False},
    {"name": "Cozy Earth",          "url": "https://www.cozyearth.com",           "category": "床品",       "is_key": False},
    {"name": "Gymshark",            "url": "https://www.gymshark.com",            "category": "运动服饰",   "is_key": True},
    {"name": "Alo Yoga",            "url": "https://www.aloyoga.com",             "category": "瑜伽服",     "is_key": False},
    {"name": "Fashion Nova",        "url": "https://www.fashionnova.com",         "category": "快时尚女装", "is_key": False},
    {"name": "Kylie Cosmetics",     "url": "https://www.kyliecosmetics.com",      "category": "美妆",       "is_key": False},
    {"name": "Jeffree Star",        "url": "https://www.jeffreestarcosmetics.com", "category": "美妆",       "is_key": False},
    {"name": "ColourPop",           "url": "https://www.colourpop.com",           "category": "美妆",       "is_key": False},
    {"name": "MVMT",                "url": "https://www.mvmt.com",                "category": "手表",       "is_key": False},
    {"name": "Chobani",             "url": "https://www.chobani.com",             "category": "健康食品",   "is_key": False},
    {"name": "Bombas",              "url": "https://www.bombas.com",              "category": "袜子",       "is_key": False},
    {"name": "Rothy's",             "url": "https://www.rothys.com",              "category": "平底鞋",     "is_key": False},
    {"name": "Outdoor Voices",      "url": "https://www.outdoorvoices.com",       "category": "运动女装",   "is_key": False},
    {"name": "Untuckit",            "url": "https://www.untuckit.com",            "category": "衬衫",       "is_key": False},
    {"name": "Brooklinen",          "url": "https://www.brooklinen.com",          "category": "床品",       "is_key": False},
    {"name": "Parachute Home",      "url": "https://www.parachutehome.com",       "category": "家居纺织品", "is_key": False},
    {"name": "Casper",              "url": "https://www.casper.com",              "category": "床垫",       "is_key": True},
    {"name": "Leesa",               "url": "https://www.leesa.com",               "category": "床垫",       "is_key": False},
    {"name": "Tuft & Needle",       "url": "https://www.tuftandneedle.com",       "category": "床垫",       "is_key": False},
    {"name": "Helix Sleep",         "url": "https://www.helixsleep.com",          "category": "床垫",       "is_key": False},
    {"name": "Nectar",              "url": "https://www.nectar.com",              "category": "床垫",       "is_key": False},
    {"name": "Purple",              "url": "https://www.purple.com",              "category": "床垫",       "is_key": True},
    {"name": "GhostBed",            "url": "https://www.ghostbed.com",            "category": "床垫",       "is_key": False},
    {"name": "Bear Mattress",       "url": "https://www.bearmattress.com",        "category": "床垫",       "is_key": False},
    {"name": "Amerisleep",          "url": "https://www.amerisleep.com",          "category": "床垫",       "is_key": False},
    {"name": "Saatva",              "url": "https://www.saatva.com",              "category": "床垫",       "is_key": False},
    {"name": "WinkBeds",            "url": "https://www.winkbeds.com",            "category": "床垫",       "is_key": False},
    {"name": "Avocado Sleep",       "url": "https://www.avocadosleep.com",        "category": "床垫",       "is_key": False},
    {"name": "PlushBeds",           "url": "https://www.plushbeds.com",           "category": "床垫",       "is_key": False},
    {"name": "Sleep Number",        "url": "https://www.sleepnumber.com",         "category": "智能床",     "is_key": True},
    {"name": "Tempur-Pedic",        "url": "https://www.tempurpedic.com",         "category": "床垫",       "is_key": False},
    {"name": "Sealy",               "url": "https://www.sealy.com",               "category": "床垫",       "is_key": False},
    {"name": "Simmons",             "url": "https://www.simmons.com",             "category": "床垫",       "is_key": False},
]
