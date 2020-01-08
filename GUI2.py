from tkinter import *
from pylab import arange,ones,mean,gca,zeros
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
# from imutils.video import VideoStream


class GUI2():
    def __init__(self, gui2):
        self.gui2 = gui2
        self.makeUp = apply_makeupCode.ApplyMakeup()
        self.background_image = ImageTk.PhotoImage(Image.open("./background.png"))
        self.background = Label(self.gui2, image=self.background_image)
        self.background.pack(fill='both', expand=True)
        self.background.image = self.background_image 
        self.background.bind('<Configure>', self._resize_image)
        self.app = 0
        self.app2 = 0
        self.cap = cv2.VideoCapture(0)
        self.imgTempLuu = 0
        self.tool_bar = 0
        self.makeUp.red_l  =  0
        self.makeUp.green_l = 0
        self.makeUp.blue_l =  0
        self.makeUp.red_e =   0
        self.makeUp.green_e = 0
        self.makeUp.blue_e =  0
        self.kind = -1
        self.checkLoaded = False
        self.storeColor = [[0,0,0],[0,0,0]]
        self.checkDoned =False
    def create_Screen(self):
        self.app = Frame(self.background, width=200, height= 400, bg="white")
        self.app.grid(row=0, column=0, padx=10, pady=5)
        self.app2 = Frame(self.background, width=200, height= 400, bg="gray")
        self.app2.grid(row=0, column=1, padx=10, pady=5)

        self.lmain = Label(self.app)
        self.lmain.grid(row=0, column=0, padx=10, pady=5)

        self.tool_bar = Frame(self.app2, width=180, height=185, bg='grey')
        self.tool_bar.grid(row=0, column=1, padx=5, pady=5)
        self.btnStart = Button(self.tool_bar, text="Start", bg = 'tan1',command= self.video_stream)
        self.btnStart.grid(row=0, column = 0, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(self.tool_bar, text="Close", bg = 'tan1', command= self.close).grid(row=0, column = 1, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        # self.checkLoaded = True


    def clicked(self):
        print("Clicked.")

    # function for video streaming
    def video_stream(self):
        # while True:
        # self.frame = self.cap.read()
        # self.frame = imutils.resize(self.frame, width=450)
        _, self.frame = self.cap.read()
        self.frame = cv2.flip(self.frame, 1)
        self.frame = imutils.resize(self.frame, width=450)
        if self.kind == 0: #lip
            img_proced = self.makeUp.apply_lipstick(self.frame)
            if self.checkDoned:
                img_proced = self.makeUp.apply_liner(img_proced)


        elif self.kind == 1: #eye
            if self.checkDoned:
                img_proced = self.makeUp.apply_lipstick(self.frame)
                img_proced = self.makeUp.apply_liner(img_proced)
            else:
                img_proced = self.makeUp.apply_liner(self.frame)
        else:
            img_proced = self.frame
            
        self.imgTempLuu = img_proced   
        self.storeColor[0][0],self.storeColor[0][1],self.storeColor[0][2] = self.makeUp.red_l,self.makeUp.green_l,self.makeUp.blue_l
        self.storeColor[1][0],self.storeColor[1][1],self.storeColor[1][2] = self.makeUp.red_e,self.makeUp.green_e,self.makeUp.blue_e
        # fps = self.cap.get(cv2.CAP_PROP_FPS)
        # if int(fps) %10==0:
        # print(fps)
        cv2image = cv2.cvtColor(img_proced, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
               
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        if not self.checkLoaded:
            self.btnStart.config(state="disabled")
            self.createBotton()
        self.checkLoaded = True
        self.lmain.after(30, self.video_stream)

    def doned(self):
        # self.frame = self.imgTempLuu 
        self.checkDoned = True  
        self.makeUp.red_l,self.makeUp.green_l,self.makeUp.blue_l = int(self.storeColor[0][0]),int(self.storeColor[0][1]),int(self.storeColor[0][2])
        self.makeUp.red_e,self.makeUp.green_e,self.makeUp.blue_e = int(self.storeColor[1][0]),int(self.storeColor[1][1]),int(self.storeColor[1][2])

    def show(self,r1,g1,b1,kind1):
        if kind1 == 0:
            self.makeUp.red_l   = r1
            self.makeUp.green_l = g1
            self.makeUp.blue_l  = b1
        else:
            self.makeUp.red_e   = r1  
            self.makeUp.green_e = g1 
            self.makeUp.blue_e  = b1 
        self.kind           = kind1


    def close(self):
        # self.cap.release() 
        self.checkLoaded = True
        cv2.destroyAllWindows()
        # self.gui2.quit()
        self.gui2.destroy()
        
    def createBotton(self):
        
        Label(self.tool_bar, text="Lip", relief=RAISED,  bg = "cyan2").grid(row=1, column=0, padx=5, pady=3, ipadx=10)
        Label(self.tool_bar, text="EyeLiner", relief=RAISED, bg = "coral1").grid(row=1, column=1, padx=5, pady=3, ipadx=10)
    
        Button(self.tool_bar, text="", bg = '#A00A14', command = partial(self.show, 160,10,20,0)).grid(row=2, column=0, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(self.tool_bar, text="", bg = '#FF69F1', command= partial(self.show, 255,100,240,0)).grid(row=3, column=0, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(self.tool_bar, text="", bg = '#CC6600', command= partial(self.show, 204,102,0,0)).grid(row=4, column=0, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(self.tool_bar, text="", bg = '#A717B2', command= partial(self.show, 167,23,178,0)).grid(row=5, column=0, padx=5, pady=5, sticky='w'+'e'+'n'+'s') 


        # eyeliner       
        Button(self.tool_bar, text="", bg = '#000000', command = partial(self.show, 0,0,0 ,1)).grid(row=2, column=1, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(self.tool_bar, text="", bg = '#663300', command=  partial(self.show, 102,51,0,1)).grid(row=3, column=1, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(self.tool_bar, text="", bg = '#5CBF38', command=  partial(self.show, 92,190,56  ,1)).grid(row=4, column=1, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        Button(self.tool_bar, text="", bg = '#A717B2', command=  partial(self.show, 167,23,178 ,1)).grid(row=5, column=1, padx=5, pady=5, sticky='w'+'e'+'n'+'s')


        Button(self.tool_bar, text="DONE", command= self.doned).grid(row=6, columnspan = 2, padx=5, pady=5, sticky='w'+'e'+'n'+'s')

    def _resize_image(self,event):

        new_width = event.width
        new_height = event.height

        self.background_image = Image.open("./background.png").resize((new_width, new_height))

        self.background_image = ImageTk.PhotoImage(self.background_image)
        self.background.configure(image =  self.background_image)






