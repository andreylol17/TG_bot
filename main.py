import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import psycopg2

class LoginWindow(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Авторизация")
        self.resize(950, 1000)

        self.username_label = QtWidgets.QLabel("Имя пользователя: (admin)")
        self.password_label = QtWidgets.QLabel("Пароль: (qwerty)")
        self.username_input = QtWidgets.QLineEdit()
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        self.login_button = QtWidgets.QPushButton("Войти")
        self.login_button.setStyleSheet(
            "background-color: #4CAF50; color: white; font-size: 36px; border-radius: 15px;"
        )

        self.error_label = QtWidgets.QLabel()
        self.error_label.setStyleSheet("color: red; font-size: 36px")

        font = QtGui.QFont()
        font.setPointSize(36)
        self.setFont(font)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.username_label, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.username_input, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.password_label, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.password_input, alignment=QtCore.Qt.AlignCenter)

        self.username_input.setFixedSize(700, 80)
        self.password_input.setFixedSize(700, 80)

        self.login_button.setFixedSize(700, 80)
        layout.addWidget(self.login_button, alignment=QtCore.Qt.AlignCenter)

        layout.addWidget(self.error_label, alignment=QtCore.Qt.AlignCenter)

        self.setLayout(layout)

        self.login_button.clicked.connect(self.login)
        self.password_input.returnPressed.connect(self.login)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "qwerty":
            self.error_label.setText("")
            self.close()
            self.main_window.show()
        else:
            self.error_label.setText("Введен неправильный логин или пароль 😔")


