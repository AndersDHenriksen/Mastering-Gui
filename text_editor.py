import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc


class MainWindow(qtw.QMainWindow):

    settings = qtc.QSettings('ProInvent', 'text editor')

    def __init__(self):
        """MainWindow constructor"""
        super().__init__()
        # Main UI code goes here
        self.textedit = qtw.QTextEdit()
        self.setCentralWidget(self.textedit)

        # statusBar
        self.statusBar().showMessage('Welcome to text_editor.py')
        charcount_label = qtw.QLabel("chars: 0")
        self.textedit.textChanged.connect(lambda: charcount_label.setText(f"chars: {len(self.textedit.toPlainText())}"))
        self.statusBar().addPermanentWidget(charcount_label)

        # menuBar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        edit_menu = menubar.addMenu('Edit')
        help_menu = menubar.addMenu('Help')
        open_action = file_menu.addAction('Open', self.openFile)
        save_action = file_menu.addAction('Save', self.saveFile)
        quit_action = file_menu.addAction('Quit', self.destroy)
        edit_menu.addAction('Undo', self.textedit.undo)
        redo_action = qtw.QAction('Redo', self)
        redo_action.triggered.connect(self.textedit.redo)
        edit_menu.addAction(redo_action)
        help_menu.addAction('About', self.showAboutDialog)

        # toolBar
        toolbar = self.addToolBar('File')
        # toolbar.addAction(open_action)
        # toolbar.addAction("Save")
        open_icon = self.style().standardIcon(qtw.QStyle.SP_DirOpenIcon)
        save_icon = self.style().standardIcon(qtw.QStyle.SP_DriveHDIcon)
        open_action.setIcon(open_icon)
        toolbar.addAction(open_action)
        toolbar.addAction(save_icon, 'Save', self.saveFile)

        help_action = qtw.QAction(
            self.style().standardIcon(qtw.QStyle.SP_DialogHelpButton),
            'Help',
            self,  # important to pass the parent!
            triggered=lambda: self.statusBar().showMessage('Sorry, no help yet!')
        )
        toolbar.addAction(help_action)

        # toolBar 2
        toolbar2 = qtw.QToolBar('Edit')
        toolbar2.addAction('Copy', self.textedit.copy)
        toolbar2.addAction('Cut', self.textedit.cut)
        toolbar2.addAction('Paste', self.textedit.paste)
        self.addToolBar(qtc.Qt.RightToolBarArea, toolbar2)

        # Docked widget
        dock = qtw.QDockWidget("Replace")
        self.addDockWidget(qtc.Qt.LeftDockWidgetArea, dock)
        dock.setFeatures(qtw.QDockWidget.DockWidgetMovable | qtw.QDockWidget.DockWidgetFloatable)
        replace_widget = qtw.QWidget()
        replace_widget.setLayout(qtw.QVBoxLayout())
        dock.setWidget(replace_widget)
        self.search_text_inp = qtw.QLineEdit(placeholderText='search')
        self.replace_text_inp = qtw.QLineEdit(placeholderText='replace')
        search_and_replace_btn = qtw.QPushButton("Search and Replace", clicked=self.search_and_replace)
        replace_widget.layout().addWidget(self.search_text_inp)
        replace_widget.layout().addWidget(self.replace_text_inp)
        replace_widget.layout().addWidget(search_and_replace_btn)
        replace_widget.layout().addStretch()

        response = qtw.QMessageBox.question(self, 'My Text Editor', 'This is beta software, do you want to continue?',
                                            qtw.QMessageBox.Yes | qtw.QMessageBox.Abort)
        if response == qtw.QMessageBox.No:
            self.close()
            sys.exit()

        if self.settings.value('show_warnings', False, type=bool):
            # Warning dialog code follows...
            self.settings.setValue('show_warnings', self.show_warnings_cb.isChecked())

        # End main UI code
        self.show()

    def search_and_replace(self):
        s_text = self.search_text_inp.text()
        r_text = self.replace_text_inp.text()
        if s_text:
            self.textedit.setText(self.textedit.toPlainText().replace(s_text, r_text))

    def showAboutDialog(self):
        qtw.QMessageBox.about(self, "About text_editor.py", "This is a text editor written in PyQt5.")

    def openFile(self):
        filename, _ = qtw.QFileDialog.getOpenFileName(self, "Select a text file to open…", qtc.QDir.homePath(),
            'Text Files (*.txt) ;;Python Files (*.py) ;;All Files (*)', 'Python Files (*.py)',
            qtw.QFileDialog.DontUseNativeDialog | qtw.QFileDialog.DontResolveSymlinks)
        if filename:
            try:
                with open(filename, 'r') as fh:
                    self.textedit.setText(fh.read())
            except Exception as e:
                qtw.QMessageBox.critical(f"Could not load file: {e}")

    def saveFile(self):
        filename, _ = qtw.QFileDialog.getSaveFileName(self, "Select the file to save to…", qtc.QDir.homePath(),
                                                      'Text Files (*.txt) ;;Python Files (*.py) ;;All Files (*)')
        if filename:
            try:
                with open(filename, 'w') as fh:
                    fh.write(self.textedit.toPlainText())
                self.statusBar().showMessage('File Saved!')
            except Exception as e:
                qtw.QMessageBox.critical(f"Could not save file: {e}")

    def set_font(self):
        current = self.textedit.currentFont()

        font, accepted = qtw.QFontDialog.getFont(current, self, options=(qtw.QFontDialog.DontUseNativeDialog |
                                                                         qtw.QFontDialog.MonospacedFonts))
        if accepted:
            self.textedit.setCurrentFont(font)

    def show_settings(self):
        settings_dialog = SettingsDialog(self.settings, self)
        settings_dialog.exec()


class SettingsDialog(qtw.QDialog):
    """Dialog for setting the settings"""

    def __init__(self, settings, parent=None):
        super().__init__(parent, modal=True)

        self.setLayout(qtw.QFormLayout())
        self.settings = settings
        self.layout().addRow(qtw.QLabel('<h1>Application Settings</h1>'),)
        self.show_warnings_cb = qtw.QCheckBox(checked=settings.get('show_warnings'))
        self.layout().addRow("Show Warnings", self.show_warnings_cb)
        self.accept_btn = qtw.QPushButton('Ok', clicked=self.accept)
        self.cancel_btn = qtw.QPushButton('Cancel', clicked=self.reject)
        self.layout().addRow(self.accept_btn, self.cancel_btn)

    def accept(self):
        self.settings['show_warnings'] = self.show_warnings_cb.isChecked()
        super().accept()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())