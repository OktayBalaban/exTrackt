# -*- coding: utf-8 -*-
"""
Created on Sat Jul  8 19:28:58 2023

@author: oktay
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from TrackProcessor import TrackProcessor
import os

class Supervisor(QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def __init__(self, track_processor, input_file_path, output_directory_path):
        super().__init__()
        self.track_processor = track_processor
        self.input_file_path = input_file_path
        self.output_directory_path = output_directory_path
        self.instrumentsToStay = []
        self.shift_semitones = 0
        self.output_file_path = ""

    @QtCore.pyqtSlot()
    def process(self, vocals, bass, drums, other):
        if vocals:
            self.instrumentsToStay.append("vocals")
        if bass:
            self.instrumentsToStay.append("bass")
        if drums:
            self.instrumentsToStay.append("drums")
        if other:
            self.instrumentsToStay.append("other")
        
        self.track_processor.separate(self.input_file_path, self.output_directory_path)
        
        # Get the song name as spleeter creates a folder with song name
        self.song_name = os.path.splitext(os.path.basename(self.input_file_path))[0]
        
        self.track_processor.merge(self.instrumentsToStay, self.output_directory_path, self.song_name)
        self.finished.emit()
        
    @QtCore.pyqtSlot(int)  # Add int argument annotation
    def shift_pitch(self, shift_amount):
        try:
            # Perform the pitch shift
            song_name = os.path.splitext(os.path.basename(self.input_file_path))[0]
            output_file_path = os.path.join(self.output_directory_path, f"{song_name}.wav")
            self.track_processor.shift_pitch(self.input_file_path, output_file_path, shift_amount)
    
        except ValueError:
            # Show an error message if the input can't be converted to an integer
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
            error_dialog.setWindowTitle("Input Error")
            error_dialog.setText("Semitone shift amount must be an integer.")
            error_dialog.exec_()
    
        self.finished.emit()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("exTrackt")
        
        #Track Processor
        self.track_processor = TrackProcessor()

        # Buttons
        self.input_button = QtWidgets.QPushButton("Select Input Song")
        self.input_button.clicked.connect(self.select_input_file)

        self.output_button = QtWidgets.QPushButton("Select Output Directory")
        self.output_button.clicked.connect(self.select_output_directory)

        self.separate_button = QtWidgets.QPushButton("Process")
        self.separate_button.clicked.connect(self.process)
        self.separate_button.setDisabled(True)

        self.shift_pitch_button = QtWidgets.QPushButton("Shift Pitch")
        self.shift_pitch_button.clicked.connect(self.shift_pitch)
        self.shift_pitch_button.setDisabled(True)

        # Checkboxes for instruments
        self.vocals_checkbox = QtWidgets.QCheckBox("Vocals")
        self.bass_checkbox = QtWidgets.QCheckBox("Bass")
        self.drums_checkbox = QtWidgets.QCheckBox("Drums")
        self.guitar_checkbox = QtWidgets.QCheckBox("Guitar/Other")
        
        # Semitone shift input field
        self.semitone_shift_input = QtWidgets.QLineEdit()
        self.semitone_shift_input.setValidator(QtGui.QIntValidator())
        self.semitone_shift_input.setPlaceholderText("Enter number of semitones to shift")
        self.semitone_shift_input.textChanged.connect(self.check_button_changes)

        # Labels to display selected paths
        self.input_file_label = QtWidgets.QLabel("No input file selected")
        self.output_directory_label = QtWidgets.QLabel("No output directory selected")

        # Path strings
        self.input_file_path = ""
        self.output_directory_path = ""

        # Checkboxes for instruments inside a GroupBox
        self.instruments_group = QtWidgets.QGroupBox("Instruments")
        self.instruments_layout = QtWidgets.QVBoxLayout()
        self.instruments_layout.addWidget(self.vocals_checkbox)
        self.instruments_layout.addWidget(self.bass_checkbox)
        self.instruments_layout.addWidget(self.drums_checkbox)
        self.instruments_layout.addWidget(self.guitar_checkbox)
        self.instruments_group.setLayout(self.instruments_layout)

        # Main layout using GridLayout
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.input_button, 0, 0)
        self.layout.addWidget(self.input_file_label, 0, 1)
        self.layout.addWidget(self.output_button, 1, 0)
        self.layout.addWidget(self.output_directory_label, 1, 1)
        self.layout.addWidget(self.instruments_group, 2, 0, 1, 2)
        self.layout.addWidget(self.separate_button, 3, 0, 1, 2)
        self.layout.addWidget(self.semitone_shift_input, 4, 0)
        self.layout.addWidget(self.shift_pitch_button, 4, 1)

        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)

        # Stylesheet
        stylesheet = """
            QPushButton {
                font: bold 12px;
                background-color: #333;
                color: white;
            }
            QLabel {
                font: 12px;
            }
            QGroupBox {
                font: bold 14px;
                color: #333;
            }
        """
        self.setStyleSheet(stylesheet)


    def select_input_file(self):
        options = QtWidgets.QFileDialog.Options()
        self.input_file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                                         "Audio Files (*.mp3 *.wav)", options=options)
        if self.input_file_path:
            self.input_file_label.setText(f"Selected input file: {self.input_file_path}")
        
        self.check_button_changes()

    def select_output_directory(self):
        options = QtWidgets.QFileDialog.Options()
        self.output_directory_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory", "",
                                                                                options=options)
        if self.output_directory_path:
            self.output_directory_label.setText(f"Selected output directory: {self.output_directory_path}")

        self.check_button_changes()
            
            
    def process(self):
        
        self.thread = QtCore.QThread()
        self.supervisor = Supervisor(self.track_processor, self.input_file_path, self.output_directory_path)
        self.supervisor.moveToThread(self.thread)
        self.thread.started.connect(lambda: self.supervisor.process(self.vocals_checkbox.isChecked(), 
                                                            self.bass_checkbox.isChecked(),
                                                            self.drums_checkbox.isChecked(), 
                                                            self.guitar_checkbox.isChecked()))
        self.supervisor.finished.connect(self.thread.quit)
        self.supervisor.finished.connect(self.supervisor.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()
        self.separate_button.setDisabled(True)

        # Enable the button when process is finished
        self.supervisor.finished.connect(lambda: self.separate_button.setDisabled(False))
    
    def shift_pitch(self):
        try:
            # Get the semitone shift amount from the input field
            semitones = int(self.semitone_shift_input.text())
          
            self.shift_thread = QtCore.QThread()
            self.shift_worker = Supervisor(self.track_processor, self.input_file_path, self.output_directory_path)
            self.shift_worker.moveToThread(self.shift_thread)
            self.shift_thread.started.connect(lambda: self.shift_worker.shift_pitch(semitones))
            self.shift_worker.finished.connect(self.shift_thread.quit)
            self.shift_worker.finished.connect(self.shift_worker.deleteLater)
            self.shift_thread.finished.connect(self.shift_thread.deleteLater)

            self.shift_thread.start()
    
        except ValueError:
            # Show an error message if the input can't be converted to an integer
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
            error_dialog.setWindowTitle("Input Error")
            error_dialog.setText("Semitone shift amount must be an integer.")
            error_dialog.exec_()
        
    def check_button_changes(self):
        # Enable the process button if both input and output paths are specified
        if self.input_file_path and self.output_directory_path:
            self.separate_button.setEnabled(True)
            
        # Enable the shift pitch button if an input file is selected and a semitone shift is entered
        if self.input_file_path and self.semitone_shift_input.text() and self.output_directory_path:
            self.shift_pitch_button.setEnabled(True)
        
        


