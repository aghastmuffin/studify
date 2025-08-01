import sys, os, playsound, json, datetime #NoQA: F401, E401
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (QFormLayout, QTableWidget, QTableWidgetItem, QScrollArea, QFrame, QTextEdit, QDialog, QDialogButtonBox, QStackedWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QMainWindow, QSpacerItem, QSizePolicy, QGraphicsOpacityEffect, QFileDialog)# noqa: F401
import PyQt6.QtCore as QtCore
import datetime as dt
import _cloud
app = QApplication(sys.argv)
TOTAL_STUDY = 0
TOTAL_BREAK = 0
THIS_STUDY = 0
THIS_BREAK = 0

#BETA FLAGS
_TOGGLESM2 = False #Use the SM2 algorithm for flashcards
_PRODFLAG = False
#Heyo! I don't know how you found this source code, but please report it to levi@adsforafrica.me for a reward!


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
        self.height = 300
        self.width = 400
        self.setMaximumHeight(300)
        self.setMaximumWidth(400)
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
        self.card_s = self.basic_study_cards()
        self.card_e = self.edit_studyset()
        self.stacked_widget.addWidget(self.title_s)
        self.stacked_widget.addWidget(self.study_s)
        self.stacked_widget.addWidget(self.pause_s)
        self.stacked_widget.addWidget(self.complete_s)
        self.stacked_widget.addWidget(self.card_s)
        self.stacked_widget.addWidget(self.card_e)

        self.stacked_widget.currentChanged.connect(self.on_page_changed)
        self.stacked_widget.setCurrentIndex(0)

        self.setMaximumHeight(9999)
        self.setMaximumWidth(9999)

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
        creds = QLabel("Created By Levi B. 태선")
        welcome_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        spacer = QSpacerItem(0, 100)
        start = QPushButton("Start")
        stats = QPushButton("Stats")
        flashcard = QPushButton("Start Flashcards")
        
        
        start.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(1)))  # Switch to study scene
        flashcard.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(4)))  # Switch to flashcard scene
        layout.addWidget(welcome_title)
        layout.addWidget(QLabel("A Study App for Students"))
        layout.addSpacerItem(spacer)
        layout.addWidget(start)
        layout.addWidget(self.clock_l)
        layout.addWidget(flashcard)
        statsholder.addWidget(stats)
        statsholder.setAlignment(Qt.AlignmentFlag.AlignRight)
        statsholder.addWidget(creds)
        statsholder.setAlignment(Qt.AlignmentFlag.AlignTop)

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

    def basic_study_cards(self):
        """
        Create the study cards scene layout FLASHCARDS
        """
        
        self.card_index = 0
        scene = QWidget()
        layout = QVBoxLayout(scene)
        
        # Get study set data
        self.studytmp = self.load_studyset()
        self.study = self.studytmp[0]
        # Set up title
        title = QLabel(f"Study Set - {self.study[0]['friendly_name']}")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.edit_studysetbtn = QPushButton("Edit Study Set ")
        self.edit_studysetbtn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(5))

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
        layout.addWidget(self.edit_studysetbtn)
        
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
        #convert to directory
        self.sfilename = "studify/studysets/study_set_test.json"
        if os.path.exists(self.sfilename):
            with open(self.sfilename, 'r') as f:
                print(f)
                cards = json.load(f)
                try:
                    if "SM2" in cards[1]["flags"]:
                        return [cards, True]
                    else:
                        # cards[1] exists but doesn't have SM2 flag
                        return [cards, False]
                except IndexError:
                    # cards[1] doesn't exist, so add it
                    cards.append({"flags": ["NON-SM2"]})
                    return [cards, False]
        else:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(self.sfilename), exist_ok=True)
            
            with open(self.sfilename, 'w') as f:
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
                return [cards, False]  # Return consistent format
            
        
    def edit_studyset(self):
            # Create the main scene widget with size constraints
            scene = QWidget()
            scene.setMinimumWidth(400)  # Match your window's minimum width
            scene.setMinimumHeight(300)  # Match your window's minimum height
            
            # Remember the current window size
            current_size = self.size()
            
            # Create main layout
            main_layout = QVBoxLayout(scene)
            main_layout.setContentsMargins(10, 10, 10, 10)
            
            # Create header
            header_label = QLabel("Edit Study Set")
            header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
            main_layout.addWidget(header_label)
            
            # Create a scroll area to contain all card editing widgets
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)  # Important - allows the widget to resize with content
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            
            # Set a fixed height for the scroll area to prevent window expansion
            scroll_area.setMinimumHeight(200)
            scroll_area.setMaximumHeight(200)  # This will force scrolling rather than expanding
            
            # Create the container widget for the scroll area
            scroll_content = QWidget()
            card_layout = QVBoxLayout(scroll_content)
            card_layout.setSpacing(15)
            
            # Add existing cards to the layout
            for i in range(len(self.study[0]["questions"])):
                # Create a group box for each card
                card_group = QWidget()
                card_group_layout = QVBoxLayout(card_group)
                card_group_layout.setContentsMargins(5, 5, 5, 10)
                
                del_btn = QPushButton(f"Delete Card {i+1}")
                del_btn.clicked.connect(lambda _, i=i: self.rm_card(i))
                card_group_layout.addWidget(del_btn)

                # Add card number label
                card_label = QLabel(f"Card {i+1}")
                card_label.setStyleSheet("font-weight: bold;")
                
                # Add question and answer text edits
                question = self.study[0]["questions"][i]["question"]
                answer = self.study[0]["questions"][i]["answer"]
                
                question_label = QLabel("Question:")
                question_edit = QTextEdit(f"{question}")
                question_edit.setMaximumHeight(80)  # Limit height
                
                answer_label = QLabel("Answer:")
                answer_edit = QTextEdit(f"{answer}")
                answer_edit.setMaximumHeight(80)  # Limit height
                
                # Add widgets to the card group layout
                card_group_layout.addWidget(card_label)
                card_group_layout.addWidget(question_label)
                card_group_layout.addWidget(question_edit)
                card_group_layout.addWidget(answer_label)
                card_group_layout.addWidget(answer_edit)
                
                # Add a line separator except for the last card
                if i < len(self.study[0]["questions"]) - 1:
                    separator = QFrame()
                    separator.setFrameShape(QFrame.Shape.HLine)
                    separator.setFrameShadow(QFrame.Shadow.Sunken)
                    card_group_layout.addWidget(separator)
                
                # Add the card group to the main layout
                card_layout.addWidget(card_group)
            
            # Set the scroll content and add it to the scroll area
            scroll_area.setWidget(scroll_content)
            
            # Create form for adding new cards
            new_card_widget = QWidget()
            new_card_layout = QVBoxLayout(new_card_widget)
            new_card_layout.setContentsMargins(0, 10, 0, 10)
            
            new_card_header = QLabel("Add New Card")
            new_card_header.setStyleSheet("font-weight: bold;")
            
            self.new_question = QTextEdit()
            self.new_question.setPlaceholderText("Enter new question...")
            self.new_question.setMaximumHeight(60)
            
            self.new_answer = QTextEdit()
            self.new_answer.setPlaceholderText("Enter new answer...")
            self.new_answer.setMaximumHeight(60)
            
            new_card_layout.addWidget(new_card_header)
            new_card_layout.addWidget(QLabel("Question:"))
            new_card_layout.addWidget(self.new_question)
            new_card_layout.addWidget(QLabel("Answer:"))
            new_card_layout.addWidget(self.new_answer)
            
            # Create button layout at the bottom
            button_layout = QHBoxLayout()
            
            add_btn = QPushButton("Add Card")
            add_btn.clicked.connect(self.add_new_card)
            
            return_btn = QPushButton("Return to Study")
            return_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
            
            # Add buttons to button layout
            button_layout.addWidget(add_btn)
            button_layout.addWidget(return_btn)
            
            # Add all components to main layout
            main_layout.addWidget(scroll_area)
            main_layout.addWidget(new_card_widget)
            main_layout.addLayout(button_layout)
            
            # Restore the original window size
            self.resize(current_size)
            
            return scene
    def rm_card(self, i: int):
        # Create confirmation dialog
        rm_conf = QDialog(self)
        rm_conf.setWindowTitle("Confirm Deletion")
        rm_layout = QVBoxLayout(rm_conf)
        rm_layout.addWidget(QLabel(f"Are you sure you want to delete card {i+1}?"))
        rm_layout.addWidget(QLabel("This action cannot be undone."))
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No)
        button_box.accepted.connect(rm_conf.accept)
        button_box.rejected.connect(rm_conf.reject)
        rm_layout.addWidget(button_box)
        
        # Show dialog and check result
        result = rm_conf.exec()
        
        if result == QDialog.DialogCode.Accepted:
            # User confirmed deletion - remove the card
            if 0 <= i < len(self.study[0]["questions"]):
                del self.study[0]["questions"][i]
                
                # Save the updated data to file
                with open(self.sfilename, 'w') as f:
                    json.dump(self.study, f)
                
                # Refresh the edit view to reflect changes
                current_index = self.stacked_widget.currentIndex()
                new_edit_view = self.edit_studyset()
                self.stacked_widget.removeWidget(self.stacked_widget.widget(5))
                self.stacked_widget.insertWidget(5, new_edit_view)
                self.stacked_widget.setCurrentIndex(current_index)
        
        
    def add_new_card(self):
        question = self.new_question.toPlainText()
        answer = self.new_answer.toPlainText()
        
        if not question or not answer:
            # Show error message
            error_dialog = QDialog(self)
            error_dialog.setWindowTitle("Error")
            error_layout = QVBoxLayout(error_dialog)
            error_layout.addWidget(QLabel("Please enter both question and answer."))
            ok_button = QPushButton("OK")
            ok_button.clicked.connect(error_dialog.accept)
            error_layout.addWidget(ok_button)
            error_dialog.exec()
            return
            
            
        # Add the card
        self.bck_add_card(question, answer)
        
        # Clear the input fields
        self.new_question.clear()
        self.new_answer.clear()
        
        # Refresh the edit view
        current_index = self.stacked_widget.currentIndex()
        new_edit_view = self.edit_studyset()
        self.stacked_widget.removeWidget(self.stacked_widget.widget(5))
        self.stacked_widget.insertWidget(5, new_edit_view)
        self.stacked_widget.setCurrentIndex(current_index)
        
        # Show confirmation
        success_dialog = QDialog(self)
        success_dialog.setWindowTitle("Success")
        success_layout = QVBoxLayout(success_dialog)
        success_layout.addWidget(QLabel("Card added successfully!"))
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(success_dialog.accept)
        success_layout.addWidget(ok_button)
        success_dialog.exec()

    def bck_add_card(self, question, answer):
        with open(self.sfilename, 'r') as f:
            cards = json.load(f)
        
        # Append the new card to the first study set
        cards[0]["questions"].append({
            "question": question,
            "answer": answer
        })
        
        # Write the updated cards back to the file
        with open(self.sfilename, 'w') as f:
            json.dump(cards, f)
        
        # Update the study variable to reflect changes
        self.study = cards
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
        if index == 5:
            self.width = 800
            self.height = 600
            self.resize(self.width, self.height)  # Actually resize the window


    

                
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
