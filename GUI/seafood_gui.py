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


from_class = uic.loadUiType("./GUI/seafood_gui.ui") [0]

#class MySideBar(QMainWindow, Ui_MainWindow):
class WindowClass(QMainWindow, from_class):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("________")
        self.setFixedSize(1200, 1000)   #fix size

        self.table_test_result.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.pixmap = QPixmap()
        self.camera = Camera()
        self.video = cv2.VideoCapture(-1)

        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)


        self.btn_camera_status = False   #False:off, True:on
        self.btn_graph_status = False
        self.btn_price_status = False
        self.load_image_status = False

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
        self.btn_directory.clicked.connect(self.load_image)
        self.btn_camera_caoture.clicked.connect(self.capture)
        self.btn_clear_data.clicked.connect(self.clear_data)

        self.camera.updateSignal.connect(self.camera_update)
        self.verticalLayout_graph.addWidget(self.canvas)

        self.camera.running = False
        self.camera.start()

        self.connect_to_database()
        self.load_combobox_data()
        #self.show_price()
        #self.graph_draw()

        self.model = YOLO("Fish_model/yolov8n.pt")

        self.f = open("./segment_log.txt", "w+")
        self.track_history = defaultdict(lambda: [])
        self.having_label = []
        self.pixmap_camera = None

