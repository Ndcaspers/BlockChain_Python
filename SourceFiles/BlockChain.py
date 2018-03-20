# Nick Caspers
# 2018-3-11
#################################

# File: BlockChain.py 
# Purpose: The class in charge of interacting, maintaining, and reading the block chain files.

import hashlib
import time

from Block import *
from Transaction import *

class BlockChain:

    ## Data members
    # Names
    chainName = ""
    chainDirPath = ""
    chainFilePath = ""
    UnconfTransactPath = ""
    configPath = ""

    # Chain Config Parameters
    owner = ""
    coinCap = -1
    coinHashKey = ""

    # Chain Blocks and Transactions
    memChain = True
    chain = []
    #confTransactions = []
    unconfTransactions = []

    #################################################
    # Constructor
    def __init__(self, chainName, memChain=True):

        print("[START] Setting up BlockChain...")

        ## setup data members
        # setup the files
        self.chainName = chainName
        self.setupChainFiles()

        print("Block Chain File Setup Completed.")

        # Obtain Configuration parameters
        self.setupMemConfig()

        print("Obtained <" + self.chainName + "> Config Parameters")

        # Check chain file
        chainFile = open(self.chainFilePath, 'r')
        noLines = not(chainFile.readline())
        chainFile.close()

        if(noLines):
            
            self.rootBlock = Block(0, 0, time.time(), [], 0, self.hashConfigParameters())
            self.writeRootBlock()

        print("Checked Chain File.")

        # Chain to Memory
        self.memChain = memChain

        if(memChain):
            self.setupMemChain()

        print("Chain is in Memory.")
        print("[COMPLETED] Setting up Block Chain.")
            

    # Constructor Helper Functions
    def setupChainFiles(self):

        # setup dir path
        self.chainDirPath = "../Chains/" + self.chainName

        # setup the other file paths
        self.chainFilePath = self.chainDirPath + "/" + self.chainName + ".chain"
        self.unconfTransactPath = self.chainDirPath + "/" + self.chainName + ".transact"
        self.configPath = self.chainDirPath + "/" + self.chainName + ".config"

    def writeRootBlock(self):

        # write the root block attributes into the file
        niceBlockString = self.rootBlock.toNiceString()

        print("- No Root Block, Writing one in...\n")
        print(niceBlockString)
        
        chainFile = open(self.chainFilePath, 'w')
        chainFile.write(niceBlockString)
        chainFile.close()
        
    ##################################################
    # Class Methods
    def validProof(self, blockIndex, proofType, proof):

        print("- Checking Proof <" + str(proof) + ">")
        print("\tagainst block " + str(blockIndex) + " with proofType" + str(proofType))

        # Get block hash of the proofType
        block = self.chain[blockIndex]
        blockHash = self.hashString(block.toStringProofType(proofType))

        endHash = self.hashString(blockHash + proof)

        print("- endHash: " + endHash)
        print("- Accepted?: " + str(endHash[4:] == self.coinHashKey))

        return (endHash[4:] == self.coinHashKey)

    def newBlock(self, proof, proofType, prevBlockIndex):

        print("- Creating New Block...")

        # initialize
        prevBlock = self.chain[prevBlockIndex]
        currentBlockIndex = (prevBlockIndex * self.proofAmount) + proofType
        
        validBlock = self.validProof(prevBlockIndex, proofType, proof) and self.isEmptyBlock(blockIndex)

        if(not(validBlock)):
            return getEmptyBlock()
        
        # Create the new block
        index = (previous.getIndex() * 3) + proofType
        prevHash = hashBlock(prevBlock)
        newBlock = Block(index, proofType, time.time(), self.unconfTransactions, proof, prevHash)

        # add it to the chain in its proper place
        self.chain[index] = newBlock

        # need to rewrite the file
        print("- Rewriting Chain File...")
        chainFile = open(self.chainFilePath, 'w')
        chainFile.write(chain[0].toNiceString())
        chainFile.close()

        chainFile = open(self.chainFilePath, 'a')

        for i in range(1, len(chain)):

            blockString = chain[i].toNiceString()
            chainFile.write(blockString)

        chainFile.close()

        # reset the unconfirmed transactions
        self.unconfTransactions = []

        print("- New Block Added and Chain File Revised.")

        return newBlock
        

    def newTransaction(self, sender, reciever, amount):

        print("- Creating a new transaction.")

        # create a new transaction
        transaction = Transaction(sender, reciever, amount)

        # need to check if the transaction is possibel
        if(self.validTransaction(transaction)):
            print("- Transaction Accepted.")
            addUnconfTransaction(transaction)
            self.unconfTransactions.append(transaction)
            return True

        else:
            print("- Transaction Rejected.")
            return False

    ##################################################
    ## Helper Functions
    # Config File reading helper functions
    def setupMemConfig(self):

        # read in the various config aspects of the Chain
        configFile = open(self.configPath, 'r')

        currentLine = configFile.readline()

        while(currentLine):

            # take out the new line characters
            currentLine = currentLine.replace('\n', '')

            print("- Current Config Line: " + currentLine)

            # parse through the various apsects
            lineSplit = currentLine.split(":")
            lineIndicator = lineSplit[0]
            lineValue = lineSplit[1]

            if(lineIndicator == "owner"):
                self.owner = lineValue

            elif(lineIndicator == "coin cap"):
                self.coinCap = int(lineValue)

            elif(lineIndicator == "coin hash key"):
                self.coinHashKey = lineValue

            # increment
            currentLine = configFile.readline()

        print("- Owner found: " + self.owner)
        print("- Coin Cap found: " + str(self.coinCap))
        print("- Coin Hash Key found: " + self.coinHashKey)

    # Chain File reading helpers functions
    def setupMemChain(self):
            
        # Read-in Blocks from files
        chainFile = open(self.chainFilePath, 'r')
            
        currentLine = chainFile.readline()
        currentBlockLines = []

        while(currentLine):

            # take out the new line character
            currentLine = currentLine.replace('\n', '')

            print("- Current Line: " + currentLine)

            # If empty, no block yet
            if(currentLine == ""):
                self.addEmptyBlock()
                print("-- No Block, Added Empty")

            # If "index" new block"
            elif(currentLine[5:] == "index"):

                # add the block if there was a block read
                if(len(currenBlockLines) != 0):
                    self.addBlockFromLines(currentBlockLines)

                # start reading in the new block
                currentBlockLines = [currentLine]

            else:

                # adding lines to current block
                currentBlockLines += [currentLine]

            # Increment
            currentLine = chainFile.readline()

        # There is still one block left over potentially
        if(len(currentBlockLines) != 0):
            self.addBlockFromLines(currentBlockLines)

        # close the file
        chainFile.close() 

        print("- Amount of Blocks Found: " + str(len(self.chain)))

    def addEmptyBlock(self):
    
        # Create an empty block and add it to the list
        #emptyBlock = Block(-1, -1, -1, [], -1, -1)
        self.chain.append(self.getEmptyBlock())

    def addBlockFromLines(self, blockLines):

        ## Parse lines
        index = int( (blockLines[0].split(':'))[-1] )
        blockType = int ( (blockLines[1].split(':'))[-1] )
        timeStamp = float( (blockLines[2].split(':'))[-1] )

        # run through transactions
        transactions = []

        for i in range(3, len(blockLines) - 2, 3):

            # create Transaction and append
            sender = ((blockLines[i]).split(':'))[-1]
            reciever = ((blockLines[i + 1]).split(':'))[-1]
            amount = float( ((blockLines[i + 2]).split(':'))[-1] )

            transaction = Transaction(sender, reciever, amount)
            transactions.append(transaction)

        proof = blockLines[-2].split(':')[-1]
        previousHash = blockLines[-1].split(':')[-1]

        # add empty blocks to fill chain uptill index
        while(len(self.chain) <= index):
            self.addEmptyBlock()

        # add block to the list
        block = Block(index, blockType, timeStamp, transactions, proof, previousHash)
        self.chain[index] = block

        print("-- Added Block to Mem:\n")
        print(block.toNiceString())

    # Mem Block manipulation helper functions
    def hashBlock(block):

        # encode in unicode string and return
        blockString = block.toString()
        unicodeBlockString = blockString.encode()

        return hashlib.sha256(uniBlockString).hexdigest()


    # Transaction helper functions
    def validTransaction(self, transaction):

        # get sender balance
        sender = transaction.sender
        sendingAmount = transaction.amount

        senderBalance = 0.0

        # check if owner
        ownerFlag = (sender == self.owner)

        # run through each block
        for block in chain:

            if(ownerFlag and block.getIndex() != -1 and block.getTimeStamp != -1 and len(block.getTransactions()) == 0):
                senderBalance += 0.01

            if(block.getMiner() == sender):
                senderBalance += 1.0

            for currentTransact in block.getTransactions():

                if(currentTransact.sender == sender):
                    senderBalance += currentTransact.amount

                elif(currentTransact.reciever == sender):
                    senderBalance -= currentTransact.amount

        # run through the unconfirmed transactions
        for unconfTransact in unconfTransactions:

            # check if sending amount vs balance
            if(currentTransact.sender == sender):
                senderBalance += currentTransact.amount

            elif(currentTransact.reciever == sender):
                senderBalance -= currentTransact.amount

        # check amount vs sender balance
        return (sendingAmount <= senderBalance) 

    def addUnconfTransaction(self, transaction):

        # add to memory list
        self.unconfTransactions.append(transaction)

        # add to file
        sender = "sender:" + String(transaction.sender) + "\n"
        reciever = "reciever:" + String(transaction.reciever) + "\n"
        amount = "amount:" + String(transaction.amount) + "\n"

        unconfTransactionFile = open(self.unconfTransactPath, 'a')

        unconfTransactionFile.write(sender)
        unconfTransactionFile.write(reciever)
        unconfTransactionFile.write(amount)


    # Generic Helper Functions
    def isEmptyBlock(self, index):

        # Block could be outside chain, which is "empty"
        if(index >= len(self.chain)):
            return True

        else:
            block = self.chain[index]
            return (block.getIndex() == -1 and block.getTimeStamp() == -1 and block.getProofType() == -1)

    def getEmptyBlock(self):
        
        return Block(-1, -1, -1, [], -1, -1)

    def hashString(self, string):

        unicodeString = string.encode()
        return hashlib.sha256(unicodeString).hexdigest()

    def hashConfigParameters(self):

        rootHash = self.hashString(self.owner + str(self.coinCap))
        return rootHash

        