class TableViewWindow(QtWidgets.QWidget):
    def __init__(self, table_name, main_window):
        super().__init__()
        self.table_name = table_name
        self.main_window = main_window
        self.setWindowTitle(f"Таблица {table_name}")
        self.resize(950, 1000)

        self.table = QtWidgets.QTableWidget()
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.table)

        # Первая строка кнопок
        if table_name == "accounts":
            add_to_sale_button = QtWidgets.QPushButton("Добавить на продажу")
            add_to_sale_button.setStyleSheet(
                "background-color: #008000; color: white; font-size: 24px; border-radius: 10px;"
            )
            add_to_sale_button.clicked.connect(self.add_account_to_sales)

            save_changes_button = QtWidgets.QPushButton("Сохранить изменения")
            save_changes_button.setStyleSheet(
                "background-color: #008000; color: white; font-size: 24px; border-radius: 10px;"
            )
            save_changes_button.clicked.connect(self.save_changes)
        else:
            add_to_sale_button = save_changes_button = QtWidgets.QWidget()

        # Вторая строка кнопок
        back_button = QtWidgets.QPushButton("Назад")
        back_button.setStyleSheet(
            "background-color: #FF0000; color: white; font-size: 24px; border-radius: 10px;"
        )
        back_button.clicked.connect(self.show_main_menu)

        delete_button = QtWidgets.QPushButton("Удалить")
        delete_button.setStyleSheet(
            "background-color: #FF0000; color: white; font-size: 24px; border-radius: 10px;"
        )
        delete_button.clicked.connect(self.delete_selected_row)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.scroll_area)

        main_layout.setContentsMargins(50, 0, 50, 0)

        # Добавление кнопок в две строки
        layout_buttons_row1 = QtWidgets.QHBoxLayout()
        layout_buttons_row1.addWidget(add_to_sale_button, alignment=QtCore.Qt.AlignCenter)
        layout_buttons_row1.addWidget(save_changes_button, alignment=QtCore.Qt.AlignCenter)

        layout_buttons_row2 = QtWidgets.QHBoxLayout()
        layout_buttons_row2.addWidget(back_button, alignment=QtCore.Qt.AlignCenter)
        layout_buttons_row2.addWidget(delete_button, alignment=QtCore.Qt.AlignCenter)

        main_layout.addLayout(layout_buttons_row1)
        main_layout.addLayout(layout_buttons_row2)

        self.setLayout(main_layout)

        delete_button.setFixedSize(420, 60)
        back_button.setFixedSize(420, 60)

        # Установка размера кнопки "Сохранить изменения" только для таблицы "accounts"
        if table_name == "accounts":
            save_changes_button.setFixedSize(420, 60)
            add_to_sale_button.setFixedSize(420, 60)

        self.load_data(table_name)

    def load_data(self, table_name):
        try:
            conn = psycopg2.connect(
                host="localhost",
                port="5433",
                database="DB_proekt",
                user="postgres",
                password="2005"
            )
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()

            cursor.close()
            conn.close()

            if not data:
                print(f"Таблица {table_name} пуста.")
                return

            self.table.setRowCount(len(data))
            self.table.setColumnCount(len(data[0]))

            headers = ["ID", "Link", "Steam Level", "Games", "Price", "login", "password", "card", "chat"]
            self.table.setHorizontalHeaderLabels(headers)

            for row in range(len(data)):
                for col in range(len(data[row])):
                    try:
                        item = QtWidgets.QTableWidgetItem(str(data[row][col]))
                        self.table.setItem(row, col, item)
                    except IndexError as e:
                        print(f"Ошибка при установке элемента в таблицу: {e}")

            self.table.resizeColumnsToContents()
            self.table.horizontalHeader().setStretchLastSection(True)

        except Exception as e:
            print(f"Ошибка загрузки данных для {table_name}: {e}")

    def add_account_to_sales(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            account_id = self.table.item(selected_row, 0).text()
            self.add_account_to_sales_db(account_id)
            self.remove_account_from_accounts_db(account_id)

    def add_account_to_sales_db(self, account_id):
        try:
            conn = psycopg2.connect(
                host="localhost",
                port="5433",
                database="DB_proekt",
                user="postgres",
                password="2005"
            )
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO sale (account_link, steam_level, games, price, login, password) "
                "SELECT account_link, steam_level, games, price, login, password FROM accounts WHERE account_id = %s RETURNING *",
                (account_id,)
            )
            conn.commit()

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка при добавлении аккаунта в sale: {e}")

    def delete_selected_row(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            account_id = self.table.item(selected_row, 0).text()
            if self.table_name == "accounts":
                self.remove_account_from_accounts_db(account_id)
            elif self.table_name == "sale":
                self.remove_account_from_sales_db(account_id)
                self.load_data("sale")

    def remove_account_from_sales_db(self, account_id):
        try:
            conn = psycopg2.connect(
                host="localhost",
                port="5433",
                database="DB_proekt",
                user="postgres",
                password="2005"
            )
            cursor = conn.cursor()

            cursor.execute("DELETE FROM sale WHERE account_id = %s RETURNING *", (account_id,))
            conn.commit()

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Ошибка при удалении аккаунта из sale: {e}")

    def remove_account_from_accounts_db(self, account_id):
        try:
            conn = psycopg2.connect(
                host="localhost",
                port="5433",
                database="DB_proekt",
                user="postgres",
                password="2005"
            )
            cursor = conn.cursor()

            cursor.execute("DELETE FROM accounts WHERE account_id = %s RETURNING *", (account_id,))
            conn.commit()

            cursor.close()
            conn.close()

            self.load_data("accounts")

        except Exception as e:
            print(f"Ошибка при удалении аккаунта из accounts: {e}")

    def show_main_menu(self):
        self.main_window.show()
        self.close()

    def save_changes(self):
        try:
            conn = psycopg2.connect(
                host="localhost",
                port="5433",
                database="DB_proekt",
                user="postgres",
                password="2005"
            )
            cursor = conn.cursor()

            for row in range(self.table.rowCount()):
                account_id = self.table.item(row, 0).text()
                link = self.table.item(row, 1).text()
                steam_level = self.table.item(row, 2).text()
                games = self.table.item(row, 3).text()
                price = self.table.item(row, 4).text()
                login = self.table.item(row, 5).text()
                password = self.table.item(row, 6).text()

                cursor.execute(
                    "UPDATE accounts SET account_link = %s, steam_level = %s, games = %s, price = %s, "
                    "login = %s, password = %s WHERE account_id = %s RETURNING *",
                    (link, steam_level, games, price, login, password, account_id)
                )
                conn.commit()

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка при сохранении изменений: {e}")

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Главное окно")
        self.resize(950, 1000)

        self.button_in_processing = QtWidgets.QPushButton("В обработке")
        self.button_for_sale = QtWidgets.QPushButton("В продаже")
        self.exit_button = QtWidgets.QPushButton("Выход")

        self.button_in_processing.clicked.connect(self.show_in_processing_table)
        self.button_for_sale.clicked.connect(self.show_for_sale_table)
        self.exit_button.clicked.connect(self.close_application)

        button_style = "background-color: #4CAF50; color: white; font-size: 36px; border-radius: 15px;"
        self.button_in_processing.setStyleSheet(button_style)
        self.button_for_sale.setStyleSheet(button_style)
        self.exit_button.setStyleSheet(button_style)

        self.button_in_processing.setFixedSize(700, 80)
        self.button_for_sale.setFixedSize(700, 80)
        self.exit_button.setFixedSize(700, 80)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.button_in_processing, alignment=QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.button_for_sale, alignment=QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.exit_button, alignment=QtCore.Qt.AlignCenter)
        self.setLayout(main_layout)

        self._table_window = None

    def show_in_processing_table(self):
        self.hide()
        self._table_window = TableViewWindow("accounts", self)
        self._table_window.show()

    def show_for_sale_table(self):
        self.hide()
        self._table_window = TableViewWindow("sale", self)
        self._table_window.show()

    def close_application(self):
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow(main_window=MainWindow())
    login_window.show()
    sys.exit(app.exec_())
