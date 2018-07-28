from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import *
from tkinter import messagebox
import bluetooth
import queue
from dbusmgr import *

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

    def buildframe(self):
        self.win.title("RPGTalker GUI")
        Label(self.win,text="Paired Devices").pack(fill="x")
        self.bluetoothlist=Listbox(self.win)
        self.bluetoothlist.pack(expand=1, fill="both")

    def buildmenu(self):
        self.menubar=Menu(self.win)
        filemenu=Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=filemenu)
        self.win.config(menu=self.menubar)

    def button1click(self):
        print("Button 1 clicked")

    def quit(self):
        self.win.destroy()

    def populatebt(self):
        "Populate bluetooth list"
        devlist=self.mgr.friendly_names()
        self.devices=devlist
        lb=self.bluetoothlist
        for name in sorted(devlist.keys()):
            lb.insert(END,name)
        
    def dostuff(self):
        print("After called.")
        
    def centerwindow(self):
        "Center window in screen"
        win=self.win
        ws = win.winfo_screenwidth() # width of the screen
        hs = win.winfo_screenheight() # height of the screen
        h = win.winfo_reqheight()
        w = win.winfo_reqwidth()
        x = (ws-w)/2
        y = (hs-h)/2
        win.geometry('%dx%d+%d+%d' % (w, h, x, y))

root=Tk()
app=RpgTalkerGUI(root)
root.mainloop()
        
