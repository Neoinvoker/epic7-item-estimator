import cv2
from PIL import Image, ImageFilter
from adbutils import AdbDevice
from Item import Item
from ADBManager import ADBManager
from ImageUtils import ImgUtils


class WrongItemException(Exception):
    def __init__(self, e):
        super().__init__(self)
        self.e = e

    def __str__(self):
        return self.e


class Estimator:
    # 默认使用雷电模拟器的ADB端口
    screenshot: Image
    address: str = ""
    device: AdbDevice
    adbManager = ADBManager()
    # 截图的位置
    pos = [((417, 309), (510, 345)),
           ((581, 304), (664, 350)),  # 主词条
           ((390, 365), (470, 390)),
           ((600, 365), (660, 390)),  # 1
           ((390, 385), (470, 410)),
           ((600, 385), (660, 410)),  # 2
           ((390, 410), (470, 435)),
           ((600, 410), (660, 435)),  # 3
           ((390, 435), (470, 460)),
           ((600, 435), (660, 460)),  # 4
           ((390, 475), (470, 500)),
           ((620, 475), (660, 500)),  # 装备分数
           ((425, 515), (510, 540))]
    # 评估结果，下标从0到3对应价值从低到高，文字内容比较抽象，下标4表示尚未强化完毕
    result = ["请直接丢进垃圾桶，狗都不要", "吃剩的，给小弟咂么个味儿行了", "凑合能用，值得重铸",
              "有这运气你玩游戏不买彩票？", "有潜力继续强化", "凑合用，但不值得重铸"]

    def __init__(self, address: str):
        self.address = address
        self.device = self.adbManager.connect(address=self.address)

    # threshold 用于设置截图的二值化阈值，取值范围0-255  对装备词条识别设置成105效果比较好，默认就设成105了
    def readPicture(self, top_left, bottom_right, threshold=105):
        # 截取矩形框内的图像
        cropped_image = self.screenshot[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

        # 保存截取的图像
        cv2.imwrite(f'cropped_image.png', cropped_image)
        cropped_image = Image.open(f'cropped_image.png').convert('L')
        img = cropped_image.point(lambda x: 0 if x > threshold else 255, '1').filter(ImageFilter.EDGE_ENHANCE_MORE)
        try:
            text = ImgUtils.img2str(img)
        except BaseException as e:
            raise e
        return text.replace('\f', '')

    def getItem(self):
        screenshot = ImgUtils.screenshot(self.device)
        screenshot.save("screenshot.png")
        self.screenshot = ImgUtils.readImg("screenshot.png")
        item_type = ""
        path = [("传说项链", "./resource/img/red_amulet.png"), ("传说戒指", "./resource/img/red_ring.png"),
                ("传说护甲", "./resource/img/red_armor.png"), ("传说鞋子", "./resource/img/red_boots.png"),
                ("传说武器", "./resource/img/red_weapon.png"), ("传说头盔", "./resource/img/red_helmet.png"),
                ("英雄项链", "./resource/img/purple_amulet.png"), ("英雄戒指", "./resource/img/purple_ring.png"),
                ("英雄头盔", "./resource/img/purple_helmet.png"), ("英雄鞋子", "./resource/img/purple_boots.png"),
                ("英雄护甲", "./resource/img/purple_armor.png"), ("英雄武器", "./resource/img/purple_weapon.png")]
        flag = False
        for it in path:
            img = ImgUtils.readImg(it[1])
            result = ImgUtils.check(self.screenshot, img)
            if result:
                flag = True
                item_type = it[0]
                break
        if not flag:
            raise WrongItemException("未识别到英雄/传说装备")
        # 紫左三
        level = 0
        sub_attribute: [[str, str]] = []

        main_attribute = [self.readPicture(self.pos[0][0], self.pos[0][1]),
                          self.readPicture(self.pos[1][0], self.pos[1][1])]
        i = 2
        while i < 10:
            buf = [self.readPicture(self.pos[i][0], self.pos[i][1]),
                   self.readPicture(self.pos[i + 1][0], self.pos[i + 1][1])]
            if not buf[0] == "":
                sub_attribute.append(buf)
            else:
                i = 10
                break
            i = i + 2

        score = int(self.readPicture(self.pos[i + 1][0], self.pos[i + 1][1]))
        set_type = self.readPicture(self.pos[i + 2][0], self.pos[i + 2][1])
        lvl = self.readPicture((445, 100), (500, 135), 180).replace("+", "")
        if '+' in lvl:
            level = int(lvl)
        else:
            level = 0
        # 等级的识别 二值化阈值设为180（等级区域的颜色为橙色）

        item = Item(item_type, level, score, main_attribute, sub_attribute, set_type)
        return item

    def estimate(self, item: Item):
        # item_flag用于标注左右三件和红紫信息 0：红左 1：红右 2：紫左 3：紫右 99: 初始值（如果没变就说明有bug）
        item_flag = 99
        # 评估结果，下标从0到3对应价值从低到高，文字内容比较抽象，下标4表示尚未强化完毕
        # result = [0 "请直接丢进垃圾桶，狗都不要", 1 "吃剩的，给小弟咂么个味儿行了", 2 "凑合能用，值得重铸",
        #          3 "有这运气你玩游戏不买彩票？", 4 "有潜力继续强化",5 "凑合用，但不值得重铸"]

        if "英雄" in item.item_type:
            bias = 0
        else:
            bias = 2
        if "戒指" in item.item_type or "项链" in item.item_type or "鞋子" in item.item_type:
            item_flag = 3
            if "攻击力" in item.main_attribute[0] or "防御力" in item.main_attribute[0] or \
                    "生命值" in item.main_attribute[0] and not ("%" in item.main_attribute[1]):
                return self.result[0]
            else:
                if item.level < 6:
                    if item.score < 18 + item.level + bias:
                        return self.result[0]
                    else:
                        return self.result[4]
                elif item.level < 9:
                    if item.score < 32 + item.level - 6:
                        return self.result[0]
                    else:
                        return self.result[4]
                elif item.level < 12:
                    if item.score < 38 + item.level - 9:
                        return self.result[0]
                    else:
                        return self.result[4]
                elif item.level < 15:
                    if item.score < 44 + item.level - 12:
                        return self.result[1]
                    else:
                        return self.result[4]
                else:
                    if item.score < 50:
                        return self.result[1]
                    elif item.score < 63:
                        return self.result[2]
                    else:
                        return self.result[3]

        else:
            item_flag = 2
            if item.level < 6:
                if item.score < 20 + item.level + bias:
                    for pair in item.sub_attribute:
                        if "速度" in pair[0]:
                            if int(pair[1]) >= 4:
                                return self.result[4]
                            else:
                                return self.result[0]
                        else:
                            return self.result[0]
                else:
                    return self.result[4]
            elif item.level < 9:
                if item.score < 34 + item.level:
                    for pair in item.sub_attribute:
                        if "速度" in pair[0]:
                            if int(pair[1]) >= 10:
                                return self.result[4]
                            else:
                                return self.result[0]
                        else:
                            return self.result[0]
                else:
                    return self.result[4]
            elif item.level < 12:
                if item.score < 40 + item.level:
                    for pair in item.sub_attribute:
                        if "速度" in pair[0]:
                            if int(pair[1]) >= 10:
                                return self.result[4]
                            else:
                                return self.result[0]
                        else:
                            return self.result[0]
                else:
                    return self.result[4]
            elif item.level < 15:
                if item.score < 46 + item.level:
                    for pair in item.sub_attribute:
                        if "速度" in pair[0]:
                            if int(pair[1]) >= 15:
                                return self.result[4]
                            elif item.score < 40 + item.level:
                                return self.result[1]
                            elif item.score >= 46 + item.level:
                                return self.result[4]
                            else:
                                return self.result[5]
                        else:
                            return self.result[1]
                else:
                    return self.result[4]
            else:
                if item.score < 52:
                    for pair in item.sub_attribute:
                        if "速度" in pair[0]:
                            if int(pair[1]) >= 20:
                                return self.result[3]
                            elif int(pair[1]) >= 15:
                                return self.result[2]
                            else:
                                return self.result[5]
                        else:
                            return self.result[1]
                elif item.score < 65:
                    for pair in item.sub_attribute:
                        if "速度" in pair[0]:
                            if int(pair[1]) >= 20:
                                return self.result[3]
                            elif int(pair[1]) >= 15:
                                return self.result[2]
                            else:
                                return self.result[5]
                        else:
                            return self.result[2]
                else:
                    return self.result[3]
