import tkinter as tk
import tkinter.font
import subprocess
from functools import partial
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
from os import listdir
from os.path import isfile, join
pyglet.font.add_file('./fonts/Roboto-Black.ttf')
pyglet.font.add_file('./fonts/Roboto-BlackItalic.ttf')
pyglet.font.add_file('./fonts/Roboto-Bold.ttf')
pyglet.font.add_file('./fonts/Roboto-BoldItalic.ttf')
pyglet.font.add_file('./fonts/Roboto-Italic.ttf')
pyglet.font.add_file('./fonts/Roboto-Regular.ttf')


FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
class ServerSocketHandler():
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 4444
    SEPARATOR = '<SEPARATOR>'
    BUFFER_SIZE = 4096
    PC_OFICINA = 'DS3tin'
    CLIENT_PORT = 5555

    def __init__(self, leftFrame):
        self.s = socket.socket()  #server
        self.s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #client
        # self.leftFrame = leftFrame
        # self.s.bind((self.SERVER_HOST, self.SERVER_PORT))
        self.leftFrame = leftFrame

    def sendCompletedTaskSignal(self, jsonTask, dxfFile):
        try:
            
            self.s2.connect((socket.gethostbyname(self.PC_OFICINA), self.CLIENT_PORT))            
            print(f"[+] Conected to {socket.gethostbyname(self.PC_OFICINA)}")
        except Exception:
            print("[!] Could not connect to CNC_PC")

        self.s2.send()
    def listenForFiles(self):
        
        # print(f'[+] Listening on port {self.SERVER_PORT}')
        while True:
            self.s = socket.socket()
            self.s.bind((self.SERVER_HOST, self.SERVER_PORT))
            self.s.listen(5)
            # self.s.listen(5)
           
            print('restar loop')
            client_socket, addres = self.s.accept()
            print(f'[+] {addres} connected')

            recieved = client_socket.recv(self.BUFFER_SIZE).decode()
            filename, filesize = recieved.split(self.SEPARATOR)
            filename = os.path.basename(filename)
            print(filename)
            if filename.split('.')[-1] == 'dxf':
                filename = os.path.join('dxf', filename)
            else:

                filename = os.path.join('draws', filename)
            print(f'[+] creating {filename}')
            filesize = int(filesize)

            with open(filename, 'wb') as f:
                while True:

                    bytes_read = client_socket.recv(self.BUFFER_SIZE)
                    if not bytes_read:
                        break

                    f.write(bytes_read)
                print(f'[+] Done recieving {filename}')
            client_socket.close()
            self.s.close()
            self.leftFrame.searchForJobs()
            time.sleep(0.3)
            
            





class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        


# class PendingTaskFrame(tk.Frame):

#     def __init__(self, parent):
#         tk.Frame.__init__(self, parent, width=366, background= '#00425A')

class PendingTaskFrame(tk.Frame):

    def __init__(self, parent, parent_height, rightFrame):
        tk.Frame.__init__(self, parent, width=1000,height=parent_height, background= '#393E46')
        self.right = rightFrame
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

    def checkFolders(self):
        print('[+] check folder initiated')
        previous_files = [f for f in listdir('./draws') if isfile(join('./draws', f))]
        while True:
            new_files = [f for f in listdir('./draws') if isfile(join('./draws', f))]
            if previous_files != new_files:
                print('[+] Draws folder was updated')
                previous_files = new_files
                # self.searchForJobs()
            print('[+] Starting new iterations')
            time.sleep(3)
            
    def searchForJobs(self):
        
        self.references = []
        
        pendinFiles = os.scandir('./draws')
        initialRow = 0
        initialColumn = 0
        for child in self.scrollFrame.winfo_children():
                child.destroy()
                print('destroying Children')
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
            
            infoButton = Button(container, text='Detalles', font=('Roboto Bold',12), width=20, height=2, command=partial(
    self.right.displayTask, self, container))
            infoButton.grid(column=0,row=4)
            self.references.append(container)
            f = open(file)
            data = json.load(f)

        # print(self.references[1].winfo_children()[2].cget('text').split(':')[1]) 
        self.sortJobs()
        
   
    
    def sortJobs(self):
        self. referencesToPass =[]
        self.references.sort(key= lambda x: datetime.datetime.strptime(x.winfo_children()[2].cget('text').split(':')[1], '%d/%m/%y'))
        # print(f'IMPORTANTE {self.references}')
        initialRow = 0
        initialColumn = 0
       
        for job in self.references:
            currentDate = job.winfo_children()[2].cget('text').split(':')[1]
            job.grid(column=initialColumn, row=initialRow, sticky='news', pady=10, padx=10)
            
            # job.winfo_children()[4].configure(command= lambda: self.right.displayTask(self, name, desc, date,file))
            #job.winfo_children()[taskCount].bind("<Button-1>", lambda x: self.right.displayTask(self, *self.referencesToPass[taskCount]))
            
            if initialColumn <= 1:
                initialColumn += 1
            else:
                initialRow += 1
                initialColumn = 0

            # print(currentDate)

