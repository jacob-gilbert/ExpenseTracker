from PyQt6.QtCore import QDate
from expense import Expense

# -------------------
# Expense Navigation
# -------------------
def set_current_expense(window):
    if len(window.expense_dataframe) != 0:
        temp_exp = window.expense_dataframe.iloc[window.curr_index]
        window.curr_expense = f"<u>Date</u>: {temp_exp.iloc[0]}<br><u>Category</u>: {temp_exp.iloc[4]}<br><u>Description</u>: {temp_exp.iloc[3]}<br><u>Debit/Credit</u>: {temp_exp.iloc[5]}/{temp_exp.iloc[6]}"
        window.curr_ex_label.setText(window.curr_expense)

def skip_to_next_row_df(window):
    df_size = len(window.expense_dataframe)
    if df_size != 0:
        window.curr_index = (window.curr_index + 1) % df_size
        set_current_expense(window)
    else:
        print("Expense Dataframe is Empty, Cannot Skip")

# -------------------
# Category Management
# -------------------
def create_new_cat(window):
    new_cat, ok = window.get_new_category()
    if ok and new_cat:
        window.cat_combo_box.addItems([new_cat])

def delete_current_expense(window):
    if len(window.expense_dataframe) != 0:
        window.expense_dataframe.drop(window.curr_index, inplace=True)
        window.expense_dataframe.reset_index(drop=True, inplace=True)
        new_len_exp_df = len(window.expense_dataframe)

        if new_len_exp_df == 0:
            window.curr_expense = "Load Expenses"
            window.curr_ex_label.setText(window.curr_expense)
            return

        if new_len_exp_df == window.curr_index:
            window.curr_index -= 1

        set_current_expense(window)
    else:
        print("Expense Dataframe is Empty, Cannot Delete")

def categorize_expense(window):
    category = window.cat_combo_box.currentText()
    exp = window.expense_dataframe.iloc[window.curr_index]

    debit = float(exp.iloc[5]) > 0
    amount = exp.iloc[5] if debit else -exp.iloc[6]

    new_exp = Expense(category, exp.iloc[0], exp.iloc[3], amount)

    if category in window.category_expense_map:
        window.category_expense_map[category].append(new_exp)
    else:
        window.category_expense_map[category] = [new_exp]

    delete_current_expense(window)

# -------------------
# Viewing / Totals
# -------------------
def update_expenses_viewed(window, start, end):
    if window.categories:
        curr_cat = window.view_cat_combo_box.currentText()
        view_text = ""

        if curr_cat == "All":
            for cat in window.category_expense_map:
                exps_from_cat = window.category_expense_map[cat]
                for exp in exps_from_cat:
                    expense_date = QDate.fromString(exp.get_date(), "yyyy-MM-dd")
                    if start <= expense_date <= end:
                        view_text += exp.__str__() + "\n\n"
        else:
            try:
                exps_from_cat = window.category_expense_map[curr_cat]
                for exp in exps_from_cat:
                    expense_date = QDate.fromString(exp.get_date(), "yyyy-MM-dd")
                    if start <= expense_date <= end:
                        view_text += exp.__str__() + "\n\n"
            except:
                view_text = "No expenses listed under this category"

        window.view_text_edit.setPlainText(view_text)

def update_totals(window, start, end):
    first_text = "Total Spend: $"
    running_text = ""
    all_total = 0

    for cat in window.category_expense_map:
        exps_from_cat = window.category_expense_map[cat]
        cat_total = 0
        for exp in exps_from_cat:
            expense_date = QDate.fromString(exp.get_date(), "yyyy-MM-dd")
            if start <= expense_date <= end:
                cat_total = int(exp.get_amount())
        running_text += f"{cat} Total Spend: ${cat_total}\n\n"
        all_total += cat_total

    first_text += f"{all_total}\n\n"
    window.total_text_edit.setPlainText(first_text + running_text)