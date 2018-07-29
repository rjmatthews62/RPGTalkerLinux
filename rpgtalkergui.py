from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import *
from tkinter import messagebox
import bluetooth
import queue
from dbusmgr import *
import threading
import queue

class RpgTalkerGUI:
    """ TKInter front end for RPG Talker
    """
    def __init__(self,win):
        "win=main window"
        self.win=win
        self.buildframe()
        self.buildmenu()
        self.input=queue.Queue()
        self.mgr=DbusManager()
        self.populatebt()
        self.centerwindow()
        self.win.bind("<<QueueThread>>",self.queuehandle)
        self.queue=queue.Queue()

    def queuehandle(self, evt):
        """
        Handle thread actions in main gui thread
        """
        while True:
            try:
                msg=self.queue.get_nowait()
            except:
                return
            print(msg)
            if msg[0]=="btlist":
                self.updatebtlist(msg[1])

    def sendqueue(self, action, msg):
        self.queue.put((action,msg))
        self.win.event_generate("<<QueueThread>>")
    
    def buildframe(self):
        self.win.title("RPGTalker GUI")
        Label(self.win,text="Paired Devices").pack(fill="x")
        self.bluetoothlist=Listbox(self.win)
        panel1=Frame(self.win)
        panel1.pack(expand=1, fill="x")
        button1=Button(panel1,text="Tick",command=self.button1click).pack(side=LEFT)
        button2=Button(panel1,text="Update",command=self.populatebt).pack(side=LEFT)
        Button(panel1,text="Connect", command=self.connect).pack(side=LEFT)
        Button(panel1,text="Disconnect", command=self.disconnect).pack(side=LEFT)
        self.bluetoothlist.pack(expand=1, fill="both")

    def buildmenu(self):
        self.menubar=Menu(self.win)
        filemenu=Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=filemenu)
        self.win.config(menu=self.menubar)

    def button1click(self):
        print("Button 1 clicked")
        t=threading.Timer(2,self.ontick)
        t.start()

    def ontick(self):
        self.sendqueue("print","This is a queued message from ontick")
        
    def quit(self):
        self.win.destroy()

    def populatebt(self):
        "Populate bluetooth list"
        devlist=self.mgr.friendly_names()
        self.devices=devlist
        lb=self.bluetoothlist
        lb.delete(0,END)
        for name in sorted(devlist.keys()):
            lb.insert(END,name)
        
    def connect(self):
        lb=self.bluetoothlist
        sel=lb.curselection()
        if len(sel)<1:
            print("Nothing selected.")
            return
        key=lb.get(sel[0])
        print("Key=",key)
        addr=self.devices[key]
        print("Addr=",addr)
        self.mgr.connect(addr,"110E")

    def disconnect(self):
        lb=self.bluetoothlist
        sel=lb.curselection()
        if len(sel)<1:
            print("Nothing selected.")
            return
        key=lb.get(sel[0])
        print("Key=",key)
        addr=self.devices[key]
        print("Addr=",addr)
        self.mgr.disconnect(addr)
        
        
    def dostuff(self):
        print("After called.")
        
    def centerwindow(self):
        "Center window in screen"
        win=self.win
        ws = win.winfo_screenwidth()/2 # width of the screen (but I have a double screen...)
        hs = win.winfo_screenheight() # height of the screen
        h = win.winfo_reqheight()
        w = win.winfo_reqwidth() 
        x = (ws-w)/2
        y = (hs-h)/2
        win.geometry('%dx%d+%d+%d' % (w, h, x, y))

print("Starting")
root=Tk()
print("Building frame")
app=RpgTalkerGUI(root)
print("Main loop")
root.mainloop()
        
