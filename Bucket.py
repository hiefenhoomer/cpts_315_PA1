class Bucket:
    def __init__(self, bucket_index):
        self.allowed_pairs = []
        self.pairs = {}
        self.count = 0
        self.bucket_index = bucket_index

    def set_pairs_allowed(self, pair):
        self.allowed_pairs.append(pair)

    def get_pairs_allowed(self):
        return self.allowed_pairs

    def add_pair(self, item):
        self.count += 1
        if item not in self.pairs:
            self.pairs[item] = 1
        else:
            self.pairs[item] += 1

    def get_pairs(self):
        pairs_list = []
        for pair in self.pairs:
            frequency = self.pairs[pair]
            pairs_list.append((pair, frequency))
        return pairs_list

    def get_count(self):
        return self.count

