import configuration as cfg
import statistics_module as stat

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
    mapping = list()

    for character in text:
        if character != previous:
            if previous != None:
                mapping.append((previous, count))
            count = 1
            previous = character
        else:
            count += 1
    else:
        mapping.append((character, count))

    result = []

    for character, count in mapping:
            result.append(str(count))
            result.append(str(character))

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
            is_run_length_valid[i] = False
            encoded_meshStruct[i] = data_np_arr
            stat.meshStruct_isRunLenghtCodingValid_InValidcount = stat.meshStruct_isRunLenghtCodingValid_InValidcount + 1
        else:
            stat.meshStruct_isRunLenghtCodingValid_Validcount = stat.meshStruct_isRunLenghtCodingValid_Validcount + 1
    return encoded_meshStruct, is_run_length_valid


def encode_meshVectors(data_np_arr_list):
    encoded_meshVector = []
    is_run_length_valid = []
    for i,data_np_arr in enumerate(data_np_arr_list): 
        encoded_meshVector.append(encode(list(data_np_arr)))
    # check that the runlength coding valid for each data block
    for i, data_np_arr in enumerate(data_np_arr_list):
        if len(data_np_arr) < len(encoded_meshVector[i]):
            is_run_length_valid[i] = False
            encoded_meshVector[i] = data_np_arr
            stat.meshVector_isRunLenghtCodingValid_InValidcount = stat.meshVector_isRunLenghtCodingValid_InValidcount + 1
        else:
            stat.meshVector_isRunLenghtCodingValid_Validcount = stat.meshVector_isRunLenghtCodingValid_Validcount + 1
    return encoded_meshVector, is_run_length_valid


def encode_dct(data_np_arr_list):
    encoded_dct = []
    is_run_length_valid = []
    for i,data_np_arr in enumerate(data_np_arr_list):
        encoded_dct.append(encode(list(data_np_arr))) 
    # check that the runlength coding valid for each data block
    for i, data_np_arr in enumerate(data_np_arr_list):
        if len(data_np_arr) < len(encoded_dct[i]):
            is_run_length_valid[i] = False
            encoded_dct[i] = data_np_arr
            stat.DCT_isRunLenghtCodingValid_InValidcount = stat.DCT_isRunLenghtCodingValid_InValidcount + 1
        else:
            stat.DCT_isRunLenghtCodingValid_Validcount = stat.DCT_isRunLenghtCodingValid_Validcount + 1
    return encoded_dct


######################################### Decoder ###################################################################
def decode_meshStruct(): 

    return decoded_meshStruct, meshStructSize


def decode_meshVectors(): 

    return decoded_meshVectors, meshVectorsSize 


def decode_dct(): 

    return encoded_dct, dctSize 

if __name__ == "__main__":
        
    encoded_str = encode("aaabbcdddd")
    print(encoded_str)
    print(decode(encoded_str))