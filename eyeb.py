import cv2
import numpy
import dlib
import time
from pylab import *
from scipy.interpolate import interp1d
from skimage.filters import gaussian
from skimage import color
import sys
import matplotlib.pyplot as plt

PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
SCALE_FACTOR = 1 
FEATHER_AMOUNT = 11

FACE_POINTS = list(range(17, 68))
MOUTH_POINTS = list(range(48, 61))
RIGHT_BROW_POINTS = list(range(17, 22))
LEFT_BROW_POINTS = list(range(22, 27))
RIGHT_EYE_POINTS = list(range(36, 42))
LEFT_EYE_POINTS = list(range(42, 48))
NOSE_POINTS = list(range(27, 35))
JAW_POINTS = list(range(0, 17))

ALIGN_POINTS = ( FACE_POINTS)

OVERLAY_POINTS = [ RIGHT_BROW_POINTS, LEFT_BROW_POINTS ]
r,g,b = 0,0,0
def eyeb(filename):
    img = filename
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def get_landmark(img):
        detector = dlib.get_frontal_face_detector() #Load face detector
        predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        landmark_point = []

        for face in faces:
            landmarks = predictor(gray, face) 
            for n in range(0,68):
                x = landmarks.part(n).x
                y = landmarks.part(n).y 
                landmark_point.append((int(x),y)) 
            for n in landmark_point:
                x=n[0]
                y = (n[1])  
        
        landmark_point = np.array(landmark_point)
        return landmark_point
        # print(landmark_point[0], landmark_point[1])
    def draw_convex_hull(im, points, color):
        points = cv2.convexHull(points)
        #cv2.fillConvexPoly(im, points, color=color)
        return points

    a = get_landmark(img) 

    a = a.reshape((-1,1,2))

    mask = np.zeros_like(img)

    for i in range (mask.shape[0]):
        for j in range (mask.shape[1]):
                mask[i,j] = [100,100,100]

    for i in OVERLAY_POINTS:
        draw_convex_hull(img,
                            a[i],
                            color=1)
        cv2.fillConvexPoly(mask, a[i], color = (r,g,b))


    # cv2.imshow('im', img)
    # cv2.imshow("img",mask)

    alpha = 0.8
    beta = 1 - alpha

    imgMask = cv2.GaussianBlur(mask, (15, 15), 0)

    dstf = (imgMask * mask + (1 - imgMask) * mask).astype('uint8')

    dst = cv2.addWeighted(img, alpha , imgMask, beta , 0.0)
    return dst
    # cv2.imshow("img2",dst)

    # cv2.waitKey(0)
    # cv2.destroyAllWindows
