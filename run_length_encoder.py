import configuration as cfg

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
def encode_meshStruct(data_np_arr): 
    encoded_meshStruct = encode(list(data_np_arr))
    meshStructSize = len(encoded_meshStruct)
    return encoded_meshStruct, meshStructSize


def encode_meshVectors(data_np_arr): 
    encoded_meshVector = encode(list(data_np_arr))
    meshVectorSize = len(encoded_meshVector)
    return encoded_meshVector, meshVectorSize


def encode_dct(data_np_arr_list):
    encoded_dct = []
    dctSize = []
    for i,data_np_arr in enumerate(data_np_arr_list):
        encoded_dct.append(encode(list(data_np_arr)))
        dctSize.append(len(encoded_dct[i])) 
    return encoded_dct, dctSize


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