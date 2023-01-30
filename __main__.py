# from tkinter import *
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import random
# root = Tk()  # main window i guess
# root.geometry("1366x769")  # initial size of main window
# add_task_window = Toplevel(root) create a new window 
# add_task = Button(root, text="+")  # defining a
# add_task.pack()

# root.mainloop()

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.geometry("1366x769")
        self.title('Trabajos')
        self['background'] = "#393E46"

        self.image = Image.open("./images/addButton.png").convert('RGBA')
      
        self.img = self.image.resize((75,75))
        
        self.add_button_image = ImageTk.PhotoImage(self.img)
        self.add_button_label = Label(image=self.add_button_image)
        self.add_button = tk.Button(self, image=self.add_button_image, command=self.show_popup, borderwidth=0)
        self.add_button.place(rely=1.0, relx=1.0, x=-10, y=-10, anchor=SE)


    def show_popup(self):
        print("button has bee nrpesed")


class AutoGrid(tk.Frame):
    def __init__(self, master=None, **kwargs):
        frame = tk.Frame.__init__(self, master, **kwargs)
        self.columns = None
        self.bind('<Configure>', self.regrid)
       

    def regrid(self, event=None):
        width = self.winfo_width()
        slaves = self.grid_slaves()
        max_width = max(slave.winfo_width() for slave in slaves)
        cols = width // max_width
        if cols == self.columns: # if the column number has not changed, abort
            return
        for i, slave in enumerate(slaves):
            slave.grid_forget()
            slave.grid(row=i//cols, column=i%cols)
        self.columns = cols


class TestFrame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, bd=5, relief=tk.RAISED, **kwargs)
        print('add')
        tk.Label(self, text="name").pack(pady=10)
        tk.Label(self, text=" info ........ info ").pack(pady=10)
        tk.Label(self, text="data\n"*5).pack(pady=10)



def callback(event):
    print('hi')

if __name__ == "__main__":

    app = App()
    app.geometry("1366x769")
    frame = AutoGrid(app, background='#393E46')
  
    frame.pack(fill=tk.BOTH, expand=True)
    
    
    TestFrame(frame).grid() # use normal grid parameters to set up initial layout
    TestFrame(frame).grid(column=1)
    TestFrame(frame).grid(column=2)
    TestFrame(frame).grid()
    for i in range(10):
        TestFrame(frame).grid()
 
    app.mainloop()
    