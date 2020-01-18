import hoffman_encoder as hoff
import run_length_encoder as rlc
import serializer as serl
import file_handler as f
import numpy as np
import configuration as cfg
import collections as col
import statistics_module as stat


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
    # TODO: Call the hoffman with the agreed sequence, check on encoded_meshStruct
    # data = hoff.encode_hoffman(symbolList)
    # binaryStreamStr = serl.SerializeIntoBitStream(data)
    # # write first time then append
    # f.write_to_binaryFile(binaryStreamStr)
    return

def encode_dct(quantized_dct_list):
    encoded_dct, is_runlength_valid = rlc.encode_dct(quantized_dct_list)
    # TODO: Do statistics on symbols
    stat.DoStatistics_DCT(encoded_dct)
    # TODO: Call the hoffman with the agreed sequance
    # data = hoff.encode_hoffman(symbolList)
    # binaryStreamStr = serl.SerializeIntoBitStream(data)
    # # write frist time then append 
    # f.write_to_binaryFile(binaryStreamStr)
    return

############################################## Decoder #############################################################
def decode_mesh(listOfData):
    data = serl.deSerialize_bitStream(listOfData)
    symbolList = hoff.decode_hoffman(data)
    decoded_meshStruct, meshStructSize = rlc.decode_meshStruct()
    decoded_meshVectors, meshVectorsSize = rlc.decode_meshVectors()

    return out

def decode_dct(listOfData):
    data = serl.deSerialize_bitStream(listOfData)
    symbolList = hoff.decode_hoffman(data)
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