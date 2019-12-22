# test the propagation of events
import wx
ID_BUTTON1 = wx.NewId() 
ID_BUTTON2 = wx.NewId()
class MyApp(wx.App):    
    def OnInit(self):        
        self.frame = MyFrame(None, title="Event Propagation")
        self.SetTopWindow(self.frame)        
        self.frame.Show()

        self.Bind(wx.EVT_BUTTON, self.OnButtonApp)

        return True

    def OnButtonApp(self, event):        
        event_id = event.GetId()        
        if event_id == ID_BUTTON1:            
            print("BUTTON ONE Event reached the App Object")

class MyFrame(wx.Frame):    
    def __init__(self, parent, id=wx.ID_ANY, title="",
                pos=wx.DefaultPosition, size=wx.DefaultSize,
                style=wx.DEFAULT_FRAME_STYLE,                 
                name="MyFrame"):        
        
        super(MyFrame, self).__init__(parent, id, title,
                                      pos, size, style, name)
        # Attributes        
        self.panel = MyPanel(self)
        self.btn1 = wx.Button(self.panel, ID_BUTTON1, "Propagates")        
        self.btn2 = wx.Button(self.panel, ID_BUTTON2, "Doesn't Propagate")
        sizer = wx.BoxSizer(wx.HORIZONTAL)        
        sizer.Add(self.btn1, 0, wx.ALL, 10)        
        sizer.Add(self.btn2, 0, wx.ALL, 10)        
        self.panel.SetSizer(sizer) 
        self.Bind(wx.EVT_BUTTON, self.OnButtonFrame)

    def OnButtonFrame(self, event):        
        event_id = event.GetId()        
        if event_id == ID_BUTTON1:            
            print("BUTTON ONE event reached the Frame")
            event.Skip()        
        elif event_id == ID_BUTTON2:            
            print("BUTTON TWO event reached the Frame")  

class MyPanel(wx.Panel):    
    def __init__(self, parent):        
        super(MyPanel, self).__init__(parent)

        self.Bind(wx.EVT_BUTTON, self.OnPanelButton)

    def OnPanelButton(self, event):        
        event_id = event.GetId()        
        if event_id == ID_BUTTON1:            
            print("BUTTON ONE event reached the Panel")
            event.Skip()        
        elif event_id == ID_BUTTON2:            
            print("BUTTON TWO event reached the Panel")
            # Not skipping the event will cause its             
            # propagation to end here

if __name__ == "__main__":    
    app = MyApp(False)    
    app.MainLoop() 