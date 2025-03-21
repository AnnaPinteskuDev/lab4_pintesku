import sqlite3
import datetime


def insert_test_data():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Заполнение таблицы Client
    clients = [
        ("Иванов Иван Иванович", "ivan@example.com", "+79123456789", "1234 567890", "password123"),
        ("Петрова Анна Сергеевна", "anna@mail.ru", "+79234567890", "2345 678901", "111"),
        ("Сидоров Петр Алексеевич", "petr@example.com", "+79345678901", "3456 789012", "testpass"),
    ]
    cursor.executemany("INSERT INTO Client (FIO, Email, Phone, Passport, Password) VALUES (?, ?, ?, ?, ?)", clients)

    # Заполнение таблицы Administrator
    administrators = [
        ("Смирнова Елена Владимировна", "+79456789012", "admin", "admin"),
        ("Козлов Дмитрий Игоревич", "+79567890123", "dmitry@example.com", "admin123"),
    ]
    cursor.executemany("INSERT INTO Administrator (FIO, Phone, Email, Password) VALUES (?, ?, ?, ?)", administrators)

    # Заполнение таблицы System_administrator
    sysadmins = [
        ("Админов Алексей Иванович", "+79678901234", "sys", "sys"),
    ]
    cursor.executemany("INSERT INTO System_administrator (FIO, Phone, Email, Password) VALUES (?, ?, ?, ?)", sysadmins)

    # Заполнение таблицы Room
    rooms = [
        ("Стандарт", "2", "Свободен", "3000", "Номер с двумя кроватями"),
        ("Люкс", "2", "Свободен", "5000", "Номер с двуспальной кроватью и видом на море"),
        ("Семейный", "4", "Занят", "6000", "Номер с двумя комнатами"),
        ("Эконом", "1", "Свободен", "2000", "Небольшой номер с одной кроватью"),
    ]
    cursor.executemany("INSERT INTO Room (Room_type, Capacity, Status, Price_per_night, Description) VALUES (?, ?, ?, ?, ?)", rooms)

    # Заполнение таблицы Booking
    bookings = [
        (1, 1, 1, datetime.date(2024, 1, 15), datetime.date(2024, 1, 20), "15000", "Подтверждено"),
        (2, 2, 2, datetime.date(2024, 2, 1), datetime.date(2024, 2, 5), "20000", "Подтверждено"),
        (3, 3, 1, datetime.date(2024, 2, 10), datetime.date(2024, 2, 12), "6000", "Отменено"),
        (1, 4, 2, datetime.date(2024, 2, 15), datetime.date(2024, 2, 18), "9000", "Подтверждено"),
    ]
    cursor.executemany("INSERT INTO Booking (Id_client, Id_room, Id_administrator, Arrival_date, Departure_date, Total_price, Booking_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       bookings)

    # Заполнение таблицы Report
    reports = [
        (1, 1),
        (2, 1),
    ]
    cursor.executemany("INSERT INTO Report (Id_booking, Id_sysadmin) VALUES (?, ?)", reports)

    conn.commit()
    conn.close()

insert_test_data()
print("База данных и тестовые данные успешно созданы.")