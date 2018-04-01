# Nick Caspers
# 2018-3-19
#################################

# File: Main.py
# Purpose: The File reponsible for starting the system for testing and the like

import hashlib

from BlockChainManager import BlockChainManager
from BlockChain import BlockChain
from Block import Block
from UserInfo import *

# generic mining thing
def mine(chain, minerInfo):

    print("Mining...")
    minerAddr = chain.obtainUserAddr(minerInfo)

    # get the least mined block and key for validation
    coinHashKey = chain.getCoinHashKey()
    target = chain.getMinableBlockTarget(0)

    print("[MINER] coin hash key: " + coinHashKey)

    targetIndex = target[0]
    targetProofType = target[1]
    targetProof = target[2]

    print("[MINER] target index: " + str(targetIndex))
    print("[MINER] target proof type: " + str(targetProofType))
    print("[MINER] target proof: " + str(targetProof))

    # start mining
    attempt = 0
    attemptStr = str(attempt)

    iteration = 0
    sets = 0

    while(not(chain.validProof(targetIndex, targetProofType, attemptStr)) or chain.getMinerBalance(minerInfo.displayName, minerAddr) < 100.0):

        # no good
        attempt += 1
        attemptStr = str(attempt)

        iteration += 1

        if(iteration == 100000):
            print("< " + str(sets) + ", " + str(iteration) + "> iterations done.")
            print("Current Balance: " + str(chain.getMinerBalance(minerInfo.displayName, minerAddr)))
            sets += 1
            iteration = 0
    
    print("Current Balance: " + str(chain.getMinerBalance(miner, minerAddr)))
    print("SUCCCCCCC!!: \n Proper proof: " + attemptStr)

    chain.newBlock(minerInfo, attemptStr, targetProofType, targetIndex)

def createTransaction(chain, displayName, userName, password, reciever, recieverAddr, amount):

    # pack into a UserInfo and do transaction
    userInfo = chain.packUserInfo(displayName, userName, password)
    
    result = chain.newTransaction(userInfo, reciever, recieverAddr, amount)

    print("====================================================")
    print(str(result))

# Main for testing
def main():

    # Startup the Block Chain Manager
    chainName = "Spurs"
    print("Starting up Chain <" + chainName + ">...")
    #blockChain = BlockChain("spurs")

    manager = BlockChainManager("../Chains")

    print("Block Chain Manager Setup Completed.")

    # practice transactions
    print("================================================")

    miner = "Spurs"
    minerUser = "polaritybot@gmail.com"
    minerPassword = "NothingButStraightCash8X0030BBC"
    minerAddr = "7879b222fa18213809713d2e947bceb4cc77c19291ab6e95b44d0b81d9de052c"

    minerInfo = UserInfo(miner, minerUser, minerPassword)

    miner2 = "Banker"
    miner2Addr = "3489456642854b3d035f697d9e73cee03f4f27a56db326f8f530d9212d7f2641"

    mine(manager.getChainByName(chainName), minerInfo)


# Starting the main function
if(__name__ == "__main__"):

    main()
