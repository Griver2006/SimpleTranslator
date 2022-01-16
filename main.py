import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidgetItem, QStackedWidget


# Загрузка базы данных
con = sqlite3.connect('Databases/Words_db.db')
cur = con.cursor()


# Главное окно перевода и добавление слов
class MainMenuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/translator.ui', self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Переводчик')
        # Назначаем функии кнопкам
        self.radiobuttonGroup.buttonClicked.connect(self.replace_text)
        self.btn_translate_add.clicked.connect(self.add_translate_word)
        self.btn_toList.clicked.connect(self.table_window_open)

    # Функия добавления и перевода слов
    def add_translate_word(self):
        word_chechen = self.lineEdit_che.text()
        if self.sender().text() == 'Перевести':
            # ищем перевод слова из поля ввода lineEdit_che в таблице, если находим то
            # lineEdit_ru выставляем его, иначе в статус баре показываем ошибку
            word_russian = cur.execute(f"""SELECT word_russian FROM Words
                                           Where word_chechen = '{word_chechen.lower()}'
                                        """).fetchone()
            if word_russian:
                self.lineEdit_ru.setText(word_russian[0])
            else:
                self.statusBar().showMessage('Слово не найдено')
        if self.sender().text() == 'Добавить':
            word_russian = self.lineEdit_ru.text()
            if word_russian and word_chechen:
                cur.execute(f"""INSERT INTO Words(word_chechen, word_russian)
                                VALUES('{word_chechen.lower()}', '{word_russian.lower()}')""")
                self.lineEdit_ru.setText('')
                self.lineEdit_che.setText('')
                self.statusBar().showMessage('Слово успешно добавлено')
            con.commit()

    # При смене radiobutton меняет текст на кнопке и сбрасывает поля ввода
    def replace_text(self):
        if self.sender().checkedButton().text() == 'Добавление':
            self.btn_translate_add.setText('Добавить')
            self.lineEdit_ru.setReadOnly(False)
            self.lineEdit_ru.setText('')
            self.lineEdit_che.setText('')
        else:
            self.btn_translate_add.setText('Перевести')
            self.lineEdit_ru.setText('')
            self.lineEdit_che.setText('')
            self.lineEdit_ru.setReadOnly(True)

    # # Функия сменяющая главное окно, на окно с таблицей
    def table_window_open(self):
        table_window = TableWindow()
        stacked_widget.addWidget(table_window)
        stacked_widget.setCurrentIndex(stacked_widget.indexOf(table_window))


# Окно с таблицей слов
class TableWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/words_table.ui', self)
        self.initUI()

    def initUI(self):
        stacked_widget.setFixedSize(791, 558)
        # Назначаем функии кнопкам
        self.btn_return.clicked.connect(self.to_return)
        self.btn_remove.clicked.connect(self.remove_selected_operations)
        self.load_table()

    def load_table(self):
        # собираем данные из таблицы Words
        data = reversed(cur.execute(f"""SELECT * FROM Words""").fetchall())
        # Загрузка таблицы
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["id", "Слово на чеченском",
                                                    "Слово на русском"])
        self.tableWidget.setRowCount(0)
        # Загружаем таблицу
        for i, row in enumerate(data):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

    # Функия удаляющая строки где выделенне хоть одна ячейка
    def remove_selected_operations(self):
        # собираем снизу вверх все номера строк из таблицы
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))[::-1]
        data = []
        # Добавляем в data строку, где выделянна ячейка для того чтобы, удалить данные из базы
        for i in rows:
            temp_data = []
            for j in range(self.tableWidget.columnCount()):
                temp_data.append(self.tableWidget.item(i, j).text())
            data.append(temp_data)
        # Сначала удаляем строки из таблицы
        for index in rows:
            self.tableWidget.model().removeRow(index)
        # Теперь удаляям данные из базы
        for item in data:
            cur.execute(f"""DELETE FROM Words 
                            WHERE id = {item[0]}""")
        cur.execute("""UPDATE SQLITE_SEQUENCE SET seq = 0
                       WHERE name = 'Words'""")
        con.commit()

    # Функия возвращения на главное окно
    def to_return(self):
        stacked_widget.setFixedSize(785, 130)
        stacked_widget.setCurrentIndex(0)
        stacked_widget.removeWidget(self)


# Функия не дающая вылетить программе + показывающая ошибку
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Создаём объект который будеть хранить окна (классы окон)
    stacked_widget = QStackedWidget()

    # Создаём главное окно и добавляем его в stacked_widget
    main_menu_window = MainMenuWindow()
    stacked_widget.addWidget(main_menu_window)

    # выставляем размер и запускаем stacked_widget
    stacked_widget.setGeometry(500, 500, 785, 130)
    stacked_widget.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())