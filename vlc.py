from scipy.spatial.distance import yule

import huffman as huff
import run_length_encoder as rlc
import serializer as serl
import file_handler as f
import numpy as np
import configuration as cfg
import collections as col
import statistics_module as stat


# ############################ Initialization Part ############################

# this function must be called before start encoding
#   "output_filename" the output file path that will contain the encoded file
#   "frame_resolution" the resolution of the frame to be encoded default value is [3840, 2160]
#   "yuv_config" which YUV configuration will be used default value is [4, 1, 1]
#   "encoder mode" =    0 -> encode data using generated DictionaryFile,
#                       1 -> generate DictionaryFile for hoffman probabilities
def init_encoder(output_filename, frame_resolution=None, yuv_config=None, encoder_mode=0):
    if frame_resolution is None:
        frame_resolution = [3840, 2160]
    if yuv_config is None:
        yuv_config = [4, 1, 1]

    assert ("" != output_filename), "Error: output file name could not be an empty string."
    cfg.OUTPUT_FILE_NAME = output_filename

    assert ((frame_resolution[0] > 0) and (frame_resolution[1] > 0)), \
        "Error: resolution can not be 0 or negative numbers."
    cfg.FRAME_RESOLUTION = frame_resolution

    assert (3 == len(yuv_config) and all(isinstance(n, int) for n in yuv_config)), \
        "Error: YUV array must be 3 integer values."
    assert (0 <= yuv_config[0] <= 4 and 0 <= yuv_config[1] <= 4 and 0 <= yuv_config[2] <= 4), \
        "Error: YUV values must be from 0 to 4"
    cfg.YUV_CONFIG = yuv_config
    cfg.ENCODER_MODE = encoder_mode
# this function must be called before decoding.
#   "input_filename" the input file path of the file to be decoded
def init_decoder(input_filename):
    assert ("" != input_filename), "Error: input file name could not be an empty string."
    cfg.INPUT_FILE_NAME = input_filename

# ############################ End of Initialization Part ############################


############################################## Encoder ############################################################
def encode_mesh(initial_mesh_block_size, mesh_struct_list, motion_vectors_list):
    frame_type = 0
    # encode using runlenght coding
    if mesh_struct_list is not None:
        encoded_meshStruct_list, is_runlength_valid_struct = rlc.encode_meshStruct(mesh_struct_list)
        frame_type = cfg.MESH_FRAME
    else:
        frame_type = cfg.MOTION_VECTORS_FRAME
    encoded_meshVector_list, is_runlength_valid_vectors = rlc.encode_meshVectors(motion_vectors_list)

    # Do statistics on symbols
    stat.DoStatistics_mesh(encoded_meshStruct_list, encoded_meshVector_list)

    # Call the huffman with the agreed sequence, check on encoded_meshStruct
    if cfg.ENCODER_MODE == 0:
        huff.begin_encoding(frame_type, initial_mesh_block_size)
        for i, encoded_meshVector in enumerate(encoded_meshVector_list):
            if frame_type == cfg.MESH_FRAME:
                huff.encode(is_runlength_valid_struct[i], encoded_meshStruct_list[i])
            huff.encode(is_runlength_valid_vectors[i], encoded_meshVector)
        huff.end_encoding()
    return

def encode_dct(quantized_dct_list):
    frame_type = cfg.DCT_FRAME
    encoded_dct, is_runlength_valid = rlc.encode_dct(quantized_dct_list)
    # Do statistics on symbols
    stat.DoStatistics_DCT(encoded_dct)

    # Call the hoffman with the agreed sequance
    if cfg.ENCODER_MODE == 0:
        huff.begin_encoding(frame_type)
        huff.encode(is_runlength_valid, encoded_dct)
        huff.end_encoding()

    return

'''I/P: frame_type: 0 -> DCT_FRAME, 1 -> MESH_FRAME, 2 -> MOTION_VECTORS_FRAME, 3 -> EOF_REACHED 
        listOfData: for DCT list of list of np array, 
                    for mesh [initial_mesh_block_size, mesh_struct_list of np array, motion_vectors_list of np array]
                    for vectors list of motion_vectors_list of np array
                    for end of file reached no data required
'''
def encode(frame_type, listOfData):

    if(frame_type == cfg.DCT_FRAME):
        encode_dct(listOfData[0])
    elif(frame_type == cfg.MESH_FRAME):
        encode_mesh(listOfData[0], listOfData[1], listOfData[2])
    elif(frame_type == cfg.MOTION_VECTORS_FRAME):
        encode_mesh(0, None, listOfData[0])
    elif(frame_type == cfg.END_FRAME):
        pass # TODO: call Ramy function to end the file

    return

############################################## Decoder #############################################################
def decode():
    # Huffman
    frame_type, box_size, listOfData = huff.decode()
    # run length
    if (frame_type == cfg.DCT_FRAME):
        decoded_data = rlc.decode_dct(listOfData[0][0], listOfData[0][1])
    elif (frame_type == cfg.MESH_FRAME):
        initial_mesh_block_size = box_size
        decoded_data = rlc.decode_mesh(initial_mesh_block_size, listOfData[0], listOfData[1])
    elif (frame_type == cfg.MOTION_VECTORS_FRAME):
        decoded_data = rlc.decode_mesh(None, listOfData[0])
    elif (frame_type == cfg.END_FRAME):
        pass  # TODO: call Ramy function to end the file

    return frame_type, decoded_data

if __name__ == "__main__":
    toggle = 0
    while (1):
        # input
        # DCT
        DCT_ip = [np.random.randint(cfg.runlenght_config[cfg.DCT]["SYMBOLS_COUNT"],size=cfg.NO_OF_DCT_BLOCKS),np.random.randint(cfg.runlenght_config[cfg.DCT]["SYMBOLS_COUNT"]
        ,size=int(cfg.NO_OF_DCT_BLOCKS/4)),np.random.randint(cfg.runlenght_config[cfg.DCT]["SYMBOLS_COUNT"], size=int(cfg.NO_OF_DCT_BLOCKS/4))]
        # mesh
        mesh_struct =  [np.random.randint(2,size=cfg.LAYER1_MESH_STRUCT_SIZE), np.random.randint(2,size=cfg.LAYER1_MESH_STRUCT_SIZE*4), np.random.randint(2,size=cfg.LAYER1_MESH_STRUCT_SIZE*4)]
        mesh_ip = [256,mesh_struct,[np.random.randint(-7,7,size = col.Counter(mesh_struct[0])[1]), np.random.randint(-7,7,size = col.Counter(mesh_struct[1])[1]), np.random.randint(-7,7,size = col.Counter(mesh_struct[2])[1])]]
        print("\n\n\ninput:")
        if(toggle):
            print(mesh_ip)
            encoded_str = encode_mesh(mesh_ip)
            print("\nencoded_str:")
            print(encoded_str)
            toggle = 0
            # print("\noutput:")
            # print(decode_mesh(encoded_str))
        else:
            print(DCT_ip)
            encoded_str = encode_dct(DCT_ip)
            print("\nencoded_str:")
            print(encoded_str)
            toggle = 1
            # print("\noutput:")
            # print(decode_dct(encoded_str))
        # output
        # decode(encoded_str)