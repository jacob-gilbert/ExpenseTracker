import pandas as pd
import json
from expense import Expense
from PyQt6.QtWidgets import QFileDialog

def load_new_expenses(file_path="transactions.csv"):
    """
    Loads transactions.csv into a dataframe and fills NaN values with 0.
    Returns the dataframe.
    """
    expense_dataframe = pd.read_csv(file_path)
    expense_dataframe["Debit"] = expense_dataframe["Debit"].fillna(0)
    expense_dataframe["Credit"] = expense_dataframe["Credit"].fillna(0)
    return expense_dataframe

def load_old_expenses():
    """
    Loads expenses.json into a dictionary mapping categories to Expense objects.
    Returns the dictionary.
    """
    category_expense_map = {}

    try:
        with open("expenses.json", "r") as f:
            data = json.load(f)
            for key in data:
                category_expense_map[key] = []
                exps = data[key]
                for exp in exps:
                    category_expense_map[key].append(Expense(exp["category"],
                                                                  exp["date"],
                                                                  exp["place"],
                                                                  exp["amount"]))
    except FileNotFoundError:
        pass

    return category_expense_map

def browse_and_load_csv(parent=None):
    """
    Opens a file dialog to select a CSV and returns a loaded DataFrame.
    parent: QWidget that will own the dialog
    """
    file_path, _ = QFileDialog.getOpenFileName(
        parent,
        "Select CSV file",
        "",
        "CSV Files (*.csv)"
    )
    if file_path:
        df = pd.read_csv(file_path)
        df["Debit"] = df["Debit"].fillna(0)
        df["Credit"] = df["Credit"].fillna(0)
        return df, file_path
    return None, None

def load_categories():
    """
    Loads categories from categories.json and returns a list.
    """
    try:
        with open("categories.json", "r") as f:
            data = json.load(f)
            return data["categories"]
    except FileNotFoundError:
        return []
    
def save_categories(categories):
    """
    Saves the list of categories to categories.json
    """
    data_to_save = {"categories": categories}
    try:
        with open("categories.json", "w") as f:
            json.dump(data_to_save, f, indent=4)
        print("Categories saved to categories.json")
    except Exception as e:
        print(f"Failed to save categories: {e}")

def save_expenses(category_expense_map):
    """
    Saves the category_expense_map to expenses.json
    """
    if not category_expense_map:
        return  # Do not overwrite if empty
    expense_dict = {}
    for key in category_expense_map:
        expense_dict[key] = [exp.to_dict() for exp in category_expense_map[key]]
    try:
        with open("expenses.json", "w") as f:
            json.dump(expense_dict, f, indent=4)
        print("Expenses saved to expenses.json")
    except Exception as e:
        print(f"Failed to save expenses: {e}")