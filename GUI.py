import os

import pytesseract
from adbutils import errors
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout

from Estimator import Estimator, WrongItemException


class E7ItemEstimator(QWidget):
    emitLog = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.adb_connected = False
        self.connect_button = QPushButton("连接ADB")
        self.adb_port = QLineEdit()
        self.item_type = QLineEdit()
        self.item_type.setReadOnly(True)
        self.level = QLineEdit()
        self.level.setReadOnly(True)
        self.main_attribute = QLineEdit()
        self.main_attribute.setReadOnly(True)
        self.main_attribute_value = QLineEdit()
        self.main_attribute_value.setReadOnly(True)
        self.sub_attribute = []
        self.sub_attribute_value = []
        self.score = QLineEdit()
        self.score.setReadOnly(True)
        self.set_type = QLineEdit()
        self.set_type.setReadOnly(True)
        self.evaluation = QLineEdit()
        self.evaluation.setReadOnly(True)
        self.prompt = QtWidgets.QPlainTextEdit()
        self.prompt.setReadOnly(True)  # 设置为只读模式
        self.estimate_button = QPushButton("计算")
        self.estimate_button.clicked.connect(self.update_ui)
        # 连接emitLog信号和update_prompt槽函数
        self.emitLog.connect(self.update_prompt)
        self.init_ui()

    def init_ui(self):

        main_layout = QVBoxLayout()

        form_layout = QFormLayout()
        form_layout.addRow("装备类型:", self.item_type)
        form_layout.addRow("强化等级:", self.level)

        main_attribute_layout = QHBoxLayout()
        main_attribute_layout.addWidget(QLabel(" 主属性:"))
        main_attribute_layout.addWidget(self.main_attribute)
        main_attribute_layout.addWidget(QLabel("数值:"))
        main_attribute_layout.addWidget(self.main_attribute_value)
        form_layout.addRow(main_attribute_layout)

        for i in range(4):
            sub_attribute = QLineEdit()
            sub_attribute.setReadOnly(True)
            sub_attribute_value = QLineEdit()
            sub_attribute_value.setReadOnly(True)
            self.sub_attribute.append(sub_attribute)
            self.sub_attribute_value.append(sub_attribute_value)
            sub_attribute_layout = QHBoxLayout()
            sub_attribute_layout.addWidget(QLabel(f"子属性{i + 1}:"))
            sub_attribute_layout.addWidget(sub_attribute)
            sub_attribute_layout.addWidget(QLabel("数值:"))
            sub_attribute_layout.addWidget(sub_attribute_value)
            form_layout.addRow(sub_attribute_layout)

        set_layout = QHBoxLayout()
        set_layout.addWidget(QLabel("装备分数:"))
        set_layout.addWidget(self.score)
        set_layout.addWidget(QLabel("套装类型:"))
        set_layout.addWidget(self.set_type)
        form_layout.addRow(set_layout)

        main_layout.addLayout(form_layout)

        estimate_layout = QHBoxLayout()
        estimate_layout.addWidget(QLabel("评估结果:"))
        estimate_layout.addWidget(self.evaluation)
        main_layout.addLayout(estimate_layout)

        main_layout.addWidget(QLabel("提示信息:"))
        main_layout.addWidget(self.prompt)

        main_layout.addWidget(self.estimate_button, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(QLabel("ADB端口号:"))
        main_layout.addWidget(self.adb_port)
        self.connect_button.clicked.connect(self.connect_adb)
        main_layout.addWidget(self.connect_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

    def connect_adb(self):
        # 读取 Tesseract 路径
        tesseract_path_file = os.path.join(os.getcwd(), "tesseract_path.txt")
        with open(tesseract_path_file, "r") as f:
            tesseract_path = f.read().strip()

        # 设置 Tesseract 路径
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

        adb_port = self.adb_port.text()
        try:
            self.estimator = Estimator(adb_port)
            self.adb_connected = True
        except errors.AdbError as e:
            self.adb_connected = False
            self.emitLog.emit(str(e))

        if self.adb_connected:
            QtWidgets.QMessageBox.information(self, "连接成功", "ADB 连接成功！")
            self.emitLog.emit("ADB 连接成功！")
        else:
            QtWidgets.QMessageBox.warning(self, "连接失败", "ADB 连接失败！ 请重试！")
            self.emitLog.emit("ADB 连接失败！ 请重试！")

    def update_ui(self):
        if not self.adb_connected:
            QtWidgets.QMessageBox.information(self, "警告", "请先连接ADB！")
            return
        # 获取item对象
        try:
            item = self.estimator.getItem()
        except WrongItemException as e:
            self.emitLog.emit(str(e))
            return
        result = self.estimator.estimate(item)
        # 更新UI界面中的各个控件内容
        self.item_type.setText(item.item_type)
        self.level.setText(str(item.level))
        self.main_attribute.setText(item.main_attribute[0])
        self.main_attribute_value.setText(str(item.main_attribute[1]))
        for i in range(len(item.sub_attribute)):
            self.sub_attribute[i].setText(item.sub_attribute[i][0])
            self.sub_attribute_value[i].setText(str(item.sub_attribute[i][1]))
        self.score.setText(str(item.score))
        self.set_type.setText(item.set_type)
        self.evaluation.setText(result)

    def update_prompt(self, message):
        self.prompt.appendPlainText(message)  # 使用appendPlainText方法追加文本


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setCentralWidget(E7ItemEstimator())
        self.setWindowTitle("第七史诗装备强化计算器 v0.1-alpha")
        self.setWindowIcon(QIcon('./resource/img/main.ico'))