def doNothing():
    print('doingNothing')

class viewTaskFrame(tk.Frame):
    SEPARATOR = '<SEPARATOR>'
    PC_OFICINA = 'DS3tin'
    CLIENT_PORT = 5555
    def __init__(self,  parent, parent_height, parent_width):
        tk.Frame.__init__(self, parent, width=366, height=parent_height, background= '#1F8A70')

        self.senderSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.confirmation = None
        self.parent = parent
        self.grid_propagate(0)
        self.name = Label(self, text='NOMBRE TRABAJO', font=('Roboto Bold',20), background="#FF6E31", fg='white',wraplength=340, justify=LEFT)
        self.name.grid(column=0,row=0, padx=10)

        self.DESCRIPTION = Label(self, text='DESCRIPCION', font=('Roboto Bold',20), background="#1F8A70", fg='white',wraplength=340, justify=LEFT)
        self.DESCRIPTION.grid(column=0,row=2)

        self.DATE = Label(self, text='FECHA LIMITE', font=('Roboto Bold',20), background="#1F8A70", fg='white',wraplength=340, justify=LEFT)
        self.DATE.grid(column=0,row=4)

        self.FILE = Label(self, text='ARCHIVO', font=('Roboto Bold',20), background="#1F8A70", fg='white',wraplength=340, justify=LEFT)
        self.FILE.grid(column=0,row=6)

        self.nameLabel = Label(self, text=' ', font=('Roboto',20), background="#1F8A70", fg='white',wraplength=340, justify=LEFT)
        self.nameLabel.grid(column=0,row=1, sticky='w', padx=10)

        self.description = Label(self, text=' ', font=('Roboto',20), background="#1F8A70", fg='white',wraplength=340, justify=LEFT)
        self.description.grid(column=0,row=3, sticky='w', padx=10)
        
        self.date = Label(self, text=' ', font=('Roboto',20), background="#1F8A70", fg='white',wraplength=340, justify=LEFT)
        self.date.grid(column=0,row=5, sticky='w', padx=10)
        
        self.file = Button(self, text=' ', background="#FF6E31", font=('Roboto',20), fg='white',wraplength=340, justify=LEFT)
        # self.file.grid(column=0,row=7, sticky='w', padx=10)

        self.taskDoneButton = Button(self, text='TERMINAR TRABAJO', command = lambda: self.finishJob(),background="#FF6E31", font=('Roboto',20), fg='white',wraplength=340, justify=LEFT)
        self.taskDoneButton.grid(column=0,row=9, sticky='w', padx=10, pady=10)
    
    def sendCompletedTaskSignal(self, jsonTask, dxfFile = 'x'):
        print('[+] fucking snding files')
        try:
            
            self.senderSocket.connect((socket.gethostbyname(self.PC_OFICINA), self.CLIENT_PORT))            
            print(f"[+] Conected to {socket.gethostbyname(self.PC_OFICINA)}")
        except Exception:
            print("[!] Could not connect to CNC_PC")

        
        self.senderSocket.send(f'{jsonTask}{self.SEPARATOR}{dxfFile}'.encode())

        self.senderSocket.close()
        time.sleep(0.5)
        self.senderSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('[+] done sending signal , conection ended')


    def setTrue(self, window):
        self.confirmation = True
        window.destroy()
        window.quit()

    def setFalse(self, window):
        self.confirmation = False
        window.destroy()
        window.quit()
    def create_popup(self):
    # Create the pop-up window
        popup_window = tk.Toplevel(self.parent)
        popup_window.title("Confirmation")
        popup_window.geometry("500x300")
    
    # Add a message to the pop-up window
        message_label = tk.Label(popup_window, text="Seguro que quieres terminar el trabajo?")
        message_label.pack(pady=20)
        
    # Add the confirmation buttons
        confirm_button = tk.Button(popup_window, text="Confirmar", width=10, background="#FF6E31", font=('Roboto',20), fg='white',wraplength=340, justify=LEFT, command= lambda: self.setTrue(popup_window))
        confirm_button.pack(side="left", padx=50)
        cancel_button = tk.Button(popup_window, text="Cancelar", width=10, background="#FF6E31", font=('Roboto',20), fg='white',wraplength=340, justify=LEFT, command= lambda: self.setFalse(popup_window))
        cancel_button.pack(side="right", padx=50)
        popup_window.mainloop()
    def finishJob(self):
        self.create_popup()
        print('hello')
        if self.confirmation == True:
            jsonFileLocation = self.nameLabel.cget('text') + '.json'
            newJsonFileLocation = os.path.join(os.getcwd(), "doneDraws", jsonFileLocation)
            jsonFileLocation = os.path.join(os.getcwd(), "draws", jsonFileLocation)
       
            print(jsonFileLocation)
            os.rename(jsonFileLocation, newJsonFileLocation)
            if self.file.cget('text') != "No archivo":
                dxfFileLocation = self.file.cget('text')
                newDxfFileLocation = os.path.join(os.getcwd(), "doneDxf", dxfFileLocation)
                dxfFileLocation = os.path.join(os.getcwd(), "dxf", dxfFileLocation)
                os.rename(dxfFileLocation, newDxfFileLocation)
                jsonName = self.nameLabel.cget('text') + '.json'
                filename = self.file.cget('text')
                sendCompletedFiles = threading.Thread(target=self.sendCompletedTaskSignal, args=(jsonName, filename))
                sendCompletedFiles.start()
            
            else:
                jsonName = self.nameLabel.cget('text') + '.json'
                sendCompletedFiles = threading.Thread(target=self.sendCompletedTaskSignal, args=(jsonName))
                sendCompletedFiles.start()
                

            print('[+] done transfering file')

            self.nameLabel.configure(text=' ')
            # self.nameLabel.grid(column=0,row=1, sticky='w', padx=10)

            self.description.configure(text=' ')
            # self.description.grid(column=0,row=3, sticky='w', padx=10)
            
            self.date.configure(text=' ')
            # self.date.grid(column=0,row=5, sticky='w', padx=10)
            
        
        
            self.file.configure(text=' ', command= lambda: doNothing())
        
            self.file.grid(column=0,row=7, sticky='w', padx=10)
            self.pendingFrame.searchForJobs()


        elif self.confirmation == False:
            print('[+] Confirmation denied')
        
        self.confirmation = None
        pass
    def displayTask(self,pendingFrame, container):
        self.pendingFrame = pendingFrame
        name = container.winfo_children()[0].cget('text')
        desc = container.winfo_children()[1].cget('text')[2:]  # decription of job
        date = container.winfo_children()[2].cget('text')[2:]  # date
        file = container.winfo_children()[3].cget('text')[2:] 
        
        self.nameLabel.configure(text=name)
        # self.nameLabel.grid(column=0,row=1, sticky='w', padx=10)

        self.description.configure(text=desc)
        # self.description.grid(column=0,row=3, sticky='w', padx=10)
        
        self.date.configure(text=date)
        # self.date.grid(column=0,row=5, sticky='w', padx=10)
        
        fileDirection = os.path.join(os.getcwd(), "dxf", file)
        fileDirection = os.path.normpath(fileDirection)
        print(fileDirection)
        if file == "No archivo":
            self.file.configure(text='No archivo', command= lambda: doNothing())
        else:
            self.file.configure(text=file, command= lambda: subprocess.run([FILEBROWSER_PATH, '/select,', fileDirection]))
        self.file.grid(column=0,row=7, sticky='w', padx=10)
        # self.file.grid(column=0,row=7, sticky='w', padx=10)
        # pendingFrame.searchForJobs()
        # print(name)

