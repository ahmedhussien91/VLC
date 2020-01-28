import configuration as cfg
import numpy as np
import bitarray
import time
import os.path
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
CURRENT_LAYER = 0
CURRENT_FRAME = bitarray.bitarray()
FRAME_OPENED = False

CURRENT_ENCODING_FRAME_NUMBER = 0
CURRENT_DECODING_FRAME_NUMBER = 0

DATA_TO_DECODE_OFFSET = 0

CODE_LENGTH_LIST = np.array([], dtype=np.uint8)


def calculate_entropy(coding_list, symbols_count_list):
    entropy = 0
    total_count = sum(symbols_count_list)

    for i in range(len(coding_list)):
        entropy += ((symbols_count_list[i] / total_count) * len(coding_list[i]))

    return entropy


def num_to_bitarray(num, no_of_bits=0):
    bitarr = bitarray.bitarray()

    if num < 0:
        bitarr = bitarray.bitarray('1')
        num = abs(num)
        no_of_bits -= 1

    if 0 == no_of_bits:
        bitarr += bitarray.bitarray(str(bin(num)).lstrip('0b'))
    elif len(str(bin(num)).lstrip('0b')) <= no_of_bits:
        zero_bits_num = no_of_bits - len(str(bin(num)).lstrip('0b'))
        bitarr += bitarray.bitarray(zero_bits_num * [False])
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
    global CODE_LENGTH_LIST
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

                if len(CODING_LISTS[i][index]) not in CODE_LENGTH_LIST:
                    CODE_LENGTH_LIST = np.append(CODE_LENGTH_LIST, len(CODING_LISTS[i][index]))

        i += 1

    CODE_LENGTH_LIST.sort()
    print("CODE_LENGTH_LIST = ", CODE_LENGTH_LIST)


# this function must be called before encode(data) to start new frame
#   "frame_type" is one of the types in configuration.py under the comment "Valid frame types"
#   [DCT_FRAME, MESH_FRAME, or MOTION_VECTORS_FRAME]
#   This function returns True if a new frame started successfully, False if there is already a frame opened to encode
def begin_encoding(frame_type, number_of_layers=3, box_size=256):
    global CURRENT_FRAME, CURRENT_FRAME_TYPE, FRAME_OPENED, ENCODED_DATA, CURRENT_LAYER

    if FRAME_OPENED:
        print("Error: encoding frame already opened.")
        return False

    assert (frame_type == cfg.DCT_FRAME) or (frame_type == cfg.MESH_FRAME) or (frame_type == cfg.MOTION_VECTORS_FRAME), \
        "Error: Invalid frame type."

    ENCODED_DATA += num_to_bitarray(frame_type, cfg.NUMBER_OF_BITS_FOR_FRAME_TYPE)

    if frame_type == cfg.MESH_FRAME:
        ENCODED_DATA += num_to_bitarray(box_size, cfg.NUMBER_OF_BITS_FOR_INITIAL_MESH_SIZE)

    if frame_type == cfg.MESH_FRAME or frame_type == cfg.MOTION_VECTORS_FRAME:
        ENCODED_DATA += num_to_bitarray(number_of_layers, cfg.NUMBER_OF_BITS_FOR_LAYERS_COUNT)

    cfg.INITIAL_MESH_BLOCK_SIZE = box_size
    CURRENT_FRAME_TYPE = frame_type
    CURRENT_FRAME = bitarray.bitarray()
    FRAME_OPENED = True
    CURRENT_LAYER = 0

    return True


# this function must be called after finishing the frame to save it to the file and clean the frame
def end_encoding():
    global CURRENT_FRAME, FRAME_OPENED, CURRENT_LAYER, CURRENT_ENCODING_FRAME_NUMBER, ENCODED_DATA

    if not FRAME_OPENED:
        print("Error: frame already closed.")
        return False

    print('encoded stream = ' + str(len(ENCODED_DATA)))
    with open(cfg.OUTPUT_FILES_NAME_PATH + str(CURRENT_ENCODING_FRAME_NUMBER) + cfg.FRAME_FILE_EXTENSION, 'wb') as file:
        ENCODED_DATA.tofile(file)
        file.close()

    CURRENT_ENCODING_FRAME_NUMBER += 1

    ENCODED_DATA = bitarray.bitarray()
    CURRENT_FRAME = bitarray.bitarray()
    FRAME_OPENED = False
    CURRENT_LAYER = 0

    return True


