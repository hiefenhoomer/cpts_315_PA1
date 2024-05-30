class Bucket:
    def __init__(self, bucket_index):
        self.allowed_pairs = []
        self.pairs = []
        self.count = 0
        self.bucket_index = bucket_index

    def set_pairs_allowed(self, pair):
        self.allowed_pairs.append(pair)

    def get_pairs_allowed(self):
        return self.allowed_pairs

    def add_pair(self, item):
        self.count += 1
        self.pairs.append(item)

    def get_pairs(self):
        return self.pairs
