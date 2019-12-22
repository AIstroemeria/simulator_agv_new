# test the way to show a pic in our app
import wx
import os

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, title="Simulator_AGV")
        self.SetTopWindow(self.frame)
        self.frame.Show()

        return True
        

class MyFrame(wx.Frame):    
    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition, 
                size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, name="MyFrame"):
        super(MyFrame, self).__init__(parent, id, title,
                                          pos, size, style, name)
        # Attributes
        # Create a panel object to ensure it shows well in different platform
        self.panel = wx.Panel(self)
        
        #Setup
        path = os.path.abspath("./icon.png")
        icon = wx.Icon(path, wx.BITMAP_TYPE_PNG)
        self.SetIcon(icon)

        self.btn1 = wx.Button(self.panel, label="Push Me")
        self.btn2 = wx.Button(self.panel, label="push me too")
        sizer = wx.BoxSizer(wx.HORIZONTAL)        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.btn1, 0, wx.ALL, 10)        
        sizer.Add(self.btn2, 0, wx.ALL, 10)        

        img_path = os.path.abspath("./part.png")
        bitmap = wx.Bitmap(img_path, type = wx.BITMAP_TYPE_PNG)
        self.bitmap = wx.StaticBitmap(self.panel, bitmap = bitmap)
        main_sizer.Add(self.bitmap, 1, wx.ALL, 10)
        main_sizer.Add(sizer, 0, wx.ALL, 10)
        self.panel.SetSizer(main_sizer)

        self.Bind(wx.EVT_BUTTON, self.OnButton, self.btn1)        
        self.Bind(wx.EVT_BUTTON,                  
                lambda event:                  
                self.btn1.Enable(not self.btn1.Enabled),                  
                self.btn2)

    def OnButton(self, event):        
        """Called when self.btn1 is clicked"""        
        event_id = event.GetId()        
        event_obj = event.GetEventObject()        
        print("Button 1 Clicked:")        
        print("ID=%d" % event_id)      
        print("object=%s" % event_obj.GetLabel())

if __name__ == "__main__":
        app = MyApp(False)
        app.MainLoop()