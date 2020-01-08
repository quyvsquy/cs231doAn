from tkinter import *
from PIL import Image, ImageTk
from GUI1 import GUI1
from GUI2 import GUI2
from GUI3 import GUI3


class GUI():
    def __init__(self,gui):
        self.gui  = gui
        self.background_image = ImageTk.PhotoImage(Image.open("./demo.png"))
        self.background = Label(self.gui, image=self.background_image)
        self.background.pack(fill='both', expand=True)
        self.background.image = self.background_image 
        self.background.bind('<Configure>', self._resize_image)

    def _resize_image(self,event):

        new_width = event.width
        new_height = event.height

        self.background_image = Image.open("./demo.png").resize((new_width, new_height))

        self.background_image = ImageTk.PhotoImage(self.background_image)
        self.background.configure(image =  self.background_image)
    def close_window(self): 
        gui.destroy()

    def call_GUI1(self):
        win1 = Toplevel()
        win1.title("Digital Makeup with Image")
        win1.geometry('1024x720')
        main = GUI1(win1)
        main.create_left_right_frames()

    def call_GUI2(self):
        win1 = Toplevel()
        win1.title("Digital Makeup with Video")
        win1.geometry('1024x720')
        win1.config(bg="skyblue")

        main = GUI2(win1)
        main.create_Screen()

    def call_GUI3(self):
        win1 = Toplevel()
        win1.title("Team Information")
        win1.geometry('1024x720')
        win1.config(bg="skyblue")

        main = GUI3(win1)

    def show(self):
        self.btn1 = Button(self.background, text='Image', width='20', height='3', bg = 'CadetBlue1', command =self.call_GUI1)
        self.btn1.pack( padx=10, pady=10)
        self.btn2= Button(self.background, text='Video', width='20', height='3', bg = 'CadetBlue1', command =self.call_GUI2)
        self.btn2.pack(padx=10, pady=10)
        self.btn3 = Button(self.background, text='Our Team', width='20', height='3', bg = 'CadetBlue1', command =self.call_GUI3)
        self.btn3.pack(padx=10, pady=10)
        Button(self.background, text='Quit', width='20', height='3', bg = 'tan1',  command = self.close_window).pack(padx=10, pady=10)

if __name__ == "__main__":
    gui = Tk()

    gui.title('Digital Face Makeup')
    gui.geometry('1024x720')
    main = GUI(gui)
    main.show()

    gui.mainloop()