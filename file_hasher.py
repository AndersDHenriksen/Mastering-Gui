import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc


class HashForm(qtw.QWidget):

    submitted = qtc.pyqtSignal(str, str, int)

    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QFormLayout())
        self.source_path = qtw.QPushButton('Click to select…', clicked=self.on_source_click)
        self.layout().addRow('Source Path', self.source_path)
        self.destination_file = qtw.QPushButton('Click to select…', clicked=self.on_dest_click)
        self.layout().addRow('Destination File', self.destination_file)
        self.threads = qtw.QSpinBox(minimum=1, maximum=7, value=2)
        self.layout().addRow('Threads', self.threads)
        submit = qtw.QPushButton('Go', clicked=self.on_submit)
        self.layout().addRow(submit)

    def on_source_click(self):
        dirname = qtw.QFileDialog.getExistingDirectory()
        if dirname:
            self.source_path.setText(dirname)

    def on_dest_click(self):
        filename, _ = qtw.QFileDialog.getSaveFileName()
        if filename:
            self.destination_file.setText(filename)

    def on_submit(self):
        self.submitted.emit(self.source_path.text(), self.destination_file.text(), self.threads.value())


class HashRunner(qtc.QRunnable):

    file_lock = qtc.QMutex()    # Will be instantiated for the class, and thus shared between objects

    def __init__(self, infile, outfile):
        super().__init__()
        self.infile = infile
        self.outfile = outfile
        self.hasher = qtc.QCryptographicHash(qtc.QCryptographicHash.Md5)
        self.setAutoDelete(True)        # Objects will be deleted after run

    def run(self):
        print(f'hashing {self.infile}')
        self.hasher.reset()
        with open(self.infile, 'rb') as fh:
            self.hasher.addData(fh.read())
        hash_string = bytes(self.hasher.result().toHex()).decode('UTF-8')
        with qtc.QMutexLocker(self.file_lock):
            with open(self.outfile, 'a', encoding='utf-8') as out:
                out.write(f'{self.infile}\t{hash_string}\n')


class HashManager(qtc.QObject):

    finished = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.pool = qtc.QThreadPool.globalInstance()

    @qtc.pyqtSlot(str, str, int)
    def do_hashing(self, source, destination, threads):
        self.pool.setMaxThreadCount(threads)
        qdir = qtc.QDir(source)
        for filename in qdir.entryList(qtc.QDir.Files):
            filepath = qdir.absoluteFilePath(filename)
            runner = HashRunner(filepath, destination)
            self.pool.start(runner)
        self.pool.waitForDone()
        self.finished.emit()


class MainWindow(qtw.QMainWindow):

    def __init__(self):
        """MainWindow constructor"""
        super().__init__()
        # Main UI code goes here
        form = HashForm()
        self.setCentralWidget(form)
        self.manager = HashManager()
        self.manager_thread = qtc.QThread()
        self.manager.moveToThread(self.manager_thread)
        self.manager_thread.start()
        form.submitted.connect(self.manager.do_hashing)
        form.submitted.connect(lambda x, y, z: self.statusBar().showMessage(f'Processing files in {x} into {y} with {z} threads.'))
        self.manager.finished.connect(lambda: self.statusBar().showMessage('Finished'))

        # End main UI code
        self.show()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())