
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