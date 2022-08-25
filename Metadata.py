import os
import pyexiv2
from PIL import Image
import sqlite3


conn = sqlite3.connect('ErrorNames.db')
cur = conn.cursor()


# считать весь exif из фотографии
def read_exif(photofile: str, photo_directory: str, own_dir: str) -> dict:  # функция чтения всех метаданных из файла
    os.chdir(photo_directory)  # pyexiv2.Image умеет работать только с английским языком, поэтому меняем директорию, тогда можно будет указывать только название самого файла, а его легко переименовать
    try:
        img = pyexiv2.Image(photofile)
        data = img.read_exif()
    except RuntimeError:    # Если в названии файла есть русские буквы, модуль его не считает, нужно переименовать, а потом обратно
        photofile_old = photofile
        os.rename(photofile, '123456789012345678901234567890.jpg')
        photofile = '123456789012345678901234567890.jpg'
        img = pyexiv2.Image(photofile)
        data = img.read_exif()
        os.rename('123456789012345678901234567890.jpg', photofile_old)
    img.close()
    os.chdir(own_dir)
    return data


# извлечь из фотографии дату съёмки
def date_from_exif(file_dir: str, own_dir: str, file: str) -> tuple[int,str,str,str]:
    data = read_exif(file, file_dir, own_dir)
    try:    # если дата считывается
        date = data['Exif.Photo.DateTimeOriginal']
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


# преобразование ебанутых дробей в exif в нормальные числа
def EXIF_text_to_float(exif_dannye: str) -> float:  # EXIF ебанутый, меняем дробные значения на float для показа
    s1 = exif_dannye
    s2 = s1.split('/')
    s3 = float(s2[0])
    s4 = float(s2[1])
    s5 = float(s3 / s4)
    return s5


