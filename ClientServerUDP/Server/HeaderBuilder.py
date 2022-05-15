import base64
import json


class HeaderBuilder:
    # Argument : self
    # Argument : operation      < Which Operations is sent (see Operation.py) >
    # Argument : status         <>
    # Argument : file:name      < What is the name of the requested\sent file >
    # Argument : Size           < The size of the file_name >
    # This method create the header file and then the Server\Client send it to the destination
    @staticmethod
    def build_header(operation, status, file_name, size, metadata):
        header = {
                  "operation": operation,
                  "file_name": file_name,
                  "status": status,
                  "size": size,
                  "metadata": base64.b64encode(metadata).decode('ascii')
                  }
        return json.dumps(header)
