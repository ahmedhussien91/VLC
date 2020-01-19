import configuration as cfg
import numpy as np
import random


# this function should be called to generate the symbol-to-code dictionary for a specific frame type
#   "frame_type" is one of the types in configuration.py under the comment "Valid frame types"
#    [DCT_FRAME, MESH_FRAME, or MOTION_VECTORS_FRAME]
#   "symbol_prob_dic" is the dictionary contains the symbols with its probabilities
def generate_coding_dictionary(frame_type, symbol_prob_dic):
    symbol_prob_dic = {k: v for k, v in sorted(symbol_prob_dic.items(), key=lambda item: item[1])}
    print("generate dic for type = " + str(frame_type))
    print("symbol_prob_dic = " + str(symbol_prob_dic))
    # print("symbol_prob_dic = " + str(sorted_symbol_dic))


def load_coding_dictionaries():
    print("loading coding dictionaries.")


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


if __name__ == "__main__":
    symbols_dic = {}
    total_count = 0
    total_prob = 0
    for i in range(127):
        symbols_dic[i] = random.randint(1, 1000)
        total_count += symbols_dic[i]

    for j in range(len(symbols_dic)):
        symbols_dic[j] /= total_count
        total_prob += symbols_dic[j]

    generate_coding_dictionary(cfg.DCT_FRAME, symbols_dic)

