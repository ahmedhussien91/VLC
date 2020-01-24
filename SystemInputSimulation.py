import cv2
import numpy as np
import matplotlib.pyplot as plt

def dct2(block8x8):
    dct = cv2.dct(cv2.dct(block8x8).T).T
    return dct

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

####### read Image ###########
img = cv2.imread('./in/20.jpg')
cv2.imshow('img_yuv', img)
####### Convert to YUV #######
img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
imf = np.float32(img_yuv)/255.0  # float conversion/scale
y, u, v = cv2.split(imf)
cv2.imshow('img_yuv', y)

####### DCT 8x8 block #######
dct_y, dct_u, dct_v = dctYUV(y,u,v)
imgcv1_y = np.uint8(dct_y*255.0)    # convert back
imgcv1_u = np.uint8(dct_u*255.0)    # convert back
imgcv1_v = np.uint8(dct_v*255.0)    # convert back
cv2.imshow('y', imgcv1_y)
print()