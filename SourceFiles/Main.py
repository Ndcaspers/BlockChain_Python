# Nick Caspers
# 2018-3-19
#################################

# File: Main.py
# Purpose: The File reponsible for starting the system for testing and the like

import hashlib

from BlockChain import BlockChain
from Block import Block

# generic mining thing
def mine(chain):

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

    while(not(chain.validProof(targetIndex, targetProofType, attemptStr))):

        # no good
        attempt += 1
        attemptStr = str(attempt)

        iteration += 1

        if(iteration == 100):
            print("100 iterations done... stopping")
            break
    
    print("SUCCCCCCC!!: \n Proper proof: " + attemptStr)

# Main for testing
def main():

    # Startup the 
    chainName = "Spurs"
    print("Starting up Chain <" + chainName + ">...")
    blockChain = BlockChain("spurs")

    print("Block Chain Setup Completed.")

    # practice mining
    print("================================================")
    mine(blockChain)


# Starting the main function
if(__name__ == "__main__"):

    main()
