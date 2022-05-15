from enum import Enum


# Enum class
# This Enum must be used in the Server and in the Client in order to
# permit a Safe and clean conversation between this two hosts.
# Every value of this Enum class represent a specific operation :
# 1) GET_FILES => The Client request to the Server all the files in the Server's directory
# 2) DOWNLOAD  => The Client request to download a specific file
# 3) UPLOAD    => The Client upload a file to the Server path
# 4) EXIT      => The Client request to close the connection
# 5) ACK       => The Server\Client Acknowledge, this operation is used for letting know that everything works good
class Operation(Enum):
    GET_FILES = 1
    DOWNLOAD = 2
    UPLOAD = 3
    EXIT = 4
    ACK = 5
    SENDING_FILE = 6
    END_FILE = 7
    ERROR = 8

