from Bucket import Bucket


class Buckets:
    def __init__(self, total_buckets, pairs):
        self.totalBuckets = total_buckets
        self.buckets = [Bucket(i) for i in range(total_buckets)]

        for pair in pairs:
            index = self.hash_pair(pair)
            self.buckets[index].set_pairs_allowed(pair)

    def hash_pair(self, pair):
        a, b = pair
        return a * b % self.totalBuckets

    def insert_pair(self, pair):
        self.buckets[self.hash_pair(pair)].add_pair(pair)

    def get_buckets(self):
        bucket_indices = []
        allowed_pair_in_buckets = []
        items_in_buckets = []
        frequencies = []

        for i in range(len(self.buckets)):
            bucket_indices.append(i)
            allowed_pair_in_bucket = []
            items_in_bucket = []

            for allowed_pair in self.buckets[i].get_pairs_allowed():
                allowed_pair_in_bucket.append(allowed_pair)

            for item in self.buckets[i].get_pairs():
                items_in_bucket.append(item)

            frequencies.append(self.buckets[i].get_count())
            allowed_pair_in_buckets.append(allowed_pair_in_bucket)
            items_in_buckets.append(items_in_bucket)

        return bucket_indices, allowed_pair_in_buckets, items_in_buckets, frequencies

