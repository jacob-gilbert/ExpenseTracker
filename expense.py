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