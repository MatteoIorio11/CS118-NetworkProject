from enum import Enum


# Enum class
# This Enum must be used in the Server and in the Client in order to
# permit a Safe and clean conversation between this two hosts.
# Every value of this Enum class represent a specific operation :
# 1) GET_FILES		=> The Client request to the Server all the files in the Server's directory
# 2) DOWNLOAD		=> The Client request to download a specific file
# 3) UPLOAD		=> The Client upload a file to the Server path
# 4) ACK		=> The Server\Client Acknowledge, this operation is used for letting know that everything works good
# 5) SENDING_FILE	=> The Server\Client uses it when is sending packets that compose the file
# 6) END_FILE		=> The Client\Server tells that the file is completelly sent
# 7) NACK		=> The Server\Client NACK, this operation is used for letting know something went wrong during the upload or download
# 8) OPEN_CONNECTION	=> The Client uses this operation in order to get the main menu
class Operation(Enum):
    GET_FILES = 1
    DOWNLOAD = 2
    UPLOAD = 3
    ACK = 4
    SENDING_FILE = 5
    END_FILE = 6
    NACK = 7
    OPEN_CONNECTION = 8
