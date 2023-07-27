import os
import sqlite3
import datetime

from Explorer import FilesDirs, Thumbnail
from Metadata import Metadata
from GUI import Settings

conn = sqlite3.connect("PhotoDB.db", check_same_thread=False)
cur = conn.cursor()


def get_all_db_ways() -> tuple[list[list[str]], list[list[str]]]:
    """
    Получить все каталоги+файлы из ФотоДБ (таблицы фото и соцсети) (обе таблицы)
    :return: список путей (путь каталога, имя файла) таблицы фото и таблицы соцсетей
    """

    sql_str1 = "SELECT catalog, filename FROM photos"
    sql_str2 = "SELECT catalog, filename FROM socialnetworks"

    cur.execute(sql_str1)
    all_photos_db = cur.fetchall()

    cur.execute(sql_str2)
    all_socnets_db = cur.fetchall()

    return all_photos_db, all_socnets_db


def check_exists_from_db(all_photos_db: list[list[str]], all_socnets_db: list[list[str]]) -> None:
    """
    Проверить существуют ли файлы из БД на диске.
    Если файла, путь к которому указан в БД, не существует - стереть запись.
    :param all_photos_db: список путей таблицы photos БД PhotoDB.
    :param all_socnets_db: список путей таблицы socialnetworks БД PhotoDB.
    :return: если файла по записанному пути не оказывается - запись из БД стирается.
    """
    for i in range(0, len(all_photos_db)):
        if os.path.exists(f"{all_photos_db[i][0]}/{all_photos_db[i][1]}"):
            if Settings.get_destination_media() not in all_photos_db[i][0]:
                sql_str1 = f"DELETE FROM photos WHERE catalog = \'{all_photos_db[i][0]}\' " \
                           f"AND filename = \'{all_photos_db[i][1]}\'"
                cur.execute(sql_str1)
                sql_str2 = f"DELETE FROM socialnetworks WHERE catalog = \'{all_photos_db[i][0]}\' " \
                           f"AND filename = \'{all_photos_db[i][1]}\'"
                cur.execute(sql_str2)
                if "/alone/" in all_photos_db[i][0]:
                    FilesDirs.transfer_const_photos(f"{all_photos_db[i][0]}/{all_photos_db[i][1]}")
                elif "/const/" in all_photos_db[i][0]:
                    FilesDirs.transfer_alone_photos(f"{all_photos_db[i][0]}", f"{all_photos_db[i][1]}")
        else:
            sql_str_del = f"DELETE FROM photos WHERE catalog = \'{all_photos_db[i][0]}\' AND filename = \'{all_photos_db[i][1]}\'"
            cur.execute(sql_str_del)

    for i in range(0, len(all_socnets_db)):
        if os.path.exists(f"{all_socnets_db[i][0]}/{all_socnets_db[i][1]}"):
            if Settings.get_destination_media() not in all_socnets_db[i][0]:
                sql_str1 = f"DELETE FROM photos WHERE catalog = \'{all_socnets_db[i][0]}\' AND filename = \'{all_socnets_db[i][1]}\'"
                cur.execute(sql_str1)
                sql_str2 = f"DELETE FROM socialnetworks WHERE catalog = \'{all_socnets_db[i][0]}\' AND filename = \'{all_socnets_db[i][1]}\'"
                cur.execute(sql_str2)
                if "/alone/" in all_socnets_db[i][0]:
                    FilesDirs.transfer_const_photos(f"{all_socnets_db[i][0]}/{all_socnets_db[i][1]}")
                elif "/const/" in all_socnets_db[i][0]:
                    FilesDirs.transfer_alone_photos(f"{all_photos_db[i][0]}", f"{all_socnets_db[i][1]}")
        else:
            sql_str = f"DELETE FROM socialnetworks WHERE catalog = \'{all_socnets_db[i][0]}\' and filename = \'{all_socnets_db[i][1]}\'"
            cur.execute(sql_str)
    conn.commit()


def research_all_media_photos() -> list[list[str]]:
    """
    Найти все фото в директории хранения медиа.
    Сбор вообще всех JPG, кроме миниатюр, в директории хранения фотографий.
    :return: список абсолютных путей.
    """
    filelist = []
    path = Settings.get_destination_media() + "/Media/Photo"
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".JPG"):
                filelist.append([root.replace("\\", "/"), file])

    return filelist


