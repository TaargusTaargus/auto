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
    self.x = x
    self.y = y

  def consume( self, controller ):
    controller.position = ( self.x, self.y )
    controller.move( 0, 0 )
    controller.press( Button.right if self.button == self.MOUSE_RIGHT else Button.left )
    controller.release( Button.right if self.button == self.MOUSE_RIGHT else Button.left )

  def to_string( self ):
    return ",".join( [ self.KEYWORD, str( self.x ), str( self.y ), str( self.button ) ] )


class StringEvent:

  def __init__( self, string ):
    self.string = string

  def consume( self, controller ):
    for char in self.string:
      keycode = KeyCode.from_char( char )
      controller.press( keycode )
      controller.release( keycode )

  def to_string( self ):
    return self.string


class TapEvent:

  KEYWORD = "tap"
  KEY_DOWN = 1
  KEY_UP = 0

  def __init__( self, keycode, motion=0 ):
    self.keycode = keycode
    self.motion = motion

  def consume( self, controller ):
    if self.motion == self.KEY_DOWN:
      controller.press( self.keycode )
    else:
      controller.release( self.keycode ) 

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

    keyboard = KeyboardController()
    mouse = MouseController()

    while self.enabled:
      time, event = self.tasks[ self.counter ]
      sleep( time )
      if isinstance( event, ClickEvent ):
        event.consume( mouse )
      elif isinstance( event, TapEvent ) or isinstance( event, StringEvent ):
        event.consume( keyboard )
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
        if attr[ 2 ] in keys.keys():
          key = keys[ attr[ 2 ] ]
        else:
          try:
            key = KeyCode.from_char( attr[ 2 ] )
          except:
            key = None

        if key:
          self.tasks.append( ( float( attr[ 0 ] ), TapEvent( key , int( attr[ 3 ] ) ) ) )

    fhandle.close()

  def load_text_file( self, handle, size=70, interval=6 ):
    self.tasks = []
    string = ""
    flush = False
    with open( handle ) as infile:
      for line in infile:
        if not line.strip():
          flush = True

        words = line.strip().split( " " )
        string = words.pop( 0 )
        for word in words:
          if len( string + " " + word ) < size:
            string = string + " " + word
          else:
            flush = True

        if flush:
          self.tasks.append( ( interval, StringEvent( string ) ) )
          self.tasks.append( ( 0, TapEvent( Key.enter, 1 ) ) )
          self.tasks.append( ( 0, TapEvent( Key.enter, 0 ) ) )
          string = ""


class EventRecorder:

  def __init__( self ):
    self.tasks = []
    self.last = time()

  def clear( self ):
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
