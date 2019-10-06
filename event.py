from pyautogui import click, keyDown, keyUp, moveTo, typewrite
from time import sleep, time
from threading import Thread

class ClickEvent:

  MOUSE_LEFT = 1
  MOUSE_RIGHT = 2

  def __init__( self, x, y, button=1 ):
    self.x = x
    self.y = y
    self.button = button

  def consume( self ):
    moveTo( self.x, self.y )
    click( x=self.x, y=self.y, button='right' if self.button == self.MOUSE_RIGHT else 'left' )

  def to_string( self ):
    return ",".join( [ "click", str( self.x ), str( self.y ), str( self.button ) ] )


class StringEvent:

  def __init__( self, string ):
    self.string = string

  def consume( self ):
    typewrite( self.string )

  def to_string( self ):
    return self.string


class TapEvent:

  KEY_DOWN = 1
  KEY_UP = 0

  def __init__( self, keycode, motion=0 ):
    self.keycode = keycode
    self.motion = motion

  def consume( self ):
    if self.motion == self.KEY_DOWN:
      keyDown( self.keycode )
    else:
      keyUp( self.keycode ) 

  def to_string( self ):
    return ",".join( [ "tap", str( self.keycode ), str( self.motion ) ] )


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
      if attr[ 1 ] == "click":
        self.tasks.append( ( float( attr[ 0 ] ), ClickEvent( int( attr[ 2 ] ), int( attr[ 3 ] ), int( attr[ 4 ] ) ) ) )
      else:
        self.tasks.append( ( float( attr[ 0 ] ), TapEvent( attr[ 2 ], int( attr[ 3 ] ) ) ) )
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
