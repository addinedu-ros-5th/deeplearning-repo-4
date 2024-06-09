#from ui_Customer_Gui import Ui_MainWindow
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtWidgets import QStackedWidget
import datetime
from PyQt5.QtCore import pyqtSignal, QThread
import time
import cv2

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import json

from_class = uic.loadUiType("./GUI/seafood_gui.ui") [0]

#class MySideBar(QMainWindow, Ui_MainWindow):
class WindowClass(QMainWindow, from_class):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("________")
        self.setFixedSize(1036, 850)   #fix size

        self.table_test_result.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.pixmap = QPixmap()
        self.camera = Camera()
        self.video = cv2.VideoCapture(-1)

        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)

    
        self.btn_camera_status = False   #False:off, True:on
        self.btn_graph_status = False
        self.btn_price_status = False

        self.btn_camera_onoff.setText("on")
        self.btn_graph_onoff.setText("on")
        self.btn_price_onoff.setText("on")

        #self.test_text_list = ["광어", "오징어", "전복"]

        self.btn_camera_onoff.clicked.connect(self.camera_onoff)
        self.btn_graph_onoff.clicked.connect(self.graph_onoff)
        self.btn_search.clicked.connect(self.search_bar)
        self.line_search.returnPressed.connect(self.search_bar)
        self.btn_price_onoff.clicked.connect(self.show_price)

        self.camera.updateSignal.connect(self.camera_update)
        self.verticalLayout_graph.addWidget(self.canvas)

        self.camera.running = False
        self.camera.start()

#==camera==

    def camera_update(self):   #maybe input YOLO here..?
        retval, self.image = self.video.read()
        if retval:
            self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)

            h, w, c = self.image.shape
            qimage = QImage(self.image.data, w, h, w*c, QImage.Format_RGB888)

            self.pixmap = self.pixmap.fromImage(qimage)
            self.pixmap_camera = self.pixmap.scaled(self.label_camera.width(), self.label_camera.height())

            self.label_camera.setPixmap(self.pixmap_camera)

    def camera_onoff(self):
        if self.btn_camera_status == False:   #to run
            self.btn_camera_status = True
            self.btn_camera_onoff.setText("off")
            
            self.camera.start()
            self.camera.running = True

        else:   #self.btn_camera_status == True #to stop
            self.btn_camera_status = False
            self.btn_camera_onoff.setText("on")

            self.video.release
            self.camera.running = False
            self.label_camera.clear()

#==graph==

    def graph_onoff(self):
        if self.btn_graph_status == False:   #to run
            self.btn_graph_status = True
            self.btn_graph_onoff.setText("off")
            
            self.canvas.setVisible(True)
            self.graph_draw()
            
        else:   #self.btn_graph_status == True   #to stop
            self.btn_graph_status = False
            self.btn_graph_onoff.setText("on")

            self.canvas.setVisible(False)

    def graph_draw(self):   #test
        x = np.arange(0, 100, 1)
        y = np.sin(x)

        ax = self.fig.add_subplot(111)
        ax.plot(x, y, label="sin")
        ax.set_xlabel("x")
        ax.set_xlabel("y")

        ax.set_title("my sin graph")
        ax.legend()
        self.canvas.draw()

#==search==

    # def search_bar(self):
    #     search_text = self.line_search.text()
    #     if search_text not in self.test_text_list:
    #         QMessageBox.information(self, "check again", "입력된 텍스트의 정보가 없습니다.\n다시 입력해주세요.")

    #         return
    #     elif search_text in self.test_text_list:   #입력한 텍스트가 물고기 종류 배열?에 속할 때
    #         print("test ok")
    #         self.line_search.clear()

    def search_bar(self):

        searched_text = self.line_search.text()
        self.table_info.clear()
        self.line_search.clear()

        with open("./GUI/fishlist.json", "r", encoding='utf-8') as file:
            fishlist = json.load(file)
        
        searched_fish_name = None

        for fish_name in fishlist:
            if fish_name["이름"] == searched_text or fish_name["초성"] == searched_text:
                searched_fish_name = fish_name
                break
        
        if searched_fish_name:
            searched_fish_name_filtered_initial = {key: value for key, value in searched_fish_name.items() if key != "초성"}
            searched_fish_info_str = "\n".join([f"{key}: {value}" for key, value in searched_fish_name_filtered_initial.items()])

            self.table_info.append(searched_fish_info_str)
        else:
            # self.table_info.append(f"{search_text}에 해당하는 정보를 찾을 수 없습니다.")
            QMessageBox.information(self, "check again", "'%s'에 대한 검색결과가 없습니다.\n다시 입력해주세요." %searched_text)


#==price==

    def show_price(self):
        if self.btn_camera_status == False:
            if self.btn_price_status == False:   #to run
                self.btn_price_status = True
                self.btn_price_onoff.setText("off")

                self.text_price.setText("test")
            
            else:   #to stop
                self.btn_price_status = False
                self.btn_price_onoff.setText("on")

                self.text_price.clear()

        #else:
                


#==========================


    #def connect_mysql(self):
    #    self.remote = mysql.connector.connect(
    #        host = '',
    #        port = 3306,
    #        user = "",
    #        password = "",
    #        database=''
    #    )

#    def connect_mysql(self) :
#        self.remote = db_connect()



class Camera(QThread):
    updateSignal = pyqtSignal()

    def __init__(self, sec = 0, parent = None):
        super().__init__()
        self.main = parent
        self.running = True

    def run(self):
        while self.running == True:
            self.updateSignal.emit()
            time.sleep(0.1)

    def stop(self):
        self.running = False



if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    sys.exit(app.exec_())