def encode_mesh(element, is_count):
    if is_count:
        bit_size = cfg.NUMBER_OF_BITS_FOR_MESH_STRUCT_COUNT
    else:
        bit_size = cfg.NUMBER_OF_BITS_FOR_MESH_STRUCT_NODE

    return num_to_bitarray(element, bit_size)


# this function must be called between a call of begin_encoding(frame_type) and end_encoding
# to attach the encoded data to the frame.
#   "data" is a numpy array for the data to be encoded
def encode(is_run_length_valid, data):
    global FRAME_OPENED, CURRENT_FRAME, CURRENT_FRAME_TYPE, ENCODED_DATA, CURRENT_LAYER

    if not FRAME_OPENED:
        print("Error: there is no frame opened for encoding.")
        return -1

    current_encoded_size = len(ENCODED_DATA)

    if is_run_length_valid:
        ENCODED_DATA += bitarray.bitarray('1')
    else:
        ENCODED_DATA += bitarray.bitarray('0')

    if CURRENT_FRAME_TYPE == cfg.DCT_FRAME:
        CURRENT_FRAME.encode(CODING_DICTIONARIES[RUN_LENGTH_KEY], data)
    elif CURRENT_FRAME_TYPE == cfg.MESH_FRAME and (CURRENT_LAYER % 2 == 0):
        for i in range(0, len(data)):
            CURRENT_FRAME += encode_mesh(data[i], (is_run_length_valid and (i % 2) == 0))
    elif CURRENT_FRAME_TYPE == cfg.MOTION_VECTORS_FRAME or CURRENT_FRAME_TYPE == cfg.MESH_FRAME:
        CURRENT_FRAME.encode(CODING_DICTIONARIES[MOTION_VECTORS_KEY], data)
    else:
        assert False, "Error: Invalid frame type."

    if CURRENT_FRAME_TYPE == cfg.DCT_FRAME:
        number_of_bit_for_stream_size = cfg.NUMBER_OF_BITS_FOR_DCT_STREAM_SIZE
    elif CURRENT_FRAME_TYPE == cfg.MESH_FRAME and (CURRENT_LAYER % 2) == 0:
        number_of_bit_for_stream_size = cfg.NUMBER_OF_BITS_FOR_MESH_STRUCT_STREAM
    elif CURRENT_FRAME_TYPE == cfg.MOTION_VECTORS_FRAME or CURRENT_FRAME_TYPE == cfg.MESH_FRAME:
        number_of_bit_for_stream_size = cfg.NUMBER_OF_BITS_FOR_MOTION_VECTOR_STREAM

    current_frame_size = len(CURRENT_FRAME)
    ENCODED_DATA += num_to_bitarray(current_frame_size, number_of_bit_for_stream_size)
    ENCODED_DATA += CURRENT_FRAME
    CURRENT_FRAME = bitarray.bitarray()
    CURRENT_LAYER += 1

    return len(ENCODED_DATA) - current_encoded_size


