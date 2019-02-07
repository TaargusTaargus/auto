from event import EventController
from manager import ClickManager, EventRecorder, GuiTapManager
from os.path import expanduser, relpath
from PyQt4 import QtCore, QtGui

try:
  _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
  def _fromUtf8( s ):
    return s

try:
  _encoding = QtGui.QApplication.UnicodeUTF8
  def _translate( context, text, disambig ):
    return QtGui.QApplication.translate( context, text, disambig, _encoding )
except AttributeError:
  def _translate( context, text, disambig ):
    return QtGui.QApplication.translate( context, text, disambig )

EMPTY_TEXT = "No recording is loaded."
HOME_DIRECTORY = expanduser( "~" )
START_TEXT = "Start"
STOP_TEXT = "Stop"
PLAYBACK_TEXT = "Playing recording ..."
RECORDING_TEXT = "Recording ..."
POST_RECORDING_TEXT = "Unsaved recording loaded."

class Ui_Form( object ):

  def setup_ui( self, form ):
    form.setObjectName( _fromUtf8( "form" ) )
    form.resize( 372, 126 )
    self.form = form
    self.startStopButton = QtGui.QPushButton( form )
    self.startStopButton.setGeometry( QtCore.QRect( 270, 20, 99, 27 ) )
    self.startStopButton.setObjectName( _fromUtf8( "startStopButton" ) )
    self.bottomHorizontalLayoutWidget = QtGui.QWidget( form )
    self.bottomHorizontalLayoutWidget.setGeometry( QtCore.QRect( 0, 59, 371, 61 ) )
    self.bottomHorizontalLayoutWidget.setObjectName( _fromUtf8( "bottomHorizontalLayoutWidget" ) )
    self.bottomHorizontalLayout = QtGui.QHBoxLayout( self.bottomHorizontalLayoutWidget )
    self.bottomHorizontalLayout.setObjectName( _fromUtf8( "bottomHorizontalLayout" ) )
    self.createNewButton = QtGui.QPushButton( self.bottomHorizontalLayoutWidget )
    self.createNewButton.setObjectName( _fromUtf8( "createNewButton" ) )
    self.bottomHorizontalLayout.addWidget( self.createNewButton )
    self.openButton = QtGui.QPushButton( self.bottomHorizontalLayoutWidget )
    self.openButton.setObjectName( _fromUtf8( "openButton" ) )
    self.bottomHorizontalLayout.addWidget( self.openButton )
    self.saveAsButton = QtGui.QPushButton( self.bottomHorizontalLayoutWidget )
    self.saveAsButton.setObjectName( _fromUtf8( "saveAsButton" ) )
    self.bottomHorizontalLayout.addWidget( self.saveAsButton )
    self.statusLabel = QtGui.QLabel( form )
    self.statusLabel.setGeometry( QtCore.QRect( 7, 16, 251, 31 ) )
    self.statusLabel.setText( _fromUtf8( "" ) )
    self.statusLabel.setObjectName( _fromUtf8( "statusLabel" ) )

    self.retranslate_ui( form )
    QtCore.QMetaObject.connectSlotsByName( form )

  def retranslate_ui( self, Form ):
    Form.setWindowTitle( _translate( "Form", "Auto Man", None ) )
    self.startStopButton.setText( _translate( "Form", START_TEXT, None ) )
    self.statusLabel.setText( _translate( "Form", EMPTY_TEXT, None ) )
    self.createNewButton.setText( _translate( "Form", "Create New", None ) )
    self.openButton.setText( _translate( "Form", "Open ...", None ) )
    self.saveAsButton.setText( _translate( "Form", "Save as ...", None ) )
    self.createNewButton.hide()
    self.saveAsButton.hide()

  def get_bottom_horizontal_layout( self ):
    return self.bottomHorizontalLayout

  def get_save_as_button( self ):
    return self.saveAsButton

  def get_start_stop_button( self ):
    return self.startStopButton

  def get_open_button( self ):
    return self.openButton

  def get_create_new_button( self ):
    return self.createNewButton

  def get_status_label( self ):
    return self.statusLabel 

  def get_parent_form( self ):
    return self.form

  def get_open_dialog( self ):
    return QtGui.QFileDialog.getOpenFileName( self.form, "Open File", HOME_DIRECTORY, "Auto Files (*.auto)" )

  def get_save_dialog( self ):
    return QtGui.QFileDialog.getSaveFileName( self.form, "Save File", HOME_DIRECTORY, "Auto Files (*.auto)" )


class Presenter( object ):

  def __init__( self, view ):
    self.controller = EventController()
    self.recorder = EventRecorder()
    self.click, self.tap = ClickManager( self.recorder ), GuiTapManager( self.recorder )
    self.isrunning = False
    self.recording = None
    self.view = view

  def init_ui( self ):
    self.click.start()
    self.tap.start()
    self.view.get_create_new_button().clicked.connect( self.on_create_new_button_click )
    self.view.get_open_button().clicked.connect( self.on_open_button_click )
    self.view.get_save_as_button().clicked.connect( self.on_save_as_button_click )
    self.view.get_start_stop_button().clicked.connect( self.on_start_stop_button_click )

  def on_start_stop_button_click( self ):
    if self.isrunning:

      if self.recording:
        self.controller.disable()
        self.controller = EventController( self.recorder.tasks )
        self.view.get_status_label().setText( _translate( "Form", self.recording + " loaded.", None ) )
      else:
        self.click.disable()
        self.tap.disable()
        self.view.get_status_label().setText( _translate( "Form", POST_RECORDING_TEXT, None ) )
        self.controller = EventController( self.recorder.tasks )
        self.recording = "Unsaved recording"

      self.view.get_create_new_button().show()
      self.view.get_open_button().show()
      self.view.get_save_as_button().show()
      self.view.get_parent_form().resize( 372, 126 )
      self.view.get_start_stop_button().setText( _translate( "Form", START_TEXT, None ) )      

    else:

      if self.recording:
        self.controller.enable()
        self.controller.start()
        self.view.get_status_label().setText( _translate( "Form", "Running " + self.recording + " ...", None ) ) 
      else:
        self.tap.enable()
        self.click.enable()
        self.view.get_status_label().setText( _translate( "Form", RECORDING_TEXT, None ) ) 

      self.view.get_parent_form().resize( 372, 58 )
      self.view.get_start_stop_button().setText( _translate( "Form", STOP_TEXT, None ) )

    self.isrunning = not self.isrunning

  def on_create_new_button_click( self ):
    self.recording = None
    self.view.get_create_new_button().hide()
    self.view.get_save_as_button().hide()
    self.view.get_status_label().setText( _translate( "Form", EMPTY_TEXT, None ) )

  def on_open_button_click( self ):
    filename = self.view.get_open_dialog()
    if filename:
      self.controller.load_auto_file( filename )
      self.recording = relpath( filename )
      self.view.get_create_new_button().show()
      self.view.get_status_label().setText( _translate( "Form", self.recording + " loaded.", None ) )
      
  def on_save_as_button_click( self ):
    filename = self.view.get_save_dialog()
    if filename:
      self.recording = relpath( filename )
      self.recorder.save( filename )
      self.view.get_status_label().setText( _translate( "Form", self.recording + " loaded.", None ) )
