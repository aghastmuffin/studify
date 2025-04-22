import sys, os, pickle, playsound
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFormLayout, QStackedWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QMainWindow, QSpacerItem, QSizePolicy, QGraphicsOpacityEffect# noqa: F401
import datetime as dt

app = QApplication(sys.argv)
TOTAL_STUDY = 0
TOTAL_BREAK = 0
THIS_STUDY = 0
THIS_BREAK = 0

class Effects:
    def fade(self, widget):
        """Apply a fade-out effect to the given widget."""
        self.effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(self.effect)

        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(1000)  # Duration in milliseconds
        self.animation.setStartValue(1)  # Fully visible
        self.animation.setEndValue(0)  # Fully transparent
        self.animation.start()

    def unfade(self, widget):
        """Apply a fade-in effect to the given widget."""
        self.effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(self.effect)

        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(1000)  # Duration in milliseconds
        self.animation.setStartValue(0)  # Fully transparent
        self.animation.setEndValue(1)  # Fully visible
        self.animation.start()
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Placement title")
        #self.setWindowIcon(QIcon("icon.png"))
        self.setFixedHeight(300)
        self.setFixedWidth(400)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.stacked_widget = QStackedWidget()
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.stacked_widget)

        self.clock = QTimer(self)
        self.clock.timeout.connect(self.update_clock)
        self.clock.start(60000)
        self.clock_l = QLabel()
        self.clock_l.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.clock_l.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.timer_container = QWidget()
        timer_layout = QVBoxLayout(self.timer_container)
        self.l_timer = QLabel("00:00")
        self.l_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.l_timer.setStyleSheet("font-size: 22px; font-weight: bold;")
        timer_layout.addWidget(self.l_timer)
        

        self.title_s = self.title_scene()
        self.study_s = self.study_scene()
        self.pause_s = self.pause_scene()
        self.complete_s = self.complete_scene()
        self.stacked_widget.addWidget(self.title_s)
        self.stacked_widget.addWidget(self.study_s)
        self.stacked_widget.addWidget(self.pause_s)
        self.stacked_widget.addWidget(self.complete_s)
        self.stacked_widget.setCurrentIndex(0)

    def title_scene(self):
        self.flag = False
        # Create a central widget and set it
        scene = QWidget()
        statsholder = QHBoxLayout()

        # Create a layout
        layout = QVBoxLayout(scene)

        # Create and configure the welcome title
        welcome_title = QLabel("Welcome to Studyify")
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        spacer = QSpacerItem(0, 100)
        start = QPushButton("Start")
        stats = QPushButton("Stats")
        
        start.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(1)))  # Switch to study scene
        layout.addWidget(welcome_title)
        layout.addSpacerItem(spacer)
        layout.addWidget(start)
        layout.addWidget(self.clock_l)
        statsholder.addWidget(stats)
        statsholder.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout.addLayout(statsholder)
        
        return scene
    
    def study_scene(self):
        """
        Create the study scene layout
        """
        self.flag = True
        self.count = 0
        scene = QWidget()
        layout = QVBoxLayout(scene)
        start_stop = QFormLayout()
        start_stop.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Add a label to the study scene
        goodluck = QLabel("Study Well")
        
        goodluck.setAlignment(Qt.AlignmentFlag. AlignLeft)
        goodluck.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        layout.addWidget(goodluck)
        layout.addWidget(self.l_timer)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        self.timer.start(1000)

        # Add a back button to return to the title scene
        pause = QPushButton("Pause")
        back_button = QPushButton("Stop")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))  # Switch to title scene
        pause.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(2)))
        start_stop.addRow(pause, back_button)
        layout.addWidget(self.clock_l)
        layout.addLayout(start_stop)


        return scene
    
    def showTime(self):
        if self.stacked_widget.currentIndex() == 1:
            self.count += 1
            # adding action to timer
            # Convert seconds to hours, minutes, and seconds
            hours = self.count // 3600
            minutes = (self.count % 3600) // 60
            seconds = self.count % 60

            # Format the time string dynamically
            if hours > 0:
                time_str = f"{hours:02}:{minutes:02}:{seconds:02}"  # Include hours
            else:
                time_str = f"{minutes:02}:{seconds:02}"  # Exclude hours

            self.l_timer.setText(str(time_str))
    
    def update_clock(self):
        """update the clocl element"""
        now = dt.datetime.now()
        self.clock_l.setText(now.strftime("%H:%M"))

    def pause_scene(self):
        scene = QWidget()
        layout = QVBoxLayout(scene)
        # Add a label to the study scene
        paused = QLabel("Paused")
        paused.setAlignment(Qt.AlignmentFlag.AlignLeft)
        paused.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        unpause = QPushButton("Unpause")
        back_button = QPushButton("Stop")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        unpause.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(paused)
        layout.addWidget(self.l_timer)
        layout.addWidget(self.clock_l)
        layout.addWidget(unpause)
        layout.addWidget(back_button)
        return scene
    
    def complete_scene(self):
        scene = QWidget()
        layout = QVBoxLayout(scene)
        # Add a label to the study scene
        completed = QLabel("Good Job!")
        completed.setAlignment(Qt.AlignmentFlag.AlignLeft)
        completed.setStyleSheet("font-size: 18px; font-weight: bold;")
        quick_stat = QLabel("You studied for: " + str(self.l_timer.text()))
        quick_stat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        quick_stat.setStyleSheet("font-size: 22px; font-weight: bold;")
        back_button = QPushButton("Restart")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(completed)
        layout.addWidget(self.l_timer)
        layout.addWidget(quick_stat)
        layout.addWidget(self.clock_l)
        layout.addWidget(back_button)
        return scene

if __name__ == "__main__":
    # Use MainWindow instead of QWidget
    window = MainWindow()
    window.show()
    app.exec()
