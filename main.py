import psycopg2


def create_table(cursor):
    """
    Создание таблицы в БД.
    """

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Client(
        id SERIAL PRIMARY KEY,
        name VARCHAR(30) NOT NULL,
        surname VARCHAR(30) NOT NULL,
        name_email VARCHAR(60) NOT NULL,
        number_phone VARCHAR(60));
    """)
    conn.commit()
    pass

def add_client(cursor, name: str, surname: str, name_email: str, number_phone=None) -> str:
    """
    Добавление клиента в базу данных.

    Параметры
    -----------
    cursor
        Курсор подключения
    name: str
        Имя клиента
    surname: str
        Фамилия клиента
    name_email: str
        Email клиента
    number_phone: None
        Номер клиента (по умолчанию None)

    Возваращает
    -----------
    Строку о успешном добавлении клиента в БД с номером по первичному ключу(id).
    """

    cursor.execute("""
    INSERT INTO Client(name, surname, name_email, number_phone)
         VALUES (%s, %s, %s, %s) RETURNING id;""", (name, surname, name_email, number_phone))
    print(f'Клиент {name} {surname} был добавлен в БД под номером {cursor.fetchone()[0]}')

def add_number_phone_for_client(cursor, number: str, id: int) -> str:
    """
    Добавление номера телефона к существующему клиенту по его id.

    Параметры
    -----------
    cursor
        Курсор подключения
    number: str
        Номер телефона для добавления
    id: int
        Id клиента к которому необходимо добавить номер

    Возвращает
    -----------
    Строку с номером телефона и номер клиента (id) при успешном добавлении
    Или сторку о том, что клиент по id в БД не найден.
    """

    cursor.execute("""
    SELECT * FROM Client
     WHERE id=%s""", (id,))
    check_id = cursor.fetchone()
    if check_id is not None:
        cursor.execute("""
        UPDATE Client SET number_phone=%s
         WHERE id=%s;""", (number, id))
        conn.commit()
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
    cursor
        Курсор подключения
    id: int
        Номер клиента в БД
    name: None
        Имя на которое необходимо изменить (по умолчанию None)
    surname: None
        Фамилия на которую необходимо изменить (по умолчанию None)
    name_email: None
        Email на который необходимо изменить (по умолчанию None)
    number_phone: None
        Номер телефона на который необходимо изменить (по умолчанию None)

    Возвращает
    -----------
    Ничего не возвращает.
    """

    check_data = {
        'name': name,
        'surname': surname,
        'name_email': name_email,
        'number_phone': number_phone
    }
    operation_data = []
    values = []
    for key, value in check_data.items():
        if value is not None:
            operation_data.append(f'{key}=%s')
            values.append(value)
    if not operation_data:
        print('Данных для обновления нет')
        return
    operation_query = f"""
        UPDATE Client SET {', '.join(operation_data)} WHERE id=%s;
    """
    values.append(id)
    cursor.execute(operation_query, values)
    conn.commit()

def delete_phone_client(cursor, id) -> str:
    """
    Удалените телефона по id клиента.

    Параметры
    -----------
    cursor
        Курсор подключения
    id: int
        Id номер клиента из БД

    Возвращает
    -----------
    Строку об успешном удалении телефона по id клиента
    Или информацию об отсутствии телефона у данного клиента.
    """

    cursor.execute("""
    SELECT number_phone FROM Client
     WHERE id=%s;""", (id,))
    phone_client = cursor.fetchone()
    if phone_client is not None:
        cursor.execute("""
        UPDATE Client SET number_phone=%s
         WHERE id=%s;""", (None, id))
        conn.commit()
        print(f'Телефон клиента под номером {id} был удален')
    else:
        print('Телефон у данного клиента не найден')

def delete_client(cursor, id):
    """
    Удаление клиента по его id.

    Параметры
    -----------
    cursor
        Курсор подключения
    id: int
        Id клиента из БД

    Возвращает
    -----------
    Строку об успешном удалении клиента 
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
    cursor
        Курсор подключения
    name: None
        Имя по которому необходимо найти (по умолчанию None)
    surname: None
        Фамилия по которой необходимо найти (по умолчанию None)
    name_email: None
        Email по которому необходимо найти (по умолчанию None)
    number_phone: None
        Номер телефона по которому необходимо найти (по умолчанию None)
    
    Возвращает
    -----------
    Кортеж(и) с данными о клиенте(ах) подходящих под параметры.
    """

    data = {
        'name': name,
        'surname': surname,
        'name_email': email,
        'number_phone': number_phone
    }
    query = 'SELECT * FROM Client WHERE '
    operation_data = []
    values = []
    for key, value in data.items():
        if value is not None:
            operation_data.append(f'{key}=%s')
            values.append(value)
    if len(operation_data) == 1:
        query += ''.join(operation_data)
        cursor.execute(query, values)
        for client in cursor.fetchall():
            print(client)
    elif len(operation_data) > 1:
        query += ' AND '.join(operation_data)
        cursor.execute(query, values)
        for client in cursor.fetchall():
            print(client)


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

        add_number_phone_for_client(cur, '89916765523', 2)
        cur.execute("""SELECT * FROM Client WHERE id=%s;""", (2,))
        print(cur.fetchone())

        change_client(cur, 4, 'Dimka', 'Dimontiev')
        cur.execute("""SELECT name, surname FROM Client WHERE id=%s;""", (4,))
        print(cur.fetchone())

        delete_phone_client(cur, 1)
        cur.execute("""SELECT number_phone FROM Client WHERE id=%s;""", (1,))
        print(cur.fetchone())

        delete_client(cur, 3)
        cur.execute("""SELECT * FROM Client WHERE id=%s;""", (3,))
        print(cur.fetchone())

        find_client(cur, name='Maxim')

