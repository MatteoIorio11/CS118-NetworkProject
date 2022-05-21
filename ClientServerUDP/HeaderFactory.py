import base64
import hashlib
from Operation import Operation
import json


# This class implements the Factory pattern. Is used in order to get a Header.
# This class has more than one method, because we can create the same Header but with different parameters.
class HeaderFactory:
    # Argument : self
    # Argument : operation      < Which Operations is sent (see Operation.py) >
    # Argument : status         <>
    # Argument : file:name      < What is the name of the requested\sent file >
    # Argument : Size           < The size of the file_name >
    # This method create the header file and then the Server\Client send it to the destination
    @staticmethod
    def build_header(operation, status, checksum,file_name, size, metadata):
        header = {
                  "operation": operation,
                  "file_name": file_name,
                  "status": status,
                  "checksum": checksum,
                  "size": size,
                  "metadata": base64.b64encode(metadata).decode('ascii')
                  }
        return json.dumps(header)

    # Factory of an ACK header
    @staticmethod
    def build_ack_header():
        md5 = hashlib.md5()
        md5.update("ACK".encode())
        header = {
            "operation": Operation.ACK.value,
            "file_name": "",
            "status": True,
            "checksum": md5.hexdigest(),
            "size": 0,
            "metadata": base64.b64encode("AKC".encode()).decode('ascii')
        }
        return json.dumps(header)

    # Argument checksum
    # Argument : metadata -> what we have to send to the Client
    # Factory of an ACK header
    @staticmethod
    def build_ack_header_wchecksum(checksum, metadata):
        header = {
            "operation": Operation.ACK.value,
            "file_name": "",
            "status": True,
            "checksum": checksum,
            "size": 0,
            "metadata": base64.b64encode(metadata).decode('ascii')
        }
        return json.dumps(header)

    # Factory of an end header, this will be used by the Client
    @staticmethod
    def build_end_header():
        md5 = hashlib.md5()
        md5.update("EXIT".encode())
        header = {
            "operation": Operation.ACK.value,
            "file_name": "",
            "status": True,
            "checksum": md5.hexdigest(),
            "size": 0,
            "metadata": base64.b64encode("EXIT".encode()).decode('ascii')
        }
        return json.dumps(header)

    # Argument : Operation -> which operation we represent
    # Argument checksum
    # Argument : metadata -> what we have to send to the Client
    # Factory of an Operation header
    @staticmethod
    def build_operation_header_wchecksum(operation, checksum, metadata):
        header = {
            "operation": operation,
            "file_name": "",
            "status": True,
            "checksum": checksum,
            "size": 0,
            "metadata": base64.b64encode(metadata).decode('ascii')
        }
        return json.dumps(header)

    # Argument : Operation -> which operation we represent
    # Argument : file -> file name
    # Argument checksum
    # Argument : metadata -> what we have to send to the Client
    # Factory of an Operation header
    @staticmethod
    def build_operation_header_wfile(operation, file, checksum, metadata):
        header = {
            "operation": operation,
            "file_name": file,
            "status": True,
            "checksum": checksum,
            "size": 0,
            "metadata": base64.b64encode(metadata).decode('ascii')
        }
        return json.dumps(header)

    # Argument : Operation -> which operation we represent
    # Argument : file -> file name
    # Argument checksum
    # Argument : size
    # Argument : metadata -> what we have to send to the Client
    # Factory of an Operation header
    @staticmethod
    def build_operation_header_wsize(operation, file, checksum, size, metadata):
        header = {
            "operation": operation,
            "file_name": file,
            "status": True,
            "checksum": checksum,
            "size": size,
            "metadata": base64.b64encode(metadata).decode('ascii')
        }
        return json.dumps(header)

    # Factory of an Error Header
    @staticmethod
    def build_error_header(checksum, metadata):
        header = {
            "operation": Operation.NAK.value,
            "file_name": "",
            "status": False,
            "checksum": checksum,
            "size": 0,
            "metadata": base64.b64encode(metadata).decode('ascii')
        }
        return json.dumps(header)



