from event import EventController, EventRecorder, ClickEvent, TapEvent
from pynput.keyboard import KeyCode, Listener as KeyboardListener
from pynput.mouse import Button, Listener as MouseListener
from PyQt4 import QtCore


class GuiClickRecordManager( QtCore.QThread ):

  def __init__( self, recorder ):
    QtCore.QThread.__init__( self )
    self.enabled = False
    self.recorder = recorder

  def disable( self ):
    self.enabled = False

  def enable( self ):
    self.enabled = True

  def run( self ):
    with MouseListener( on_click = self.on_click ) as listener:
      listener.join()

  def on_click( self, x, y, button, pressed ):
    if self.enabled and pressed:
      if button == Button.left:
        self.recorder.record( ClickEvent( x, y, 1 ) )
      elif button == Button.right:
        self.recorder.record( ClickEvent( x, y, 2 ) )


class GuiTapRecordManager( QtCore.QThread ):

  def __init__( self, recorder, control_config ):
    QtCore.QThread.__init__( self )
    self.config = control_config
    self.enabled = False
    self.recorder = recorder
    self.signal = QtCore.SIGNAL( "SIGNAL" )

  def disable( self ):
    self.enabled = False

  def enable( self ):
    self.enabled = True

  def run( self ):
    with KeyboardListener( on_press = self.on_press, on_release = self.on_release ) as listener:
      listener.join()

  def on_press( self, key ):
    if isinstance( key, KeyCode ) and key.char == self.config[ "stop" ]:
      self.emit( self.signal )
      self.enabled = False

    if self.enabled:
      self.recorder.record( TapEvent( key, 1 ) )
 
  def on_release( self, key ):
    if self.enabled:
      self.recorder.record( TapEvent( key, 0 ) )
