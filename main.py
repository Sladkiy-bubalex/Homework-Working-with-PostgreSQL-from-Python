import psycopg2


def create_table(cursor):
    """
    Создание таблиц в БД.

    Таблица Client
    -----------
    Параметры
    -----------
    id: int\n
        Id клиента по первичному ключу (SERIAL)\n
    name: VARCHAR(30) NOT NULL\n
        Имя клиента\n
    surname: VARCHAR(30) NOT NULL\n
        Фамилия клиента\n
    name_email: VARCHAR(60) NOT NULL\n
        Email клиента\n

    Таблица Phone
    -----------
    Параметры
    -----------
    id: int\n
        Id номера телефона по первичному ключу (SERIAL)\n
    client_id: int NOT NULL REFERENCES Client(id)\n
        Id клиента по внешнему ключу\n
    number_phone: VARCHAR(100)\n
        Номер телефона клиента\n
    """

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Client(
        id SERIAL PRIMARY KEY,
        name VARCHAR(30) NOT NULL,
        surname VARCHAR(30) NOT NULL,
        name_email VARCHAR(60) NOT NULL);
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Phone(
        id SERIAL PRIMARY KEY,
        client_id INTEGER NOT NULL REFERENCES Client(id),
        number_phone VARCHAR(100));
    """)
    conn.commit()
    pass

def add_client(cursor, name: str, surname: str, name_email: str, number_phone=None) -> str:
    """
    Добавление клиента в базу данных.

    Параметры
    -----------
    cursor\n
        Курсор подключения\n
    name: str\n
        Имя клиента\n
    surname: str\n
        Фамилия клиента\n
    name_email: str\n
        Email клиента\n
    number_phone: None\n
        Номер клиента (по умолчанию None)\n

    Возвращает
    -----------
    Строку о успешном добавлении клиента в БД с номером по первичному ключу(id).
    """

    cursor.execute("""
    INSERT INTO Client(name, surname, name_email)
         VALUES (%s, %s, %s) RETURNING id;""", (name, surname, name_email))
    id_client = cursor.fetchone()[0]
    if number_phone is not None:
        cursor.execute("""
        INSERT INTO Phone(client_id, number_phone)
            VALUES (%s, %s);""", (id_client, number_phone))
    conn.commit()

    print(f'Клиент {name} {surname} был добавлен в БД под номером {id_client}')

def add_number_phone_for_client(cursor, number: str, id: int) -> str:
    """
    Добавление номера телефона к существующему клиенту по его id.

    Параметры
    -----------
    cursor\n
        Курсор подключения\n
    number: str\n
        Номер телефона для добавления\n
    id: int\n
        Id клиента к которому необходимо добавить номер\n

    Возвращает
    -----------
    Строку с номером телефона и номер клиента (id) при успешном добавлении\n
    Или сторку о том, что клиент по id в БД не найден.
    """

    cursor.execute("""
    SELECT * FROM Client
     WHERE id=%s""", (id,))
    check_id = cursor.fetchone()
    if check_id is not None:
        cursor.execute("""
        INSERT INTO Phone (client_id, number_phone)
             VALUES (%s, %s);""", (id, number))
        print(f'Телефон {number} был успешно добавлен клиенту под номером {id}')
    else:
        print(f'Клиент под номером {id} в БД не найден')

def change_client(
    cursor,
    id,
    name=None,
    surname=None,
    name_email=None,
    number_phone=None
    ):
    """
    Изменение данных о клиенте по id клиента.

    Параметры
    -----------
    cursor\n
        Курсор подключения\n
    id: int\n
        Номер клиента в БД\n
    name: None\n
        Имя на которое необходимо изменить (по умолчанию None)\n
    surname: None\n
        Фамилия на которую необходимо изменить (по умолчанию None)\n
    name_email: None\n
        Email на который необходимо изменить (по умолчанию None)\n
    number_phone: None\n
        Номер телефона на который необходимо изменить (по умолчанию None)\n

    Возвращает
    -----------
    При удачном изменении ничего не возвращает\n
    Или сторку о том, что клиент по id в БД не найден.
    """

    cursor.execute("""SELECT * FROM Client WHERE id=%s""", (id,))
    check_client = cursor.fetchone()
    if check_client is None:
        print('Данный клиент в БД не найдет')
        return
    if name is not None:
        cursor.execute("""UPDATE Client SET name=%s WHERE id=%s;""", (name, id))
    if surname is not None:
        cursor.execute("""UPDATE Client SET surname=%s WHERE id=%s;""", (surname, id))
    if name_email is not None:
        cursor.execute("""UPDATE Client SET name_email=%s WHERE id=%s;""", (name_email, id))
    if number_phone is not None:
        cursor.execute("""
            UPDATE Phone SET number_phone=%s
             WHERE client_id=%s;""", (number_phone, id))

def delete_phone_client(cursor, id: int, number: str) -> str:
    """
    Удаление телефона по id клиента.

    Параметры
    -----------
    cursor\n
        Курсор подключения\n
    id: int\n
        Id номер клиента из БД\n
    number: str\n
        Номер телефона, который небходимо удалить

    Возвращает
    -----------
    Строку об успешном удалении телефона по id клиента\n
    Либо информацию об отсутствии телефона у данного клиента\n
    Либо информацию об отсутсвии клиента в БД.
    """

    cursor.execute("""
    SELECT * FROM Client
     WHERE id=%s;""", (id,))
    check_client = cursor.fetchone()
    if check_client is not None:
        cursor.execute("""
        SELECT * FROM Phone
        WHERE client_id=%s;""", (id,))
        check_phone = cursor.fetchone()
        if check_phone is not None:
            cursor.execute("""
            DELETE FROM Phone WHERE client_id=%s AND number_phone=%s;""", (id, number))
            conn.commit()
            print(f'Номер телефона {number} был удален у клиента {id}')
        else:
            print('Телефон у данного клиента не найден')
    else:
        print('Данный клиент в БД не найден')

def delete_client(cursor, id):
    """
    Удаление клиента по его id.

    Параметры
    -----------
    cursor\n
        Курсор подключения\n
    id: int\n
        Id клиента из БД\n

    Возвращает
    -----------
    Строку об успешном удалении клиента\n
    Или информацию о отсутствии клиента по данному id.
    """

    cursor.execute("""
    SELECT * FROM Client
     WHERE id=%s;""", (id,))
    client = cursor.fetchone()
    if client is not None:
        cursor.execute("""
        DELETE FROM Client
         WHERE id=%s;""", (id,))
        conn.commit()
        print(f'Клиент под номером {id} успешно удален')
    else:
        print(f'Клиент под номером {id} не найден')

def find_client(cursor, name=None, surname=None, email=None, number_phone=None) -> tuple:
    """
    Поиск клиента по его данным (Имя, Фамилия, email, номер телефона).

    Параметры
    -----------
    cursor\n
        Курсор подключения\n
    name: None\n
        Имя по которому необходимо найти (по умолчанию None)\n
    surname: None\n
        Фамилия по которой необходимо найти (по умолчанию None)\n
    name_email: None\n
        Email по которому необходимо найти (по умолчанию None)\n
    number_phone: None\n
        Номер телефона по которому необходимо найти (по умолчанию None)\n
    
    Возвращает
    -----------
    Кортеж(и) с данными о клиенте(ах) подходящих под параметры.
    """

    data = {
        'name': name,
        'surname': surname,
        'name_email': email
    }
    query = 'SELECT * FROM Client WHERE '
    operation_data = []
    values = []
    for key, value in data.items():
        if value is not None:
            operation_data.append(key)
            values.append(value)
    if len(operation_data) == 1:
        query += operation_data[0] + '=%s'
        cursor.execute(query, values)
        for client in cursor.fetchall():
            cursor.execute("""
            SELECT number_phone FROM Phone
             WHERE client_id=%s;""", (client[0],))
            client_number = [x[0] for x in cursor.fetchall()]
            if client_number == []:
                print(f'Данные клиента {client} Номеров телефонов нет')
            else:
                print(f'Данные клиента {client} Номера телефонов {', '.join(client_number)}')

    elif len(operation_data) > 1:
        query += '=%s AND '.join(operation_data) + '=%s'
        cursor.execute(query, values)
        for client in cursor.fetchall():
            cursor.execute("""
            SELECT number_phone FROM Phone
             WHERE client_id=%s;""", (client[0],))
            client_number = [x[0] for x in cursor.fetchall()]
            if client_number == []:
                print(f'Данные клиента {client} Номеров телефонов нет')
            else:
                print(f'Данные клиента {client} Номера телефонов {', '.join(client_number)}')


if __name__ == "__main__":
    with psycopg2.connect(
        database='homework_postgres',
        user='postgres',
        password='maxim53306') as conn:
        with conn.cursor() as cur:
            create_table(cur)
            add_client(cur, 'Maxim', 'Rochev', 'ololo@mail.ru', '88005555535')
            add_client(cur, 'Polina', 'Skiba', 'polasha@mail.ru')
            add_client(cur, 'Dmitriy', 'Semenov', 'chilliburher@mail.ru', '89113524000')
            add_client(cur, 'Dmitriy', 'Demetyev', 'balda@yandex.ru', '89123531254')

            cur.execute("""SELECT * FROM Client;""")
            for client in cur.fetchall():
                print(client)

            add_number_phone_for_client(cur, '8991676553242', 2)
            cur.execute("""SELECT number_phone FROM Phone
                            WHERE client_id=2;""")
            print(cur.fetchall())

            change_client(cur, 4, 'Dimka', 'Dimontiev')
            cur.execute("""SELECT * FROM Client WHERE id=%s;""", (4,))
            print(cur.fetchone())

            delete_phone_client(cur, 1, '88005555535')
            cur.execute("""SELECT * FROM Phone;""")
            print(cur.fetchall())

            delete_client(cur, 3)
            cur.execute("""SELECT * FROM Client WHERE id=%s;""", (3,))
            print(cur.fetchone())

            find_client(cur, name='Dmitriy')
    conn.close()