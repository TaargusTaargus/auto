from event import EventController
from manager import EventRecorder, GuiClickRecordManager, GuiTapRecordManager
from os.path import expanduser, relpath, sep
from PyQt4 import QtCore, QtGui
from platform import system

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
STOP_KEY = "~"
STOP_TEXT = "Stop"
PLAYBACK_TEXT = "Playing recording ..."
POST_RECORDING_TEXT = "Unsaved recording loaded."

CONTROL_CONFIG = {
  "stop": "`"
}
 
class Ui_Form( object ):

  def setup_ui( self, form ):
    form.setObjectName( _fromUtf8( "form" ) )
    form.resize( 372, 126 )
    self.form = form
    self.startButton = QtGui.QPushButton( form )
    self.startButton.setGeometry( QtCore.QRect( 270, 20, 99, 27 ) )
    self.startButton.setObjectName( _fromUtf8( "startButton" ) )
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
    self.startButton.setText( _translate( "Form", START_TEXT, None ) )
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

  def get_start_button( self ):
    return self.startButton

  def get_open_button( self ):
    return self.openButton

  def get_create_new_button( self ):
    return self.createNewButton

  def get_status_label( self ):
    return self.statusLabel 

  def get_parent_form( self ):
    return self.form

  def get_open_dialog( self ):
    return QtGui.QFileDialog.getOpenFileName( self.form, "Open File", HOME_DIRECTORY, "Auto Files (*.auto);;Text Files (*.txt)" )

  def get_save_dialog( self ):
    dialog = QtGui.QFileDialog()
    dialog.setAcceptMode( QtGui.QFileDialog.AcceptSave )
    dialog.setDefaultSuffix( "auto" )
    dialog.setDirectory( HOME_DIRECTORY )
    dialog.setFileMode( QtGui.QFileDialog.AnyFile )
    dialog.setNameFilter( "Auto Files (*.auto)" )
    dialog.setViewMode( QtGui.QFileDialog.Detail )
    dialog.exec()
    return dialog.selectedFiles()[ -1 ]


class OnStopCallback( QtCore.QThread ):

  def __init__( self ):
    QtCore.QThread.__init__( self )
    self.signal = QtCore.SIGNAL( "SIGNAL" )

  def run( self ):
    self.emit( self.signal )

  def stop_thread( self ):
    self.emit( self.signal )

class Presenter( QtGui.QWidget ):

  def __init__( self, view ):
    QtGui.QWidget.__init__( self )
    self.controller = EventController()
    self.recorder = EventRecorder()
    self.click_manager, self.tap_manager = GuiClickRecordManager( self.recorder ), GuiTapRecordManager( self.recorder, CONTROL_CONFIG )
    self.recording = None
    self.view = view

  def init( self ):
    self.click_manager.start()
    self.tap_manager.start()
    self.view.get_create_new_button().clicked.connect( self.on_create_new_button_click )
    self.view.get_open_button().clicked.connect( self.on_open_button_click )
    self.view.get_save_as_button().clicked.connect( self.on_save_as_button_click )
    self.view.get_start_button().clicked.connect( self.on_start_button_click )

  def on_start_button_click( self ):
    if self.recording:
      self.controller.enable()
      self.controller.start()
      self.view.get_status_label().setText( _translate( "Form", "Running " + self.recording + " ( press " + STOP_KEY + " to stop ) ...", None ) ) 
    else:
      self.click_manager.enable()
      self.tap_manager.enable()
      self.view.get_status_label().setText( _translate( "Form", "Recording ( press " + STOP_KEY + " to stop ) ...", None ) ) 

    self.connect( self.tap_manager, self.tap_manager.signal, self.on_stop )
    self.view.get_parent_form().resize( 372, 58 )
    self.view.get_start_button().hide()
    self.view.get_status_label().resize( 350, 31 )

  def on_stop( self ):
    if self.recording:
      self.controller.disable()
      self.controller = EventController( self.recorder.tasks )
      self.view.get_status_label().setText( _translate( "Form", self.recording + " loaded.", None ) )
    else:
      self.click_manager.disable()
      self.tap_manager.disable()
      self.view.get_status_label().setText( _translate( "Form", POST_RECORDING_TEXT, None ) )
      self.controller = EventController( self.recorder.tasks )
      self.recording = "unsaved recording"

    self.view.get_create_new_button().show()
    self.view.get_open_button().show()
    self.view.get_save_as_button().show()
    self.view.get_start_button().show()
    self.view.get_status_label().resize( 249, 31 )
    self.view.get_parent_form().resize( 372, 126 )


  def on_create_new_button_click( self ):
    self.recording = None
    self.recorder.clear()
    self.view.get_create_new_button().hide()
    self.view.get_save_as_button().hide()
    self.view.get_status_label().setText( _translate( "Form", EMPTY_TEXT, None ) )

  def on_open_button_click( self ):
    filename = self.view.get_open_dialog()

    if not filename:
      return

    extension = filename.split( "." )[ -1 ]
    if extension == "auto":
      self.controller.load_auto_file( filename )
    elif extension == "txt":
      self.controller.load_text_file( filename )

    self.recording = relpath( filename ).split( sep )[ -1 ]
    self.view.get_create_new_button().show()
    self.view.get_status_label().setText( _translate( "Form", self.recording + " loaded.", None ) )
      
  def on_save_as_button_click( self ):
    filename = self.view.get_save_dialog()
    if filename:
      self.recording = relpath( filename ).split( sep )[ -1 ]
      self.recorder.save( filename )
      self.view.get_status_label().setText( _translate( "Form", self.recording + " loaded.", None ) )