#==camera==

    def camera_update(self):
        retval, self.image = self.video.read()
        self.image = cv2.resize(self.image, (self.label_camera.width(), self.label_camera.height()))
        if retval:
            results_tracking = self.model.track(self.image, conf=0.5, persist=True)
            if results_tracking is not None and len(results_tracking) > 0 and results_tracking[0] is not None and results_tracking[0].boxes is not None:
                boxes = results_tracking[0].boxes.xywh.cpu()
                track_ids = []
                
                for box in results_tracking[0].boxes:
                    if box.id is not None:
                        track_ids.append(box.id)
                        label = int(box.cls.item())
                        if label in label_mapping:
                            label_name = label_mapping[label]
                            
                            if label_name not in self.having_label:                    
                                
                                self.having_label.append(label_name)
                            
                self.line_detect.setText(', '.join(self.having_label))
                print(self.having_label)

                self.f.write('boxes : ' + str(boxes))
                self.f.write('track_ids : ' + str(track_ids))

                annotated_frame = results_tracking[0].plot()
                height, width, channel = annotated_frame.shape   #opencv -> Qpixmap
                bytesPerLine = 3 * width
                QImg = QImage(annotated_frame.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
                self.pixmap_camera = QPixmap.fromImage(QImg)

                self.label_camera.setPixmap(self.pixmap_camera)

                for box, track_id in zip(boxes, track_ids):
                    x, y, w, h = box
                    track = self.track_history[track_id]
                    track.append((float(x), float(y)))
                    if len(track) > 30: # retain 90 tracks for 90 frames
                        track.pop(0)
            else:
                print("No objects found in the tracking results_tracking.")   # 객체가 없는 경우
        else:
            print("Failed to read video frame.")


    def camera_onoff(self):
        if self.btn_camera_status == False:   #to run
            self.btn_camera_status = True
            self.btn_camera_onoff.setText("off")

            self.camera.start()
            self.camera.running = True
            self.load_image_status = False

        else:   #self.btn_camera_status == True #to stop
            self.btn_camera_status = False
            self.btn_camera_onoff.setText("on")

            self.video.release
            self.camera.running = False
            self.label_camera.clear()


    def load_image(self):
        self.load_image_status = True
        self.btn_camera_status = False
        self.btn_camera_onoff.setText("on")

        self.video.release
        self.camera.running = False
        
        file = QFileDialog.getOpenFileName(filter="image (*.*)")
        self.image = cv2.imread(file[0])
        self.image = cv2.resize(self.image, (self.label_camera.width(), self.label_camera.height()))

        results_detect = self.model.track(self.image, conf=0.5, persist=True)
        boxes = results_detect[0].boxes.xywh.cpu()
        track_ids = []

        for box in results_detect[0].boxes:
            if box.id is not None:
                track_ids.append(box.id)
                label = int(box.cls.item())
                if label in label_mapping:
                    label_name = label_mapping[label]
                    
                    if label_name not in self.having_label:                    
                        
                        self.having_label.append(label_name)
                            
        self.line_detect.setText(', '.join(self.having_label))
        print(self.having_label)

        self.f.write('boxes : ' + str(boxes))
        self.f.write('track_ids : ' + str(track_ids))

        annotated_frame = results_detect[0].plot()

        height, width, channel = annotated_frame.shape
        bytesPerLine = 3 * width
        QImg = QImage(annotated_frame.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        self.pixmap_camera = QPixmap.fromImage(QImg)

        self.label_camera.setPixmap(self.pixmap_camera)


    def capture(self):
        if self.btn_camera_status == True or self.load_image_status == True:

            self.now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_path = "taken/"
            input_filename = os.path.join(folder_path, self.now + ".jpg")

            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            cap_qimage = self.pixmap_camera.toImage()
            cap_qimage = cap_qimage.convertToFormat(QImage.Format_RGB32)

            width = cap_qimage.width()
            height = cap_qimage.height()
            ptr = cap_qimage.bits()
            ptr.setsize(height * width * 4)
            arr = np.array(ptr).reshape(height, width, 4)
            cv_image = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
            
            cv2.imwrite(input_filename, cv_image)
        else:
            print("camera off")

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
        searched_text_list = [text.strip() for text in searched_text.split(',')]
        
        self.table_info.clear()
        self.line_search.clear()

        with open("./GUI/fishlist.json", "r", encoding='utf-8') as file:
            fishlist = json.load(file)

        for search_text in searched_text_list:
            searched_fish_name = None

            for fish_name in fishlist:

                if fish_name["이름"] == search_text or fish_name["초성"] == search_text:
                    searched_fish_name = fish_name
                    break

            if searched_fish_name:
                searched_fish_name_filtered_initial = {key: value for key, value in searched_fish_name.items() if key != "초성"}
                searched_fish_info_str = "\n".join([f"{key}: {value}" for key, value in searched_fish_name_filtered_initial.items()])

                self.table_info.append(searched_fish_info_str)
            else:
                QMessageBox.information(self, "check again", "'%s'에 대한 검색결과가 없습니다.\n다시 입력해주세요." %searched_text)


#==price==
    def show_price(self):
        #if self.btn_camera_status == False:
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
            self.table_price.clear()

    def display_table_data(self, table, columns, results):
        table.setRowCount(len(results))
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

        for row_idx, row_data in enumerate(results):
            for col_idx, col_data in enumerate(row_data):
                table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def load_combobox_data(self):
        if connection and connection.is_connected():
            cursor = connection.cursor()

            cursor.execute("SELECT DISTINCT species FROM auction_price_data")
            species = cursor.fetchall()
            self.cb_filter_species.addItem("전체")
            for item in species:
                self.cb_filter_species.addItem(item[0])

            cursor.execute("SELECT DISTINCT origin FROM auction_price_data")
            origins = cursor.fetchall()
            self.cb_filter_origins.addItem("전체")
            for item in origins:
                self.cb_filter_origins.addItem(item[0])

    def filtered_price_table(self):
        start_date =  self.edit_filter_start_date.text()
        end_date = self.edit_filter_end_date.text()
        origins = self.cb_filter_origins.currentText()
        species = self.cb_filter_species.currentText()
        packaging = self.cb_filter_packaging.currentText()
        keywords =  self.cb_filter_keywords.currentText()


        table = "auction_price_data"
        species = ["넙치", "암꽃게"]
        size = "대"
        start_date = "2020-01-01"
        end_date = "2023-12-31"
        origins = ["태안"]
        keywords = ["활"]

        query = self.generate_query(table, species, size, start_date, end_date, origins, keywords)
        columns, results = self.search_query(query)
        if results :
            self.display_table_data(self.table_price, columns, results)


#==test==

    def show_test_result(self):
        query = """
        SELECT * FROM radioactive_test1;
        """
        columns, results = self.search_query(query)
        if results:
            self.display_table_data(self.table_test_result, columns, results)


#==clear==
    def clear_data(self):
        self.btn_camera_status = False   #camera off
        self.btn_camera_onoff.setText("on")
        self.video.release
        self.camera.running = False
        self.label_camera.clear()

        self.line_detect.clear()   #label keyword delete
        self.having_label = []

        self.line_search.clear()   #search and info clear
        self.table_info.clear()
        
        self.btn_price_status == False   #price clear
        self.btn_price_onoff.setText("on")
        self.table_test_result.clear()
        if connection.is_connected():
            connection.close()
        self.table_price.clear()

        self.canvas.setVisible(False)   
        self.btn_graph_onoff.setText("on")   #graph hide   #graph clear check please
        self.btn_graph_status = False
        # x = 10
        # y = 10
        # ax = self.fig.add_subplot(111)
        # ax.plot(x, y, label="price")
        # ax.set_xlabel("x")
        # ax.set_xlabel("y")
        # ax.set_title("my graph")
        # ax.legend()
        # self.canvas.draw()

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

    def generate_query(self, table, species=None, size=None, start_date=None, end_date=None, origins=None, keywords=None):
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

        query = f"{base_query} {' AND '.join(conditions)} ORDER BY date DESC LIMIT 50"
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