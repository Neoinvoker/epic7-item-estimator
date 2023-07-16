# Epic7-Item-Estimator

目前还是测试状态 不稳定 谨慎使用  当前仅支持模拟器

需要停留在刚刚点击装备的界面来识别，因为识别的位置是写死的

用了Tesseract的模型来做OCR，需要把E7.traineddata文件放进TesseractOCR\tessdata目录下，安装Tesseract依赖后会自动下载这个TesseractOCR，找到这个路径放进去就可以了

需要先连接ADB再使用，先再模拟器的根目录下打开控制台 输入adb.exe kill-server
再输入 adb.exe devices
然后打开模拟器，同时确保模拟器开启了adb调试功能，不同模拟器开启的位置自行百度
不同模拟器adb端口不同 雷电模拟器端口为5555
即在adb端口框内输入 127.0.0.1:5555来连接
mumu的应该是7555
其他的自行百度

模拟器分辨率设置为：宽 720 长 1280 DPI 320

针对编程小白的友好化处理正在进行 个人开发 时间有限 缓慢更新
