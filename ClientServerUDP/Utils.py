import hashlib


# This class implements three static methods, every method is used in order to get the checksum
# in our Header file.
class Util:
    # Get the HEXDIGEST of input metadata
    @staticmethod
    def get_hash_with_metadata(metadata):
        md5_hash = hashlib.md5()
        md5_hash.update(metadata)
        return md5_hash.hexdigest()

    # Update md5 content with the input metadata
    @staticmethod
    def update_md5(md5:hashlib.md5(), metadata):
        md5.update(metadata)
        return md5

    # Get the HEXDIGEST of the input md5
    @staticmethod
    def get_digest(md5):
        return md5.hexdigest()
