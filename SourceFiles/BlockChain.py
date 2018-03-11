# Nick Caspers
# 2018-3-11
#################################

# File: BlockChain.py 
# Purpose: The class in charge of interacting, maintaining, and reading the block chain files.

import hashlib


class BlockChain:

	## Data members
	# Names
	chainName = ""
	chainDirPath = ""
	chainFilePath = ""
	chainTransactionsPath = ""
	chainConfigPath = ""

	# Current Chain
	memChain = True
	chain = []
	currentTransactions = []

	#################################################
	# Constructor
	def __init__(self, chainName, memChain=True):

		## setup data members
		# setup the files
		self.chainName = chainName
		setupChainFiles()

		# bring chain in memory
		self.memChain = memChain

		if(memChain):
			setupMemChain()
		

	# Constructor Helper Functions
	def setupChainFiles(self):

		# setup dir path
		self.chainDirPath = "../Chains/" + self.chainName

		# setup the other file paths
		self.chainFilePath = self.chaiDirPath + "/" + self.chainName + ".chain"
		self.chainCurrentTransactions = self.chainDirPath + "/" + self.chainName + "_transactions.chain"
		self.chainConfigPath = self.chainDirPath + "/" + self.chainName + ".config"

	##################################################
	# Class Methods
	

	##################################################
	# Helper Functions
	def setupMemChain(self):
		
		# Read-in Blocks from files
		chainFile = open(self.chainFilePath, 'r')
		
		currentLine = chainFile.readline()
		currentBlockLines = []

		while(currentLine):

			# If "index" new block"
			if(currentLine[5:] == "index"):

				# add the block if there was a block read
				if(len(currenBlockLines) != 0):
					addBlockFromLines(currentBlockLines)

				# start reading in the new block
				currentBlockLines = [currentLine]

			# Increment
			currentLine = chainFile.readline()

	def addBlockFromLines(self, blockLines):

		## Parse lines
		index = int( (blockLines[0].split(':'))[-1] )
		timeStamp = float( (blockLines[1].split(':'))[-1] )

		# run through transactions
		transactions =[]

		for i in range(2, len(blockLines) - 2, 3):

			# create Transaction and append
			sender = ((blockLines[i]).split(':'))[-1]
			reciever = ((blockLines[i + 1]).split(':'))[-1]
			amount = float( ((blockLines[i + 2]).split(':'))[-1] )

			transaction = Transaction(sender, reciever, amount)
			transactions.append(transaction)

		proof = blockLines[-2].split(':')
		previousHash = blockLines[-1].split(':')

		# add block to the list
		block = Block(index, timeStamp, transactions, proof, previousHash)
		self.chain[block]