# # из всех exif-данных вытаскиваются интересные для нас (камера, производитель, объектив, выдержка, ISO, диафрагма, фокусное расстояние, дата съёмки, координаты)
# def filter_exif(data: dict, photofile: str, photo_directory: str) -> tuple[str, str]:
#
#     metadata_text = str()
#
#     try:
#         width = data['Exif.Image.ImageWidth']
#         height = data['Exif.Image.ImageLength']
#         metadata_text += 'Разрешение: ' + width + 'x' + height + '\n'
#     except KeyError:
#         im = Image.open(photo_directory + '/' + photofile)
#         width, height = im.size
#         metadata_text += 'Разрешение: ' + str(width) + 'x' + str(height) + '\n'
#
#     if width > height:  # Eсли ширина фотографии больше -> она горизонтальная, иначе - вертикальная. Нужно для размещения элементов GUI на экране
#         photo_rotation = 'gor'
#     else:
#         photo_rotation = 'ver'
#
#     try:
#         date = data['Exif.Photo.DateTimeOriginal']  # делаем дату русской, а не пиндосской
#         date_show = date[11:] + ' ' + date[8:10] + '.' + date[5:7] + '.' + date[0:4]
#         metadata_text += 'Время съёмки: ' + date_show + '\n'
#     except KeyError:
#         pass
#
#     try:
#         maker = data['Exif.Image.Make']
#         sql_str = f'SELECT normname FROM ernames WHERE type = \'maker\' AND exifname = \'{maker}\''
#         cur.execute(sql_str)
#         try:
#             maker = cur.fetchone()[0]
#         except TypeError:
#             pass
#
#         metadata_text += 'Производитель: ' + maker + '\n'
#     except KeyError:
#         pass
#
#     try:
#         camera = data['Exif.Image.Model']
#
#         sql_str = f'SELECT normname FROM ernames WHERE type = \'camera\' AND exifname = \'{camera}\''
#         cur.execute(sql_str)
#         try:
#             camera = cur.fetchone()[0]
#         except TypeError:
#             pass
#
#         metadata_text += 'Камера: ' + camera + '\n'
#     except KeyError:
#         pass
#
#     try:
#         lens = data['Exif.Photo.LensModel']
#
#         sql_str = f'SELECT normname FROM ernames WHERE type = \'lens\' AND exifname = \'{lens}\''
#         cur.execute(sql_str)
#         try:
#             lens = cur.fetchone()[0]
#         except TypeError:
#             pass
#
#         metadata_text += 'Объектив: ' + lens + '\n'
#     except KeyError:
#         pass
#
#     try:
#         FocalLength_float = EXIF_text_to_float(data['Exif.Photo.FocalLength'])
#         FocalLength_str = str(FocalLength_float)
#         metadata_text += 'Фокусное расстояние: ' + FocalLength_str + '\n'
#     except KeyError:
#         pass
#
#     try:
#         FNumber_float = EXIF_text_to_float(data['Exif.Photo.FNumber'])
#         Number_str = str(FNumber_float)
#         metadata_text += 'Диафрагма: ' + Number_str + '\n'
#     except KeyError:
#         pass
#
#     try:
#         expo_time_fraction = data['Exif.Photo.ExposureTime']
#         expo_time_float = EXIF_text_to_float(data['Exif.Photo.ExposureTime'])
#         if expo_time_float >= 0.1:
#             expo_time_str = str(expo_time_float)
#             metadata_text += 'Выдержка: ' + expo_time_str + '\n'
#         else:
#             metadata_text += 'Выдержка: ' + expo_time_fraction + '\n'
#     except KeyError:
#         pass
#
#     try:
#         iso = data['Exif.Photo.ISOSpeedRatings']
#         metadata_text += 'ISO: ' + iso + '\n'
#     except KeyError:
#         pass
#
#     try:
#         GPSLatitudeRef = data['Exif.GPSInfo.GPSLatitudeRef']  # Считывание GPS из метаданных
#         GPSLatitude = data['Exif.GPSInfo.GPSLatitude']
#         GPSLongitudeRef = data['Exif.GPSInfo.GPSLongitudeRef']
#         GPSLongitude = data['Exif.GPSInfo.GPSLongitude']
#
#         if GPSLongitudeRef and GPSLatitudeRef and GPSLongitude and GPSLatitude:
#
#             GPSLatitude_splitted = GPSLatitude.split(' ')  # Приведение координат к десятичным числам, как на Я.Картах
#             GPSLongitude_splitted = GPSLongitude.split(' ')
#
#             GPSLongitude_float = list()
#             GPSLatitude_float = list()
#
#             for i in range(0, 3):
#                 GPSLongitude_float.append(EXIF_text_to_float(GPSLongitude_splitted[i]))
#                 GPSLatitude_float.append((EXIF_text_to_float(GPSLatitude_splitted[i])))
#
#             GPSLongitude_value = GPSLongitude_float[0] + GPSLongitude_float[1] / 60 + GPSLongitude_float[2] / 3600
#             GPSLatitude_value = GPSLatitude_float[0] + GPSLatitude_float[1] / 60 + GPSLatitude_float[2] / 3600
#
#             GPSLongitude_value = round(GPSLongitude_value, 6)
#             GPSLatitude_value = round(GPSLatitude_value, 6)
#
#             if GPSLongitudeRef == 'E':
#                 pass
#             else:
#                 GPSLongitude_value = GPSLongitude_value * (-1)
#
#             if GPSLatitudeRef == 'N':
#                 pass
#             else:
#                 GPSLatitude_value = GPSLatitude_value * (-1)
#
#             metadata_text += 'GPS: ' + str(GPSLatitude_value) + ' ' + str(GPSLongitude_value)
#         else:
#             pass
#     except KeyError:
#         pass
#
#     return metadata_text, photo_rotation


