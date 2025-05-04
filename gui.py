from dis import show_code
import sys, os, playsound, json, datetime
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QFormLayout, QTableWidget, QTableWidgetItem, QDialog, QDialogButtonBox, QStackedWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QMainWindow, QSpacerItem, QSizePolicy, QGraphicsOpacityEffect# noqa: F401
import PyQt6.QtCore as QtCore
import datetime as dt
import _cloud
app = QApplication(sys.argv)
TOTAL_STUDY = 0
TOTAL_BREAK = 0
THIS_STUDY = 0
THIS_BREAK = 0

class TodoModel(QtCore.QAbstractListModel):
    def __init__(self, *args, todos=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.todos = todos or []

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            status, text = self.todos[index.row()]
            return text

    def rowCount(self, index):
        return len(self.todos)


class TodoManager:
    def __init__(self, filename="todos.json"):
        self.filename = filename
        self.todos = self.load_todos()
        
    def load_todos(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    todos = json.load(f)
                    # Convert date strings back to date objects
                    for todo in todos:
                        if todo.get('due_date'):
                            try:
                                todo['due_date'] = datetime.date.fromisoformat(todo['due_date'])
                            except ValueError:
                                pass  # Keep as string if invalid date
                    return todos
            except:
                return []
        return []


        
    def save_todos(self):
        # Create a copy of todos to modify for saving
        todos_to_save = []
        
        # Convert any date objects to strings
        for todo in self.todos:
            todo_copy = dict(todo)  # Create a copy to avoid modifying the original
            
            # Convert date to string if it's a date object
            if isinstance(todo_copy.get('due_date'), datetime.date):
                todo_copy['due_date'] = todo_copy['due_date'].isoformat()
                
            todos_to_save.append(todo_copy)
        
        # Save the converted todos to file
        with open(self.filename, 'w') as f:
            json.dump(todos_to_save, f)
    
    def add_todo(self, title:str, description:str="", due_date=None, important:bool=False, completed:bool=False):
        # Convert date object to string if it exists
        date_str = due_date.isoformat() if isinstance(due_date, datetime.date) else due_date
        
        todo = {
            "title": title,
            "description": description,
            "due_date": date_str,
            "important": important,
            "completed": completed
        }
        self.todos.append(todo)
        self.save_todos()
    
    def delete_todo(self, index):
        if 0 <= index < len(self.todos):
            del self.todos[index]
            self.save_todos()

    def readall(self):
        return self.todos
    
    def get_todo(self, index):
        if 0 <= index < len(self.todos):
            return self.todos[index]
        return None
    

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

        self.old_pg = 0
        self.todomgr = TodoManager()
        self.timer_time = ""
        self.setWindowTitle("Studify")
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets", "full-logo.png"))
        self.setWindowIcon(QIcon(QPixmap(icon_path)))
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
        self.card_s = self.study_cards()
        self.stacked_widget.addWidget(self.title_s)
        self.stacked_widget.addWidget(self.study_s)
        self.stacked_widget.addWidget(self.pause_s)
        self.stacked_widget.addWidget(self.complete_s)
        self.stacked_widget.addWidget(self.card_s)

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
        flashcard = QPushButton("Start Flashcards")
        
        
        start.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(1)))  # Switch to study scene
        flashcard.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(4)))  # Switch to flashcard scene
        layout.addWidget(welcome_title)
        layout.addSpacerItem(spacer)
        layout.addWidget(start)
        layout.addWidget(self.clock_l)
        layout.addWidget(flashcard)
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
        """update the clock element"""
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

    def study_cards(self):
        """
        Create the study cards scene layout
        """
        self.card_index = 0
        scene = QWidget()
        layout = QVBoxLayout(scene)
        
        # Get study set data
        self.study = self.load_studyset()
        
        # Set up title
        title = QLabel(f"Study Set - {self.study[0]['friendly_name']}")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.edit_studyset = QPushButton("Edit Study Set (implemented in future)")
        self.edit_studyset.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        layout.addWidget(self.edit_studyset)

        # Set up question and answer labels
        self.question = QLabel("Question")
        self.question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.answer = QLabel("Answer Hidden")
        self.answer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.answer.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        # Add the main content to the layout
        layout.addWidget(title)
        layout.addWidget(self.question)
        layout.addWidget(self.answer)
        
        # Create buttons layout (horizontal) instead of table
        button_layout = QHBoxLayout()
        
        # Create and add buttons
        show_a = QPushButton("Show Answer")
        next_q = QPushButton("Next")
        back_q = QPushButton("Back")
        back_button = QPushButton("Back to Menu")
        
        # Add buttons to the horizontal layout
        button_layout.addWidget(show_a)
        button_layout.addWidget(back_q)
        button_layout.addWidget(next_q)
        button_layout.addWidget(back_button)
        
        # Add the button layout to main layout
        layout.addLayout(button_layout)
        
        # Connect signals
        show_a.clicked.connect(lambda: self.show_card())
        next_q.clicked.connect(lambda: self.next_card())
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        return scene
    def next_card(self):
        if self.answer.text() == "Answer Hidden":
            self.show_card()
            return
        else:
            if self.card_index + 1 == len(self.study[0]["questions"]):
                self.card_index = 0
            else:
                self.card_index += 1 
            self.reset_card()
            return

    def reset_card(self):
        cards = self.study 
        question = cards[0]["questions"][self.card_index]["question"]
        answer = "Answer Hidden"
        self.question.setText(question)
        self.answer.setText(answer)

    def show_card(self):
        cards = self.study 
        question = cards[0]["questions"][self.card_index]["question"]
        answer = cards[0]["questions"][self.card_index]["answer"]
        self.question.setText(question)
        self.answer.setText(answer)

    def load_studyset(self):
        filename = "study_set.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                print(f)
                cards = json.load(f)
                return cards
        else:
            with open(filename, 'w') as f:
                cards = [
                    {
                        "friendly_name": "Sample Study Set",
                        "questions": [
                            {"question": "What is the capital of France?", "answer": "Paris"},
                            {"question": "What is 2 + 2?", "answer": "4"},
                            {"question": "What is the largest planet in our solar system?", "answer": "Jupiter"}
                        ]
                    }
                ]
                json.dump(cards, f)
                return cards
        


    def clubs(self):
        """
        Creates the clubview layout, for online interactivity only
        """
        scene = QWidget()
        layout = QVBoxLayout(scene)
        # Add a label to the study scene
        clubs = QLabel("Clubs")
        clubs.setAlignment(Qt.AlignmentFlag.AlignLeft)
        clubs.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        # Add a back button to return to the title scene
        back_button = QPushButton("Back")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(clubs)
    def on_page_changed(self, index):
        self.old_pg = self.stacked_widget.currentIndex()
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
    updatefunc()
    window = MainWindow()
    window.show()
    app.exec()