def begin_decoding():
    global DATA_TO_DECODE_OFFSET, ENCODED_DATA

    DATA_TO_DECODE_OFFSET = 0

    filename = cfg.INPUT_FILES_NAME_PATH + str(CURRENT_DECODING_FRAME_NUMBER) + cfg.FRAME_FILE_EXTENSION
    if os.path.exists(filename):
        if len(ENCODED_DATA) == 0:
            ENCODED_DATA = bitarray.bitarray()

            with open(filename, 'rb') as file:
                ENCODED_DATA.fromfile(file)
                file.close()
    else:
        ENCODED_DATA = bitarray.bitarray()


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
    global DATA_TO_DECODE_OFFSET, ENCODED_DATA, CURRENT_DECODING_FRAME_NUMBER

    if ENCODED_DATA.length() == 0:
        return cfg.EOF_REACHED, -1, []

    data = []

    frame_type = bitarray_to_num(
        ENCODED_DATA[DATA_TO_DECODE_OFFSET: DATA_TO_DECODE_OFFSET + cfg.NUMBER_OF_BITS_FOR_FRAME_TYPE])
    print("frame_type = " + str(frame_type))
    DATA_TO_DECODE_OFFSET += cfg.NUMBER_OF_BITS_FOR_FRAME_TYPE

    box_size = -1
    if frame_type == cfg.MESH_FRAME:
        box_size = bitarray_to_num(ENCODED_DATA[DATA_TO_DECODE_OFFSET:
                                                DATA_TO_DECODE_OFFSET + cfg.NUMBER_OF_BITS_FOR_INITIAL_MESH_SIZE])
        DATA_TO_DECODE_OFFSET += cfg.NUMBER_OF_BITS_FOR_INITIAL_MESH_SIZE

    number_of_layers = 0
    if frame_type == cfg.DCT_FRAME:
        number_of_layers = 3
    else:
        number_of_layers = bitarray_to_num(
            ENCODED_DATA[DATA_TO_DECODE_OFFSET:DATA_TO_DECODE_OFFSET + cfg.NUMBER_OF_BITS_FOR_LAYERS_COUNT])
        DATA_TO_DECODE_OFFSET += cfg.NUMBER_OF_BITS_FOR_LAYERS_COUNT

    for i in range(0, number_of_layers):
        new_decoded_layer = [False, np.array([], dtype=np.uint8)]
        new_decoded_layer[0] = ENCODED_DATA[DATA_TO_DECODE_OFFSET]  # adding the bit that represent if run length coding valid or not
        DATA_TO_DECODE_OFFSET += 1

        if frame_type == cfg.DCT_FRAME:
            number_of_bit_for_stream_size = cfg.NUMBER_OF_BITS_FOR_DCT_STREAM_SIZE
        elif frame_type == cfg.MESH_FRAME and (i % 2 == 0):
            number_of_bit_for_stream_size = cfg.NUMBER_OF_BITS_FOR_MESH_STRUCT_STREAM
        elif frame_type == cfg.MOTION_VECTORS_FRAME or frame_type == cfg.MESH_FRAME:
            number_of_bit_for_stream_size = cfg.NUMBER_OF_BITS_FOR_MOTION_VECTOR_STREAM

        layer_stream_size = bitarray_to_num(
            ENCODED_DATA[DATA_TO_DECODE_OFFSET: DATA_TO_DECODE_OFFSET + number_of_bit_for_stream_size])
        DATA_TO_DECODE_OFFSET += number_of_bit_for_stream_size

        sub_encoded_stream = ENCODED_DATA[DATA_TO_DECODE_OFFSET:DATA_TO_DECODE_OFFSET + layer_stream_size]
        DATA_TO_DECODE_OFFSET += layer_stream_size

        if frame_type == cfg.DCT_FRAME:
            new_decoded_layer[1] = np.array(sub_encoded_stream.decode(CODING_DICTIONARIES[RUN_LENGTH_KEY]), dtype=np.uint8)
        elif frame_type == cfg.MESH_FRAME and (i % 2 == 0):
            layer_offset = 0
            current_element_index = 0
            while layer_offset < len(sub_encoded_stream):
                if new_decoded_layer[0] and (current_element_index % 2) == 0:
                    bit_size = cfg.NUMBER_OF_BITS_FOR_MESH_STRUCT_COUNT
                else:
                    bit_size = cfg.NUMBER_OF_BITS_FOR_MESH_STRUCT_NODE
                new_decoded_layer[1] = np.append(new_decoded_layer[1], bitarray_to_num(sub_encoded_stream[layer_offset:
                                                                                       layer_offset + bit_size]))
                layer_offset += bit_size
                current_element_index += 1
        elif frame_type == cfg.MOTION_VECTORS_FRAME or frame_type == cfg.MESH_FRAME:
            new_decoded_layer[1] = np.array(sub_encoded_stream.decode(CODING_DICTIONARIES[MOTION_VECTORS_KEY]), dtype=np.int)

        data.append(new_decoded_layer)

    CURRENT_DECODING_FRAME_NUMBER += 1

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
