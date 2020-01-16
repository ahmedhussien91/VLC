import hoffman_encoder as hoff
import run_length_encoder as rlc
import serializer as serl
import file_handler as f
import numpy as np

############################################## Encoder ############################################################
def encode_mesh():
    encoded_meshStruct, meshStructSize = rlc.encode_meshStruct()
    encoded_meshVector, meshVectorSize = rlc.encode_meshVectors()
    symbolList = encoded_meshVector + encoded_meshStruct

    data = hoff.encode_hoffman(symbolList)
    binaryStreamStr = serl.SerializeIntoBitStream(data)
    # write frist time then append
    f.write_to_binaryFile(binaryStreamStr)
    return out

def encode_dct():
    encoded_dct, dctSize = rlc.encode_dct()
    symbolList = encoded_dct

    data = hoff.encode_hoffman(symbolList)
    binaryStreamStr = serl.SerializeIntoBitStream(data)
    # write frist time then append 
    f.write_to_binaryFile(binaryStreamStr)
    return out

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
    # input
    
    encoded_str_mesh = encode_mesh()
    encoded_str_dct = encode_dct()
    print("input:")
    print(encoded_str_mesh)
    print(encoded_str_dct)
    # output
    print("\noutput:")
    # print(decode_mesh(encoded_str_mesh))
    # print(decode_dct(encoded_str_dct))
    decode()    