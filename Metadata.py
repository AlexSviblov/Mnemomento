import logging
import os

import PIL.Image
import exif  # type: ignore[import]
from PIL import Image  # type: ignore[import]
import sqlite3
from typing import Union, Tuple
from GPSPhoto import gpsphoto
from piexif import load, dump

import ErrorsAndWarnings

conn = sqlite3.connect('ErrorNames.db', check_same_thread=False)

cur = conn.cursor()


# считать весь exif из фотографии
def read_exif(photofile: str) -> dict[str, str]:
    """
    Функция чтения из файла всех метаданных, что может вычленить библиотека exif.
    :param photofile: абсолютный путь к файлу фотографии.
    :return: словарь всех вытащенных библиотекой exif метаданных.
    """
    with open(photofile, 'rb') as img:
        img = exif.Image(photofile)
        data = img.get_all()  # type: ignore[attr-defined]
    return data


# извлечь из фотографии дату съёмки
def date_from_exif(file: str) -> tuple[int, str, str, str]:
    """
    Для определения папки хранения файла в основном каталоге, необходимо при его добавлении в программу, достать
    дату съёмки из метаданных.
    :param file: абсолютный путь к файлу.
    :return: error = 1, если даты нет, и фото следует поместить в No_Date_Info, иначе - day, month, year - строки
    длинами 2, 2, 4 соответственно.
    """
    data = read_exif(file)

    try:  # если дата считывается
        date = data['datetime_original']
        day = date[8:10]
        month = date[5:7]
        year = date[0:4]
        error = 0
    except KeyError:  # если дата не считывается - No_Date_Info
        error = 1
        day = '0'
        month = '0'
        year = '0'
    return error, day, month, year


