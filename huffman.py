import configuration as cfg
import numpy as np
import bitarray
import time
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
CODING_LISTS = {
    RUN_LENGTH_KEY: [],
    MOTION_VECTORS_KEY: []
}

CODING_DICTIONARIES = {
    RUN_LENGTH_KEY: {},
    MOTION_VECTORS_KEY: {}
}
DECODING_DICTIONARIES = {
    RUN_LENGTH_KEY: {},
    MOTION_VECTORS_KEY: {}
}

ENCODED_DATA = bitarray.bitarray()

CURRENT_FRAME_TYPE = cfg.DCT_FRAME
CURRENT_FRAME = bitarray.bitarray()
FRAME_OPENED = False

DATA_TO_DECODE_OFFSET = 0


def calculate_entropy(coding_list, symbols_count_list):
    entropy = 0
    total_count = sum(symbols_count_list)

    for i in range(len(coding_list)):
        entropy += ((symbols_count_list[i] / total_count) * len(coding_list[i]))

    return entropy


def num_to_bitarray(num, no_of_bits=0):
    if 0 == no_of_bits:
        bitarr = bitarray.bitarray(str(bin(num)).lstrip('0b'))
    elif len(str(bin(num)).lstrip('0b')) <= no_of_bits:
        zero_bits_num = no_of_bits - len(str(bin(num)).lstrip('0b'))
        bitarr = bitarray.bitarray(zero_bits_num * [False])
        bitarr.extend(str(bin(num)).lstrip('0b'))
    else:
        assert False, "Casting Failed"

    return bitarr


def bitarray_to_num(bitarr):
    num = int(bitarr.to01(), 2)
    return num


def add_header():
    global CURRENT_FRAME
    CURRENT_FRAME += num_to_bitarray(cfg.FRAME_RESOLUTION[0], 16)
    CURRENT_FRAME += num_to_bitarray(cfg.FRAME_RESOLUTION[1], 16)
    CURRENT_FRAME += num_to_bitarray(cfg.YUV_CONFIG[0], 3)
    CURRENT_FRAME += num_to_bitarray(cfg.YUV_CONFIG[1], 3)
    CURRENT_FRAME += num_to_bitarray(cfg.YUV_CONFIG[2], 3)
    # TODO: add number of frames @ the end or we can end the frame with a code that is not a part of huffman code
    return


def generate_huffman_coding(symbols_prob_dic):
    symbols_prob_dic = {key: value for key, value in sorted(symbols_prob_dic.items(), key=lambda item: item[1])}
    merge_symbols_dic = {}
    symbols_list = []
    coding_list = []
    symbols_count_list = []

    for key, value in symbols_prob_dic.items():
        merge_symbols_dic[(key,)] = value
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
        filename = "CodingDictionaries/dct_coding_dictionary.txt"
    elif cfg.MOTION_VECTORS_FRAME == frame_type or cfg.MESH_FRAME == frame_type:
        filename = "CodingDictionaries/motion_coding_dictionary.txt"

    with open(filename, 'w') as file:
        file.write(str([symbols_list, symbols_count_list, coding_list]))


def load_coding_dictionaries():
    filenames = ["CodingDictionaries/dct_coding_dictionary.txt", "CodingDictionaries/motion_coding_dictionary.txt"]

    i = 0
    for filename in filenames:
        with open(filename, 'r') as file:
            coding_dictionary_lists = eval(file.read())

            SYMBOLS_DICTIONARY[i] = coding_dictionary_lists[0]
            SYMBOLS_COUNT_DICTIONARY[i] = coding_dictionary_lists[1]
            CODING_LISTS[i] = coding_dictionary_lists[2]

            for index in range(len(SYMBOLS_DICTIONARY[i])):
                CODING_DICTIONARIES[i][SYMBOLS_DICTIONARY[i][index]] = bitarray.bitarray(CODING_LISTS[i][index])
                DECODING_DICTIONARIES[i][CODING_LISTS[i][index]] = SYMBOLS_DICTIONARY[i][index]

        i += 1


