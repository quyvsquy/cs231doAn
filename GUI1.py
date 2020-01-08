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
from tkinter import messagebox
from numba import jit
import dlib
import time
from functools import partial
from scipy.interpolate import interp1d
from skimage import color
import sys
import imutils
import apply_makeupCode

class GUI1():
    def __init__(self, gui1):
        self.gui1 = gui1
        self.background_image = ImageTk.PhotoImage(Image.open("./background.png"))
        self.background = Label(self.gui1, image=self.background_image)
        self.background.pack(fill='both', expand=True)
        self.background.image = self.background_image 
        self.background.bind('<Configure>', self._resize_image)

        self.left_frame = 0
        self.right_frame = 0
        self.img = 0
        self.imgTk = 0
        self.imgScale = 0
        self.makeUp = apply_makeupCode.ApplyMakeup()
        self.makeUp.red_l  =  0
        self.makeUp.green_l = 0
        self.makeUp.blue_l =  0
        self.makeUp.red_e =   0
        self.makeUp.green_e = 0
        self.makeUp.blue_e =  0
        self.imgTempLuu = 0
        self.checkLoaded = False

    def create_left_right_frames(self):
        self.left_frame = Frame(self.background)
        self.left_frame.grid(row=0, column=0, padx=10, pady=5, sticky='w'+'e'+'n'+'s')
        
        self.right_frame = Frame(self.background)
        self.right_frame.grid(row=0, column=1, padx=10, pady=5, sticky='w'+'e'+'n'+'s')

        Grid.columnconfigure(self.left_frame,0, weight = 1)
        Grid.rowconfigure(self.left_frame,0, weight = 1)

        Grid.columnconfigure(self.right_frame,0, weight = 1)
        Grid.rowconfigure(self.right_frame,0, weight = 1)

        Button(self.right_frame, text="Load Image", command = self.loadFile).grid(row=1, column=0, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        btnClose = Button(self.right_frame, text="Close", bg = 'tan1', command= self.close)
        btnClose.grid(row=1, column = 1, padx=5, pady=5, sticky='w'+'e'+'n'+'s') 
          	

    def loadFile(self):
        self.gui1.filename =  filedialog.askopenfilename(initialdir = "./",title = "Select file",\
            filetypes = (("jpg files","*.jpg"),("all files","*.*")))
        if self.gui1.filename != "" and type(self.gui1.filename) == str:
            self.img = cv2.imread(self.gui1.filename)
            print("(height,width)= ({},{})".format(self.img.shape[0],self.img.shape[1]))
            image = cv2.resize(self.img, (60,80), interpolation = cv2.INTER_AREA)
            dim,width,height = 0,0,0
            
            for ia in range(100,0,-1):
                width = int(self.img.shape[1] * ia / 100)
                if width >1024: 
                    continue
                height = int(self.img.shape[0] * ia / 100)
                if height > 720:
                    continue
                dim = (width, height) 
                if ia != 100:
                    print("scaled_(height,width)= ({},{})".format(height,width))
                break
            self.img = cv2.resize(self.img,dim, interpolation = cv2.INTER_AREA)
            b,g,r = cv2.split(self.img)
            imgg = cv2.merge((r,g,b))

            b1,g1,r1 = cv2.split(image)
            image = cv2.merge((r1,g1,b1))

            im = Image.fromarray(imgg)
            self.imgTk = ImageTk.PhotoImage(image=im)

            im2 = Image.fromarray(image)
            self.imgScale = ImageTk.PhotoImage(image=im2)

            # self.left_frame.grid_forget()
            self.left_frame.destroy()
            self.left_frame = Frame(self.background, width=width, height= height)
            self.left_frame.grid(row=0, column=0, padx=10, pady=5)

            Label(self.left_frame, image = self.imgTk).grid(row=0, column=0, padx=0, pady=0,sticky='w'+'e'+'n'+'s')
            Label(self.right_frame, image=self.imgScale).grid(row=0, column=0, padx=0, pady=0, sticky='w'+'e'+'n'+'s')
            self.showBotton()

    def show(self,r,g,b,kind):
        self.makeUp.red_l  = r
        self.makeUp.green_l = g
        self.makeUp.blue_l = b
        self.makeUp.red_e = r
        self.makeUp.green_e = g
        self.makeUp.blue_e = b
        self.makeUp.red_h = r
        self.makeUp.green_h = g
        self.makeUp.blue_h = b
        self.makeUp.red_eb = r
        self.makeUp.green_eb = g
        self.makeUp.blue_eb = b
        if kind == 0: #lip
            start = time.time()
            img_proced = self.makeUp.apply_lipstick(self.img)
            print("Execution time",(time.time() - start)*1000)
        elif kind == 1: #eye
            start = time.time()
            img_proced = self.makeUp.apply_liner(self.img)
            print("Execution time",(time.time() - start)*1000)
        elif kind == 2: #hair
            start = time.time()
            img_proced = self.makeUp.hair(self.img)
            print("Execution time",(time.time() - start)*1000)
        elif kind == 3: #eyeb
            start = time.time()
            img_proced = self.makeUp.eyeb(self.img)
            print("Execution time",(time.time() - start)*1000)
        else:
            start = time.time()
            img_proced = self.img
            print("Execution time",(time.time() - start)*1000)

        self.imgTempLuu = img_proced

        b3,g3,r3 = cv2.split(img_proced)
        im2 = cv2.merge((r3,g3,b3))
        temp = Image.fromarray(im2)
        self.imgTk = ImageTk.PhotoImage(image = temp)
        Label(self.left_frame, image = self.imgTk).grid(row=0, column=0, padx=0, pady=0)

    def doned(self):
        self.img = self.imgTempLuu
    def clicked(self):
        print("Clicked.")
    def close(self): 
        self.checkLoaded = True
        self.gui1.destroy()

    def showBotton(self):
        tool_bar = Frame(self.right_frame, width=180, height=185)
        tool_bar.grid(row=3, column=0, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Grid.columnconfigure(tool_bar,0, weight = 1)
        Grid.rowconfigure(tool_bar,0, weight = 1)
        Label(tool_bar, text="Lip", relief=RAISED,  bg = "cyan2").grid(row=0, column=0, padx=5, pady=3, ipadx=10)
        Label(tool_bar, text="EyeLiner", relief=RAISED, bg = "khaki").grid(row=0, column=1, padx=5, pady=3, ipadx=10)
        Label(tool_bar, text="Hair", relief=RAISED, bg = "slateGray1").grid(row=0, column=2, padx=5, pady=3, ipadx=10)
        Label(tool_bar, text="EyeBrow", relief=RAISED, bg = "coral1").grid(row=0, column=3, padx=5, pady=3, ipadx=10)
        # lip color button
        Button(tool_bar, text="", bg = '#A00A14', command = partial(self.show, 160,10,20,0)).grid(row=1, column=0, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(tool_bar, text="", bg = '#FF69F1', command= partial(self.show, 255,100,240,0)).grid(row=2, column=0, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(tool_bar, text="", bg = '#CC6600', command= partial(self.show, 204,102,0,0)).grid(row=3, column=0, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(tool_bar, text="", bg = '#A717B2', command= partial(self.show, 167,23,178,0)).grid(row=4, column=0, padx=5, pady=5, sticky='w'+'e'+'n'+'s')

        # eyeliner       
        Button(tool_bar, text="", bg = '#000000', command = partial(self.show, 0,0,0 ,1)).grid(row=1, column=1, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(tool_bar, text="", bg = '#663300', command=  partial(self.show, 102,51,0,1)).grid(row=2, column=1, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(tool_bar, text="", bg = '#5CBF38', command=  partial(self.show, 92,190,56  ,1)).grid(row=3, column=1, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(tool_bar, text="", bg = '#A717B2', command=  partial(self.show, 167,23,178 ,1)).grid(row=4, column=1, padx=5, pady=5, sticky='w'+'e'+'n'+'s')

		# hair
        Button(tool_bar, text="", bg = '#A00A14', command= partial(self.show, 0,0,0 ,2)).grid(row=1, column=2, padx=5, pady=5, sticky='w'+'e'+'n'+'s')        
        Button(tool_bar, text="", bg = '#FF69F1', command=partial(self.show, 255,100,240,2)).grid(row=2, column=2, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(tool_bar, text="", bg = '#5CBF38', command=partial(self.show, 92,190,56  ,2)).grid(row=3, column=2, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(tool_bar, text="", bg = '#A717B2',command=partial(self.show, 167,23,178 ,2)).grid(row=4, column=2, padx=5, pady=5, sticky='w'+'e'+'n'+'s')

        # eyebrow color button
        Button(tool_bar, text="", bg = '#A00A14', command =partial(self.show, 0,0,0 ,3) ).grid(row=1, column=3, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(tool_bar, text="", bg = '#FF69F1', command= partial(self.show, 255,100,240,3) ).grid(row=2, column=3, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(tool_bar, text="", bg = '#5CBF38', command= partial(self.show, 92,190,56  ,3)).grid(row=3, column=3, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(tool_bar, text="", bg = '#A717B2', command= partial(self.show, 167,23,178 ,3) ).grid(row=4, column=3, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
       

        Button(self.right_frame, text="DONE", command= self.doned).grid(row=5, column = 0, padx=5, pady=5, sticky='w'+'e'+'n'+'s') 
        # Button(tool_bar, text="done2", command= self.clicked).grid(row=5, column = 1, padx=5, pady=5, sticky='w'+'e'+'n'+'s') 
        # Button(tool_bar, text="done3", command= self.clicked).grid(row=5, column = 2, padx=5, pady=5, sticky='w'+'e'+'n'+'s') 
        # Button(tool_bar, text="done4", command= self.clicked).grid(row=5, column = 3, padx=5, pady=5, sticky='w'+'e'+'n'+'s') 

    def _resize_image(self,event):

        new_width = event.width
        new_height = event.height

        self.background_image = Image.open("./background.png").resize((new_width, new_height))

        self.background_image = ImageTk.PhotoImage(self.background_image)
        self.background.configure(image =  self.background_image)

