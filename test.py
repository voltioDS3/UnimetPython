import tkinter as tk
import tkinter.font
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
from tkcalendar import DateEntry
import os
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
        tk.Frame.__init__(self, parent, width=1000, height=parent_height, background= '#393E46')



class AddTaskFrame(tk.Frame):
    
    def __init__(self, parent, parent_height, parent_width):
        tk.Frame.__init__(self, parent, width=parent_width-1000, height=parent_height, background= '#1F8A70')
        self.grid_propagate(0)

        ###  form variables ###
        self.dxfFileName = 'x'
        self.jobName = 'x'
        self.description = 'x'
        self.date = 'x'

        ###  Job name section ###
        self.nameLabel = Label(self, text='Nombre del trabajo', font=('Roboto Bold',20), background="#1F8A70", fg='white')
        self.nameEntrie = tk.Entry(self, width=37,font=('Roboto Bold',12))
        self.nameEntrie.grid(column=0,row=1, padx=10, pady=10)
        self.nameLabel.grid(column=0,row=0, sticky='w', padx=10)

        ###  Description section ###
        self.descriptionLabel = Label(self, text='Descripción', font=('Roboto Bold',20), background="#1F8A70", fg='white')
        self.descriptionEntrie = Text(self, height=10, width=37, font=('Roboto Bold',12))
        self.descriptionEntrie.grid(column=0, row=3)
        self.descriptionLabel.grid(column=0,row=2, sticky='w', padx=10, pady=10)

        ###  Date section ###
        self.dateLabel = Label(self, text='Fecha Limite', font=('Roboto Bold',20), background="#1F8A70", fg='white')
        self.dateLabel.grid(column=0,row=4, sticky='w', padx=10, pady=10)
        self.cal = DateEntry(self, selectmode='day', width = 30, locale='es_ES',  font=('Roboto Bold',12))
        self.cal.grid(column=0, row=5, sticky='w', padx=10)

        ###  Upload File section ###
        self.fileLabel = Label(self, text='Archivo', font=('Roboto Bold',20), background="#1F8A70", fg='white')
        self.fileLabel.grid(column=0,row=6, sticky='w', padx=10, pady=10)
        self.fileButton = Button(self, text='Abrir archivo', width=20,command=lambda:self.uploadFile())
        self.fileButton.grid(column=0, row=7)

        ###  Submit Button section ###
        self.submitButton = Button(self, text='Subir Trabajo', font=('Roboto Bold',12), width=20, height=2, command= lambda:self.getFormEntries())
        self.submitButton.grid(column=0,row=11, pady=10)

    def uploadFile(self):
        fileTypes = [('dxf Files','*dxf')]
        filename = filedialog.askopenfilename(filetypes=fileTypes)
        self.dxfFileName = filename
        print(filename)
        

        dxfButtonImage = ImageTk.PhotoImage(Image.open('./images/dxf.png').resize((100,100)))

        dxfButton = Button(self, image=dxfButtonImage, background= '#1F8A70', borderwidth=0,  activebackground='#1F8A70', command= lambda : os.startfile(filename))
        dxfButton.photo = dxfButtonImage
        
        
        # dxfButtonLabel.grid(column=0,row=9)
        dxfButton.grid(column=0, row=9, pady=10)

        name = filename.split('/')[-1]
        print(name)
        dxfButtonLabel = Label(self,text=name, background='#1F8A70', font=('Roboto Bold',10))
        dxfButtonLabel.grid(column=0, row=10)

    def getFormEntries(self):
        pass
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