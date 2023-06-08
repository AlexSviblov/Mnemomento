import datetime
import logging
import os
import sqlite3
from typing import Tuple, List, Any

import Metadata
import Settings

conn = sqlite3.connect(f'file:{os.getcwd()}\\PhotoDB.db', check_same_thread=False, uri=True)
cur = conn.cursor()


# Добавление записи в БД при добавлении фото в каталог
def add_to_database(photoname: str, photodirectory: str, metadata: dict) -> None:
    """
    Добавить запись о фотографии, добавляемой в программу, в базу данных.
    :param metadata: словар ьс метаданными
    :param photoname: имя фотографии.
    :param photodirectory: каталог хранения фотографии.
    :return: добавляются 2 записи в БД (1 в таблице photos, 2 в socialnetworks)
    """
    additiontime = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")

    # camera, lens, shootingdate, GPS = 'Canon EOS 200D', 'EF-S 10-18 mm', '2020.05.20 14:21:20', "No Data"
    camera, lens, shootingdatetime, GPS, usercomment = Metadata.exif_for_db(metadata)
    if shootingdatetime != "":
        shootingdate = shootingdatetime[:10]
    else:
        shootingdate = shootingdatetime

    sql_str1 = f'INSERT INTO photos VALUES (\'{photoname}\', \'{photodirectory}\', \'{camera}\', \'{lens}\',' \
               f' \'{shootingdate}\', \'{shootingdatetime}\', \'{additiontime}\', \'{GPS}\', \'{usercomment}\')'
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

    cur.execute(sql_str1)

    cur.execute(sql_str2)
    conn.commit()
    logging.info(f'In DB added record about {photodirectory}/{photoname}')


# Удаление записи из БД при удалении фото из основного каталога
def del_from_database(photoname: str, photodirectory: str) -> None:
    """
    Удаление записи из БД при удалении фотографии, определение какую запрись удалять - по имени файла и каталогу.
    :param photoname: абсолютный путь фотографии.
    :param photodirectory: каталог хранения фотографии.
    :return: удаляются 2 записи в БД (1 в таблице photos, 2 в socialnetworks)
    """
    sql_str = f'DELETE FROM photos WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
    cur.execute(sql_str)

    sql_str = f'DELETE FROM socialnetworks WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
    cur.execute(sql_str)

    conn.commit()
    logging.info(f'From DB removed record about {photodirectory}/{photoname}')


# Запись изменений, внесённых пользователем при редактировании метаданных, которые есть в БД
def edit_in_database(photoname: str, photodirectory: str, new_value_dict) -> None:
    """
    Редактированию подлежат поля таблицы photos камера, объектив, дата съёмки,координаты GPS.
    :param new_value_dict: словарь с новыми значениями
    :param photoname: имя файла.
    :param photodirectory: каталог хранения.
    :return: изменение записи в соответствии с редактированием метаданных.
    """
    for editing_type in list(new_value_dict.keys()):
        new_text = new_value_dict[editing_type]

        match editing_type:
            case 1:       # камера
                sql_str = f'UPDATE photos SET camera = \'{new_text}\' WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
                cur.execute(sql_str)
                conn.commit()

            case 2:     # объектив
                sql_str = f'UPDATE photos SET lens = \'{new_text}\' WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
                cur.execute(sql_str)
                conn.commit()

            case 11:     # дата съёмки
                shootingdate = new_text[:4] + '.' + new_text[5:7] + '.' + new_text[8:10]
                shootingdatetime = new_text[:4] + '.' + new_text[5:7] + '.' + new_text[8:10] + new_text[10:]
                sql_str1 = f'UPDATE photos SET shootingdate = \'{shootingdate}\' WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
                sql_str2 = f'UPDATE photos SET shootingdatetime = \'{shootingdatetime}\' WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
                sql_str3 = f'UPDATE socialnetworks SET shootingdate = \'{shootingdate}\' WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''

                cur.execute(sql_str1)
                cur.execute(sql_str2)
                cur.execute(sql_str3)
                conn.commit()

            case 7:    # GPS
                sql_str = f'UPDATE photos SET GPSdata = \'{new_text}\' WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
                cur.execute(sql_str)
                conn.commit()

            case 12:
                sql_str = f'UPDATE photos SET comment = \'{new_text}\' WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
                cur.execute(sql_str)
                conn.commit()

            case _:       # другие данные (которых нет в БД)
                pass

        logging.info(f"PhotoDataDB - In DB edited record about {photodirectory}/{photoname} - {editing_type} = {new_text}")


