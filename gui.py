# -*- coding: utf-8 -*-
"""
Created on Sat Jul  8 19:28:58 2023

@author: oktay
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from TrackProcessor import TrackProcessor
import time
import os

class Supervisor(QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def __init__(self, track_processor, input_file_path, output_directory_path):
        super().__init__()
        self.track_processor = track_processor
        self.stemCount = 5
        self.input_file_path = input_file_path
        self.output_directory_path = output_directory_path
        self.instrumentsToStay = []
        self.shift_semitones = 0
        self.output_file_path = ""

    @QtCore.pyqtSlot()
    def process(self):
        
        if self.vocals_checkbox.isChecked():
            instrumentsToStay.append("vocals")
        if self.bass_checkbox.isChecked():
            instrumentsToStay.append("bass")
        if self.drums_checkbox.isChecked():
            instrumentsToStay.append("drums")
        if self.piano_checkbox.isChecked():
            instrumentsToStay.append("piano")
        if self.guitar_checkbox.isChecked():
            instrumentsToStay.append("other")
        
        self.track_processor.separate(self.stemCount, self.input_file_path, self.output_directory_path)
        
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

        self.setWindowTitle("Music Separator")
        
        #Track Processor
        self.track_processor = TrackProcessor()

        #Buttons
        self.input_button = QtWidgets.QPushButton("Select Input Song")
        self.input_button.clicked.connect(self.select_input_file)

        self.output_button = QtWidgets.QPushButton("Select Output Directory")
        self.output_button.clicked.connect(self.select_output_directory)

        self.separate_button = QtWidgets.QPushButton("Process")
        self.separate_button.clicked.connect(self.process)
        
        # Process button
        self.separate_button = QtWidgets.QPushButton("Process")
        self.separate_button.clicked.connect(self.process)
        self.separate_button.setDisabled(True)
        
        # Pitch shift button
        self.shift_pitch_button = QtWidgets.QPushButton("Shift Pitch")
        self.shift_pitch_button.clicked.connect(self.shift_pitch)
        self.shift_pitch_button.setDisabled(True)


        # Checkboxes for instruments
        self.vocals_checkbox = QtWidgets.QCheckBox("Vocals")
        self.bass_checkbox = QtWidgets.QCheckBox("Bass")
        self.drums_checkbox = QtWidgets.QCheckBox("Drums")
        self.piano_checkbox = QtWidgets.QCheckBox("Piano")
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

        # Layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.input_button)
        self.layout.addWidget(self.input_file_label)
        self.layout.addWidget(self.output_button)
        self.layout.addWidget(self.output_directory_label)
        
        self.layout.addWidget(self.vocals_checkbox)
        self.layout.addWidget(self.bass_checkbox)
        self.layout.addWidget(self.drums_checkbox)
        self.layout.addWidget(self.piano_checkbox)
        self.layout.addWidget(self.guitar_checkbox)
        self.layout.addWidget(self.separate_button)
        
        self.layout.addWidget(self.semitone_shift_input)
        self.layout.addWidget(self.shift_pitch_button)


        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)

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
        # Merge selected instruments
        instrumentsToStay = []


        # Create a QThread object
        self.thread = QtCore.QThread()
        # Create a worker object
        self.supervisor = Supervisor(self.track_processor, self.input_file_path, self.output_directory_path)

        # Move worker to the thread
        self.supervisor.moveToThread(self.thread)
        
        # Connect signals and slots
        self.thread.started.connect(self.supervisor.process)
        self.supervisor.finished.connect(self.thread.quit)
        self.supervisor.finished.connect(self.supervisor.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the thread
        self.thread.start()

        # Once the process starts, disable the button
        self.separate_button.setDisabled(True)

        # Enable the button when process is finished
        self.supervisor.finished.connect(lambda: self.separate_button.setDisabled(False))
    
    def shift_pitch(self):
        try:
            # Get the semitone shift amount from the input field
            semitones = int(self.semitone_shift_input.text())
          
            # Create a QThread object for pitch shifting
            self.shift_thread = QtCore.QThread()
            # Create a worker object
            self.shift_worker = Supervisor(self.track_processor, self.input_file_path, self.output_directory_path)
            # Move the worker to the thread
            self.shift_worker.moveToThread(self.shift_thread)
            # Connect signals and slots
            self.shift_thread.started.connect(lambda: self.shift_worker.shift_pitch(semitones))  # Pass semitones argument
            self.shift_worker.finished.connect(self.shift_thread.quit)
            self.shift_worker.finished.connect(self.shift_worker.deleteLater)
            self.shift_thread.finished.connect(self.shift_thread.deleteLater)
            # Start the thread
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
        
        


