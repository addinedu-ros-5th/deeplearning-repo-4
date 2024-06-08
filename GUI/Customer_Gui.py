#from ui_Customer_Gui import Ui_MainWindow
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtWidgets import QStackedWidget
import resources_rc
#import mysql.connector
import re
import datetime
#import db_connect


from_class = uic.loadUiType("Customer_Gui.ui") [0]

#class MySideBar(QMainWindow, Ui_MainWindow):
class WindowClass(QMainWindow, from_class):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("________")

        #self.Customer_Gui_tablewidgetCartList.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        #self.connect_mysql()

        #self.start_stock_label()

        # 카테고리 클릭 시 해당 페이지 로드
        self.btn_home_page_1.clicked.connect(self.switch_to_HomePage)
        self.btn_fish_list_page_1.clicked.connect(self.switch_to_FishListPage)
        self.btn_image_search_page_1.clicked.connect(self.switch_to_ImageSearchPage)
        self.btn_safety_page_1.clicked.connect(self.switch_to_SafetyPage)

        # header 클릭 시 홈페이지 로드
        self.btn_header.clicked.connect(self.switch_to_HomePage)

        # 홈페이지의 오늘 거래가 위젯 페이지 로드
        self.btn_today_price_stacked_widget_1.clicked.connect(self.switch_to_widget_page_1)
        self.btn_today_price_stacked_widget_1.clicked.connect(self.switch_to_widget_page_2)
        self.btn_today_price_stacked_widget_1.clicked.connect(self.switch_to_widget_page_3)
        self.btn_today_price_stacked_widget_1.clicked.connect(self.switch_to_widget_page_4)
        self.btn_today_price_stacked_widget_1.clicked.connect(self.switch_to_widget_page_5)
        self.btn_today_price_stacked_widget_1.clicked.connect(self.switch_to_widget_page_6)
        self.btn_today_price_stacked_widget_1.clicked.connect(self.switch_to_widget_page_7)


    # 페이지 로드
    def switch_to_HomePage(self):
        self.stacked_widget_total_page.setCurrentIndex(0)

    def switch_to_FishListPage(self):
        self.stacked_widget_total_page.setCurrentIndex(1)

    def switch_to_ImageSearchPage(self):
        self.stacked_widget_total_page.setCurrentIndex(2)

    def switch_to_SafetyPage(self):
        self.stacked_widget_total_page.setCurrentIndex(3)

    
    # 위젯 페이지 로드
    def switch_to_widget_page_1(self):
        self.today_price_stacked_widget.setCurrentIndex(0)

    def switch_to_widget_page_2(self):
        self.today_price_stacked_widget.setCurrentIndex(1)

    def switch_to_widget_page_3(self):
        self.today_price_stacked_widget.setCurrentIndex(2)

    def switch_to_widget_page_4(self):
        self.today_price_stacked_widget.setCurrentIndex(3)
    
    def switch_to_widget_page_5(self):
        self.today_price_stacked_widget.setCurrentIndex(4)

    def switch_to_widget_page_6(self):
        self.today_price_stacked_widget.setCurrentIndex(5)

    def switch_to_widget_page_7(self):
        self.today_price_stacked_widget.setCurrentIndex(6)

    #def connect_mysql(self):
    #    self.remote = mysql.connector.connect(
    #        host = '',
    #        port = 3306,
    #        user = "",
    #        password = "",
    #        database=''
    #    )

    def connect_mysql(self) :
        self.remote = db_connect()

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())