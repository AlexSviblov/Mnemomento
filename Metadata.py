import logging
import os
import exif
from PIL import Image
import sqlite3
from typing import Union
from GPSPhoto import gpsphoto

import ErrorsAndWarnings

conn = sqlite3.connect('ErrorNames.db')


cur = conn.cursor()


# считать весь exif из фотографии
def read_exif(photofile: str) -> dict:  # функция чтения всех метаданных из файла
    with open(photofile, 'rb') as img:
        img = exif.Image(photofile)
        data = img.get_all()

    return data


# извлечь из фотографии дату съёмки
def date_from_exif(file: str) -> tuple[Union[int, str]]:
    data = read_exif(file)
    try:    # если дата считывается
        date = data['datetime_original']
        day = date[8:10]
        month = date[5:7]
        year = date[0:4]
        error = 0
    except KeyError: # если дата не считывается - No_Date_Info
        error = 1
        day = 0
        month = 0
        year = 0
    return error, day, month, year


# из всех exif-данных вытаскиваются интересные для нас (камера, производитель, объектив, выдержка, ISO, диафрагма, фокусное расстояние, дата съёмки, координаты)
def filter_exif(data: dict, photofile: str, photo_directory: str) -> dict[str, str]:

    metadata = dict()

    try:
        width = str(data['image_width'])
        height = str(data['image_height'])
        metadata['Разрешение'] = width + 'x' + height
    except KeyError:
        im = Image.open(photo_directory +'/'+ photofile)
        width, height = im.size
        metadata['Разрешение'] = str(width) + 'x' + str(height)

    if width > height:  # Eсли ширина фотографии больше -> она горизонтальная, иначе - вертикальная. Нужно для размещения элементов GUI на экране
        metadata['Rotation'] = 'gor'
    else:
        metadata['Rotation'] = 'ver'

    try:
        date = data['datetime_original']  # делаем дату русской, а не пиндосской
        date_show = date[11:] + ' ' + date[8:10] + '.' + date[5:7] + '.' + date[0:4]
        metadata['Дата съёмки'] = date_show
    except KeyError:
        metadata['Дата съёмки'] = ''

    try:
        maker = data['make']
        sql_str = f'SELECT normname FROM ernames WHERE type = \'maker\' AND exifname = \'{maker}\''
        cur.execute(sql_str)
        try:
            maker = cur.fetchone()[0]
        except TypeError:
            pass

        metadata['Производитель'] = maker
    except KeyError:
        metadata['Производитель'] = ''

    try:
        camera = data['model']

        sql_str = f'SELECT normname FROM ernames WHERE type = \'camera\' AND exifname = \'{camera}\''
        cur.execute(sql_str)
        try:
            camera = cur.fetchone()[0]
        except TypeError:
            pass

        metadata['Камера'] = camera
    except KeyError:
        metadata['Камера'] = ''

    try:
        lens = data['lens_model']

        sql_str = f'SELECT normname FROM ernames WHERE type = \'lens\' AND exifname = \'{lens}\''
        cur.execute(sql_str)
        try:
            lens = cur.fetchone()[0]
        except TypeError:
            pass

        metadata['Объектив'] = lens
    except KeyError:
        metadata['Объектив'] = ''

    try:
        FocalLength_float = data['focal_length']
        metadata['Фокусное расстояние'] = str(int(FocalLength_float))
    except KeyError:
        metadata['Фокусное расстояние'] = ''

    try:
        FNumber_float = data['f_number']
        metadata['Диафрагма'] = str(FNumber_float)
    except KeyError:
        metadata['Диафрагма'] = ''

    try:
        expo_time = data['exposure_time']
        if expo_time >= 0.1:
            expo_time_str = str(expo_time)
            metadata['Выдержка'] = expo_time_str
        else:
            denominator = 1/expo_time
            expo_time_fraction = f"1/{int(denominator)}"
            metadata['Выдержка'] = expo_time_fraction
    except KeyError:
        metadata['Выдержка'] = ''

    try:
        iso = data['photographic_sensitivity']
        metadata['ISO'] = str(iso)
    except KeyError:
        metadata['ISO'] = ''

    try:
        GPSLatitudeRef = data['gps_latitude_ref']  # Считывание GPS из метаданных
        GPSLatitude = data['gps_latitude']
        GPSLongitudeRef = data['gps_longitude_ref']
        GPSLongitude = data['gps_longitude']

        if GPSLongitudeRef and GPSLatitudeRef and GPSLongitude and GPSLatitude:

            GPSLatitude_splitted = list(GPSLatitude)  # Приведение координат к десятичным числам, как на Я.Картах
            GPSLongitude_splitted = list(GPSLongitude)

            GPSLongitude_float = list()
            GPSLatitude_float = list()

            for i in range(0, 3):
                GPSLongitude_float.append(GPSLongitude_splitted[i])
                GPSLatitude_float.append((GPSLatitude_splitted[i]))

            GPSLongitude_value = GPSLongitude_float[0] + GPSLongitude_float[1] / 60 + GPSLongitude_float[2] / 3600
            GPSLatitude_value = GPSLatitude_float[0] + GPSLatitude_float[1] / 60 + GPSLatitude_float[2] / 3600

            GPSLongitude_value = round(GPSLongitude_value, 6)
            GPSLatitude_value = round(GPSLatitude_value, 6)

            if GPSLongitudeRef == 'E':
                pass
            else:
                GPSLongitude_value = GPSLongitude_value * (-1)

            if GPSLatitudeRef == 'N':
                pass
            else:
                GPSLatitude_value = GPSLatitude_value * (-1)

            metadata['GPS'] = str(GPSLatitude_value) + ', ' + str(GPSLongitude_value)
        else:
            metadata['GPS'] = ''
    except KeyError:
        metadata['GPS'] = ''

    return metadata


