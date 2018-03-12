# Nick Caspers
# 2018-3-11
#################################

# File: Transaction.py
# Purpose: Meant to be holders and managers of data for a single transaction

class Transaction:

    # Data members
    sender = ""
    reciever = ""
    amount = -1

    ############################
    # Constructor
    def __init__(self, sender, reciever, amount):

        # Setup the data members
        self.sender = sender
        self.reciever = reciever
        self.amount = amount

