import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc


class SlowSearcher(qtc.QObject):
    match_found = qtc.pyqtSignal(str)
    directory_changed = qtc.pyqtSignal(str)
    finished = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.term = None

    def set_term(self, term):
        self.term = term

    def do_search(self):
        root = qtc.QDir.rootPath()
        self._search(self.term, root)
        self.finished.emit()

    def _search(self, term, path):
        self.directory_changed.emit(path)
        directory = qtc.QDir(path)
        directory.setFilter(directory.filter() | qtc.QDir.NoDotAndDotDot | qtc.QDir.NoSymLinks)
        for entry in directory.entryInfoList():
            if term in entry.filePath():
                print(entry.filePath())
                self.match_found.emit(entry.filePath())
            if entry.isDir():
                self._search(term, entry.filePath())


class SearchForm(qtw.QWidget):
    textChanged = qtc.pyqtSignal(str)
    returnPressed = qtc.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QVBoxLayout())
        self.search_term_inp = qtw.QLineEdit(placeholderText='Search Term', textChanged=self.textChanged, returnPressed=self.returnPressed)
        self.layout().addWidget(self.search_term_inp)
        self.results = qtw.QListWidget()
        self.layout().addWidget(self.results)
        self.returnPressed.connect(self.results.clear)

    def addResult(self, result):
        self.results.addItem(result)



class MainWindow(qtw.QMainWindow):

    def __init__(self):
        """MainWindow constructor"""
        super().__init__()
        # Main UI code goes here
        form = SearchForm()
        self.setCentralWidget(form)
        self.ss = SlowSearcher()

        self.searcher_thread = qtc.QThread()
        self.ss.moveToThread(self.searcher_thread)
        self.ss.finished.connect(self.searcher_thread.quit)
        self.searcher_thread.start()

        form.textChanged.connect(self.ss.set_term)
        form.returnPressed.connect(self.ss.do_search)
        form.returnPressed.connect(self.searcher_thread.start)
        self.ss.match_found.connect(form.addResult)
        self.ss.finished.connect(self.on_finished)
        self.ss.directory_changed.connect(self.on_directory_changed)

        # End main UI code
        self.show()

    def on_finished(self):
        qtw.QMessageBox.information(self, 'Complete', 'Search complete')

    def on_directory_changed(self, path):
        self.statusBar().showMessage(f'Searching in: {path}')


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())