import os
import shutil
import sqlite3
import datetime

import FilesDirs
import Metadata

import PhotoDataDB
import Settings

conn = sqlite3.connect('PhotoDB.db', check_same_thread=False)
cur = conn.cursor()


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
def check_exists_from_db(all_photos_db: list[list[str, str], ...], all_socnets_db: list[list[str, str], ...]):
    for i in range(0, len(all_photos_db)):
        if os.path.exists(f"{all_photos_db[i][0]}/{all_photos_db[i][1]}"):
            if Settings.get_destination_media() not in all_photos_db[i][0]:
                sql_str1 = f"DELETE FROM photos WHERE catalog = \'{all_photos_db[i][0]}\' and filename = \'{all_photos_db[i][1]}\'"
                cur.execute(sql_str1)
                sql_str2 = f"DELETE FROM socialnetworks WHERE catalog = \'{all_photos_db[i][0]}\' and filename = \'{all_photos_db[i][1]}\'"
                cur.execute(sql_str2)
                if '/alone/' in all_photos_db[i][0]:
                    FilesDirs.transfer_const_photos(f"{all_photos_db[i][0]}/{all_photos_db[i][1]}")
                elif '/const/' in all_photos_db[i][0]:
                    FilesDirs.transfer_alone_photos(f"{all_photos_db[i][0]}/{all_photos_db[i][1]}")
        else:
            sql_str_del = f"DELETE FROM photos WHERE catalog = \'{all_photos_db[i][0]}\' and filename = \'{all_photos_db[i][1]}\'"
            cur.execute(sql_str_del)

    for i in range(0, len(all_socnets_db)):
        if os.path.exists(f"{all_socnets_db[i][0]}/{all_socnets_db[i][1]}"):
            if Settings.get_destination_media() not in all_socnets_db[i][0]:
                sql_str1 = f"DELETE FROM photos WHERE catalog = \'{all_socnets_db[i][0]}\' and filename = \'{all_socnets_db[i][1]}\'"
                cur.execute(sql_str1)
                sql_str2 = f"DELETE FROM socialnetworks WHERE catalog = \'{all_socnets_db[i][0]}\' and filename = \'{all_socnets_db[i][1]}\'"
                cur.execute(sql_str2)
                if '/alone/' in all_socnets_db[i][0]:
                    FilesDirs.transfer_const_photos(f"{all_socnets_db[i][0]}/{all_socnets_db[i][1]}")
                elif '/const/' in all_socnets_db[i][0]:
                    FilesDirs.transfer_alone_photos(f"{all_socnets_db[i][0]}/{all_socnets_db[i][1]}")
        else:
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
        photoname = combo[1]
        photodirectory = combo[0]
        sql_str1 = f"SELECT * FROM photos WHERE catalog = \'{photodirectory}\' AND filename =\'{photoname}\'"
        sql_str2 = f"SELECT * FROM socialnetworks WHERE catalog = \'{photodirectory}\' AND filename =\'{photoname}\'"

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


def check_destination_corr_db():
    all_photos_db, all_socnets_db = get_all_db_ways()
    media_destination = Settings.get_destination_media()
    photo_conflicts = 0
    socnet_conflicts = 0

    for combo in all_photos_db:
        if media_destination in combo[0]:
            pass
        else:
            photo_conflicts += 1
    for combo in all_socnets_db:
        if media_destination in combo[0]:
            pass
        else:
            socnet_conflicts += 1
    return photo_conflicts, socnet_conflicts


# работает лучше, чем ожидалось
# check_exists_from_db(get_all_db_ways()[0], get_all_db_ways()[1])
# add_flaw_to_db(research_all_media_photos())
