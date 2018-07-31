from tkinter import *

class ListboxObjects(Listbox):
    "Listbox with objects"

    def __init__(self, master=None, **options):
        super().__init__(master,options)
        self.objectlist=[]
       
    def insert(self, index, *elements):
        for obj in elements:
            super().insert(index,str(obj))
            if (index==END):
                self.objectlist.append(obj)
            else:
                self.objectlist.insert(index,obj)
                index+=1
            
    def delete(self, first, last=None):
        super().delete(first,last)
        if (last==END):
            last=len(self.objectlist)
        del self.objectlist[first:last]

    def selected(self):
        sel=self.curselection()
        if (len(sel)<1):
            return None
        return self.objectlist[sel[0]]

    def selectObject(self,obj):
        self.selection_clear(0,END)
        try:
            i=self.objectlist.index(obj)
            self.selection_set(i)
            self.see(i)
        except ValueError:
            pass
        return
    
