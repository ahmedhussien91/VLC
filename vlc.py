import runLength_encoding as rlc

def encode_mesh():
    encoded_meshStruct, meshStructSize = rlc.encode_mesh_struct()
    encoded_meshVector, meshVectorSize = rlc.encode_mesh_vectors()

    execute_Hoffman()
    SerializeIntoBitStream()
    writeToBinaryFile()
    return 

def encode_dct():
    encoded_dct, dctSize = rlc.encode_dct():

    execute_Hoffman()
    SerializeIntoBitStream()
    writeToBinaryFile()
    return
