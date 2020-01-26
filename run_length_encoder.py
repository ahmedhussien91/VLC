import configuration as cfg
import statistics_module as stat
import numpy as np

########################################### Run lenght coding #######################################################
def encode(text):

    """
    Returns a run-length encoded string from an input string.
    Note: This function will not return the character count in the return
    string if only a single instance of the character is found.

    Args:
        text (str): A string to encode

    Returns:
        str: A run length encoded string

    Example:
        input: "aaabbcdddd"
        returns: "3a2b1c4d"
    """

    count = 1
    previous = None
    result = []

    for character in text:
        if (character != previous) or (count == 127) :
            if previous != None:
                result.append(int(count))
                result.append(int(character))
            count = 1
            previous = character
        else:
            count += 1
    else:
        result.append(int(count))
        result.append(int(character))

    return result

def decode(text):
        
    """
    Returns a decoded string from an input runlength encoded string.
    Note: This function will not return the character count in the return
    string if only a single instance of the character is found.

    Args:
        text (str): A run length encoded string

    Returns:
        str: A string to encode

    Example:
        input: "3a2b1c4d"
        returns: "aaabbcdddd"
    """
    result= []
    isCount = True
    for character in text:
        if isCount:
            count = int(character)
            isCount = False
        else:
            for i in range(count):
                result.append(character)
            isCount = True                

    return result

########################################### Encoder #################################################################
def encode_meshStruct(data_np_arr_list): 
    encoded_meshStruct = []
    is_run_length_valid = []
    for i,data_np_arr in enumerate(data_np_arr_list):
        encoded_meshStruct.append(encode(list(data_np_arr)))
    # check that the runlength coding valid for each data block
    for i, data_np_arr in enumerate(data_np_arr_list):
        if len(data_np_arr) < len(encoded_meshStruct[i]):
            is_run_length_valid.append(False)
            encoded_meshStruct[i] = data_np_arr
            stat.meshStruct_isRunLenghtCodingValid_InValidcount = stat.meshStruct_isRunLenghtCodingValid_InValidcount + 1
        else:
            is_run_length_valid.append(True)
            stat.meshStruct_isRunLenghtCodingValid_Validcount = stat.meshStruct_isRunLenghtCodingValid_Validcount + 1
    return encoded_meshStruct, is_run_length_valid


def encode_meshVectors(data_np_arr_list):
    encoded_meshVector = []
    is_run_length_valid = []
    for i, data_np_arr in enumerate(data_np_arr_list):
        encoded_meshVector.append(encode(list(data_np_arr)))
        # check that the runlength coding valid for each data block
    for i, data_np_arr in enumerate(data_np_arr_list):
        if len(data_np_arr) < len(encoded_meshVector[i]):
            is_run_length_valid.append(False)
            encoded_meshVector[i] = data_np_arr
            stat.meshVector_isRunLenghtCodingValid_InValidcount = stat.meshVector_isRunLenghtCodingValid_InValidcount + 1
        else:
            is_run_length_valid.append(True)
            stat.meshVector_isRunLenghtCodingValid_Validcount = stat.meshVector_isRunLenghtCodingValid_Validcount + 1

    return encoded_meshVector, is_run_length_valid


def encode_dct(data_np_arr_list):
    is_run_length_valid = []
    concatenated_encoded_dct = []

    # concatenate the dct
    for dct in list(data_np_arr_list):
        # Do Run length coding
        encoded_dct = encode(dct)

        if len(dct) < len(encoded_dct):
            is_run_length_valid.append(False)
            concatenated_encoded_dct.append(np.array(dct))
            stat.DCT_isRunLenghtCodingValid_InValidcount = stat.DCT_isRunLenghtCodingValid_InValidcount + 1
        else:
            stat.DCT_isRunLenghtCodingValid_Validcount = stat.DCT_isRunLenghtCodingValid_Validcount + 1
            concatenated_encoded_dct.append(encoded_dct)
            is_run_length_valid.append(True)

    return concatenated_encoded_dct, is_run_length_valid


######################################### Decoder ###################################################################
def decode_mesh(initial_mesh_block_size, data_np_arr_list):
    box_size = 0
    decoded_meshStruct = []
    decoded_meshVectors = []
    # add the initial_mesh_block_size
    if initial_mesh_block_size:
        box_size = initial_mesh_block_size
    # add mesh struct and mesh vectors
    isStruct = True
    for i, data_np_arr_rlcValid in enumerate(data_np_arr_list):
        if initial_mesh_block_size:
            if isStruct:
                if data_np_arr_rlcValid[0]:
                    decoded_meshStruct.append(np.array(decode(data_np_arr_rlcValid[1])))
                else:
                    decoded_meshStruct.append(data_np_arr_rlcValid[1])
                isStruct = False
            else :
                if data_np_arr_rlcValid[0]:
                    decoded_meshVectors.append(np.array(decode(data_np_arr_rlcValid[1])))
                else:
                    decoded_meshVectors.append(data_np_arr_rlcValid[1])
                isStruct = True
        else:
            if data_np_arr_rlcValid[0]:
                decoded_meshVectors.append(np.array(decode(data_np_arr_rlcValid[1])))
            else:
                decoded_meshVectors.append(data_np_arr_rlcValid[1])

    return [box_size, decoded_meshStruct, decoded_meshVectors]



    return


def decode_dct(is_run_length_valid, dct_np_arr):
    quantized_dct_list = []
    # decode run length if it's valid
    if is_run_length_valid:
        dct_np_arr = decode(list(dct_np_arr))
    # separate into 3 lists depending on configuration
    cfg_sum = sum(cfg.YUV_CONFIG)
    ysize = int((cfg.YUV_CONFIG[0] / cfg_sum) * len(list(dct_np_arr)))
    usize = int((cfg.YUV_CONFIG[1] / cfg_sum) * len(list(dct_np_arr)))
    vsize = int((cfg.YUV_CONFIG[2] / cfg_sum) * len(list(dct_np_arr)))
    quantized_dct_list.append(np.array(dct_np_arr[0: ysize]))
    quantized_dct_list.append(np.array(dct_np_arr[ysize: ysize + usize]))
    quantized_dct_list.append(np.array(dct_np_arr[ysize + usize: ysize + usize + vsize]))

    return quantized_dct_list

if __name__ == "__main__":
        
    encoded_str = encode([1,1,1,4,4,4,4,5,5,5,5,6])
    print(encoded_str)
    print(decode(encoded_str))