# при переносе в другую папку надо переписать её путь в БД
def catalog_after_transfer(photoname: str, old_directory: str, new_directory: str) -> None:
    """
    При переносе фотографии основного каталога из-за смены даты съёмки в метаданных, необходимо отредактировать
    поле catalog обеих таблиц.
    :param photoname: имя файла.
    :param old_directory: путь новой директории.
    :param new_directory: путь старой директории.
    :return: отредактированные записи.
    """
    sql_str1 = f'UPDATE photos SET catalog =\'{old_directory}\' WHERE filename = \'{photoname}\' AND catalog = \'{new_directory}\''
    sql_str2 = f'UPDATE socialnetworks SET catalog =\'{old_directory}\' WHERE filename = \'{photoname}\' AND catalog = \'{new_directory}\''

    cur.execute(sql_str1)
    cur.execute(sql_str2)
    conn.commit()

    logging.info(f"PhotoDataDB - After transfer to another directory, updated record in DB, file {photoname} moved from {old_directory} to {new_directory}")


# записать в БД новое имя при переименовании при переносе
def filename_after_transfer(prewname: str, rename: str, newcatalog: str, oldcatalog: str, code: int) -> None:
    """
    Если при смене даты, пришлось менять имя файла - перезаписать и каталог, и имя файла в БД.
    :param prewname: прошлое имя файла.
    :param rename: новое имя файла.
    :param newcatalog: каталог, откуда переносится файл.
    :param oldcatalog: каталог, куда переносится файл.
    :param code: 0 - переименовывается переносимый файл, 1 - переименовывается файл в папк еназначения.
    :return: отредактированная 1/2 записи в БД.
    """
    if code == 0:   # переименовывается переносимый файл, в котором поменяли дату
        sql_str1 = f"UPDATE photos SET catalog = \'temp\' WHERE filename = \'{prewname}\' AND catalog = \'{newcatalog}\'"
        cur.execute(sql_str1)
        sql_str2 = f"UPDATE photos SET filename = \'{rename}\' WHERE filename = \'{prewname}\' AND catalog = \'temp\'"
        cur.execute(sql_str2)
        sql_str3 = f"UPDATE photos SET catalog = \'{oldcatalog}\' WHERE filename = \'{rename}\' AND catalog = \'temp\'"
        cur.execute(sql_str3)

        sql_str4 = f"UPDATE socialnetworks SET catalog = \'temp\' WHERE filename = \'{prewname}\' AND catalog = \'{newcatalog}\'"
        cur.execute(sql_str4)
        sql_str5 = f"UPDATE socialnetworks SET filename = \'{rename}\' WHERE filename = \'{prewname}\' AND catalog = \'temp\'"
        cur.execute(sql_str5)
        sql_str6 = f"UPDATE socialnetworks SET catalog = \'{oldcatalog}\' WHERE filename = \'{rename}\' AND catalog = \'temp\'"
        cur.execute(sql_str6)

    else:   # code == 1 - переименовывается файл уже находящийся в папке назначения
        sql_str1 = f"UPDATE photos SET filename = \'{rename}\' WHERE filename = \'{prewname}\' AND catalog = \'{oldcatalog}\'"
        cur.execute(sql_str1)
        sql_str2 = f"UPDATE photos SET catalog = \'{oldcatalog}\' WHERE filename = \'{prewname}\' AND catalog = \'{newcatalog}\'"
        cur.execute(sql_str2)

        sql_str3 = f"UPDATE socialnetworks SET filename = \'{rename}\' WHERE filename = \'{prewname}\' AND catalog = \'{oldcatalog}\'"
        cur.execute(sql_str3)
        sql_str4 = f"UPDATE socialnetworks SET catalog = \'{oldcatalog}\' WHERE filename = \'{prewname}\' AND catalog = \'{newcatalog}\'"
        cur.execute(sql_str4)
    conn.commit()

    logging.info(f"PhotoDataDB - File {newcatalog}/{prewname} transfered to {oldcatalog}/{rename}")


