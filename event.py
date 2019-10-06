from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, KeyCode, Controller as KeyboardController
from pyautogui import typewrite
from time import sleep, time
from threading import Thread

class ClickEvent:

  KEYWORD = "click"
  MOUSE_LEFT = 1
  MOUSE_RIGHT = 2

  def __init__( self, x, y, button=1 ):
    self.button = button
    self.controller = MouseController()
    self.x = x
    self.y = y

  def consume( self ):
    self.controller.position = ( self.x, self.y )
    self.controller.move( 0, 0 )
    self.controller.press( Button.right if self.button == self.MOUSE_RIGHT else Button.left )
    self.controller.release( Button.right if self.button == self.MOUSE_RIGHT else Button.left )

  def to_string( self ):
    return ",".join( [ self.KEYWORD, str( self.x ), str( self.y ), str( self.button ) ] )


class StringEvent:

  def __init__( self, string ):
    self.string = string

  def consume( self ):
    typewrite( self.string )

  def to_string( self ):
    return self.string


class TapEvent:

  KEYWORD = "tap"
  KEY_DOWN = 1
  KEY_UP = 0

  def __init__( self, keycode, motion=0 ):
    self.controller = KeyboardController()
    self.keycode = keycode
    self.motion = motion

  def consume( self ):
    if self.motion == self.KEY_DOWN:
      self.controller.press( self.keycode )
    else:
      self.controller.release( self.keycode ) 

  def to_string( self ):
    keycode = self.keycode
    if isinstance( keycode, Key ):
      keycode = str( keycode )
    elif isinstance( keycode, KeyCode ):
      keycode = keycode.char      
    return ",".join( [ self.KEYWORD, str( keycode ), str( self.motion ) ] )


class EventController ( Thread ):
  
  def __init__( self, tasks=[] ):
    Thread.__init__( self )
    self.tasks = tasks
    self.counter = 0
    self.enabled = False


  def run( self ):
    if not len( self.tasks ):
      return

    while self.enabled:
      time, event = self.tasks[ self.counter ]
      sleep( time )
      event.consume()
      self.counter = ( self.counter + 1 ) % len( self.tasks )

  def disable( self ):
    self.enabled = False

  def enable( self ):
    self.enabled = True

  def load_auto_file( self, handle ): 
    self.tasks = []
    fhandle = open( handle, "r" )
    for line in fhandle:
      attr = line.strip().split( "," )

      if attr[ 1 ] == ClickEvent.KEYWORD:
        self.tasks.append( ( float( attr[ 0 ] ), ClickEvent( int( attr[ 2 ] ), int( attr[ 3 ] ), int( attr[ 4 ] ) ) ) )
      elif attr[ 1 ] == TapEvent.KEYWORD:
        key = None
        keys = dict( [ ( str( e ), e ) for e in Key ] )
        if attr[ 1 ] in keys.keys():  
          key = keys[ attr[ 1 ] ]
        else:
          try:
            key = KeyCode( attr[ 1 ] )
          except:
            key = None

        if key:
          self.tasks.append( ( float( attr[ 0 ] ), TapEvent( key , int( attr[ 3 ] ) ) ) )

    fhandle.close()

  def load_text_file( self, handle, size=70, interval=10 ):
    self.tasks = []
    string = ""
    tmp = ""
    fire = False
    with open( handle ) as infile:
      for line in infile:
        if not line.strip():
          tmp = string
          string = ""
          fire = True

        string = string + line.strip()
        if len( string ) > 70:
          tmp = string[ :70 ]
          if string[ 69 ] != " " and string[ 70 ] != " ":
            tmp = " ".join( string.split( " " )[ :-1 ] )
            string = string[ len( tmp ): ]
          else:
            string = string[ 70: ]
          fire = True
 
        if fire:
          self.tasks.append( ( interval, StringEvent( tmp ) ) )
          self.tasks.append( ( 0, TapEvent( "Enter", 1 ) ) )
          self.tasks.append( ( 0, TapEvent( "Enter", 0 ) ) )
          fire = False


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
