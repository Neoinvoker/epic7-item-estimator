import aircv
from adbutils import AdbDevice
import pytesseract


class ImgUtils:

    @staticmethod
    def screenshot(device: AdbDevice):
        return device.screenshot()

    @staticmethod
    def check(img1, img2):
        return aircv.find_template(img1, img2, 0.9)

    @staticmethod
    def readImg(path):
        return aircv.imread(path)

    @staticmethod
    def img2str(img):
        return pytesseract.image_to_string(img, lang='E7', config='--dpi 96 --psm 8 --user-words item_vocabulary.txt')

    @staticmethod
    def img2num(img):
        return pytesseract.image_to_data(img)