# данные для вноса в БД photos
def exif_for_db(photoname: str, photodirectory: str) -> tuple[str]:
    data = read_exif(photodirectory + photoname)

    try:
        camera = data['model']
    except KeyError:
        camera = "No data"

    try:
        lens = data['lens_model']
    except KeyError:
        lens = "No data"

    try:
        date = data['datetime_original']  # делаем дату русской, а не пиндосской
        date = date[0:4] + '.' + date[5:7] + '.' + date[8:10] + ' ' + date[11:]
    except KeyError:
        date = "No data"

    try:
        GPSLatitudeRef = data['gps_latitude_ref']  # Считывание GPS из метаданных
        GPSLatitude = data['gps_latitude']
        GPSLongitudeRef = data['gps_longitude_ref']
        GPSLongitude = data['gps_longitude']

        GPSLatitude_splitted = list(GPSLatitude)  # Приведение координат к десятичным числам, как на Я.Картах
        GPSLongitude_splitted = list(GPSLongitude)

        GPSLongitude_float = list()
        GPSLatitude_float = list()

        for i in range(0, 3):
            GPSLongitude_float.append(GPSLongitude_splitted[i])
            GPSLatitude_float.append((GPSLatitude_splitted[i]))

        GPSLongitude_value = GPSLongitude_float[0] + GPSLongitude_float[1] / 60 + GPSLongitude_float[2] / 3600
        GPSLatitude_value = GPSLatitude_float[0] + GPSLongitude_float[1] / 60 + GPSLongitude_float[2] / 3600

        if GPSLongitudeRef == 'E':
            pass
        else:
            GPSLongitude_value = GPSLongitude_value * (-1)

        if GPSLatitudeRef == 'N':
            pass
        else:
            GPSLatitude_value = GPSLatitude_value * (-1)
        GPS = str(GPSLatitude_value) + ', ' + str(GPSLongitude_value)
    except KeyError:
        GPS = "No data"

    return camera, lens, date, GPS


