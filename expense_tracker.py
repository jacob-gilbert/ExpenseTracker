import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.expense_dataframe = pd.DataFrame()
        self.curr_index = 0
        self.curr_expense = "Load Expenses"

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

        # layout for sort visuals
        sort_grid_widget = QWidget()
        sort_grid_layout = QGridLayout()
        sort_grid_widget.setLayout(sort_grid_layout)
        self.stack.addWidget(sort_grid_widget)

        # create text for current expense
        # made this label self. because i need it to be accessible to be changed in a function call
        self.curr_ex_label = QLabel(self.curr_expense) 
        sort_grid_layout.addWidget(self.curr_ex_label, 0, 0, 1, 3)

        # create new cateogory for sorting
        new_cat = QPushButton("Create Category")
        sort_grid_layout.addWidget(new_cat, 1, 0)

        # skip button for sort
        skip_button = QPushButton("Skip")
        sort_grid_layout.addWidget(skip_button, 1, 1)
        skip_button.clicked.connect(self.skip_to_next_row_df)

        # delete button for sort
        delete_button = QPushButton("Delete")
        sort_grid_layout.addWidget(delete_button, 1, 2)
        delete_button.clicked.connect(self.delete_current_expense)

        temp_button = QPushButton("Temporary")
        self.stack.addWidget(temp_button)

        # create button that takes in csv data and add it to the sidebar
        new_transactions_button = QPushButton("Upload Transactions") # create button
        new_transactions_button.adjustSize() # resizes button so all of the text is shown
        new_transactions_button.clicked.connect(lambda: self.stack.setCurrentIndex(0)) # connects the button being clicked to changing what is displayed from the stack
        sidebar.addWidget(new_transactions_button) # adds the button to the sidebar layout

        new_sort_button = QPushButton("Sort")
        new_sort_button.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        new_sort_button.clicked.connect(self.set_current_expense)
        sidebar.addWidget(new_sort_button)

        other_temp_button = QPushButton("Temporary")
        sidebar.addWidget(other_temp_button)
        other_temp_button.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        sidebar.addStretch() # pushes everything to the top

        # add the stack to the main window
        main_layout.addWidget(self.stack)

    def load_new_expenses(self):
        self.expense_dataframe = pd.read_csv("transactions.csv")

        # Example: if it is a debit expense credit is nan but same as a $0 credit so change nan to 0 in these columns
        self.expense_dataframe["Debit"] = self.expense_dataframe["Debit"].fillna(0)
        self.expense_dataframe["Credit"] = self.expense_dataframe["Credit"].fillna(0)

        # Print this to confirm it loaded and updated properly
        print(self.expense_dataframe.head())

    # when the sort button is clicked set the first row of our expense dataframe to the label
    # make sure there are expenses in the dataframe first
    def set_current_expense(self):
        if len(self.expense_dataframe) != 0:
            temp_exp = self.expense_dataframe.iloc[self.curr_index] # this gets the current expense out of row self.current_index
            
            # the .setText() function can read html so added underlines to key words, must use <br> instead of /n for new lines since it is looking for html
            self.curr_expense = f"<u>Date</u>: {temp_exp.iloc[0]}<br><u>Category</u>: {temp_exp.iloc[4]}<br><u>Description</u>: {temp_exp.iloc[3]}<br><u>Debit/Credit</u>: {temp_exp.iloc[5]}/{temp_exp.iloc[6]}"

            # reset the text of the label
            self.curr_ex_label.setText(self.curr_expense)

    # the current index indicates which expense is being processed by the user;
    # make sure that there are expenses and that the index does not surpass the
    # size of the dataframe while iterating through it
    def skip_to_next_row_df(self):
        df_size = len(self.expense_dataframe)
        if df_size != 0:
            self.curr_index = (self.curr_index + 1) % df_size

            # now update the current expense with the new index
            self.set_current_expense()
        else:
            print("Expense Dataframe is empty!")

    # make sure there are expenses and update the current index after the delete
    def delete_current_expense(self):
        if len(self.expense_dataframe) != 0:
            self.expense_dataframe.drop(self.curr_index, inplace=True) # deleting row without creating new dataframe

            # update the current expense
            self.set_current_expense()
        

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