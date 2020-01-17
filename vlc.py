import hoffman_encoder as hoff
import run_length_encoder as rlc
import serializer as serl
import file_handler as f
import numpy as np
import configuration as cfg
import collections as col

############################################## Encoder ############################################################
def encode_mesh(data):
    encoded_meshStruct, meshStructSize = rlc.encode_meshStruct(data[1])
    encoded_meshVector, meshVectorSize = rlc.encode_meshVectors(data[2])
    symbolList = [data [0]] + encoded_meshStruct + encoded_meshVector

    # data = hoff.encode_hoffman(symbolList)
    # binaryStreamStr = serl.SerializeIntoBitStream(data)
    # # write frist time then append
    # f.write_to_binaryFile(binaryStreamStr)
    return symbolList

def encode_dct(data):
    encoded_dct, dctSize = rlc.encode_dct(data)
    symbolList = encoded_dct

    # data = hoff.encode_hoffman(symbolList)
    # binaryStreamStr = serl.SerializeIntoBitStream(data)
    # # write frist time then append 
    # f.write_to_binaryFile(binaryStreamStr)
    return symbolList

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
        mesh_struct =  np.random.randint(2,size=cfg.LAYER1_MESH_STRUCT_SIZE)
        mesh_ip = [256,mesh_struct,np.random.randint(-7,7,size = col.Counter(mesh_struct)[1])]
        print("\n\n\ninput:")
        if(toggle):
            print(mesh_ip)
            encoded_str = encode_mesh(mesh_ip)
            print("\nencoded_str:")
            print(encoded_str)
            toggle = 0
        else:
            print(DCT_ip)
            encoded_str = encode_dct(DCT_ip)
            print("\nencoded_str:")
            print(encoded_str)
            toggle = 1 
        # output
        # print("\noutput:")
        # # print(decode_mesh(encoded_str_mesh))
        # # print(decode_dct(encoded_str_dct))
        # decode(encoded_str)    