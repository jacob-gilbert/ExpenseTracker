import pandas as pd
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QComboBox, QInputDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.expense_dataframe = pd.DataFrame()
        self.curr_index = 0
        self.curr_expense = "Load Expenses"
        self.category_expense_map = {}

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
        upload_button.clicked.connect(self.load_old_expenses)

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
        sort_grid_layout.addWidget(new_cat, 2, 0)
        new_cat.clicked.connect(self.create_new_cat)

        # skip button for sort
        skip_button = QPushButton("Skip")
        sort_grid_layout.addWidget(skip_button, 2, 1)
        skip_button.clicked.connect(self.skip_to_next_row_df)

        # delete button for sort
        delete_button = QPushButton("Delete")
        sort_grid_layout.addWidget(delete_button, 2, 2)
        delete_button.clicked.connect(self.delete_current_expense)

        # user will categorize the expense, so give them a drop down list of categories to choose
        # will try to load categories if the json already exists, otherwise the user will have to
        # create them within the program
        self.cat_combo_box = QComboBox()
        sort_grid_layout.addWidget(self.cat_combo_box, 1, 0, 1, 2)
        try:
            self.cat_combo_box.addItems(load_categories())
        except:
            pass


        # button that confirms the category selection for an expense
        select_cat_button = QPushButton("Select Category")
        sort_grid_layout.addWidget(select_cat_button, 1, 2)
        select_cat_button.clicked.connect(self.categorize_expense)

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


    def load_old_expenses(self):
        with open("expenses.json", "r") as f:
            data = json.load(f)
            for key in data:
                self.category_expense_map[key] = []
                exps = data[key]
                for expense in exps:
                    self.category_expense_map[key].append(Expense(expense["category"], expense["date"], expense["place"], expense["amount"]))


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
            print("Expense Dataframe is Empty, Cannot Skip")


    # prompt user for input to create a new category to sort expenses into
    def create_new_cat(self):
        new_cat, ok = QInputDialog.getText(self, "Create New Category", "Enter name of new category:") # ok is a boolean that shows whether the user clicked OK or cancel
        if ok and new_cat: # if user clicked OK and didn't leave textbox blank
            self.cat_combo_box.addItems([new_cat])


    # make sure there are expenses and update the current index after the delete
    def delete_current_expense(self):
        if len(self.expense_dataframe) != 0:
            self.expense_dataframe.drop(self.curr_index, inplace=True) # deleting row without creating new dataframe
            self.expense_dataframe.reset_index(drop=True, inplace=True) # creates new indices for the dataframe inplace and drops old indices
            print(self.expense_dataframe.head())

            # if the end of the dataframe is deleted the index will be out of bounds or if the dataframe becomes empty
            new_len_exp_df = len(self.expense_dataframe)
            if new_len_exp_df == 0: # dataframe is empty
                self.curr_expense = "Load Expenses"

                # reset the text of the label
                self.curr_ex_label.setText(self.curr_expense)
                return
            
            if new_len_exp_df == self.curr_index: # index out of range due to delete
                self.curr_index -= 1

            # update the current expense
            self.set_current_expense()
        else:
            print("Expense Dataframe is Empty, Cannot Delete")

    
    # take the category the user picked and pair it with the current expense
    # save that pairing
    def categorize_expense(self):
        category = self.cat_combo_box.currentText()
        exp = self.expense_dataframe.iloc[self.curr_index]

        # determines if the expense is a credit or debit (debit will be treated as positive)
        debit = False
        if float(exp.iloc[5]) > 0:
            debit = True

        # determine the amount, either debit or credit
        if debit:
            amount = exp.iloc[5]
        else:
            amount = -exp.iloc[6]

        # create new instance of Expense
        new_exp = Expense(category, exp.iloc[0], exp.iloc[3], amount)

        # store the expense based on category in the dictionary
        if category in self.category_expense_map:
            self.category_expense_map[category].append(new_exp)
        else:
            self.category_expense_map[category] = [new_exp]

        # expense has been categorized, now delete it from unsorted list
        self.delete_current_expense()


    # Override closeEvent to export to JSON on close
    def closeEvent(self, event):

        # prepare to save the categories to a json file
        categories = [self.cat_combo_box.itemText(i) for i in range(self.cat_combo_box.count())]
        data_to_save = {
            "categories": categories
        }

        try:
            with open("categories.json", "w") as f:
                json.dump(data_to_save, f, indent=4)
            print("Data saved to output.json")
        except Exception as e:
            print(f"Failed to save category data: {e}")

        # prepare to save expenses to a json file
        expense_dict = {}
        
        for key in self.category_expense_map:
            exp_list = self.category_expense_map[key]
            expense_dict[key] = [exp.to_dict() for exp in exp_list]

        try:
            with open("expenses.json", "w") as f:
                json.dump(expense_dict, f, indent=4)
        except Exception as e:
            print(f"Failed to save expense data: {e}")

        # Accept the close event
        event.accept()
        

class Expense:
    def __init__(self, category, date, place_of_purchase, amount):
        self.cat = category # what kind of expense it is
        self.dt = date # date the expense was made
        self.place = place_of_purchase
        self.amnt = amount # the cost of the expense

    def __str__(self):
        return f"Category: {self.cat}, Date: {self.dt}, Place: {self.place}, Amount: {self.amnt}"
    
    def to_dict(self):
        return {"category" : self.cat, "date" : self.dt, "place" : self.place, "amount" : self.amnt}

    def get_category(self):
        return self.cat
    
    def get_date(self):
        return self.dt
    
    def get_place(self):
        return self.place
    
    def get_amount(self):
        return self.amnt


def load_old_expenses():
    expense_dataframe = pd.read_csv("")


def save_expenses(analyzed_expenses):
    analyzed_expenses.to_csv("", index = False)


def load_categories():
    with open("categories.json", "r") as f:
        data = json.load(f)
        return data["categories"]


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()