# достать вбитые в БД теги соцсетей
def get_social_tags(photoname: str, photodirectory: str) -> tuple[list[str], dict]:
    """
    Для фотографии достать выбранные статусы выкладывания в БД.
    :param photoname: имя файла.
    :param photodirectory: каталог хранения.
    :return: список названий соцсетей, список статусов, соответствие друг другу по индексам, так как они одной длины.
    """
    sql_str_get_nets = 'PRAGMA table_info(socialnetworks)'
    cur.execute(sql_str_get_nets)
    all_column_names = cur.fetchall()

    sn_column_names = [all_column_names[i][1] for i in range(3, len(all_column_names))]

    sql_str_get_status = f'SELECT * FROM socialnetworks WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
    cur.execute(sql_str_get_status)

    all_data = cur.fetchall()
    all_sn_data = all_data[0]

    sn_tags_values = dict()
    for i in range(3, len(all_sn_data)):
        sn_tags_values[f'{sn_column_names[i-3]}'] = all_sn_data[i]

    return sn_column_names, sn_tags_values


# редактирование тегов соцсетей
def edit_sn_tags(photoname: str, photodirectory: str, new_status: str, network: str) -> None:
    """
    При изменении тега в графическом интерфейсе - сменить статус в БД.
    :param photoname: имя файла.
    :param photodirectory: каталог.
    :param new_status: новый выбранный статус (Не выбрано(No value), Не публиковать(No publicate),
    Опубликовать(Will publicate), Опубликовано(Publicated))
    :param network: соцсеть, в которой надо сменить статус.
    :return: изменение статуса в БД.
    """
    sql_str = f'UPDATE socialnetworks SET {network} = \'{new_status}\' WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
    cur.execute(sql_str)

    conn.commit()


# список соцсетей в БД
def get_socialnetworks() -> list[str]:
    """
    Достаётся список добавленных в программу соцсетей. Возвращаются имена столбцов таблицы.
    :return: список названий столбцов - соцсетей.
    """
    sql_str_get_nets = 'PRAGMA table_info(socialnetworks)'
    cur.execute(sql_str_get_nets)
    all_column_names = cur.fetchall()

    sn_column_names = [all_column_names[i][1] for i in range(3, len(all_column_names))]

    return sn_column_names


# список камер и объективов из БД
def get_equipment() -> tuple[list[str], list[str]]:
    """
    Вытащить из базы данных все имеющиеся варианты камер и объективов.
    :return: список всех камер и объективов, по одному экземпляру каждого, с исправлением из ErrorNames.db
    """
    sql_str_get_camera = 'SELECT camera, count(camera) FROM photos GROUP BY camera'
    cur.execute(sql_str_get_camera)
    camera_all_data = cur.fetchall()
    camera_counter = dict()
    for i in range(len(camera_all_data)):
        camera_counter[f'{camera_all_data[i][0]}'] = camera_all_data[i][1]

    cameras_list = Metadata.equip_name_check_with_counter(camera_counter, 'camera')

    sql_str_get_lens = 'SELECT lens, count(lens) FROM photos GROUP BY lens'
    cur.execute(sql_str_get_lens)
    lens_all_data = cur.fetchall()
    lens_counter = dict()
    for i in range(len(lens_all_data)):
        lens_counter[f'{lens_all_data[i][0]}'] = lens_all_data[i][1]

    lens_list = Metadata.equip_name_check_with_counter(lens_counter, 'lens')

    return cameras_list, lens_list,