# this function must be called before encode(data) to start new frame
#   "frame_type" is one of the types in configuration.py under the comment "Valid frame types"
#   [DCT_FRAME, MESH_FRAME, or MOTION_VECTORS_FRAME]
#   This function returns True if a new frame started successfully, False if there is already a frame opened to encode
def begin_encoding(frame_type, box_size=0):
    global CURRENT_FRAME, CURRENT_FRAME_TYPE, FRAME_OPENED, ENCODED_DATA

    if FRAME_OPENED:
        print("Error: encoding frame already opened.")
        return False

    assert (frame_type == cfg.DCT_FRAME) or (frame_type == cfg.MESH_FRAME) or (frame_type == cfg.MOTION_VECTORS_FRAME), \
        "Error: Invalid frame type."

    ENCODED_DATA += num_to_bitarray(frame_type, cfg.NUMBER_OF_BITS_FOR_FRAME_TYPE)

    cfg.INITIAL_MESH_BLOCK_SIZE = box_size
    CURRENT_FRAME_TYPE = frame_type
    CURRENT_FRAME = bitarray.bitarray()
    FRAME_OPENED = True

    return True


# this function must be called after finishing the frame to save it to the file and clean the frame
def end_encoding():
    global CURRENT_FRAME, FRAME_OPENED

    if not FRAME_OPENED:
        print("Error: frame already closed.")
        return False

    print('encoded stream = ' + str(len(ENCODED_DATA)))
    with open(cfg.OUTPUT_FILE_NAME, 'wb') as file:
        ENCODED_DATA.tofile(file)

    CURRENT_FRAME = bitarray.bitarray()
    FRAME_OPENED = False

    return True


def encode_symbol(is_run_length_valid, symbol, index, current_encoding_dictionary):
    global CURRENT_FRAME

    if is_run_length_valid and ((index % 2) == 0):
        CURRENT_FRAME += CODING_DICTIONARIES[RUN_LENGTH_KEY][symbol]
    else:
        CURRENT_FRAME += CODING_DICTIONARIES[current_encoding_dictionary][symbol]


# this function must be called between a call of begin_encoding(frame_type) and end_encoding
# to attach the encoded data to the frame.
#   "data" is a numpy array for the data to be encoded
def encode(is_run_length_valid, data):
    global FRAME_OPENED, CURRENT_FRAME, CURRENT_FRAME_TYPE, ENCODED_DATA

    if not FRAME_OPENED:
        print("Error: there is no frame opened for encoding.")
        return -1

    current_encoded_size = len(ENCODED_DATA)
    current_encoding_dictionary = -1

    if is_run_length_valid:
        ENCODED_DATA += bitarray.bitarray('1')
    else:
        ENCODED_DATA += bitarray.bitarray('0')

    if cfg.DCT_FRAME == CURRENT_FRAME_TYPE:
        current_encoding_dictionary = RUN_LENGTH_KEY
    elif cfg.MOTION_VECTORS_FRAME:
        current_encoding_dictionary = MOTION_VECTORS_KEY

    for i in range(0, len(data)):
        encode_symbol(is_run_length_valid, data[i], i, current_encoding_dictionary)

    current_frame_size = len(CURRENT_FRAME)
    ENCODED_DATA += num_to_bitarray(current_frame_size, cfg.NUMBER_OF_BITS_FOR_FRAME_STREAM_SIZE)
    ENCODED_DATA += CURRENT_FRAME
    CURRENT_FRAME = bitarray.bitarray()

    return len(ENCODED_DATA) - current_encoded_size


def begin_decoding():
    global DATA_TO_DECODE_OFFSET, ENCODED_DATA

    DATA_TO_DECODE_OFFSET = 0

    if len(ENCODED_DATA) == 0:
        ENCODED_DATA = bitarray.bitarray()

        with open(cfg.INPUT_FILE_NAME, 'rb') as file:
            ENCODED_DATA.fromfile(file)
            file.close()


def end_decoding():
    global DATA_TO_DECODE_OFFSET, ENCODED_DATA
    ENCODED_DATA = bitarray.bitarray()
    DATA_TO_DECODE_OFFSET = 0


