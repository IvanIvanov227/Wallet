from PyQt5.QtWidgets import QWidget, QCalendarWidget
from PyQt5 import uic
import sqlite3
from datetime import time
from PyQt5.QtCore import QDate


class Income(QWidget):
    def __init__(self, update):
        super().__init__()
        uic.loadUi('ui/addincome.ui', self)
        self.AddIncomeButtonSave.clicked.connect(self.add_info_income)
        self.con = sqlite3.connect('wallet.sqlite')
        self.date = None
        self.update = update

    def add_info_income(self):
        # Дата
        selected_date = self.calendarWidget.selectedDate().toString("yyyy-MM-dd")
        # Часы и секунды
        hour, minute = self.timeEdit.time().hour(), self.timeEdit.time().minute()
        if minute < 10:
            minute = '0' + str(minute)
        # Сумма
        summa = self.lineEdit.text()
        # Тип дохода
        type_income = self.lineEdit_2.text()
        if not type_income:
            self.labelEditErrorIncome.setText('Заполни поле типа дохода')
        elif not summa:
            self.labelEditErrorIncome.setText('Заполни поле суммы')
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
                self.labelEditErrorIncome.setText('В поле суммы только число!')
            except TypeError:
                self.labelEditErrorIncome.setText('Доход только больше 0')
            else:
                cur = self.con.cursor()
                cur.execute('INSERT INTO income (income_date, income_sum, income_type) '
                            'VALUES (?, ?, ?);', (f"{selected_date} {hour}:{minute}", summa, type_income))
                self.con.commit()
                self.update()
                self.hide()


class UpdateIncome(QWidget):
    def __init__(self, update):
        super().__init__()
        uic.loadUi('ui/editincome.ui', self)
        self.con = sqlite3.connect('wallet.sqlite')
        self.update = update
        self.id = None
        self.income_date = None
        self.income_sum = None
        self.income_type = None
        self.EditIncomeButtonSave.clicked.connect(self.edit_income)

    def save_dialog(self, info: list):
        self.id = int(info[0].split()[0])
        self.income_date = info[1]
        year = int(self.income_date.split('-')[0])
        month = int(self.income_date.split('-')[1])
        day = int(''.join(self.income_date.split('-')[2]).split()[0])
        hour = int(''.join(self.income_date.split(':')[0]).split()[-1])
        minute = int(self.income_date.split(':')[-1])
        self.timeEdit_2.setTime(time(hour, minute))
        new_date = QDate(year, month, day)  # Устанавливаем новую дату
        self.calendarWidget.setSelectedDate(new_date)
        self.lineEdit.setText(str(info[2]).split()[0])
        self.lineEdit_2.setText(str(info[3]))

    def edit_income(self):
        # Дата
        selected_date = self.calendarWidget.selectedDate().toString("yyyy-MM-dd")
        # Часы и секунды
        hour, minute = self.timeEdit_2.time().hour(), self.timeEdit_2.time().minute()
        if minute < 10:
            minute = '0' + str(minute)
        # Сумма
        summa = self.lineEdit.text()
        # Тип дохода
        type_income = self.lineEdit_2.text()
        if not type_income:
            self.labelEditErrorIncome.setText('Заполни поле типа дохода')
        elif not summa:
            self.labelEditErrorIncome.setText('Заполни поле суммы')
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
                self.labelEditErrorIncome.setText('В поле суммы только число!')
            except TypeError:
                self.labelEditErrorIncome.setText('Доход только больше 0')
            else:
                cur = self.con.cursor()
                cur.execute('UPDATE income SET income_date = (?), income_sum = (?), income_type = (?) WHERE id = (?);',
                            (f"{selected_date} {hour}:{minute}", summa, type_income, self.id))
                self.con.commit()
                self.update()
                self.hide()
