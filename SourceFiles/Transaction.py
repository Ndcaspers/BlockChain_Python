# Nick Caspers
# 2018-3-11
#################################

# File: Transaction.py
# Purpose: Meant to be holders and managers of data for a single transaction

class Transaction:

    # Data members
    sender = ""
    senderAddr = ""
    reciever = ""
    recieverAddr = ""
    amount = -1

    ############################
    # Constructor
    def __init__(self, sender, senderAddr, reciever, recieverAddr, amount):

        # Setup the data members
        self.sender = sender
        self.senderAddr = senderAddr
        self.reciever = reciever
        self.recieverAddr = recieverAddr
        self.amount = amount

