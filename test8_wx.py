# test the event to update ui
# test for mouse event and handler
import wx
ID_CHECK_ITEM = 12345
class TextFrame(wx.Frame):    
    def __init__(self, parent, *args, **kwargs):        
        super(TextFrame, self).__init__(parent,*args, **kwargs)
        # Attributes        
        self.panel = wx.Panel(self)        
        self.txtctrl = wx.TextCtrl(self.panel,value="Hello World",style=wx.TE_MULTILINE)

        # Layout        
        sizer = wx.BoxSizer(wx.HORIZONTAL)        
        sizer.Add(self.txtctrl, 1, wx.EXPAND)        
        self.panel.SetSizer(sizer)        
        self.CreateStatusBar() # For output display

        # Menu        
        menub = wx.MenuBar()        
        editm = wx.Menu()        
        editm.Append(wx.ID_COPY, "Copy\tCtrl+C")        
        editm.Append(wx.ID_CUT, "Cut\tCtrl+X")        
        editm.Append(ID_CHECK_ITEM, "Selection Made?", kind=wx.ITEM_CHECK)        
        menub.Append(editm, "Edit")        
        self.SetMenuBar(menub)

        # Event Handlers        
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateEditMenu)

    def OnUpdateEditMenu(self, event):        
        event_id = event.GetId()        
        sel = self.txtctrl.GetSelection()        
        has_sel = sel[0] != sel[1]        
        if event_id in (wx.ID_COPY, wx.ID_CUT):            
            event.Enable(has_sel)        
        elif event_id == ID_CHECK_ITEM:            
            event.Check(has_sel)        
        else:            
            event.Skip()

class MouseFrame(wx.Frame):    
    def __init__(self, parent, *args, **kwargs):        
        super(MouseFrame, self).__init__(parent, *args, **kwargs)

        # Attributes        
        self.panel = wx.Panel(self)        
        self.btn = wx.Button(self.panel)

        # Event Handlers        
        self.panel.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)        
        self.panel.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)        
        self.panel.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)        
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)

    def OnEnter(self, event):        
        """Called when the mouse enters the panel"""        
        self.btn.SetForegroundColour(wx.BLACK)
        self.btn.SetLabel("EVT_ENTER_WINDOW")        
        self.btn.SetInitialSize()
    
    def OnLeave(self, event):        
        """Called when the mouse leaves the panel"""        
        self.btn.SetLabel("EVT_LEAVE_WINDOW")        
        self.btn.SetForegroundColour(wx.RED)

    def OnLeftDown(self, event):        
        """Called for left down clicks on the Panel"""        
        self.btn.SetLabel("EVT_LEFT_DOWN")            
     
    def OnLeftUp(self, event):        
        """Called for left clicks on the Panel"""        
        position = event.GetPosition()        
        self.btn.SetLabel("EVT_LEFT_UP")        
        # Move the button        
        self.btn.SetPosition(position - (25, 25))

app = wx.App()
fram = TextFrame(None)
fram.Show()
app.MainLoop()