import datetime
import os
import sqlite3

import Metadata
import Settings

conn = sqlite3.connect(f'file:{os.getcwd()}\\PhotoDB.db', check_same_thread=False, uri=True)
cur = conn.cursor()


# Добавление записи в БД при добавлении фото в каталог
def add_to_database(photoname: str, photodirectory: str, metadata: dict) -> None:
    """
    Добавить запись о фотографии, добавляемой в программу, в базу данных.
    :param photoname: имя фотографии.
    :param photodirectory: каталог хранения фотографии.
    :return: добавляются 2 записи в БД (1 в таблице photos, 2 в socialnetworks)
    """
    additiontime = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")

    # camera, lens, shootingdate, GPS = 'Canon EOS 200D', 'EF-S 10-18 mm', '2020.05.20 14:21:20', "No Data"
    camera, lens, shootingdatetime, GPS = Metadata.exif_for_db(photoname, photodirectory, metadata)
    if shootingdatetime != "No data":
        shootingdate = shootingdatetime[:10]
    else:
        shootingdate = shootingdatetime

    sql_str1 = f'INSERT INTO photos VALUES (\'{photoname}\', \'{photodirectory}\', \'{camera}\', \'{lens}\',' \
               f' \'{shootingdate}\', \'{shootingdatetime}\', \'{additiontime}\', \'{GPS}\')'
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


# Запись изменений, внесённых пользователем при редактировании метаданных, которые есть в БД
def edit_in_database(photoname: str, photodirectory: str, editing_type: int, new_text: str) -> None:
    """
    Редактированию подлежат поля таблицы photos камера, объектив, дата съёмки,координаты GPS.
    :param photoname: имя файла.
    :param photodirectory: каталог хранения.
    :param editing_type: тип (1 - камера, 2 - объектив, 7 - PGS, 11 - дата)
    :param new_text: новое значение, вносимое в БД.
    :return: изменение записи в соответствии с редактированием метаданных.
    """
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

        case _:       # другие данные (которых нет в БД)
            pass


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
    if code == 0: # переименовывается переносимый файл, в котором поменяли дату
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

    else: # code == 1 - переименовывается файл уже находящийся в папке назначения
        sql_str1 = f"UPDATE photos SET filename = \'{rename}\' WHERE filename = \'{prewname}\' AND catalog = \'{oldcatalog}\'"
        cur.execute(sql_str1)
        sql_str2 = f"UPDATE photos SET catalog = \'{oldcatalog}\' WHERE filename = \'{prewname}\' AND catalog = \'{newcatalog}\'"
        cur.execute(sql_str2)

        sql_str3 = f"UPDATE socialnetworks SET filename = \'{rename}\' WHERE filename = \'{prewname}\' AND catalog = \'{oldcatalog}\'"
        cur.execute(sql_str3)
        sql_str4 = f"UPDATE socialnetworks SET catalog = \'{oldcatalog}\' WHERE filename = \'{prewname}\' AND catalog = \'{newcatalog}\'"
        cur.execute(sql_str4)
    conn.commit()


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
    sn_column_names = list()
    for i in range(3, len(all_column_names)):
        sn_column_names.append(all_column_names[i][1])

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
    sn_column_names = list()
    for i in range(3, len(all_column_names)):
        sn_column_names.append(all_column_names[i][1])
    return sn_column_names


# список камер и объективов из БД
def get_equipment() -> tuple[list[str], list[str]]:
    """
    Вытащить из базы данных все имеющиеся варианты камер и объективов.
    :return: список всех камер и объективов, по одному экземпляру каждого, с исправлением из ErrorNames.db
    """
    sql_str_get_camera = 'SELECT camera FROM photos'
    cur.execute(sql_str_get_camera)
    camera_all_data = cur.fetchall()
    camera_buf = list()
    for i in range(len(camera_all_data)):
        if camera_all_data[i][0] in camera_buf:
            pass
        else:
            camera_buf.append(camera_all_data[i][0])

    cameras_list = Metadata.equip_name_check(camera_buf, 'camera')

    sql_str_get_lens = 'SELECT lens FROM photos'
    cur.execute(sql_str_get_lens)
    lens_all_data = cur.fetchall()
    lens_buf = list()
    for i in range(len(lens_all_data)):
        if lens_all_data[i][0] in lens_buf:
            pass
        else:
            lens_buf.append(lens_all_data[i][0])

    lens_list = Metadata.equip_name_check(lens_buf, 'lens')

    return cameras_list, lens_list


