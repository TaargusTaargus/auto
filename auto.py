from pyautogui import click, keyDown, keyUp, typewrite
from pymouse import PyMouseEvent
from pykeyboard import PyKeyboardEvent
from time import time, sleep
from threading import Thread
from sys import argv
import ctypes

START_MASTER_SERVICE = "start"
READ_TEXT_FILE = "read"

class StringEvent:

  def __init__( self, string ):
    self.string = string

  def consume( self ):
    typewrite( self.string )

  def to_string( self ):
    return self.string


class ClickEvent:

  MOUSE_LEFT = 1
  MOUSE_RIGHT = 2

  def __init__( self, x, y, button=1 ):
    self.x = x
    self.y = y
    self.button = button

  def consume( self ):
    click( x=self.x, y=self.y, button='right' if self.button == self.MOUSE_RIGHT else 'left' )

  def to_string( self ):
    return ",".join( [ "click", str( self.x ), str( self.y ), str( self.button ) ] )


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



class Controller (Thread):
  
  def __init__( self, tasks=[] ):
    Thread.__init__( self )
    self.tasks = tasks
    self.counter = 0
    self.running = True


  def run( self ):
    while self.running:
      time, event = self.tasks[ self.counter ]
      sleep( time )
      event.consume()
      self.counter = ( self.counter + 1 ) % len( self.tasks )


  def switch( self ):
    self.running = not self.running


  def load_auto_file( self, handle ): 
    self.tasks = []
    fhandle = open( handle, "rb" )
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

class ClickManager (PyMouseEvent):

  def __init__( self, recorder ):
    PyMouseEvent.__init__( self )
    self.recorder = recorder


  def click( self, x, y, button, pressed ):    
    if pressed:
      self.recorder.record( ClickEvent( x, y, button ) )


class Recorder:

  def __init__( self ):
    self.tasks = []
    self.last = time()

  
  def record( self, event ):
    now = time()
    self.tasks.append( ( now - self.last if self.tasks else 0, event ) )
    self.last = now


  def save( self, handle ):
    fhandle = open( handle, "wb" )
    for time, event in self.tasks:
      fhandle.write( ",".join( [ str( time ), event.to_string() ] ) + "\n" )
    fhandle.close()

  def get_snapshot( self ):
    return list( self.tasks )

 
class TapManager (PyKeyboardEvent):
 
  LOAD = 23 ## tab
  SAVE = 49 ## `
  RECORD = 50 ## R-Shift
  PLAY = 62 ## L-Shift 
 
  def __init__( self ):
    PyKeyboardEvent.__init__( self )
    self.record = False
    self.play = True
    self.snapshot = None
    self.mouse = None
    self.control = None
    self.recorder = Recorder()


  def tap( self, code, char, press ):
    if not self.record:
      if code == self.SAVE and not press:
        self.recorder.save( "recording.auto" )

      if code == self.LOAD and not press:
        self.control = Controller()
        self.control.load_auto_file( "recording.auto" )

      if code == self.PLAY and not press and self.control:
        if self.play:
          self.control.start()
          self.play = False
        else: 
          self.control.switch()
          self.control = Controller( self.control.scheme )
          self.play = True

    else:
      self.recorder.record( TapEvent( char, int( press ) ) ) 


    if code == self.RECORD and not press:
      self.record = not self.record
      if self.record:
        self.mouse = ClickManager( self.recorder )
        self.mouse.start()
      else:
        self.snapshot = self.recorder.get_snapshot()
        self.control = Controller( self.snapshot )



'''
mode = argv[ 1 ]
if mode == START_MASTER_SERVICE:
  keyboard = TapManager()
  keyboard.run()
elif mode == READ_TEXT_FILE:
  controller = Controller()
  controller.load_text_file( argv[ 2 ] )
  controller.run()
'''
