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
import queue
import socket
import time
import threading
pyglet.font.add_file('./fonts/Roboto-Black.ttf')
pyglet.font.add_file('./fonts/Roboto-BlackItalic.ttf')
pyglet.font.add_file('./fonts/Roboto-Bold.ttf')
pyglet.font.add_file('./fonts/Roboto-BoldItalic.ttf')
pyglet.font.add_file('./fonts/Roboto-Italic.ttf')
pyglet.font.add_file('./fonts/Roboto-Regular.ttf')


class NetworkHandler():

    ### CONSTANTS AS A CLIENT ###
    CNC_PC_NAME = 'DS3tin'  # the cnc pc that is far away
    CNC_PC_PORT = 4444  # port for conecting and sending
    SEPARATOR = "<SEPARATOR>"
    BUFFER_SIZE = 4096

    ### CONSTANTS AS A SERVER ###
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 5555
    SEPARATOR = '<SEPARATOR>'

    def  __init__(self, q, q2):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket for sending files to CNC
        self.server = socket.socket()  # socket for recieving and listening for completed tasks form CNC
        self.q = q
        self.q2 = q2
    def listenForCompletedTask(self):
        while True:
            try:
                self.server = socket.socket()
                self.server.bind((self.SERVER_HOST, self.SERVER_PORT))
                self.server.listen(5)  # listening for CNC to send completed tasks
            
                client_socket, addres = self.server.accept()
                print(f'[+] {addres} connected')

                recieved = client_socket.recv(1024).decode()
                jsonFile , dxfFile = recieved.split(self.SEPARATOR)

                newJsonFileLocation = os.path.join(os.getcwd(), "doneDraws", jsonFile)
                jsonFileLocation = os.path.join(os.getcwd(), "draws", jsonFile)
                os.rename(jsonFileLocation, newJsonFileLocation)

                if dxfFile != 'x':
                    newDxfFileLocation = os.path.join(os.getcwd(), 'doneDxf', dxfFile)
                    dxfFileLocation = os.path.join(os.getcwd(), 'dxf', dxfFile)
                    os.rename(dxfFileLocation, newDxfFileLocation)
                print('[+] moving finished tasks')

                self.q2.put('True')
                #########################################################################
                # NEED TO IMPLEMENT QUEUE TO PASS TKINTER OBJECT A SIGNAL TO REFRESH FILES
                #########################################################################
            except socket.error:
                print('[!] Error with socket, either CNC_PC could not mantain conection files or conection could not happen')
                ################################################################
                # NEED TO DO SOMETHING TO HANDLE AN ERROR WHEN TRANSFERING FILES
                ################################################################
    def sendTasks(self):
        jsonFile, dxfFile = self.q.get() 
        print(f' queue retrived file: {jsonFile}')
        filesList = [jsonFile,dxfFile]
        print(filesList)
        for file in filesList:
            if file == 'x':
                break
            try:
                self.client.connect((socket.gethostbyname(self.CNC_PC_NAME), self.CNC_PC_PORT))           
                print(f"[+] Conected to {socket.gethostbyname(self.CNC_PC_NAME)}")
            except socket.error:
                print("[!] Could not connect to CNC_PC")

            try:
                filesize = os.path.getsize(file)
                self.client.send(f"{file}{self.SEPARATOR}{filesize}".encode())
                with open(file, 'rb') as f:
                    while True:
                        bytes_read = f.read(self.BUFFER_SIZE)
                        if not bytes_read:
                            break  
                        self.client.sendall(bytes_read)
                    print(f'[+] Done sending {file}')
                    
                
                
                self.client.close()
                time.sleep(0.5)
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print('[+] Conection ended')
            except socket.error:
                print('[!] Socket could not send files or file')

            print('[!] Trying to send another file')
        
        # self.q.clear()
                ##################################
                #NEED TO DO SOME TYPE OF FILES THAT WHERE NOT SEND AND SEND THEM WHEN CNC PC IS AVAILABLE
                ##################################


