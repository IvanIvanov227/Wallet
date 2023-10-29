from PyQt5.QtWidgets import QWidget
from PyQt5 import uic
import sqlite3
from datetime import time
from PyQt5.QtCore import QDate
from datetime import datetime


class Expense(QWidget):
    """Виджет добавления расхода"""
    def __init__(self, update):
        super().__init__()
        uic.loadUi('ui/addexpense.ui', self)
        self.AddExpenseButtonSave_2.clicked.connect(self.add_info_expense)
        self.con = sqlite3.connect('wallet.sqlite')
        self.date = None
        self.update = update

    def add_info_expense(self):
        """Получение данных и вставление данных в таблицу"""
        # Дата
        selected_date = self.calendarWidget.selectedDate().toString("yyyy-MM-dd")
        # Часы и секунды
        hour, minute = self.timeEdit.time().hour(), self.timeEdit.time().minute()
        if hour < 10:
            hour = '0' + str(hour)
        else:
            hour = str(hour)
        if minute < 10:
            minute = '0' + str(minute)
        # Сумма
        summa = self.lineEdit.text()
        # Тип дохода
        type_expense = self.lineEdit_2.text()
        if not type_expense:
            self.labelEditErrorExpense.setText('Заполни поле типа расхода')
        elif len(type_expense) > 100:
            self.labelEditErrorExpense.setText('Длина типа расхода только <= 100')
        elif not summa:
            self.labelEditErrorExpense.setText('Заполни поле суммы')
        elif selected_date > datetime.today().strftime('%Y-%m-%d'):
            self.labelEditErrorExpense.setText('Только за прошедшие и за нынешний день')
        else:
            try:
                if ',' in str(summa):
                    summa = round(float(str(summa).replace(',', '.')), 2)
                elif '.' in str(summa):
                    summa = round(float(summa), 2)
                else:
                    summa = int(summa)
                if summa <= 0:
                    raise TypeError
            except ValueError:
                self.labelEditErrorExpense.setText('В поле суммы только число!')
            except TypeError:
                self.labelEditErrorExpense.setText('Число только больше 0')
            else:
                cur = self.con.cursor()
                cur.execute('INSERT INTO expense (expense_date, expense_sum, expense_type) '
                            'VALUES (?, ?, ?);', (f"{selected_date} {hour}:{minute}", summa, type_expense))
                self.con.commit()
                self.update()
                self.hide()


class UpdateExpense(QWidget):
    """Обновление уже существующей записи"""
    def __init__(self, update):
        super().__init__()
        uic.loadUi('ui/editexpense.ui', self)
        self.con = sqlite3.connect('wallet.sqlite')
        self.update = update
        self.id = None
        self.expense_date = None
        self.expense_sum = None
        self.expense_type = None
        self.EditExpenseButtonSave_2.clicked.connect(self.edit_expense)

    def save_dialog(self, info: list):
        """Получение данных уже в существующей записи"""
        self.id = info[0][0]
        self.expense_date = info[1]
        year = int(self.expense_date.split('-')[0])
        month = int(self.expense_date.split('-')[1])
        day = int(''.join(self.expense_date.split('-')[2]).split()[0])
        hour = int(''.join(self.expense_date.split(':')[0]).split()[-1])
        minute = int(self.expense_date.split(':')[-1])
        self.timeEdit.setTime(time(hour, minute))
        new_date = QDate(year, month, day)  # Устанавливаем новую дату
        self.calendarWidget.setSelectedDate(new_date)
        self.lineEdit.setText(str(info[2]).split()[0])
        self.lineEdit_2.setText(str(info[3]))

    def edit_expense(self):
        """Получение данных уже в существующей записи"""
        # Дата
        selected_date = self.calendarWidget.selectedDate().toString("yyyy-MM-dd")
        # Часы и секунды
        hour, minute = self.timeEdit.time().hour(), self.timeEdit.time().minute()
        if hour < 10:
            hour = '0' + str(hour)
        else:
            hour = str(hour)
        if minute < 10:
            minute = '0' + str(minute)
        # Сумма
        summa = self.lineEdit.text()
        # Тип дохода
        type_expense = self.lineEdit_2.text()
        if not type_expense:
            self.labelEditErrorExpense.setText('Заполни поле типа расхода')
        elif not summa:
            self.labelEditErrorExpense.setText('Заполни поле суммы')
        elif selected_date > datetime.today().strftime('%Y-%m-%d'):
            self.labelEditErrorExpense.setText('Только за прошедшие и за нынешний день')
        else:
            try:
                if ',' in str(summa):
                    summa = round(float(str(summa).replace(',', '.')), 2)
                elif '.' in str(summa):
                    summa = round(float(summa), 2)
                else:
                    summa = int(summa)
                if summa <= 0:
                    raise TypeError
            except ValueError:
                self.labelEditErrorExpense.setText('В поле суммы только число!')
            except TypeError:
                self.labelEditErrorExpense.setText('Число только больше 0')
            else:
                cur = self.con.cursor()
                cur.execute('UPDATE expense '
                            'SET expense_date = (?), expense_sum = (?), expense_type = (?) WHERE id = (?);',
                            (f"{selected_date} {hour}:{minute}", summa, type_expense, self.id))
                self.con.commit()
                self.update()
                self.hide()
