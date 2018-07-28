from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import *
from tkinter import messagebox
import bluetooth
import queue

class RpgTalkerGUI:
    """ TKInter front end for RPG Talker
    """
    def __init__(self,win):
        "win=main window"
        self.win=win
        self.buildframe()
        self.input=queue.Queue()
        win.after(100,self.dostuff)

    def buildframe(self):
        self.win.title("RPGTalker GUI")
        label=Label(self.win,text="Paired Devices").pack(fill="x")
        self.bluetoothlist=Listbox(self.win).pack(expand=1, fill="both")
        self.centerwindow()

    def button1click(self):
        print("Button 1 clicked")

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
        
