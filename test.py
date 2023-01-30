import tkinter as tk
import tkinter.font
from tkinter import *

import pyglet
pyglet.font.add_file('./fonts/Roboto-Black.ttf')
pyglet.font.add_file('./fonts/Roboto-BlackItalic.ttf')
pyglet.font.add_file('./fonts/Roboto-Bold.ttf')
pyglet.font.add_file('./fonts/Roboto-BoldItalic.ttf')
pyglet.font.add_file('./fonts/Roboto-Italic.ttf')
pyglet.font.add_file('./fonts/Roboto-Regular.ttf')
class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        


# class PendingTaskFrame(tk.Frame):

#     def __init__(self, parent):
#         tk.Frame.__init__(self, parent, width=366, background= '#00425A')

class PendingTaskFrame(tk.Frame):

    def __init__(self, parent, parent_height):
        tk.Frame.__init__(self, parent, width=1000, height=parent_height, background= '#00425A')
    


class AddTaskFrame(tk.Frame):
    
    def __init__(self, parent, parent_height, parent_width):
        tk.Frame.__init__(self, parent, width=parent_width-1000, height=parent_height, background= '#1F8A70')
        self.grid_propagate(0)
        
        self.nameLabel = Label(self, text='Nombre del trabajo', font=('Roboto Bold',20), background="#1F8A70", fg='white')
        self.nameEntrie = tk.Entry(self, width=55,font=('Roboto Regular',10))
        self.nameEntrie.grid(column=0,row=1, padx=10, pady=10)
        self.nameLabel.grid(column=0,row=0, sticky='w', padx=10, pady=10)

        self.nameLabel = Label(self, text='Descripcion', font=('Roboto',25), background="#1F8A70")
        self.nameLabel.grid(column=0,row=2, sticky='w', padx=10, pady=10)
if __name__ == "__main__":
    root = tk.Tk()
    root['background'] = "#393E46"
    root.geometry("1366x769")
    root.update_idletasks()
    root.resizable(False,False)
    main = MainApplication(root,  background= '#393E46')
    
    main.pack(side="top", fill="both", expand=True)
    print(main.winfo_width())

    left = PendingTaskFrame(root, root.winfo_height())
    left.pack(side='left')

    right = AddTaskFrame(root, root.winfo_height(), root.winfo_width())
    right.pack(side='right')
    print(left.winfo_width())
    print(root.winfo_width())
    print(root.winfo_height())
    root.mainloop()