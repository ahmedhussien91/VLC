from networkx.algorithms.tree import coding

import configuration as cfg
import numpy as np
import json
import random

RUN_LENGTH_KEY = 0
MOTION_VECTORS_KEY = 1

SYMBOLS_DICTIONARY = {
    RUN_LENGTH_KEY: [],
    MOTION_VECTORS_KEY: []
}
SYMBOLS_COUNT_DICTIONARY = {
    RUN_LENGTH_KEY: [],
    MOTION_VECTORS_KEY: []
}
CODING_DICTIONARY = {
    RUN_LENGTH_KEY: [],
    MOTION_VECTORS_KEY: []
}

def calculate_entropy(coding_list, symbols_count_list):
    entropy = 0
    total_count = sum(symbols_count_list)

    for i in range(len(coding_list)):
        entropy += ((symbols_count_list[i] / total_count) * len(coding_list[i]))

    return entropy

def generate_huffman_coding(symbols_prob_dic):
    symbols_prob_dic = {key: value for key, value in sorted(symbols_prob_dic.items(), key=lambda item: item[1])}
    merge_symbols_dic = {}
    symbols_list = []
    coding_list = []
    symbols_count_list = []

    for key, value in symbols_prob_dic.items():
        merge_symbols_dic[(key, )] = value
        symbols_list.append(key)
        coding_list.append('')
        symbols_count_list.append(value)

    while len(merge_symbols_dic) > 1:
        # Sorting the dictionary with the probability of the symbols
        merge_symbols_dic = {key: value for key, value in sorted(merge_symbols_dic.items(), key=lambda item: item[1])}

        bit = '1'
        new_key = ()
        new_prob = 0.0
        
        for item in list(merge_symbols_dic.items()):
            new_key = item[0] + new_key
            new_prob += item[1]

            for symbol in item[0]:
                coding_list[symbols_list.index(symbol)] = bit + coding_list[symbols_list.index(symbol)]
            
            del merge_symbols_dic[item[0]]
            
            if '1' == bit:
                bit = '0'
            else:
                break

        merge_symbols_dic[new_key] = new_prob
    
    return symbols_list, symbols_count_list, coding_list


# this function should be called to generate the symbol-to-code dictionary for a specific frame type
#   "frame_type" is one of the types in configuration.py under the comment "Valid frame types"
#    [DCT_FRAME, MESH_FRAME, or MOTION_VECTORS_FRAME]
#   "symbols_prob_dic" is the dictionary contains the symbols with its probabilities
def generate_coding_dictionary(frame_type, symbols_prob_dic):
    symbols_list, symbols_count_list, coding_list = generate_huffman_coding(symbols_prob_dic)

    filename = ""
    if cfg.DCT_FRAME == frame_type:
        filename = "dct_coding_dictionary.txt"
    elif cfg.MOTION_VECTORS_FRAME == frame_type or cfg.MESH_FRAME == frame_type:
        filename = "motion_coding_dictionary.txt"

    with open(filename, 'w') as file:
        file.write(str([symbols_list, symbols_count_list, coding_list]))


def load_coding_dictionaries():
    filenames = ["dct_coding_dictionary.txt", "motion_coding_dictionary.txt"]

    i = 0
    for filename in filenames:
        with open(filename, 'r') as file:
            coding_dictionary_lists = eval(file.read())

            SYMBOLS_DICTIONARY[i] = coding_dictionary_lists[0]
            SYMBOLS_COUNT_DICTIONARY[i] = coding_dictionary_lists[1]
            CODING_DICTIONARY[i] = coding_dictionary_lists[2]
        i += 1


# this function must be called before encode(data) to start new frame
#   "frame_type" is one of the types in configuration.py under the comment "Valid frame types"
#   [DCT_FRAME, MESH_FRAME, or MOTION_VECTORS_FRAME]
#   This function returns True if a new frame started successfully, False if there is already a frame opened to encode
def begin_encoding(frame_type, box_size=0):
    print("frame started with type = " + str(frame_type))
    print("box_size = " + str(box_size))

    return True


# this function must be called after finishing the frame to save it to the file and clean the frame
def end_encoding():
    print("frame ended")
    
    return True


# this function must be called between a call of begin_encoding(frame_type) and end_encoding
# to attach the encoded data to the frame.
#   "data" is a numpy array for the data to be encoded
def encode(is_run_length_valid, data):
    print("run length valid  = " + str(is_run_length_valid))
    print("input shape = " + str(data.shape))


# this function returns the decoded frame type and the decoded data
# in list of layers of list of 2 [Is RunLength Valid, frame's data]
# example: [[True, np.array([5, 0, 6, 1, 10, 0])],
#           [False, np.array([0, 1, 0, 1, 0, 1])],
#           [True, np.array([5, 0, 6, 1, 10, 0])]]
# length of the returned list will be 1 in case of DCT frame
# and the number of the layers in case of mesh or motion vectors frames
def decode():
    frame_type = 0
    data = [[True, np.array([5, 0, 6, 1, 10, 0])],
            [False, np.array([0, 1, 0, 1, 0, 1])],
            [True, np.array([5, 0, 6, 1, 10, 0])]]
    box_size = 256
    return frame_type, box_size, data


def test_code_generation(frame_type, symbols_dictionary):
    # generate_coding_dictionary(cfg.DCT_FRAME, symbols_dictionary)
    # generate_coding_dictionary(cfg.MOTION_VECTORS_FRAME, symbols_dictionary)

    load_coding_dictionaries()

    for i in range(0, len(SYMBOLS_DICTIONARY[0])):
        print('[' + str(SYMBOLS_COUNT_DICTIONARY[0][i]) + ', ' + str(SYMBOLS_DICTIONARY[0][i]) + ']: ' +
              str(CODING_DICTIONARY[0][i]))
        
    print("entropy = " + str(calculate_entropy(CODING_DICTIONARY[0], SYMBOLS_COUNT_DICTIONARY[0])))
    print("var = " + str(np.array(SYMBOLS_COUNT_DICTIONARY[0]).std()))
    print("mean = " + str(np.mean(SYMBOLS_COUNT_DICTIONARY[0])))


if __name__ == "__main__":
    symbols_dic = {'a': 20, 'b': 30, 'c': 40,
                   'd': 50, 'e': 60, 'f': 70}

    test_code_generation(cfg.DCT_FRAME, symbols_dic)

    # total_count = 0
    # total_prob = 0

    # for i in range(1000):
    #     symbols_dic[i] = random.randint(1, 1000)
    #     total_count += symbols_dic[i]
    #
    # for j in range(len(symbols_dic)):
    #     symbols_dic[j] /= total_count
    #     total_prob += symbols_dic[j]

    # for step in range(1, 6, 1):
    #     i = 0
    #     prob_step = 0.03
    #     for item in symbols_dic.items():
    #         if i < 3:
    #             symbols_dic[item[0]] += prob_step
    #         elif 2 < i < 6:
    #             symbols_dic[item[0]] -= prob_step
    #         i += 1
    #
    #     test_code_generation(cfg.DCT_FRAME, symbols_dic)