# exif для показа в режиме редактирования
def exif_show_edit(photoname: str) -> dict[str, str]:
    with open(photoname, 'rb') as img:
        img = exif.Image(photoname)
        all_data = img.get_all()

    useful_data = dict()

    try:
        maker = all_data['make']
        sql_str = f'SELECT normname FROM ernames WHERE type = \'maker\' AND exifname = \'{maker}\''
        cur.execute(sql_str)
        try:
            maker = cur.fetchone()[0]
        except TypeError:
            pass
        useful_data['Производитель'] = maker
    except KeyError:
        useful_data['Производитель'] = ''

    try:
        camera = all_data['model']
        sql_str = f'SELECT normname FROM ernames WHERE type = \'camera\' AND exifname = \'{camera}\''
        cur.execute(sql_str)
        try:
            camera = cur.fetchone()[0]
        except TypeError:
            pass
        useful_data['Камера'] = camera
    except KeyError:
        useful_data['Камера'] = ''

    try:
        lens = all_data['lens_model']

        sql_str = f'SELECT normname FROM ernames WHERE type = \'lens\' AND exifname = \'{lens}\''
        cur.execute(sql_str)
        try:
            lens = cur.fetchone()[0]
        except TypeError:
            pass
        useful_data['Объектив'] = lens
    except KeyError:
        useful_data['Объектив'] = ''

    try:
        if all_data['exposure_time'] < 0.1:
            denominator = 1/all_data['exposure_time']
            expo_time_show = f"1/{int(denominator)}"
            useful_data['Выдержка'] = expo_time_show
        else:
            useful_data['Выдержка'] = str(all_data['exposure_time'])
    except KeyError:
        useful_data['Выдержка'] = ''

    try:
        useful_data['ISO'] = all_data['photographic_sensitivity']
    except KeyError:
        useful_data['ISO'] = ''

    try:
        useful_data['Диафрагма'] = str(all_data['f_number'])
    except KeyError:
        useful_data['Диафрагма'] = ''

    try:
        useful_data['Фокусное расстояние'] = str(int(all_data['focal_length']))
    except KeyError:
        useful_data['Фокусное расстояние'] = ''

    try:
        useful_data['Время съёмки'] = all_data['datetime_original']
    except KeyError:
        useful_data['Время съёмки'] = ''

    try:
        useful_data['Часовой пояс'] = all_data['offset_time']
    except KeyError:
        useful_data['Часовой пояс'] = ''

    try:
        useful_data['Серийный номер камеры'] = all_data['body_serial_number']
    except KeyError:
        useful_data['Серийный номер камеры'] = ''

    try:
        useful_data['Серийный номер объектива'] = all_data['lens_serial_number']
    except KeyError:
        useful_data['Серийный номер объектива'] = ''

    try:
        GPSLatitudeRef = all_data['gps_latitude_ref']  # Считывание GPS из метаданных
        GPSLatitude = all_data['gps_latitude']
        GPSLongitudeRef = all_data['gps_longitude_ref']
        GPSLongitude = all_data['gps_longitude']

        GPSLatitude_splitted = list(GPSLatitude)  # Приведение координат к десятичным числам, как на Я.Картах
        GPSLongitude_splitted = list(GPSLongitude)

        GPSLongitude_float = list()
        GPSLatitude_float = list()

        for i in range(0, len(GPSLongitude_splitted)):
            GPSLongitude_float.append(GPSLongitude_splitted[i])

        for i in range(0, len(GPSLatitude_splitted)):
            GPSLatitude_float.append((GPSLatitude_splitted[i]))

        if len(GPSLongitude_float) == 3:
            GPSLongitude_value = GPSLongitude_float[0] + GPSLongitude_float[1] / 60 + GPSLongitude_float[2] / 3600
        elif len(GPSLongitude_float) == 1:
            GPSLongitude_value = GPSLongitude_float[0]
        else:
            GPSLongitude_value = 0.0

        if len(GPSLatitude_float) == 3:
            GPSLatitude_value = GPSLatitude_float[0] + GPSLatitude_float[1] / 60 + GPSLatitude_float[2] / 3600
        elif len(GPSLatitude_float) == 1:
            GPSLatitude_value = GPSLatitude_float[0]
        else:
            GPSLatitude_value = 0.0

        GPSLongitude_value = round(GPSLongitude_value, 6)
        GPSLatitude_value = round(GPSLatitude_value, 6)

        if GPSLongitudeRef == 'E':
            pass
        else:
            GPSLongitude_value = GPSLongitude_value * (-1)

        if GPSLatitudeRef == 'N':
            pass
        else:
            GPSLatitude_value = GPSLatitude_value * (-1)

        useful_data['Координаты'] = str(GPSLatitude_value) + ', ' + str(GPSLongitude_value)

    except KeyError:
        useful_data['Координаты'] = ''

    return useful_data


