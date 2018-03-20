# Nick Caspers
# 2018-3-19
#################################

# File: Main.py
# Purpose: The File reponsible for starting the system for testing and the like

from BlockChain import BlockChain


def main():

    # Startup the 
    chainName = "Spurs"
    print("Starting up Chain <" + chainName + ">...")
    blockChain = BlockChain("spurs")

    print("Block Chain Setup Completed.")


# Starting the main function
if(__name__ == "__main__"):

    main()
