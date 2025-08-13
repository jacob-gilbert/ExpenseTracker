import pandas as pd
import json
from expense import Expense

def load_new_expenses():
    expense_dataframe = pd.read_csv("transactions.csv")

    # Example: if it is a debit expense credit is nan but same as a $0 credit so change nan to 0 in these columns
    expense_dataframe["Debit"] = expense_dataframe["Debit"].fillna(0)
    expense_dataframe["Credit"] = expense_dataframe["Credit"].fillna(0)

    # Print this to confirm it loaded and updated properly
    print(expense_dataframe.head())