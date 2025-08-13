import pandas as pd
import json
from expense import Expense 
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QComboBox, QInputDialog, QPlainTextEdit, QDateEdit
from PyQt6.QtCore import QDate

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
            self.categories = load_categories()
            self.cat_combo_box.addItems(self.categories)
        except:
            pass

        # button that confirms the category selection for an expense
        select_cat_button = QPushButton("Select Category")
        sort_grid_layout.addWidget(select_cat_button, 1, 2)
        select_cat_button.clicked.connect(self.categorize_expense)

        # view
        # layout for view visuals
        view_grid_widget = QWidget()
        view_grid_layout = QGridLayout()
        view_grid_widget.setLayout(view_grid_layout)
        self.stack.addWidget(view_grid_widget)
        
        # user will view expenses based on their category, so give them a drop down list of categories to choose from
        # will take the categories from the sort combo box
        self.view_cat_combo_box = QComboBox()
        view_grid_layout.addWidget(self.view_cat_combo_box, 0, 0)
        self.view_cat_combo_box.addItems(["All"] + self.categories)

        # get today's date and one month before
        today = QDate.currentDate()
        one_month_before = today.addMonths(-1)

        # start date selector
        start_date = QDateEdit()
        start_date.setCalendarPopup(True)
        start_date.setDate(one_month_before)  # default: 1 month before today
        view_grid_layout.addWidget(start_date, 1, 0)

        # end date selector
        end_date = QDateEdit()
        end_date.setCalendarPopup(True)
        end_date.setDate(today)  # default: today
        view_grid_layout.addWidget(end_date, 1, 1)

        # create text edit in view to see all the expenses and its read only
        self.view_text_edit = QPlainTextEdit()
        view_grid_layout.addWidget(self.view_text_edit, 2, 0, 1, 2)
        self.view_text_edit.setReadOnly(True)


        # total
        # layout for total visuals
        total_grid_widget = QWidget()
        total_grid_layout = QGridLayout()
        total_grid_widget.setLayout(total_grid_layout)
        self.stack.addWidget(total_grid_widget)

        # start date selector
        total_start_date = QDateEdit()
        total_start_date.setCalendarPopup(True)
        total_start_date.setDate(one_month_before)  # default: 1 month before today
        total_grid_layout.addWidget(total_start_date, 0, 0)

        # end date selector
        total_end_date = QDateEdit()
        total_end_date.setCalendarPopup(True)
        total_end_date.setDate(today)  # default: today
        total_grid_layout.addWidget(total_end_date, 0, 1)

        # create text edit in view to see all the expenses and its read only
        self.total_text_edit = QPlainTextEdit()
        total_grid_layout.addWidget(self.total_text_edit, 1, 0, 1, 2)
        self.total_text_edit.setReadOnly(True)

        # connect the signal that the user selected a new option in the combo box to the function updates the plaintextbox below it
        self.view_cat_combo_box.currentIndexChanged.connect(lambda: self.update_expenses_viewed(start_date.date(), end_date.date()))

        # connect the signal that the user updated the time range to the function that updates which expenses are displayed
        start_date.dateChanged.connect(lambda: self.update_expenses_viewed(start_date.date(), end_date.date()))
        end_date.dateChanged.connect(lambda: self.update_expenses_viewed(start_date.date(), end_date.date()))

        # create button that takes in csv data and add it to the sidebar
        new_transactions_button = QPushButton("Upload Transactions") # create button
        new_transactions_button.adjustSize() # resizes button so all of the text is shown
        new_transactions_button.clicked.connect(lambda: self.stack.setCurrentIndex(0)) # connects the button being clicked to changing what is displayed from the stack
        sidebar.addWidget(new_transactions_button) # adds the button to the sidebar layout

        new_sort_button = QPushButton("Sort")
        new_sort_button.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        new_sort_button.clicked.connect(self.set_current_expense)
        sidebar.addWidget(new_sort_button)

        view_button = QPushButton("View")
        sidebar.addWidget(view_button)
        view_button.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        view_button.clicked.connect(lambda: self.update_expenses_viewed(start_date.date(), end_date.date()))

        total_button = QPushButton("Total")
        sidebar.addWidget(total_button)
        total_button.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        total_button.clicked.connect(lambda: self.update_totals(total_start_date.date(), total_end_date.date()))

        # connect the signal that the user updated the time range to the function that updates which expenses are displayed
        total_start_date.dateChanged.connect(lambda: self.update_totals(total_start_date.date(), total_end_date.date()))
        total_end_date.dateChanged.connect(lambda: self.update_totals(total_start_date.date(), total_end_date.date()))

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
                #print(key)
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

    
    # update the plaintextbox in view based on the category the user chooses, when viewing all it is sorted by category
    def update_expenses_viewed(self, start, end):
        # verify that at least on category exists
        if self.categories:
            curr_cat = self.view_cat_combo_box.currentText()
            view_text = ""

            # if the current category is "All" display all expenses
            if curr_cat == "All":
                # iterate through the categories
                for cat in self.category_expense_map:
                    exps_from_cat = self.category_expense_map[cat]
                    # for each expense, add it to the string of expenses to be viewed and newline
                    for exp in exps_from_cat:
                        # convert the expense's date a QDate
                        expense_date = QDate.fromString(exp.get_date(), "yyyy-MM-dd")

                        # compare the date to the date time range
                        # if within the range add the expense to be displayed
                        if start <= expense_date <= end:
                            view_text += exp.__str__()
                            view_text += "\n\n"
            else:
                # put all of the expenses from the selected category into view while ignoring expenses from other categories
                try:
                    exps_from_cat = self.category_expense_map[curr_cat]
                    for exp in exps_from_cat:
                        # convert the expense's date a QDate
                        expense_date = QDate.fromString(exp.get_date(), "yyyy-MM-dd")

                        # compare the date to the date time range
                        # if within the range add the expense to be displayed
                        if start <= expense_date <= end:
                            view_text += exp.__str__()
                            view_text += "\n\n"
                except:
                    view_text = "No expenses listed under this category"

            # update the text box with the expenses
            self.view_text_edit.setPlainText(view_text)

    # calculates the total expenses spent in every category and all combined to be displayed including
    # only expenses who's date falls between the start and end date range
    def update_totals(self, start, end):
        first_text = "Total Spend: $"
        running_text = ""
        all_total = 0
        for cat in self.category_expense_map:
            exps_from_cat = self.category_expense_map[cat]

            # for each expense, add the expense's total to the running total of all expenses in that category
            cat_total = 0
            for exp in exps_from_cat:
                # convert the expense's date a QDate
                expense_date = QDate.fromString(exp.get_date(), "yyyy-MM-dd")

                # compare the date to the date time range
                # if within the range add the expense to the total
                if start <= expense_date <= end:
                    cat_total = int(exp.get_amount())

            running_text += f"{cat} Total Spend: ${cat_total}"
            running_text += "\n\n"

            all_total += cat_total

        # after the for loop every category's total has been calculated and added together into all_total var
        first_text += f"{all_total}\n\n"

        # update the text box with the total
        self.total_text_edit.setPlainText(first_text + running_text)



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

        # if the category_expense_map is empty do not write to expenses.json
        # if no expenses are loaded this prevents the program from writing to the file as it
        # may delete expenses that exist but weren't uploaded to the program
        if not self.category_expense_map:
            event.accept()
            return

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


def load_categories():
    with open("categories.json", "r") as f:
        data = json.load(f)
        return data["categories"]


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()