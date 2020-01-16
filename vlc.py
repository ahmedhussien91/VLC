import hoffman_encoder as hoff
import run_length_encoder as rlc
import serializer as serl
import file_handler as f

def encode_mesh():
    encoded_meshStruct, meshStructSize = rlc.encode_meshStruct()
    encoded_meshVector, meshVectorSize = rlc.encode_meshVectors()

    hoff.encode_hoffman()
    serl.SerializeIntoBitStream()
    f.write_to_binaryFile()
    return out

def encode_dct():
    encoded_dct, dctSize = rlc.encode_dct()

    hoff.encode_hoffman()
    serl.SerializeIntoBitStream()
    f.write_to_binaryFile()
    return out


def decode_mesh():
    f.read_from_binaryFile()
    serl.deSerialize_bitStream()
    hoff.decode_hoffman()
    decoded_meshStruct, meshStructSize = rlc.decode_meshStruct()
    decoded_meshVectors, meshVectorsSize = rlc.decode_meshVectors()

    return out

def decode_dct():
    f.read_from_binaryFile()
    serl.deSerialize_bitStream()
    hoff.decode_hoffman()
    encoded_dct, dctSize = rlc.decode_dct()

    return out


if __name__ == "__main__":    
    # input 
    encoded_str_mesh = encode_mesh("aaabbcdddd")
    encoded_str_dct = encode_dct()
    print("input:")
    print(encoded_str_mesh)
    print(encoded_str_dct)
    # output
    print("\noutput:")
    print(decode_mesh(encoded_str_mesh))
    print(decode_dct(encoded_str_dct))    