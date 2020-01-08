import itertools
import scipy.interpolate
import cv2
import numpy as np
from skimage import color
import os.path
import sys
import dlib
import time
from timeit import default_timer as timer
import keras
PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"

class ApplyMakeup():

    def __init__(self):
        self.predictor = dlib.shape_predictor(PREDICTOR_PATH)
        self.detector = dlib.get_frontal_face_detector()
        self.model = keras.models.load_model('hairnet_matting.hdf5', compile=False)
        self.red_l = 0
        self.green_l = 0
        self.blue_l = 0
        self.red_e = 0
        self.green_e = 0
        self.blue_e = 0
        self.red_h = 0
        self.green_h = 0
        self.blue_h = 0
        self.red_eb = 0
        self.green_eb = 0
        self.blue_eb = 0
        self.debug = 0
        self.countFace = 0
        self.image = 0
        self.width = 0
        self.height = 0
        self.im_copy = 0
        self.lip_x = []
        self.lip_y = []
    
    def __read_image(self, filename):
        self.image = filename
        self.image = cv2.cvtColor(self.image , cv2.COLOR_BGR2RGB)
        self.im_copy = self.image.copy()
        self.height, self.width = self.image.shape[:2]
        self.debug = 0
    
    def get_lips_and_eyes(self):
        try:
            image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
            rects = self.detector(image, 0)
            size = len(rects)
            if size == 0:
                return None,None,None
                
            landmark_point = []
            landmark_point_eye_left = []
            landmark_point_eyeb_left = []
            landmark_point_eye_right = []
            landmark_point_eyeb_right = []
            for rect in rects:
                landmarks = self.predictor(image, rect)
                temp_point = []
                temp_point1 = []
                for n in range(48, 68):
                    x = landmarks.part(n).x
                    y = landmarks.part(n).y
                    temp_point.append((x,y))
                landmark_point.append(np.array(temp_point))

                for n in range(36, 40):
                    x = landmarks.part(n).x
                    y = landmarks.part(n).y
                    temp_point1.append((x,y))
                landmark_point_eye_left.append(np.array(temp_point1))
                temp_point1 = []
                for n in range(42, 46):
                    x = landmarks.part(n).x
                    y = landmarks.part(n).y
                    temp_point1.append((x,y))
                landmark_point_eye_right.append(np.array(temp_point1))

                temp_point1 = []
                for n in range(17, 22):
                    x = landmarks.part(n).x
                    y = landmarks.part(n).y
                    temp_point1.append((x,y))
                landmark_point_eyeb_right.append(np.array(temp_point1))

                temp_point1 = []
                for n in range(22, 27):
                    x = landmarks.part(n).x
                    y = landmarks.part(n).y
                    temp_point1.append((x,y))
                landmark_point_eyeb_left.append(np.array(temp_point1))

            landmark_point = np.array(landmark_point)
            landmark_point_eye_left = np.array(landmark_point_eye_left)
            landmark_point_eye_right = np.array(landmark_point_eye_right)
            landmark_point_eyeb_left = np.array(landmark_point_eyeb_left)
            landmark_point_eyeb_right = np.array(landmark_point_eyeb_right)
            return landmark_point, landmark_point_eye_left, landmark_point_eye_right, landmark_point_eyeb_left, landmark_point_eyeb_right                   
        except Exception:
            return None,None,None

    
    def __draw_curve(self, points):
        """ Draws a curve alone the given points by creating an interpolated path. """
        x_pts = []
        y_pts = []
        curvex = []
        curvey = []
        self.debug += 1
        x_pts = points[:,0]
        y_pts = points[:,1]
        try:
            curve = scipy.interpolate.interp1d(x_pts, y_pts, 'cubic')
        except:
            return False
        if self.debug == 1 or self.debug == 2:
            for i in np.arange(x_pts[0], x_pts[len(x_pts) - 1] + 1, 1):
                curvex.append(i)
                curvey.append(int(curve(i)))
        else:
            for i in np.arange(x_pts[len(x_pts) - 1] + 1, x_pts[0], 1):
                curvex.append(i)
                curvey.append(int(curve(i)))
        return curvex, curvey

    
    def __fill_lip_lines(self, outer, inner):
        """ Fills the outlines of a lip with colour. """
        outer_curve = zip(outer[0], outer[1])
        inner_curve = zip(inner[0], inner[1])
        count = len(inner[0]) - 1
        try:
            last_inner = [inner[0][count], inner[1][count]]
        except:
            return False
        for o_point, i_point in itertools.zip_longest(
                outer_curve, inner_curve, fillvalue=last_inner
            ):
            line = scipy.interpolate.interp1d(
                [o_point[0], i_point[0]], [o_point[1], i_point[1]], 'linear')
            xpoints = list(np.arange(o_point[0], i_point[0], 1))
            self.lip_x.extend(xpoints)
            self.lip_y.extend([int(point) for point in line(xpoints)])

    
    def __fill_lip_solid(self, outer, inner):
        """ Fills solid colour inside two outlines. """
        inner[0].reverse()
        inner[1].reverse()
        outer_curve = zip(outer[0], outer[1])
        inner_curve = zip(inner[0], inner[1])
        points = []
        for point in outer_curve:
            points.append(np.array(point, dtype=np.int32))
        for point in inner_curve:
            points.append(np.array(point, dtype=np.int32))
        points = np.array(points, dtype=np.int32)
        self.red_l = int(self.red_l)
        self.green_l = int(self.green_l)
        self.blue_l = int(self.blue_l)
        cv2.fillPoly(self.image, [points], (self.red_l, self.green_l, self.blue_l))

    
    def __smoothen_color(self, outer, inner):
        """ Smoothens and blends colour applied between a set of outlines. """
        outer_curve = zip(outer[0], outer[1])
        inner_curve = zip(inner[0], inner[1])
        x_points = []
        y_points = []
        for point in outer_curve:
            x_points.append(point[0])
            y_points.append(point[1])
        for point in inner_curve:
            x_points.append(point[0])
            y_points.append(point[1])
        img_base = np.zeros((self.height, self.width))
        cv2.fillConvexPoly(img_base, np.array(np.c_[x_points, y_points], dtype='int32'), 1)
        img_mask = cv2.GaussianBlur(img_base, (61, 61), 0)
        img_blur_3d = np.ndarray([self.height, self.width, 3], dtype='float')
        img_blur_3d[:, :, 0] = img_mask
        img_blur_3d[:, :, 1] = img_mask
        img_blur_3d[:, :, 2] = img_mask
        if self.countFace == 1:
            self.im_copy = (img_blur_3d * self.image + (1 - img_blur_3d) * self.im_copy).astype('uint8')
        else:
            self.im_copy = (img_blur_3d * cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR) + (1 - img_blur_3d) * self.im_copy).astype('uint8')

    
    def __add_color(self, intensity):
        """ Adds base colour to all points on lips, at mentioned intensity. """
        val = color.rgb2lab(
            (self.image[self.lip_y, self.lip_x] / 255.)
            .reshape(len(self.lip_y), 1, 3)
        ).reshape(len(self.lip_y), 3)
        l_val, a_val, b_val = np.mean(val[:, 0]), np.mean(val[:, 1]), np.mean(val[:, 2])
        l1_val, a1_val, b1_val = color.rgb2lab(
            np.array(
                (self.red_l / 255., self.green_l / 255., self.blue_l / 255.)
                ).reshape(1, 1, 3)
            ).reshape(3,)
        l_final, a_final, b_final = (l1_val - l_val) * \
            intensity, (a1_val - a_val) * \
            intensity, (b1_val - b_val) * intensity
        val[:, 0] = np.clip(val[:, 0] + l_final, 0, 100)
        val[:, 1] = np.clip(val[:, 1] + a_final, -127, 128)
        val[:, 2] = np.clip(val[:, 2] + b_final, -127, 128)
        self.image[self.lip_y, self.lip_x] = color.lab2rgb(val.reshape(
            len(self.lip_y), 1, 3)).reshape(len(self.lip_y), 3) * 255

    
    def __get_points_lips(self, lips_points):
        """ Get the points for the lips. """
        uol = []
        uil = []
        lol = []
        lil = []
        uol = lips_points[:7]
        lol = np.append(lips_points[6:12],[lips_points[0]],0)
        uil = lips_points[12:17]
        lil = np.append(lips_points[16:20],[lips_points[12]],0)
        uol_curve = self.__draw_curve(uol)
        uil_curve = self.__draw_curve(uil)
        lol_curve = self.__draw_curve(lol)
        lil_curve = self.__draw_curve(lil)
        return uol_curve, uil_curve, lol_curve, lil_curve

    
    def __fill_color(self, uol_c, uil_c, lol_c, lil_c):
        """ Fill colour in lips. """
        if self.__fill_lip_lines(uol_c, uil_c) == False or \
        self.__fill_lip_lines(lol_c, lil_c) == False:
            return False
        self.__add_color(0.5)
        self.__fill_lip_solid(uol_c, uil_c)
        self.__fill_lip_solid(lol_c, lil_c)
        
        self.__smoothen_color(uol_c, uil_c) #môi trên
        self.__smoothen_color(lol_c, lil_c) #môi dưới
    
    def __draw_liner(self, eye, kind):
        """ Draws eyeliner. """
        eye_x = []
        eye_y = []
        x_points = eye[:,0]
        y_points = eye[:,1]
        try:
            curve = scipy.interpolate.interp1d(x_points, y_points, 'quadratic')
        except:
            return False
        for point in np.arange(x_points[0], x_points[len(x_points) - 1] + 1, 1):
            eye_x.append(point)
            eye_y.append(int(curve(point)))
        if kind == 'left':
            y_points[0] -= 1
            y_points[1] -= 1
            y_points[2] -= 1
            x_points[0] -= 5
            x_points[1] -= 1
            x_points[2] -= 1
            curve = scipy.interpolate.interp1d(x_points, y_points, 'quadratic')
            count = 0
            for point in np.arange(x_points[len(x_points) - 1], x_points[0], -1):
                count += 1
                eye_x.append(point)
                if count < (len(x_points) / 2):
                    eye_y.append(int(curve(point)))             #eye_y: độ rộng
                elif count < (2 * len(x_points) / 3):
                    eye_y.append(int(curve(point)) - 1)
                elif count < (4 * len(x_points) / 5):
                    eye_y.append(int(curve(point)) - 1.5)
                elif count:
                    eye_y.append(int(curve(point)) - 2)
        elif kind == 'right':
            x_points[3] += 5
            x_points[2] += 1
            x_points[1] += 1
            y_points[3] -= 1
            y_points[2] -= 1
            y_points[1] -= 1
            curve = scipy.interpolate.interp1d(x_points, y_points, 'quadratic')
            count = 0
            for point in np.arange(x_points[len(x_points) - 1], x_points[0], -1):
                count += 1
                eye_x.append(point)
                if count < (len(x_points) / 2):
                    eye_y.append(int(curve(point)))
                elif count < (2 * len(x_points) / 3):
                    eye_y.append(int(curve(point)) - 1)
                elif count < (4 * len(x_points) / 5):
                    eye_y.append(int(curve(point)) - 1.5)
                elif count:
                    eye_y.append(int(curve(point)) - 2)
        curve = zip(eye_x, eye_y)
        points = []
        for point in curve:
            points.append(np.array(point, dtype=np.int32))
        points = np.array(points, dtype=np.int32)
        self.red_e = int(self.red_e)
        self.green_e = int(self.green_e)
        self.blue_e = int(self.blue_e)
        cv2.fillPoly(self.im_copy, [points], (self.red_e, self.green_e, self.blue_e))

    
    
    def apply_lipstick(self, filename):
        
        self.__read_image(filename)
        lips,_,_,_,_ = self.get_lips_and_eyes()
        if type(lips) == np.ndarray:
            dem = 0
            for lip in lips:
                dem += 1
                self.countFace = dem
                uol, uil, lol, lil = self.__get_points_lips(lip)
                if uol== False or uil== False or lol== False or lil== False:
                    continue
                if self.__fill_color(uol, uil, lol, lil) == False:
                    continue
                if dem == 1:
                    self.im_copy = cv2.cvtColor(self.im_copy, cv2.COLOR_RGB2BGR)
                self.debug = 0
            return self.im_copy
        else:
            return self.im_copy

    
    def apply_liner(self, filename):
        
        self.__read_image(filename)
        _,eye_left,eye_right,_,_ = self.get_lips_and_eyes()
        if type(eye_left) == np.ndarray and type(eye_right) == np.ndarray:
            dem = 0
            for ia,eye_l in enumerate(eye_left):
                dem += 1
                if self.__draw_liner(eye_l, 'left') == False \
                or self.__draw_liner(eye_right[ia], 'right') == False:
                    continue
                if dem == 1:
                    self.im_copy = cv2.cvtColor(self.im_copy, cv2.COLOR_RGB2BGR)
            return self.im_copy
        else:
            return self.im_copy


    def hair(self,filename):
        self.__read_image(filename)
        im = self.image / 255
        im = cv2.resize(im, (224, 224))
        im = im.reshape((1,) + im.shape)   
        pred = self.model.predict(im)  
        mask = pred.reshape((224, 224))
        mask[mask > 0.5] = 255
        mask[mask <= 0.5] = 0
        mask = cv2.resize(mask, (self.width, self.height))
        mask_n = np.zeros_like(self.image)
        mask_n[:, :, 2] = mask
        for i in range (mask_n.shape[0]):
            for j in range (mask_n.shape[1]):
                if ( mask_n[i, j, 2] != 0):
                    mask_n[i,j] = [self.blue_h,self.green_h,self.red_h]
                else:
                    mask_n[i,j] = [80,80,80]
        alpha = 0.85
        beta = (1.0 - alpha)
        dst = cv2.addWeighted(self.image, alpha, mask_n, beta, 0.0)
        dst = cv2.bilateralFilter(dst, 7,20,20)
        dst = cv2.cvtColor(dst,cv2.COLOR_BGR2RGB)
        return dst

    def eyeb(self, filename):
        self.__read_image(filename)
        _,_,_,left,right = self.get_lips_and_eyes()
        for ia in range(len(left)):
            point_l = cv2.convexHull(left[ia])
            point_r = cv2.convexHull(right[ia])
            self.mask = np.zeros_like(self.image)
            cv2.fillConvexPoly(self.mask, point_l, color = (self.red_eb,self.green_eb,self.blue_eb))
            cv2.fillConvexPoly(self.mask, point_r, color = (self.red_eb,self.green_eb,self.blue_eb))
            alpha = 0.8
            beta = 1 - alpha
            imgMask = cv2.GaussianBlur(self.mask, (15, 15), 0)
            dstf = (imgMask * self.mask + (1 - imgMask) * self.mask).astype('uint8')
            dst = cv2.addWeighted(self.image, alpha , imgMask, beta , 0.0)
            dst = cv2.cvtColor(dst,cv2.COLOR_BGR2RGB)
            return dst


        