import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.expense_dataframe = pd.DataFrame()

        # create a layout for the expense tracker
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget) # add layout to main window

        # create layout for sidebar
        sidebar = QVBoxLayout()
        main_layout.addLayout(sidebar)

        # create a stacked widget --> changes what is displayed when a button on the sidebar is clicked
        self.stack = QStackedWidget()

        # create what is displayed when "Upload Transactions" is clicked
        upload_button = QPushButton("Upload")
        self.stack.addWidget(upload_button)
        upload_button.clicked.connect(self.load_new_expenses)

        temp_button = QPushButton("Temporary")
        self.stack.addWidget(temp_button)


        # create button that takes in csv data and add it to the sidebar
        new_transactions_button = QPushButton("Upload Transactions") # create button
        new_transactions_button.adjustSize() # resizes button so all of the text is shown
        new_transactions_button.clicked.connect(lambda: self.stack.setCurrentIndex(0)) # connects the button being clicked to changing what is displayed from the stack
        sidebar.addWidget(new_transactions_button) # adds the button to the sidebar layout

        other_temp_button = QPushButton("Temporary")
        sidebar.addWidget(other_temp_button)
        other_temp_button.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        sidebar.addStretch() # pushes everything to the top

        # add the stack to the main window
        main_layout.addWidget(self.stack)

    def load_new_expenses(self):
        self.expense_dataframe = pd.read_csv("transactions.csv")
        print(self.expense_dataframe.head())
        

class Expense:
    def __init__(self, category, date, amount):
        self.cat = category # what kind of expense it is
        self.dt = date # date the expense was made
        self.amnt = amount # the cost of the expense

    def get_category(self):
        return self.cat
    
    def get_date(self):
        return self.dt
    
    def get_amount(self):
        return self.amnt


def load_old_expenses():
    expense_dataframe = pd.read_csv("")

def save_expenses(analyzed_expenses):
    analyzed_expenses.to_csv("", index = False)



if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()