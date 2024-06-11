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

import pandas as pd
import mysql.connector
from mysql.connector import Error
from db_connect import DB_CONFIG


from ultralytics import YOLO
from collections import defaultdict
import os
label_mapping = {
    0: "우럭",
    1: "갈치",
    2: "가자미",
    3: "도미",
    4: "아귀",
    5: "고등어"
}


<<<<<<< HEAD
from_class = uic.loadUiType("GUI/seafood_gui.ui") [0]
=======
from_class = uic.loadUiType("./GUI/seafood_gui.ui") [0]
>>>>>>> fa5d2b52fe7beab0fa63ef82d3c024fef678a980

#class MySideBar(QMainWindow, Ui_MainWindow):
class WindowClass(QMainWindow, from_class):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("________")
        self.setFixedSize(1200, 900)   #fix size

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
        self.btn_table_price_search.clicked.connect(self.filtered_price_table)

        self.camera.updateSignal.connect(self.camera_update)
        self.verticalLayout_graph.addWidget(self.canvas)

        self.camera.running = False
        self.camera.start()

        self.connect_to_database()

        self.model = YOLO("Fish_model/yolov8n.pt")

        self.f = open("./segment_log.txt", "w+")
        self.track_history = defaultdict(lambda: [])
        self.having_label = []
        self.pixmap_camera = None

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
        query = """
                SELECT
                    species,
                    DATE_FORMAT(date, '%Y-%m') AS month,
                    SUM(quantity * average) AS total_amount,
                    SUM(quantity) AS total_quantity,
                    SUM(quantity * average) / SUM(quantity) AS monthly_average
                FROM auction_price_data
                WHERE
                    species LIKE "(활)암꽃게" AND
                    date BETWEEN '2009-01-01' AND '2023-12-31'
                GROUP BY species, month ORDER BY month;
                """
        columns, results = self.search_query(query)
        df = pd.DataFrame(results)
        df.columns = columns

        x = df['month']
        y = df['monthly_average']

        ax = self.fig.add_subplot(111)
        ax.plot(x, y, label="price")
        ax.set_xlabel("x")
        ax.set_xlabel("y")

        ax.set_title("my graph")
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
                if not connection.is_connected():
                    self.connect_to_database()
                query = """
                SELECT * FROM auction_price_data ORDER BY date DESC LIMIT 10;
                """
                columns, results = self.search_query(query)
                if results:
                    self.display_table_data(self.table_price, columns, results)
                else:
                    print("No data found.")
                self.show_test_result()

            else:   #to stop
                self.btn_price_status = False
                self.btn_price_onoff.setText("on")
                if connection.is_connected():
                    connection.close()
                self.table_price.clear()

    def display_table_data(self, table, columns, results):
        table.setRowCount(len(results))
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

        for row_idx, row_data in enumerate(results):
            for col_idx, col_data in enumerate(row_data):
                table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def filtered_price_table(self):
        region = self.cb_filter_region.currentText()
        species = self.cb_filter_species.currentText()
        origin = self.cb_filter_origin.currentText()
        status =  self.cb_filter_status.currentText()

#==test==

    def show_test_result(self):
        query = """
        SELECT * FROM radioactive_test1;
        """
        columns, results = self.search_query(query)
        if results:
            self.display_table_data(self.table_test_result, columns, results)

#==========================

    ####
    # Usage :
    #   table = "auction_price_data"
    #   species = ["넙치", "암꽃게"]
    #   size = "대"
    #   start_date = "2020-01-01"
    #   end_date = "2023-12-31"
    #   origins = ["태안"]
    #   keywords = ["활"]
    #   sql_query = generate_query(table, species, size, start_date, end_date, origins, keywords)
    #   print(sql_query)

    def generate_query(table, species=None, size=None, start_date=None, end_date=None, origins=None, keywords=None):
        base_query = f"SELECT * FROM {table} WHERE"
        conditions = []

        if keywords: # 활, 냉, 선
            keywords_condition = " OR ".join([f"species LIKE '({keyword})%'" for keyword in keywords])
            conditions.append(f"({keywords_condition})")

        if species: # 넙치, 암꽃게, 오징어
            color_condition = " OR ".join([f"species LIKE '%{specie}%'" for specie in species])
            conditions.append(f"({color_condition})")

        if size:    # 대, 중, 소, kg, box
            conditions.append(f"size = '{size}'")

        if start_date and end_date: # 2024-06-09
            if start_date > end_date:
                raise ValueError("Start date cannot be after end date")
            conditions.append(f"date BETWEEN '{start_date}' AND '{end_date}'")

        if origins: #태안, 목포, 제주
            origin_condition = " OR ".join([f"origin = '{origin}'" for origin in origins])
            conditions.append(f"({origin_condition})")

        query = f"{base_query} {' AND '.join(conditions)} ORDER BY date DESC LIMIT 100"
        return query
    ####

    def connect_to_database(self):
        global connection, cursor
        try:
            connection = mysql.connector.connect(
                host=DB_CONFIG['host'],
                database=DB_CONFIG['database'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password']
            )

            if connection.is_connected():
                cursor = connection.cursor()
                return connection

        except Error as e:
            print(f"Error: {e}")

    def search_query(self, query) :
        cursor.execute(query)
        columns = cursor.column_names
        results = cursor.fetchall()
        return columns, results
    
    
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