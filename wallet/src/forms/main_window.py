from PyQt5 import uic
import sqlite3
# QMainWindow - главное окно приложения
# QTableWidgetItem - используется для отображения и редактирования данных в таблицах,
# таких как QTableWidget. Каждая ячейка таблицы представляется объектом QTableWidgetItem,
# который может содержать текст, числа, изображения и другие типы данных.
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt5 import QtWidgets

from wallet.src.forms.expenses import Expense, UpdateExpense
from wallet.src.forms.incomes import Income, UpdateIncome


class Wallet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.update_form_expense = None
        self.update_form_income = None
        self.id_info_expense = None
        self.id_info_income = None
        self.id1 = set()
        self.id2 = set()
        self.edit_expenses = None
        self.add_expenses = None
        self.add_incomes = None
        self.edit_incomes = None
        uic.loadUi('ui/main.ui', self)

        self.con = sqlite3.connect('wallet.sqlite')

        self.setupComboBox()

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

        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget_2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.update_income()
        self.update_expense()
        self.update_sum()

    def setupComboBox(self):
        self.comboBoxIncome.addItems(['Все', 'Сегодня', 'Вчера', 'Неделю', 'Месяц', 'Полгода', 'Год', 'Другое'])
        self.comboBoxExpense.addItems(['Все', 'Сегодня', 'Вчера', 'Неделю', 'Месяц', 'Полгода', 'Год', 'Другое'])

    def update_sum(self):
        cur = self.con.cursor()
        com1 = """
                SELECT SUM(expense_sum) FROM expense;
        """
        com2 = """
                SELECT SUM(income_sum) FROM income;
        """
        result1 = cur.execute(com1).fetchone()[0]
        result2 = cur.execute(com2).fetchone()[0]
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
        cur = self.con.cursor()
        com = """
        SELECT id, income_date, income_sum, income_type FROM income;
        """
        result = cur.execute(com).fetchall()
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
                    self.id1.add(str(itm) + ' ' + str(i + 1))
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(i + 1)))

                else:
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(itm) if j != 2 else str(itm) + " руб."))
                item = self.tableWidget.item(i, j)

        self.tableWidget.resizeRowsToContents()
        self.tableWidget.resizeColumnsToContents()
        self.update_sum()

    def update_expense(self):
        cur = self.con.cursor()
        com = """
        SELECT id, expense_date, expense_sum, expense_type FROM expense;
        """
        result = cur.execute(com).fetchall()
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
                    self.id2.add(str(itm) + ' ' + str(i + 1))
                    self.tableWidget_2.setItem(i, j,
                                               QTableWidgetItem(str(i + 1)))

                else:
                    self.tableWidget_2.setItem(i, j, QTableWidgetItem(str(itm) if j != 2 else str(itm) + " руб."))
                item = self.tableWidget_2.item(i, j)

        self.tableWidget_2.resizeRowsToContents()
        self.tableWidget_2.resizeColumnsToContents()
        self.update_sum()

    def add_income(self):
        self.add_incomes = Income(self.update_income)
        self.add_incomes.show()

    def edit_income(self):
        # Устанавливается пустой текст для label, который используется для отображения ошибок
        self.labelIncome.setText('')
        # Выбрана ли строка?
        if len(self.tableWidget.selectedItems()) == 1:
            # Создаётся виджет для изменения контакта
            self.update_form_income = UpdateIncome(self.update_income)
            # self.tableWidget.currentRow() возвращает индекс текущей выбранной строки, а i - столбца
            # В функцию передаётся список значений выбранной строки.
            for i in self.id1:
                if int(i.split()[1]) == self.tableWidget.currentRow() + 1:
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
        self.labelIncome.setText('')
        # Выбрана ли строка?
        if len(self.tableWidget.selectedItems()) == 1:
            for i in self.id1:
                if int(i.split()[1]) == self.tableWidget.currentRow() + 1:
                    self.id_info_income = i

            cur = self.con.cursor()
            com = '''
            DELETE FROM income WHERE id = (?);
            '''
            cur.execute(com, (int(self.id_info_income.split()[0]), ))
            for i in self.id1:
                if int(i.split()[0]) == self.id_info_income:
                    self.id1.remove(i)
            self.con.commit()
            self.update_income()

        # Не выбрал строку
        else:
            self.labelIncome.setText('Некорректные данные')

    def learn_income(self):
        ...

    def add_expense(self):
        self.add_expenses = Expense(self.update_expense)
        self.add_expenses.show()

    def edit_expense(self):
        # Устанавливается пустой текст для label, который используется для отображения ошибок
        self.labelExpense.setText('')
        # Выбрана ли строка?
        if len(self.tableWidget_2.selectedItems()) == 1:
            # Создаётся виджет для изменения контакта
            self.update_form_expense = UpdateExpense(self.update_expense)
            # self.tableWidget.currentRow() возвращает индекс текущей выбранной строки, а i - столбца
            # В функцию передаётся список значений выбранной строки.
            for i in self.id2:
                if int(i.split()[1]) == self.tableWidget_2.currentRow() + 1:
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
        self.labelExpense.setText('')
        # Выбрана ли строка?

        if len(self.tableWidget_2.selectedItems()) == 1:
            for i in self.id2:
                if int(i.split()[1]) == self.tableWidget_2.currentRow() + 1:
                    self.id_info_expense = i

            cur = self.con.cursor()
            com = '''
                    DELETE FROM expense WHERE id = (?);
                    '''
            cur.execute(com, (int(self.id_info_expense.split()[0]),))
            for i in self.id2:
                if int(i.split()[0]) == self.id_info_expense:
                    self.id2.remove(i)
            self.con.commit()
            self.update_expense()

        # Не выбрал строку
        else:
            self.labelExpense.setText('Некорректные данные')

    def learn_expense(self):
        ...
