# -*- coding: utf-8 -*-

import sys
sys.path.append('/Users/jubilee/Projects/screenshot-app/venv/lib/python3.11/site-packages')

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QLabel, QPushButton, QGroupBox, QWidget, QScrollArea, QVBoxLayout, QTextEdit, QHBoxLayout, QGridLayout
from PIL import ImageGrab
import sys
import cv2
import numpy as np
# import imageToString
import pyperclip
import webbrowser
import pytesseract
import pyscreenshot
import xpinyin
from xpinyin import Pinyin
import transliterate
from transliterate import translit
import pykakasi
import pygame
import googletrans
from googletrans import Translator


class MyWindow(QMainWindow):

    langCodes = ['jpn', 'chi_sim', 'chi_tra', 'rus', 'fra', 'eng']
    languages = ["Japanese", "Chinese (Simplified)", "Chinese (Traditional)", "Russian", "French", "English"]
    googleTransLangs = ['ja', 'zh-CN', 'zh-TW', 'ru', 'fr', 'en']
    set_content = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MyWindow, self).__init__()
        self.win_width = 340
        self.win_height = 200
        self.setGeometry(50, 50, self.win_width, self.win_height)
        self.inputLangCode = 'jpn'
        self.targetLangCode = 'jpn'
        self.translationMode = True
        self.set_content.connect(self.onChangeContent)
        self.wid = QtWidgets.QWidget(self)
        self.setCentralWidget(self.wid)
        self.initUI()
        
        
    def initUI(self):
        langSelectBox = QGroupBox()
        snipSelectBox = QGroupBox()
        langSelectHBox = QHBoxLayout()
        snipSelectHBox = QHBoxLayout()

        self.inputLangSelect = QComboBox(self)
        for language in self.languages:
            self.inputLangSelect.addItem(language)
        # self.inputLangSelect.setFixedSize(int(self.win_width/2), 20)
        self.search_browser = self.inputLangSelect.currentText()
        self.inputLangSelect.activated[str].connect(self.onChangeInputLang)

        self.targetLangSelect = QComboBox(self)
        for language in self.languages:
            self.targetLangSelect.addItem(language)
        # self.targetLangSelect.setFixedSize(int(self.win_width/2), 20)
        self.search_browser = self.targetLangSelect.currentText()
        self.targetLangSelect.activated[str].connect(self.onChangeTargetLang)

        #Define buttons
        # self.searchBtn = QPushButton(self)
        # self.searchBtn.setText("Snip and Search")
        # self.searchBtn.setFixedSize(150,40)
        # self.searchBtn.clicked.connect(lambda: self.snip_clicked(True))
        
        self.copyBtn = QPushButton(self)
        self.copyBtn.setText("Snip And Copy")
        self.copyBtn.setFixedSize(150,40)
        self.copyBtn.clicked.connect(lambda: self.snip_clicked(False))

        self.arrow = QLabel(self)
        self.arrow.setText(u"\u2192")
        self.arrow.adjustSize()

        self.toggleTranslationCheckbox = QtWidgets.QCheckBox(self)
        self.toggleTranslationCheckbox.setText("Translate Text")
        self.toggleTranslationCheckbox.setChecked(True)
        self.toggleTranslationCheckbox.stateChanged.connect(self.onToggleTranslation)

        self.textBox = QTextEdit(self)
        self.inputReading = QTextEdit(self)
        self.textBox.textChanged.connect(self.onTextChanged)

        self.translationWidget = QWidget(self)
        self.translationReading = QTextEdit(self)
        self.translation = QTextEdit(self)

        self.inputReading.setPlaceholderText("Reading")
        self.translation.setPlaceholderText("Translation")

        self.inputReading.setReadOnly(True)
        self.translationReading.setReadOnly(True)
        self.translation.setReadOnly(True)

        langSelectHBox.addWidget(self.inputLangSelect)
        langSelectHBox.addWidget(self.arrow)
        langSelectHBox.addWidget(self.targetLangSelect)
        langSelectBox.setLayout(langSelectHBox)

        # snipSelectHBox.addWidget(self.searchBtn)
        snipSelectHBox.addWidget(self.copyBtn)
        snipSelectBox.setLayout(snipSelectHBox)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(langSelectBox)
        windowLayout.addWidget(snipSelectBox)
        windowLayout.addWidget(self.toggleTranslationCheckbox)
        windowLayout.addWidget(self.textBox)
        windowLayout.addWidget(self.inputReading)
        windowLayout.addWidget(self.translation)
        windowLayout.addWidget(self.translationReading)

        # self.translationLayout = QVBoxLayout()
        # self.translationLayout.addWidget(self.translation)
        # self.translationLayout.addWidget(self.translationReading)
        # self.translationWidget.setLayout(self.translationLayout)
        # windowLayout.addWidget(self.translationWidget)

        self.wid.setLayout(windowLayout)

        self.reset_content()

    def snip_clicked(self, search):
        search = search
        copy = not search
        self.snipWin = SnipWidget(copy, search, self.search_browser, self)

    def onToggleTranslation(self):
        self.translationMode = not self.translationMode
        self.translationWidget.setVisible(self.translationMode)
        self.targetLangSelect.setVisible(self.translationMode)
        self.arrow.setVisible(self.translationMode)
        self.translation.setVisible(self.translationMode)
        self.translationReading.setVisible(self.translationMode)
        self.changeOutput(self.textBox.toPlainText())
    
    def onTextChanged(self):
        text = self.textBox.toPlainText()
        self.changeOutput(text)

    def onChangeInputLang(self):
        index = self.languages.index(self.inputLangSelect.currentText())
        self.inputLangCode = self.langCodes[index]
        text = self.textBox.toPlainText()
        if text:
            self.changeOutput(text)

    def onChangeTargetLang(self):
        index = self.languages.index(self.targetLangSelect.currentText())
        self.targetLangCode = self.langCodes[index]
        text = self.textBox.toPlainText()
        if text:
            self.changeOutput(text)

    def onChangeContent(self, text):
        self.textBox.setText(text)
        self.changeOutput(text)

    def changeOutput(self, text):
        translator = Translator()
        src_index = self.langCodes.index(self.inputLangCode)
        dest_index = self.langCodes.index(self.targetLangCode)

        self.inputReading.setText(get_reading(text, self.inputLangCode))
        if self.translationMode and text:
            self.translation.setText(translator.translate(text, 
                src=self.googleTransLangs[src_index], dest=self.googleTransLangs[dest_index]).text)
            self.translationReading.setText(get_reading(self.translation.toPlainText(), self.targetLangCode))

    def reset_content(self):
        # print(self.wid.palette().color(QtGui.QPalette.Background).name())
        self.inputReading.setStyleSheet("background-color: #ececec; padding: 5px;"); 
        self.translationReading.setStyleSheet("background-color: #ececec; padding: 5px;"); 
        self.translation.setStyleSheet("background-color: #ececec; padding: 5px;"); 


