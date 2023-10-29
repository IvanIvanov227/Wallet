from PyQt5 import uic
import sqlite3
# QMainWindow - главное окно приложения
# QTableWidgetItem - используется для отображения и редактирования данных в таблицах,
# таких как QTableWidget. Каждая ячейка таблицы представляется объектом QTableWidgetItem,
# который может содержать текст, числа, изображения и другие типы данных.
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt5 import QtWidgets

from expenses import Expense, UpdateExpense
from incomes import Income, UpdateIncome


class Wallet(QMainWindow):
    """Главное окно"""
    def __init__(self):
        super().__init__()
        # Формы изменения дохода и расхода
        self.update_form_expense = None
        self.update_form_income = None

        # Формы добавления дохода и расхода
        self.add_expenses = None
        self.add_incomes = None

        # id выбранной записи
        self.id_info_expense = None
        self.id_info_income = None

        # список id оставшихся записей
        self.id1 = []
        self.id2 = []

        uic.loadUi('ui/main.ui', self)

        self.con = sqlite3.connect('wallet.sqlite')

        # Добавление вариантов в фильтры
        self.setupComboBox()
        self.setupComboBoxSort()

        self.addIncomeButton.clicked.connect(self.add_income)
        self.editIncomeButton.clicked.connect(self.edit_income)
        self.deleteIncomeButton.clicked.connect(self.delete_income)
        self.learnIncomeButton.clicked.connect(self.learn_income)

        # Заголовки таблицы
        self.titles = ['Номер', "Дата", "Сумма", "Тип"]

        self.addExpenseButton.clicked.connect(self.add_expense)
        self.editExpenseButton.clicked.connect(self.edit_expense)
        self.deleteExpenseButton.clicked.connect(self.delete_expense)
        self.learnExpenseButton.clicked.connect(self.learn_expense)

        # Фильтры
        self.time = 10e20
        self.sort = ''

        # Нельзя изменять таблицы
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.update_income()
        self.update_expense()
        self.update_sum()

    def setupComboBox(self):
        """Добавление вариантов сортировки"""
        self.comboBoxIncome.addItems(['Все', 'За 1 день', 'За 2 дня', 'Неделю', 'Месяц', 'Полгода', 'Год'])
        self.comboBoxExpense.addItems(['Все', 'За 1 день', 'За 2 дня', 'Неделю', 'Месяц', 'Полгода', 'Год'])

    def setupComboBoxSort(self):
        """Добавление вариантов сортировки"""
        self.comboBoxSortIncome.addItems(['Никак', '↑ Даты', '↓ Даты', '↑ Дохода', '↓ Дохода'])
        self.comboBoxSortExpense.addItems(['Никак', '↑ Даты', '↓ Даты', '↑ Расхода', '↓ Расхода'])

    def update_sum(self):
        """Обновление баланса"""
        cur = self.con.cursor()

        result1 = cur.execute('SELECT SUM(expense_sum) FROM expense;').fetchone()[0]
        result2 = cur.execute('SELECT SUM(income_sum) FROM income;').fetchone()[0]
        if result1 is None:
            result1 = 0
        if result2 is None:
            result2 = 0
        if self.labelmoney_1.text() == '':
            self.labelmoney_1.setText('0')
        else:
            self.labelmoney_1.setText(str(round(result2 - result1, 2)) + " руб.")
        if self.labelmoney_2.text() == '':
            self.labelmoney_2.setText('0')
        else:
            self.labelmoney_2.setText(str(round(result2 - result1, 2)) + " руб.")

    def update_income(self):
        """Обновление отображаемой таблицы доходов"""
        cur = self.con.cursor()

        if self.sort == '↑ Даты':
            com = f"""
                        SELECT id, income_date, income_sum, income_type FROM income WHERE
                        julianday('now') - julianday(income_date) < ? 
                        ORDER BY income_date ASC;
            """
        elif self.sort == '↓ Даты':
            com = f"""
                        SELECT id, income_date, income_sum, income_type FROM income WHERE
                        julianday('now') - julianday(income_date) < ? 
                        ORDER BY income_date DESC;
            """
        elif self.sort == '↑ Дохода':
            com = f"""
                        SELECT id, income_date, income_sum, income_type FROM income WHERE
                        julianday('now') - julianday(income_date) < ? 
                        ORDER BY income_sum ASC;
            """
        elif self.sort == '↓ Дохода':
            com = f"""
                        SELECT id, income_date, income_sum, income_type FROM income WHERE
                        julianday('now') - julianday(income_date) < ? 
                        ORDER BY income_sum DESC;
            """
        else:
            com = f"""
                        SELECT id, income_date, income_sum, income_type FROM income WHERE
                        julianday('now') - julianday(income_date) < ?;
            """

        # Выполнение запроса с передачей параметров
        result = cur.execute(com, (self.time,)).fetchall()
        self.tableWidget.setRowCount(len(result))

        if not result:
            self.tableWidget.setColumnCount(0)
        else:
            self.tableWidget.setColumnCount(len(result[0]))

        self.tableWidget.setHorizontalHeaderLabels(self.titles)
        for i, row in enumerate(result):
            self.tableWidget.setVerticalHeaderItem(i, QTableWidgetItem(''))
            for j, itm in enumerate(row):
                if j == 0:
                    if [itm, i + 1] not in self.id1:
                        self.id1.append([itm, i + 1])
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(i + 1)))

                else:
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(itm) if j != 2 else str(itm) + " руб."))

        self.tableWidget.resizeRowsToContents()
        self.tableWidget.resizeColumnsToContents()
        self.update_sum()

    def update_expense(self):
        """Обновление отображаемой таблицы расходов"""
        cur = self.con.cursor()
        if self.sort == '↑ Даты':
            com = f"""
                        SELECT id, expense_date, expense_sum, expense_type FROM expense WHERE
                        julianday('now') - julianday(expense_date) < ? 
                        ORDER BY expense_date ASC;
            """
        elif self.sort == '↓ Даты':
            com = f"""
                        SELECT id, expense_date, expense_sum, expense_type FROM expense WHERE
                        julianday('now') - julianday(expense_date) < ? 
                        ORDER BY expense_date DESC;
            """
        elif self.sort == '↑ Расхода':
            com = f"""
                        SELECT id, expense_date, expense_sum, expense_type FROM expense WHERE
                        julianday('now') - julianday(expense_date) < ? 
                        ORDER BY expense_sum ASC;
            """
        elif self.sort == '↓ Расхода':
            com = f"""
                        SELECT id, expense_date, expense_sum, expense_type FROM expense WHERE
                        julianday('now') - julianday(expense_date) < ? 
                        ORDER BY expense_sum DESC;
            """
        else:
            com = f"""
                        SELECT id, expense_date, expense_sum, expense_type FROM expense WHERE
                        julianday('now') - julianday(expense_date) < ?;
            """

        result = cur.execute(com, (self.time,)).fetchall()
        self.tableWidget_2.setRowCount(len(result))

        if not result:
            self.tableWidget_2.setColumnCount(0)
        else:
            self.tableWidget_2.setColumnCount(len(result[0]))

        self.tableWidget_2.setHorizontalHeaderLabels(self.titles)
        for i, row in enumerate(result):
            self.tableWidget_2.setVerticalHeaderItem(i, QTableWidgetItem(''))
            for j, itm in enumerate(row):
                if j == 0:
                    if [itm, i + 1] not in self.id2:
                        self.id2.append([itm, i + 1])
                    self.tableWidget_2.setItem(i, j,
                                               QTableWidgetItem(str(i + 1)))

                else:
                    self.tableWidget_2.setItem(i, j, QTableWidgetItem(str(itm) if j != 2 else str(itm) + " руб."))

        self.tableWidget_2.resizeRowsToContents()
        self.tableWidget_2.resizeColumnsToContents()
        self.update_sum()

    def add_income(self):
        """Нажатие кнопки 'Добавить доход'"""
        self.add_incomes = Income(self.update_income)
        self.add_incomes.show()

    def edit_income(self):
        """Нажатие кнопки 'Изменить доход'"""
        # Устанавливается пустой текст для label, который используется для отображения ошибок
        self.labelIncome.setText('')
        # Выбрана ли строка?
        if len(self.tableWidget.selectedItems()) == 1:
            # Создаётся виджет для изменения контакта
            self.update_form_income = UpdateIncome(self.update_income)
            # self.tableWidget.currentRow() возвращает индекс текущей выбранной строки, а i - столбца
            # В функцию передаётся список значений выбранной строки.
            for i in self.id1:
                if i[1] == self.tableWidget.currentRow() + 1:
                    self.id_info_income = i
            self.update_form_income.save_dialog([self.id_info_income] +
                                                [self.tableWidget.item(self.tableWidget.currentRow(), i).text()
                                                for i in range(1, 4)])
            # Отображение виджета
            self.update_form_income.show()

        # Не выбрал строку
        else:
            self.labelIncome.setText('Некорректные данные')

    def delete_income(self):
        """Нажатие кнопки 'Удалить доход'"""
        self.labelIncome.setText('')
        # Выбрана ли строка?
        if len(self.tableWidget.selectedItems()) == 1:
            # Нахождение выбранной записи
            for i in self.id1:
                if i[1] == self.tableWidget.currentRow() + 1:
                    self.id_info_income = i

            cur = self.con.cursor()
            com = '''
                    DELETE FROM income WHERE id = (?);
            '''
            cur.execute(com, (self.id_info_income[0],))

            # Добавление в список остальных записей
            for i in range(len(self.id1)):
                if self.id1[i][0] == self.id_info_income:
                    del self.id1[i]
                    for j in range(i, len(self.id1)):
                        self.id1[j] = [self.id1[j][0], self.id1[j][1] - 1]

            self.con.commit()
            self.update_income()

        # Не выбрал строку
        else:
            self.labelIncome.setText('Некорректные данные')

    def learn_income(self):
        """Нажатие кнопки 'Узнать'"""
        period = self.comboBoxIncome.currentText()
        sort = self.comboBoxSortIncome.currentText()
        self.learn(period, sort)
        self.update_income()

    def learn(self, period, sort):
        """Получает выбранные параметры фильтрации"""
        if period == 'Все':
            self.time = 10e18
        if period == 'За 1 день':
            self.time = 1
        if period == 'За 2 дня':
            self.time = 2
        if period == 'Неделю':
            self.time = 7
        if period == 'Месяц':
            self.time = 31
        if period == 'Полгода':
            self.time = 183
        if period == 'Год':
            self.time = 365

        self.sort = sort

    def add_expense(self):
        """Нажатие кнопки 'Добавить расход'"""
        self.add_expenses = Expense(self.update_expense)
        self.add_expenses.show()

    def edit_expense(self):
        """Нажатие кнопки 'Изменить расход'"""
        # Устанавливается пустой текст для label, который используется для отображения ошибок
        self.labelExpense.setText('')
        # Выбрана ли строка?
        if len(self.tableWidget_2.selectedItems()) == 1:
            # Создаётся виджет для изменения контакта
            self.update_form_expense = UpdateExpense(self.update_expense)
            # self.tableWidget.currentRow() возвращает индекс текущей выбранной строки, а i - столбца
            # В функцию передаётся список значений выбранной строки.
            for i in self.id2:
                if i[1] == self.tableWidget_2.currentRow() + 1:
                    self.id_info_expense = i

            self.update_form_expense.save_dialog([self.id_info_expense] +
                                                 [self.tableWidget_2.item(self.tableWidget_2.currentRow(), i).text()
                                                 for i in range(1, 4)])
            # Отображение виджета
            self.update_form_expense.show()

        # Не выбрал строку
        else:
            self.labelExpense.setText('Некорректные данные')

    def delete_expense(self):
        """Нажатие кнопки 'Удалить расход'"""
        self.labelExpense.setText('')
        # Выбрана ли строка или строки?
        if len(self.tableWidget_2.selectedItems()) == 1:
            for i in self.id2:
                if i[1] == self.tableWidget_2.currentRow() + 1:
                    self.id_info_expense = i

            cur = self.con.cursor()
            com = '''
                    DELETE FROM expense WHERE id = (?);
            '''
            cur.execute(com, (self.id_info_expense[0],))

            for i in range(len(self.id2)):
                if self.id2[i][0] == self.id_info_expense:
                    del self.id2[i]
                    for j in range(i, len(self.id2)):
                        self.id2[j] = [self.id2[j][0], self.id2[j][1] - 1]

            self.con.commit()
            self.update_expense()

        # Не выбрал строку
        else:
            self.labelExpense.setText('Некорректные данные')

    def learn_expense(self):
        """Нажатие кнопки 'Узнать'"""
        period = self.comboBoxExpense.currentText()
        sort = self.comboBoxSortExpense.currentText()
        self.learn(period, sort)
        self.update_expense()
