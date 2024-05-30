from itertools import combinations
from Buckets import Buckets
from tabulate import tabulate

max_tuple_size = 2
min_support = 1
file_name = 'text/hw1.txt'
buckets_size = 11


# Convert lines to baskets.
def line_to_basket(line):
    # Split by whitespace and strip '\n' characters.
    return sorted(line.strip().split(' '))


# Generate all tuples of tuple_size in a list. itertools.combinations is magic.
def create_tuples_from_list(basket, tuple_size):
    return list(combinations(basket, tuple_size))


# Only accept tuples with min_support in dictionary.
def prune_tuples(tuples_dict, min_support):
    delete_tuples_keys = []
    # Iterate over keys in the dictionary.
    for key in tuples_dict.keys():
        # If the key has an absolute support below 100, add to the delete key list.
        if tuples_dict[key] < min_support:
            delete_tuples_keys.append(key)

    # Delete all tuple keys in delete_tuples_key.
    for key in delete_tuples_keys:
        del tuples_dict[key]

    return tuples_dict


# Need a baseline to start from in this a-priori algorithm.
def create_tuples_1(file):
    singles = {}
    with open(file, 'r') as f:
        for line in f:
            # Each line is a basket. Convert it.
            basket = line_to_basket(line)
            # For each tuple in a basket, add to dictionary or increment frequency by 1 - tuples will have a size
            # of 1 for single items.
            for tup in create_tuples_from_list(basket, 1):
                if tup not in singles:
                    singles[tup] = 1
                else:
                    singles[tup] += 1
    return singles


# Create tuples by using our single items and our most recently generated series of items.
# The tuple size for create_tuples_n is tuples_size = 1 + len(item from: tuples_prev)
def create_tuples_n(tuples_1, tuples_previous, tuple_size):
    tuples_n = []
    # For each tuple in our 1 tuples...
    for tup_1 in tuples_1:
        # For each tuple in our tuples_previous or n tuples...
        for tup_2 in tuples_previous:
            # Merge both tuples together.
            merged = tuple(sorted(set(tup_1 + tup_2)))
            if len(merged) == tuple_size:
                tuples_n.append(merged)
    return tuples_n


# In finding the frequency of tuples, we need our file to scan, our generated list of tuples, and the size of our
# tuples. These comments have abstracted away what tuple means in the context of this programming assignment.
# Tuples here are the combinations of items frequently seen together.
def frequency_tuples_n(file, tuples_list, tuple_size):
    # Instantiate dictionary to return. Tuples with frequency.
    tuples_dict = {}

    # Instantiate all item combinations browsed together in the dictionary.
    for tup in tuples_list:
        tuples_dict[tup] = 0

    with open(file, 'r') as f:
        # Read the file and convert each line to a computer comprehensible basket.
        for line in f:
            basket = line_to_basket(line)
            comb = combinations(basket, tuple_size)
            # For each combination seen in the basket, increment the dictionary item by 1.
            for tup in comb:
                if tup in tuples_dict:
                    tuples_dict[tup] += 1

    return tuples_dict


# Driver code to generate all frequently browsed items.
def get_frequent_tuples(file, tuple_size, min_support):
    tuple_dict_list = []

    # Generate pruned single items frequently seen.
    single_tuples = create_tuples_1(file)
    single_tuples = prune_tuples(single_tuples, min_support)
    # Append this dictionary to the list of dictionaries. Each index indicates the number of items commonly seen
    # together.
    tuple_dict_list.append(single_tuples)

    # i here represents the size of tuples currently being added. Earlier, we added tuples of size 1.
    # We want to add tuples of size 2 now up to max tuple size.
    for i in range(2, tuple_size + 1):
        # Generate tuple combinations. i - 2 corresponds to the list index we are currently at. We've added 1
        # previously to represent tuple size. We now want to subtract 2 to undo the +1 operation and retrieve
        # the index before index i.
        current_tuple = create_tuples_n(single_tuples, list(tuple_dict_list[i - 2].keys()), i)
        # Get the support of the items frequently viewed together.
        current_dict = frequency_tuples_n(file, current_tuple, i)
        # Prune the tuples below the minimum support level.
        current_dict = prune_tuples(current_dict, min_support)
        # Append this dictionary to the list.
        tuple_dict_list.append(current_dict)

    return tuple_dict_list


def create_buckets(tuples, bucket_size):
    tuple_dict_0 = tuples[0]
    tuple_list = pairs_from_tuples(tuple_dict_0)
    buckets = Buckets(bucket_size, tuple_list)
    return buckets


def put_pairs_in_buckets(file, buckets):
    with open(file, 'r') as f:
        for line in f:
            basket = line_to_basket(line)
            tuples = create_tuples_from_list(basket, 2)
            tuples = tuple_strs_to_ints(tuples)
            for tup in tuples:
                buckets.insert_pair(tup)
        return buckets


def format_buckets_display(buckets):
    indices, corresponding_pairs, items, frequencies = buckets.get_buckets()
    items = format_pairs_for_table(items)
    head = ['Bucket', 'Corresponding Pairs', 'Pairs In Bucket', 'Total In Bucket']
    table_data = []
    for idx in indices:
        row = [idx, corresponding_pairs[idx], items[idx], frequencies[idx]]
        table_data.append(row)
    return tabulate(table_data, headers=head, tablefmt='grid')


def format_frequent_buckets(buckets, support):
    indices, corresponding_pairs, items, frequencies = buckets.get_buckets()
    items = format_pairs_for_table(items)
    head = ['Bucket', 'Corresponding Pairs', 'Pairs In Bucket', 'Total In Bucket']
    table_data = []
    for idx in indices:
        if frequencies[idx] < support:
            continue
        row = [idx, corresponding_pairs[idx], items[idx], frequencies[idx]]
        table_data.append(row)
    return tabulate(table_data, headers=head, tablefmt='grid')


def format_pairs_for_table(pair_list):
    formatted_list = []
    for pairs in pair_list:
        if len(pairs) == 0:
            formatted_list.append('N/A')
            continue

        pair_string = ''
        for pair in pairs:
            pair, frequency = pair[0], pair[1]
            pair_string += str(pair) + ': ' + str(frequency) + ', '
        formatted_list.append(pair_string)
    return formatted_list

def tuple_strs_to_ints(tuples):
    tuples_list = list(tuples)
    int_tuples = []
    for tup in tuples_list:
        tup_list = list(tup)
        int_tup_list = []
        for value in tup_list:
            int_tup_list.append(int(value))
        int_tuples.append(tuple(int_tup_list))

    return int_tuples


def pairs_from_tuples(tuple_dict):
    pairs = create_tuples_from_list(tuple_dict.keys(), 2)
    formatted_list = []
    for tup in pairs:
        a, b = tup[0], tup[1]
        combined_tuple = a + b
        val_1, val_2 = combined_tuple
        val_1 = int(val_1)
        val_2 = int(val_2)
        integer_vals = (val_1, val_2)
        formatted_list.append(integer_vals)

    return formatted_list


# Driver code to run the program.
if __name__ == '__main__':
    tuple_dict_list = get_frequent_tuples(file_name, max_tuple_size, min_support)
    buckets = create_buckets(tuple_dict_list, buckets_size)
    buckets = put_pairs_in_buckets(file_name, buckets)
    buckets_table = format_buckets_display(buckets)
    frequent_buckets_table = format_frequent_buckets(buckets, 4)
    print(buckets_table)
    print(frequent_buckets_table)
