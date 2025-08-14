from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QComboBox, QInputDialog, QPlainTextEdit, QDateEdit
from PyQt6.QtCore import Qt, QDate

from expense import Expense
import data_handler as dh
import logic as lg

class DropLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Drop CSV file here")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 2px dashed gray; padding: 40px; font-size: 16px;")
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().endswith('.csv'):
                    self.setStyleSheet("border: 2px dashed green; padding: 40px; font-size: 16px;")
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.csv'):
                # Calls MainWindow method
                self.load_csv(file_path)
                self.setText(f"Loaded: {file_path}")

    def dragLeaveEvent(self, event):
        self.setStyleSheet("border: 2px dashed gray; padding: 40px; font-size: 16px;")

    def load_csv(self, file_path):
        self.expense_dataframe = dh.load_new_expenses(file_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # -------------------
        # Initialize Variables
        # -------------------
        self.expense_dataframe = dh.load_new_expenses()  # initially empty, loaded when user uploads
        self.curr_index = 0
        self.curr_expense = "Load Expenses"
        self.category_expense_map = dh.load_old_expenses()

        # Load categories if they exist
        self.categories = dh.load_categories()

        # -------------------
        # Layout Setup
        # -------------------
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        sidebar = QVBoxLayout()
        main_layout.addLayout(sidebar)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # -------------------
        # Upload Widget
        # -------------------
        upload_grid_widget = QWidget()
        upload_grid_layout = QGridLayout()
        upload_grid_widget.setLayout(upload_grid_layout)
        self.stack.addWidget(upload_grid_widget)

        upload_button = QPushButton("Upload Old Expenses")
        upload_grid_layout.addWidget(upload_button)
        #upload_button.clicked.connect(self.load_new_expenses)
        upload_button.clicked.connect(self.load_old_expenses)

        # -------------------
        # Drop Label
        # -------------------
        self.drop_label = DropLabel(self)
        upload_grid_layout.addWidget(self.drop_label)

        # -------------------
        # Sort Widget
        # -------------------
        sort_grid_widget = QWidget()
        sort_grid_layout = QGridLayout()
        sort_grid_widget.setLayout(sort_grid_layout)
        self.stack.addWidget(sort_grid_widget)

        self.curr_ex_label = QLabel(self.curr_expense)
        sort_grid_layout.addWidget(self.curr_ex_label, 0, 0, 1, 3)

        new_cat = QPushButton("Create Category")
        sort_grid_layout.addWidget(new_cat, 2, 0)
        new_cat.clicked.connect(self.create_new_cat)

        skip_button = QPushButton("Skip")
        sort_grid_layout.addWidget(skip_button, 2, 1)
        skip_button.clicked.connect(self.skip_to_next_row_df)

        delete_button = QPushButton("Delete")
        sort_grid_layout.addWidget(delete_button, 2, 2)
        delete_button.clicked.connect(self.delete_current_expense)

        self.cat_combo_box = QComboBox()
        sort_grid_layout.addWidget(self.cat_combo_box, 1, 0, 1, 2)
        if self.categories:
            self.cat_combo_box.addItems(self.categories)

        select_cat_button = QPushButton("Select Category")
        sort_grid_layout.addWidget(select_cat_button, 1, 2)
        select_cat_button.clicked.connect(self.categorize_expense)

        # -------------------
        # View Widget
        # -------------------
        view_grid_widget = QWidget()
        view_grid_layout = QGridLayout()
        view_grid_widget.setLayout(view_grid_layout)
        self.stack.addWidget(view_grid_widget)

        self.view_cat_combo_box = QComboBox()
        view_grid_layout.addWidget(self.view_cat_combo_box, 0, 0)
        self.view_cat_combo_box.addItems(["All"] + self.categories)

        today = QDate.currentDate()
        one_month_before = today.addMonths(-1)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(one_month_before)
        view_grid_layout.addWidget(self.start_date, 1, 0)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(today)
        view_grid_layout.addWidget(self.end_date, 1, 1)

        self.view_text_edit = QPlainTextEdit()
        view_grid_layout.addWidget(self.view_text_edit, 2, 0, 1, 2)
        self.view_text_edit.setReadOnly(True)

        # Connect signals for view
        self.view_cat_combo_box.currentIndexChanged.connect(lambda: lg.update_expenses_viewed(self, self.start_date.date(), self.end_date.date()))
        self.start_date.dateChanged.connect(lambda: lg.update_expenses_viewed(self, self.start_date.date(), self.end_date.date()))
        self.end_date.dateChanged.connect(lambda: lg.update_expenses_viewed(self, self.start_date.date(), self.end_date.date()))

        # -------------------
        # Total Widget
        # -------------------
        total_grid_widget = QWidget()
        total_grid_layout = QGridLayout()
        total_grid_widget.setLayout(total_grid_layout)
        self.stack.addWidget(total_grid_widget)

        self.total_start_date = QDateEdit()
        self.total_start_date.setCalendarPopup(True)
        self.total_start_date.setDate(one_month_before)
        total_grid_layout.addWidget(self.total_start_date, 0, 0)

        self.total_end_date = QDateEdit()
        self.total_end_date.setCalendarPopup(True)
        self.total_end_date.setDate(today)
        total_grid_layout.addWidget(self.total_end_date, 0, 1)

        self.total_text_edit = QPlainTextEdit()
        total_grid_layout.addWidget(self.total_text_edit, 1, 0, 1, 2)
        self.total_text_edit.setReadOnly(True)

        self.total_start_date.dateChanged.connect(lambda: lg.update_totals(self, self.total_start_date.date(), self.total_end_date.date()))
        self.total_end_date.dateChanged.connect(lambda: lg.update_totals(self, self.total_start_date.date(), self.total_end_date.date()))

        # -------------------
        # Sidebar Buttons
        # -------------------
        new_transactions_button = QPushButton("Upload Transactions")
        new_transactions_button.adjustSize()
        new_transactions_button.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        sidebar.addWidget(new_transactions_button)

        new_sort_button = QPushButton("Sort")
        new_sort_button.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        new_sort_button.clicked.connect(lambda: lg.set_current_expense(self))
        sidebar.addWidget(new_sort_button)

        view_button = QPushButton("View")
        view_button.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        view_button.clicked.connect(lambda: lg.update_expenses_viewed(self, self.start_date.date(), self.end_date.date()))
        sidebar.addWidget(view_button)

        total_button = QPushButton("Total")
        total_button.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        total_button.clicked.connect(lambda: lg.update_totals(self, self.total_start_date.date(), self.total_end_date.date()))
        sidebar.addWidget(total_button)

        sidebar.addStretch()
    
    # -------------------
    # GUI Functions that call logic.py or data_handler.py
    # -------------------
    def load_new_expenses(self):
        self.expense_dataframe = dh.load_new_expenses()

    def load_old_expenses(self):
        self.category_expense_map = dh.load_old_expenses()

    def create_new_cat(self):
        lg.create_new_cat(self)

    def skip_to_next_row_df(self):
        lg.skip_to_next_row_df(self)

    def delete_current_expense(self):
        lg.delete_current_expense(self)

    def categorize_expense(self):
        lg.categorize_expense(self)

    # -------------------
    # New method for input dialog
    # -------------------
    def get_new_category(self):
        return QInputDialog.getText(self, "Create New Category", "Enter name of new category:")

    # -------------------
    # Save on Close
    # -------------------
    def closeEvent(self, event):
        categories = [self.cat_combo_box.itemText(i) for i in range(self.cat_combo_box.count())]
        dh.save_categories(categories)
        dh.save_expenses(self.category_expense_map)
        event.accept()