# получить полный путь ко всем фото, у которых указаны выбранные камера и объектив
def get_equip_photo_list(camera_exif: str, camera: str, lens_exif: str, lens: str) -> list[str]:
    """
    Получить полный путь ко всем фото, у которых указаны выбранные камера и объектив.
    При наличии исправлений в ErrorNames, надо учесть, что какие-то записи могут быть сделаны вручную, а какие-то
    автоматически из метаданных.
    :param camera_exif: значение из автоматически созданных exif.
    :param camera: исправленное название камеры (либо повторение exif, если оно не исправляется).
    :param lens_exif: значение из автоматически созданных exif.
    :param lens: исправленное название объектива (либо повторение exif, если оно не исправляется).
    :return: список абсолютных путей ко всем файлам с выбранными камерой и объективом.
    """
    sql_str = f'SELECT filename, catalog FROM photos WHERE (camera = \'{camera}\' OR camera = \'{camera_exif}\') AND (lens = \'{lens}\' OR lens = \'{lens_exif}\')'
    cur.execute(sql_str)

    photodb_data = cur.fetchall()

    fullpaths = list()
    for photo in photodb_data:
        if 'Media/Photo/const' in photo[1]:
            fullpaths.append(photo[1]+'/'+photo[0])

    return fullpaths


