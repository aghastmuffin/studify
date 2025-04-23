import sys, os, playsound, json
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFormLayout, QDialog, QDialogButtonBox, QStackedWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QMainWindow, QSpacerItem, QSizePolicy, QGraphicsOpacityEffect# noqa: F401
import datetime as dt
import _cloud
app = QApplication(sys.argv)
TOTAL_STUDY = 0
TOTAL_BREAK = 0
THIS_STUDY = 0
THIS_BREAK = 0

class TodoManager:
    def __init__(self, filename="todos.json"):
        self.filename = filename
        self.todos = self.load_todos()
        
    def load_todos(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_todos(self):
        with open(self.filename, 'w') as f:
            json.dump(self.todos, f)
    
    def add_todo(self, title, description="", due_date=None, completed=False):
        todo = {
            "title": title,
            "description": description,
            "due_date": due_date,
            "completed": completed
        }
        self.todos.append(todo)
        self.save_todos()
    
    def delete_todo(self, index):
        if 0 <= index < len(self.todos):
            del self.todos[index]
            self.save_todos()
            
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

        self.timer_time = ""
        self.setWindowTitle("Placement title")
        icon_path = os.path.join(os.path.dirname(__file__), "assets/mini-logo.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setMinimumHeight(300)
        self.setMinimumWidth(400)
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
        self.l_timer = QLabel("unupdated time")
        self.l_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.l_timer.setStyleSheet("font-size: 22px; font-weight: bold;")
        timer_layout.addWidget(self.l_timer)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        self.timer.start(1000)
        self.l_timer.setText("00:00")

        self.title_s = self.title_scene()
        self.study_s = self.study_scene()
        self.pause_s = self.pause_scene()
        self.complete_s = self.complete_scene()
        self.stacked_widget.addWidget(self.title_s)
        self.stacked_widget.addWidget(self.study_s)
        self.stacked_widget.addWidget(self.pause_s)
        self.stacked_widget.addWidget(self.complete_s)

        self.stacked_widget.currentChanged.connect(self.on_page_changed)
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
        layout.addWidget(self.timer_container)


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
            hours = self.count // 3600
            minutes = (self.count % 3600) // 60
            seconds = self.count % 60
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
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        unpause.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(paused)
        pause_timer = QLabel("await")
        pause_timer.setObjectName("timer")
        pause_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pause_timer.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(pause_timer)
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
        quick_stat = QLabel("You studied for: ")
        quick_stat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        quick_stat.setStyleSheet("font-size: 22px; font-weight: bold;")
        back_button = QPushButton("Restart")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(completed)
        complete_timer = QLabel("incomplete_update")
        complete_timer.setObjectName("timer")
        complete_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        complete_timer.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(quick_stat)
        layout.addWidget(complete_timer)
        layout.addWidget(self.clock_l)
        layout.addWidget(back_button)
        return scene

    def on_page_changed(self, index):
        if index in [2, 3, 4]:
            current_time = self.l_timer.text()
            scene = self.stacked_widget.widget(index)
            for timer_widget in scene.findChildren(QLabel, "timer"):
                timer_widget.setText(current_time)
            if index == 4:
                self.timer_time = self.l_timer.text()
class CustomDialog(QDialog):
    def __init__(self, message="", title="", buttons=None):
        super().__init__()

        self.setWindowTitle(title or "Update Available")

        # Default buttons if none provided
        if buttons is None:
            QBtn = (
                QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No
            )
        else:
            QBtn = buttons

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Handle custom button clicks if provided
        if buttons is not None:
            for button_type, callback in buttons.items():
                if isinstance(callback, callable):
                    self.buttonBox.button(button_type).clicked.connect(callback)

        layout = QVBoxLayout()
        message_label = QLabel(message or "There is an update available. Do you wish to update now?")
        message_label.setWordWrap(True)  # Allow text to wrap
        layout.addWidget(message_label)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

def updatefunc():
    update_info = _cloud.check_for_updates()
    
    if update_info.get("update_available", False):
        updater = _cloud.UpdateChecker()
        if updater.is_git_repo():
            if CustomDialog().exec():
                print("Updating...")
                result = updater.update()
                
                if result["success"]:
                    print(result["message"])
                    if "details" in result:
                        print(f"Details: {result['details']}")
                else:
                    print(f"Update failed: {result['message']}")
                    if "error" in result:
                        print(f"Error: {result['error']}")
            else:
                print("Update cancelled.")
        else:
            print("This is not a git repository. Cannot update automatically.")
            print("fixing.")
            os.system("git init")
            updatefunc()


if __name__ == "__main__":
    # Use MainWindow instead of QWidget

    window = MainWindow()
    window.show()
    app.exec()