# из всех exif-данных вытаскиваются интересные для нас (камера, производитель, объектив, выдержка, ISO, диафрагма, фокусное расстояние, дата съёмки, координаты)
def filter_exif(data: dict, photofile: str, photo_directory: str) -> dict[str, str]:
    """
    Фильтрация всех метаданных, оставляет только те, что показываются при просмотре фотографии в таблице.
    :param data: словарь, содержащий все метаданные.
    :param photofile: имя файла.
    :param photo_directory: директория хранения файла.
    :return: словарь с 11 значениями (Разрешение, ориентация, производитель, камера, объектив, дата съёмки,
    фокусное расстояние, ISO, диафрагма, выдержка, координаты GPS.
    """
    metadata = dict()

    try:
        width = str(data['image_width'])
        height = str(data['image_height'])
        metadata['Разрешение'] = width + 'x' + height

    except KeyError:
        im = Image.open(photo_directory + '/' + photofile)
        width, height = im.size
        metadata['Разрешение'] = str(width) + 'x' + str(height)
        im.close()

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
            try:
                denominator = 1 / expo_time
                expo_time_fraction = f"1/{int(denominator)}"
            except ZeroDivisionError:
                expo_time_fraction = 0
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

            GPSLongitude_float = list(GPSLongitude)  # Приведение координат к десятичным числам, как на Я.Картах
            GPSLatitude_float = list(GPSLatitude)

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
def exif_for_db(photoname: str, photodirectory: str) -> tuple[str, str, str, str]:
    """
    Вынуть из фото метаданные для БД: камера, объектив, дата съёмки, дата-время съёмки, GPS.
    :param photoname: имя файла.
    :param photodirectory: директория для хранения фото.
    :return: камера, объектив, дата, GPS.
    """
    data = read_exif(photodirectory + '/' + photoname)

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

        GPSLongitude_float = list(GPSLongitude)  # Приведение координат к десятичным числам, как на Я.Картах
        GPSLatitude_float = list(GPSLatitude)

        GPSLongitude_value = GPSLongitude_float[0] + GPSLongitude_float[1] / 60 + GPSLongitude_float[2] / 3600  # type: ignore[operator]
        GPSLatitude_value = GPSLatitude_float[0] + GPSLatitude_float[1] / 60 + GPSLatitude_float[2] / 3600  # type: ignore[operator]

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
    """
    Вычленить из метаданных фотографии необходимые к показу в окне редактирования (производитель, камера, объектив,
    ISO, диафрагма, фокусное расстояние, выдержка, GPS, серийный номер объектива, серийный номер фотоаппарата,
    время съёмки, часовой пояс).
    :param photoname: абсолютный путь к файлу.
    :return: словарь с 11 значениями.
    """
    with open(photoname, 'rb') as img:
        img = exif.Image(photoname)
        all_data = img.get_all()  # type: ignore[attr-defined]

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
            try:
                denominator = 1 / all_data['exposure_time']
                expo_time_show = f"1/{int(denominator)}"
            except ZeroDivisionError:
                expo_time_show = '0'
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
    """
    Перезапись exif-метаданных в фотографии. Осуществляется полностью exif, кроме записи GPS в файл, где их до этого
    не было, для этого используется библиотека GPSPhoto.
    :param photoname: имя файла.
    :param photodirectory: директоряи хранения файла.
    :param editing_type: код изменяемого параметра (
    0 - производитель;
    1 - камера;
    2 - объектив;
    3 - выдержка;
    4 - ISO;
    5 - диафрагма;
    6 - фокусное расстояние;
    7 - GPS;
    8 - часовой пояс съёмки;
    9 - серийный номер фотоаппарата;
    10 - серийный номер объектива;
    11 - дата-время съёмки
    ).
    :param new_value: новое значение для параметра.
    :return: перезаписанные метаданные в файле (по факту создаётся НОВЫЙ ФАЙЛ с тем же именем).
    """
    photofile = photodirectory + '/' + photoname

    # перевод координат из формата вещественного числа в кортеж для записи в exif
    def exif_coord_to_tuple(coord: float) -> tuple[float, float, float]:
        deg = float(int(coord))
        mins_full = (coord - deg) * 60
        mins = float(int(mins_full))
        sec_full = (mins_full - mins) * 60
        sec = round(sec_full, 4)
        return (deg, mins, sec)

    original_metadata = get_original_metadata(photofile)

    modify_dict = dict()
    modify_dict_gps = dict()

    with open(photofile, 'rb') as img:
        img = exif.Image(photofile)

    if editing_type == 0:
        modify_dict = {'make': str(new_value)}
        try:
            original_metadata.pop('make')
        except KeyError:
            pass

    elif editing_type == 1:
        modify_dict = {'model': str(new_value)}
        try:
            original_metadata.pop('model')
        except KeyError:
            pass

    elif editing_type == 2:
        modify_dict = {'lens_model': str(new_value)}
        try:
            original_metadata.pop('lens_model')
        except KeyError:
            pass

    elif editing_type == 3:
        if '/' in new_value:
            float_value = 1 / float(new_value.split('/')[1])
            modify_dict = {'exposure_time': float_value}  # type: ignore[dict-item]
        else:
            float_value = float(new_value)
            modify_dict = {'exposure_time': str(float_value)}
        try:
            original_metadata.pop('exposure_time')
        except KeyError:
            pass

    elif editing_type == 4:
        modify_dict = {'photographic_sensitivity': int(new_value)}  # type: ignore[dict-item]
        try:
            original_metadata.pop('photographic_sensitivity')
        except KeyError:
            pass

    elif editing_type == 5:
        modify_dict = {'f_number': float(new_value)}  # type: ignore[dict-item]
        try:
            original_metadata.pop('f_number')
        except KeyError:
            pass

    elif editing_type == 6:
        modify_dict = {'focal_length': int(new_value)}  # type: ignore[dict-item]
        try:
            original_metadata.pop('focal_length')
        except KeyError:
            pass

    elif editing_type == 11:
        modify_dict = {'datetime_original': str(new_value)}
        try:
            original_metadata.pop('datetime_original')
        except KeyError:
            pass

    elif editing_type == 8:
        modify_dict = {'offset_time': str(new_value)}
        try:
            original_metadata.pop('offset_time')
        except KeyError:
            pass

    elif editing_type == 9:
        modify_dict = {'body_serial_number': str(new_value)}
        try:
            original_metadata.pop('body_serial_number')
        except KeyError:
            pass

    elif editing_type == 10:
        modify_dict = {'lens_serial_number': str(new_value)}
        try:
            original_metadata.pop('lens_serial_number')
        except KeyError:
            pass

    elif editing_type == 7:
        new_value_splitted = new_value.split(', ')
        float_value_lat = float(new_value_splitted[0])
        float_value_long = float(new_value_splitted[1])

        lat_list = exif_coord_to_tuple(float_value_lat)
        long_list = exif_coord_to_tuple(float_value_long)
        if float_value_lat > 0:
            lat_ref = 'N'
        else:
            lat_ref = 'S'

        if float_value_long > 0:
            lon_ref = 'E'
        else:
            lon_ref = 'W'

        modify_dict_gps = [float_value_lat, lat_ref, float_value_long, lon_ref]
        try:
            original_metadata.pop('gps_latitude_ref')
        except KeyError:
            pass
        try:
            original_metadata.pop('gps_latitude')
        except KeyError:
            pass
        try:
            original_metadata.pop('gps_longitude_ref')
        except KeyError:
            pass
        try:
            original_metadata.pop('gps_longitude')
        except KeyError:
            pass

    # Сделать сам модифай
    if modify_dict:
        img.set(list(modify_dict.keys())[0],
                modify_dict[f"{list(modify_dict.keys())[0]}"])  # type: ignore[attr-defined]

        for i in range(len(original_metadata)):
            img.set(list(original_metadata.keys())[i], original_metadata[f"{list(original_metadata.keys())[i]}"])

        with open(f"{photofile}_temp", 'wb') as new_file:
            new_file.write(img.get_file())  # type: ignore[attr-defined]
        os.remove(photofile)
        os.rename(f"{photofile}_temp", photofile)

    if modify_dict_gps:

        try:
            info = gpsphoto.GPSInfo((float_value_lat, float_value_long))
            photo = gpsphoto.GPSPhoto(photofile)
            photo.modGPSData(info, f'{photofile}_temp')
        except Exception:
            img.set('gps_latitude_ref', lat_ref)
            img.set('gps_latitude', lat_list)
            img.set('gps_longitude_ref', lon_ref)
            img.set('gps_longitude', long_list)

            for i in range(len(original_metadata)):
                img.set(list(original_metadata.keys())[i], original_metadata[f"{list(original_metadata.keys())[i]}"])

            with open(f"{photofile}_temp", 'wb') as new_file:
                new_file.write(img.get_file())  # type: ignore[attr-defined]

        os.remove(photofile)
        os.rename(f"{photofile}_temp", photofile)


