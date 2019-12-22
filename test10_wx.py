# test to paint on screen (make widgets and control)
import os 
import wx

class ImageCanvas(wx.PyPanel):    
    def __init__(self, parent):        
        super(SlideShowPanel, self).__init__(parent)

        # Attributes        
        self.idx = 0 # Current index in image list        
        self.images = list() # list of images found to display

        # Event Handlers        
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def DoGetBestSize(self):        
        """Virtual override for PyPanel"""        
        newsize = wx.Size(0, 0)        
        if len(self.images):            
            imgpath = self.images[self.idx]            
            bmp = wx.Bitmap(imgpath)            
            newsize = bmp.GetSize()            
            newsize = newsize + (20, 20) # some padding        
        else:
            tsize = self.GetTextExtent("No Image!")            
            newsize = tsize + (20, 20)

        # Ensure new size is at least 300x300        
        return wx.Size(max(300, newsize[0]), max(300, newsize[1]))

    def OnPaint(self, event):        
        """Draw the image on to the panel"""        
        dc = wx.PaintDC(self) # Must create a PaintDC

        # Get the working rectangle        
        rect = self.GetClientRect()

        # Setup the DC        
        dc.SetTextForeground(wx.BLACK)

        # Do the drawing        
        if len(self.images):            
            # Draw the current image            
            imgpath = self.images[self.idx]            
            bmp = wx.Bitmap(imgpath)            
            bsize = bmp.GetSize()            
            # Try and center the image            
            # Note: assumes image is smaller than canvas  
            xpos = (rect.width - bsize[0]) / 2            
            ypos = (rect.height - bsize[1]) / 2            
            dc.DrawBitmap(bmp, xpos, ypos)            
            # Draw a label under the image saying what        
            # number in the set it is.            
            imgcount = len(self.images)            
            number = "%d / %d" % (self.idx+1, imgcount)     
            tsize = dc.GetTextExtent(number)            
            xpos = (rect.width - tsize[0]) / 2            
            ypos = ypos + bsize[1] + 5 # 5px below image        
            dc.DrawText(number, xpos, ypos)        
        else:            
            # Display that there are no images            
            font = self.GetFont()            
            font.SetWeight(wx.FONTWEIGHT_BOLD)            
            dc.SetFont(font)            
            dc.DrawLabel("No Images!", rect, wx.ALIGN_CENTER)
    
    def Next(self):        
        """Goto next image"""        
        self.idx += 1        
        if self.idx >= len(self.images):            
            self.idx = 0 # Go back to zero        
        self.Refresh() # Causes a repaint

    def Previous(self):        
        """Goto previous image"""        
        self.idx -= 1        
        if self.idx < 0:            
            self.idx = len(self.images) - 1 # Goto end        
        self.Refresh() # Causes a repaint

    def SetImageDir(self, imgpath):        
        """Set the path to where the images are"""        
        assert os.path.exists(imgpath)        
        # Find all the images in the directory        
        self.images = [ os.path.join(imgpath, img)    
                      for img in os.listdir(imgpath)  
                      if img.lower().endswith('.png') or 
                         img.lower().endswith('.jpg') ]        
        self.idx = 0