# server = ServerSocketHandler()
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
    right = viewTaskFrame(root, root.winfo_height(), root.winfo_width())
    left = PendingTaskFrame(root, root.winfo_height(), right)
    left.grid(column=0,row=0, sticky="nsew")
    server = ServerSocketHandler(left)
    serverLooop = threading.Thread(target=server.listenForFiles)
    serverLooop.start()
    # server = ServerSocketHandler(left)
    # Process(target=server.listenForFiles).start()
    
    #\right = AddTaskFrame(root, root.winfo_height(), root.winfo_width(), left, server)
    right.grid(column=1,row=0, sticky="nsew")

    
    # p = multiprocessing.Process(target=detectChanges, args=[left])
    # p.start()
    # print(left.winfo_width())
    # print(root.winfo_width())
    # print(root.winfo_height())
    # Process(target=left.checkFolders).start()
    # Process(root.mainloop()).start()
    

    root.mainloop() 

def updateJobs(left):
    left.searchForJobs()

def listenFiles():
    # server.listenForFiles()
    pass
def detectChanges(fuckingLeft):
    
    previous_files = [f for f in listdir('./draws') if isfile(join('./draws', f))]
    while True:
        new_files = [f for f in listdir('./draws') if isfile(join('./draws', f))]
        if previous_files != new_files:
            print('[+] Draws folder was updated')
            previous_files = new_files
            fuckingLeft.searchForJobs()
            
            
        time.sleep(3)
if __name__ == "__main__":
    main = threading.Thread(target=initRoot)
    main.start()
    # serverLooop = threading.Thread(target=server.listenForFiles)
    # serverLooop.start()
    
    # Process(target=detectChanges).start()
    # Process(target=sendFiles).start()
    # Process(target=conectToServer).start()