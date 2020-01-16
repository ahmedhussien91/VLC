
FILE_NAME = "test.bnr"
DataCount = 0

def write_to_binaryFile(bin_array):
    global DataCount
    if DataCount == 0:
        with open(FILE_NAME, "wb") as f:
            f.write(bin_array)
    else:
        with open(FILE_NAME, "ab") as f:
            f.write(bin_array)
    return

def read_from_binaryFile():
    with open(FILE_NAME, "rb") as f:
        data = f.read()

    return data


if __name__ == "__main__":   
    write_to_binaryFile("000011111000000100010")
    data = read_from_binaryFile()
    print(data[1:16])
    print(int(data[1:16],2))