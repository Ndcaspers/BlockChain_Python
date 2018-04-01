# Nick Caspers
# 2018-3-30
#################################

# File: UserInfo.py
# Purpose: Class for holding user information

class UserInfo:

    # Data Members
    displayName = ""
    userName = ""
    password = ""
    addr = ""

    # Constructor
    def __init__(self, displayName, userName, password):

        # Initialize
        self.displayName = displayName
        self.userName = userName
        self.password = password

