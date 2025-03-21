import sys
import os
import sqlite3
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox, QInputDialog
from PyQt6.QtCore import QDate


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def create_database():
    db_path = resource_path('database.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Client (
                        Id_client INTEGER PRIMARY KEY AUTOINCREMENT,
                        FIO VARCHAR(100) NOT NULL,
                        Email VARCHAR(100) NOT NULL,
                        Phone VARCHAR(50),
                        Passport VARCHAR(100) NOT NULL,
                        Password VARCHAR(20) NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Administrator (
                        Id_administrator INTEGER PRIMARY KEY AUTOINCREMENT,
                        FIO VARCHAR(100) NOT NULL,
                        Phone VARCHAR(50),
                        Email VARCHAR(100) NOT NULL,
                        Password VARCHAR(20) NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS System_administrator (
                        Id_sysadmin INTEGER PRIMARY KEY AUTOINCREMENT,
                        FIO VARCHAR(100) NOT NULL,
                        Phone VARCHAR(50),
                        Email VARCHAR(100) NOT NULL,
                        Password VARCHAR(20) NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Room (
                        Id_room INTEGER PRIMARY KEY AUTOINCREMENT,
                        Room_type VARCHAR(50),
                        Capacity VARCHAR(50) NOT NULL,
                        Status VARCHAR(50) NOT NULL,
                        Price_per_night VARCHAR(50) NOT NULL,
                        Description VARCHAR(250))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Booking (
                        Id_booking INTEGER PRIMARY KEY AUTOINCREMENT,
                        Id_client INTEGER,
                        Id_room INTEGER,
                        Id_administrator INTEGER,
                        Arrival_date DATE NOT NULL,
                        Departure_date DATE NOT NULL,
                        Total_price VARCHAR(100) NOT NULL,
                        Booking_status VARCHAR(30),
                        FOREIGN KEY (Id_client) REFERENCES Client (Id_client),
                        FOREIGN KEY (Id_room) REFERENCES Room (Id_room),
                        FOREIGN KEY (Id_administrator) REFERENCES Administrator (Id_administrator))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Report (
                        Id_report INTEGER PRIMARY KEY AUTOINCREMENT,
                        Id_booking INTEGER,
                        Id_sysadmin INTEGER,
                        FOREIGN KEY (Id_booking) REFERENCES Booking (Id_booking),
                        FOREIGN KEY (Id_sysadmin) REFERENCES System_administrator (Id_sysadmin))''')

    conn.commit()
    conn.close()

class HotelApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Система бронирования номеров')
        self.setGeometry(100, 100, 400, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.login_ui()

    def login_ui(self):
        self.clear_layout()

        self.layout.addWidget(QLabel('Авторизация'))

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText('Почта')
        self.layout.addWidget(self.email_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Пароль')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input)

        self.role_combobox = QComboBox(self)
        self.role_combobox.addItems(["Клиент", "Администратор", "Системный администратор"])
        self.layout.addWidget(self.role_combobox)

        self.login_button = QPushButton('Войти', self)
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        self.register_button = QPushButton('Зарегистрироваться', self)
        self.register_button.clicked.connect(self.register_ui)
        self.layout.addWidget(self.register_button)

    def clear_layout(self):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        role = self.role_combobox.currentText()

        db_path = resource_path('database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if role == "Клиент":
            cursor.execute("SELECT * FROM Client WHERE Email = ? AND Password = ?", (email, password))
        elif role == "Администратор":
            cursor.execute("SELECT * FROM Administrator WHERE Email = ? AND Password = ?", (email, password))
        elif role == "Системный администратор":
            cursor.execute("SELECT * FROM System_administrator WHERE Email = ? AND Password = ?", (email, password))

        user = cursor.fetchone()
        conn.close()

        if user:
            self.show_user_dashboard(role, user)
        else:
            self.show_error_message("Неверные данные!")

    def show_user_dashboard(self, role, user=None):
        self.clear_layout()

        if role == "Клиент":
            self.layout.addWidget(QLabel('Панель управления клиента'))
            self.show_room_booking_ui(user)
        elif role == "Администратор":
            self.layout.addWidget(QLabel('Панель управления администратора'))
            self.show_admin_dashboard(user)
        elif role == "Системный администратор":
            self.layout.addWidget(QLabel('Панель управления системного администратора'))
            self.show_sysadmin_dashboard(user)

    def show_sysadmin_dashboard(self, user):
        """Способ отображения панели мониторинга системного администратора."""
        self.layout.addWidget(QLabel(''))

        # Button to create a report
        self.create_report_button = QPushButton('Создать отчёт', self)
        self.create_report_button.clicked.connect(self.create_report)
        self.layout.addWidget(self.create_report_button)

        self.view_reports_button = QPushButton('Просмотр отчетов', self)
        self.view_reports_button.clicked.connect(self.view_reports)
        self.layout.addWidget(self.view_reports_button)

    def create_report(self):
        """Способ создания отчета по бронированию."""
        booking_id, ok = QInputDialog.getInt(self, 'Создать отчёт', 'Введите ID бронирования:')
        if ok and booking_id:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM Booking WHERE Id_booking = ?", (booking_id,))
            booking = cursor.fetchone()

            if booking:
                cursor.execute("INSERT INTO Report (Id_booking, Id_sysadmin) VALUES (?, ?)",
                               (booking_id, booking[3]))
                conn.commit()
                conn.close()
                self.show_error_message("Отчёт успешно создан.")
            else:
                self.show_error_message("ID  бронирования не найдено.")

    def view_reports(self):
        """Способ просмотра всех отчётов, сгенерированных системным администратором."""
        self.clear_layout()

        db_path = resource_path('database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT Report.Id_report, Booking.Id_booking, Client.FIO, Room.Room_type, Report.Id_sysadmin "
                       "FROM Report "
                       "JOIN Booking ON Report.Id_booking = Booking.Id_booking "
                       "JOIN Client ON Booking.Id_client = Client.Id_client "
                       "JOIN Room ON Booking.Id_room = Room.Id_room")
        reports = cursor.fetchall()

        self.layout.addWidget(QLabel('Отчёты:'))

        for report in reports:
            self.layout.addWidget(
                QLabel(f"ID отчёта: {report[0]} - ID бронирования: {report[1]} - Клиент: {report[2]} - Номер: {report[3]}"))

        self.back_button = QPushButton('Вернуться к панели управления', self)
        self.back_button.clicked.connect(lambda: self.show_user_dashboard("Системный администратор"))
        self.layout.addWidget(self.back_button)

    def show_error_message(self, message):
        self.clear_layout()
        self.layout.addWidget(QLabel(message))

    def show_room_booking_ui(self, user):
        self.layout.addWidget(QLabel('Свободные номера для бронирования:'))

        db_path = resource_path('database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Room WHERE Status = 'Свободен'")
        rooms = cursor.fetchall()

        self.room_combobox = QComboBox(self)
        self.room_combobox.addItem('Выберите номер')  # No data for this placeholder item
        for room in rooms:
            self.room_combobox.addItem(f"Номер {room[0]}: {room[1]} - {room[4]} за ночь", room[0])
        self.layout.addWidget(self.room_combobox)

        self.arrival_date_input = QLineEdit(self)
        self.arrival_date_input.setPlaceholderText('Дата заезда (ГГГГ-ММ-ДД)')
        self.layout.addWidget(self.arrival_date_input)

        self.departure_date_input = QLineEdit(self)
        self.departure_date_input.setPlaceholderText('Дата выезда (ГГГГ-ММ-ДД)')
        self.layout.addWidget(self.departure_date_input)

        self.book_button = QPushButton('Забронировать номер', self)
        self.book_button.clicked.connect(lambda: self.book_room(user))
        self.layout.addWidget(self.book_button)

    def book_room(self, user):
        room_id = self.room_combobox.currentData()
        if room_id is None:
            self.show_error_message("Пожалуйста, выберите номер.")
            return

        arrival_date = self.arrival_date_input.text()
        departure_date = self.departure_date_input.text()

        if not arrival_date or not departure_date:
            self.show_error_message("Укажите даты заезда и выезда.")
            return

        db_path = resource_path('database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Room WHERE Id_room = ?", (room_id,))
        room = cursor.fetchone()

        if room:
            price_per_night = float(room[4])
            print(arrival_date, departure_date)
            total_price = self.calculate_total_price(arrival_date, departure_date, price_per_night)

            cursor.execute(
                "INSERT INTO Booking (Id_client, Id_room, Arrival_date, Departure_date, Total_price, Booking_status) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (user[0], room_id, arrival_date, departure_date, total_price, "Подтверждено"))

            # Обновляем статус номера на "Занят"
            cursor.execute("UPDATE Room SET Status = 'Занят' WHERE Id_room = ?", (room_id,))

            conn.commit()
            conn.close()

            self.show_error_message("Бронирование прошло успешно!")
        else:
            self.show_error_message("Комната не найдена.")

    def calculate_total_price(self, arrival_date, departure_date, price_per_night):
        try:
            arrival = QDate.fromString(arrival_date, 'yyyy-MM-dd')
            departure = QDate.fromString(departure_date, 'yyyy-MM-dd')
            if not arrival.isValid() or not departure.isValid():
                print("Invalid date format.")
                return 0
            print(arrival, departure)
            days_diff = arrival.daysTo(departure)
            if days_diff < 1:
                return 0
            return days_diff * price_per_night
        except Exception as e:
            print(f"An error occurred: {e}")
            return 0

    def show_admin_dashboard(self, user):
        self.layout.addWidget(QLabel(''))

        self.view_booked_rooms_button = QPushButton('Просмотр забронированных номеров', self)
        self.view_booked_rooms_button.clicked.connect(self.view_booked_rooms)
        self.layout.addWidget(self.view_booked_rooms_button)

    def view_booked_rooms(self):
        self.clear_layout()

        db_path = resource_path('database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT Booking.Id_booking, Client.FIO, Room.Room_type, Booking.Arrival_date, Booking.Departure_date, Booking.Total_price "
                       "FROM Booking "
                       "JOIN Client ON Booking.Id_client = Client.Id_client "
                       "JOIN Room ON Booking.Id_room = Room.Id_room "
                       "WHERE Booking.Booking_status = 'Подтверждено'")

        booked_rooms = cursor.fetchall()

        self.layout.addWidget(QLabel('Забронированные номера:'))

        for booking in booked_rooms:
            self.layout.addWidget(QLabel(f"ID бронирования: {booking[0]} - {booking[1]} - {booking[2]} - с {booking[3]} до {booking[4]} - Цена: {booking[5]}"))

        self.back_button = QPushButton('Вернуться к панели управления', self)
        self.back_button.clicked.connect(lambda: self.show_user_dashboard("Администратор"))
        self.layout.addWidget(self.back_button)

    def register_ui(self):
        self.clear_layout()
        self.layout.addWidget(QLabel('Регистрация'))

        self.fio_input = QLineEdit(self)
        self.fio_input.setPlaceholderText('ФИО')
        self.layout.addWidget(self.fio_input)

        self.phone_input = QLineEdit(self)
        self.phone_input.setPlaceholderText('Номер телефона')
        self.layout.addWidget(self.phone_input)

        self.passport_input = QLineEdit(self)
        self.passport_input.setPlaceholderText('Паспорт')
        self.layout.addWidget(self.passport_input)

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText('Почта')
        self.layout.addWidget(self.email_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Пароль')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input)

        self.register_button = QPushButton('Зарегистрироваться', self)
        self.register_button.clicked.connect(self.register)
        self.layout.addWidget(self.register_button)

    def register(self):
        fio = self.fio_input.text()
        phone = self.phone_input.text()
        passport = self.passport_input.text()
        email = self.email_input.text()
        password = self.password_input.text()

        if not fio or not email or not password:
            self.show_error_message("Все поля должны быть заполнены.")
            return

        db_path = resource_path('database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO Client (FIO, Email, Phone, Passport, Password) VALUES (?, ?, ?, ?, ?)",(fio, email, phone, passport, password))
        conn.commit()
        conn.close()

        self.show_error_message('Регистрация прошла успешно! Войдите в систему.')


if __name__ == '__main__':
    create_database()
    app = QApplication(sys.argv)
    window = HotelApp()
    window.show()
    sys.exit(app.exec())
