# -*- coding: utf-8 -*-
"""
Created on Fri Jun  6 15:40:08 2025

@author: quynh
"""
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QStackedWidget,
    QComboBox,
    QGridLayout,
    QListWidget,
    QMessageBox,
    QTextEdit
)
from PyQt5.QtGui import (
    QPixmap,
    QFont,
)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import subprocess
from ALNS import *
from configuration_data1 import * 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas 
from matplotlib.figure import Figure 
from collections import Counter
import matplotlib.cm as cm
import numpy as np
import time


# STYLE
class StyleManager:
    def set_button_style():
         return"""
             QPushButton {
                 background-color: #3a96ff;  
                 color: white;
                 border-radius: 8px;
                 padding: 8px 16px;
             }
             QPushButton:hover {
                 background-color: #c1edfe;
                 color: #f9555c;
             }
         """
    def set_size_heading1():
        return QFont("Aptos", 16)
    def set_size_normal():
        return QFont("Aptos", 10)
    def set_frame_font():
        return"""
            QLabel {
                background-color: #3a96ff;
                color: white;
                font-weight: bold;
                border-radius: 20px;   /* làm khung bo tròn */
                padding: 10px 10px;    /* top/bottom: 10px, left/right: 20px */
        }
        """
        

class FirstScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        
        # BACKGROUND
        label1 = QLabel()
        pixmap = QPixmap('port.png')
        label1.setPixmap(pixmap)
        
        #BUTTON
        button = QPushButton("LET'S GO")
        button.setFont(QFont("ee", 15, QFont.Weight.Bold))
        button.setStyleSheet(StyleManager.set_button_style())
        button.clicked.connect(self.goto_second)
        
        #LAYOUT
        layout = QVBoxLayout()
        layout.addWidget(label1, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(button)
        self.setLayout(layout)
    
    def goto_second(self):
        self.stacked_widget.setCurrentIndex(1)
        
 
class SecondScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget     
        
        #BUTTON CHOOSE SOLVER
        button_run = QPushButton("CHOOSE SOLVER")
        button_run.setFont(QFont("ee", 15, QFont.Weight.Bold))
        button_run.setStyleSheet(StyleManager.set_button_style())
        button_run.clicked.connect(self.choose_solver)
        
        #BUTTON GO BACK
        button_go_back = QPushButton("GO BACK")
        button_go_back.setFont(QFont("ee", 15, QFont.Weight.Bold))
        button_go_back.setStyleSheet(StyleManager.set_button_style())
        button_go_back.clicked.connect(self.goto_first)
        
        instruction = QLabel("Choose the region or nation that you want to optimize the feeder network to South Vietnam")
        instruction.setFont(StyleManager.set_size_normal())
        
        # REGIONAL OPTIMIZE
        region = QLabel("REGION")
        region.setFont(StyleManager.set_size_heading1()) 
        region.setStyleSheet(StyleManager.set_frame_font())
        
        # SELECT FILE DATA AND LINK REGION
        self.region_platform = QListWidget(self)
        self.region_platform.addItems(
            ['Asia_59ports',
             'North_Europe_77ports',
             'Africa_29ports'
             ])
        self.region_platform.setFixedHeight(450)
        self.region_platform.itemClicked.connect(self.on_platform_selected_python)
        
        # NATIONAL OPTIMIZE
        nation = QLabel("NATION")
        nation.setFont(StyleManager.set_size_heading1()) 
        nation.setStyleSheet(StyleManager.set_frame_font())
        
        # SELECT FILE DATA AND LINK NATION >>> gộp nation lại làm file riêng
        self.nation_platform = QListWidget(self)
        self.nation_platform.addItems(
            ['Latvia_5ports',
             'Latvia_6ports',
             'Latvia_7ports',
             'Latvia_8ports',
             'Latvia_9ports',
             'Latvia_10ports',
             'Estonia_10ports', 
             'Angeria_12ports',
             'Thailand_16ports',
             'Morocco_17ports',
             'Crotia_19ports',
             'Ireland_35ports',
             'Philipines_43ports',
             'Norway_57ports'])
        self.nation_platform.setFixedHeight(450)
        self.nation_platform.itemClicked.connect(self.on_platform_selected_cplex)
        
        #LAYOUT
        layout = QGridLayout()
        layout.addWidget(instruction,0,0,1,2,alignment=Qt.AlignHCenter)
        layout.addWidget(nation, 1,0, alignment=Qt.AlignHCenter)
        layout.addWidget(region,1,1, alignment=Qt.AlignHCenter)
        layout.addWidget(self.nation_platform, 2,0)
        layout.addWidget(self.region_platform, 2,1)
        layout.addWidget(button_run,3,1,1,1)
        layout.addWidget(button_go_back,3,0,1,1)
        self.setLayout(layout)

    def goto_first(self):
        self.stacked_widget.setCurrentIndex(0)  # Quay lại màn hình đầu
    
    def choose_solver(self):
        self.stacked_widget.setCurrentIndex(2)
    
    def on_platform_selected_cplex(self, item):
        self.selected_name = item.text()
   
        
    def on_platform_selected_python(self, item):
        self.selected_name = item.text()
 
                              
        

class ThirdScreen(QWidget):
    def __init__(self, stacked_widget, first_screen, second_screen):
        super().__init__()
        self.stacked_widget = stacked_widget   
        self.first_screen = first_screen
        self.second_screen = second_screen
        self.result() 
        self.cplex_nations = ['Latvia_5ports','Latvia_6ports','Latvia_7ports',
                              'Latvia_8ports','Latvia_9ports','Latvia_10ports',
                              'Estonia_10ports',  'Angeria_12ports','Thailand_16ports',
                              'Morocco_17ports', 'Crotia_19ports', 'Ireland_35ports','Africa_29ports']
   
        
        #BUTTON GO BACK
        button_go_back = QPushButton("GO BACK")
        button_go_back.setFont(QFont("ee", 15, QFont.Weight.Bold))
        button_go_back.setStyleSheet(StyleManager.set_button_style())
        button_go_back.clicked.connect(self.first_screen.goto_second)
        
        #BUTTON RUN CPLEX
        button_run_cplex = QPushButton("CPLEX")
        button_run_cplex.setFont(QFont("ee", 15, QFont.Weight.Bold))
        button_run_cplex.setStyleSheet(StyleManager.set_button_style())
        button_run_cplex.clicked.connect(self.run_cplex)
        #BUTTON RUN PYTHON
        button_run_python = QPushButton("PYTHON")
        button_run_python.setFont(QFont("ee", 15, QFont.Weight.Bold))
        button_run_python.setStyleSheet(StyleManager.set_button_style())
        button_run_python.clicked.connect(self.run_python)
       
        # DRAW PYTHON
        button_draw = QPushButton("DRAW")
        button_draw.setFont(QFont("ee", 15, QFont.Weight.Bold))
        button_draw.setStyleSheet(StyleManager.set_button_style())
        button_draw.clicked.connect(self.draw)
        # LAYOUT 
        
        
        self.main3_layout = QGridLayout()
        self.main3_layout.addWidget(button_run_cplex, 1,0, alignment=Qt.AlignHCenter)
        self.main3_layout.addWidget(self.result1, 3, 0, 1, 1)
        self.main3_layout.addWidget(button_run_python, 1,1, alignment=Qt.AlignHCenter)
        self.main3_layout.addWidget(self.result2, 3, 1, 1, 1)
        self.main3_layout.addWidget(button_go_back,4,0,1,1)
        self.main3_layout.addWidget(button_draw,4,1,1,1)
        self.setLayout(self.main3_layout)
        
    def portName(self):
        DATA_PATH               = r"C:\Users\quynh\opl\Thesis\DATA.xlsx"
        df_ports                = pd.read_excel(DATA_PATH, sheet_name="port_code")
        self.port_name_dict     = dict(zip(df_ports['no'], df_ports['port_name']))
        self.port_cood          = {row['no']: (row['x'], row['y'])  for _, row in df_ports.iterrows()}             
        df_ship                 = pd.read_excel(DATA_PATH, sheet_name="port_code")
        self.ship_dict          = dict(zip(df_ports['no_ship'], df_ports['ship_cap']))
        return self.port_name_dict, self.ship_dict, self.port_cood
    
    def phase2(self):
        OPL_RUN = r"C:\Desktop\setting\opl\bin\x64_win64\oplrun.exe"
        MODFILE_phase2=r"C:\Users\quynh\opl\Thesis\phase2.mod"
        DATFILE_phase2=r"C:\Users\quynh\opl\Thesis\phase2.dat"
        result_file_phase2 = r"C:\Users\quynh\opl\Thesis\Result_phase2.txt"
        subprocess.run([OPL_RUN,MODFILE_phase2,DATFILE_phase2])

        with open(result_file_phase2, 'r') as f:
            lines = f.read().splitlines()

        self.cost_phase2 = float(lines[0].strip().replace("Objective:", "").strip())
        self.route_phase_2 = []
        for i in range(len(lines)-1):
            solution = lines[i+1].strip().replace("Route", "")
            solution = list(map(int, solution.split()))
            self.route_phase_2.append(solution)
        self.route_phase_2 = self.route_phase_2
            
        return self.cost_phase2, self.route_phase_2
    
    def run_cplex(self):
        self.port_name_dict, self.ship_dict, self.port_cood = self.portName()
        OPL_RUN = r"C:\Desktop\setting\opl\bin\x64_win64\oplrun.exe"
        MODFILE = r"C:\Users\quynh\opl\Thesis\Thesis.mod"
        
        if self.second_screen.selected_name not in self.cplex_nations:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Announce!!!")
            msg.setText(f"CPLEX execution is not supported for:\n{self.second_screen.selected_name}")
            msg.exec_()
            return
        else:
            if self.second_screen.selected_name == 'Latvia_5ports':
                DATFILE=r"C:\Users\quynh\opl\Thesis\data1_latvia_5.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Latvia_6ports':
                DATFILE=r"C:\Users\quynh\opl\Thesis\data1_latvia_6.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Latvia_7ports':
                DATFILE=r"C:\Users\quynh\opl\Thesis\data1_latvia_7.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Latvia_8ports':
                DATFILE=r"C:\Users\quynh\opl\Thesis\data1_latvia_8.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Latvia_9ports':
                DATFILE=r"C:\Users\quynh\opl\Thesis\data1_latvia_9.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Latvia_10ports':
                DATFILE=r"C:\Users\quynh\opl\Thesis\data1_latvia_10.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Estonia_10ports':
                DATFILE=r"C:\Users\quynh\opl\Thesis\data2_estonia_10.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Angeria_12ports':
                DATFILE=r"C:\Users\quynh\opl\Thesis\data3_angeria_12.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Thailand_16ports':
                DATFILE=r"C:\Users\quynh\opl\Thesis\data4_thailand_16.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Morocco_17ports':
                DATFILE=r"C:\Users\quynh\opl\Thesis\data5_morocco_17.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Crotia_19ports':
                DATFILE=r"C:\Users\quynh\opl\Thesis\data6_crotia_19.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Ireland_35ports':
                DATFILE=r"C:\Users\quynh\opl\Thesis\data7_ireland_35.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Africa_29ports':
                DATFILE=r"C:\Users\quynh\opl\Thesis\data12_africa_29.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
                
            #check
            #if self.second_screen.selected_name == 'Philipines_43ports':
                #DATFILE=r"C:\Users\quynh\opl\Thesis\Thesis.dat"
                #subprocess.run([OPL_RUN,MODFILE,DATFILE])
        result_file = r"C:\Users\quynh\opl\Thesis\Result.txt"
        
        with open(result_file, 'r') as f:
                lines = f.readlines() 
                if len(lines) >= 4:
                    self.total_cost_1 = float(lines[0].strip().replace("Objective:", "").strip())
                    self.hub_line = lines[1].strip()
                    self.ship_line = lines[2].strip() 
                    self.port_line = lines[3].strip()
                    self.hub_1 = list(map(int, self.hub_line.split()))
                    self.ship_1 = list(map(int, self.ship_line.split()))
                    self.origin_1 = list(map(int, self.port_line.split()))
                    self.result1.setReadOnly(True)
                    text = f"🎯 Total cost is {self.total_cost_1}\n"
                    for i in range(len(self.origin_1)):
                        port_id = self.origin_1[i]
                        port_name = self.port_name_dict.get(port_id)
                        
                        hub_id = self.hub_1[i]
                        hub_name = self.port_name_dict.get(hub_id)
                        ship   = self.ship_1[i]
                        ship_cap = self.ship_dict.get(ship)
                        text += f"⚓ Port {port_id} ({port_name}) connected to 🏗 Hub {hub_id} ({hub_name}) using 🚢 Ship {ship} ({ship_cap})\n"
                
                    #PHASE 2 RESULT
                    self.cost_phase2, self.route_phase_2 = self.phase2()
                    text += f"🎯 Among the total cost, the cost for phase 2 is ({self.cost_phase2})\n"
                    for i in range(len(self.route_phase_2)):
                        text += f"Using the barge 🚢 the route {i+1}: "
                        for port_id in self.route_phase_2[i]:
                            port_name = self.port_name_dict.get(port_id)
                            text += f"{port_id} ({port_name}) - "
                        text = text.rstrip(" - ")    
                        text += "\n"
                    self.result1.setPlainText(text)
                    
        return self.total_cost_1, self.hub_1, self.ship_1, self.origin_1
    
    def run_python(self):
        self.port_name_dict, self.ship_dict, self.port_cood = self.portName()
        print("Hi")
        DATA_PATH       = r"C:\Users\quynh\opl\Thesis\DATA.xlsx"
        OPL_RUN         = r"C:\Desktop\setting\opl\bin\x64_win64\oplrun.exe"
        MODFILE         = r"C:\Users\quynh\opl\Thesis\Thesis.mod"
 
        # Small scale = initial solution from cplex + datasheet of nations
        if self.second_screen.selected_name in self.cplex_nations:
            if self.second_screen.selected_name == 'Latvia_5ports':
                SHEET_NAME = r"data1_latvia_5"
                p = 5
                DATFILE=r"C:\Users\quynh\opl\Thesis\data1_latvia_5.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Latvia_6ports':
                SHEET_NAME = r"data1_latvia_6"
                p = 6
                DATFILE=r"C:\Users\quynh\opl\Thesis\data1_latvia_6.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Latvia_7ports':
                SHEET_NAME = r"data1_latvia_7"
                p = 7
                DATFILE=r"C:\Users\quynh\opl\Thesis\data1_latvia_7.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Latvia_8ports':
                SHEET_NAME = r"data1_latvia_8"
                p = 8
                DATFILE=r"C:\Users\quynh\opl\Thesis\data1_latvia_8.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Latvia_9ports':
                SHEET_NAME = r"data1_latvia_9"
                p = 9
                DATFILE=r"C:\Users\quynh\opl\Thesis\data1_latvia_9.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
                
            if self.second_screen.selected_name == 'Latvia_10ports':
                SHEET_NAME = r"data1_latvia_10"
                p = 10
                DATFILE=r"C:\Users\quynh\opl\Thesis\data1_latvia_10.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Estonia_10ports':
                SHEET_NAME = r"data2_estonia_10"
                p = 10
                DATFILE=r"C:\Users\quynh\opl\Thesis\data2_estonia_10.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Angeria_12ports':
                SHEET_NAME = r"data3_angeria_12"
                p = 12
                DATFILE=r"C:\Users\quynh\opl\Thesis\data3_angeria_12.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Thailand_16ports':
                SHEET_NAME = r"data4_thailand_16"
                p = 16
                DATFILE=r"C:\Users\quynh\opl\Thesis\data4_thailand_16.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Morocco_17ports':
                SHEET_NAME = r"data5_morocco_17"
                p = 17
                DATFILE=r"C:\Users\quynh\opl\Thesis\data5_morocco_17.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Crotia_19ports':
                SHEET_NAME = r"data6_crotia_19"
                p = 19
                DATFILE=r"C:\Users\quynh\opl\Thesis\data6_crotia_19.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Ireland_35ports':
                SHEET_NAME = r"data7_ireland_35"
                p = 35
                DATFILE=r"C:\Users\quynh\opl\Thesis\data7_ireland_35.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
            if self.second_screen.selected_name == 'Africa_29ports':
                SHEET_NAME = r"data12_africa_29"
                p = 29
                DATFILE=r"C:\Users\quynh\opl\Thesis\data12_africa_29.dat"
                subprocess.run([OPL_RUN,MODFILE,DATFILE])
        result_file = r"C:\Users\quynh\opl\Thesis\Result.txt"
        
        # Large scale - only datasheet
        if self.second_screen.selected_name not in self.cplex_nations:
            DATFILE=r"C:\Users\quynh\opl\Thesis\data1_latvia_10.dat"
            subprocess.run([OPL_RUN,MODFILE,DATFILE])
            result_file = r"C:\Users\quynh\opl\Thesis\Result.txt"
            if self.second_screen.selected_name == 'Philipines_43ports':
                SHEET_NAME = r"data8_philipines_43"
                p = 43
            if self.second_screen.selected_name == 'Norway_57ports':
                SHEET_NAME = r"data9_norway_57"
                p = 57
            if self.second_screen.selected_name == 'Asia_59ports':
                SHEET_NAME = r"data10_asia_59"
                p = 59
            if self.second_screen.selected_name == 'North_Europe_77ports':
                SHEET_NAME = r"data11_north_europe_77"
                p = 77
        start_time = time.time()       
        self.total_cost_2, self.hub_2, self.ship_2, self.origin_2 = ALNS(DATA_PATH, SHEET_NAME,result_file,
                                                                         cycle_length, p,m,maxIteration, 
                                                                         num_remove_hub,num_remove_ship, 
                                                                         rho, initial_temp, cooling_rate, stopping_temp)
        end_time = time.time()
        running_time = end_time - start_time
        print(f"⏱️ ALNS execution time: {running_time:.2f} seconds")
        self.result2.setReadOnly(True)
        text = f"🎯 Total cost is {self.total_cost_2}\n"
        
        for i in range(len(self.origin_2)):
            port_id = self.origin_2[i]
            port_name = self.port_name_dict.get(port_id)
            hub_id = self.hub_2[i]
            hub_name = self.port_name_dict.get(hub_id)
            ship   = self.ship_2[i]
            ship_cap = self.ship_dict.get(ship)
            text += f"⚓ Port {port_id} ({port_name}) connected to 🏗 Hub {hub_id} ({hub_name}) using 🚢 Ship {ship} ({ship_cap})\n"
        
        #PHASE 2 RESULT
        self.cost_phase2, self.route_phase_2 = self.phase2()
        text += f"🎯 Among the total cost, the cost for phase 2 is ({self.cost_phase2})\n"
        for i in range(len(self.route_phase_2)):
            text += f"Using the barge 🚢 the route {i+1}: "
            for port_id in self.route_phase_2[i]:
                port_name = self.port_name_dict.get(port_id)
                text += f"{port_id} ({port_name}) - "
            text = text.rstrip(" - ")    
            text += "\n"
        self.result2.setPlainText(text)      
        return self.total_cost_2, self.hub_2, self.ship_2, self.origin_2
            
    def result(self):
        self.result1 = QTextEdit()
        self.result2 = QTextEdit()
        self.result1.setReadOnly(True)
        self.result2.setReadOnly(True)
       
    def draw(self):
        self.stacked_widget.setCurrentIndex(3)
        
   
        
class FourthScreen(QWidget):
    def __init__(self,stacked_widget,first_screen, second_screen, third_screen):
        super().__init__()
        self.stacked_widget = stacked_widget   
        self.first_screen = first_screen
        self.second_screen = second_screen
        self.third_screen = third_screen
        
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        
        #self.result() 
        
        #BUTTON GO BACK
        button_go_back = QPushButton("GO BACK")
        button_go_back.setFont(QFont("ee", 15, QFont.Weight.Bold))
        button_go_back.setStyleSheet(StyleManager.set_button_style())
        button_go_back.clicked.connect(self.second_screen.choose_solver)
        
        # DRAW PHASE1-CPLEX
        button_draw_1_cplex = QPushButton("DRAW PHASE 1 - CPLEX")
        button_draw_1_cplex.setFont(QFont("ee", 15, QFont.Weight.Bold))
        button_draw_1_cplex.setStyleSheet(StyleManager.set_button_style())
        button_draw_1_cplex.clicked.connect(self.plot_phase1_cplex) 
        
        # DRAW PHASE1-PYTHON
        button_draw_1_python = QPushButton("DRAW PHASE 1 - PYTHON")
        button_draw_1_python.setFont(QFont("ee", 15, QFont.Weight.Bold))
        button_draw_1_python.setStyleSheet(StyleManager.set_button_style())
        button_draw_1_python.clicked.connect(self.plot_phase1_python) 
        
        # DRAW PHASE2
        button_draw_2 = QPushButton("DRAW PHASE 2")
        button_draw_2.setFont(QFont("ee", 15, QFont.Weight.Bold))
        button_draw_2.setStyleSheet(StyleManager.set_button_style())
        button_draw_2.clicked.connect(self.plot_phase2) 
        
        # LAYOUT
        self.main4_layout = QGridLayout()
        self.main4_layout.addWidget(button_draw_1_cplex, 0,0, alignment=Qt.AlignHCenter)
        self.main4_layout.addWidget(button_draw_1_python, 0,1, alignment=Qt.AlignHCenter)
        self.main4_layout.addWidget(button_draw_2, 0,2, alignment=Qt.AlignHCenter)
        self.main4_layout.addWidget(self.canvas,1,0,1,3)
        self.main4_layout.addWidget(button_go_back,2,0,1,3)
        self.setLayout(self.main4_layout)
    
    def plot_phase1_cplex(self):
        self.total_cost = self.third_screen.total_cost_1
        self.hub = self.third_screen.hub_1
        self.ship = self.third_screen.ship_1
        self.origin = self.third_screen.origin_1
        self.plot_routes_phase1(self.origin, self.hub)
        
    def plot_phase1_python(self):
        self.total_cost = self.third_screen.total_cost_2
        self.hub = self.third_screen.hub_2
        self.ship = self.third_screen.ship_2
        self.origin = self.third_screen.origin_2
        self.plot_routes_phase1(self.origin, self.hub)
        
    def plot_routes_phase1(self, origin, hub):
      
        self.figure.clear() 
        self.canvas.draw_idle()
        self.port_name_dict, self.ship_dict, self.port_cood= self.third_screen.portName()
        
        plot = self.figure.add_subplot(111)
        #origin 
        is_first_origin = True
        for port_id in origin:
            x,y = self.port_cood[port_id]
            label = 'Origin' if is_first_origin else None
            name = self.port_name_dict[port_id]
            plot.scatter(x, y, color='blue', marker='o', label=label if port_id == origin[0] else "", s=10)
            plot.text(x + 0.2, y + 0.1, port_id, fontsize=5)
            is_first_origin = False
        
        #hub
        is_first_hub = True
        for port_id in hub:
            x, y = self.port_cood[port_id]
            label = 'Hub' if is_first_hub else None
            name = self.port_name_dict[port_id]
            plot.scatter(x, y, color='red',marker='s', label=label if port_id == hub[0] else "", s= 10)
            plot.text(x + 0.05, y + 0.05, name, fontsize=10)
            is_first_hub = False
        
        #link origin vs hub
        for i in range(len(origin)):
            origin_id = origin[i]
            hub_id = hub[i]
            x1, y1 = self.port_cood[origin_id]
            x2, y2 = self.port_cood[hub_id]
            plot.plot([x1, x2], [y1, y2], color='gray', linestyle='--', linewidth=1)  
                
        
        plot.legend()
        plot.grid(True)
        plot.set_title(f"Phase 1 ")
        plot.set_xlabel(f"x coodinate")
        plot.set_ylabel(f"y_coodinate")
        self.canvas.draw() 

    def plot_phase2(self):
        self.cost_phase2, self.route_phase_2 = self.third_screen.cost_phase2, self.third_screen.route_phase_2
        self.port_name_dict, self.ship_dict, self.port_cood = self.third_screen.portName()
        self.figure.clear() 
        self.canvas.draw_idle()
    
        all_ports = [port_id for route in self.route_phase_2 for port_id in route]
        port_counts = Counter(all_ports)
        
        plot = self.figure.add_subplot(111)
        labeled = {"Gateway port": False, "Feeder port": False}
        for idx, route_id in enumerate(self.route_phase_2):
            for i, port_id in enumerate(route_id):
                x, y = self.port_cood[port_id]
    
                # Marker & label
                if port_counts[port_id] > 1:
                    marker = '^'
                    color = 'orange'
                    label = 'Gateway port' if not labeled['Gateway port'] else None
                    labeled['Gateway port'] = True
                else:
                    marker = 'o'
                    color = 'blue'
                    label = 'Feeder port' if not labeled['Feeder port'] else None
                    labeled['Feeder port'] = True
    
                plot.scatter(x, y, color=color, marker=marker, label=label, s=20)
                plot.text(x + 0.05, y + 0.05, port_id, fontsize=10)
    
             
                if i < len(route_id) - 1:
                    next_port = route_id[i + 1]
                    x2, y2 = self.port_cood[next_port]
                    plot.annotate(
                        '', xy=(x2, y2), xytext=(x, y),
                        arrowprops=dict(
                            arrowstyle='-|>',    
                            color='gray',        
                            lw=1.5,             
                            linestyle='dashed'   
                        )
                    )
    
        plot.legend()
        plot.grid(True)
        plot.set_title("Phase 2")
        plot.set_xlabel("X Coordinate")
        plot.set_ylabel("Y Coordinate")
        self.canvas.draw()
                             
        

        
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.stacked_widget = QStackedWidget()
        self.first = FirstScreen(self.stacked_widget)
        self.second = SecondScreen(self.stacked_widget)
        self.third = ThirdScreen(self.stacked_widget, self.first,self.second) 
        self.four   = FourthScreen(self.stacked_widget, self.first, self.second, self.third)

        self.stacked_widget.addWidget(self.first)
        self.stacked_widget.addWidget(self.second)
        self.stacked_widget.addWidget(self.third)
        self.stacked_widget.addWidget(self.four)

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
        self.setWindowTitle("Strategic Feeder Network For Optimized Maritime Gateway")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
    
           

