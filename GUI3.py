from tkinter import *
from pylab import arange
from pylab import ones
from pylab import mean
from pylab import gca
from pylab import zeros
from PIL import Image, ImageTk
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
import dlib
import time
from functools import partial
from scipy.interpolate import interp1d
from skimage import color
import sys
import imutils
import apply_makeupCode
import os


class GUI3():
    def __init__(self,gui3):
        self.gui3 = gui3
        self.background_image = ImageTk.PhotoImage(Image.open("./demo.png"))
        self.background = Label(self.gui3, image=self.background_image)
        self.background.pack(fill='both', expand=True)
        self.background.image = self.background_image 
        self.background.bind('<Configure>', self._resize_image)
        self.show()
    def close(self):
        self.gui3.destroy()
    def show(self):
        title = tk.Label(self.background, text = 'Đồ án Nhập môn thị giác máy tính '
                                ,bg = 'lightskyblue1', font = ("Times New Roman", 15))
        title.pack(padx=10, pady=5)

        t0 = tk.Label(self.background, text = 'DIGITAL FACE MAKEUP '
                                ,bg = 'lightskyblue1', fg = 'firebrick1', font = ("Times New Roman", 24, "bold"))
        t0.pack(padx=10, pady=5) 

        T2 = tk.Label(self.background, text = 'GVHD: TS. Nguyễn Vinh Tiệp'
                                ,bg = 'lightskyblue1', font = ("Times New Roman", 16, "bold"))
        T2.pack(padx=10, pady=5)


        T = tk.Label(self.background, text = 'Nhóm thực hiện:\n Đặng Quốc Quy  MSSV: 17520960 \n Trần Vũ Hoàng Tú  MSSV: 17521209 \n Đặng Hoàng Sang  MSSV: 17520967'
                                ,bg = 'lightskyblue1', font = ("Times New Roman", 15, "bold"))
        T.pack(padx=10, pady=5)
        
        b = tk.Button(self.background, text = 'Close' ,bg = 'burlywood1', font = ("Times New Roman", 13), command = self.close)
        b.pack( padx=10, pady=15 )
    def _resize_image(self,event):

        new_width = event.width
        new_height = event.height

        self.background_image = Image.open("./demo.png").resize((new_width, new_height))

        self.background_image = ImageTk.PhotoImage(self.background_image)
        self.background.configure(image =  self.background_image)


# if __name__ == "__main__":
#     # gui1 = tk.Tk()
#     gui3 = Tk() # create gui1 window
#     gui3.title("Team Information")
#     gui3.minsize(600, 400) # width x height
#     main = GUI3(gui3)
#     #main.create_left_right_frames()
#     gui3.config(bg="lightskyblue1")
#     gui3.mainloop()