# получить полный путь всех фото, у которых в выбранной соцсети указан выбранный статус
def get_sn_photo_list(network: str, status: str) -> list[str]:
    """
    Список абсолютных путей с выбранным статусом в выбранной соцсети.
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
        sql_str = f'SELECT filename, catalog FROM socialnetworks WHERE {network} = \'{status_bd}\''
        cur.execute(sql_str)
        photodb_data = cur.fetchall()
    except: # поймать ошибку с тем, что нет столбца network, так как у столбца начало 'numnumnum'
        sql_str = f'SELECT filename, catalog FROM socialnetworks WHERE numnumnum{network} = \'{status_bd}\''
        cur.execute(sql_str)
        photodb_data = cur.fetchall()

    if not photodb_data:
        try:
            int(network[1])
            sql_str = f'SELECT filename, catalog FROM socialnetworks WHERE numnumnum{network} = \'{status}\''
            cur.execute(sql_str)
            photodb_data = cur.fetchall()
        except:
            pass

    fullpaths = list()
    for photo in photodb_data:
        if 'Media/Photo/const' in photo[1]:
            fullpaths.append(photo[1]+'/'+photo[0])

    return fullpaths


# удалить все записи о файлах из удаляемой папки доп.каталога
def del_alone_dir(photo_directory: str) -> None:
    """
    Удалить все записи, в которых указан удаляемый каталог.
    :param photo_directory: название папки.
    :return: удаление записей.
    """
    photo_list = list()
    for file in os.listdir(photo_directory):
        if file.endswith(".jpg") or file.endswith(".JPG"):
            photo_list.append(file)

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
    except: # поймать ошибку с тем, что нет столбца network, так как у столбца начало 'numnumnum'
        sql_str = f'SELECT filename FROM socialnetworks WHERE numnumnum{network} = \'{status}\' AND catalog = \'{photo_directory}\''
        cur.execute(sql_str)
        photodb_data = cur.fetchall()

    photo_list = list()
    for photo in photodb_data:
        photo_list.append(photo[0])

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

    all = cur.fetchall()
    old_catalogs = list()
    for i in range(len(all)):
        old_catalogs.append(all[i][0])

    end_catalogs = list()
    for i in range(len(all)):
        end_catalogs.append(old_catalogs[i][len(old_way):])

    new_catalogs = list()
    for i in range(len(all)):
        new_catalogs.append(new_way + end_catalogs[i])

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


# при очистке метаданных - обнулить значения в 'No data' в БД
def clear_metadata(photo_name: str, photo_directory: str) -> None:
    """
    Очистка столбцов метаданных в БД (камера, объектив, дата съёмки, дата и время съёмки, GPS в таблице photos и
    дата съёмки в таблице socialnetworks).
    :param photo_name:
    :param photo_directory:
    :return: у файла с очищенными метаданными в БД заменить значения метаданных на No data.
    """
    sql_str1 = f"UPDATE photos SET camera = \'No data\' WHERE catalog = \'{photo_directory}\' and filename = \'{photo_name}\'"
    sql_str2 = f"UPDATE photos SET lens = \'No data\' WHERE catalog = \'{photo_directory}\' and filename = \'{photo_name}\'"
    sql_str3 = f"UPDATE photos SET shootingdate = \'No data\' WHERE catalog = \'{photo_directory}\' and filename = \'{photo_name}\'"
    sql_str4 = f"UPDATE photos SET shootingdatetime = \'No data\' WHERE catalog = \'{photo_directory}\' and filename = \'{photo_name}\'"
    sql_str5 = f"UPDATE photos SET GPSdata = \'No data\' WHERE catalog = \'{photo_directory}\' and filename = \'{photo_name}\'"
    sql_str6 = f"UPDATE socialnetworks SET shootingdate = \'No data\' WHERE catalog = \'{photo_directory}\' and filename = \'{photo_name}\'"

    cur.execute(sql_str1)
    cur.execute(sql_str2)
    cur.execute(sql_str3)
    cur.execute(sql_str4)
    cur.execute(sql_str5)
    cur.execute(sql_str6)

    conn.commit()


# достать из БД список фото сделанных в определённый день (используется только в GlobalMap)
def get_date_photo_list(year: str, month: str, day: str) -> list[str]:
    photodb_data = list()
    if year == 'No_Date_Info':
        date_to_search = 'No data'
        sql_str = f"SELECT filename, catalog FROM photos WHERE shootingdate = \'{date_to_search}\'"
        cur.execute(sql_str)
        date_info = cur.fetchall()
    else:
        if year != 'All' and month != 'All' and day == 'All':
            for i in range(1, 32):
                str_i = str(i)
                if len(str_i) == 1:
                    str_i = '0' + str_i
                date_to_search = f"{year}.{month}.{str_i}"
                sql_str = f"SELECT filename, catalog FROM photos WHERE shootingdate = \'{date_to_search}\'"
                cur.execute(sql_str)
                date_info = cur.fetchall()
                if date_info:
                    for photo_data in date_info:
                        photodb_data.append(photo_data)
        elif year != 'All' and month == 'All' and day == 'All':
            for j in range(1, 13):
                str_j = str(j)
                if len(str_j) == 1:
                    str_j = '0' + str_j
                for i in range(1, 32):
                    str_i = str(i)
                    if len(str_i) == 1:
                        str_i = '0' + str_i
                    date_to_search = f"{year}.{str_j}.{str_i}"
                    sql_str = f"SELECT filename, catalog FROM photos WHERE shootingdate = \'{date_to_search}\'"
                    cur.execute(sql_str)
                    date_info = cur.fetchall()
                    if date_info:
                        for photo_data in date_info:
                            photodb_data.append(photo_data)
        elif year == 'All' and month == 'All' and day == 'All':
            sql_str = f"SELECT filename, catalog FROM photos"
            cur.execute(sql_str)
            date_info = cur.fetchall()
            if date_info:
                for photo_data in date_info:
                    photodb_data.append(photo_data)
        else:
            date_to_search = f"{year}.{month}.{day}"
            sql_str = f"SELECT filename, catalog FROM photos WHERE shootingdate = \'{date_to_search}\'"
            cur.execute(sql_str)
            date_info = cur.fetchall()
            if date_info:
                for photo_data in date_info:
                    photodb_data.append(photo_data)

    fullpaths = list()
    for photo in photodb_data:
        if 'Media/Photo/const' in photo[1]:
            fullpaths.append(photo[1] + '/' + photo[0])

    return fullpaths


# достать GPS-координаты фотографий основного каталога из БД (используется только в GlobalMap)
def get_global_map_info(fullpaths: list[str]) -> list[str, tuple[float], str, str, str, bool]:
    names_and_coords = list()
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
        if gps_from_db == 'No data':
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

    return names_and_coords


# переименовать файлы в Б при смене имени
def file_rename(catalog: str, old_file_name: str, new_file_name: str) -> None:
    sql_str1 = f"UPDATE photos SET filename = \'{new_file_name}\' WHERE filename = \'{old_file_name}\' AND catalog = \'{catalog}\'"
    sql_str2 = f"UPDATE socialnetworks SET filename = \'{new_file_name}\' WHERE filename = \'{old_file_name}\' AND catalog = \'{catalog}\'"
    cur.execute(sql_str1)
    cur.execute(sql_str2)

    conn.commit()
