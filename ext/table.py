from PyQt6 import QtGui, QtWidgets
from enum import Enum


class Mode(Enum):
    REMOVE_ROW = 1
    REMOVE_COL = 2
    INSERT_ROW = 3
    INSERT_COL = 4


class Table(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.rows: QtWidgets.QSpinBox | None = None
        self.cols: QtWidgets.QSpinBox | None = None
        self.space: QtWidgets.QSpinBox | None = None
        self.pad: QtWidgets.QSpinBox | None = None

        self.text: QtWidgets.QTextEdit = parent.text

        self.init_ui()

    def init_ui(self):
        # Linhas
        rows_label = QtWidgets.QLabel('Linhas: ', self)
        self.rows = QtWidgets.QSpinBox(self)

        # Colunas
        cols_label = QtWidgets.QLabel('Colunas: ', self)
        self.cols = QtWidgets.QSpinBox(self)

        # Distância entre células
        space_label = QtWidgets.QLabel('Distância entre células: ', self)
        self.space = QtWidgets.QSpinBox(self)

        # Distância ente célula e texto
        pad_label = QtWidgets.QLabel('Distância entre célula e texto: ', self)
        self.pad = QtWidgets.QSpinBox(self)

        self.pad.setValue(10)

        # Botões
        insert_button = QtWidgets.QPushButton('Inserir', self)
        insert_button.clicked.connect(self.insert)

        # Layout
        layout = QtWidgets.QGridLayout()

        layout.addWidget(rows_label, 0, 0)
        layout.addWidget(self.rows, 0, 1)

        layout.addWidget(cols_label, 1, 0)
        layout.addWidget(self.cols, 1, 1)

        layout.addWidget(pad_label, 2, 0)
        layout.addWidget(self.pad, 2, 1)

        layout.addWidget(space_label, 3, 0)
        layout.addWidget(self.space, 3, 1)

        layout.addWidget(insert_button, 4, 0, 1, 2)

        self.setWindowTitle('Inserir Tabela')
        self.setGeometry(300, 300, 200, 100)
        self.setLayout(layout)

    def insert(self):
        cursor = self.text.textCursor()

        # Pega a configuração
        rows = self.rows.value()
        cols = self.cols.value()

        if not rows or not cols:
            popup = QtWidgets.QMessageBox()
            popup.warning(self, 'Erro de parâmetro', 'O valor de linha e coluna não pode ser zero!',
                          QtWidgets.QMessageBox.StandardButton.Ok)
        else:
            padding = self.pad.value()
            space = self.space.value()

            # Seta o valor de padding e spacing
            fmt = QtGui.QTextTableFormat()
            fmt.setCellPadding(padding)
            fmt.setCellSpacing(space)

            # Insere a nova tabela
            cursor.insertTable(rows, cols, fmt)

            self.close()
