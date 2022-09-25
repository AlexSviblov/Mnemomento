import sqlite3

conn = sqlite3.connect(r'C:\Users\Public\AppData\TestForPhotoPr\PhotoDB.db')   # соединение с БД
cur = conn.cursor()

sql_str1 = 'CREATE TABLE photos (filename TEXT, catalog TEXT, camera TEXT, lens TEXT, shootingdate TEXT, shootingdatetime TEXT, additiondate TEXT, GPSdata TEXT)'

sql_str2 = 'CREATE TABLE socialnetworks (filename TEXT, catalog TEXT, shootingdate TEXT)'

cur.execute(sql_str1)
cur.execute(sql_str2)

conn.commit()


# conn = sqlite3.connect('C:/Users/user/PycharmProjects/PhotoExeNotTouched/ErrorNames.db')   # соединение с БД
# cur = conn.cursor()
#
# sql_str3 = 'CREATE TABLE ernames (type TEXT, exifname TEXT, normname TEXT)'
#
# cur.execute(sql_str3)
#
# conn.commit()