# получить полный путь ко всем фото, у которых указаны выбранные камера и объектив
def get_equip_photo_list(camera_exif: str, camera: str, lens_exif: str, lens: str, comment_status: bool, comment_text: str) -> list[str]:
    """
    Получить полный путь ко всем фото, у которых указаны выбранные камера и объектив.
    При наличии исправлений в ErrorNames, надо учесть, что какие-то записи могут быть сделаны вручную, а какие-то
    автоматически из метаданных.
    :param comment_text: тег, если есть
    :param comment_status: искать ли по тегам
    :param camera_exif: значение из автоматически созданных exif.
    :param camera: исправленное название камеры (либо повторение exif, если оно не исправляется).
    :param lens_exif: значение из автоматически созданных exif.
    :param lens: исправленное название объектива (либо повторение exif, если оно не исправляется).
    :return: список абсолютных путей ко всем файлам с выбранными камерой и объективом.
    """
    if not comment_status:
        if camera_exif == 'All' and camera == 'All' and lens == 'All' and lens_exif == 'All':
            sql_str = f'SELECT filename, catalog FROM photos {db_order_settings()}'
        elif (camera_exif == 'All' and camera == 'All') and (lens != 'All' or lens_exif != 'All'):
            sql_str = f'SELECT filename, catalog FROM photos WHERE (lens = \'{lens}\' OR lens = \'{lens_exif}\') {db_order_settings()}'
        elif (camera_exif != 'All' or camera != 'All') and (lens == 'All' and lens_exif == 'All'):
            sql_str = f'SELECT filename, catalog FROM photos WHERE (camera = \'{camera}\' OR camera = \'{camera_exif}\') {db_order_settings()}'
        else:
            sql_str = f'SELECT filename, catalog FROM photos WHERE (camera = \'{camera}\' OR camera = \'{camera_exif}\') AND (lens = \'{lens}\' OR lens = \'{lens_exif}\') {db_order_settings()}'
    else:
        if camera_exif == 'All' and camera == 'All' and lens == 'All' and lens_exif == 'All':
            sql_str = f'SELECT filename, catalog FROM photos  WHERE comment LIKE \'%{comment_text}%\' {db_order_settings()}'
        elif (camera_exif == 'All' and camera == 'All') and (lens != 'All' or lens_exif != 'All'):
            sql_str = f'SELECT filename, catalog FROM photos WHERE (lens = \'{lens}\' OR lens = \'{lens_exif}\') AND comment LIKE \'%{comment_text}%\' {db_order_settings()}'
        elif (camera_exif != 'All' or camera != 'All') and (lens == 'All' and lens_exif == 'All'):
            sql_str = f'SELECT filename, catalog FROM photos WHERE (camera = \'{camera}\' OR camera = \'{camera_exif}\')  AND comment LIKE \'%{comment_text}%\' {db_order_settings()}'
        else:
            sql_str = f'SELECT filename, catalog FROM photos WHERE (camera = \'{camera}\' OR camera = \'{camera_exif}\') AND (lens = \'{lens}\' OR lens = \'{lens_exif}\')  AND comment LIKE \'%{comment_text}%\' {db_order_settings()}'

    cur.execute(sql_str)

    photodb_data = cur.fetchall()

    fullpaths = [f"{photo[1]}/{photo[0]}" for photo in photodb_data if 'Media/Photo/const' in photo[1]]

    return fullpaths


# получить полный путь всех фото, у которых в выбранной соцсети указан выбранный статус
def get_sn_photo_list(network: str, status: str, comment_status: bool, comment_text: str) -> list[str]:
    """
    Список абсолютных путей с выбранным статусом в выбранной соцсети.
    :param comment_text: тег, если есть
    :param comment_status: искать по тегу или нет
    :param network: соцсеть (надпись из GUI, без приставки numnumnum).
    :param status: 1 из 4 возможных статусов в формате БД.
    :return: абсолютные пути фото с выбранным статусом в выбранной соцсети.
    """
    match status:
        case 'Не выбрано':
            status_bd = 'No value'
        case 'Не публиковать':
            status_bd = 'No publicate'
        case 'Опубликовать':
            status_bd = 'Will publicate'
        case 'Опубликовано':
            status_bd = 'Publicated'
        case _:
            status_bd = 'No value'

    try:
        sql_str = f'SELECT filename, catalog FROM socialnetworks WHERE {network} = \'{status_bd}\' {db_order_settings()}'
        cur.execute(sql_str)
        photodb_data = cur.fetchall()
    except:     # поймать ошибку с тем, что нет столбца network, так как у столбца начало 'numnumnum'
        sql_str = f'SELECT filename, catalog FROM socialnetworks WHERE numnumnum{network} = \'{status_bd}\' {db_order_settings()}'
        cur.execute(sql_str)
        photodb_data = cur.fetchall()

    if comment_status:
        sql_str = f'SELECT filename, catalog FROM photos WHERE comment LIKE \'%{comment_text}%\''
        cur.execute(sql_str)
        with_comments_list = cur.fetchall()
    else:
        with_comments_list = photodb_data

    fullpaths = [f"{photo[1]}/{photo[0]}" for photo in photodb_data if 'Media/Photo/const' in photo[1] and photo in with_comments_list]

    return fullpaths


