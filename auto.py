from event import ClickEvent, StringEvent, TapEvent, EventController, EventRecorder
from manager import ShellTapManager
from gui import Presenter, Ui_Form
from PyQt4 import QtGui

GUI_MODE = "gui"
SHELL_MODE = "shell"
READ_MODE = "read"

if __name__ == "__main__":
  from sys import argv, exit
  mode = argv[ 1 ]

  if mode == GUI_MODE:
    app = QtGui.QApplication( argv )
    form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setup_ui( form )

    presenter = Presenter( ui )
    presenter.init_ui()

    form.show()
    exit( app.exec_() )

  elif mode == SHELL_MODE:
    print( ShellTapManager.HELP_SHELL_TEXT )
    keyboard = ShellTapManager()
    try:
      keyboard.run()
    except:
      print( "exiting ..." )

  elif mode == READ_MODE:
    controller = EventController()
    controller.load_text_file( argv[ 2 ] )
    controller.run()