# проверка ввода при редактировании exif
def exif_check_edit(editing_type: int, new_value: str) -> None:
    """
    Проверка корректности ввода новых метаданных.
    :param editing_type: изменяемый тип (0-11).
    :param new_value: новое значение.
    :return: если всё верно - pass и перезапись метаданных, если есть ошибка - окно предупреждения и запрет на перезапись.
    """

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

            if new_value[4] == ':' and new_value[7] == ':' and new_value[13] == ':' and new_value[16] == ':' and \
                    new_value[10] == ' ':
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
    """
    Для корректного отображения выпадающих списком камер и объективов в основном каталоге при группировке по
    оборудованию - данные достаются из БД фотографий, сравниваются с данными БД исправлений и очищаются от повторений.
    :param equip_list: список строк с названием оборудования.
    :param type: тип оборудования.
    :return: список уникальных исправленных названий оборудования.
    """
    for i in range(len(equip_list)):
        sql_str = f'SELECT normname FROM ernames WHERE type = \'{type}\' AND exifname = \'{equip_list[i]}\''
        cur.execute(sql_str)
        try:
            right_equip = cur.fetchone()[0]
            equip_list[i] = right_equip
        except TypeError:
            pass
        equip_set = set(equip_list)
        equip_list_final = list(equip_set)
    return equip_list_final


# проверка, является ли переданное имя - исправлением неправильного
def equip_name_check_reverse(normname: str, type: str) -> str:
    """
    Для поиска в БД необходимо искать не только отображаемое значение и неправильное, которое могло быть
    исправлено.
    :param normname: корректное исправленное имя.
    :param type: тип устройства.
    :return: как оборудование автоматически пишется в exif.
    """
    sql_str = f'SELECT exifname FROM ernames WHERE type = \'{type}\' AND normname = \'{normname}\''
    cur.execute(sql_str)
    try:
        exifname = cur.fetchone()[0]
    except TypeError:
        exifname = normname

    return exifname


# удалить все метаданные
def clear_exif(photoname: str, photodirectory: str) -> None:
    """
    Удалить все метаданные из файла.
    :param photoname:  имя файла.
    :param photodirectory: директори хранения.
    :return: в отличие от перезаписи или добавления метаданных, не требуется осздание нового файла.
    """
    photofile = photodirectory + '/' + photoname
    with open(photofile, 'rb') as img:
        img = exif.Image(photofile)
        img.delete_all()  # type: ignore[attr-defined]

    with open(f"{photofile}_temp", 'wb') as new_file:
        new_file.write(img.get_file())  # type: ignore[attr-defined]
    os.remove(photofile)
    os.rename(f"{photofile}_temp", photofile)


