# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QT_TRANSLATE_NOOP
import os, subprocess
from xml.dom import minidom
from datetime import datetime
from collections import OrderedDict

import i18n_rc

class LanguageChooser(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(LanguageChooser, self).__init__(parent, Qt.WindowStaysOnTopHint)

        self.qmFileForCheckBoxMap = {}
        self.mainWindowForCheckBoxMap = {} 

        groupBox = QtWidgets.QGroupBox("Languages")

        groupBoxLayout = QtWidgets.QGridLayout()

        qmFiles = self.findQmFiles()

        for i, qmf in enumerate(qmFiles):
            checkBox = QtWidgets.QCheckBox(self.languageName(qmf))
            self.qmFileForCheckBoxMap[checkBox] = qmf
            checkBox.toggled.connect(self.checkBoxToggled)
            groupBoxLayout.addWidget(checkBox, i / 2, i % 2)

        groupBox.setLayout(groupBoxLayout)

        buttonBox = QtWidgets.QDialogButtonBox()

        showAllButton = buttonBox.addButton("Show All",
                QtWidgets.QDialogButtonBox.ActionRole)
        hideAllButton = buttonBox.addButton("Hide All",
                QtWidgets.QDialogButtonBox.ActionRole)

        showAllButton.clicked.connect(self.showAll)
        hideAllButton.clicked.connect(self.hideAll)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(groupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("I18N")

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.Close:
            if isinstance(object, Ui_MainWindow):
                window = object

                for checkBox, w in self.mainWindowForCheckBoxMap.items():
                    if w is window:
                        break
                else:
                    checkBox = None

                if checkBox:
                    checkBox.setChecked(False)

        return QtWidgets.QWidget.eventFilter(self, object, event)

    def closeEvent(self, event):
        QtWidgets.QApplication.instance().quit()

    def checkBoxToggled(self):
        checkBox = self.sender()
        window = self.mainWindowForCheckBoxMap.get(checkBox)

        if not window:
            translator = QtCore.QTranslator()
            translator.load(self.qmFileForCheckBoxMap[checkBox])
            QtWidgets.QApplication.installTranslator(translator)

            # Because we will be installing an event filter for the main window
            # it is important that this instance isn't garbage collected before
            # the main window when the program terminates.  We ensure this by
            # making the main window a child of this one.
            window = Ui_MainWindow(self)
            window.setPalette(QtGui.QPalette(self.colorForLanguage(checkBox.text())))

            window.installEventFilter(self)
            self.mainWindowForCheckBoxMap[checkBox] = window

        window.setVisible(checkBox.isChecked())

    def showAll(self):
        for checkBox in self.qmFileForCheckBoxMap.keys():
            checkBox.setChecked(True)

    def hideAll(self):
        for checkBox in self.qmFileForCheckBoxMap.keys():
            checkBox.setChecked(False)

    def findQmFiles(self):
        trans_dir = QtCore.QDir(':/translations')
        fileNames = trans_dir.entryList(['*.qm'], QtCore.QDir.Files, QtCore.QDir.Name)

        return [trans_dir.filePath(fn) for fn in fileNames]

    def languageName(self, qmFile):
        translator = QtCore.QTranslator() 
        translator.load(qmFile)

        return translator.translate("MainWindow", "English")

    def colorForLanguage(self, language):
        hashValue = hash(language)
        red = 156 + (hashValue & 0x3F)
        green = 156 + ((hashValue >> 6) & 0x3F)
        blue = 156 + ((hashValue >> 12) & 0x3F)
        return QtGui.QColor(red, green, blue)


class LineEditWidget(QtWidgets.QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)
        # self.resize(200, 200)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            url = event.mimeData().urls()

            if url != [] and url[0].isLocalFile():
                link = str(url[0].toLocalFile())
                # else:
                #     links.append(str(url.toString()))
                self.clear()
                self.setText(link)
        else:
            event.ignore()

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Ui_MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.bookmark_file = None
        self.djvu_file = None

    def convert_btn_clicked(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)

        if self.bookmark_file != None and self.djvu_file != None:
            text_file = self.convert_xml_to_txt(self.bookmark_file)
            text_file = text_file.replace('/', '\\')
            self.djvu_file = self.djvu_file.replace('/', '\\')
            # os.system('djvused -e "set-outline %s" -s "%s"'%(text_file, self.djvu_file))
            # print('djvused -e "set-outline %s" -s "%s"'%(text_file, self.djvu_file))
            # result = subprocess.run(['djvused', '-e', '"set-outline %s"'%text_file, '-s', '"%s"'%self.djvu_file], stdout=subprocess.PIPE)
            result = subprocess.Popen('djvused -e "set-outline %s" -s "%s"'%(text_file, self.djvu_file), shell=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return_code = result.wait()
            # output, err = result.communicate()

            if return_code == 0:
                msg.setText("Закладки успешно экспортированы!")
            else:
                msg.setText("Произошла ошибка")

        else:
            msg.setText("Не выбран(-ы) файлы закладок/djvu")

        self.bookmark_file = None
        self.djvu_file = None

        self.lineEdit.setText("")
        self.lineEdit_2.setText("")

        msg.exec_()

    def convert_xml_to_txt(self, bookmark_file):
        doc = minidom.parse(bookmark_file)

        bookmarks = doc.getElementsByTagName('bookmarks')
        if bookmarks != []:
            bookmarks = bookmarks[0].getElementsByTagName('bookmark')

        pages_titles = {}
        result = "(bookmarks\n"
        for bookmark in bookmarks:
            title = bookmark.attributes['title'].value
            page = bookmark.attributes['page'].value
            pages_titles[page] = title

        sorted_pages_titles = OrderedDict(sorted(pages_titles.items()))
        for page, title in sorted_pages_titles.items():
            result += '("' + title + '" "#' + page + '")\n'

        result += ")"

        dt = datetime.today()  # Get timezone naive now
        seconds = dt.timestamp()
        file = open("bmk" + str(seconds) + '.txt', 'w')
        file.write(result)
        file.close()

        text_file = "bmk" + str(seconds) + '.txt'

        return text_file

    def bookmark_btn_clicked(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilters({"Bookmarks (*.bookmarks)"})
            
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.bookmark_file = filenames[0]
            self.lineEdit.setText(self.bookmark_file)

    def djvu_btn_clicked(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilters({"Djvu (*.djvu)"})
            
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            f = open(filenames[0], 'r')
            self.djvu_file = filenames[0]
            self.lineEdit_2.setText(self.djvu_file)

    def setupUi(self, MainWindow):
        font = QtGui.QFont()
        font.setPointSize(12)
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(500, 400)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel()
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.bookmark_btn = QtWidgets.QPushButton()
        self.bookmark_btn.setObjectName("bookmark_btn")
        self.bookmark_btn.setFont(font)
        self.bookmark_btn.clicked.connect(self.bookmark_btn_clicked)

        self.gridLayout.addWidget(self.bookmark_btn, 0, 2, 1, 1)
        self.djvu_btn = QtWidgets.QPushButton()
        self.djvu_btn.setObjectName("djvu_btn")
        self.djvu_btn.setFont(font)
        self.djvu_btn.clicked.connect(self.djvu_btn_clicked)
        self.gridLayout.addWidget(self.djvu_btn, 1, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel()
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.lineEdit_2 = LineEditWidget(self)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setReadOnly(True)
        self.lineEdit_2.setPlaceholderText("или перетащите файл сюда")
        self.lineEdit_2.setFont(font)
        self.gridLayout.addWidget(self.lineEdit_2, 1, 1, 1, 1)

        self.convert_btn = QtWidgets.QPushButton()
        self.convert_btn.setObjectName("convert_btn")
        self.convert_btn.setFont(font)
        self.convert_btn.clicked.connect(self.convert_btn_clicked)
        self.gridLayout.addWidget(self.convert_btn, 2, 1, 1, 1)

        self.lineEdit = LineEditWidget(self)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setPlaceholderText("или перетащите файл сюда")
        self.lineEdit.setFont(font)
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)

        self.centralwidget.setLayout(self.gridLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Встраиватель закладок WinDjView в документы DjVu и PDF"))
        self.bookmark_btn.setText(_translate("MainWindow", "Файл закладок"))
        self.djvu_btn.setText(_translate("MainWindow", "Файл DJVU"))
        self.convert_btn.setText(self.tr("Perspective"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # MainWindow = QtWidgets.QMainWindow()
    # ui = Ui_MainWindow()
    # ui.show()

    chooser = LanguageChooser()
    chooser.show()
    sys.exit(app.exec_())
