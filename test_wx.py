# round corner
import wx
 
class RCDialog(wx.Dialog):
    def __init__(self,parent=None,size=wx.DefaultSize):
        wx.Dialog.__init__(self, parent, -1, size=size,
            style=wx.FRAME_SHAPED |
                  wx.SIMPLE_BORDER |
                  wx.FRAME_NO_TASKBAR |
                  wx.STAY_ON_TOP)
 
        self.Centre( wx.BOTH)
 
        # linux平台
        if wx.Platform == "__WXGTK__":
            self.Bind(wx.EVT_WINDOW_CREATE, self.SetBalloonShape)
        else:
            self.SetBalloonShape()
 
 
 
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
 
    def OnLeftDown(self, event):
        pos = event.GetPosition()
        x, y = self.ClientToScreen(event.GetPosition())
        ox, oy = self.GetPosition()
        dx = x - ox
        dy = y - oy
        self.delta = ((dx, dy))
 
    def OnMouseMove(self, event):
        if event.Dragging() and event.LeftIsDown():
            x, y = self.ClientToScreen(event.GetPosition())
            fp = (x - self.delta[0], y - self.delta[1])
            self.Move(fp)
 
    def OnRightUp(self, evt):
        self.Close()
 
    def SetBalloonShape(self, event=None):
        width, height = self.GetSize()
        bmp = wx.EmptyBitmap(width,height)
        dc = wx.BufferedDC(None, bmp)
        dc.SetBackground(wx.Brush(wx.Colour(0,0,0), wx.SOLID))
        dc.Clear()
 
        dc.DrawRoundedRectangle(0, 0, width-1, height-1, 4)
 
        r = wx.Region(bmp, wx.Colour(0,0,0))
        self.hasShape = self.SetShape(r)
 
 
 
 
if __name__ == "__main__":
    app = wx.PySimpleApp()
    dlg = RCDialog(size=(376,282))
    dlg.Show()
    app.MainLoop()