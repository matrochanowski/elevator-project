# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'config.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHeaderView, QLabel,
    QMainWindow, QMenuBar, QPushButton, QRadioButton,
    QSizePolicy, QSlider, QSpinBox, QStackedWidget,
    QStatusBar, QTableWidget, QTableWidgetItem, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setGeometry(QRect(30, 30, 721, 491))
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.startButton = QPushButton(self.page)
        self.startButton.setObjectName(u"startButton")
        self.startButton.setGeometry(QRect(280, 350, 91, 41))
        self.settingsButton = QPushButton(self.page)
        self.settingsButton.setObjectName(u"settingsButton")
        self.settingsButton.setGeometry(QRect(520, 350, 101, 41))
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.SaveButton = QPushButton(self.page_2)
        self.SaveButton.setObjectName(u"SaveButton")
        self.SaveButton.setGeometry(QRect(470, 440, 101, 41))
        self.MenuButton = QPushButton(self.page_2)
        self.MenuButton.setObjectName(u"MenuButton")
        self.MenuButton.setGeometry(QRect(210, 440, 101, 41))
        self.FloorsSpinBox = QSpinBox(self.page_2)
        self.FloorsSpinBox.setObjectName(u"FloorsSpinBox")
        self.FloorsSpinBox.setGeometry(QRect(70, 50, 81, 31))
        self.FloorsSpinBox.setMinimum(2)
        self.FloorsSpinBox.setMaximum(20)
        self.FloorsSpinBox.setValue(5)
        self.label = QLabel(self.page_2)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(70, 30, 101, 16))
        self.StepsHorizontalSlider = QSlider(self.page_2)
        self.StepsHorizontalSlider.setObjectName(u"StepsHorizontalSlider")
        self.StepsHorizontalSlider.setGeometry(QRect(70, 120, 261, 18))
        self.StepsHorizontalSlider.setMinimumSize(QSize(160, 0))
        self.StepsHorizontalSlider.setMinimum(100)
        self.StepsHorizontalSlider.setMaximum(10000)
        self.StepsHorizontalSlider.setSliderPosition(1000)
        self.StepsHorizontalSlider.setOrientation(Qt.Orientation.Horizontal)
        self.label_2 = QLabel(self.page_2)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(70, 100, 101, 16))
        self.MaxPeopleFloorSpinBox = QSpinBox(self.page_2)
        self.MaxPeopleFloorSpinBox.setObjectName(u"MaxPeopleFloorSpinBox")
        self.MaxPeopleFloorSpinBox.setGeometry(QRect(70, 170, 81, 31))
        self.label_3 = QLabel(self.page_2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(70, 150, 221, 16))
        self.VisualisationRadioButton = QRadioButton(self.page_2)
        self.VisualisationRadioButton.setObjectName(u"VisualisationRadioButton")
        self.VisualisationRadioButton.setGeometry(QRect(70, 220, 92, 20))
        self.ElevatorTable = QTableWidget(self.page_2)
        if (self.ElevatorTable.columnCount() < 3):
            self.ElevatorTable.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.ElevatorTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.ElevatorTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.ElevatorTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.ElevatorTable.setObjectName(u"ElevatorTable")
        self.ElevatorTable.setGeometry(QRect(370, 120, 301, 181))
        self.ElevatorsSpinBox = QSpinBox(self.page_2)
        self.ElevatorsSpinBox.setObjectName(u"ElevatorsSpinBox")
        self.ElevatorsSpinBox.setGeometry(QRect(370, 50, 71, 31))
        self.ElevatorsSpinBox.setMinimum(1)
        self.ElevatorsSpinBox.setMaximum(8)
        self.ElevatorsSpinBox.setValue(2)
        self.label_4 = QLabel(self.page_2)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(370, 30, 121, 16))
        self.AlgorithmComboBox = QComboBox(self.page_2)
        self.AlgorithmComboBox.setObjectName(u"AlgorithmComboBox")
        self.AlgorithmComboBox.setGeometry(QRect(70, 270, 161, 24))
        self.label_5 = QLabel(self.page_2)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(70, 250, 221, 16))
        self.label_6 = QLabel(self.page_2)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(70, 300, 221, 16))
        self.ModelComboBox = QComboBox(self.page_2)
        self.ModelComboBox.setObjectName(u"ModelComboBox")
        self.ModelComboBox.setGeometry(QRect(70, 320, 161, 24))
        self.stackedWidget.addWidget(self.page_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.startButton.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.settingsButton.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.SaveButton.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.MenuButton.setText(QCoreApplication.translate("MainWindow", u"Menu", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Number of floors", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Simulation steps", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Maximum number of people at the floor", None))
        self.VisualisationRadioButton.setText(QCoreApplication.translate("MainWindow", u"Visualisation", None))
        ___qtablewidgetitem = self.ElevatorTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Max people", None));
        ___qtablewidgetitem1 = self.ElevatorTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Speed", None));
        ___qtablewidgetitem2 = self.ElevatorTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Max floor", None));
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Number of elevators", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"AlgorithmEnum", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Model", None))
    # retranslateUi