class SnipWidget(QMainWindow):
    
    exit_signal = pyqtSignal()
    snip_saved = pyqtSignal()
    # pinyin = Pinyin()
    
    def __init__(self, copy, search, search_browser, parent):
        super().__init__()
        self.search = search
        self.copy = copy
        self.parent = parent
        self.search_browser = search_browser

        desktopSize = QApplication.desktop().screenGeometry()
        screen_height = desktopSize.height()
        screen_width = desktopSize.width()
        self.setGeometry(0, 0, screen_width, screen_height)

        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.is_snipping = False
        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(QtCore.Qt.CrossCursor)
        )
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.snip_saved.connect(self.processImg)

        self.show()


    def paintEvent(self, event):
        if self.is_snipping:
            brush_color = (0, 0, 0, 0)
            lw = 0
            opacity = 0
        else:
            brush_color = (128, 128, 255, 128)
            lw = 1
            opacity = 0.3

        self.setWindowOpacity(opacity)
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('black'), lw))
        qp.setBrush(QtGui.QColor(*brush_color))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            print('Quit')
            QtWidgets.QApplication.restoreOverrideCursor();
            self.exit_signal.emit()
            self.close()
        event.accept()

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())
        self.is_snipping = True        
        self.repaint()
        QtWidgets.QApplication.processEvents()
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2), include_layered_windows=False, all_screens=True)
        self.is_snipping = False
        self.repaint()
        QtWidgets.QApplication.processEvents()
        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
        self.snipped_image = img
        # cv2.imshow('image',img)
        QtWidgets.QApplication.restoreOverrideCursor();
        self.snip_saved.emit()
        self.close()
        self.msg = 'snip complete'
        self.exit_signal.emit()
        
    def processImg(self):
        img = self.snipped_image
        text = self.get_text(img)
        if self.search:
            self.openTab(text)
        elif self.copy:
            pyperclip.copy(text)
        self.parent.set_content.emit(text)
       
    def get_text(self, img):
        # cv2.imshow('image',img)
        text = pytesseract.image_to_string(img, lang=self.parent.inputLangCode)
        text = text.strip()
        return text
    
    def openTab(self, text):
        url = "https://www.google.com.tr/search?q={}".format(text)
        mozilla_path = 'C:/Program Files/Mozilla Firefox/firefox.exe %s'
        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
        
        if self.search_browser == 'Chrome':
            browser_path = chrome_path
            webbrowser.get(browser_path).open(url, new=1)
        elif self.search_browser == 'Mozilla':
            browser_path = mozilla_path
            webbrowser.get(browser_path).open(url, new=1)
        else: 
            browser_path = chrome_path
            webbrowser.open(url, new=1)

def get_reading(text, lang):
    reading = ''
    # lang = self.parent.inputLangCode
    pinyin = Pinyin()
    if(lang == 'chi_sim' or lang == 'chi_tra'):
        reading = pinyin.get_pinyin(text, tone_marks='marks')
    elif(lang == 'jpn'):
        result = pykakasi.kakasi().convert(text)
        reading = ""
        for item in result:
            reading += item['hira']
    elif(lang == 'rus'):
        reading = translit(text, reversed=True)

    return reading

        

def window():
    app = QApplication(sys.argv)
    
    win = MyWindow()
    win.show()
    
    sys.exit(app.exec_())
    
window()