# удалить все записи о файлах из удаляемой папки доп.каталога
def del_alone_dir(photo_directory: str) -> None:
    """
    Удалить все записи, в которых указан удаляемый каталог.
    :param photo_directory: название папки.
    :return: удаление записей.
    """
    photo_list = [file for file in os.listdir(photo_directory) if file.endswith(".jpg") or file.endswith(".JPG")]

    for photo in photo_list:
        sql_str = f'DELETE FROM photos WHERE filename = \'{photo}\' AND catalog = \'{photo_directory}\''
        cur.execute(sql_str)

        sql_str = f'DELETE FROM socialnetworks WHERE filename = \'{photo}\' AND catalog = \'{photo_directory}\''
        cur.execute(sql_str)

        conn.commit()


# выдать список фоток в папке доп.каталога с выбранными статусами в соцсетях
def get_sn_alone_list(photo_directory: str, network: str, status: str) -> list[str]:
    """
    Для папки в доп.каталоге вернуть список файлов с выбранным статусом в выбранной соцсети.
    :param photo_directory: путь директории папки.
    :param network: имя выбранной соцсети.
    :param status: выбранный статус.
    :return: список имён файлов из выбранной папки с выбранным статусом в выбранной соцсети.
    """
    try:
        sql_str = f'SELECT filename FROM socialnetworks WHERE {network} = \'{status}\' AND catalog = \'{photo_directory}\''
        cur.execute(sql_str)
        photodb_data = cur.fetchall()
    except:     # поймать ошибку с тем, что нет столбца network, так как у столбца начало 'numnumnum'
        sql_str = f'SELECT filename FROM socialnetworks WHERE numnumnum{network} = \'{status}\' AND catalog = \'{photo_directory}\''
        cur.execute(sql_str)
        photodb_data = cur.fetchall()

    photo_list = [photo[0] for photo in photodb_data]

    return photo_list


# получить пути для БД для перезаписи при переносе
def transfer_media_ways(old_way: str, new_way: str) -> tuple[list[str], list[str]]:
    """
    При переносе файлов из-за изменения пути хранения фотографии в настройках перезаписать пути в БД.
    :param old_way: старый путь.
    :param new_way: новый путь каталога.
    :return: все старые пути и все новые пути для перезаписи.
    """
    sql_str = f"SELECT catalog from photos"
    cur.execute(sql_str)

    all_catalogs = cur.fetchall()

    old_catalogs = [all_catalogs[i][0] for i in range(len(all_catalogs))]

    end_catalogs = [old_catalogs[i][len(old_way):] for i in range(len(all_catalogs))]

    new_catalogs = [new_way + end_catalogs[i] for i in range(len(all_catalogs))]

    return new_catalogs, old_catalogs


# перезаписать пути в БД, если при изменении настроек программы, был перенос файлов
def transfer_media(new_catalog: str, old_catalog: str) -> None:
    """
    При переносе файлов из-за изменения пути хранения фотографии в настройках перезаписать пути в БД.
    :param new_catalog: новый путь каталога.
    :param old_catalog: старый путь каталога.
    :return: перезаписанные данные в БД.
    """
    sql_str1 = f'UPDATE photos SET catalog = \'{new_catalog}\' WHERE catalog = \'{old_catalog}\''
    sql_str2 = f'UPDATE socialnetworks SET catalog = \'{new_catalog}\' WHERE catalog = \'{old_catalog}\''
    cur.execute(sql_str1)
    cur.execute(sql_str2)
    conn.commit()