class PendingTaskFrame(tk.Frame):
   
    def __init__(self, parent, parent_height, q2):
        tk.Frame.__init__(self, parent, width=1000,height=parent_height, background= '#393E46')
        
        self.q2 = q2
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

        checkLoop = threading.Thread(target=self.chechCompletedTasks)
        checkLoop.start()
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def chechCompletedTasks(self):
        while True:
            print('[+] pending detected change')
            result =self.q2.get(block=True)
            print('[+] RECIEVED')
            if result == 'True':
                self.searchForJobs()
                
    def searchForJobs(self):
        self.references = []
        
        pendinFiles = os.scandir('./draws')
        initialRow = 0
        initialColumn = 0

        for child in self.scrollFrame.winfo_children():
            child.destroy()
            print('[+] destroying children')
        for file in pendinFiles:
            
            container = Frame(self.scrollFrame, width=300, background= '#243763', height=300)
            container.grid_propagate(0)
            container.grid_rowconfigure(0, weight=0)
            container.grid_columnconfigure(0, weight=0)
            
            
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
        self.sortJobs()
        
    
    def sortJobs(self):
        
        self.references.sort(key= lambda x: datetime.datetime.strptime(x.winfo_children()[2].cget('text').split(':')[1], '%d/%m/%y'))
        
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


class AddTaskFrame(tk.Frame):
   
    def __init__(self, parent, parent_height, parent_width, left_frame, queue, p2phandler):
        tk.Frame.__init__(self, parent, width=366, height=parent_height, background= '#1F8A70')
        self.left = left_frame
        self.grid_propagate(0)

        ### MULTIPROCESING VARIABLES DECLARATION ###
        self.q = queue
        self.p2phadler = p2phandler
        
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
        self.submitButton = Button(self, text='Subir Trabajo', font=('Roboto Bold',12), width=20, height=2, command= lambda: threading.Thread(target = self.getFormEntries).start())
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
        
        ### SEND FILE VIA FTP ##############################################
        
        jsonfile = f'./draws/{dataDictionary["jobName"]}.json'

        self.q.put((jsonfile,dataDictionary["file"]))
        sendingThread = threading.Thread(target=self.p2phadler.sendTasks)
        sendingThread.start()
        sendingThread.join()
        # sendFiles = threading.Thread(target=self.clientSocket.sendTasks(jsonfile,dataDictionary["file"]))
        # self.sendTasks(jsonfile,dataDictionary["file"])
        # sendFiles.start()
        ### SEND FILE VIA FTP ##############################################
        print(f'[+] json: {dataDictionary}')
        ##### TESTING AREA UNCOMENT IF BAD
        # updateJobs(self.left)

        self.left.searchForJobs()

        ### end of testing area
        dataDictionary = dict.fromkeys(dataDictionary, 0)

    



def updateJobs(left):
    left.searchForJobs()


    
if __name__ == "__main__":
    ### defining queue for comunications between threads ###
    q = queue.Queue()  # queue for sending task
    q2 = queue.Queue()  # queue for listening files
    ### defining main window ###
    root = tk.Tk()
    root['background'] = "#393E46"
    root.geometry("1366x769")
    root.update_idletasks()
    root.title("UnimetApp")
    root.resizable(False,False)
    p2phandler = NetworkHandler(q, q2)
    ### defining pending side frame
    pendingTask = PendingTaskFrame(root, root.winfo_height(), q2=q2)
    pendingTask.grid(column=0,row=0, sticky="nsew")

    ### defining add task side frame
    addTask = AddTaskFrame(root, root.winfo_height(), root.winfo_width(), pendingTask, q, p2phandler)
    addTask.grid(column=1,row=0, sticky="nsew")

    ### p2p handler ###
    
    server = threading.Thread(target=p2phandler.listenForCompletedTask) 
    server.start()
    print(threading.enumerate())
    root.mainloop()
    
