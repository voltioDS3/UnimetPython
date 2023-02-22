import tkinter as tk
import tkinter.font
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
from tkcalendar import DateEntry
import os
import pyglet
import json
import datetime
import multiprocessing
from multiprocessing import Process
import socket
import time
import threading
pyglet.font.add_file('./fonts/Roboto-Black.ttf')
pyglet.font.add_file('./fonts/Roboto-BlackItalic.ttf')
pyglet.font.add_file('./fonts/Roboto-Bold.ttf')
pyglet.font.add_file('./fonts/Roboto-BoldItalic.ttf')
pyglet.font.add_file('./fonts/Roboto-Italic.ttf')
pyglet.font.add_file('./fonts/Roboto-Regular.ttf')



class ClientSocketHadler():
    CNC_PC_NAME = 'DS3tin'
    
    print(socket.gethostbyname(CNC_PC_NAME))
    CNC_PC_PORT = 4444
    SEPARATOR = "<SEPARATOR>"
    BUFFER_SIZE = 4096
    def  __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    
    def startConection(self):

        try:
            
            self.s.connect((socket.gethostbyname(self.CNC_PC_NAME), self.CNC_PC_PORT))            
            print(f"[+] Conected to {socket.gethostbyname(self.CNC_PC_NAME)}")
        except Exception:
            print("[!] Could not connect to CNC_PC")
        
    def sendTasks(self, jsonFile, dxfFile = 'x'):
        # try:
            
        #     self.s.connect((socket.gethostbyname(self.CNC_PC_NAME), self.CNC_PC_PORT))            
        #     print(f"[+] Conected to {socket.gethostbyname(self.CNC_PC_NAME)}")
        # except Exception:
        #     print("[!] Could not connect to CNC_PC")
        
        filesList = [jsonFile,dxfFile]
        print(filesList)
        
     
   
        for file in filesList:
            
            if file == 'x':
                break
            try:
            
                self.s.connect((socket.gethostbyname(self.CNC_PC_NAME), self.CNC_PC_PORT))            
                print(f"[+] Conected to {socket.gethostbyname(self.CNC_PC_NAME)}")
            except Exception:
                print("[!] Could not connect to CNC_PC")

            filesize = os.path.getsize(file)
            self.s.send(f"{file}{self.SEPARATOR}{filesize}".encode())
            with open(file, 'rb') as f:
                while True:
                    bytes_read = f.read(self.BUFFER_SIZE)
                    if not bytes_read:
                        break  
                    self.s.sendall(bytes_read)
                print(f'[+] Done sending {file}')
                # self.s.close()
            
            print('trying to send another file')
            
            self.s.close()
            time.sleep(0.5)
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('conection ended')

        # self.s.close()
        
                



class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        


# class PendingTaskFrame(tk.Frame):

#     def __init__(self, parent):
#         tk.Frame.__init__(self, parent, width=366, background= '#00425A')

class PendingTaskFrame(tk.Frame):

    def __init__(self, parent, parent_height):
        tk.Frame.__init__(self, parent, width=1000,height=parent_height, background= '#393E46')
        
        self.grid_propagate(0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, background="#393E46")
        self.verticalScrollbar = Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.scrollFrame = tk.Frame(self.canvas, background="#393E46")
        self.scrollFrame.bind(
    "<Configure>",
    lambda e: self.canvas.configure(
        scrollregion=self.canvas.bbox("all")
    )
)       
        self.canvas.create_window((0, 0), window=self.scrollFrame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.verticalScrollbar.set)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.grid(column=0,row=0, sticky="nsew")

        self.verticalScrollbar.grid(row=0,column=1, sticky="nsew")
        self.searchForJobs()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def searchForJobs(self):
        self.references = []
        
        pendinFiles = os.scandir('./draws')
        initialRow = 0
        initialColumn = 0
        for file in pendinFiles:
            # print(self.winfo_width)
            container = Frame(self.scrollFrame, width=300, background= '#243763', height=300)
            container.grid_propagate(0)
            container.grid_rowconfigure(0, weight=0)
            container.grid_columnconfigure(0, weight=0)
            # container.grid(column=initialColumn, row=initialRow, sticky='news', pady=10, padx=10)
            
            f = open(file)
            data = json.load(f)
            jobLabel = Label(container,text=data['jobName'], font=('Roboto Bold',20), background="#FF6E31", fg='white', justify=CENTER, wraplength=300)
            jobLabel.grid(column=0, row=0)

            descLabel = Label(container,text=f'D:{data["descripcion"]}', font=('Roboto Bold',20), background="#243763", fg='white', wraplength=300, justify=LEFT)
            descLabel.grid(column=0, row=1, sticky='w')
            
            dateLabel = Label(container,text=f"F:{data['date']}", font=('Roboto Bold',20), background="#243763", fg='white')
            dateLabel.grid(column=0, row=2, sticky='w')

            if data['file'] == 'x':
                fileLabel = Label(container,text='A:No archivo', font=('Roboto Bold',20), background="#243763", fg='white')
                fileLabel.grid(column=0, row=3, sticky='w')
            else:
                fileLabel = Label(container,text=f"A:{data['file'].split('/')[-1]}", font=('Roboto Bold',20), background="#243763", fg='white')
                fileLabel.grid(column=0, row=3, sticky='w')
            if initialColumn <= 1:
                initialColumn += 1
            else:
                initialRow += 1
                initialColumn = 0
            self.references.append(container)
            f = open(file)
            data = json.load(f)

        # print(self.references[1].winfo_children()[2].cget('text').split(':')[1]) 
        self.sortJobs()
        
    
    def sortJobs(self):
        
        self.references.sort(key= lambda x: datetime.datetime.strptime(x.winfo_children()[2].cget('text').split(':')[1], '%d/%m/%y'))
        # print(f'IMPORTANTE {self.references}')
        initialRow = 0
        initialColumn = 0
        for job in self.references:
            currentDate = job.winfo_children()[2].cget('text').split(':')[1]
            job.grid(column=initialColumn, row=initialRow, sticky='news', pady=10, padx=10)

            if initialColumn <= 1:
                initialColumn += 1
            else:
                initialRow += 1
                initialColumn = 0

            # print(currentDate)




