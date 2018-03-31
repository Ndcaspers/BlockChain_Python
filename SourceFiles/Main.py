# Nick Caspers
# 2018-3-19
#################################

# File: Main.py
# Purpose: The File reponsible for starting the system for testing and the like

import hashlib

from BlockChain import BlockChain
from Block import Block

# generic mining thing
def mine(chain, miner, minerAddr):

    print("Mining...")

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

    while(not(chain.validProof(targetIndex, targetProofType, attemptStr))):

        # no good
        attempt += 1
        attemptStr = str(attempt)

        iteration += 1

        if(iteration == 100000):
            print("< " + str(sets) + ", " + str(iteration) + "> iterations done... stopping")
            sets += 1
            iteration = 0
    
    print("SUCCCCCCC!!: \n Proper proof: " + attemptStr)

    chain.newBlock(miner, minerAddr, attemptStr, targetProofType, targetIndex)

# Main for testing
def main():

    # Startup the 
    chainName = "Spurs"
    print("Starting up Chain <" + chainName + ">...")
    blockChain = BlockChain("spurs")

    print("Block Chain Setup Completed.")

    # practice mining
    print("================================================")

    miner = "Spurs"
    minerAddr = "7879b222fa18213809713d2e947bceb4cc77c19291ab6e95b44d0b81d9de052c"

    mine(blockChain, miner, minerAddr)


# Starting the main function
if(__name__ == "__main__"):

    main()
