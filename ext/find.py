import re
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtWidgets import QRadioButton, QTextEdit, QCheckBox

'''
Lógica usada para procurar e substituir está deprecada.
A partir do PyQt5 já é possível usar métodos do próprio QTextEdit para fazer essa ação, tais como o método Find
e/ou usando o QRegEx (PyQt5) / QRegularExpression (PyQt6) para substituir o tradicional RegEx de uma forma muito mais 
eficiente, usando menos linhas.
'''


class Find(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.normal_radio: QRadioButton | None = None
        self.regex_radio: QRadioButton | None = None

        self.find_field: QTextEdit | None = None
        self.replace_field: QTextEdit | None = None

        self.case_sens: QCheckBox | None = None
        self.whole_words: QCheckBox | None = None

        self.last_match: re.Match | None = None
        self.last_query: str = ''

        self.parent = parent

        self.init_ui()

    def init_ui(self):
        # Botão para procurar algo no documento
        find_button = QtWidgets.QPushButton('Procurar', self)
        find_button.clicked.connect(self.find_)

        # Botão para substituir a última ocorrência
        replace_button = QtWidgets.QPushButton('Substituir', self)
        replace_button.clicked.connect(self.replace)

        # Botão para substituir todas as ocorrências
        all_button = QtWidgets.QPushButton('Substituir tudo', self)
        all_button.clicked.connect(self.replace_all)

        # Modo normal — botão radial
        self.normal_radio = QRadioButton('Normal', self)
        self.normal_radio.toggled.connect(self.normal_mode)

        # Modo de expressão regular — botão radial
        self.regex_radio = QRadioButton('RegEx', self)
        self.regex_radio.toggled.connect(self.regex_mode)

        # Campo para digitar a consulta
        self.find_field = QTextEdit(self)
        self.find_field.resize(250, 50)

        # Campo para digitar o texto para substituir a consulta
        self.replace_field = QTextEdit(self)
        self.replace_field.resize(250, 50)

        options_label = QtWidgets.QLabel('Opções: ', self)

        # Opção para coincidir maiúsculas e minúsculas
        self.case_sens = QCheckBox('Diferenciar maiúsculas', self)

        # Opção para coincidir palavra inteira
        self.whole_words = QCheckBox('Coincidir palavra', self)

        # Layout dos objetos na tela
        layout = QtWidgets.QGridLayout()

        layout.addWidget(self.find_field, 1, 0, 1, 4)
        layout.addWidget(self.normal_radio, 2, 2)
        layout.addWidget(self.regex_radio, 2, 3)
        layout.addWidget(find_button, 2, 0, 1, 2)

        layout.addWidget(self.replace_field, 3, 0, 1, 4)
        layout.addWidget(replace_button, 4, 0, 1, 2)
        layout.addWidget(all_button, 4, 2, 1, 2)

        # Adicionando espaço adicional
        spacer = QtWidgets.QWidget(self)
        spacer.setFixedSize(0, 10)

        layout.addWidget(spacer, 5, 0)

        layout.addWidget(options_label, 6, 0)
        layout.addWidget(self.case_sens, 6, 1)
        layout.addWidget(self.whole_words, 6, 2)
        
        # Centralizar dialog box
        width = 360
        height = 250
        x = int(self.parent.width() / 2 - width / 2 + self.parent.x())
        y = int(self.parent.height() / 2 - height / 2 + self.parent.y())

        self.setGeometry(x, y, width, height)
        self.setLayout(layout)
        self.setWindowTitle('Procurar e Substituir')

        # Por padrão o modo normal é ativado e o campo encontrar recebe o foco
        self.normal_radio.setChecked(True)
        self.find_field.setFocus()

    def find_(self):
        # Pega o texto do formulário principal
        text = self.parent.text.toPlainText()

        # E o texto para procurar
        query = self.find_field.toPlainText()

        # Verifica se a query atual é diferente da última query, se sim, reseta a last_match e salva a query na memória
        if self.last_query != query:
            self.last_match = None
            self.last_query = query

        # Se a checkbox 'Coincidir palavra' estiver marcada, é preciso acrescentar a consulta entre characteres
        # não alfanuméricos para compilar no re, além de acrescentar um espaço em branco no início do texto para
        # permitir a identificação de uma possível ocorrência no primeiro character do documento
        if self.whole_words.isChecked():
            query = r'\W' + query + r'\W'
            text = ' ' + text

        # Por padrão regex tem match case, portanto, é preciso alterar caso a checkbox
        # 'Diferenciar maiúsculas' não esteja marcada
        flags = 0 if self.case_sens.isChecked() else re.I

        # Compila o padrão
        pattern = re.compile(query, flags)

        # Se a última procura teve êxito, comece na posição após o final da última correspondência, se não comece no 0
        start = self.last_match.start() + 1 if self.last_match else 0

        # A busca atual
        self.last_match = pattern.search(text, start)

        if self.last_match:
            start = self.last_match.start()
            end = self.last_match.end()

            # Caso 'Coincidir palavra inteira' estiver marcado, a seleção incluiria os dois character não alfanuméricos
            # inclusos na pesquisa que precisam ser removidos antes de serem destacados
            if self.whole_words.isChecked():
                # start += 1
                end -= 2

            self.move_cursor(start, end)
        else:
            # Seta o cursor para o fim caso a pesquisa não tenha êxito
            self.parent.text.moveCursor(QtGui.QTextCursor.MoveOperation.End)

    def replace(self):
        # Pega o objeto de cursor de texto
        cursor = self.parent.text.textCursor()

        # Verifica se a última procura teve êxito e se o cursor está selecionando algo
        if self.last_match and cursor.hasSelection():
            # Insere o novo texto que irá sobrescrever o texto selecionado
            cursor.insertText(self.replace_field.toPlainText())

            # E seta o novo cursor
            self.parent.text.setTextCursor(cursor)

    def replace_all(self):
        # Seta last_match como None para que a pesquisa comece no início do documento
        self.last_match = None

        # Chama o método find(), dessa forma last_match não é mais None
        self.find_()

        # Substitui até não houver mais nenhuma correspondência
        while self.last_match:
            self.replace()
            self.find_()

    def regex_mode(self):
        # Primeiro é desmarcado todas as checkboxes
        self.case_sens.setChecked(False)
        self.whole_words.setChecked(False)

        # Depois desabilita-os
        self.case_sens.setEnabled(False)
        self.whole_words.setEnabled(False)

    def normal_mode(self):
        # Habilita as checkboxes
        self.case_sens.setEnabled(True)
        self.whole_words.setEnabled(True)

    def move_cursor(self, start, end):
        # Cria um objeto de cursor a partir do cursor do QText Edit da janela principal
        cursor = self.parent.text.textCursor()

        # Então é setado a posição para o começo da última correspondência
        cursor.setPosition(start)

        # A seguir é movido o cursor pela correspondência sendo passado o parâmetro que faz o cursor selecionar o
        # texto da correspondência
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.Right, QtGui.QTextCursor.MoveMode.KeepAnchor, end - start)

        # fmt = QtGui.QTextCharFormat()
        # fmt.setBackground(QtGui.QBrush(QtGui.QColor('yellow')))
        # cursor.mergeCharFormat(fmt)

        # Seta o cursor 'artificial' como cursor principal
        self.parent.text.setTextCursor(cursor)
