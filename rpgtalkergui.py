from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import *
from tkinter import messagebox
import bluetooth
import queue
from dbusmgr import *
import threading
import queue

class BtDevice:
    "Holder for Bluetooth device info."
    def __init__(self,name,addr):
        self.name=name
        self.addr=addr
        self.connected=False

    def __str__(self):
        result=self.name
        if self.connected:
            result+="*"
        return result
    
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
        self.device={}
        self.devindex=[]
        self.populatebt()
        self.win.update_idletasks()
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
        self.panes = ttk.Notebook(self.win)
        self.panes.pack(expand=1, fill="both")

        tab1 = Frame(self.panes)
        self.panes.add(tab1,text="Paired Devices")
        
        self.bluetoothlist=Listbox(tab1)
        panel1=Frame(tab1)
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
        self.devices=self.mgr.device_properties()
        lb=self.bluetoothlist
        lb.delete(0,END)
        self.devindex=[]
        for name in sorted(devlist.keys()):
            dev=BtDevice(name,devlist[name])
            prop=self.devices[dev.addr]
            dev.connected=(prop['Connected']==1)
            lb.insert(END,dev)
            self.devindex.append(dev)
        
    def getselected(self):
        lb=self.bluetoothlist
        sel=lb.curselection()
        if len(sel)<1:
            return None
        return self.devindex[sel[0]]
    
    def connect(self):
        dev=self.getselected()
        if dev==None:
            print("Nothing selected.")
            return
        print("Key=",dev)
        print("Addr=",dev.addr)
        self.mgr.connect(dev.addr,"110E")

    def disconnect(self):
        dev=self.getselected()
        if dev==None:
            print("Nothing selected.")
            return
        self.mgr.disconnect(dev.addr)
        
    def dostuff(self):
        print("After called.")
        
    def centerwindow(self):
        "Center window in screen"
        win=self.win
        ws = win.winfo_screenwidth()  # width of the screen (I have a wide screen)
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
        
