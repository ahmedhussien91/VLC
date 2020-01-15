# Define some status global variable that is filled by other module
# count the status variable and provide statistics 
# status variables -> is Runlenght valid from mesh structure, mesh vectors, DCT blocks 

meshStruct_isRunLenghtCodingValid = True
meshVector_isRunLenghtCodingValid = True
DCT_isRunLenghtCodingValid = True

meshStruct_isRunLenghtCodingValid_Validcount = 0
meshVector_isRunLenghtCodingValid_Validcount = 0
DCT_isRunLenghtCodingValid_Validcount = 0

DCT_Total_Count = 0
mesh_Total_Count = 0

def DoStatistics_mesh():
    global mesh_Total_Count, meshStruct_isRunLenghtCodingValid, meshStruct_isRunLenghtCodingValid_Validcount
    global meshVector_isRunLenghtCodingValid, meshVector_isRunLenghtCodingValid_Validcount  
    
    # count the total mesh cycles
    mesh_Total_Count = mesh_Total_Count + 1
    # count the cycles inwhich the runlenght was executed 
    if (meshStruct_isRunLenghtCodingValid):
       meshStruct_isRunLenghtCodingValid_Validcount = meshStruct_isRunLenghtCodingValid_Validcount + 1
    if (meshVector_isRunLenghtCodingValid):
       meshVector_isRunLenghtCodingValid_Validcount = meshVector_isRunLenghtCodingValid_Validcount + 1     

    return

def DoStatistics_DCT():
    global DCT_Total_Count, DCT_isRunLenghtCodingValid, DCT_isRunLenghtCodingValid_Validcount 
    
    # count the total mesh cycles
    DCT_Total_Count = DCT_Total_Count + 1
    # count the cycles inwhich the runlenght was executed 
    if (DCT_isRunLenghtCodingValid):
       DCT_isRunLenghtCodingValid_Validcount = DCT_isRunLenghtCodingValid_Validcount + 1   

    return