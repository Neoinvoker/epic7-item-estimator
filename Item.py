class Item:
    item_type: str
    # 装备类型 例：英雄戒指
    level = 0
    # 物品强化等级 例：12
    score = 0
    # 装备分数 例： 34
    main_attribute: [str, str] = []
    # 主属性 例：["生命值", "305"]
    sub_attribute: [[str, str]] = []
    # 副属性 例：[["生命值", "105"], ["攻击力", "100"]]
    set_type: str
    # 套装属性 例： 速度套装

    def __init__(self, item_type, level, score, main_attribute, sub_attribute, set_type):
        self.main_attribute = main_attribute
        self.item_type = item_type
        self.level = level
        self.score = score
        self.sub_attribute = sub_attribute
        self.set_type = set_type
