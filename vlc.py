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
def init_encoder(output_filename, frame_resolution=None, yuv_config=None):
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

# this function must be called before decoding.
#   "input_filename" the input file path of the file to be decoded
def init_decoder(input_filename):
    assert ("" != input_filename), "Error: input file name could not be an empty string."
    cfg.INPUT_FILE_NAME = input_filename

# ############################ End of Initialization Part ############################


############################################## Encoder ############################################################
def encode_mesh(initial_mesh_block_size, mesh_struct_list, motion_vectors_list):

    # encode using runlenght coding
    if mesh_struct_list is not None:  # TODO: Recheck this condition
        encoded_meshStruct, is_runlength_valid = rlc.encode_meshStruct(mesh_struct_list)
    else:
        encoded_meshStruct = []
    encoded_meshVector, is_runlength_valid = rlc.encode_meshVectors(motion_vectors_list)
    # TODO: Do statistics on symbols
    stat.DoStatistics_mesh(encoded_meshStruct, encoded_meshVector)
    # TODO: Call the huffman with the agreed sequence, check on encoded_meshStruct
    # data = huff.encode_huffman(symbolList)
    # binaryStreamStr = serl.SerializeIntoBitStream(data)
    # # write first time then append
    # f.write_to_binaryFile(binaryStreamStr)
    return

def encode_dct(quantized_dct_list):
    encoded_dct, is_runlength_valid = rlc.encode_dct(quantized_dct_list)
    # TODO: Do statistics on symbols
    stat.DoStatistics_DCT(encoded_dct)
    # TODO: Call the huffman with the agreed sequance
    # data = huff.encode_huffman(symbolList)
    # binaryStreamStr = serl.SerializeIntoBitStream(data)
    # # write frist time then append 
    # f.write_to_binaryFile(binaryStreamStr)
    return

############################################## Decoder #############################################################
def decode_mesh(listOfData):
    data = serl.deSerialize_bitStream(listOfData)
    symbolList = huff.decode_huffman(data)
    decoded_meshStruct, meshStructSize = rlc.decode_meshStruct()
    decoded_meshVectors, meshVectorsSize = rlc.decode_meshVectors()

    return out

def decode_dct(listOfData):
    data = serl.deSerialize_bitStream(listOfData)
    symbolList = huff.decode_huffman(data)
    encoded_dct, dctSize = rlc.decode_dct()

    return out

def decode():
    data = f.read_from_binaryFile()

    # read the frist u16 byte Size(15bits) + Type(1bit)
    # Type (1bit) 1 -> mesh, 0 -> dct
    # pass the data to  decode_dct() or decode_mesh()
    # jumb the Size and repeat the loop 

    current_pos = 0
    while(current_pos < (len(data)+1)):
        if (data[current_pos]):
            data_size = data[current_pos+1:current_pos+16]
            decode_mesh(data[current_pos+16:current_pos+data_size])
        else:
            data_size = data[current_pos+1:current_pos+16]
            decode_dct(data[current_pos+16:current_pos+data_size])
        
        current_pos = current_pos + data_size + 16
    return

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