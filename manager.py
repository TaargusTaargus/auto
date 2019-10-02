from event import ClickEvent, TapEvent, EventController
from pymouse import PyMouseEvent
from pykeyboard import PyKeyboardEvent
from time import time

class EventRecorder:

  def __init__( self ):
    self.tasks = []
    self.last = time()

  
  def record( self, event ):
    now = time()
    self.tasks.append( ( now - self.last if self.tasks else 0, event ) )
    self.last = now


  def save( self, handle ):
    fhandle = open( handle, "w" )
    for time, event in self.tasks:
      fhandle.write( ",".join( [ str( time ), event.to_string() ] ) + "\n" )
    fhandle.close()

  def get_snapshot( self ):
    return list( self.tasks )


class ClickManager( PyMouseEvent ):

  def __init__( self, recorder ):
    PyMouseEvent.__init__( self )
    self.enabled = False
    self.recorder = recorder

  def disable( self ):
    self.enabled = False

  def enable( self ):
    self.enabled = True

  def click( self, x, y, button, pressed ):    
    if pressed and self.enabled:
      self.recorder.record( ClickEvent( x, y, button ) )


class ShellTapManager ( PyKeyboardEvent ):
 
  LOAD = 23 ## tab
  SAVE = 49 ## `
  RECORD = 50 ## R-Shift
  PLAY = 62 ## L-Shift 
 
  HELP_SHELL_TEXT = '''
START/STOP RECORDING = R-Shift
PLAYBACK RECORDING = L-Shift
LOAD RECORDING = Tab
SAVE RECORDING = `
'''


  def __init__( self ):
    PyKeyboardEvent.__init__( self )
    self.record = False
    self.play = True
    self.snapshot = None
    self.mouse = None
    self.control = None
    self.recorder = EventRecorder()


  def tap( self, code, char, press ):
    if not self.record:
      if code == self.SAVE and not press:
        self.recorder.save( "recording.auto" )

      if code == self.LOAD and not press:
        self.control = EventController()
        self.control.load_auto_file( "recording.auto" )

      if code == self.PLAY and not press and self.control:
        if self.play:
          self.control.enable()
          self.control.start()
          self.play = False
        else: 
          self.control.disable()
          self.control = EventController( self.control.scheme )
          self.play = True

    else:
      self.recorder.record( TapEvent( char, int( press ) ) ) 


    if code == self.RECORD and not press:
      self.record = not self.record
      if self.record:
        self.mouse = ClickManager( self.recorder )
        self.mouse.start()
        self.mouse.enable()
      else:
        self.snapshot = self.recorder.get_snapshot()
        self.control = EventController( self.snapshot )


class GuiTapManager ( PyKeyboardEvent ):

  def __init__( self, recorder, stop_thread, config = { "stop": { "key": "~", "code": 49 } } ):
    PyKeyboardEvent.__init__( self )
    self.config = config
    self.enabled = False
    self.recorder = recorder
    self.stop_thread = stop_thread

  def disable( self ):
    self.enabled = False

  def enable( self ):
    self.enabled = True

  def tap( self, code, char, press ):
    if code == self.config[ "stop" ][ "code" ]:
        self.stop_thread.start()
        self.enabled = False
    
    if self.enabled:
      self.recorder.record( TapEvent( char, int( press ) ) )

