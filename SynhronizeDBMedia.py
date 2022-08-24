import os
import shutil
import sqlite3
import datetime
import Metadata

import PhotoDataDB
import Settings

conn = sqlite3.connect('PhotoDB.db', check_same_thread=False)
cur = conn.cursor()


# TODO: Если файл есть, но он не в папке хранения медиа - уведомление, что его надо добавить вручную заново.
#  И дать пользователю выбор: стереть запись из БД, либо не стирать, а перенести, изменив в БД только каталог
#  (тогда перезапись сразу в двух таблицах).
#  При этом элемент из второго списка на exist получит False, отдаст команду стереть, но ничего не сотрётся,
#  ведь путь уже будет перезаписан (если файл переместили).
#  Т.е. 1) стёрка из БД и всё
#  2) перенос файла в директорию медиа, перезапись каталога в БД (оставляя остальные поля). Тогда для socnets
#  он будет уже не существовать, но ничего не удалится, т.к. catalog будет к тому времени сменён на новый




# получить все каталоги+файлы из ФотоДБ (таблицы фото и соцсети)
def get_all_db_ways() -> tuple[list[list[str, str], ...], list[list[str, str], ...]]:

    sql_str1 = "SELECT catalog, filename FROM photos"
    sql_str2 = "SELECT catalog, filename FROM socialnetworks"

    cur.execute(sql_str1)
    all_photos_db = cur.fetchall()

    cur.execute(sql_str2)
    all_socnets_db = cur.fetchall()

    return all_photos_db, all_socnets_db


# проверить существуют ли файлы из БД на диске
def check_exists_from_db(all_photos_db, all_socnets_db):
    for i in range(0, len(all_photos_db)):
        if os.path.exists(f"{all_photos_db[i][0]}/{all_photos_db[i][1]}"):
            print("exists")
            pass
        else:
            print('delete')
            sql_str = f"DELETE FROM photos WHERE catalog = \'{all_photos_db[i][0]}\' and filename = \'{all_photos_db[i][1]}\'"
            cur.execute(sql_str)

    for i in range(0, len(all_socnets_db)):
        if os.path.exists(f"{all_socnets_db[i][0]}/{all_socnets_db[i][1]}"):
            print("exists")
            pass
        else:
            print('delete')
            sql_str = f"DELETE FROM socialnetworks WHERE catalog = \'{all_socnets_db[i][0]}\' and filename = \'{all_socnets_db[i][1]}\'"
            cur.execute(sql_str)
    conn.commit()


# найти все фото в директории хранения медиа
def research_all_media_photos():
    filelist = []
    path = Settings.get_destination_media()
    for root, dirs, files in os.walk(path):
        for file in files:
            if (file.endswith(".jpg") or file.endswith(".JPG")) and 'thumbnail_' not in file:
                # append the file name to the list
                filelist.append([root.replace('\\', '/'), file])

    return filelist


# Если фото есть в директории хранения, но нет в БД - записать
def add_flaw_to_db(filelist):
    for combo in filelist:
        photoname = combo[0]
        photodirectory = combo[1]
        sql_str1 = f"SELECT * FROM photos WHERE catalog = \'{photoname}\' and \'{photodirectory}\'"
        sql_str2 = f"SELECT * FROM socialnetworks WHERE catalog = \'{photoname}\' and \'{photodirectory}\'"

        cur.execute(sql_str1)
        answer_photo = cur.fetchone()

        cur.execute(sql_str2)
        answer_socnets = cur.fetchone()

        if not answer_photo or not answer_socnets:
            additiontime = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
            # camera, lens, shootingdate, GPS = 'Canon EOS 200D', 'EF-S 10-18 mm', '2020.05.20 14:21:20', "No Data"
            camera, lens, shootingdatetime, GPS = Metadata.exif_for_db(photoname, photodirectory, os.getcwd())
            if shootingdatetime != "No data":
                shootingdate = shootingdatetime[:10]
            else:
                shootingdate = shootingdatetime

            if not answer_photo:
                sql_str1 = f'INSERT INTO photos VALUES (\'{photoname}\', \'{photodirectory}\', \'{camera}\', \'{lens}\',' \
                           f' \'{shootingdate}\', \'{shootingdatetime}\', \'{additiontime}\', \'{GPS}\')'

                cur.execute(sql_str1)

            if not answer_socnets:
                sql_str_get_nets = 'PRAGMA table_info(socialnetworks)'
                cur.execute(sql_str_get_nets)
                all_column_names = cur.fetchall()
                if len(all_column_names) == 3:
                    sql_str2 = f'INSERT INTO socialnetworks VALUES (\'{photoname}\',\'{photodirectory}\',\'{shootingdate}\')'
                else:
                    sn_str = r''
                    for i in range(len(all_column_names) - 3):
                        sn_str += ',\'No value\' '
                    sql_str2 = f'INSERT INTO socialnetworks VALUES (\'{photoname}\',\'{photodirectory}\',\'{shootingdate}\'{sn_str})'

                cur.execute(sql_str2)

    conn.commit()



