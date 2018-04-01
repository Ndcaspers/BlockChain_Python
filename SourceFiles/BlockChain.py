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
from UserInfo import *

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
    ownerAddr = ""
    blockCap = -1
    coinHashKey = ''
    proofsPerBlock = -1
    chainLevel = 0
    derivationDepth = -1

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

        print("===============================================")
        print("Block Chain File Setup Completed.")
        print("===============================================")

        # Obtain Configuration parameters
        self.setupMemConfig()

        print("Obtained <" + self.chainName + "> Config Parameters")

        # Check chain file
        chainFile = open(self.chainFilePath, 'r')
        noLines = not(chainFile.readline())
        chainFile.close()

        if(noLines):
            
            self.rootBlock = Block(0, 0, time.time(), self.owner, self.ownerAddr, [], 0, self.hashConfigParameters())
            self.writeRootBlock()

        print("===============================================")
        print("Checked Chain File.")
        print("===============================================")

        # Chain to Memory
        self.memChain = memChain

        if(memChain):
            self.setupMemChain()

        print("===============================================")

        self.fillChainWithEmpty()

        print("Chain Level: " + str(self.chainLevel))
        print("Chain Block Amount: " + str(len(self.chain)))
        print("Chain is in Memory.")

        print("=========================================")

        # change the difficulty depending on the depth
        for i in range(1, self.chainLevel):
            self.coinHashKey += '0'

        # Obtain the info of blocks available for mining
        print("Getting Minable Blocks...")
        self.getMinableBlocks()

        print("=========================================")

        # setup the unconfirmed transactions in memory
        print("Setting up Mem Unconf Transactions...")
        self.setupMemUnconfTransact()
       
        print("=========================================")

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

    def fillChainWithEmpty(self):

        # fill rest of tree with remaining blocks
        iteration = 0
        idealTreeSize = 0

        while(idealTreeSize < len(self.chain)):
            idealTreeSize += (self.proofsPerBlock ** iteration)
            iteration += 1
            self.chainLevel += 1

        if(self.fullLevel()):
        
            print("- Adding another level...")
            self.addNextLevel()
            self.chainLevel += 1

        print("- Chain Level: " + str(self.chainLevel))

        while(len(self.chain) < idealTreeSize):
            self.addEmptyBlock()


    ##################################################
    # Class Methods
    def validProof(self, blockIndex, proofType, proof):

        #print("- Checking Proof <" + str(proof) + ">")
        #print("\tagainst block " + str(blockIndex) + " with proofType <" + str(proofType) + ">")

        # Get block hash of the proofType
        block = self.chain[blockIndex]
        blockHash = self.hashStringtoString(block.toStringProofType(proofType))

        endHash = self.hashStringtoString(blockHash + proof)

        #print("- endHash: " + endHash)
        #print("- endHash[:4]: " + endHash[:4])
        #print("- Accepted?: " + str(endHash[:4] == self.coinHashKey))

        if(endHash[:len(self.coinHashKey)] == self.coinHashKey):
            print("- Checking Proof <" + str(proof) + ">")
            print("\tagainst block " + str(blockIndex) + " with proofType <" + str(proofType) + ">")
            print("- endHash: " + endHash + " (length: " + str(len(endHash)) + ")")
            print("- Accepted?: " + str(endHash[:len(self.coinHashKey)] == self.coinHashKey))

        #self.coinHashKey
        return (endHash[:len(self.coinHashKey)] == self.coinHashKey)


    def newBlock(self, minerInfo, proof, proofType, prevBlockIndex):

        # Determine the miner Address
        minerName = minerInfo.displayName
        minerAddr = self.obtainUserAddr(minerInfo)

        if(not(self.verifyUserMatchAddr(minerName, minerAddr))):
            return 2

        #minerName = minerInfo.displayName
        #minerAddr = self.obtainUserAddr(minerInfo)

        # Initialize
        print("- Creating New Block...")
        prevBlock = self.chain[prevBlockIndex]
        index = (prevBlockIndex * self.proofsPerBlock) + proofType
        
        validBlock = (self.validProof(prevBlockIndex, proofType, proof) and self.isEmptyBlock(index))

        if(not(validBlock)):
            return 1
        
        # Create the new block
        prevHash = self.hashBlock(prevBlock)
        newBlock = Block(index, proofType, time.time(), minerName, minerAddr, self.unconfTransactions, proof, prevHash)

        # add it to the chain, remove it from minable
        self.chain[index] = newBlock
        self.removeMinableBlock(index)

        # if completed entire level in the tree add the next level
        print("- Checking completion of the current level")
        if(self.fullLevel()):

            print("- Adding another level...")
            self.addNextLevel()
            self.chainLevel += 1
            self.coinHashKey += '0'

        # need to rewrite the file
        print("- Rewriting Chain File...")
        chainFile = open(self.chainFilePath, 'w')
        chainFile.write(self.chain[0].toNiceString())
        chainFile.close()

        chainFile = open(self.chainFilePath, 'a')

        for i in range(1, len(self.chain)):

            if(self.isEmptyBlock(i)):
                chainFile.write('\n')

            else:
                blockString = self.chain[i].toNiceString()
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
        

    def newTransaction(self, senderInfo, reciever, recieverAddr, amount):

        # verify the sender is legit
        print("- Get sender addr.")
        senderAddr = self.obtainUserAddr(senderInfo)

        print("- checking sender name and addr")
        if(not(self.verifyUserMatchAddr(senderInfo.displayName, senderAddr))):
            return False

        # create a new transaction
        print("- Creating a new transaction.")
        transaction = Transaction(senderInfo.displayName, senderAddr, reciever, recieverAddr, amount)

        # need to check if the transaction is possibel
        if(self.validTransaction(transaction)):
            print("- Transaction Accepted.")
            self.addUnconfTransaction(transaction)
            self.unconfTransactions.append(transaction)
            return True

        else:
            print("- Transaction Rejected on valid Transaction.")
            return False

    def getCoinHashKey(self):

        return self.coinHashKey

    def getMinableBlockTarget(self, index):

        # use the given index on the minable blocks
        if(index >= len(self.minableBlocks)):
            return [-1, -1]

        return self.minableBlocks[index]

    def getMinerBalance(self, miner, minerAddr):
    
        # Run through the blocks and get balance
        minerBalance = 0.0

        # check if owner
        ownerFlag = (miner == self.owner) and (minerAddr == self.ownerAddr)

        print("- miner is owner of the chain? " + str(ownerFlag))
        print("- miner Addr: " + minerAddr)
        print("- owner Addr: " + self.ownerAddr)

        # run through each block
        for block in self.chain:

            if(ownerFlag and not(self.isEmptyBlock(block.getIndex()))):
                minerBalance += 0.01

            if(block.getMinerName() == miner and block.getMinerAddr() == minerAddr):
                minerBalance += 10.0

            #print("- Sender Current Balance: " + str(senderBalance))

            for currentTransact in block.getTransactions():

                if(currentTransact.sender == miner and currentTransact.senderAddr == minerAddr):
                    minerBalance -= currentTransact.amount

                elif(currentTransact.reciever == miner and currentTransact.recieverAddr == minerAddr):
                    minerBalance += currentTransact.amount

        # run through the unconfirmed transactions
        for unconfTransact in self.unconfTransactions:

            #print("- Sender Current Balance: " + str(senderBalance))

            # check if sending amount vs balance
            if(unconfTransact.sender == miner and unconfTransact.senderAddr == minerAddr):
                minerBalance -= unconfTransact.amount

            elif(unconfTransact.reciever == miner and unconfTransact.recieverAddr == minerAddr):
                minerBalance += unconfTransact.amount

            #print("- Sender Current Balance: " + str(senderBalance))

        # check amount vs sender balance
        print("- Miner Balance: " + str(minerBalance))
        return (minerBalance) 

    def verifyUserMatchAddr(self, displayName, addr):

        # run through the blocks and transactions looking for the same name
        for block in self.chain:

            if(block.getMinerName() == displayName and block.getMinerAddr() != addr):
                return False

            for currentTransact in block.getTransactions():

                if(currentTransact.sender == displayName and currentTransact.senderAddr != addr):  
                    return False

                elif(currentTransact.reciever == displayName and currentTransact.recieverAddr != addr):
                    return False

        # run through the unconfirmed transactions
        for unconfTransact in self.unconfTransactions:

            # check if sending amount vs balance
            if(unconfTransact.sender == displayName and unconfTransact.senderAddr != addr):
                return False

            elif(unconfTransact.reciever == displayName and unconfTransact.recieverAddr != addr):
                return False

        return True

    def findUserAddr(self, displayName):

        # Run through the blocks lookng for an addr to a user
        for block in self.chain:

            if(block.getMinerName() == displayName):
                return block.getMinerAddr()

            for currentTransact in block.getTransactions():

                if(currentTransact.sender == displayName):  
                    return currentTransact.senderAddr

                elif(currentTransact.reciever == displayName):
                    return currentTransact.recieverAddr

        # run through the unconfirmed transactions
        for unconfTransact in self.unconfTransactions:

            # check if sending amount vs balance
            if(unconfTransact.sender == displayName):
                return currentTransact.senderAddr

            elif(unconfTransact.reciever == displayName):
                return unconfTransact.recieverAddr

        # couldnt find the user address
        return -1

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

            #print("- Current Config Line: " + currentLine)

            # parse through the various apsects
            lineSplit = currentLine.split(":")
            lineIndicator = lineSplit[0]
            lineValue = lineSplit[1]

            if(lineIndicator == "owner"):
                self.owner = lineValue

            elif(lineIndicator == "owner address"):
                self.ownerAddr = lineValue

            elif(lineIndicator == "block cap"):
                self.blockCap = int(lineValue)

            #elif(lineIndicator == "coin hash key"):
            #    self.coinHashKey = lineValue

            elif(lineIndicator == "proofs per block"):
                self.proofsPerBlock = int(lineValue)

            #elif(lineIndicator == "chain level"):
            #    self.chainLevel = int(lineValue)

            elif(lineIndicator == "chain derivation depth"):
                self.derivationDepth = int(lineValue)

            # increment
            currentLine = configFile.readline()

        print("- Owner found: " + self.owner)
        print("- Owner Address: " + self.ownerAddr)
        print("- Block Cap found: " + str(self.blockCap))
        #print("- Coin Hash Key found: " + self.coinHashKey)
        print("- Proofs Per Block: " + str(self.proofsPerBlock))
        #print("- Chain Level: " + str(self.chainLevel))
        print("- Derivation Depth: " + str(self.derivationDepth))

        # close file
        configFile.close()

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

            #print("- Current Line: " + currentLine)

            # If empty, no block yet
            if(currentLine == ""):

                # add the block if there was a block read
                if(len(currentBlockLines) != 0):
                    self.addBlockFromLines(currentBlockLines)

                # Adding empty block with the given index
                self.addEmptyBlock()
                currentBlockLines = []

                # increment the block counter
                #print("-- No Block, Added Empty")

            # If "index" new block"
            elif(currentLine[:5] == "index"):

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
        minerName = blockLines[3].split(':')[-1]
        minerAddr = blockLines[4].split(':')[-1]

        # run through transactions
        transactions = []

        for i in range(5, len(blockLines) - 2, 5):

            # create Transaction and append
            sender = ((blockLines[i]).split(':'))[-1]
            senderAddr = ((blockLines[i + 1]).split(':'))[-1]
            reciever = ((blockLines[i + 2]).split(':'))[-1]
            recieverAddr = ((blockLines[i + 3]).split(':'))[-1]
            amount = float( ((blockLines[i + 4]).split(':'))[-1] )

            transaction = Transaction(sender, senderAddr, reciever, recieverAddr, amount)
            transactions.append(transaction)

        proof = blockLines[-2].split(':')[-1]
        previousHash = blockLines[-1].split(':')[-1]

        # add empty blocks to fill chain uptill index
        while(len(self.chain) <= index):
            self.addEmptyBlock()

        # add block to the list
        block = Block(index, blockType, timeStamp, minerName, minerAddr, transactions, proof, previousHash)
        self.chain[index] = block

        #print("-- Added Block to Mem:\n")
        #print(block.toNiceString())

    # Setup Unconf Transactions in memory function and helpers
    def setupMemUnconfTransact(self):

        # open the needed file
        unconfFile = open(self.unconfTransactPath, 'r')

        # initialize the line and the transact linesj
        currentLine = unconfFile.readline()
        transactLines = []
        transactNumber = 0

        while(currentLine):

            currentLine = currentLine.replace('\n', '')
            #print("- Current Line: " + currentLine)

            # split the current line
            lineIndicator = currentLine.split(':')[0]
            lineValue = currentLine.split(':')[-1]

            # add it to the transact lines
            transactLines += [lineValue]

            if(lineIndicator == "amount"):
        
                # Create transaction from the lines
                self.addTransactFromLines(transactLines)
    
                # increment and clear
                transactLines = []
                transactNumber += 1

            # increment to the nextline
            currentLine = unconfFile.readline()

        # Add the last transact if it exists
        #if(transactNumber >= 1):
            #self.addTransactFromLines(transactLines)

        print("- Total Unconfirmed Transactions: " + str(len(self.unconfTransactions)))

        # close the unconfirmed transaction file
        unconfFile.close()

    def addTransactFromLines(self, transactLines):

        # Create Transaction form the lines and append to unconfTransact
        sender =  transactLines[0]
        senderAddr = transactLines[1]
        reciever = transactLines[2]
        recieverAddr = transactLines[3]
        amount = float(transactLines[4])

        transaction = Transaction(sender, senderAddr, reciever, recieverAddr, amount)
        self.unconfTransactions.append(transaction)

    # Minable Block Helper Functions
    def getMinableBlocks(self):

        # Run through the list getting the empty blocks
        print("Chain Length: " + str(len(self.chain)))
    
        for i in range(len(self.chain)):

            #print("Current Parent: " + str(i))

            if(((i * self.proofsPerBlock) + 1) >= len(self.chain)):
                break

            #print("Current Parent: " + str(i))

            for j in range(1, self.proofsPerBlock + 1):

                blockIndex = (i * self.proofsPerBlock) + j

                #print("Current Child: " + str(j) + ", " + str(blockIndex))

                if(self.isEmptyBlock(blockIndex)):
                    self.minableBlocks.append([i, j, self.chain[i].getProof(j)])

    def removeMinableBlock(self, blockIndex):

        # move everything into temp and copy over
        temp = []

        for i in range(len(self.minableBlocks)):

            if(not((self.minableBlocks[i])[0] == blockIndex)):
                temp += [self.minableBlocks[i]]

        self.minableBlocks = temp
                

    # Mem Block manipulation helper functions
    def hashBlock(self, block):

        # encode in unicode string and return
        blockString = block.toString()
        uniBlockString = blockString.encode()

        return hashlib.sha256(uniBlockString).hexdigest()

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

        currentType = 1

        while(len(self.chain) < totalAmount):

            parentIndex = (len(self.chain) - currentType) / self.proofsPerBlock
            currentProof =  self.chain[parentIndex].getProof(currentType)
            

            self.addEmptyBlock()
            self.minableBlocks.append([parentIndex, currentType, currentProof])

            # increment current Type
            currentType += 1

            if(currentType > self.proofsPerBlock):
                currentType = 1


    # Transaction helper functions
    def obtainUserAddr(self, userInfo):

        # Hash together the sender Info
        firstHash = self.hashStringtoString(userInfo.displayName + userInfo.userName + userInfo.password)

        displayLength = str(len(userInfo.displayName))
        userLength = str(len(userInfo.userName))
        passwordLength = str(len(userInfo.password))
        
        addr = self.hashStringtoString(firstHash + displayLength + userLength + passwordLength)

        return addr
 
    def validTransaction(self, transaction):

        # get sender balance
        print("- Checking valididty of transaction...")
        sender = transaction.sender
        senderAddr = transaction.senderAddr
        sendingAmount = transaction.amount

        senderBalance = 0.0

        # check if owner
        ownerFlag = (sender == self.owner) and (senderAddr == self.ownerAddr)

        print("- sender is owner of the chain? " + str(ownerFlag))
        print("- sender Addr: " + senderAddr)
        print("- owner Addr: " + self.ownerAddr)

        if(not(ownerFlag) and sender == self.owner):
            return False

        # run through each block
        for block in self.chain:

            if(ownerFlag and not(self.isEmptyBlock(block.getIndex()))):
                senderBalance += 0.01

            if(block.getMinerName() == sender):

                if(not(block.getMinerAddr() == senderAddr)):
                    print("- [Error] addresses dont match")
                    return False

                senderBalance += 10.0

            #print("- Sender Current Balance: " + str(senderBalance))

            for currentTransact in block.getTransactions():

                if(currentTransact.sender == sender):

                    if(currentTransact.senderAddr != senderAddr):
                        print("- [Error] addresses dont match")
                        return False

                    senderBalance -= currentTransact.amount

                elif(currentTransact.reciever == sender):

                    if(currentTransact.recieverAddr != senderAddr):
                        print("- [Error] addresses dont match")
                        return False

                    senderBalance += currentTransact.amount


        # run through the unconfirmed transactions
        for unconfTransact in self.unconfTransactions:

            #print("- Sender Current Balance: " + str(senderBalance))

            # check if sending amount vs balance
            if(unconfTransact.sender == sender):

                if(unconfTransact.senderAddr != senderAddr):
                    print("- [Error] addresses dont match")
                    return False

                senderBalance -= unconfTransact.amount

            elif(unconfTransact.reciever == sender):
        
                if(unconfTransact.recieverAddr != senderAddr):
                    print("- [Error] addresses dont match")
                    return False

                senderBalance += unconfTransact.amount

            #print("- Sender Current Balance: " + str(senderBalance))

        # check amount vs sender balance
        print("- Does balance check out: " + str(sendingAmount) + " <= " + str(senderBalance))
        return (sendingAmount <= senderBalance) 

    def addUnconfTransaction(self, transaction):

        # add to memory list
        self.unconfTransactions.append(transaction)

        # add to file
        sender = "sender:" + str(transaction.sender) + "\n"
        senderAddr = "senderAddr:" + str(transaction.senderAddr) + "\n"
        reciever = "reciever:" + str(transaction.reciever) + "\n"
        recieverAddr = "recieverAddr:" + str(transaction.recieverAddr) + "\n"
        amount = "amount:" + str(transaction.amount) + "\n"

        unconfTransactionFile = open(self.unconfTransactPath, 'a')

        unconfTransactionFile.write(sender)
        unconfTransactionFile.write(senderAddr)
        unconfTransactionFile.write(reciever)
        unconfTransactionFile.write(recieverAddr)
        unconfTransactionFile.write(amount)

        unconfTransactionFile.close()


    # Generic Helper Functions
    def packUserInfo(self, displayName, userName, password):

        userInfo = UserInfo(displayName, userName, password)
        return userInfo

    def isEmptyBlock(self, index):

        # Block could be outside chain, which is "empty"
        #if(index >= len(self.chain)):
            #return True

        #else:
        block = self.chain[index]

        return (block.getTimeStamp() == -1 and block.getProofType() == -1)

    def getEmptyBlock(self, index):
        return Block(index, -1, -1, "", "", [], -1, -1)

    def getChainName(self):
        return self.chainName

    def getDerivationLevel(self):
        return self.derivationDepth

    def hashStringtoHex(self, string):

        unicodeString = string.encode()
        return hashlib.sha256(unicodeString)

    def hashStringtoString(self, string):

        unicodeString = string.encode()
        return hashlib.sha256(unicodeString).hexdigest()

    def hashConfigParameters(self):

        rootHash = self.hashStringtoString(self.owner + self.ownerAddr + str(self.blockCap))
        return rootHash

        