# при очистке метаданных - обнулить значения в '' в БД
def clear_metadata(photo_name: str, photo_directory: str) -> None:
    """
    Очистка столбцов метаданных в БД (камера, объектив, дата съёмки, дата и время съёмки, GPS в таблице photos и
    дата съёмки в таблице socialnetworks).
    :param photo_name:
    :param photo_directory:
    :return: у файла с очищенными метаданными в БД заменить значения метаданных на No data.
    """
    sql_str1 = f"UPDATE photos SET camera = \'\' WHERE catalog = \'{photo_directory}\' and filename = \'{photo_name}\'"
    sql_str2 = f"UPDATE photos SET lens = \'\' WHERE catalog = \'{photo_directory}\' and filename = \'{photo_name}\'"
    sql_str3 = f"UPDATE photos SET shootingdate = \'\' WHERE catalog = \'{photo_directory}\' and filename = \'{photo_name}\'"
    sql_str4 = f"UPDATE photos SET shootingdatetime = \'\' WHERE catalog = \'{photo_directory}\' and filename = \'{photo_name}\'"
    sql_str5 = f"UPDATE photos SET GPSdata = \'\' WHERE catalog = \'{photo_directory}\' and filename = \'{photo_name}\'"
    sql_str6 = f"UPDATE socialnetworks SET shootingdate = \'\' WHERE catalog = \'{photo_directory}\' and filename = \'{photo_name}\'"
    sql_str7 = f"UPDATE photos SET catalog = \'{Settings.get_destination_media()}/Media/Photo/const/No_Date_Info/No_Date_Info/No_Date_Info\' WHERE catalog = \'{photo_directory}\' and filename = \'{photo_name}\'"
    sql_str8 = f"UPDATE socialnetworks SET catalog = \'{Settings.get_destination_media()}/Media/Photo/const/No_Date_Info/No_Date_Info/No_Date_Info\' WHERE catalog = \'{photo_directory}\' and filename = \'{photo_name}\'"

    cur.execute(sql_str1)
    cur.execute(sql_str2)
    cur.execute(sql_str3)
    cur.execute(sql_str4)
    cur.execute(sql_str5)
    cur.execute(sql_str6)
    cur.execute(sql_str7)
    cur.execute(sql_str8)

    conn.commit()

    logging.info(f"PhotoDataDB - Metadata of {photo_directory}/{photo_name} cleared in DB")

# TODO: comment


