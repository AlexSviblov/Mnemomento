import datetime
import os
import Metadata
import sqlite3


conn = sqlite3.connect('PhotoDB.db', check_same_thread=False)
cur = conn.cursor()


# Добавление записи в БД при добавлении фото в основной каталог
def add_to_database(photoname: str, photodirectory: str) -> None:

    additiontime = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")

    own_dir = os.getcwd()

    # camera, lens, shootingdate, GPS = 'Canon EOS 200D', 'EF-S 10-18 mm', '2020.05.20 14:21:20', "No Data"
    camera, lens, shootingdatetime, GPS = Metadata.exif_for_db(photoname, photodirectory, own_dir)
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
def del_from_databese(photoname: str, photodirectory: str) -> None:

    sql_str = f'DELETE FROM photos WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
    cur.execute(sql_str)

    sql_str = f'DELETE FROM socialnetworks WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
    cur.execute(sql_str)

    conn.commit()


# Запись изменений, внёсённых пользователем при редактировании метаданных, которые есть в БД
def edit_in_database(photoname: str, photodirectory: str, editing_type: int, new_text: str) -> None:
    if editing_type == 1:       # камера
        sql_str = f'UPDATE photos SET camera = \'{new_text}\' WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
        cur.execute(sql_str)
        conn.commit()

    elif editing_type == 2:     # объектив
        sql_str = f'UPDATE photos SET lens = \'{new_text}\' WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
        cur.execute(sql_str)
        conn.commit()

    elif editing_type == 9:     # дата съёмки
        shootingdate = new_text[:4] + '.' + new_text[5:7] + '.' + new_text[8:10]
        shootingdatetime = new_text[:4] + '.' + new_text[5:7] + '.' + new_text[8:10] + new_text[10:]
        sql_str1 = f'UPDATE photos SET shootingdate = \'{shootingdate}\' WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
        sql_str2 = f'UPDATE photos SET shootingdatetime = \'{shootingdatetime}\' WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
        sql_str3 = f'UPDATE socialnetworks SET shootingdate = \'{shootingdate}\' WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''

        cur.execute(sql_str1)
        cur.execute(sql_str2)
        cur.execute(sql_str3)
        conn.commit()

    elif editing_type == 13:    # GPS
        sql_str = f'UPDATE photos SET GPSdata = \'{new_text}\' WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
        cur.execute(sql_str)
        conn.commit()

    else:       # другие данные (которых нет в БД)
        pass


# при переносе в другую папку надо переписать её путь в БД
def catalog_after_transfer(photoname: str, old_directory: str, new_directory: str) -> None:
    sql_str1 = f'UPDATE photos SET catalog =\'{old_directory}\' WHERE filename = \'{photoname}\' AND catalog = \'{new_directory}\''
    sql_str2 = f'UPDATE socialnetworks SET catalog =\'{old_directory}\' WHERE filename = \'{photoname}\' AND catalog = \'{new_directory}\''

    cur.execute(sql_str1)
    cur.execute(sql_str2)
    conn.commit()


# записать в БД новое имя при переименовании при переносе | new - откуда, old -куда, prew - прошлое имя, re - новое имя
def filename_after_transfer(prewname: str, rename: str, newcatalog: str, oldcatalog: str, code: int) -> None:
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

    else: # code == 1  переименовывается файл уже находящийся в папке назначения
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
def get_social_tags(photoname: str, photodirectory: str) -> tuple[list[str,...], dict]:
    sql_str_get_nets = 'PRAGMA table_info(socialnetworks)'
    cur.execute(sql_str_get_nets)
    all_column_names = cur.fetchall()
    sn_column_names = list()
    for i in range(3, len(all_column_names)):
        sn_column_names.append(all_column_names[i][1])

    sql_str_get_status = f'SELECT * FROM socialnetworks WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
    cur.execute(sql_str_get_status)

    # all_sn_data = cur.fetchall()[0]

    all_data = cur.fetchall()
    all_sn_data = all_data[0]

    sn_tags_values = dict()
    for i in range(3, len(all_sn_data)):
        sn_tags_values[f'{sn_column_names[i-3]}'] = all_sn_data[i]

    return sn_column_names, sn_tags_values


# редактирование тегов соцсетей
def edit_sn_tags(photoname: str, photodirectory: str, new_status: str, network: str) -> None:
    sql_str = f'UPDATE socialnetworks SET {network} = \'{new_status}\' WHERE filename = \'{photoname}\' AND catalog = \'{photodirectory}\''
    cur.execute(sql_str)

    conn.commit()


# список соцсетей в БД
def get_socialnetworks() -> list[str, ...]:
    sql_str_get_nets = 'PRAGMA table_info(socialnetworks)'
    cur.execute(sql_str_get_nets)
    all_column_names = cur.fetchall()
    sn_column_names = list()
    for i in range(3, len(all_column_names)):
        if all_column_names[i][1][:9] != 'numnumnum':
            sn_column_names.append(all_column_names[i][1])
        else:
            sn_column_names.append(all_column_names[i][1][9:])
    return sn_column_names


# список камер и объективов из БД
def get_equipment() -> tuple[list[str, ...], list[str, ...]]:
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
def get_equip_photo_list(camera_exif: str, camera: str, lens_exif: str, lens: str) -> list[str, ...]:
    sql_str = f'SELECT filename, catalog FROM photos WHERE (camera = \'{camera}\' OR camera = \'{camera_exif}\') AND (lens = \'{lens}\' OR lens = \'{lens_exif}\')'
    cur.execute(sql_str)

    photodb_data = cur.fetchall()

    fullpaths = list()
    for photo in photodb_data:
        if 'Media/Photo/const' in photo[1]:
            fullpaths.append(photo[1]+'/'+photo[0])

    return fullpaths


# получить полный путь всех фото, у которых в выбранной соцсети указан выбранный статус
def get_sn_photo_list(network: str, status: str) -> list[str, ...]:
    try:
        sql_str = f'SELECT filename, catalog FROM socialnetworks WHERE {network} = \'{status}\''
        cur.execute(sql_str)
        photodb_data = cur.fetchall()
    except: # поймать ошибку с тем, что нет столбца network, так как у столбца начало 'numnumnum'
        sql_str = f'SELECT filename, catalog FROM socialnetworks WHERE numnumnum{network} = \'{status}\''
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
def get_sn_alone_list(photo_directory: str, network: str, status: str) -> list[str, ...]:
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
def transfer_media_ways(old_way: str, new_way: str) -> tuple[list[str,...], list[str, ...]]:
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
def transfer_media(new_catalog: str, old_catalog: str):
    sql_str1 = f'UPDATE photos SET catalog = \'{new_catalog}\' WHERE catalog = \'{old_catalog}\''
    sql_str2 = f'UPDATE socialnetworks SET catalog = \'{new_catalog}\' WHERE catalog = \'{old_catalog}\''
    cur.execute(sql_str1)
    cur.execute(sql_str2)
    conn.commit()
