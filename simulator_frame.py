# remainning problem : why the demand derives that make the agvs in junc run out?
import wx
import wx.lib.agw.shapedbutton as SB
import os
import numpy as np
import copy
import json
import sys, os, time
import threading
import random
from junction_model import junction_btn
from entrance_model import entrance_btn
from main_window import the_map_window

points = []
nums = []

class Simulator_frame(wx.Frame):
    def __init__(self, parent, m=6, n=6, id=wx.ID_ANY, title="",
                pos=wx.DefaultPosition, size=wx.DefaultSize,
                style=wx.DEFAULT_FRAME_STYLE,                 
                name="Simulator_frame"):  
        
        super(Simulator_frame, self).__init__(parent, id, title,
                                     pos, size, style, name)

        # Attributes
        self.m = m #num of horizontal lines
        self.n = n #num of vertival lines
        self.noj = 2*m*n - m - n
        self.rythmn = 2
        
        self.is_start = False
        self.t_start = None
        self.pausing_t_start = None
        self.pausing_time = 0
        self.next_flag = False
        self.next_t_start = None
        self.counting = -1

        block_scale = 100
        road_scale = 1/12
        self.size = ((n+2)*block_scale,(m+2)*block_scale)
        self.blocksize = (self.size[0]/(n+2),self.size[1]/(m+2))
        self.roadwidth = self.blocksize[0]*road_scale

        self.juncs = []
        #[x,y]
        for j in range(m):
            for i in range(n-1):
                self.juncs.append([i+0.5, j])
        for i in range(n):
            for j in range(m-1):
                self.juncs.append([i, j+0.5])
        self.locations = self.get_locations(self.m,self.n,self.noj)

        # junction2block
        self.junc2block = {}
        blocknum0 = m-1
        blocknum1 = n-1
        for i in range(blocknum0):
            for j in range(blocknum1):
                decision = [0,0,0,0]
                if i == (blocknum0-1)/2 and j == (blocknum1-1)/2:
                    decision = [1,1,1,1]
                elif i == (blocknum0-1)/2 and j < (blocknum1-1)/2:
                    decision = [1,1,1,0]
                elif i == (blocknum0-1)/2 and j > (blocknum1-1)/2:
                    decision = [1,1,0,1]
                elif i < (blocknum0-1)/2 and j == (blocknum1-1)/2:
                    decision = [1,0,1,1] 
                elif i > (blocknum0-1)/2 and j == (blocknum1-1)/2:             
                    decision = [0,1,1,1] 
                elif i < (blocknum0-1)/2 and j < (blocknum1-1)/2:
                    decision = [1,0,1,0]      
                elif i > (blocknum0-1)/2 and j < (blocknum1-1)/2:
                    decision = [0,1,1,0]    
                elif i > (blocknum0-1)/2 and j > (blocknum1-1)/2:
                    decision = [0,1,0,1]  
                elif i < (blocknum0-1)/2 and j > (blocknum1-1)/2:
                    decision = [1,0,0,1]    

                if decision[0] == 1:
                    self.junc2block[i*(n-1)+j] = [i,j]                   #down
                if decision[1] == 1:
                    self.junc2block[(i+1)*(n-1)+j] = [i,j]               #up
                if decision[2] == 1:
                    self.junc2block[m*(n-1) + j*(m-1)+i] = [i,j]         #left
                if decision[3] == 1:
                    self.junc2block[m*(n-1) + (j+1)*(m-1)+i] = [i,j]     #right
        

        # Controls
        self.map = the_map_window(self,self.size, self.m, self.n, self.juncs)

        self.panel = wx.Panel(self)

        self.btn1 = wx.Button(self.panel, -1, label = 'load')
        self.btn2 = wx.Button(self.panel, -1, label = 'play')
        self.btn2.Enabled = False
        self.btn3 = wx.Button(self.panel, -1, label = 'pause')
        self.btn4 = wx.Button(self.panel, -1, label = 'resume')       
        self.btn5 = wx.Button(self.panel, -1, label = 'next rhythm')
        self.btn3.Enable(False)
        self.btn4.Enable(False)
        self.btn5.Enable(False)
        self.rate_label = wx.StaticText(self.panel, -1, "time rate: ",size = [70,-1])
        self.blank_label = wx.StaticText(self.panel, -1, " ",size = [100,-1])
        self.rate_sc = wx.SpinCtrl(self.panel, -1, "", min = 1, max = 50, initial = 5, size = [30,-1])
        self.rate_slider = wx.Slider(self.panel, -1, 5, 1, 50, size=(100, -1),
            style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_MIN_MAX_LABELS)
        self.rate_slider.SetTickFreq(5)

        self.gauge = wx.Gauge(self, -1, 100)
        self.gauge.SetBezelFace(3)
        self.gauge.SetShadowWidth(3)

        # block buttons
        img1 = wx.Image(name="mate\junc.png", type = wx.BITMAP_TYPE_PNG)
        self.junction_blocks = []
        change1 = 1-3*road_scale
        change2 = 0.5 + (1-change1)/2
        img2 = img1.Scale(change1*self.blocksize[0],change1*self.blocksize[1])
        self.junc_appe = wx.Bitmap(img2)
        self.junc_appe
        for i in range(self.m-1):
            self.junction_blocks.append([])
            for j in range(self.n-1):
                b = junction_btn(self.map, -1, bitmap = self.junc_appe, pos = ((1+change2+j)*self.blocksize[0],(self.m-i-1+change2)*self.blocksize[1]), 
                    size = (change1*self.blocksize[0],change1*self.blocksize[1]), order = [i,j])
                b.SetUseFocusIndicator(False)
                b.Setnum1Data(100)
                b.Setnum2Data(20)
                self.Bind(wx.EVT_BUTTON, self.watching_junction, b)
                self.junction_blocks[i].append(b)
        
        # entrance buttons
        self.entrance2block = {}
        self.entr_appe = wx.Bitmap(name="mate\entrance.png", type = wx.BITMAP_TYPE_PNG)
        self.entrance_blocks = []
        i = 0
        self.entrance_blocks.append([])
        for j in range(self.m):
            if np.mod(j,2) == 0:
                b = entrance_btn(self.map, -1, bitmap = self.entr_appe, pos = (0,(self.m-0.9-j)*self.blocksize[1]), 
                    size = (self.blocksize[0],1.8*self.blocksize[1]), order = [i,j])
                self.entrance2block[j] = [i,j]
                self.entrance2block[j+1+self.m+self.n] = [i,j]
            else:
                b = entrance_btn(self.map, -1, bitmap = self.entr_appe, pos = ((self.n+1)*self.blocksize[0],(self.m+0.1-j)*self.blocksize[1]), 
                    size = (self.blocksize[0],1.8*self.blocksize[1]), order = [i,j])
                self.entrance2block[j] = [i,j]
                self.entrance2block[j-1+self.m+self.n] = [i,j]
            b.SetUseFocusIndicator(False)
            b.Setnum1Data(0)
            b.Setnum2Data(40)
            self.Bind(wx.EVT_BUTTON, self.watching_entrance, b)
            self.entrance_blocks[i].append(b)
        i = 1
        self.entrance_blocks.append([])
        for j in range(self.n):    
            if np.mod(j,2) == 0:
                b = entrance_btn(self.map, -1, bitmap = self.entr_appe, pos = ((1.1+j)*self.blocksize[0],0), 
                    size = (1.8*self.blocksize[0],self.blocksize[1]), order = [i,j])
                self.entrance2block[self.m + j] = [i,j]
                self.entrance2block[j+1+2*self.m+self.n] = [i,j]
            else:
                b = entrance_btn(self.map, -1, bitmap = self.entr_appe, pos = ((0.1+j)*self.blocksize[0],(self.m+1)*self.blocksize[1]), 
                    size = (1.8*self.blocksize[0],self.blocksize[1]), order = [i,j])
                self.entrance2block[self.m + j] = [i,j]
                self.entrance2block[j-1+2*self.m+self.n] = [i,j]
            b.SetUseFocusIndicator(False)
            b.Setnum1Data(0)
            b.Setnum2Data(40)
            self.Bind(wx.EVT_BUTTON, self.watching_entrance, b)
            self.entrance_blocks[i].append(b)
        

        # layout
        time_rate_box = wx.BoxSizer(wx.HORIZONTAL)
        time_rate_box.Add(self.rate_label,1, wx.EXPAND)
        time_rate_box.Add(self.rate_sc,1, wx.EXPAND)

        toolarea = wx.BoxSizer(wx.VERTICAL)
        toolarea.Add(self.btn1, 0, wx.EXPAND)
        toolarea.Add(self.btn2, 0, wx.EXPAND)
        toolarea.Add(self.btn3, 0, wx.EXPAND)
        toolarea.Add(self.btn4, 0, wx.EXPAND)
        toolarea.Add(self.btn5, 0, wx.EXPAND)
        toolarea.Add(self.blank_label, 0, wx.EXPAND)
        toolarea.Add(time_rate_box, 0, wx.EXPAND)
        toolarea.Add(self.rate_slider, 0, wx.EXPAND)
        
        self.panel.SetSizer(toolarea)   
        toolarea.Fit(self.panel)

        working_area = wx.BoxSizer(wx.VERTICAL)
        working_area.Add(self.map, 0, wx.EXPAND)
        working_area.Add(self.gauge, 1, wx.EXPAND)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.panel, 0, wx.EXPAND)
        box.Add(working_area, 0, wx.EXPAND)
        self.SetSizer(box)
        # box.Fit(self)
        print(self.GetSize())
        
        self.initStatusBar()

        # Event Handlers 
        self.Bind(wx.EVT_BUTTON, self.loading, self.btn1)
        self.Bind(wx.EVT_BUTTON, self.playing, self.btn2)
        self.Bind(wx.EVT_BUTTON, self.pausing, self.btn3)
        self.Bind(wx.EVT_BUTTON, self.resuming, self.btn4)
        self.Bind(wx.EVT_BUTTON, self.go_next_rhy, self.btn5)
        self.Bind(wx.EVT_SCROLL_CHANGED, self.Change_rate_slider, self.rate_slider)
        self.Bind(wx.EVT_SPINCTRL, self.Change_rate_sc, self.rate_sc)

        thread_sw = threading.Thread(target=self.StopWatchThread)
        thread_sw.setDaemon(True)
        thread_sw.start()
    
    def initStatusBar(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(3)
        self.statusbar.SetStatusWidths([-1, -2, -3])
        self.statusbar.SetStatusText("No data" , 0)

    def Change_rate_slider(self, event): 
        r = self.rate_slider.GetValue()
        self.rate_sc.SetValue(r)
        self.accelarate_r = r
    
    def Change_rate_sc(self, event): 
        r = self.rate_sc.GetValue()
        self.rate_slider.SetValue(r)
        self.accelarate_r = r

    #get the location of each node
    def get_locations(self,m,n,noj):
        num = 2*m + 2*n + noj + 4*m*n
        locs = []
        for i in range(m):
            if np.mod(i,2) == 0:
                locs.append([self.blocksize[0],self.size[1] - (i+1.5)*self.blocksize[1]])
            else:
                locs.append([self.size[0] - self.blocksize[0],self.size[1] - (i+1.5)*self.blocksize[1]])
        for i in range(n):
            if np.mod(i,2) == 0:
                locs.append([(i+1.5)*self.blocksize[0],self.blocksize[1]])
            else:
                locs.append([(i+1.5)*self.blocksize[0],self.size[1] - self.blocksize[1]])
        for i in range(m):
            if np.mod(i,2) == 1:
                locs.append([self.blocksize[0]/2,self.size[1] - (i+1.5)*self.blocksize[1]])
            else:
                locs.append([self.size[0] - self.blocksize[0]/2,self.size[1] - (i+1.5)*self.blocksize[1]])
        for i in range(n):
            if np.mod(i,2) == 1:
                locs.append([(i+1.5)*self.blocksize[0],self.blocksize[1]/2])
            else:
                locs.append([(i+1.5)*self.blocksize[0],self.size[1] - self.blocksize[1]/2])
        for i in range(noj):
            junc_loc = self.juncs[i]
            locs.append([(1.5+junc_loc[0])*self.blocksize[0],self.size[1] - (1.5+junc_loc[1])*self.blocksize[1]])
        
        offset0 = [(-0.25,0),(0,0.25),(0.25,0),(0,-0.25)]
        offset1 = [(-0.25,0),(0,-0.25),(0.25,0),(0,0.25)]
        offset2 = [(0.25,0),(0,0.25),(-0.25,0),(0,-0.25)]
        offset3 = [(0.25,0),(0,-0.25),(-0.25,0),(0,0.25)] 
        for i in range(4*m*n):
            turning = np.floor(i/4)
            order = np.mod(i,4)
            turn_loc = [np.floor(turning/n),np.mod(turning,n)]
            if np.mod(turn_loc[0],2) == 0 and np.mod(turn_loc[1],2) == 0:
                locs.append([(1.5+turn_loc[1]+offset0[order][0])*self.blocksize[0],self.size[1] - (1.5+turn_loc[0]+offset0[order][1])*self.blocksize[1]])
            elif np.mod(turn_loc[0],2) == 0 and np.mod(turn_loc[1],2) == 1:
                locs.append([(1.5+turn_loc[1]+offset1[order][0])*self.blocksize[0],self.size[1] - (1.5+turn_loc[0]+offset1[order][1])*self.blocksize[1]])
            elif np.mod(turn_loc[0],2) == 1 and np.mod(turn_loc[1],2) == 0:
                locs.append([(1.5+turn_loc[1]+offset2[order][0])*self.blocksize[0],self.size[1] - (1.5+turn_loc[0]+offset2[order][1])*self.blocksize[1]])
            elif np.mod(turn_loc[0],2) == 1 and np.mod(turn_loc[1],2) == 1:
                locs.append([(1.5+turn_loc[1]+offset3[order][0])*self.blocksize[0],self.size[1] - (1.5+turn_loc[0]+offset3[order][1])*self.blocksize[1]])
        return locs

    # load simulation result
    def loading(self, event):
        print("press btn1")

        self.res=[]
        with open("./res.json",'r',encoding='utf-8') as json_file: 
            self.res=json.load(json_file)
        data={}
        with open("./data.json",'r',encoding='utf-8') as json_file: 
            data=json.load(json_file)
        self.pre_matrix = data['pre']
        self.dis_matrix = data['dis']

        self.btn2.Enabled = True
        self.btn3.Show(True)
        self.btn4.Show(True)
        wx.MessageBox('Done!')
        self.statusbar.SetStatusText("Loading success" , 0)
        
    # play simulation 
    def playing(self, event):
        print("press btn2")
        self.accelarate_r = 5
        self.completemission = 0
        self.is_start = True
        self.reload = True
        self.t_start= time.time()
        self.btn3.Enable(True)
        self.btn4.Enable(False)
        self.btn5.Enable(False)
        self.statusbar.SetStatusText("Playing" , 0)
        self.statusbar.SetStatusText("Complete mission: %d" % self.completemission, 2)
    
    # pause and resume
    def pausing(self, event):
        print("press btn3")
        self.btn3.Enable(False)
        self.btn4.Enable(True)
        self.btn5.Enable(True)

        self.pausing_t_start = time.time()
        self.is_start = False
        self.statusbar.SetStatusText("Pausing" , 0)

    
    def resuming(self, event):
        print("press btn4")
        self.btn4.Enable(False)
        self.btn3.Enable(True)
        self.btn5.Enable(False)

        self.pausing_time = time.time() - self.pausing_t_start
        self.pausing_t_start = None
        self.t_start= self.t_start + self.pausing_time
        self.pausing_time = 0
        self.is_start = True
        self.statusbar.SetStatusText("Playing" , 0)
    
    # go to next rhythm, able when paused
    def go_next_rhy(self, event):
        print("press btn5")

        self.pausing_time = time.time() - self.pausing_t_start
        self.pausing_t_start = None
        self.t_start= self.t_start + self.pausing_time
        self.pausing_time = 0
        self.is_start = True
        self.next_flag = True
        self.statusbar.SetStatusText("Next rhythm" , 0)

    # press at junctions
    def watching_junction(self, event):
        theid = event.GetId()
        item = self.FindWindowById(theid)
        m,n = item.get_order()
        print("press at junction (%d,%d)" % (m,n))
    
    # press at entrances
    def watching_entrance(self, event):
        theid = event.GetId()
        item = self.FindWindowById(theid)
        m,n = item.get_order()
        print("press at entrance (%d,%d)" % (m,n))

    # simulation player
    def StopWatchThread(self):
        '''线程函数'''
        global points
        global nums
        # points = [[28,33,10,self.locations[28],35]]

        while True:
            if self.is_start:
                if self.reload:
                    wave = 0
                    wave_flag = [False for i in range(len(self.res))]
                    timer1 = 0
                    points = []
                    nums = []
                    self.reload = False
                current_running_t = self.accelarate_r*(time.time() - self.t_start) # scaling simulation time

                self.statusbar.SetStatusText("Operating time: %d sec %d min %d hour" %(np.mod(current_running_t,60),np.floor(np.mod(current_running_t,3600)/60),
                    np.floor(current_running_t/3600)) , 1)
                self.counting = int(current_running_t) 
                pre_wave = wave
                wave = int(np.floor(self.counting/self.rythmn))
                timer1 = np.mod(self.counting,self.rythmn)

                self.set_gauge(wave/len(self.res)*100)
                
                if self.next_flag: # Next function
                    if wave != pre_wave:
                        self.pausing_t_start = time.time()
                        self.is_start = False
                        self.next_flag = False
                
                new_points = []
                for item in points:  
                # [starting_node, ending_node, starting_time, point_location, lifetime, point_flags]
                # [0            , 1          , 2            , 3,            , 4       , 5     ]

                    moving_time = self.counting - item[2]

                    # unit arrives, removed
                    if item[4] <= (self.counting - item[2]):
                        if item[1] >= 2*(self.m+self.n):
                            block_loc = self.junc2block[item[1] - 2*self.m - 2*self.n]
                            wx.CallAfter(self.updating_infos_in_juncbtn,0, 1, block_loc)
                            self.completemission = self.completemission + 1
                            self.statusbar.SetStatusText("Complete mission: %d" % self.completemission, 2)
                        elif item[1] >= (self.m+self.n):
                            block_loc = self.entrance2block[item[1]]
                            wx.CallAfter(self.updating_infos_in_entrbtn,1, 1, block_loc)
                            self.completemission = self.completemission + 1
                            self.statusbar.SetStatusText("Complete mission: %d" % self.completemission, 2)
                        continue
                    
                    # unit is on its way
                    if moving_time > 0:
                        if item[1] < 2*self.m + 2*self.n or (item[2] + item[4] - self.counting) > 5:
                            new_flags = copy.copy(item[5])
                            loc0 = []
                            loc1 = []
                            pre_point = item[1]
                            timing = float(self.dis_matrix[item[0]][pre_point])
                            while True:
                                loc1 = self.locations[pre_point]
                                next_timing = timing
                                pre_point = int(self.pre_matrix[item[0]][pre_point])
                                timing = float(self.dis_matrix[item[0]][pre_point])
                                if timing <= moving_time:
                                    loc0 = self.locations[pre_point] 
                                    if (next_timing - timing) == 10:    # unit is turning
                                        order = pre_point - 2*self.m - 2*self.n-self.noj
                                        x1 = np.mod(order,4)
                                        x2 = np.floor(order/(4*self.n))
                                        x3 = np.floor(order/4)
                                        direction = np.mod(x1+x2+x3,2)  #0 right; 1 left
                                    break

                            new_location = [loc0[0] + (loc1[0]-loc0[0])*(moving_time-timing)/(next_timing-timing),loc0[1] + (loc1[1]-loc0[1])*(moving_time-timing)/(next_timing-timing)]

                            rate = ((moving_time-timing)/(next_timing-timing)-0.5)
                            thre = 0.2
                            change = [loc1[0]-loc0[0],loc1[1]-loc0[1]]
                            # turning location adjustment
                            if change[0] != 0 and change[1] != 0 and rate < thre and rate >=0 :
                                new_location = [loc0[0] + (loc1[0]-loc0[0])*(0.5+thre),loc0[1] + (loc1[1]-loc0[1])*(0.5+thre)]
                                if (change[0]*change[1] > 0 and direction == 1) or (change[0]*change[1] < 0 and direction == 0):
                                    new_location[0] = new_location[0] - 2*(thre-rate)*change[0]
                                else:
                                    new_location[1] = new_location[1] - 2*(thre-rate)*change[1]
                            elif change[0] != 0 and change[1] != 0 and rate < 0 and rate > -thre:
                                new_location = [loc0[0] + (loc1[0]-loc0[0])*(0.5-thre),loc0[1] + (loc1[1]-loc0[1])*(0.5-thre)]
                                if (change[0]*change[1] > 0 and direction == 1) or (change[0]*change[1] < 0 and direction == 0):
                                    new_location[1] = new_location[1] + 2*(thre+rate)*change[1]
                                else:
                                    new_location[0] = new_location[0] + 2*(thre+rate)*change[0]

                        
                        # get into junction        
                        elif (item[2] + item[4] - self.counting) <= 5:
                            new_flags = copy.copy(item[5])
                            surplus = (item[2] + item[4] - self.counting)
                            block_loc = self.junc2block[item[1] - 2*self.m - 2*self.n]
                            exitan = [(2+block_loc[1])*self.blocksize[0],(self.m-block_loc[0])*self.blocksize[1]]
                            junc_loc = self.locations[item[1]]
                            new_location = [exitan[0]*(5-surplus)/5+junc_loc[0]*surplus/5,
                                exitan[1]*(5-surplus)/5+junc_loc[1]*surplus/5]
                            new_flags[1] = False

                        new_points.append([item[0],item[1],item[2],new_location,item[4], new_flags])

                    # get out of junction , waiting to move
                    elif item[0] >= 2*self.m+2*self.n:
                        block_loc = self.junc2block[item[0] - 2*self.m - 2*self.n]
                        exitan = [(2+block_loc[1])*self.blocksize[0],(self.m-block_loc[0])*self.blocksize[1]]
                        junc_loc = self.locations[item[0]]
                        new_location = [exitan[0]*(-moving_time)/self.rythmn + junc_loc[0]*(1+moving_time/self.rythmn),
                            exitan[1]*(-moving_time)/self.rythmn + junc_loc[1]*(1+moving_time/self.rythmn)]
                        
                        new_flags = copy.copy(item[5])
                        if moving_time == 0 and not new_flags[1]:
                            wx.CallAfter(self.updating_infos_in_juncbtn,-1,-1, block_loc)
                            new_flags[1] = True

                        new_points.append([item[0],item[1],item[2],new_location,item[4], new_flags]) 
                    
                    # get out of entrance , waiting to move
                    else:
                        block_loc = self.entrance2block[item[0]]
                        new_location = copy.copy(item[3])

                        new_flags = copy.copy(item[5])
                        if moving_time == 0 and not new_flags[1]:
                            wx.CallAfter(self.updating_infos_in_entrbtn,0,-1, block_loc)
                            new_flags[1] = True

                        new_points.append([item[0],item[1],item[2],new_location,item[4], new_flags])
                        
                points = copy.copy(new_points)

                # refresh demands and permissions at new rythmn arrival
                if timer1 == 0:
                    if not wave_flag[wave]:
                        wave_flag[wave] = True
                        nums = []
                        self.temp_res = self.res[wave]
                        for item in self.temp_res:
                            temp_location = [int(item[0]),int(item[1]) + self.m + self.n]
                            if temp_location[0] >= self.m+self.n:
                                temp_location[0] = temp_location[0] + self.m + self.n
                            nums.append([self.locations[temp_location[0]][0],self.locations[temp_location[0]][1],int(item[2])])
                            lifetime = float(self.dis_matrix[temp_location[0]][temp_location[1]])
                            if temp_location[1] >= 2*self.m+2*self.n:
                                lifetime = lifetime + 5
                            for i in range(int(item[3])):
                                point_flags = [int(item[4]),False] # loaded, on_road
                                points.append([temp_location[0],temp_location[1],(wave+1)*self.rythmn,self.locations[temp_location[0]],lifetime,point_flags])
                        
                    
                wx.CallAfter(self.updating_infos_in_map)
            time.sleep(0.03)
    
    def updating_infos_in_map(self):
        self.map.SetpointsData(points)
        self.map.SetnumsData(nums)

    def updating_infos_in_juncbtn(self,num1,num2,order):
        self.junction_blocks[order[0]][order[1]].Changenum1Data(num1)
        self.junction_blocks[order[0]][order[1]].Changenum2Data(num2)
    
    def updating_infos_in_entrbtn(self,num1,num2,order):
        self.entrance_blocks[order[0]][order[1]].Changenum1Data(num1)
        self.entrance_blocks[order[0]][order[1]].Changenum2Data(num2)
    
    def set_gauge(self, r):
        self.gauge.SetValue(r)

'''if __name__ == "__main__":
    m = 6
    n = 6
    points = []
    nums = []

    app = wx.App(False)
    frame = Simulator_frame(None,size=(960,880),m=m,n=n, title='simulator')
    frame.Show()
    app.MainLoop()'''

m = 6
n = 6
points = []
nums = []

app = wx.App(False)
frame = Simulator_frame(None,size=(960,880),m=m,n=n, title='simulator')
frame.Show()
app.MainLoop()