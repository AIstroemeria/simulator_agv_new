import wx
import os

class MDIFrame(wx.MDIParentFrame):
   def __init__(self):
      wx.MDIParentFrame.__init__(self, None, -1, "MDI Parent", size = (600,400))
      menu = wx.Menu()
      menu.Append(5000, "&New Window")
      menu.Append(5001, "&Exit")
      menubar = wx.MenuBar()
      menubar.Append(menu, "&File")

      self.SetMenuBar(menubar)
      self.Bind(wx.EVT_MENU, self.OnNewWindow, id = 5000)
      self.Bind(wx.EVT_MENU, self.OnExit, id = 5001)

   def OnExit(self, evt):
      self.Close(True)  

   def OnNewWindow(self, evt):
      self.OnOpenFile()
      win = wx.MDIChildFrame(self, -1, "Child Window")
      win.Show(True)

   def OnOpenFile(self):
        wildcard = 'All files(*.*)|*.*'
        dialog = wx.FileDialog(None,'select',os.getcwd(),'',wildcard,wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.FileName=dialog.GetPath()
            dialog.Destroy

app = wx.App()

frame = MDIFrame()
frame.Show()

app.MainLoop()