# из всех exif-данных вытаскиваются интересные для нас (камера, производитель, объектив, выдержка, ISO, диафрагма, фокусное расстояние, дата съёмки, координаты)
def filter_exif_beta(data: dict, photofile: str, photo_directory: str) -> dict[str, ...]:

    metadata = dict()

    try:
        width = data['Exif.Image.ImageWidth']
        height = data['Exif.Image.ImageLength']
        metadata['Разрешение'] = width + 'x' + height
    except KeyError:
        im = Image.open(photo_directory + '/' + photofile)
        width, height = im.size
        metadata['Разрешение'] = str(width) + 'x' + str(height)

    if width > height:  # Eсли ширина фотографии больше -> она горизонтальная, иначе - вертикальная. Нужно для размещения элементов GUI на экране
        metadata['Rotation'] = 'gor'
    else:
        metadata['Rotation'] = 'ver'

    try:
        date = data['Exif.Photo.DateTimeOriginal']  # делаем дату русской, а не пиндосской
        date_show = date[11:] + ' ' + date[8:10] + '.' + date[5:7] + '.' + date[0:4]
        metadata['Дата съёмки'] = date_show
    except KeyError:
        metadata['Дата съёмки'] = ''

    try:
        maker = data['Exif.Image.Make']
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
        camera = data['Exif.Image.Model']

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
        lens = data['Exif.Photo.LensModel']

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
        FocalLength_float = EXIF_text_to_float(data['Exif.Photo.FocalLength'])
        metadata['Фокусное расстояние'] = str(int(FocalLength_float))
    except KeyError:
        metadata['Фокусное расстояние'] = ''

    try:
        FNumber_float = EXIF_text_to_float(data['Exif.Photo.FNumber'])
        metadata['Диафрагма'] = str(FNumber_float)
    except KeyError:
        metadata['Диафрагма'] = ''

    try:
        expo_time_fraction = data['Exif.Photo.ExposureTime']
        expo_time_float = EXIF_text_to_float(data['Exif.Photo.ExposureTime'])
        if expo_time_float >= 0.1:
            expo_time_str = str(expo_time_float)
            metadata['Выдержка'] = expo_time_str
        else:
            metadata['Выдержка'] = expo_time_fraction
    except KeyError:
        metadata['Выдержка'] = ''

    try:
        iso = data['Exif.Photo.ISOSpeedRatings']
        metadata['ISO'] = iso
    except KeyError:
        metadata['ISO'] = ''

    try:
        GPSLatitudeRef = data['Exif.GPSInfo.GPSLatitudeRef']  # Считывание GPS из метаданных
        GPSLatitude = data['Exif.GPSInfo.GPSLatitude']
        GPSLongitudeRef = data['Exif.GPSInfo.GPSLongitudeRef']
        GPSLongitude = data['Exif.GPSInfo.GPSLongitude']

        if GPSLongitudeRef and GPSLatitudeRef and GPSLongitude and GPSLatitude:

            GPSLatitude_splitted = GPSLatitude.split(' ')  # Приведение координат к десятичным числам, как на Я.Картах
            GPSLongitude_splitted = GPSLongitude.split(' ')

            GPSLongitude_float = list()
            GPSLatitude_float = list()

            for i in range(0, 3):
                GPSLongitude_float.append(EXIF_text_to_float(GPSLongitude_splitted[i]))
                GPSLatitude_float.append((EXIF_text_to_float(GPSLatitude_splitted[i])))

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
def exif_for_db(photoname: str, photodirectory: str, own_dir: str) -> tuple[str, str, str, str]:
    data = read_exif(photoname, photodirectory, own_dir)

    try:
        camera = data['Exif.Image.Model']
    except KeyError:
        camera = "No data"

    try:
        lens = data['Exif.Photo.LensModel']
    except KeyError:
        lens = "No data"

    try:
        date = data['Exif.Photo.DateTimeOriginal']  # делаем дату русской, а не пиндосской
        date = date[0:4] + '.' + date[5:7] + '.' + date[8:10] + ' ' + date[11:]
    except KeyError:
        date = "No data"

    try:
        GPSLatitudeRef = data['Exif.GPSInfo.GPSLatitudeRef']  # Считывание GPS из метаданных
        GPSLatitude = data['Exif.GPSInfo.GPSLatitude']
        GPSLongitudeRef = data['Exif.GPSInfo.GPSLongitudeRef']
        GPSLongitude = data['Exif.GPSInfo.GPSLongitude']

        GPSLatitude_splitted = GPSLatitude.split(' ')  # Приведение координат к десятичным числам, как на Я.Картах
        GPSLongitude_splitted = GPSLongitude.split(' ')

        GPSLongitude_float = list()
        GPSLatitude_float = list()

        for i in range(0, 3):
            GPSLongitude_float.append(EXIF_text_to_float(GPSLongitude_splitted[i]))
            GPSLatitude_float.append((EXIF_text_to_float(GPSLatitude_splitted[i])))

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
def exif_show_edit(photoname: str, photodirectory: str, own_dir: str) -> dict:
    all_data = read_exif(photoname, photodirectory, own_dir)
    useful_data = dict()

    try:
        maker = all_data['Exif.Image.Make']
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
        camera = all_data['Exif.Image.Model']
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
        lens = all_data['Exif.Photo.LensModel']

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
        if EXIF_text_to_float(all_data['Exif.Photo.ExposureTime']) < 0.5:
            useful_data['Выдержка'] = all_data['Exif.Photo.ExposureTime']
        else:
            useful_data['Выдержка'] = str(EXIF_text_to_float(all_data['Exif.Photo.ExposureTime']))
    except KeyError:
        useful_data['Выдержка'] = ''

    try:
        useful_data['ISO'] = all_data['Exif.Photo.ISOSpeedRatings']
    except KeyError:
        useful_data['ISO'] = ''

    try:
        useful_data['Диафрагма'] = str(EXIF_text_to_float(all_data['Exif.Photo.FNumber']))
    except KeyError:
        useful_data['Диафрагма'] = ''

    try:
        useful_data['Фокусное расстояние'] = str(int(EXIF_text_to_float(all_data['Exif.Photo.FocalLength'])))
    except KeyError:
        useful_data['Фокусное расстояние'] = ''

    try:
        useful_data['Режим съёмки'] = all_data['Exif.Photo.ExposureProgram']
    except KeyError:
        useful_data['Режим съёмки'] = ''

    try:
        useful_data['Режим вспышки'] = all_data['Exif.Photo.Flash']
    except KeyError:
        useful_data['Режим вспышки'] = ''

    try:
        useful_data['Время съёмки'] = all_data['Exif.Photo.DateTimeOriginal']
    except KeyError:
        useful_data['Время съёмки'] = ''

    try:
        useful_data['Часовой пояс'] = all_data['Exif.Photo.OffsetTime']
    except KeyError:
        useful_data['Часовой пояс'] = ''

    try:
        useful_data['Серийный номер камеры'] = all_data['Exif.Photo.BodySerialNumber']
    except KeyError:
        useful_data['Серийный номер камеры'] = ''

    try:
        useful_data['Серийный номер объектива'] = all_data['Exif.Photo.LensSerialNumber']
    except KeyError:
        useful_data['Серийный номер объектива'] = ''

    try:
        GPSLatitudeRef = all_data['Exif.GPSInfo.GPSLatitudeRef']
        GPSLatitude = all_data['Exif.GPSInfo.GPSLatitude']
        GPSLongitudeRef = all_data['Exif.GPSInfo.GPSLongitudeRef']
        GPSLongitude = all_data['Exif.GPSInfo.GPSLongitude']

        GPSLatitude_splitted = GPSLatitude.split(' ')
        GPSLongitude_splitted = GPSLongitude.split(' ')

        GPSLongitude_float = list()
        GPSLatitude_float = list()

        for i in range(0, len(GPSLongitude_splitted)):
            GPSLongitude_float.append(EXIF_text_to_float(GPSLongitude_splitted[i]))

        for i in range(0, len(GPSLatitude_splitted)):
            GPSLatitude_float.append((EXIF_text_to_float(GPSLatitude_splitted[i])))

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
def exif_rewrite_edit(photoname: str, photodirectory: str, editing_type: int, new_value: str, own_dir: str) -> None:

    os.chdir(photodirectory)

    modify_dict = dict()
    modify_dict1 = dict()
    modify_dict2 = dict()
    modify_dict3 = dict()
    modify_dict4 = dict()

    try:
        img = pyexiv2.Image(photoname)
        renaming = 0
    except RuntimeError:    # Если в названии файла есть русские буквы, модуль его не считает, нужно переименовать, а потом обратно
        photofile_old = photoname
        os.rename(photoname, '123456789012345678901234567890.jpg')
        photofile = '123456789012345678901234567890.jpg'
        img = pyexiv2.Image(photofile)
        renaming = 1

    if editing_type == 0:
        modify_dict = {'Exif.Image.Make': str(new_value)}

    elif editing_type == 1:
        modify_dict = {'Exif.Image.Model': str(new_value)}

    elif editing_type == 2:
        modify_dict = {'Exif.Photo.LensModel': str(new_value)}

    elif editing_type == 3:

        if '/' in new_value:
            modify_dict = {'Exif.Photo.ExposureTime': str(new_value)}
        elif '.' in new_value:
            float_value = float(new_value)
            after = len(str(float_value).split('.')[1])
            int_value = int(float_value * (10 ** after))
            str_value = str(int_value) + '/' + str(10 ** after)

            modify_dict = {'Exif.Photo.ExposureTime': str(str_value)}
        else:
            str_value = str(new_value) + '/1'
            modify_dict = {'Exif.Photo.ExposureTime': str(str_value)}

    elif editing_type == 4:
        modify_dict = {'Exif.Photo.ISOSpeedRatings': str(new_value)}

    elif editing_type == 5:
        float_value = float(new_value)
        after = len(str(float_value).split('.')[1])
        int_value = int(float_value * (10 ** after))
        str_value = str(int_value) + '/' + str(10 ** after)

        modify_dict = {'Exif.Photo.FNumber': str(str_value)}

    elif editing_type == 6:
        str_value = str(new_value) + '/1'
        modify_dict = {'Exif.Photo.FocalLength': str(str_value)}

    elif editing_type == 7:
        modify_dict = {'Exif.Photo.ExposureProgram': str(new_value)}

    elif editing_type == 8:
        modify_dict = {'Exif.Photo.Flash': str(new_value)}

    elif editing_type == 9:
        modify_dict = {'Exif.Photo.DateTimeOriginal': str(new_value)}

    elif editing_type == 10:
        modify_dict = {'Exif.Photo.OffsetTime': str(new_value)}

    elif editing_type == 11:
        modify_dict = {'Exif.Photo.BodySerialNumber': str(new_value)}

    elif editing_type == 12:
        modify_dict = {'Exif.Photo.LensSerialNumber': str(new_value)}

    elif editing_type == 13:
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
        secund_float_lat = ((abs_value_lat - grad_lat) * 60 - int((abs_value_lat - grad_lat) * 60)) * 60
        secund_lat = round(secund_float_lat, 6)

        grad_lat_str = str(grad_lat) + '/1'
        minut_lat_str = str(minut_lat) + '/1'
        secund_lat_str = str(int(secund_lat*10000)) + '/10000'

        GPSLatitude = grad_lat_str + ' ' + minut_lat_str + ' ' + secund_lat_str

        abs_value_long = abs(float_value_long)
        grad_long = int(abs_value_long)
        minut_long = int((abs_value_long - grad_long) * 60)
        secund_float_long = ((abs_value_long - grad_long) * 60 - int((abs_value_long - grad_long) * 60)) * 60
        secund_long = round(secund_float_long, 6)

        grad_long_str = str(grad_long) + '/1'
        minut_long_str = str(minut_long) + '/1'
        secund_long_str = str(int(secund_long * 10000)) + '/10000'

        GPSLongitude = grad_long_str + ' ' + minut_long_str + ' ' + secund_long_str

        modify_dict1 = {'Exif.GPSInfo.GPSLatitudeRef': GPSLatitudeRef}
        modify_dict2 = {'Exif.GPSInfo.GPSLatitude': GPSLatitude}
        modify_dict3 = {'Exif.GPSInfo.GPSLongitudeRef': GPSLongitudeRef}
        modify_dict4 = {'Exif.GPSInfo.GPSLongitude': GPSLongitude}

    # Сделать сам модифай
    if modify_dict:
        img.modify_exif(modify_dict)

    if modify_dict1:
        img.modify_exif(modify_dict1)
        img.modify_exif(modify_dict2)
        img.modify_exif(modify_dict3)
        img.modify_exif(modify_dict4)

    img.close()

    if renaming != 1:
        pass
    else:
        os.rename('123456789012345678901234567890.jpg', photofile_old)
    os.chdir(own_dir)


