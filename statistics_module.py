# Define some status global variable that is filled by other module
# count the status variable and provide statistics 
# status variables -> is Runlenght valid from mesh structure, mesh vectors, DCT blocks
import collections as col
import huffman as hoff
import configuration as cfg

meshStruct_isRunLenghtCodingValid_Validcount = 0
meshVector_isRunLenghtCodingValid_Validcount = 0
DCT_isRunLenghtCodingValid_Validcount = 0

meshStruct_isRunLenghtCodingValid_InValidcount = 0
meshVector_isRunLenghtCodingValid_InValidcount = 0
DCT_isRunLenghtCodingValid_InValidcount = 0

meshStruct_Symbols_count_dic = {}
meshVector_Symbols_count_dic = {}
DCT_Symbols_count_dic = {}

meshStruct_Symbols_prob_dic = {}
meshVector_Symbols_prob_dic = {}
DCT_Symbols_prob_dic = {}

meshStruct_total_symbols_count = 0
meshVector_total_symbols_count = 0
DCT_total_symbols_count = 0

DCT_Total_Count = 0
mesh_Total_Count = 0

def DoStatistics_mesh(encoded_meshStruct_list, encoded_meshVector_list):
    global mesh_Total_Count

    # count the total mesh cycles
    mesh_Total_Count = mesh_Total_Count + 1
    # Huffman
    ## count the total number of symbols then count unique symbols then append on dictionary
    if not encoded_meshStruct_list:
        for encoded_meshStruct in encoded_meshStruct_list:
            meshStruct_total_symbols_count = meshStruct_total_symbols_count + len(encoded_meshStruct)
            for symbol, count in col.Counter(encoded_meshStruct).items():
                if symbol in meshStruct_Symbols_count_dic:
                    meshStruct_Symbols_count_dic[symbol] = meshStruct_Symbols_count_dic[symbol] + count
                else:
                    meshStruct_Symbols_count_dic[symbol] = count

    for encoded_meshVector in encoded_meshVector_list:
        meshVector_total_symbols_count = meshVector_total_symbols_count + len(encoded_meshVector)
        for symbol, count in col.Counter(encoded_meshVector).items():
            if symbol in meshVector_Symbols_count_dic:
                meshVector_Symbols_count_dic[symbol] = meshVector_Symbols_count_dic[symbol] + count
            else:
                meshVector_Symbols_count_dic[symbol] = count

    #
    return

def DoStatistics_DCT(encoded_dct_list):
    global DCT_Total_Count

    # count the total DCT cycles
    DCT_Total_Count = DCT_Total_Count + 1
    # Huffman
    ## count the total number of symbols then count unique symbols then append on dictionary
    for encoded_dct in encoded_dct_list:
        DCT_total_symbols_count = DCT_total_symbols_count + len(encoded_dct)
        for symbol, count in col.Counter(encoded_dct).items():
            if symbol in DCT_Symbols_count_dic:
                DCT_Symbols_count_dic[symbol] = DCT_Symbols_count_dic[symbol] + count
            else:
                DCT_Symbols_count_dic[symbol] = count

    return


def GetProbability_GenerateHoffmanTable():
    for symbol, count in DCT_Symbols_count_dic.items():
        DCT_Symbols_prob_dic[symbol] = DCT_Symbols_count_dic/DCT_total_symbols_count
    for symbol, count in meshVector_Symbols_count_dic.items():
        meshVector_Symbols_prob_dic[symbol] = meshVector_Symbols_count_dic / meshVector_total_symbols_count
    for symbol, count in meshStruct_Symbols_count_dic.items():
        meshStruct_Symbols_prob_dic[symbol] = meshStruct_Symbols_count_dic / meshStruct_total_symbols_count

    hoff.generate_coding_dictionary(cfg.DCT_FRAME, DCT_Symbols_prob_dic)
    hoff.generate_coding_dictionary(cfg.MESH_FRAME, meshStruct_Symbols_prob_dic)
    hoff.generate_coding_dictionary(cfg.MOTION_VECTORS_FRAME, meshVector_Symbols_prob_dic)
    return