def add_flaw_to_db(filelist: list[list[str]]) -> None:
    """
    Если фото есть в директории хранения, но нет в БД - сделать запись в БД, как при добавлении фото в каталог.
    Для каждой таблицы производится отдельная проверка на наличие записи. Защита от дублирований на случай, если в
    однйо таблице запись есть, а во второй нет.
    :param filelist: список абсолютных путей всех фотографий формата JPG, кроме миниатюр, в директории хранения фото.
    :return: записи в БД PhotoDB в обеих таблицах
    """
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
            # camera, lens, shootingdate, GPS = "Canon EOS 200D", "EF-S 10-18 mm", "2020.05.20 14:21:20", ""
            camera, lens, shootingdatetime, gps, usercomment = Metadata.exif_for_db(
                Metadata.read_exif(f"{photodirectory}/{photoname}"))
            if shootingdatetime != "":
                shootingdate = shootingdatetime[:10]
            else:
                shootingdate = shootingdatetime

            if not answer_photo:
                sql_str1 = f"INSERT INTO photos VALUES (\'{photoname}\', \'{photodirectory}\', \'{camera}\', \'{lens}\',' \
                           f' \'{shootingdate}\', \'{shootingdatetime}\', \'{additiontime}\', \'{gps}\', \'{usercomment}\')"

                cur.execute(sql_str1)

            if not answer_socnets:
                sql_str_get_nets = "PRAGMA table_info(socialnetworks)"
                cur.execute(sql_str_get_nets)
                all_column_names = cur.fetchall()
                if len(all_column_names) == 3:
                    sql_str2 = f"INSERT INTO socialnetworks VALUES (\'{photoname}\',\'{photodirectory}\',\'{shootingdate}\')"
                else:
                    sn_str = r""
                    for i in range(len(all_column_names) - 3):
                        sn_str += ",\'No value\' "
                    sql_str2 = f"INSERT INTO socialnetworks VALUES (\'{photoname}\',\'{photodirectory}\',\'{shootingdate}\'{sn_str})"

                cur.execute(sql_str2)

    conn.commit()


def check_destination_corr_db() -> tuple[int, int]:
    """
    Проверка, что в путях в БД содержится путь хранения медиа, т.е. БД ведёт к папке хранения, а не куда-то в небытие.
    Проверка для отображения "количества ошибок" в ГУЕ.
    :return: количество записей, где в графе catalog не содержится путь к директории хранения фото из настроек.
    """
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


def get_photo_db_ways():
    """
    Получить все каталоги+файлы из ФотоДБ (таблица фото)
    """
    sql_str = "SELECT catalog, filename FROM photos"
    cur.execute(sql_str)
    all_photos_db = cur.fetchall()
    return all_photos_db


def thumbnail_photo_conformity() -> None:
    """
    Соотнести миниатюры в папке хранения и фотографии, лишние миниатюры удалить, недостающие добавить.
    Используется для удаления лишних миниатюр, которые не были удалены при удалении фотографий и создания недостающих.
    :return: создаются или удаляются миниатюры
    """
    thumb_list = research_all_thumbnails()
    destination_media = Settings.get_destination_media() + "/Media/Photo/"
    for file in thumb_list:
        if "thumbnail_" not in file:
            os.remove(file)
        else:
            path_splitted = file.split("/")
            file_name = path_splitted[-1][10:]
            if "const" in path_splitted:
                date_part = f"{path_splitted[-4]}/{path_splitted[-3]}/{path_splitted[-2]}/"
                photo_way = destination_media + "const/" + date_part + file_name
                if os.path.exists(photo_way):
                    pass
                else:
                    os.remove(file)
            elif "alone" in path_splitted:
                dir_name_part = path_splitted[-2]
                photo_way = destination_media + "alone/" + dir_name_part + "/" + file_name
                if os.path.exists(photo_way):
                    pass
                else:
                    os.remove(file)
            elif "view" in path_splitted:
                pass
            else:
                os.remove(file)

    destination_thumbs = Settings.get_destination_thumb() + "/thumbnail/"
    photo_paths = get_photo_db_ways()
    for combo in photo_paths:
        catalog_splitted = combo[0].split("/")
        if "const" in catalog_splitted:
            date_part = f"{catalog_splitted[-3]}/{catalog_splitted[-2]}/{catalog_splitted[-1]}/"
            thumbnail_way = destination_thumbs + "const/" + date_part + "thumbnail_" + combo[1]
            if os.path.exists(thumbnail_way):
                pass
            else:
                Thumbnail.make_const_thumbnails(combo[0], combo[1])

        elif "alone" in catalog_splitted:
            catalog_name = combo[0].split("/")[-1]
            thumbnail_way = destination_thumbs + "alone/" + catalog_name + "/" + "thumbnail_" + combo[1]
            if os.path.exists(thumbnail_way):
                pass
            else:
                Thumbnail.make_alone_thumbnails(catalog_name, f"{combo[0]}/{combo[1]}", combo[1])


def research_all_thumbnails() -> list[str]:
    """
    Получается список всех миниатюр в директории хранения
    :return: список путей файлов, которые передаются как список из 1 элемента, надо бы это поправить
    """
    filelist = []
    path = Settings.get_destination_thumb() + "/thumbnail"
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".JPG"):
                filelist.append(root.replace("\\", "/") + "/" + file)

    return filelist