class AddTaskFrame(tk.Frame):
    
    def __init__(self, parent, parent_height, parent_width, left_frame, clientObj):
        tk.Frame.__init__(self, parent, width=366, height=parent_height, background= '#1F8A70')
        self.left = left_frame
        self.grid_propagate(0)
        self.clientSocket = clientObj
        # self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)
        ###  form variables ###
        self.dxfFileName = 'x'
        self.jobName = 'x'
        self.description = 'x'
        self.date = 'x'

        ###  Job namgite section ###
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

        self.closeFile = Button(self, text='X', command=lambda:self.removeDxf())
        self.closeFile.grid(column=0, row=8)

        ###  Submit Button section ###
        self.submitButton = Button(self, text='Subir Trabajo', font=('Roboto Bold',12), width=20, height=2, command= lambda:self.getFormEntries())
        self.submitButton.grid(column=0,row=11, pady=10)

    def removeDxf(self):
        self.dxfButton.grid_remove()
        self.dxfButtonLabel.grid_remove()

    def uploadFile(self):
        fileTypes = [('dxf Files','*dxf')]
        filename = filedialog.askopenfilename(filetypes=fileTypes)
        self.dxfFileName = filename
        print(filename)
        
        if 'dxf' in filename:
            self.dxfButtonImage = ImageTk.PhotoImage(Image.open('./images/dxf.png').resize((100,100)))
            self.dxfButton = Button(self, image=self.dxfButtonImage, background= '#1F8A70', borderwidth=0,  activebackground='#1F8A70', command= lambda : os.startfile(filename))
            self.dxfButton.photo = self.dxfButtonImage
        

        # dxfButtonLabel.grid(column=0,row=9)
            self.dxfButton.grid(column=0, row=9, pady=10)

            name = filename.split('/')[-1]
            print(f"[+] Succefuly loaded {name}")
            self.dxfButtonLabel = Label(self,text=name, background='#1F8A70', font=('Roboto Bold',10))
            self.dxfButtonLabel.grid(column=0, row=10)

    def getFormEntries(self):
        dataDictionary = {"jobName" : "x",
        "descripcion" : "x",
        "date" : "x",
        "file" : "x"} 
        
        dataDictionary["jobName"] = self.nameEntrie.get()
        dataDictionary["descripcion"] = self.descriptionEntrie.get("1.0",END)[0:-2]
        dataDictionary["date"] = self.cal.get()
        
        if self.dxfFileName != "x":
            dataDictionary["file"] = self.dxfFileName
            self.removeDxf()

        self.dxfFileName = 'x'
        self.jobName = 'x'
        self.description = 'x'
        self.date = 'x'
        self.nameEntrie.delete(0,END)
        self.descriptionEntrie.delete("1.0",END)
        
        with open(f'./draws/{dataDictionary["jobName"]}.json', 'w') as outputFile:
            json.dump(dataDictionary, outputFile)
            

            print('[+] File created succesfuly')
        
        ### SEND FILE VIA FTP ###
        jsonfile = f'./draws/{dataDictionary["jobName"]}.json'
        sendFiles = threading.Thread(target=self.clientSocket.sendTasks(jsonfile,dataDictionary["file"]))
        sendFiles.start()
        # Process(target=self.clientSocket.sendTasks(jsonfile, dataDictionary['file']))
       
        print(f'[+] json: {dataDictionary}')
        updateJobs(self.left)
        dataDictionary = dict.fromkeys(dataDictionary, 0)
        
        # pendinFiles = os.scandir('./draws')
        # for file in pendinFiles:
        #     print(file)
        # print(pendinFiles)
        # print(dataDictionary)
        pass


clie = ClientSocketHadler()
def initRoot():
    root = tk.Tk()
    root['background'] = "#393E46"
    root.geometry("1366x769")
    root.update_idletasks()
    # root.grid_rowconfigure(0, weight=1)
    # root.columnconfigure(0, weight=1)
    root.title("UnimetApp")
    root.resizable(False,False)
    # main = MainApplication(root,  background= '#393E46')
    
    # main.pack(side="top", fill="both", expand=True)
    # print(main.winfo_width())
    
    left = PendingTaskFrame(root, root.winfo_height())
    left.grid(column=0,row=0, sticky="nsew")

    right = AddTaskFrame(root, root.winfo_height(), root.winfo_width(), left, clie)
    right.grid(column=1,row=0, sticky="nsew")

  
    
    # print(left.winfo_width())
    # print(root.winfo_width())
    # print(root.winfo_height())
    root.mainloop()

def updateJobs(left):
    left.searchForJobs()

def conectToServer():
    clie.startConection()
def sendFiles():
    CNC_PC_NAME = 'DS3tin'
    
    print(socket.gethostbyname(CNC_PC_NAME))
    CNC_PC_PORT = 4444
    SEPARATOR = "<SEPARATOR>"
    BUFFER_SIZE = 4096

    while True:
        print('strat sening')
        time.sleep(2)
        print('sfdj sengind')
    
if __name__ == "__main__":
    main = threading.Thread(target=initRoot)
    main.start()
    # Process(target=initRoot).start()
    # Process(target=sendFiles).start()
    # Process(target=conectToServer).start()