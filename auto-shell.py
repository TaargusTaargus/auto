from event import EventController, EventRecorder, ClickEvent, TapEvent
from pymouse import PyMouseEvent
from pykeyboard import PyKeyboardEvent

SHELL_MODE = "shell"
READ_MODE = "read"

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
START/STOP RECORDING = L-Shift
PLAYBACK RECORDING = R-Shift
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

if __name__ == "__main__":
  from sys import argv, exit
  mode = argv[ 1 ]

  if mode == SHELL_MODE:
    keyboard = ShellTapManager()
    print( keyboard.HELP_SHELL_TEXT )
    try:
      keyboard.run()
    except:
      print( "exiting ..." )

  elif mode == READ_MODE:
    controller = EventController()
    controller.load_text_file( argv[ 2 ] )
    controller.run()



