import sys
import json
import os
from ext import *
from PyQt6 import QtGui, QtCore, QtWidgets, QtPrintSupport
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QToolBar, QStatusBar, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon


def exception_hook(exctype, value, traceback):
    sys.__excepthook__(exctype, value, traceback)
    sys.exit(1)


class Main(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.toolbar: QToolBar | None = None
        self.formatbar: QToolBar | None = None

        self.statusbar: QStatusBar | None = None
        self.text: QTextEdit | None = None

        self.new_action: QAction | None = None
        self.open_action: QAction | None = None
        self.save_action: QAction | None = None
        self.print_action: QAction | None = None
        self.preview_action: QAction | None = None
        self.cut_action: QAction | None = None
        self.copy_action: QAction | None = None
        self.paste_action: QAction | None = None
        self.undo_action: QAction | None = None
        self.redo_action: QAction | None = None
        self.toolbar_action: QAction | None = None
        self.formatbar_action: QAction | None = None
        self.statusbar_action: QAction | None = None
        self.find_action: QAction | None = None

        self.language = ''
        self.filename = ''
        self.changes_saved = True

        self.init_ui()

    def init_ui(self):
        # Cria objeto e seta como widget central
        self.text = QTextEdit(self)
        self.setCentralWidget(self.text)

        self.text.setTabStopDistance(33)

        # Relaciona eventos do objeto QTextEdit à funções
        self.text.cursorPositionChanged.connect(self.cursor_position)
        self.text.textChanged.connect(self.changed)

        # Precisamos do nosso próprio menu de contexto para tabelas
        self.text.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.text.customContextMenuRequested.connect(self.context)

        # Seta título e ícone da janela
        self.setWindowTitle('MonkeyText Editor')
        self.setWindowIcon(QIcon('icons/icon.png'))

        # Retorna as preferências do usuário
        data = self.read_json()

        self.language = data['language']

        height = data['height']
        width = data['width']
        x = data['x']
        y = data['y']

        maximized = data['maximized']

        toolbar = data['toolbar']
        formatbar = data['formatbar']
        statusbar = data['statusbar']

        # Define posição, altura e largura da janela
        self.setGeometry(x, y, width, height)

        if maximized:
            self.showMaximized()

        # inicia uma barra de status para a janela
        self.statusbar = self.statusBar()

        # Inicia barras e menus
        self.init_toolbar()
        self.init_formatbar()
        self.init_menubar()

        # Seta visibilidade
        self.toolbar.setVisible(toolbar)
        self.formatbar.setVisible(formatbar)
        self.statusbar.setVisible(statusbar)

    def new(self):
        spawn = Main(self)
        spawn.show()

    def open(self):
        # Pega o nome do arquivo e mostra apenas arquivos .writer
        self.filename = QFileDialog.getOpenFileName(self, 'Abrir arquivo', '.', '(*.writer)')[0]

        if self.filename:
            with open(self.filename, 'rt') as file:
                self.text.setText(file.read())

    def save(self):
        # Apenas abre a caixa de diálogo se não há um caminho de arquivo ainda
        if not self.filename:
            self.filename = QFileDialog.getSaveFileName(self, 'Salvar arquivo')[0]

        # Aplica a extensão caso não haja
        if not self.filename.endswith('.writer'):
            self.filename += '.writer'

        # Armazena o conteúdo do arquivo de texto em HTML
        with open(self.filename, 'wt') as file:
            file.write(self.text.toHtml())

        self.changes_saved = True

    def preview(self):
        # Abre a caixa de diálogo de preview
        preview = QtPrintSupport.QPrintPreviewDialog()

        # Se uma impressão for solicitada, abrir caixa de diálogo impressão
        preview.paintRequested.connect(lambda p: self.text.print(p))

        preview.exec()

    def print(self):
        # Abre caixa de diálogo de impressão
        dialog = QtPrintSupport.QPrintDialog()

        if dialog.exec():
            self.text.document().print(dialog.printer())

    def bulleted_list(self):
        cursor = self.text.textCursor()

        # Insere lista de marcadores
        cursor.insertList(QtGui.QTextListFormat.Style.ListDisc)

    def numbered_list(self):
        cursor = self.text.textCursor()

        # Insere lista numerada
        cursor.insertList(QtGui.QTextListFormat.Style.ListDecimal)

    def cursor_position(self):
        cursor = self.text.textCursor()

        # Faz a contagem começar a partir do index 1
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1

        # Mostra na barra de status a localização do cursor
        self.statusbar.showMessage(f'Linha: {line} | Coluna: {col}')

    def font_family(self, font: QtGui.QFont):
        self.text.setCurrentFont(font)

    def font_size(self, font_size: str):
        self.text.setFontPointSize(int(font_size))

    def font_color(self):
        # Pega uma cor da caixa de diálogo de cor
        color = QtWidgets.QColorDialog.getColor()

        # Seta como a nova cor de texto
        self.text.setTextColor(color)

    def highlight(self):
        color = QtWidgets.QColorDialog.getColor()
        self.text.setTextBackgroundColor(color)

    def bold(self):
        if self.text.fontWeight() == QtGui.QFont.Weight.Bold:
            self.text.setFontWeight(QtGui.QFont.Weight.Normal)
        else:
            self.text.setFontWeight(QtGui.QFont.Weight.Bold)

    def italic(self):
        state = self.text.fontItalic()

        self.text.setFontItalic(not state)

    def underline(self):
        state = self.text.fontUnderline()

        self.text.setFontUnderline(not state)

    def strike(self):
        # Pega o formato do texto
        fmt = self.text.currentCharFormat()

        # Seta a propriedade fonte riscada para seu oposto
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())

        # E seta o próximo formato de character
        self.text.setCurrentCharFormat(fmt)

    def super_script(self):
        # Pega o formato atual
        fmt = self.text.currentCharFormat()

        # E pega a propriedade de alinhamento vertical
        align = fmt.verticalAlignment()

        # Troca o estado
        if align == QtGui.QTextCharFormat.VerticalAlignment.AlignNormal:
            fmt.setVerticalAlignment(QtGui.QTextCharFormat.VerticalAlignment.AlignSuperScript)
        else:
            fmt.setVerticalAlignment(QtGui.QTextCharFormat.VerticalAlignment.AlignNormal)

        # Seta o novo formato
        self.text.setCurrentCharFormat(fmt)

    def sub_script(self):
        # Pega o formato atual
        fmt = self.text.currentCharFormat()

        # E pega a propriedade de alinhamento vertical
        align = fmt.verticalAlignment()

        # Troca o estado
        if align == QtGui.QTextCharFormat.VerticalAlignment.AlignNormal:
            fmt.setVerticalAlignment(QtGui.QTextCharFormat.VerticalAlignment.AlignSubScript)
        else:
            fmt.setVerticalAlignment(QtGui.QTextCharFormat.VerticalAlignment.AlignNormal)

        # Seta o novo formato
        self.text.setCurrentCharFormat(fmt)

    def align_left(self):
        self.text.setAlignment(Qt.AlignmentFlag.AlignLeft)

    def align_right(self):
        self.text.setAlignment(Qt.AlignmentFlag.AlignRight)

    def align_center(self):
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def align_justify(self):
        self.text.setAlignment(Qt.AlignmentFlag.AlignJustify)

    def indent(self):
        self.indent_dedent(indent=True)

    def dedent(self):
        self.indent_dedent(indent=False)

    def indent_dedent(self, indent: bool):
        # Pega o cursor
        cursor = self.text.textCursor()

        if cursor.hasSelection():
            # Armazena a posição do último character, pois ao alterar a posição do cursor esse valor é perdido
            f_position = cursor.selectionEnd()

            # Move o cursor até o início da seleção
            cursor.setPosition(cursor.selectionStart())

            # Armazena o atual número da linha/bloco
            temp = cursor.blockNumber()

            # Move até a última linha da seleção
            cursor.setPosition(f_position)

            # Calcula o número de linhas da seleção
            diff = cursor.blockNumber() - temp

            # Itera sobre as linhas
            for n in range(diff + 1):
                if indent:
                    # Move até o início de cada linha
                    cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine)

                    # Insere tabulação
                    cursor.insertText('\t')
                else:
                    # Remove tabulação
                    self.handle_dedent(cursor)

                # Vai para a linha acima
                cursor.movePosition(QtGui.QTextCursor.MoveOperation.Up)

        # Se não há nenhuma seleção, apenas insere/remove a tabulação
        else:
            if indent:
                cursor.insertText('\t')
            else:
                self.handle_dedent(cursor)

    @staticmethod
    def handle_dedent(cursor: QtGui.QTextCursor):
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine)

        # Pega a linha
        line = cursor.block().text()

        # Se a linha começar com um character de tabulação, então o deleta
        if line.startswith('\t'):
            cursor.deleteChar()

        # Caso contrário, deleta todos os espaços até outro character ser encontrado
        else:
            for char in line[:8]:
                if char != ' ':
                    break

                cursor.deleteChar()

    def toggle_toolbar(self):
        self.toggle_bars(self.toolbar, self.toolbar_action)

    def toggle_formatbar(self):
        self.toggle_bars(self.formatbar, self.formatbar_action)

    def toggle_statusbar(self):
        self.toggle_bars(self.statusbar, self.statusbar_action)

    @staticmethod
    def toggle_bars(bar: QToolBar | QStatusBar, action: QAction):
        labels = ['Exibir', 'Ocultar']
        text = action.text()
        state = bar.isVisible()

        # Seta a propriedade visible para seu inverso
        bar.setVisible(not state)

        # Seta o label da ação
        action.setText(text.replace(labels[int(state)], labels[int(not state)]))

    def insert_image(self):
        # Pega o caminho da imagem
        filename = QFileDialog.getOpenFileName(self, 'Inserir imagem', '.', 'Imagens(*.png *.xpm *.jpg *.bmp *.gif)')[0]

        if filename:
            # Cria um objeto de imagem
            image = QtGui.QImage(filename)

            # Informa se não for possível carregar a imagem
            if image.isNull():
                popup = QtWidgets.QMessageBox()
                popup.critical(self, 'Erro ao carregar imagem', 'Não foi possível carregar a '
                                                                'imagem!', QtWidgets.QMessageBox.StandardButton.Ok)
            else:
                cursor = self.text.textCursor()
                cursor.insertImage(image)

    def word_count(self):
        wc = wordcount.WordCount(self)
        wc.get_text()
        wc.show()

    def context(self, pos):
        # Pega o cursor
        cursor = self.text.textCursor()

        # Pega a atual tabela, se houver uma
        current_table = cursor.currentTable()

        # A table vai retornar 0 se não encontrar uma tabela, nesse caso chamamos o menu de contexto normal.
        # Caso haja uma tabela, é criado nosso próprio menu de contexto para a tabela especifica
        if current_table:
            menu = QtWidgets.QMenu(self)

            append_row_action = QAction('Acrescentar linha', self)
            append_row_action.triggered.connect(lambda: current_table.appendRows(1))

            append_col_action = QAction('Acrescentar coluna', self)
            append_col_action.triggered.connect(lambda: current_table.appendColumns(1))

            remove_row_action = QAction('Remover linha', self)
            remove_row_action.triggered.connect(self.remove_row)

            remove_col_action = QAction('Remover coluna', self)
            remove_col_action.triggered.connect(self.remove_col)

            insert_row_action = QAction('Inserir linha', self)
            insert_row_action.triggered.connect(self.insert_row)

            insert_col_action = QAction('Inserir coluna', self)
            insert_col_action.triggered.connect(self.insert_col)

            merge_action = QAction('Mesclar células', self)
            merge_action.triggered.connect(lambda: current_table.mergeCells(cursor))

            # Apenas permite mesclar se houver uma seleção
            if not cursor.hasSelection():
                merge_action.setEnabled(False)

            split_action = QAction('Separar células', self)
            cell = current_table.cellAt(cursor)

            # Apenas permite separar se a célula atual é maior que uma célula normal
            if cell.rowSpan() > 1 or cell.columnSpan() > 1:
                split_action.triggered.connect(lambda: current_table.splitCell(cell.row(), cell.column(), 1, 1))
            else:
                split_action.setEnabled(False)

            menu.addAction(append_row_action)
            menu.addAction(append_col_action)

            menu.addSeparator()

            menu.addAction(remove_row_action)
            menu.addAction(remove_col_action)

            menu.addSeparator()

            menu.addAction(insert_row_action)
            menu.addAction(insert_col_action)

            menu.addSeparator()

            menu.addAction(merge_action)
            menu.addAction(split_action)

            # Converte as coordenadas em coordenadas globais
            pos = self.mapToGlobal(pos)

            # Adiciona pixels para as barras ferramentas e formato, que não são incluídas no mapToGlobal(), mas apenas
            # se ambas estiverem visíveis

            if self.toolbar.isVisible():
                pos.setY(pos.y() + 45)

            if self.formatbar.isVisible():
                pos.setY(pos.y() + 45)

            # Move o menu para a nova posição
            menu.move(pos)
            menu.show()
        else:
            event = QtGui.QContextMenuEvent(QtGui.QContextMenuEvent.Reason.Mouse, QtCore.QPoint())
            self.text.contextMenuEvent(event)

    def remove_row(self):
        self.insert_remove(table.Mode.REMOVE_ROW)

    def remove_col(self):
        self.insert_remove(table.Mode.REMOVE_COL)

    def insert_row(self):
        self.insert_remove(table.Mode.INSERT_ROW)

    def insert_col(self):
        self.insert_remove(table.Mode.INSERT_COL)

    def insert_remove(self, mode: table.Mode):
        # Pega o cursor
        cursor = self.text.textCursor()

        # Pega a tabela atual (É esperado que haja uma já que é checado antes de chamar essa função)
        current_table = cursor.currentTable()

        # Pega a célula atual
        cell = current_table.cellAt(cursor)

        # Verifica qual modo foi passado como parâmetro
        if mode == table.Mode.REMOVE_ROW:
            current_table.removeRows(cell.row(), 1)
        elif mode == table.Mode.REMOVE_COL:
            current_table.removeColumns(cell.column(), 1)
        elif mode == table.Mode.INSERT_ROW:
            current_table.insertRows(cell.row(), 1)
        elif mode == table.Mode.INSERT_COL:
            current_table.insertRows(cell.column(), 1)

    def changed(self):
        self.changes_saved = False

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.write_json()

        if self.changes_saved:
            event.accept()
        else:
            # Seta botões à variáveis
            save = QtWidgets.QMessageBox.StandardButton.Save
            cancel = QtWidgets.QMessageBox.StandardButton.Cancel
            discard = QtWidgets.QMessageBox.StandardButton.Discard

            # Cria um popup
            popup = QtWidgets.QMessageBox(self)

            # Aplica propriedades
            popup.setWindowTitle('O documento foi alterado')
            popup.setText('Deseja salvar as alterações?')
            popup.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            popup.setStandardButtons(save | cancel | discard)
            popup.setDefaultButton(save)

            # Altera o caption padrão dos botões
            popup.button(save).setText('Salvar')
            popup.button(cancel).setText('Cancelar')
            popup.button(discard).setText('Descartar')

            # Executa o popup e aguarda sua resposta para prosseguir o código
            answer = popup.exec()

            if answer == save:
                self.save()
            elif answer == discard:
                event.accept()
            else:
                event.ignore()

    def write_json(self):
        config = self.geometry()

        data = {
            'language': self.language,

            'width': config.width(),
            'height': config.height(),
            'x': config.x(),
            'y': config.y(),
            'maximized': self.isMaximized(),

            'toolbar': self.toolbar.isVisible(),
            'formatbar': self.formatbar.isVisible(),
            'statusbar': self.statusbar.isVisible()
        }

        with open('config.json', 'w') as f:
            f.write(json.dumps(data, indent=2))

    def read_json(self):
        if not os.path.exists('config.json'):
            self.default_config()

        with open('config.json', 'r') as f:
            return json.load(f)

    @staticmethod
    def default_config():
        default = {
            'language': 'English',

            'width': 600,
            'height': 1030,
            'x': 100,
            'y': 100,

            'maximized': False,
            'toolbar': True,
            'formatbar': True,
            'statusbar': True
        }

        with open('config.json', 'w') as f:
            f.write(json.dumps(default, indent=2))

    def init_toolbar(self):
        self.new_action = QAction(QIcon('icons/new.png'), 'Novo', self)
        self.new_action.setStatusTip('Cria um novo documento em branco. Ctrl+N')
        self.new_action.setShortcut('Ctrl+N')
        self.new_action.triggered.connect(self.new)

        self.open_action = QAction(QIcon('icons/open.png'), 'Abrir documento', self)
        self.open_action.setStatusTip('Abre um documento existente. Ctrl+O')
        self.open_action.setShortcut('Ctrl+O')
        self.open_action.triggered.connect(self.open)

        self.save_action = QAction(QIcon('icons/save.png'), 'Salvar', self)
        self.save_action.setStatusTip('Salva o atual documento. Ctrl+S')
        self.save_action.setShortcut('Ctrl+S')
        self.save_action.triggered.connect(self.save)

        self.print_action = QAction(QIcon('icons/print.png'), 'Imprimir', self)
        self.print_action.setStatusTip('Imprimir documento. Ctrl+P')
        self.print_action.setShortcut('Ctrl+P')
        self.print_action.triggered.connect(self.print)

        self.preview_action = QAction(QIcon('icons/preview.png'), 'Ver página', self)
        self.preview_action.setStatusTip('Ver página antes de imprimir. Ctrl+Shift+P')
        self.preview_action.setShortcut('Ctrl+Shift+P')
        self.preview_action.triggered.connect(self.preview)

        self.cut_action = QAction(QIcon('icons/cut.png'), 'Recortar para a área de transferência', self)
        self.cut_action.setStatusTip('Deleta e copia o texto para a área de transferência. Ctrl+X')
        self.cut_action.setShortcut('Ctrl+X')
        self.cut_action.triggered.connect(self.text.cut)

        self.copy_action = QAction(QIcon('icons/copy.png'), 'Copiar para a área de transferência', self)
        self.copy_action.setStatusTip('Copia o texto para a área de transferência. Ctrl+C')
        self.copy_action.setShortcut('Ctrl+C')
        self.copy_action.triggered.connect(self.text.copy)

        self.paste_action = QAction(QIcon('icons/paste.png'), 'Cola da área de transferência', self)
        self.paste_action.setStatusTip('Cola texto da área de transferência. Ctrl+V')
        self.paste_action.setShortcut('Ctrl+V')
        self.paste_action.triggered.connect(self.text.paste)

        self.undo_action = QAction(QIcon('icons/undo.png'), 'Desfaz a última ação', self)
        self.undo_action.setStatusTip('Desfaz a última ação. Ctrl+Z')
        self.undo_action.setShortcut('Ctrl+Z')
        self.undo_action.triggered.connect(self.text.undo)

        self.redo_action = QAction(QIcon('icons/redo.png'), 'Refaz a última ação desfeita', self)
        self.redo_action.setStatusTip('Refaz a última ação desfeita. Ctrl+Y')
        self.redo_action.setShortcut('Ctrl+Y')
        self.redo_action.triggered.connect(self.text.redo)

        # Não há a necessidade de declarar como membro da classe uma vez que essas duas ações só serão usadas aqui
        bulleted_action = QAction(QIcon('icons/bullet.png'), 'Inserir uma lista com marcadores', self)
        bulleted_action.setStatusTip('Insere uma lista com marcadores. Ctrl+Shift+B')
        bulleted_action.setShortcut('Ctrl+Shift+B')
        bulleted_action.triggered.connect(self.bulleted_list)

        numbered_action = QAction(QIcon('icons/number.png'), 'Inserir uma lista numerada', self)
        numbered_action.setStatusTip('Insere uma lista numerada. Ctrl+Shift+L')
        numbered_action.setShortcut('Ctrl+Shift+L')
        numbered_action.triggered.connect(self.numbered_list)

        self.find_action = QAction(QIcon('icons/find.png'), 'Procurar e substituir', self)
        self.find_action.setStatusTip('Procure e substitua palavras no seu documento. Ctrl+F')
        self.find_action.setShortcut('Ctrl+F')
        self.find_action.triggered.connect(find.Find(self).show)

        image_action = QAction(QIcon('icons/image.png'), 'Inserir uma imagem', self)
        image_action.setStatusTip('Inserir uma imagem. Ctrl+Shift+I')
        image_action.setShortcut('Ctrl+Shift+I')
        image_action.triggered.connect(self.insert_image)

        word_count_action = QAction(QIcon('icons/count.png'), 'Ver contagem de palavras e símbolos', self)
        word_count_action.setStatusTip('Ver contagem de palavras e símbolos. Ctrl+W')
        word_count_action.setShortcut('Ctrl+W')
        word_count_action.triggered.connect(self.word_count)

        datetime_action = QAction(QIcon('icons/calender.png'), 'Inserir data e hora atual', self)
        datetime_action.setStatusTip('Inserir data e hora atual. Ctrl+D')
        datetime_action.setShortcut('Ctrl+D')
        datetime_action.triggered.connect(datetime.DateTime(self).show)

        table_action = QAction(QIcon('icons/table.png'), 'Inserir tabela', self)
        table_action.setStatusTip('Inserir tabela. Ctrl+T')
        table_action.setShortcut('Ctrl+T')
        table_action.triggered.connect(table.Table(self).show)

        self.toolbar = self.addToolBar('Opções')

        # Remove o clique com o lado direito do mouse
        self.toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

        self.toolbar.addAction(self.new_action)
        self.toolbar.addAction(self.open_action)
        self.toolbar.addAction(self.save_action)

        self.toolbar.addSeparator()

        self.toolbar.addAction(self.print_action)
        self.toolbar.addAction(self.preview_action)

        self.toolbar.addSeparator()

        self.toolbar.addAction(self.cut_action)
        self.toolbar.addAction(self.copy_action)
        self.toolbar.addAction(self.paste_action)
        self.toolbar.addAction(self.undo_action)
        self.toolbar.addAction(self.redo_action)

        self.toolbar.addSeparator()

        self.toolbar.addAction(bulleted_action)
        self.toolbar.addAction(numbered_action)

        self.toolbar.addSeparator()

        self.toolbar.addAction(image_action)
        self.toolbar.addAction(datetime_action)
        self.toolbar.addAction(table_action)

        self.toolbar.addSeparator()

        self.toolbar.addAction(self.find_action)
        self.toolbar.addAction(word_count_action)

        # Faz a próxima barra de ferramentas aparecer abaixo da primeira
        self.addToolBarBreak()

    def init_formatbar(self):
        font_box = QtWidgets.QFontComboBox(self)
        font_box.currentFontChanged.connect(self.font_family)

        font_size = QtWidgets.QComboBox(self)
        font_size.setEditable(True)

        # Tamanho mínimo de caracteres mostrados
        font_size.setMinimumContentsLength(3)

        # Altera a fonte ao interagir com a caixa de tamanho de fontes
        font_size.activated.connect(self.font_size)

        # Tamanho típico de fontes
        font_sizes = ['6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '18', '20', '22', '24', '26', '28',
                      '32', '36', '40', '44', '48', '54', '60', '66', '72', '80', '88', '96']

        font_size.addItems(font_sizes)

        font_color = QAction(QIcon('icons/font-color.png'), 'Alterar a cor da fonte', self)
        font_color.setStatusTip('Alterar a cor da fonte.')
        font_color.triggered.connect(self.font_color)

        backcolor = QAction(QIcon('icons/highlight.png'), 'Alterar a cor de fundo da fonte', self)
        backcolor.setStatusTip('Alterar a cor de fundo da fonte.')
        backcolor.triggered.connect(self.highlight)

        bold_action = QAction(QIcon('icons/bold.png'), 'Negrito', self)
        bold_action.setStatusTip('Inserir negrito.')
        bold_action.triggered.connect(self.bold)

        italic_action = QAction(QIcon('icons/italic.png'), 'Itálico', self)
        italic_action.setStatusTip('Inserir itálico.')
        italic_action.triggered.connect(self.italic)

        under_action = QAction(QIcon('icons/underline.png'), 'Sublinhado', self)
        under_action.setStatusTip('Inserir sublinhado.')
        under_action.triggered.connect(self.underline)

        strike_action = QAction(QIcon('icons/strike.png'), 'Riscado', self)
        strike_action.setStatusTip('Inserir riscado.')
        strike_action.triggered.connect(self.strike)

        super_action = QAction(QIcon('icons/superscript.png'), 'Sobrescrito', self)
        super_action.setStatusTip('Inserir sobrescrito.')
        super_action.triggered.connect(self.super_script)

        sub_action = QAction(QIcon('icons/subscript.png'), 'Subscrito', self)
        sub_action.setStatusTip('Inserir subscrito.')
        sub_action.triggered.connect(self.sub_script)

        align_left = QAction(QIcon('icons/align-left.png'), 'Alinhar à esquerda', self)
        align_left.setStatusTip('Alinhar à esquerda.')
        align_left.triggered.connect(self.align_left)

        align_center = QAction(QIcon('icons/align-center.png'), 'Alinhar ao centro', self)
        align_center.setStatusTip('Alinhar ao centro.')
        align_center.triggered.connect(self.align_center)

        align_right = QAction(QIcon('icons/align-right.png'), 'Alinhar à direita', self)
        align_right.setStatusTip('Alinhar à direita.')
        align_right.triggered.connect(self.align_right)

        align_justify = QAction(QIcon('icons/align-justify.png'), 'Alinhar justificado', self)
        align_justify.setStatusTip('Alinhar justificado.')
        align_justify.triggered.connect(self.align_justify)

        indent_action = QAction(QIcon('icons/indent.png'), 'Recuar', self)
        indent_action.setStatusTip('Recuar. Ctrl+Tab')
        indent_action.setShortcut('Ctrl+Tab')
        indent_action.triggered.connect(self.indent)

        dedent_action = QAction(QIcon('icons/dedent.png'), 'Desfazer recuo', self)
        dedent_action.setStatusTip('Desfazer recuo. Shift+Tab')
        dedent_action.setShortcut('Shift+Tab')
        dedent_action.triggered.connect(self.dedent)

        self.formatbar = self.addToolBar('Formatar')

        # Remove o clique com o lado direito do mouse
        self.formatbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

        self.formatbar.addWidget(font_box)
        self.formatbar.addWidget(font_size)

        self.formatbar.addSeparator()

        self.formatbar.addAction(font_color)
        self.formatbar.addAction(backcolor)

        self.formatbar.addSeparator()

        self.formatbar.addAction(bold_action)
        self.formatbar.addAction(italic_action)
        self.formatbar.addAction(under_action)
        self.formatbar.addAction(strike_action)
        self.formatbar.addAction(super_action)
        self.formatbar.addAction(sub_action)

        self.formatbar.addSeparator()

        self.formatbar.addAction(align_left)
        self.formatbar.addAction(align_center)
        self.formatbar.addAction(align_right)
        self.formatbar.addAction(align_justify)

        self.formatbar.addSeparator()

        self.formatbar.addAction(indent_action)
        self.formatbar.addAction(dedent_action)

    def init_menubar(self):
        menubar = self.menuBar()

        file = menubar.addMenu('Arquivo')
        edit = menubar.addMenu('Editar')
        view = menubar.addMenu('Exibir')

        file.addAction(self.new_action)
        file.addAction(self.open_action)
        file.addAction(self.save_action)

        file.addAction(self.print_action)
        file.addAction(self.preview_action)

        edit.addAction(self.undo_action)
        edit.addAction(self.redo_action)
        edit.addAction(self.cut_action)
        edit.addAction(self.copy_action)
        edit.addAction(self.paste_action)

        edit.addAction(self.find_action)

        # Alternando ações para várias barras
        self.toolbar_action = QAction('Ocultar barra de ferramentas', self)
        self.toolbar_action.triggered.connect(self.toggle_toolbar)

        self.formatbar_action = QAction('Ocultar barra de formatação', self)
        self.formatbar_action.triggered.connect(self.toggle_formatbar)

        self.statusbar_action = QAction('Ocultar barra de status', self)
        self.statusbar_action.triggered.connect(self.toggle_statusbar)

        view.addAction(self.toolbar_action)
        view.addAction(self.formatbar_action)
        view.addAction(self.statusbar_action)


if __name__ == '__main__':
    sys.excepthook = exception_hook

    app = QApplication(sys.argv)
    window = Main()
    window.show()

    sys.exit(app.exec())