# достать из БД список фото сделанных в определённый день
def get_date_photo_list(year: str, month: str, day: str, comment_status: bool, comment_text: str) -> list[str]:
    """
    В БД записывается дата съёмки, тут достаются из БД все записи о фото, сделанных в указанную дату
    :param comment_text: тег, если есть
    :param comment_status: искать по тегам или нет
    :param year: год съёмки
    :param month: месяц съёмки
    :param day: день съёмки
    :return: список полных путей к фотографиям
    """
    if year == 'No_Date_Info':
        date_to_search = ''
        if not comment_status:
            sql_str = f"SELECT filename, catalog FROM photos WHERE shootingdate = \'{date_to_search}\' {db_order_settings()}"
        else:
            sql_str = f"SELECT filename, catalog FROM photos WHERE shootingdate = \'{date_to_search}\' AND comment LIKE \'%{comment_text}%\' {db_order_settings()}"
        cur.execute(sql_str)
        photodb_data = cur.fetchall()
    else:
        if year != 'All' and month != 'All' and day == 'All':
            date_part = ''
            for i in range(1, 32):
                str_i = str(i)
                if len(str_i) == 1:
                    str_i = '0' + str_i
                date_to_search = f"{year}.{month}.{str_i}"
                date_part += f"(shootingdate = \'{date_to_search}\')"
                if i != 31:
                    date_part += f" OR "
            if not comment_status:
                sql_str = f"SELECT filename, catalog FROM photos WHERE {date_part} {db_order_settings()}"
            else:
                sql_str = f"SELECT filename, catalog FROM photos WHERE {date_part} AND comment LIKE \'%{comment_text}%\' {db_order_settings()}"

            cur.execute(sql_str)
            photodb_data = cur.fetchall()
        elif year != 'All' and month == 'All' and day == 'All':
            date_part = ''
            for j in range(1, 13):
                str_j = str(j)
                if len(str_j) == 1:
                    str_j = '0' + str_j
                for i in range(1, 32):
                    str_i = str(i)
                    if len(str_i) == 1:
                        str_i = '0' + str_i
                    date_to_search = f"{year}.{str_j}.{str_i}"
                    date_part += f"(shootingdate = \'{date_to_search}\')"
                    if j != 12:
                        date_part += f" OR "
                    elif j == 12 and i != 31:
                        date_part += f" OR "
                    else:
                        pass

            if not comment_status:
                sql_str = f"SELECT filename, catalog FROM photos WHERE {date_part} {db_order_settings()}"
            else:
                sql_str = f"SELECT filename, catalog FROM photos WHERE {date_part} AND comment LIKE \'%{comment_text}%\' {db_order_settings()}"

            cur.execute(sql_str)
            photodb_data = cur.fetchall()
        elif year == 'All' and month == 'All' and day == 'All':
            if not comment_status:
                sql_str = f"SELECT filename, catalog FROM photos {db_order_settings()}"
            else:
                sql_str = f"SELECT filename, catalog FROM photos WHERE comment LIKE \'%{comment_text}%\' {db_order_settings()}"

            cur.execute(sql_str)
            photodb_data = cur.fetchall()
        else:
            date_to_search = f"{year}.{month}.{day}"
            if not comment_status:
                sql_str = f"SELECT filename, catalog FROM photos WHERE shootingdate = \'{date_to_search}\' {db_order_settings()}"
            else:
                sql_str = f"SELECT filename, catalog FROM photos WHERE shootingdate = \'{date_to_search}\' AND comment LIKE \'%{comment_text}%\' {db_order_settings()} "

            cur.execute(sql_str)
            photodb_data = cur.fetchall()

    fullpaths = [f"{photo[1]}/{photo[0]}" for photo in photodb_data if 'Media/Photo/const' in photo[1]]

    return fullpaths


# достать GPS-координаты фотографий основного каталога из БД (используется только в GlobalMap)
def get_global_map_info(fullpaths: list[str]) -> tuple[list[list[str | tuple[float, float] | bool | Any]], int, tuple[float | Any, ...] | tuple[float, float]]:
    """
    Достать из БД координаты фотографий. Это очень сильно намного пиздец как намного быстрее, чем доставать их из
    метаданных каждый раз. Заодно здесь же вычисляется, как центрировать и отдалять карту OSM.
    :param fullpaths: абсолютные пути к фото
    :return: сочетание имени файла, его координат, даты съёмки, камеры, пути к миниатюре и группировки, отдаление карты,
    центральные координаты карты.
    """
    names_and_coords = list()
    map_center_buffer = [0.0, 0.0]

    most_north_point = -200.0
    most_south_point = 200.0
    most_west_point = 200.0
    most_east_point = -200.0

    for photofile in fullpaths:
        filename = photofile.split('/')[-1]
        catalog = photofile[:(-1)*len(filename)-1]

        sql_str = f'SELECT GPSdata, camera, shootingdate FROM photos WHERE filename = \'{filename}\' AND catalog = \'{catalog}\''
        cur.execute(sql_str)
        all_db_data = cur.fetchall()[0]
        gps_from_db = all_db_data[0]
        camera_db = all_db_data[1]
        camera = Metadata.equip_name_check([camera_db], 'camera')[0]
        shootingdate = all_db_data[2]
        if gps_from_db == '':
            pass
        else:
            catalog_splitted = catalog.split('/')
            thumbnail_way = f"{Settings.get_destination_thumb()}/thumbnail/const/{catalog_splitted[-3]}/{catalog_splitted[-2]}/{catalog_splitted[-1]}/thumbnail_{filename}"

            lat = float(gps_from_db.split(', ')[0])
            lon = float(gps_from_db.split(', ')[1])

            coords = (lat, lon)
            group_by = False
            for already_added in names_and_coords:
                if already_added[1] == coords:
                    already_added[5] = True
                    group_by = True
            names_and_coords.append([filename, coords, shootingdate, camera, thumbnail_way, group_by])

            map_center_buffer[0] = map_center_buffer[0] + lat
            map_center_buffer[1] = map_center_buffer[1] + lon

            if lat > most_north_point:
                most_north_point = lat
            if lat < most_south_point:
                most_south_point = lat
            if lon > most_east_point:
                most_east_point = lon
            if lon < most_west_point:
                most_west_point = lon

    try:
        map_center_list = [map_center_buffer[0]/len(names_and_coords), map_center_buffer[1]/len(names_and_coords)]
        map_center = tuple(map_center_list)
    except ZeroDivisionError:
        map_center = (55.754117, 37.620280)

    latitude_size = most_north_point - most_south_point
    longitude_size = most_east_point - most_west_point

    if latitude_size > 90 or longitude_size > 180:
        zoom_level = 1
    elif latitude_size > 22.5 or longitude_size > 45:
        zoom_level = 3
    elif latitude_size > 2.813 or longitude_size > 5.625:
        zoom_level = 5
    elif latitude_size > 0.703 or longitude_size > 1.406:
        zoom_level = 7
    elif latitude_size > 0.176 or longitude_size > 0.352:
        zoom_level = 9
    elif latitude_size > 0.044 or longitude_size > 0.088:
        zoom_level = 11
    elif latitude_size > 0.011 or longitude_size > 0.022:
        zoom_level = 13
    elif latitude_size > 0.003 or longitude_size > 0.005:
        zoom_level = 15
    elif latitude_size > 0.0005 or longitude_size > 0.001:
        zoom_level = 17
    elif latitude_size > 0.0001 or longitude_size > 0.0003:
        zoom_level = 19
    else:
        zoom_level = 14

    return names_and_coords, zoom_level, map_center


