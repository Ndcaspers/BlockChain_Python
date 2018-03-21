# Nick Caspers
# 2018-3-11
#################################

# File: BlockChain.py 
# Purpose: The class in charge of interacting, maintaining, and reading the block chain files.

import hashlib
import time
import math

from Block import *
from Transaction import *

class BlockChain:

    ## Data members
    # Names
    chainName = ""
    chainDirPath = ""
    chainFilePath = ""
    unconfTransactPath = ""
    configPath = ""

    # Chain Config Parameters
    owner = ""
    coinCap = -1
    coinHashKey = ""
    proofsPerBlock = -1
    chainLevel = -1

    # Chain Blocks and Transactions
    memChain = True
    chain = []
    #confTransactions = []
    unconfTransactions = []
    minableBlocks = []

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

        # Fill out chain with empty blocks
        iteration = 0
        idealTreeSize = 0

        while(idealTreeSize < len(self.chain)):
            idealTreeSize += (3 ** iteration)
            iteration += 1

        if(iteration != self.chainLevel):
            print("- [ERROR]: chain level does not match length of chain")
            return

        if(self.fullLevel()):
        
            self.addNextLevel()
            self.chainLevel += 1

        while(len(self.chain) < idealTreeSize):
            self.addEmptyBlock()

        print("Chain Level: " + str(self.chainLevel))
        print("Chain Block Amount: " + str(len(self.chain)))
        print("Chain is in Memory.")

        # Obtain the info of blocks available for mining
        print("Getting Minable Blocks...")
        self.getMinableBlocks()

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
        index = (prevBlockIndex * self.proofsPerBlock) + proofType
        
        validBlock = (self.validProof(prevBlockIndex, proofType, proof) and self.isEmptyBlock(index))

        if(not(validBlock)):
            return 1
        
        # Create the new block
        prevHash = self.hashBlock(prevBlock)
        newBlock = Block(index, proofType, time.time(), self.unconfTransactions, proof, prevHash)

        # add it to the chain, remove it from minable
        self.chain[index] = newBlock
        self.removeMinableBlock(index)

        # if completed entire level in the tree add the next level
        print("- Checking completion of the current level")
        if(self.fullLevel()):

            print("- Adding another level...")
            self.addNextLevel()
            self.chainLevel += 1

        # need to rewrite the file
        print("- Rewriting Chain File...")
        chainFile = open(self.chainFilePath, 'w')
        chainFile.write(chain[0].toNiceString())
        chainFile.close()

        chainFile = open(self.chainFilePath, 'a')

        for i in range(1, len(chain)):

            if(self.isEmptyBlock(i)):
                chainFile.write('\n')

            else:
                blockString = chain[i].toNiceString()
                chainFile.write(blockString)

        chainFile.close()

        # reset the unconfirmed transactions in mem and file
        print("- Resetting the unconf transactions and its file...")
        self.unconfTransactions = []
        
        unconfFile = open(self.unconfTransactPath, 'w')
        unconfFile.write("")
        unconfFile.close()

        print("- New Block Added and Chain File Revised.")

        return 0
        

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

    def getLeastMinedBlock(self):

        # Get the least mined block
        leastMiners = self.minableBlocks[0].getMiners()
        minBlock = self.minableBlocks[0]

        for block in self.minableBlocks:

            if(block.getMiners() < leastMiners):
                minBlock = block

        return minBlock
        

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

            elif(lineIndicator == "proofs per block"):
                self.proofsPerBlock = int(lineValue)

            elif(lineIndicator == "chain level"):
                self.chainLevel = int(lineValue)

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
        blockCounter = 0

        while(currentLine):

            # take out the new line character
            currentLine = currentLine.replace('\n', '')

            print("- Current Line: " + currentLine)

            # If empty, no block yet
            if(currentLine == ""):

                # add the block if there was a block read
                if(len(currentBlockLines) != 0):
                    self.addBlockFromLines(currentBlockLines)

                # Adding empty block with the given index
                self.addEmptyBlock()
                currentBlockLines = []

                # increment the block counter
                print("-- No Block, Added Empty")

            # If "index" new block"
            elif(currentLine[5:] == "index"):

                # add the block if there was a block read
                if(len(currentBlockLines) != 0):
                    self.addBlockFromLines(currentBlockLines)

                # start reading in the new block
                currentBlockLines = [currentLine]

                # increment blockCounter
                #blockCounter += 1

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
        self.chain.append(self.getEmptyBlock(len(self.chain)))

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

    # Minable Block Helper Functions
    def getMinableBlocks(self):

        # Run through the list getting the empty blocks
        for i in range(len(self.chain)):

            if(self.isEmptyBlock(i)):
                self.minableBlocks.append(self.chain[i])

    def removeMinableBlock(self, blockIndex):

        # move everything into temp and copy over
        temp = []

        for i in range(len(self.minableBlocks)):

            if(not(self.minableBlocks[i].getIndex() == blockIndex)):
                temp += [self.minableBlocks[i]]

        self.minableBlocks = temp
                

    # Mem Block manipulation helper functions
    def hashBlock(block):

        # encode in unicode string and return
        blockString = block.toString()
        unicodeBlockString = blockString.encode()

        return hashlib.sha256(uniBlockString).hexdigest()

    def removeMin

    def fullLevel(self):

        # check if any of the blocks are currently emtpy
        for i in range(len(self.chain)):

            if(self.isEmptyBlock(i)):
                return False

        return True

    def addNextLevel(self):

        # Adding the next full level to the chain tree
        self.minableBlocks = []
        totalAmount = (self.proofsPerBlock ** (self.chainLevel)) + len(self.chain)

        while(len(self.chain) < totalAmount):
            self.addEmptyBlock()
            self.minableBlocks.append(self.chain[-1])

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
        #if(index >= len(self.chain)):
            #return True

        #else:
        block = self.chain[index]
        return (block.getTimeStamp() == -1 and block.getProofType() == -1)

    def getEmptyBlock(self, index):
        
        return Block(index, -1, -1, [], -1, -1)

    def hashString(self, string):

        unicodeString = string.encode()
        return hashlib.sha256(unicodeString).hexdigest()

    def hashConfigParameters(self):

        rootHash = self.hashString(self.owner + str(self.coinCap))
        return rootHash

        

