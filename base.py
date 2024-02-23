import sqlite3
import datetime

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# Создание таблиц
cursor.execute('CREATE TABLE IF NOT EXISTS users(user_id TEXT,username TEXT,subscribe TEXT,region TEXT,check_sub '
               'TEXT,truck TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS posts(username TEXT,region TEXT,post_text TEXT,post_photo TEXT,post_video '
               'TEXT, '
               'time_1 TEXT,time_2 TEXT,time_3 TEXT,moderate TEXT,active TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS free(user_id TEXT,username TEXT,channel TEXT,end_date TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS groups(name TEXT,link TEXT,region TEXT,chat_id TEXT)')


async def check_post(user):
    try:
        sql = """SELECT * FROM posts WHERE username = ?"""
        cursor.execute(sql, (user,))
        if cursor.fetchone():
            return True
        else:
            return False
    except:
        return False


async def check_truck(user):
    sql = """SELECT truck FROM users WHERE username = ?"""
    cursor.execute(sql, (user,))
    return cursor.fetchone()[0]


async def get_subs(date):
    try:
        sql = """SELECT username FROM users WHERE check_sub = ?"""
        cursor.execute(sql, (date,))
    except:
        return False
    else:
        return cursor.fetchall()


async def get_all_id():
    list = []
    sql = """SELECT user_id FROM users"""
    cursor.execute(sql)
    for row in cursor.fetchall():
        list.append(row[0])
    else:
        return list


async def get_region(user_id):
    sql = """SELECT region FROM users WHERE user_id = ?"""
    try:
        cursor.execute(sql, (user_id,))
        return cursor.fetchone()[0]
    except:
        return False


async def add_user(data):
    sql = """SELECT user_id FROM users"""
    cursor.execute(sql)
    record = cursor.fetchall()
    for row in record:
        if (str(data[0]),) == row:
            break
    else:
        sql = """INSERT INTO users (user_id,username,subscribe,region,check_sub,truck) VALUES (?,?,?,?,?,?)"""
        cursor.execute(sql, data)
        conn.commit()


async def get_chat(link):
    sql = """SELECT chat_id FROM groups WHERE link = ?"""
    cursor.execute(sql, (link,))
    return cursor.fetchone()[0]


async def get_chats(region):
    sql = """SELECT chat_id FROM groups WHERE region = ?"""
    cursor.execute(sql, (region,))
    return cursor.fetchall()


async def get_link(name):
    sql = """SELECT link FROM groups WHERE name = ?"""
    cursor.execute(sql, (name,))
    return cursor.fetchone()[0]


async def get_groups(region):
    regs = []
    sql = """SELECT name FROM groups WHERE region = ?"""
    cursor.execute(sql, (region,))
    for reg in cursor.fetchall():
        regs.append(reg[0])
    else:
        return regs


async def edit_media_post(data):
    sql = """UPDATE posts SET post_photo = ?,post_video=? WHERE username = ? AND post_text = ?"""
    cursor.execute(sql, data)
    conn.commit()


async def edit_text_post(data):
    sql = """UPDATE posts SET post_text = ? WHERE username = ? AND post_text = ?"""
    cursor.execute(sql, data)
    conn.commit()


async def get_post_info(data):
    sql = """SELECT * FROM posts WHERE username = ? AND region = ?"""
    cursor.execute(sql, (data[0], data[1]))
    for row in cursor.fetchall():
        post = {'text': row[2],
                'photo': row[3],
                'video': row[4]}
        return post


async def get_post(username):
    post = {}
    try:
        sql = """SELECT * FROM posts WHERE username = ?"""
        cursor.execute(sql, (username,))
        result = cursor.fetchall()
    except:
        return False
    else:
        for row in result:
            post = {'text': row[2],
                    'photo': row[3],
                    'video': row[4]}
        else:
            return post


async def check_and_publicate(time, region):
    from handlers import publ_pay
    try:
        sql = """SELECT * FROM posts WHERE region = ?"""
        cursor.execute(sql, (region,))
        records = cursor.fetchall()
    except:
        pass
    else:
        for row in records:
            if await check_sub(row[0]):
                if row[5] == time or row[6] == time or row[7] == time:
                    publ = {'username': row[0], 'region': row[1], 'text': row[2], 'photo': row[3], 'video': row[4]}
                    await publ_pay(publ)
            else:
                sql = 'UPDATE posts SET active = "-" WHERE username = ?'
                cursor.execute(sql, (row[0],))
                conn.commit()


