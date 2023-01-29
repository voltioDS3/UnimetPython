# from tkinter import *
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
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
        self.image = Image.open("./images/addButton.png")
        self.img = self.image.resize((75,75))
        self.add_button_image = ImageTk.PhotoImage(self.img)
        self.add_button_label = Label(image=self.add_button_image)
        self.add_button = Button(self, image=self.add_button_image, command=self.show_popup, borderwidth=0, )
        self.add_button.pack()


    def show_popup(self):
        print("button has bee nrpesed")
if __name__ == "__main__":
    app = App()
    app.geometry("1366x769")
    app.mainloop()
