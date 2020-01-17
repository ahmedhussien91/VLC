
'''This File contain the Configuration of the encoder data type 
Data type Configurations: 
- MAX_COUNT: max occurance count for runlenght coding, e.g in dct 8x8 blocks max count can be 64
- "NO_OF_MAX_COUNT_BITS": max number of bits to carry the count, e.g dctOUNT=64 -> "NO_OF_MAX_COUNT_BITS"=6  
- "SYMBOLS_COUNT": number of symbols for this data type
- "NO_OF_SYMBOL_BITS": max number of bits to carry all the symbols of the data type, e.g "SYMBOLS_COUNT"=64 -> "NO_OF_SYMBOL_BITS"=6  
- "FULL_LENGTH": "NO_OF_SYMBOL_BITS" + "NO_OF_MAX_COUNT_BITS" 
 '''

# runlenght_config Structure Indices 
MESH = 0
MESH_VECTORS = 1
DCT = 2
# runlenght_config Structure
runlenght_config = ([ 
    #MESH Structure 
    {
        "MAX_COUNT" : 128,     # agreed with ramy on it 
        "NO_OF_MAX_COUNT_BITS" : 7,  
        "SYMBOLS_COUNT" : 2,
        "NO_OF_SYMBOL_BITS" : 1, 
        "FULL_LENGTH" : 8,    # 7+1
    },
    # MESH VECTORS
    {
        "MAX_COUNT" : 255,    # minimum value (Not agreed on)
        "NO_OF_MAX_COUNT_BITS" : 8,  
        "SYMBOLS_COUNT" : 14,
        "NO_OF_SYMBOL_BITS" : 4,
        "FULL_LENGTH" : 12,   # 8+4
    },
    # DCT
    { 
        "MAX_COUNT" : 64,
        "NO_OF_MAX_COUNT_BITS" : 6,  
        "SYMBOLS_COUNT" : 64,          # depend on the quantization assumed 64
        "NO_OF_SYMBOL_BITS" : 6, 
        "FULL_LENGTH" : 12,    # 6+6
    }
])

# DCT Input Image Configuration 
IMAGE_PIXEL_SIZE = 3840*2160
DCT_BLOCK_PIXEL_SIZE = 8*8
NO_OF_DCT_BLOCKS = int(IMAGE_PIXEL_SIZE/DCT_BLOCK_PIXEL_SIZE)

# Mesh Input Image Configuration
NO_OF_LAYERS = 4
LAYER1_BLOCK_SIZE = 265
LAYER1_MESH_STRUCT_SIZE = int(IMAGE_PIXEL_SIZE/(LAYER1_BLOCK_SIZE * LAYER1_BLOCK_SIZE))
LAYER1_MESH_VECTORS_SIZE = LAYER1_MESH_STRUCT_SIZE * 4
# to get the layer structure after this layer LAYER2_MESH_STRUCT_SIZE = LAYER1_MESH_STRUCT_SIZE * 4
# to get the layer mesh LAYER2_MESH_VECTORS_SIZE = LAYER2_MESH_STRUCT_SIZE * 5 