async def add_subscribe(data):
    now = datetime.datetime.now()
    period = datetime.timedelta(days=30)
    date = now + period
    date = date.strftime('%d.%m.%y')
    try:
        sql = """SELECT username FROM users WHERE username = ?"""
        cursor.execute(sql, (data[1],))
    except:
        sql = """INSERT INTO users (user_id,username,subscribe,check_sub,truck) VALUES (?,?,?,?,?)"""
        data.insert(2, 'yes')
        data.insert(3, date)
        data.insert(4, data[2])
        cursor.execute(sql, data)
        conn.commit()
    else:
        sql = """UPDATE users SET subscribe = ?, check_sub = ?,truck=? WHERE username = ?"""
        data.insert(2, 'yes')
        data.insert(3, date)
        data.insert(4, data[2])
        cursor.execute(sql, ('yes', date, data[2], data[1]))
        conn.commit()


async def del_subscribe(name):
    sql = """UPDATE users SET subscribe = ?, check_sub = ?,truck = ? WHERE username = ?"""
    cursor.execute(sql, ('-', '-', '-', name))
    conn.commit()


async def check_sub(user):
    try:
        sql = """SELECT subscribe FROM users WHERE username = ?"""
        cursor.execute(sql, (user,))
        if cursor.fetchone()[0] == 'yes':
            return True
        else:
            return False
    except:
        return False


async def add_free_post(data):
    now = datetime.datetime.now()
    future = now + datetime.timedelta(hours=24)
    end_date = future.strftime('%d/%m/%y %H:%M')
    data.insert(3, end_date)
    sql = """INSERT INTO free(user_id,username,channel,end_date) VALUES (?,?,?,?)"""
    cursor.execute(sql, data)
    conn.commit()


async def add_post(data):
    try:
        sql = """SELECT * FROM posts WHERE username = ?"""
        cursor.execute(sql, (data[0],))
    except:
        pass
    else:
        sql = """DELETE FROM posts WHERE username = ?"""
        cursor.execute(sql, (data[0],))
        conn.commit()
    finally:
        sql = """SELECT time_1,time_2,time_3 FROM posts WHERE region = ?"""
        cursor.execute(sql, (data[1],))
        result = cursor.fetchall()
        if not result:
            data.insert(5, '09:00')
            data.insert(6, '14:00')
            data.insert(7, '19:00')
        else:
            for row in result:
                time_1 = datetime.datetime.strptime(row[0], '%H:%M')
                time_2 = datetime.datetime.strptime(row[1], '%H:%M')
                time_3 = datetime.datetime.strptime(row[2], '%H:%M')
                time_1 = time_1 + datetime.timedelta(minutes=5)
                time_2 = time_2 + datetime.timedelta(minutes=5)
                time_3 = time_3 + datetime.timedelta(minutes=5)
                time_1 = time_1.strftime('%H:%M')
                time_2 = time_2.strftime('%H:%M')
                time_3 = time_3.strftime('%H:%M')
                if (time_1, time_2, time_3) not in result:
                    data.insert(5, time_1)
                    data.insert(6, time_2)
                    data.insert(7, time_3)
                    break

        file = open('filter.txt', 'r', encoding='utf-8')
        strokes = file.readlines()
        list = []
        file.close()
        for item in strokes:
            list.append(item.replace('\n', ''))
        else:
            for elem in list:
                if elem in data[2]:
                    break
            else:
                data.insert(8, '+')
                data.insert(9, '+')
                sql = """INSERT INTO posts (username,region,post_text,post_photo,post_video,time_1,time_2,time_3,
                moderate,active) VALUES (?,?, ?,?,?,?,?,?,?,?) """
                cursor.execute(sql, data)
                conn.commit()
                return True


async def check_free(data):
    sql = """SELECT end_date FROM free WHERE user_id = ?"""
    cursor.execute(sql, data)
    try:
        result = cursor.fetchall()[0]
        if result is not None:
            end = str(result).replace('(', '').replace(')', '').replace(',', '').replace("'", "")
            now = datetime.datetime.now()
            date = str(end).split(' ')[0]
            time = str(end).split(' ')[1]
            future = datetime.datetime(day=int(date.split('/')[0]), month=int(date.split('/')[1]),
                                       year=2000 + int(date.split('/')[2]), hour=int(time.split(':')[0]),
                                       minute=int(time.split(':')[1]))
            period = future - now
            period = f'{str(period).split(":")[0]}ч.{str(period).split(":")[1]}мин.'
            return period
    except ValueError:
        return False
    except IndexError:
        return False


async def check_and_delete_free(date):
    try:
        sql = """DELETE FROM free WHERE end_date = ?"""
        cursor.execute(sql, (date,))
        conn.commit()
    except:
        pass
