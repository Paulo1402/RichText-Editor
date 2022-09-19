import locale
from PyQt6 import QtWidgets


class WordCount(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_words: QtWidgets.QLabel | None = None
        self.current_symbols: QtWidgets.QLabel | None = None
        self.total_words: QtWidgets.QLabel | None = None
        self.total_symbols: QtWidgets.QLabel | None = None

        self.parent = parent

        self.init_ui()

    def init_ui(self):
        # Conta as palavras na seleção
        current_label = QtWidgets.QLabel('Atual seleção', self)
        current_label.setStyleSheet('font-weight: bold; font-size: 15px;')

        current_words_label = QtWidgets.QLabel('Palavras: ', self)
        current_symbols_label = QtWidgets.QLabel('Letras: ', self)

        self.current_words = QtWidgets.QLabel(self)
        self.current_symbols = QtWidgets.QLabel(self)

        # Total de palavras e símbolos
        total_label = QtWidgets.QLabel('Total', self)
        total_label.setStyleSheet('font-weight: bold; font-size: 15px;')

        total_words_label = QtWidgets.QLabel('Palavras: ', self)
        total_symbols_label = QtWidgets.QLabel('Letras: ', self)

        self.total_words = QtWidgets.QLabel(self)
        self.total_symbols = QtWidgets.QLabel(self)

        # Layout
        layout = QtWidgets.QGridLayout()

        layout.addWidget(current_label, 0, 0)

        layout.addWidget(current_words_label, 1, 0)
        layout.addWidget(self.current_words, 1, 1)

        layout.addWidget(current_symbols_label, 2, 0)
        layout.addWidget(self.current_symbols, 2, 1)

        spacer = QtWidgets.QWidget()
        spacer.setFixedSize(0, 5)

        layout.addWidget(spacer, 3, 0)

        layout.addWidget(total_label, 4, 0)

        layout.addWidget(total_words_label, 5, 0)
        layout.addWidget(self.total_words, 5, 1)

        layout.addWidget(total_symbols_label, 6, 0)
        layout.addWidget(self.total_symbols, 6, 1)

        # Centralizar dialog box
        width = 150
        height = 200
        x = int(self.parent.width() / 2 - width / 2 + self.parent.x())
        y = int(self.parent.height() / 2 - height / 2 + self.parent.y())

        self.setGeometry(x, y, width, height)
        self.setLayout(layout)
        self.setWindowTitle('Contagem')

    def get_text(self):
        # Pega o texto atual da seleção
        text = self.parent.text.textCursor().selectedText()

        # Divide o texto para contar as palavras
        words = len(text.split())

        # Apenas pega o comprimento do texto para a contagem dos símbolos
        symbols = len(text)

        self.current_words.setText(self.format_number(words))
        self.current_symbols.setText(self.format_number(symbols))

        # Para a contagem total, mesma coisa acima, mas para o texto total
        text = self.parent.text.toPlainText()

        words = len(text.split())
        symbols = len(text)

        self.total_words.setText(self.format_number(words))
        self.total_symbols.setText(self.format_number(symbols))

    # Retorna o número formatado com separador de milhar conforme o país.
    @staticmethod
    def format_number(number: float | int):
        locale.setlocale(locale.LC_ALL, '')

        return locale.format_string('%d', number, grouping=True)
