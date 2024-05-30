from itertools import combinations

max_tuple_size = 3
min_support = 100
file_name = 'text/browsing-data.txt'


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


def get_confidence(tuple_dict_list):
    tuples_confidence_dict_list = []

    # There is no support rule to find at index 0, as such, we need to start from index 1.
    # For each dictionary in the list...
    for i in range(1, len(tuple_dict_list)):
        # Instantiate a dictionary to prevent data loss.
        confidence_rule_dict = {}

        # For each key tuple in the dictionary of each list...
        for key_tup in tuple_dict_list[i].keys():
            # Convert each tuple to a list.
            key_list = list(key_tup)
            # Get each combination in the key for use in our tuple_dict_list.
            subkey_list = create_tuples_from_list(key_list, i)

            # For each combination in the key...
            for subkey_tup in subkey_list:
                # Create composite key for use later.
                confidence_key = (key_tup, subkey_tup)
                # Get the absolute support of the frequent combination of items.
                key_sup = tuple_dict_list[i][key_tup]
                # Get the absolute support of the sub-combinations frequently visited together.
                subkey_sup = tuple_dict_list[i - 1][subkey_tup]
                # associate the composite key used in the confidence_rule_dict with the support rule.
                confidence_rule_dict[confidence_key] = key_sup / subkey_sup
        # Append the confidence tuple dictionary to the tuples_confidence_dict_list.
        tuples_confidence_dict_list.append(confidence_rule_dict)

    return tuples_confidence_dict_list
    pass


# Sort the top 5 confidence rules at each dictionary in the list except the dictionary starting at index 0.
# There is no support to associate with items at index 0 - these are our base items.
def get_top_5_confidence(confidence_dict_list):
    top_5_confidence_nested_lists = []

    # While iterating over the confidence_dict_list index i...
    for i in range(len(confidence_dict_list)):
        # Instantiate the top 5 confidence list at this level.
        top_5_confidence_list = []

        # For each composite key in confidence_dict_list...
        for key_tup in confidence_dict_list[i].keys():
            # Get the confidence rule associated with this key. This was probably redundant. Not gonna worry about it.
            key_and_confidence_tup = (key_tup, confidence_dict_list[i][key_tup])
            # If the length of our list is less than 5 append the key and confidence rule.
            if len(top_5_confidence_list) < 5:
                top_5_confidence_list.append(key_and_confidence_tup)
            # Otherwise, if the lowest key's associated value in the list is less than the current key and confidence
            # rule, then replace the lowest key.
            elif top_5_confidence_list[-1][1] < key_and_confidence_tup[1]:
                top_5_confidence_list[-1] = key_and_confidence_tup
            # Sort the list. If we replaced a key and the current key is the greatest in the list, then it will filter
            # to the top.
            top_5_confidence_list = sorted(top_5_confidence_list, key=lambda tup: tup[1], reverse=True)
        top_5_confidence_nested_lists.append(top_5_confidence_list)

    return top_5_confidence_nested_lists


def format_top_5_confidence_lists(top_5_confidence_nested_lists):
    top_5_formatted_lists = []
    for unformatted_list in top_5_confidence_nested_lists:
        formatted_list = []
        # Almost there! For each tuple in the unformatted list...
        for tup in unformatted_list:
            # Example: (composite_key, confidence_value) = ((('smeckledorf', 'bamboozled'), 'something else') 0.124...)
            # The example values above reflects the types of data found in each tuple.
            key_tup, confidence_value = tup
            # Convert both the key and its associated subkey to arrays. The subkey represents items typically associated
            # with the items in the primary key.
            key_list = list(key_tup[0]) if isinstance(key_tup[0], tuple) else [key_tup[0]]
            subkey_list = list(key_tup[1]) if isinstance(key_tup[1], tuple) else [key_tup[1]]
            # The line below starts the frequently visited items lexicographically
            formatted_item = subkey_list
            # For each item in the key list not in the formatted_item list, append the item.
            for item in key_list:
                if item not in formatted_item:
                    formatted_item.append(item)
            # Add the confidence value to the formatted item.
            formatted_item.append(confidence_value)
            # Add the formatted item list to the formatted list of lists.
            formatted_list.append(formatted_item)
        # Add the list of lists to the list of list of lists. That's a little convoluted, isn't it?
        top_5_formatted_lists.append(formatted_list)
    return top_5_formatted_lists


def generate_strings(formatted_top_5_confidence_lists):
    # Let's make this modular. Start at letter 'A'.
    start_letter = ord('A')
    # Instantiate the formatted string.
    formatted_str = ''

    # For index i in the list of list of lists...
    for i in range(len(formatted_top_5_confidence_lists)):
        # Format the string with 'OUTPUT'.
        formatted_str += 'OUTPUT ' + chr(start_letter + i) + ':\n'
        # For index j in the list of lists...
        for j in range(len(formatted_top_5_confidence_lists[i])):
            # For item k in the list...
            for k in formatted_top_5_confidence_lists[i][j]:
                # k in this context can be something like FRO1234 or 0.123.
                formatted_str += str(k) + ' '
            # Add formatting.
            formatted_str += '\n'

    return formatted_str

def create_text_file(text):
    file = open('./text/PA1_output.txt', 'w')
    file.write(text)
    file.close()


# Driver code to run the program.
if __name__ == '__main__':
    tuple_dict_list = get_frequent_tuples(file_name, max_tuple_size, min_support)
    confidence_dict_list = get_confidence(tuple_dict_list)
    top_5_confidence_lists = get_top_5_confidence(confidence_dict_list)
    formatted_top_5_confidence_lists = format_top_5_confidence_lists(top_5_confidence_lists)
    create_text_file(generate_strings(formatted_top_5_confidence_lists))
