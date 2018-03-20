# Nick Caspers
# 2018-3-11
#################################

# File: Block.py
# Purpose: meant to create containers to hold the various aspects of a block

class Block:

    ## Data Members
    # Block fundamental aspects
    index = -1
    proofType = -1
    timeStamp = -1
    transactions = []
    proof = -1
    prevHash = -1

    # block secondary features
    proofTypes = []

    ##################################
    # Constructor
    def __init__(self, index, proofType, timeStamp, transactions, proof, prevHash):

        # Setup data members
        self.index = index
        self.proofType = proofType
        self.timeStamp = timeStamp
        self.transactions = transactions
        self.proof = proof
        self.prevHash = prevHash

        self.proofTypes = [self.timeStamp, self.proof, self.prevHash]

    
    ####################################
    # Getter and Setter Functions
    def getIndex(self):
        return self.index

    def getProofType(self):
        return self.proofType

    def getTransactions(self):
        return self.transactions

    ###################################
    # toString Functions
    def toString(self):

        # for hashing, just a concatenation of everything
        string = str(self.index) + str(self.proofType) + str(self.timeStamp) + str(self.proof) + str(self.prevHash)
        return string

    def toStringProofType(self, proofType):

        # based on the given proof type grab the corresponding string
        return str(self.proofTypes[proofType])

    def toNiceString(self):

        # write string in the format of chain file
        niceString = "index:" + str(self.index) + "\n"
        niceString += "proofType:" + str(self.proofType) + "\n"
        niceString += "timeStamp:" + str(self.timeStamp) + "\n"

        # need to run through the transactions
        for transact in self.transactions:

            niceString += "sender:" + transact.sender + "\n"
            niceString += "reciever:" + transact.reciever + "\n"
            niceString += "amount:" + str(transact.amount) + "\n"

        niceString += "proof:" + str(self.proof) + "\n"
        niceString += "prevHash:" + str(self.prevHash) + "\n"

        # return the string
        return niceString
