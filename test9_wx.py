# test for custom event class
# and EventStack #?
import wx
import wx.lib.newevent
import wx.lib.eventStack as eventStack

# Our first custom event 
MyEvent, EVT_MY_EVENT = wx.lib.newevent.NewCommandEvent()

'''
event = MyEvent(eventID) 
wx.PostEvent(myFrame, event) | myFrame.GetEventHandler().ProcessEvent(event)
'''

# Our second custom event that transfer parameters
myEVT_TIME_EVENT = wx.NewEventType() 
EVT_MY_TIME_EVENT = wx.PyEventBinder(myEVT_TIME_EVENT, 1) 

class MyTimeEvent(wx.PyCommandEvent):    
    def __init__(self, id=0, time="12:00:00"):        
        evttype = myEVT_TIME_EVENT        
        super(MyTimeEvent, self).__init__(evttype, id)

        # Attributes        
        self.time = time

    def GetTime(self):        
        return self.time

############################################

class EventMgrApp(wx.App, eventStack.AppEventHandlerMixin):    
    """Application object base class that    
    event handler managment.    
    """    
    def __init__(self, *args, **kwargs):        
        eventStack.AppEventHandlerMixin.__init__(self)        
        wx.App.__init__(self, *args, **kwargs)

class EventMgrFrame(wx.Frame):    
    """Frame base class that provides event    
    handler managment.    
    """    
    def __init__(self, parent, *args, **kwargs):        
        super(EventMgrFrame, self).__init__(parent, *args, **kwargs)
        # Attributes        
        self._menu_handlers = []        
        self._ui_handlers = []
        # Event Handlers        
        self.Bind(wx.EVT_ACTIVATE, self._OnActivate)

    def _OnActivate(self, event):        
        """Pushes/Pops event handlers"""        
        app = wx.GetApp()        
        active = event.GetActive()        
        if active: 
            mode = wx.UPDATE_UI_PROCESS_SPECIFIED            
            wx.UpdateUIEvent.SetMode(mode)            
            self.SetExtraStyle(wx.WS_EX_PROCESS_UI_UPDATES)

            # Push this instances handlers            
            for handler in self._menu_handlers:                
                app.AddHandlerForID(*handler)
            for handler in self._ui_handlers:                
                app.AddUIHandlerForID(*handler)        
        else:            
            self.SetExtraStyle(0)            
            wx.UpdateUIEvent.SetMode(wx.UPDATE_UI_PROCESS_ALL)            
            # Pop this instances handlers            
            for handler in self._menu_handlers:                
                app.RemoveHandlerForID(handler[0])
            for handler in self._ui_handlers:                
                app.RemoveUIHandlerForID(handler[0])

    def RegisterMenuHandler(self, event_id, handler):        
        """Register a MenuEventHandler        
        @param event_id: MenuItem ID        
        @param handler: Event handler function        
        """        
        self._menu_handlers.append((event_id, handler))

    def RegisterUpdateUIHandler(self, event_id, handler):        
        """Register a controls UpdateUI handler        
        @param event_id: Control ID        
        @param handler: Event handler function        
        """        
        self._ui_handlers.append((event_id, handler)) 