# modify при редактировании метаданных, без проверки, так как проверка предварительно осуществляется в exif_check_edit
def exif_rewrite_edit(photoname: str, photodirectory: str, editing_type: int, new_value: str) -> None:
    photofile = photodirectory + '/' + photoname

    modify_dict = dict()
    modify_dict1 = dict()
    modify_dict2 = dict()
    modify_dict3 = dict()
    modify_dict4 = dict()

    with open(photofile, 'rb') as img:
        img = exif.Image(photofile)

    if editing_type == 0:
        modify_dict = {'make': str(new_value)}

    elif editing_type == 1:
        modify_dict = {'model': str(new_value)}

    elif editing_type == 2:
        modify_dict = {'lens_model': str(new_value)}

    elif editing_type == 3:
        if '/' in new_value:
            float_value = 1/float(new_value.split('/')[1])
            modify_dict = {'exposure_time': float_value}
        else:
            float_value = float(new_value)
            modify_dict = {'exposure_time': str(float_value)}

    elif editing_type == 4:
        modify_dict = {'photographic_sensitivity': int(new_value)}

    elif editing_type == 5:
        modify_dict = {'f_number': float(new_value)}

    elif editing_type == 6:
        modify_dict = {'focal_length': int(new_value)}

    elif editing_type == 11:
        modify_dict = {'datetime_original': str(new_value)}

    elif editing_type == 8:
        modify_dict = {'offset_time': str(new_value)}

    elif editing_type == 9:
        modify_dict = {'body_serial_number': str(new_value)}

    elif editing_type == 10:
        modify_dict = {'lens_serial_number': str(new_value)}

    elif editing_type == 7:
        new_value_splitted = new_value.split(', ')
        float_value_lat = float(new_value_splitted[0])
        float_value_long = float(new_value_splitted[1])

        if float_value_lat < 0:
            GPSLatitudeRef = 'S'
        else:
            GPSLatitudeRef = 'N'

        if float_value_long < 0:
            GPSLongitudeRef = 'W'
        else:
            GPSLongitudeRef = 'E'

        abs_value_lat = abs(float_value_lat)
        grad_lat = int(abs_value_lat)
        minut_lat = int((abs_value_lat - grad_lat) * 60)
        secund_float_lat = round(((abs_value_lat - grad_lat) * 60 - int((abs_value_lat - grad_lat) * 60)) * 60, 6)

        GPSLatitude = tuple([float(grad_lat), float(minut_lat), float(secund_float_lat)])


        abs_value_long = abs(float_value_long)
        grad_long = int(abs_value_long)
        minut_long = int((abs_value_long - grad_long) * 60)
        secund_float_long = round(((abs_value_long - grad_long) * 60 - int((abs_value_long - grad_long) * 60)) * 60, 6)

        GPSLongitude = tuple([float(grad_long), float(minut_long), float(secund_float_long)])

        modify_dict1 = {'gps_latitude_ref': GPSLatitudeRef}
        modify_dict2 = {'gps_latitude': GPSLatitude}
        modify_dict3 = {'gps_longitude_ref': GPSLongitudeRef}
        modify_dict4 = {'gps_longitude': GPSLongitude}
        info = gpsphoto.GPSInfo((float_value_lat, float_value_long))

    # Сделать сам модифай
    if modify_dict:
        img.set(list(modify_dict.keys())[0], modify_dict[f"{list(modify_dict.keys())[0]}"])

    with open(f"{photofile}_buffername", 'wb') as new_file:
        new_file.write(img.get_file())
    os.remove(photofile)
    os.rename(f"{photofile}_buffername", photofile)

    if modify_dict1:
        # img.set(list(modify_dict1.keys())[0], modify_dict1[f"{list(modify_dict1.keys())[0]}"])
        # img.set(list(modify_dict2.keys())[0], modify_dict2[f"{list(modify_dict2.keys())[0]}"])
        # img.set(list(modify_dict3.keys())[0], modify_dict3[f"{list(modify_dict3.keys())[0]}"])
        # img.set(list(modify_dict4.keys())[0], modify_dict4[f"{list(modify_dict4.keys())[0]}"])
        photo = gpsphoto.GPSPhoto(photofile)
        photo.modGPSData(info, photofile)


