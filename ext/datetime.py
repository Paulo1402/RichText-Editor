from PyQt6 import QtWidgets
from time import strftime


'''
Adicionar uma opção para salvar as preferências do usuário.
E uma config para alterar o idioma do aplicativo, alterando todas as legendas e também da string das datas da função
'insert'
'''


class DateTime(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.box: QtWidgets.QComboBox | None = None

        self.parent = parent

        self.formats = ['%A, %d. %B %Y %H:%M',
                        '%A, %d. %B %Y',
                        '%d. %B %Y %H:%M',
                        '%d.%m.%Y %H:%M',
                        '%d. %B %Y',
                        '%d %m %Y',
                        '%d.%m.%Y',
                        '%x',
                        '%X',
                        '%H:%M']

        self.init_ui()

    def init_ui(self):
        self.box = QtWidgets.QComboBox(self)

        for i in self.formats:
            self.box.addItem(strftime(i))

        insert = QtWidgets.QPushButton('Inserir', self)
        insert.clicked.connect(self.insert)

        cancel = QtWidgets.QPushButton('Cancelar', self)
        cancel.clicked.connect(self.close)

        layout = QtWidgets.QGridLayout()

        layout.addWidget(self.box, 0, 0, 1, 2)
        layout.addWidget(insert, 1, 0)
        layout.addWidget(cancel, 1, 1)

        # Centralizar dialog box
        width = 360
        height = 250
        x = int(self.parent.width() / 2 - width / 2 + self.parent.x())
        y = int(self.parent.height() / 2 - height / 2 + self.parent.y())

        self.setGeometry(x, y, width, height)
        self.setLayout(layout)
        self.setWindowTitle('Data e Hora')

    def insert(self):
        # Pega o cursor
        cursor = self.parent.text.textCursor()

        # Pega o atual padrão escolhido na combobox pelo seu índice
        datetime = strftime(self.formats[self.box.currentIndex()])

        # Inserir atual texto da combobox
        cursor.insertText(datetime)

        # Fecha a janela
        self.close()