# переименовать файлы в БД при смене имени
def file_rename(catalog: str, old_file_name: str, new_file_name: str) -> None:
    """
    Переименование файла при его перименовнании в специальной графе окошка редактирования метаданных
    :param catalog: каталог хранения
    :param old_file_name: старое имя файла
    :param new_file_name: новое имя файла
    :return: в БД обновляется запись
    """
    sql_str1 = f"UPDATE photos SET filename = \'{new_file_name}\' WHERE filename = \'{old_file_name}\' AND catalog = \'{catalog}\'"
    sql_str2 = f"UPDATE socialnetworks SET filename = \'{new_file_name}\' WHERE filename = \'{old_file_name}\' AND catalog = \'{catalog}\'"
    cur.execute(sql_str1)
    cur.execute(sql_str2)

    conn.commit()

    logging.info(f"PhotoDataDB - Renaming file in database, catalog - {catalog}, old name - {old_file_name}, new name - {new_file_name}")


# обновить в БД много записей одновременно
def massive_edit_metadata(photo_list: list[str], modify_dict: dict[int, str]) -> None:
    """
    При массовом редактировании камеры, объектив, даты съёмки или координат, надо обновить и записи в БД
    :param photo_list: список абсолютных путей файлов
    :param modify_dict: словарь с новыми данными
    :return: обновлённые записи в БД
    """
    for file in photo_list:
        file_name = file.split('/')[-1]
        file_dir = file[:(-1) * (len(file_name) + 1)]
        edit_in_database(file_name, file_dir, modify_dict)


# в каком порядке выдавать список из БД -> в таком же порядке создаются миниатюры в GUI
def db_order_settings() -> str:
    setting = Settings.get_sort_type()

    match setting:
        case "name-up":
            sort_str = "ORDER BY filename"
        case "name-down":
            sort_str = "ORDER BY filename DESC"
        case "made-up":
            sort_str = "ORDER BY shootingdatetime"
        case "made-down":
            sort_str = "ORDER BY shootingdatetime DESC"
        case "add-up":
            sort_str = "ORDER BY additiondate"
        case "add-down":
            sort_str = "ORDER BY additiondate DESC"
        case _:
            sort_str = "ORDER BY filename"

    return sort_str
