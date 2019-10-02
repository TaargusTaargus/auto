from event import EventController
from manager import ShellTapManager
from gui import Presenter, Ui_Form
from PyQt4 import QtGui
from sys import argv, exit

def main():
  app = QtGui.QApplication( argv )
  form = QtGui.QWidget()
  ui = Ui_Form()
  ui.setup_ui( form )

  presenter = Presenter( ui )
  presenter.init()

  form.show()
  exit( app.exec_() )

if __name__ == "__main__":
  main()
