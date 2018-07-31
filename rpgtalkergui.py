from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter.scrolledtext import *
from tkinter import messagebox
import bluetooth
import queue
from dbusmgr import *
import threading
import queue
from rpgutils import *
import glob
import os
from pygame import mixer
import pulsectl

class BtDevice:
    "Holder for Bluetooth device info."
    def __init__(self,name=None,addr=None):
        self.name=name
        self.addr=addr
        self.connected=False

    def __str__(self):
        result=str(self.name)
        if self.connected:
            result+="*"
        return result

    def __eq__(self,y):
        if type(y) is BtDevice:
            return self.addr==y.addr
        return self.addr==str(y)
    def __repr__(self):
        return str(self.name)+": "+str(self.addr)

    def copy(self,btdevice):
        if (type(btdevice) is BtDevice):
            self.name=btdevice.name
            self.addr=btdevice.addr
            self.connected=btdevice.connected
        
class SoundFile:
    "Holder for sound files"
    def __init__(self,file):
        self.file=file

    def __str__(self):
        apath,afile=os.path.split(self.file)
        aname,ext=os.path.splitext(afile)
        return str(aname)
        
        
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
        
        self.bluetoothlist=ListboxObjects(tab1)
        panel1=Frame(tab1)
        panel1.pack(fill=X)
        button1=Button(panel1,text="Tick",command=self.button1click).pack(side=LEFT)
        button2=Button(panel1,text="Update",command=self.populatebt).pack(side=LEFT)
        Button(panel1,text="Connect", command=self.connect).pack(side=LEFT)
        Button(panel1,text="Disconnect", command=self.disconnect).pack(side=LEFT)
        self.bluetoothlist.pack(expand=1, fill="both")

        tab2=Frame(self.panes)
        self.panes.add(tab2,text="Sounds")
        panel4=Frame(tab2)
        panel4.pack(side=TOP, fill=X)
        button3=Button(panel4,text="Play", command=self.play).pack(side=LEFT)
        button4=Button(panel4,text="Stop", command=self.stop).pack(side=LEFT)
        self.soundlist=ListboxObjects(tab2)
        self.soundlist.pack(expand=1, fill="both")

    def buildmenu(self):
        self.menubar=Menu(self.win)
        filemenu=Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Sounds", command=self.askSounds)
        filemenu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=filemenu)
        self.win.config(menu=self.menubar)

    def busy(self):
        "Set Wait cursor"
        print("Show busy...")
        self.win.config(cursor="watch")
        self.win.update()

    def notbusy(self):
        "Normal cursor"
        print("Show normal")
        self.win.config(cursor="")

    def button1click(self):
        print("Button 1 clicked")
        t=threading.Timer(2,self.ontick)
        t.start()

    def askSounds(self):
        "Ask for sound files."
        print("sound files here")
        myfolder=filedialog.askdirectory(initialdir="~/Music",title = "Select Sound Folder")
        print(myfolder,type(myfolder))
        if (len(myfolder)>0):
            self.loadSounds(myfolder)
        
    def loadSounds(self,folder):
        lb=self.soundlist
        lb.delete(0,END)
        mylist=[]
        for f in glob.iglob(folder+"/*.mp3"):
            ff=SoundFile(f)
            mylist.append(ff)
        mylist.sort(key=str)
        for sf in mylist:
            lb.insert(END,sf)

    def play(self):
        "Play music"
        sf=self.soundlist.selected()
        if (sf==None):
            return
        mixer.quit()
        mixer.init()
        print("Loading ",sf.file)
        mixer.music.load(sf.file)
        print("playing")
        mixer.music.play()

    
    def stop(self):
        "Stop Music"
        mixer.music.stop()
    
    def ontick(self):
        self.sendqueue("print","This is a queued message from ontick")
        
    def quit(self):
        self.win.destroy()

    def populatebt(self):
        "Populate bluetooth list"
        self.devices=self.mgr.device_properties()
        devlist=self.mgr.friendly_names()
        lb=self.bluetoothlist
        orig=self.bluetoothlist.selected()
        lb.delete(0,END)
        for name in sorted(devlist.keys()):
            dev=BtDevice(name,devlist[name])
            prop=self.devices[dev.addr]
            dev.connected=(prop['Connected']==1)
            lb.insert(END,dev)
        if (orig!=None):
            lb.selectObject(orig)
        
    def connect(self):
        dev=self.bluetoothlist.selected()
        if dev==None:
            print("Nothing selected.")
            return
        self.busy()
        try:
            print("Key=",dev)
            print("Addr=",dev.addr)
            self.mgr.connect(dev.addr,"110E")
            self.populatebt()
            self.setpulse()
        finally:
            self.notbusy()

    def setpulse(self):
        with pulsectl.Pulse("Testing") as pulse:
            for sink in pulse.sink_list():
                print(sink)
                print(sink.index,sink.name)
                if sink.name.startswith("bluez_sink"):
                    print("Setting sink.")
                    pulse.sink_default_set(sink)
                    
    def disconnect(self):
        dev=self.bluetoothlist.selected()
        if dev==None:
            print("Nothing selected.")
            return
        self.busy()
        try:
            self.mgr.disconnect(dev.addr)
            self.populatebt()
        finally:
            self.notbusy()
            
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
        
