import cv2
import numpy as np
import matplotlib.pyplot as plt

zigzag_index_inverse = [ [(0,0), (0,1), (0,5), (0,6), (1,6), (1,7), (3,3), (3,4)],
                         [(0,2), (0,4), (0,7), (1,5), (2,0), (3,2), (3,5), (5,2)],
                         [(0,3), (1,0), (1,4), (2,1), (3,1), (3,6), (5,1), (5,3)],
                         [(1,1), (1,3), (2,2), (3,0), (3,7), (5,0), (5,4), (6,5)],
                         [(1,2), (2,3), (2,7), (4,0), (4,7), (5,5), (6,4), (6,6)],
                         [(2,4), (2,6), (4,1), (4,6), (5,6), (6,3), (6,7), (7,4)],
                         [(2,5), (4,2), (4,5), (5,7), (6,2), (7,0), (7,3), (7,5)],
                         [(4,3), (4,4), (6,0), (6,1), (7,1), (7,2), (7,6), (7,7)]]

zigzag_index = [ [(0,0), (0,1), (1,0), (2,0), (1,1), (0,2), (0,3), (1,2)],
                 [(2,1), (3,0), (4,0), (3,1), (2,2), (1,3), (0,4), (0,5)],
                 [(1,4), (2,3), (3,2), (4,1), (5,0), (6,0), (5,1), (4,2)],
                 [(3,3), (2,4), (1,5), (0,6), (0,7), (1,6), (2,5), (3,4)],
                 [(4,3), (5,2), (6,1), (7,0), (7,1), (6,2), (5,3), (4,4)],
                 [(3,5), (2,6), (1,7), (2,7), (3,6), (4,5), (5,4), (6,3)],
                 [(7,2), (7,3), (6,4), (5,5), (4,6), (3,7), (4,7), (5,6)],
                 [(6,5), (7,4), (7,5), (6,6), (5,7), (6,7), (7,6), (7,7)]]

quantization_matrix = np.array([[16, 11, 10, 16, 24, 40, 51, 61],
                                [12, 12, 14, 19, 26, 58, 60, 55],
                                [14, 13, 16, 24, 40, 57, 69, 56],
                                [14, 17, 22, 29, 51, 87, 80, 62],
                                [18, 22, 37, 56, 68, 109, 103, 77],
                                [24, 35, 55, 64, 81, 104, 113, 92 ],
                                [49, 64, 78, 87, 103, 121, 120, 101],
                                [72, 92, 95,98, 112, 100, 103, 99]])

def dct2(block8x8):
    dct_zigzag = np.zeros((8,8))
    # dct
    dct = cv2.dct(cv2.dct(block8x8).T).T
    # zigzag
    for i in range(8):
        for j in range(8):
            dct_zigzag[i][j] = dct[zigzag_index[i][j][0]][zigzag_index[i][j][1]]
    # Quantization
    dct_zigzag = dct_zigzag/quantization_matrix
    return dct_zigzag

def dctYUV(y,u,v):
    dct_y_shape = y.shape
    dct_u_shape = u.shape
    dct_v_shape = v.shape
    dct_y = np.zeros(dct_y_shape)
    dct_u = np.zeros(dct_u_shape)
    dct_v = np.zeros(dct_v_shape)

    # Do 8x8 DCT on image (in-place)
    for i in np.r_[:dct_y_shape[0]:8]:
        for j in np.r_[:dct_y_shape[1]:8]:
            dct_y[i:(i + 8), j:(j + 8)] = dct2(y[i:(i + 8), j:(j + 8)])
            dct_u[i:(i + 8), j:(j + 8)] = dct2(u[i:(i + 8), j:(j + 8)])
            dct_v[i:(i + 8), j:(j + 8)] = dct2(v[i:(i + 8), j:(j + 8)])

    return dct_y, dct_u, dct_v

def sim_DCT_in():
    ####### read Image ###########
    img = cv2.imread('./in/20.jpg',1)
    # cv2.imshow('Display frame', img)
    # cv2.waitKey(0)

    ####### Convert to YUV #######
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    imf = np.float32(img_yuv)/255.0  # float conversion/scale
    y, u, v = cv2.split(imf)
    # cv2.imshow('Display frame', y.shape)
    # cv2.waitKey(0)

    ####### DCT 8x8 block #######
    dct_y, dct_u, dct_v = dctYUV(y,u,v)
    imgcv1_y = np.uint8(dct_y*255.0)    # convert back
    imgcv1_u = np.uint8(dct_u*255.0)    # convert back
    imgcv1_v = np.uint8(dct_v*255.0)    # convert back
    # imy_S = cv2.resize(imgcv1_y, (960, 540))
    # cv2.imshow('Display frame', imy_S)
    # cv2.waitKey(0)

    ####### ZIZAG ###############
    return imgcv1_y.ravel(), imgcv1_u.ravel(), imgcv1_v.ravel()
