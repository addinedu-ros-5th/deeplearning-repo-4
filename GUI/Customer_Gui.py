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
    

        #카테고리 클릭 시 해당 페이지 로드
    
        self.Customer_Gui_btnHomePage_1.clicked.connect(self.switch_to_HomePage)
        self.Customer_Gui_btnFishListPage_1.clicked.connect(self.switch_to_FishListPage)
        self.Customer_Gui_btnImageSearchPage_1.clicked.connect(self.switch_to_ImageSearchPage)
        self.Customer_Gui_btnsafetyPage_1.clicked.connect(self.switch_to_SafetyPage)

        #header 클릭 시 홈페이지 로드
        self.Customer_Gui_btnHeader.clicked.connect(self.switch_to_HomePage)



    def switch_to_HomePage(self):
        self.stackedWidget.setCurrentIndex(0)

    def switch_to_FishListPage(self):
        self.stackedWidget.setCurrentIndex(1)

    def switch_to_ImageSearchPage(self):
        self.stackedWidget.setCurrentIndex(2)

    def switch_to_SafetyPage(self):
        self.stackedWidget.setCurrentIndex(3)



    #def connect_mysql(self):
    #    self.remote = mysql.connector.connect(
    #        host = '',
    #        port = 3306,
    #        user = "",
    #        password = "",
    #        database='' 
    #    )


                
        
if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())