def check_photo_rotation(photo_file):
    data = read_exif(photo_file)
    try:
        width = str(data['image_width'])
        height = str(data['image_height'])
    except KeyError:
        meta_orientation = data['orientation']
        im = Image.open(photo_file)
        exif_dict = load(im.info["exif"])
        exif_bytes = dump(exif_dict)
        match meta_orientation:
            case 1:
                im_flipped = im
                width = data['pixel_x_dimension']
                height = data['pixel_y_dimension']
            case 2:
                im_flipped = im.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
                width = data['pixel_x_dimension']
                height = data['pixel_y_dimension']
            case 3:
                im_flipped = im.transpose(method=Image.Transpose.ROTATE_180)
                width = data['pixel_x_dimension']
                height = data['pixel_y_dimension']
            case 4:
                im_flipped = im.transpose(method=Image.Transpose.FLIP_TOP_BOTTOM)
                width = data['pixel_x_dimension']
                height = data['pixel_y_dimension']
            case 5:
                im_flipped_temp = im.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
                # im_flipped = im_flipped_temp.transpose(method=Image.Transpose.ROTATE_270)
                im_flipped = im.transpose(method=Image.Transpose.ROTATE_90)
                width = data['pixel_y_dimension']
                height = data['pixel_x_dimension']
            case 6:
                # im_flipped = im.transpose(method=Image.Transpose.ROTATE_90)
                im_flipped = im.transpose(method=Image.Transpose.ROTATE_270)
                width = data['pixel_y_dimension']
                height = data['pixel_x_dimension']
            case 7:
                im_flipped_temp = im.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
                # im_flipped = im_flipped_temp.transpose(method=Image.Transpose.ROTATE_90)
                im_flipped = im.transpose(method=Image.Transpose.ROTATE_270)
                width = data['pixel_y_dimension']
                height = data['pixel_x_dimension']
            case 8:
                # im_flipped = im.transpose(method=Image.Transpose.ROTATE_270)
                im_flipped = im.transpose(method=Image.Transpose.ROTATE_90)
                width = data['pixel_y_dimension']
                height = data['pixel_x_dimension']
            case _:
                im_flipped = im
                width = data['pixel_x_dimension']
                height = data['pixel_y_dimension']

        im_flipped.save(photo_file + '_temp', 'jpeg', exif=exif_bytes, quality=95, subsampling=0)
        os.remove(photo_file)
        os.rename(photo_file + '_temp', photo_file)
        im.close()
        im_flipped.close()
        write_normal_photo_size(photo_file, width, height)


def write_normal_photo_size(photo_file, width, height):
    with open(photo_file, 'rb') as img:
        img = exif.Image(photo_file)

    img.set('image_width', width)
    img.set('image_height', height)
    img.set('orientation', exif._constants.Orientation.TOP_LEFT)

    original_metadata = get_original_metadata(photo_file)

    for i in range(len(original_metadata)):
        img.set(list(original_metadata.keys())[i], original_metadata[f"{list(original_metadata.keys())[i]}"])

    with open(f"{photo_file}_temp", 'wb') as new_file:
        new_file.write(img.get_file())
    os.remove(photo_file)
    os.rename(f"{photo_file}_temp", photo_file)


def get_original_metadata(photo_file):
    all_data = read_exif(photo_file)
        
    original_metadata = {}
    
    try:
        original_metadata['make'] = all_data['make']
    except KeyError:
        pass

    try:
        original_metadata['model'] = all_data['model']
    except KeyError:
        pass

    try:
        original_metadata['lens_model'] = all_data['lens_model']
    except KeyError:
        pass

    try:
        original_metadata['exposure_time'] = all_data['exposure_time']
    except KeyError:
        pass

    try:
        original_metadata['photographic_sensitivity'] = all_data['photographic_sensitivity']
    except KeyError:
        pass

    try:
        original_metadata['f_number'] = all_data['f_number']
    except KeyError:
        pass

    try:
        original_metadata['focal_length'] = all_data['focal_length']
    except KeyError:
        pass

    try:
        original_metadata['datetime_original'] = all_data['datetime_original']
    except KeyError:
        pass

    try:
        original_metadata['offset_time'] = all_data['offset_time']
    except KeyError:
        pass

    try:
        original_metadata['body_serial_number'] = all_data['body_serial_number']
    except KeyError:
        pass

    try:
        original_metadata['lens_serial_number'] = all_data['lens_serial_number']
    except KeyError:
        pass

    try:
        original_metadata['gps_latitude_ref'] = all_data['gps_latitude_ref']
    except KeyError:
        pass

    try:
        original_metadata['gps_latitude'] = all_data['gps_latitude']
    except KeyError:
        pass

    try:
        original_metadata['gps_longitude_ref'] = all_data['gps_longitude_ref']
    except KeyError:
        pass

    try:
        original_metadata['gps_longitude'] = all_data['gps_longitude']
    except KeyError:
        pass
    
    return original_metadata


