import os


# This class is used in order to get the file's name in the Server's directory.
# If a client send a file (ex.txt) and this file is already in the Server's directory,
# the File will be named ex(1).txt
class FileNameFactory:
    @staticmethod
    def get_file_name(file, file_name, path):
        fk = file_name
        cont = 0
        for file in os.listdir(path):
            file_s = file.split('.')[0] # A.txt -> A
            suff_file = file.split('.')[1]
            suff_name = file_name.split('.')[1]
            if file_s.__contains__('(') and suff_file == suff_name:
                # Get the left part of the file's name
                file_s = file_s.split('(')[0] + '.' + file_name.split('.')[1]
                if file_s == file_name:
                    # Is the same file, update the cont
                    cont = cont + 1
                elif file_name.__contains__('('):
                    f_tmp = file_name.split('(')[0] + '.' + file_name.split('.')[1]
                    if f_tmp == file_s:
                        cont = cont+1
            elif file == file_name:
                cont = cont + 1
        if cont > 0:
            file_name = fk.split('.')[0] + '(' + str(cont) + ').' + fk.split('.')[1]
        return file_name