# проверка ввода при редактировании exif
def exif_check_edit(photoname: str, photodirectory: str, editing_type: int, new_value: str, own_dir: str) -> None:

    # Ошибка ввода вызывает ошибку для except в объекте окна, который уже там делает return
    def make_error():
        # Если имело место переименование, надо переименовать обратно, иначе фото, по сути будет потеряно
        if renaming != 1:
            pass
        else:
            os.rename('123456789012345678901234567890.jpg', photofile_old)
        os.chdir(own_dir)
        raise EditExifError

    os.chdir(photodirectory)

    try:
        img = pyexiv2.Image(photoname)
        renaming = 0
    except RuntimeError:    # Если в названии файла есть русские буквы, модуль его не считает, нужно переименовать, а потом обратно
        photofile_old = photoname
        os.rename(photoname, '123456789012345678901234567890.jpg')
        photofile = '123456789012345678901234567890.jpg'
        img = pyexiv2.Image(photofile)
        renaming = 1

    if editing_type == 3:
        if '/' in new_value:
            try:
                if int(new_value.split('/')[0]) < 0 or int(new_value.split('/')[1]) < 0:
                    make_error()
            except Exception:
                make_error()
        elif '.' in new_value:
            try:
                float_value = float(new_value)
                if float_value < 0:
                    make_error()
            except ValueError:
                make_error()
        else:
            try:
                int(new_value)
            except ValueError:
                make_error()

    elif editing_type == 4:
        try:
            int(new_value)
            if int(new_value) < 0:
                make_error()
        except ValueError:
            make_error()

    elif editing_type == 5:
        try:
            float_value = float(new_value)
            after = len(str(float_value).split('.')[1])
            int_value = int(float_value * (10 ** after))
            if float_value < 0:
                make_error()
        except ValueError:
            make_error()

    elif editing_type == 6:
        try:
            if int(new_value) < 0:
                make_error()
        except ValueError:
            make_error()

    elif editing_type == 7:
        try:
            if int(new_value) < 10:
                pass
            else:
                make_error()
        except ValueError:
            make_error()

    elif editing_type == 8:
        try:
            if int(new_value) < 256:
                pass
            else:
                make_error()
        except ValueError:
            make_error()

    elif editing_type == 9:
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

    elif editing_type == 10:
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

    elif editing_type == 13:
        new_value_splitted = new_value.split(', ')

        try:
            float(new_value_splitted[0])
            float(new_value_splitted[1])
        except (ValueError, IndexError):
            make_error()

    img.close()

    if renaming != 1:
        pass
    else:
        os.rename('123456789012345678901234567890.jpg', photofile_old)
    os.chdir(own_dir)


# Замена неправильного названия для выбора группировки на правильное
def equip_name_check(equip_list: list[str, ...], type: str) -> list[str,...]:
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


# при любой ошибки в процессе modify_exif вызывается ошибка
class EditExifError(Exception):
    pass