def onlyshow_rotation(photo_file):
    data = read_exif(photo_file)
    im = Image.open(photo_file)
    try:
        width = str(data['image_width'])
        height = str(data['image_height'])
    except KeyError:
        meta_orientation = data['orientation']
        match meta_orientation:
            case 1:
                im_flipped = im
                orientation = 1
            case 2:
                im_flipped = im.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
                orientation = 1
            case 3:
                im_flipped = im.transpose(method=Image.Transpose.ROTATE_180)
                orientation = 1
            case 4:
                im_flipped = im.transpose(method=Image.Transpose.FLIP_TOP_BOTTOM)
                orientation = 1
            case 5:
                im_flipped_temp = im.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
                # im_flipped = im_flipped_temp.transpose(method=Image.Transpose.ROTATE_270)
                im_flipped = im.transpose(method=Image.Transpose.ROTATE_90)
                orientation = 0
            case 6:
                # im_flipped = im.transpose(method=Image.Transpose.ROTATE_90)
                im_flipped = im.transpose(method=Image.Transpose.ROTATE_270)
                orientation = 0
            case 7:
                im_flipped_temp = im.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
                # im_flipped = im_flipped_temp.transpose(method=Image.Transpose.ROTATE_90)
                im_flipped = im.transpose(method=Image.Transpose.ROTATE_270)
                orientation = 0
            case 8:
                # im_flipped = im.transpose(method=Image.Transpose.ROTATE_270)
                im_flipped = im.transpose(method=Image.Transpose.ROTATE_90)
                orientation = 0
            case _:
                im_flipped = im
                orientation = 1

        im_flipped.save(photo_file + '_temp', 'jpeg', quality=95, subsampling=0)
        photo_show = photo_file + '_temp'
    else:
        photo_show = photo_file
        orientation = 1

    return photo_show, orientation


def onlyshow_thumbnail_orientation(photo_file, thumbnail_file):
    data = read_exif(photo_file)
    thum = Image.open(thumbnail_file)
    try:
        width = str(data['image_width'])
        height = str(data['image_height'])
    except KeyError:
        meta_orientation = data['orientation']
        match meta_orientation:
            case 1:
                thum_flipped = thum
            case 2:
                thum_flipped = thum.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
            case 3:
                thum_flipped = thum.transpose(method=Image.Transpose.ROTATE_180)
            case 4:
                thum_flipped = thum.transpose(method=Image.Transpose.FLIP_TOP_BOTTOM)
            case 5:
                thum_flipped_temp = thum.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
                # thum_flipped = thum_flipped_temp.transpose(method=Image.Transpose.ROTATE_270)
                thum_flipped = thum.transpose(method=Image.Transpose.ROTATE_90)
            case 6:
                # thum_flipped = thum.transpose(method=Image.Transpose.ROTATE_90)
                thum_flipped = thum.transpose(method=Image.Transpose.ROTATE_270)
            case 7:
                thum_flipped_temp = thum.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
                # thum_flipped = thum_flipped_temp.transpose(method=Image.Transpose.ROTATE_90)
                thum_flipped = thum.transpose(method=Image.Transpose.ROTATE_270)
            case 8:
                # thum_flipped = thum.transpose(method=Image.Transpose.ROTATE_270)
                thum_flipped = thum.transpose(method=Image.Transpose.ROTATE_90)
            case _:
                thum_flipped = thum

        thum_flipped.save(thumbnail_file + '_temp', 'jpeg', quality=95, subsampling=0)
        os.remove(thumbnail_file)
        os.rename(thumbnail_file + '_temp', thumbnail_file)
    else:
        pass
