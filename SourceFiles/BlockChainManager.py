# Nick Caspers
# 2018-3-31
#################################

# File: BlockChainManager.py
# Purpose: The Block Chain Manager is responsible for handling interactions with the various chains

import os

from BlockChain import BlockChain

class BlockChainManager:

    # Data Members
    chainsDir = ""
    blockChains = []
    derivMultiplier = 10

    ################################################
    # Constructor (defualt)
    def __init__(self, chainsDir):

        print("Starting up Block Chain Manager...")

        # initialize data members
        self.chainsDir = chainsDir
        self.blockChains = []

        # determine the chains based on Chains directory
        print("Determining the various chains...")
        self.constructChains()

        print("[COMPLETED] Chain Manager Setup.")

    # Constructor Helper Methods
    def constructChains(self):

        # Get directories in chains directory
        filesInChainsDir = os.listdir(self.chainsDir)
        dirInChainsDir = []

        for chainsFile in filesInChainsDir:

            print("- File In Chains: " + chainsFile)

            if(os.path.isdir(self.chainsDir + '/' + chainsFile)):
                print("\tIs a directory")
                dirInChainsDir += [chainsFile]

        # Construct the various chains (could add a bit more checking of files here as well)
        for someDir in dirInChainsDir:

            # pull out the name
            dirName = someDir.split('/')[-1]
            print("- adding chain <" + dirName + ">...")

            # create chain and append
            self.blockChains.append(BlockChain(someDir))

        print("- Chains constructed")
        

    ################################################
    # class methods
    def constructNewChain(self, minerInfo, fundingChainName, newChainName):

        # get miner's balance at the given chain
        fundingChain = self.blockChains[self.getChainIndex(fundingChainName)]

        minerAddr = fundingChain.obtainUserAddr(minerInfo)

        fundingChainDerivLevel = fundingChain.getDerivationLevel()
        minerBalance = fundingChain.getMinerBalance(minerInfo.displayName , minerAddr)

        # is enough to obtain new currency
        cost = (self.derMultiplier ** (3 + fundingChainDerivLevel))

        if(minerBalance <= cost):
            return False

        # check if the chain name already exists
        if(self.getChainIndex(newChainName) == -1):
            return False

        # pay for it
        if(not(fundingChain.newTransaction(minerInfo, "0", "0", cost))):
            return False

        # produce chain directory
        newChainDir = self.chainDir + "/" + newChainName
        os.mkdir(newChainDir)

        # create the chain files
        chainFilePath = newChainDir + "/" + newChainName + ".chain"
        chainConfigPath = newChainDir + "/" + newChainName + ".config"
        chainUnconfPath = newChainDir + "/" + newChainName + ".transact"

        chainFile = open(chainFilePath, 'w')
        chainConfig = open(chainConfigPath, 'w')
        chainUnconf = open(chainUnconfPath, 'w')

        # write in the appropriate config
        configString = "owner:" + miner + "\n"
        configString += "owner address:" + minerAddr + "\n"
        configString += "block cap:265720\n"
        configString += "proofs per block:3\n"
        configString += "chain derivation depth:" + str(1 + fundingChainDerivLevel)

        chainConfig.write(configString)

        # close files
        chainFile.close()
        chainConfig.close()
        chainUnconf.close()

        # create chain and append to list
        newChain =  BlockChain(newChainName)
        self.blockChains.append(newChain)

        return True

    ##################################################
    # helper functions
    def getChainIndex(self, name):

        for i in range(0, len(self.blockChains)):

            if(self.blockChains[i].getChainName() == name):
                return i

        return -1

    def getChainByName(self, name):

        return self.blockChains[self.getChainIndex(name)]


