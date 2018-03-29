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
    minerName = ""
    minerAddr = ""
    transactions = []
    proof = -1
    prevHash = -1

    # block secondary features
    proofTypes = []
    #miners = [0, 0, 0, 0] # might need to make this more dynamic
    #totalMiners = 0

    ##################################
    # Constructor
    def __init__(self, index, proofType, timeStamp, minerName, minerAddr, transactions, proof, prevHash):

        # Setup data members
        self.index = index
        self.proofType = proofType
        self.timeStamp = timeStamp
        self.minerName = minerName
        self.minerAddr = minerAddr
        self.transactions = transactions
        self.proof = proof
        self.prevHash = prevHash

        self.proofTypes = [0, self.timeStamp, self.proof, self.prevHash]

    
    ####################################
    # class functions
    '''
    def getLeastMinedStat(self):

        # providing stat of 
        minMiners = self.miners[1]
        minIndex = 1

        for i in range(2, len(self.miners)):

            if(self.miners[i] < minMiners):
                minMiners = self.miners[i]
                minIndex = 1

        return [minMiners, minIndex, self.proofTypes[minIndex]]
                

    def incrementMiners(self, minedProof):

        if(minedProof != -1):
            self.miners[minedProof] += 1

        self.totalMiners += 1

    def decrementMiners(self, minedProof):

        if(minedProof != -1):
            self.miners[minedProof] -= 1

        self.totalMiners -= 1
    '''

    def getProof(self, proofIndex):
        return self.proofTypes[proofIndex]

    ####################################
    # Getter and Setter Functions
    def getIndex(self):
        return self.index

    def getProofType(self):
        return self.proofType

    def getTimeStamp(self):
        return self.timeStamp

    def getMinerName(self):
        return self.minerName
    
    def getMinerAddr(self):
        return self.minerAddr

    def getTransactions(self):
        return self.transactions

    '''
    def getMiners(self):
        return self.miners
    '''

    ###################################
    # toString Functions
    def toString(self):

        # for hashing, just a concatenation of everything
        string = str(self.index) + str(self.proofType) + str(self.timeStamp) 
        string += self.minerName + self.minerAddr + str(self.proof) + str(self.prevHash)
        return string

    def toStringProofType(self, proofType):

        # based on the given proof type grab the corresponding string
        return str(self.proofTypes[proofType])

    def toNiceString(self):

        # write string in the format of chain file
        niceString = "index:" + str(self.index) + "\n"
        niceString += "proofType:" + str(self.proofType) + "\n"
        niceString += "timeStamp:" + str(self.timeStamp) + "\n"
        niceString += "minerName:" + self.minerName + "\n"
        niceString += "minerAddr:" + self.minerAddr + "\n"

        # need to run through the transactions
        for transact in self.transactions:

            niceString += "sender:" + transact.sender + "\n"
            niceString += "reciever:" + transact.reciever + "\n"
            niceString += "amount:" + str(transact.amount) + "\n"

        niceString += "proof:" + str(self.proof) + "\n"
        niceString += "prevHash:" + str(self.prevHash) + "\n"

        # return the string
        return niceString
