import hashlib


class Util:
    @staticmethod
    def get_hash_with_metadata(metadata):
        md5_hash = hashlib.md5()
        md5_hash.update(metadata)
        return md5_hash.hexdigest()

    @staticmethod
    def update_md5(md5:hashlib.md5(), metadata):
        md5.update(metadata)
        return md5

    @staticmethod
    def get_digest(md5):
        return md5.hexdigest()
