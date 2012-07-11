from Tkinter import *
from collections import namedtuple
import chainfinder
import numpy as np

CParams = namedtuple("ChainParams",['distance_limit', 'angle_limit', 'min_line_length',
               'anglevar_weight', 'distvar_weight','dist_weight',
               'mode'])


class PlaygroundWindow:
    def __init__(self,master):
        
        self.dragOrigin = []
        frame = Frame(master)
        frame.pack()
        
        
        #algorithm parameters
        self.pathfinding_mode = 1
        
        #variables
        varFrame = Frame(frame,relief=SUNKEN,borderwidth=2,width=2,)
        self.distance_limit=StringVar()
        self.distance_limit.set("3")
        self.angle_limit=StringVar()
        self.angle_limit.set(".9")
        self.min_line_length=StringVar()
        self.min_line_length.set("3")
        self.anglevar_weight=StringVar()
        self.anglevar_weight.set(".1")
        self.distvar_weight=StringVar()
        self.distvar_weight.set(".1")
        self.dist_weight=StringVar()
        self.dist_weight.set("1")
        
        pmode_button_lines = Radiobutton(varFrame,text="Lines",variable=self.pathfinding_mode,value=1).pack(anchor=W)
        pmode_button_chains = Radiobutton(varFrame,text="Chains",variable=self.pathfinding_mode,value=2).pack(anchor=W)
        
        distvar_limit_label = Label(varFrame, text="Distance Limit:", anchor=W).pack()
        self.distvar_limit_field = Entry(varFrame, width=5,textvariable=self.distance_limit).pack()
        
        angle_limit_label = Label(varFrame, text="Angle Limit:", anchor=W).pack()
        self.angle_limit_field = Entry(varFrame, width=5,textvariable=self.angle_limit).pack()
        
        length_limit_label = Label(varFrame, text="Min Length:", anchor=W).pack()
        self.length_limit_field = Entry(varFrame, width=5,textvariable=self.min_line_length).pack()
        
        distance_weight_label = Label(varFrame, text="Distance Weight:", anchor=W).pack()
        self.distance_weight_field = Entry(varFrame, width=5,textvariable=self.dist_weight).pack()
        
        distvar_weight_label = Label(varFrame, text="Distance Var Weight:", anchor=W).pack()
        self.distvar_weight_field = Entry(varFrame, width=5,textvariable=self.distvar_weight).pack()
        
        angle_weight_label = Label(varFrame, text="Angle Weight:", anchor=W).pack()
        self.length_weight_field = Entry(varFrame, width=5,textvariable=self.anglevar_weight).pack()
        
        #viewport
        viewport = Frame(frame,relief=SUNKEN,borderwidth=2,width=500,height=500)
        self.c = Canvas(viewport,width=500,height=500,confine=True)
        self.c.pack()

        varFrame.pack(side=LEFT,padx=2, pady=2)
        self.c.bind("<Button-1>", self.mousedown)
        self.c.bind("<B1-Motion>", self.mousedrag)
        self.c.bind("<ButtonRelease-1>", self.mouseup)
        self.c.bind("<ButtonRelease-2>", self.leftclick)
        self.c.bind("<Double-Button-1>", self.doubleclick)
        viewport.pack(padx=2, pady=2)
        
    def mousedown(self,event):
        self.c.delete("line")
        self.dragOrigin=[event.x,event.y]
        
        
    def mousedrag(self,event):
        self.c.move("current",event.x-self.dragOrigin[0],event.y-self.dragOrigin[1])
        self.dragOrigin = [event.x,event.y]

    def mouseup(self,event):
        self.research()
        
    def leftclick(self,event):
        self.c.delete("current")
        self.research()

    def doubleclick(self,event):
        self.c.create_oval(event.x-10,event.y-10,event.x+10,event.y+10,fill="red")


    def research(self):
        params = CParams(eval(self.distance_limit.get()),
                         eval(self.angle_limit.get()),
                         eval(self.min_line_length.get()),
                         eval(self.anglevar_weight.get()),
                         eval(self.distvar_weight.get()),
                         eval(self.dist_weight.get()),
                         self.pathfinding_mode
                         )
        print params
        self.c.delete("line")
        searchMe = []
        for o in self.c.find_all():
            searchMe.append(PhysicalObject(o,np.array(self.c.coords(o)),0,0))
        results = chainfinder.findChains(searchMe,params.distance_limit,params.angle_limit,params.min_line_length,
                                         params.anglevar_weight,params.distvar_weight,params.dist_weight,params.mode)
        if len(results)>0:
            self.chainViz(results)
            
    def chainViz(self,chains):
        rank = 0
        print chains
        self.c.delete("line")
        
        for c in chains:

            if rank ==0: 
                color = "green"
                weight = 4

            elif rank == 1: 
                color = "orange"
                weight = 2
            elif rank == 2: 
                color = "red"
                weight = 1
            if rank < 3:
                for o in range(len(c[1])-1):
                    linePts = self.c.coords(c[1][o])[0:2]+self.c.coords(c[1][o+1])[0:2]
                    linePts = map(int,linePts)
                    linePts = map(lambda x: x+10,linePts)
                    self.c.create_line(linePts,fill=color,tags="line",width=weight) 
            rank += 1
            
        
        
    
root = Tk(className=" Chainfinder Playground ")

PhysicalObject = namedtuple('physicalObject', ['id', 'position', 'bbmin', 'bbmax'])






app = PlaygroundWindow(root)

root.mainloop()
