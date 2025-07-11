import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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
    

def load_new_expenses():
    expense_dataframe = pd.read_csv("")

def load_old_expenses():
    expense_dataframe = pd.read_csv("")

def save_expenses(analyzed_expenses):
    analyzed_expenses.to_csv("", index = False)



if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()