# проверка ввода при редактировании exif
def exif_check_edit(editing_type: int, new_value: str) -> None:

    # Ошибка ввода вызывает ошибку для except в объекте окна, который уже там делает return
    def make_error():
        raise ErrorsAndWarnings.EditExifError()

    # выдержка
    if editing_type == 3:
        if '/' in new_value:
            try:
                if int(new_value.split('/')[0]) < 0 or int(new_value.split('/')[1]) < 0:
                    make_error()
            except Exception:
                make_error()
        else:
            try:
                float(new_value)
            except ValueError:
                make_error()

    # ISO
    elif editing_type == 4:
        try:
            int(new_value)
            if int(new_value) < 0:
                make_error()
        except ValueError:
            make_error()

    # диафрагма
    elif editing_type == 5:
        try:
            float_value = float(new_value)
            if float_value < 0:
                make_error()
        except ValueError:
            make_error()

    # фокусное расстояние
    elif editing_type == 6:
        try:
            if int(new_value) < 0:
                make_error()
        except ValueError:
            make_error()

    # дата съёмки
    elif editing_type == 11:
        try:
            int(new_value[0:4])

            if 1 <= int(new_value[5:7]) <= 12:
                pass
            else:
                make_error()

            if 1 <= int(new_value[8:10]) <= 31:
                pass
            else:
                make_error()

            if 0 <= int(new_value[11:13]) <= 24:
                pass
            else:
                make_error()

            if 0 <= int(new_value[14:16]) <= 60:
                pass
            else:
                make_error()

            if 0 <= int(new_value[17:19]) <= 60:
                pass
            else:
                make_error()

            if new_value[4] == ':' and new_value[7] == ':' and new_value[13] == ':' and new_value[16] == ':' and new_value[10] == ' ':
                pass
            else:
                make_error()

        except ValueError:
            make_error()

    # часовой пояс
    elif editing_type == 8:
        try:
            int(new_value[1])
            int(new_value[2])
            if new_value[0] == '+' or new_value[0] == '-':
                pass
            else:
                make_error()
            if new_value[3] == ':' and new_value[4] == '0' and new_value[5] == '0':
                pass
            else:
                make_error()
        except (ValueError, IndexError):
            make_error()

    # GPS
    elif editing_type == 7:
        new_value_splitted = new_value.split(', ')

        try:
            float(new_value_splitted[0])
            float(new_value_splitted[1])
        except (ValueError, IndexError):
            make_error()


# Замена неправильного названия для выбора группировки на правильное
def equip_name_check(equip_list: list[str], type: str) -> list[str]:
    for i in range(len(equip_list)):
        sql_str = f'SELECT normname FROM ernames WHERE type = \'{type}\' AND exifname = \'{equip_list[i]}\''
        cur.execute(sql_str)
        try:
            right_equip = cur.fetchone()[0]
            equip_list[i] = right_equip
        except TypeError:
            pass

    return equip_list


# проверка, является ли переданное имя - исправлением неправильного
def equip_name_check_reverse(normname: str, type: str) -> str:

    sql_str = f'SELECT exifname FROM ernames WHERE type = \'{type}\' AND normname = \'{normname}\''
    cur.execute(sql_str)
    try:
        exifname = cur.fetchone()[0]
    except TypeError:
        exifname = normname

    return exifname


def clear_exif(photoname: str, photodirectory: str):
    photofile = photodirectory + '/' + photoname
    with open(photofile, 'wb') as img:
        img = exif.Image(photofile)
        img.delete_all()

