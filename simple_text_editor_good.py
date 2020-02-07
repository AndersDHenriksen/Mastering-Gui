import os
import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc


class MainWindow(qtw.QMainWindow):

    def __init__(self):
        """MainWindow constructor"""
        super().__init__()
        # Main UI code goes here

        self.view = View()
        self.setCentralWidget(self.view)
        self.model = Model()
        self.view.submitted.connect(self.model.save)
        self.model.error.connect(self.view.show_error)

        # End main UI code
        self.show()


class Model(qtc.QObject):
    error = qtc.pyqtSignal(str)

    def save(self, filename, content):
        print("save_called")
        error = ''
        if not filename:
            error = 'Filename empty'
        elif os.path.exists(filename):
            error = f'Will not overwrite {filename}'
        else:
            try:
                with open(filename, 'w') as fh:
                    fh.write(content)
            except Exception as e:
                error = f'Cannot write file: {e}'
        if error:
            self.error.emit(error)


class View(qtw.QWidget):
    submitted = qtc.pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QVBoxLayout())
        self.filename = qtw.QLineEdit()
        self.filecontent = qtw.QTextEdit()
        self.savebutton = qtw.QPushButton('Save', clicked=self.submit)
        self.layout().addWidget(self.filename)
        self.layout().addWidget(self.filecontent)
        self.layout().addWidget(self.savebutton)

    def submit(self):
        filename = self.filename.text()
        filecontent = self.filecontent.toPlainText()
        self.submitted.emit(filename, filecontent)

    def show_error(self, error):
        qtw.QMessageBox.critical(None, 'Error', error)

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())