# this function returns the decoded frame type and the decoded data
# in list of layers of list of 2 [Is RunLength Valid, frame's data]
# example: [[True, np.array([5, 0, 6, 1, 10, 0])],
#           [False, np.array([0, 1, 0, 1, 0, 1])],
#           [True, np.array([5, 0, 6, 1, 10, 0])]]
# length of the returned list will be 1 in case of DCT frame
# and the number of the layers in case of mesh or motion vectors frames
def decode():
    global DATA_TO_DECODE_OFFSET, ENCODED_DATA

    data = []

    decoding_dictionary = RUN_LENGTH_KEY

    frame_type = bitarray_to_num(ENCODED_DATA[DATA_TO_DECODE_OFFSET: DATA_TO_DECODE_OFFSET + cfg.NUMBER_OF_BITS_FOR_FRAME_TYPE])
    print("frame_type = " + str(frame_type))

    if frame_type == cfg.DCT_FRAME:
        decoding_dictionary = RUN_LENGTH_KEY
    elif frame_type == cfg.MOTION_VECTORS_FRAME:
        decoding_dictionary = MOTION_VECTORS_KEY

    DATA_TO_DECODE_OFFSET += cfg.NUMBER_OF_BITS_FOR_FRAME_TYPE

    number_of_layers = 0
    if frame_type == cfg.DCT_FRAME:
        number_of_layers = 3
    else:
        number_of_layers = bitarray_to_num(ENCODED_DATA[DATA_TO_DECODE_OFFSET:DATA_TO_DECODE_OFFSET + cfg.NUMBER_OF_BITS_FOR_LAYERS_COUNT])
        DATA_TO_DECODE_OFFSET += cfg.NUMBER_OF_BITS_FOR_LAYERS_COUNT

    for i in range(0, number_of_layers):
        new_decoded_layer = [False, np.array()]
        new_decoded_layer[0] = ENCODED_DATA[DATA_TO_DECODE_OFFSET]
        DATA_TO_DECODE_OFFSET += 1
        layer_stream_size = bitarray_to_num(ENCODED_DATA[DATA_TO_DECODE_OFFSET:cfg.NUMBER_OF_BITS_FOR_FRAME_STREAM_SIZE])
        DATA_TO_DECODE_OFFSET += cfg.NUMBER_OF_BITS_FOR_FRAME_STREAM_SIZE
        sub_encoded_stream = ENCODED_DATA[DATA_TO_DECODE_OFFSET:DATA_TO_DECODE_OFFSET + layer_stream_size]
        DATA_TO_DECODE_OFFSET += layer_stream_size

        code = ''
        for bit in sub_encoded_stream:
            if bit:
                code += '1'
            else:
                code += '0'

            if SYMBOLS_DICTIONARY[decoding_dictionary][code] is not None:
                new_decoded_layer[1] = np.append(new_decoded_layer[1], SYMBOLS_DICTIONARY[decoding_dictionary][code])
                code = ''

        data.append(new_decoded_layer)

    box_size = 256
    return frame_type, box_size, data


def test_code_generation(frame_type, symbols_dictionary):
    # generate_coding_dictionary(cfg.DCT_FRAME, symbols_dictionary)
    # generate_coding_dictionary(cfg.MOTION_VECTORS_FRAME, symbols_dictionary)

    load_coding_dictionaries()

    for i in range(0, len(SYMBOLS_DICTIONARY[0])):
        print('[' + str(SYMBOLS_COUNT_DICTIONARY[0][i]) + ', ' + str(SYMBOLS_DICTIONARY[0][i]) + ']: ' +
              str(CODING_LISTS[0][i]))

    print("entropy = " + str(calculate_entropy(CODING_LISTS[0], SYMBOLS_COUNT_DICTIONARY[0])))
    print("var = " + str(np.array(SYMBOLS_COUNT_DICTIONARY[0]).std()))
    print("mean = " + str(np.mean(SYMBOLS_COUNT_DICTIONARY[0])))

    data_to_encode = np.array(
        ['a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e',
         'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f',
         'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a',
         'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e', 'a', 'a', 'f', 'f', 'e', 'e'])

    time_start = time.time()
    begin_encoding(cfg.DCT_FRAME)
    encode(True, data_to_encode)
    with open("TestingOutput/test.bin", 'wb') as file:
        CURRENT_FRAME.tofile(file)
    end_encoding()
    time_end = time.time()

    print("consumed time = " + str(time_end - time_start))
    print("number of elements to encode = " + str(len(data_to_encode)))

    decode()


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
