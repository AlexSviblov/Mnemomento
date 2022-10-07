import sqlite3
import piexif
import exiftool
from PIL import Image

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
    data = {}
    with exiftool.ExifToolHelper() as et:
        for dictionary in et.get_metadata(photofile):
            for tag_key, tag_value in dictionary.items():
                data[f"{tag_key}"]= tag_value
    return data


# извлечь из фотографии дату съёмки
def date_from_exif(data: dict) -> tuple[int, str, str, str]:
    """
    Для определения папки хранения файла в основном каталоге, необходимо при его добавлении в программу, достать
    дату съёмки из метаданных.
    :param file: абсолютный путь к файлу.
    :return: error = 1, если даты нет, и фото следует поместить в No_Date_Info, иначе - day, month, year - строки
    длинами 2, 2, 4 соответственно.
    """

    try:  # если дата считывается
        date = data['EXIF:DateTimeOriginal']
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
        width = str(data['File:ImageWidth'])
        height = str(data['File:ImageHeight'])
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
        date = data['EXIF:DateTimeOriginal']  # делаем дату русской, а не пиндосской
        date_show = date[11:] + ' ' + date[8:10] + '.' + date[5:7] + '.' + date[0:4]
        metadata['Дата съёмки'] = date_show
    except KeyError:
        metadata['Дата съёмки'] = ''

    try:
        maker = data['EXIF:Make']
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
        camera = data['EXIF:Model']

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
        lens = data['EXIF:LensModel']

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
        FocalLength_float = data['EXIF:FocalLength']
        metadata['Фокусное расстояние'] = str(int(FocalLength_float))
    except KeyError:
        metadata['Фокусное расстояние'] = ''

    try:
        FNumber_float = data['EXIF:FNumber']
        metadata['Диафрагма'] = str(FNumber_float)
    except KeyError:
        metadata['Диафрагма'] = ''

    try:
        expo_time = data['EXIF:ExposureTime']
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
        iso = data['EXIF:ISO']
        metadata['ISO'] = str(iso)
    except KeyError:
        metadata['ISO'] = ''

    try:
        GPSLatitudeRef = data['EXIF:GPSLatitudeRef']  # Считывание GPS из метаданных
        GPSLatitude = data['EXIF:GPSLatitude']
        GPSLongitudeRef = data['EXIF:GPSLongitudeRef']
        GPSLongitude = data['EXIF:GPSLongitude']

        if GPSLongitudeRef and GPSLatitudeRef and GPSLongitude and GPSLatitude:

            GPSLongitude_float = float(GPSLongitude)  # Приведение координат к десятичным числам, как на Я.Картах
            GPSLatitude_float = float(GPSLatitude)

            GPSLongitude_value = round(GPSLongitude_float, 4)
            GPSLatitude_value = round(GPSLatitude_float, 4)

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
def exif_for_db(data: dict) -> tuple[str, str, str, str]:
    """
    Вынуть из фото метаданные для БД: камера, объектив, дата съёмки, дата-время съёмки, GPS.
    :param photoname: имя файла.
    :param photodirectory: директория для хранения фото.
    :return: камера, объектив, дата, GPS.
    """
    try:
        camera = data['EXIF:Model']
    except KeyError:
        camera = ""

    try:
        lens = data['EXIF:LensModel']
    except KeyError:
        lens = ""

    try:
        date = data['EXIF:DateTimeOriginal']  # делаем дату русской, а не пиндосской
        date = date[0:4] + '.' + date[5:7] + '.' + date[8:10] + ' ' + date[11:]
    except KeyError:
        date = ""

    try:
        GPSLatitudeRef = data['EXIF:GPSLatitudeRef']  # Считывание GPS из метаданных
        GPSLatitude = round(float(data['EXIF:GPSLatitude']), 4)
        GPSLongitudeRef = data['EXIF:GPSLongitudeRef']
        GPSLongitude = round(float(data['EXIF:GPSLongitude']), 4)

        if GPSLongitudeRef == 'E':
            pass
        else:
            GPSLongitude = GPSLongitude * (-1)

        if GPSLatitudeRef == 'N':
            pass
        else:
            GPSLatitude = GPSLatitude * (-1)
        GPS = str(GPSLatitude) + ', ' + str(GPSLongitude)
    except KeyError:
        GPS = ""

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
    all_data = read_exif(photoname)

    useful_data = dict()

    try:
        maker = all_data['EXIF:Make']
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
        camera = all_data['EXIF:Model']
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
        lens = all_data['EXIF:LensModel']

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
        if all_data['EXIF:ExposureTime'] < 0.1:
            try:
                denominator = 1 / all_data['EXIF:ExposureTime']
                expo_time_show = f"1/{int(denominator)}"
            except ZeroDivisionError:
                expo_time_show = '0'
            useful_data['Выдержка'] = expo_time_show
        else:
            useful_data['Выдержка'] = str(all_data['EXIF:ExposureTime'])
    except KeyError:
        useful_data['Выдержка'] = ''

    try:
        useful_data['ISO'] = all_data['EXIF:ISO']
    except KeyError:
        useful_data['ISO'] = ''

    try:
        useful_data['Диафрагма'] = str(all_data['EXIF:FNumber'])
    except KeyError:
        useful_data['Диафрагма'] = ''

    try:
        useful_data['Фокусное расстояние'] = str(int(all_data['EXIF:FocalLength']))
    except KeyError:
        useful_data['Фокусное расстояние'] = ''

    try:
        useful_data['Время съёмки'] = all_data['EXIF:DateTimeOriginal']
    except KeyError:
        useful_data['Время съёмки'] = ''

    try:
        useful_data['Часовой пояс'] = all_data['EXIF:OffsetTime']
    except KeyError:
        useful_data['Часовой пояс'] = ''

    try:
        useful_data['Серийный номер камеры'] = all_data['EXIF:SerialNumber']
    except KeyError:
        useful_data['Серийный номер камеры'] = ''

    try:
        useful_data['Серийный номер объектива'] = all_data['EXIF:LensSerialNumber']
    except KeyError:
        useful_data['Серийный номер объектива'] = ''

    try:
        GPSLatitudeRef = all_data['EXIF:GPSLatitudeRef']  # Считывание GPS из метаданных
        GPSLatitude = all_data['EXIF:GPSLatitude']
        GPSLongitudeRef = all_data['EXIF:GPSLongitudeRef']
        GPSLongitude = all_data['EXIF:GPSLongitude']

        GPSLatitude_float = float(GPSLatitude)  # Приведение координат к десятичным числам, как на Я.Картах
        GPSLongitude_float = float(GPSLongitude)

        GPSLongitude_value = round(GPSLongitude_float, 4)
        GPSLatitude_value = round(GPSLatitude_float, 4)

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
def exif_rewrite_edit(photoname: str, photodirectory: str, new_value_dict):
    photofile = photodirectory + '/' + photoname

    modify_dict = dict()

    editing_types = list(new_value_dict.keys())

    for edit_type in editing_types:
        match edit_type:
            case 0:
                modify_dict['EXIF:Make'] = new_value_dict[0]

            case 1:
                modify_dict['EXIF:Model'] = new_value_dict[1]

            case 2:
                modify_dict['EXIF:LensModel'] =new_value_dict[2]

            case 3:
                if '/' in new_value_dict[3]:
                    float_value = 1 / float(new_value_dict[3].split('/')[1])
                else:
                    float_value = float(new_value_dict[3])
                modify_dict['EXIF:ExposureTime'] = float_value

            case 4:
                modify_dict['EXIF:ISO'] = new_value_dict[4]

            case 5:
                modify_dict['EXIF:FNumber'] = new_value_dict[5]

            case 6:
                modify_dict['EXIF:FocalLength'] = new_value_dict[6]

            case 11:
                modify_dict['EXIF:DateTimeOriginal'] = new_value_dict[11]

            case 8:
                modify_dict['EXIF:OffsetTime'] = new_value_dict[8]

            case 9:
                modify_dict['EXIF:SerialNumber'] = new_value_dict[9]

            case 10:
                modify_dict['EXIF:LensSerialNumber'] = new_value_dict[10]

            case 7:
                new_value_splitted =  new_value_dict[7].split(', ')
                float_value_lat = float(new_value_splitted[0])
                float_value_long = float(new_value_splitted[1])

                if float_value_lat > 0:
                    lat_ref = 'N'
                else:
                    lat_ref = 'S'

                if float_value_long > 0:
                    long_ref = 'E'
                else:
                    long_ref = 'W'

                modify_dict['GPSLatitudeRef'] = lat_ref
                modify_dict['GPSLatitude'] = float_value_lat
                modify_dict['GPSLongitudeRef'] = long_ref
                modify_dict['GPSLongitude'] = float_value_long

    # Сделать сам модифай
    if modify_dict:
        with exiftool.ExifToolHelper() as et:
            et.set_tags(photofile,
                        tags=modify_dict,
                        params=["-P", "-overwrite_original"])




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

    match editing_type:

        # выдержка
        case 3:
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
        case 4:
            try:
                int(new_value)
                if int(new_value) < 0:
                    make_error()
            except ValueError:
                make_error()

        # диафрагма
        case 5:
            try:
                float_value = float(new_value)
                if float_value < 0:
                    make_error()
            except ValueError:
                make_error()

        # фокусное расстояние
        case 6:
            try:
                if int(new_value) < 0:
                    make_error()
            except ValueError:
                make_error()

        # дата съёмки
        case 11:
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
        case 8:
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
        case 7:
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
    :param photodirectory: директория хранения.
    :return: в отличие от перезаписи или добавления метаданных, не требуется создание нового файла.
    """
    photofile = photodirectory + '/' + photoname

    piexif.remove(photofile)


# Проверка и исправление ориентации фотографии
def check_photo_rotation(photo_file: str, data: dict) -> None:
    """
    Для добавляемых в каталоги фотографий можно сделать нормальный поворот, чтобы ен крутить их каждый раз
    :param photo_file: абсолютный путь к фотографии
    :return: фотография нормально повёрнута
    """
    try:
        try:
            width = data['EXIF:ImageWidth']
            height = data['EXIF:ImageHeight']
        except KeyError:
            meta_orientation = data['EXIF:Orientation']
            im = Image.open(photo_file)
            exif_dict = piexif.load(im.info["exif"])
            exif_bytes = piexif.dump(exif_dict)
            match meta_orientation:
                case 1:
                    im_flipped = im
                    width = data['File:ImageWidth']
                    height = data['File:ImageHeight']
                case 2:
                    im_flipped = im.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
                    width = data['File:ImageWidth']
                    height = data['File:ImageHeight']
                case 3:
                    im_flipped = im.transpose(method=Image.Transpose.ROTATE_180)
                    width = data['File:ImageWidth']
                    height = data['File:ImageHeight']
                case 4:
                    im_flipped = im.transpose(method=Image.Transpose.FLIP_TOP_BOTTOM)
                    width = data['File:ImageWidth']
                    height = data['File:ImageHeight']
                case 5:
                    im_flipped_temp = im.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
                    # im_flipped = im_flipped_temp.transpose(method=Image.Transpose.ROTATE_270)
                    im_flipped = im_flipped_temp.transpose(method=Image.Transpose.ROTATE_90)
                    width = data['File:ImageHeight']
                    height = data['File:ImageWidth']
                case 6:
                    # im_flipped = im.transpose(method=Image.Transpose.ROTATE_90)
                    im_flipped = im.transpose(method=Image.Transpose.ROTATE_270)
                    width = data['File:ImageHeight']
                    height = data['File:ImageWidth']
                case 7:
                    im_flipped_temp = im.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
                    # im_flipped = im_flipped_temp.transpose(method=Image.Transpose.ROTATE_90)
                    im_flipped = im_flipped_temp.transpose(method=Image.Transpose.ROTATE_270)
                    width = data['File:ImageHeight']
                    height = data['File:ImageWidth']
                case 8:
                    # im_flipped = im.transpose(method=Image.Transpose.ROTATE_270)
                    im_flipped = im.transpose(method=Image.Transpose.ROTATE_90)
                    width = data['File:ImageHeight']
                    height = data['File:ImageWidth']
                case _:
                    im_flipped = im
                    width = data['File:ImageWidth']
                    height = data['File:ImageHeight']

            im_flipped.save(photo_file, 'jpeg', exif=exif_bytes, quality=95, subsampling=0)

            im.close()
            im_flipped.close()
            write_normal_photo_size(photo_file, int(width), int(height))
    except KeyError:
        im = Image.open(photo_file)
        width = im.width
        height = im.height
        im.close()
        write_normal_photo_size(photo_file, int(width), int(height))


# записать в метаданные нормально ширину и высоту картинки
def write_normal_photo_size(photo_file: str, width: int, height: int) -> None:
    """
    После поворота, как надо, необходимо вписать в метаданные в нормальном виде размеры сторон и актуальную ориентацию (Top_Left)
    :param photo_file: абсолютный пуь к фотографии
    :param width: ширина в пикселях
    :param height: высота в пикселях
    :return:
    """

    with exiftool.ExifToolHelper() as et:
        et.set_tags(photo_file,
                    tags={'EXIF:ImageWidth': width, 'EXIF:ImageHeight': height, 'EXIF:Orientation': 1},
                    params=["-P", "-overwrite_original"])


# Ориантация файла при разовом просмотре
def onlyshow_rotation(photo_file: str) -> tuple[str, int]:
    """
    Так как для разового просомтра файл не редактируется, а отобразить корректно его надо - если он с нормальной
    ориентацией, то показывается он, иначе создаётся нормально повёрнутая копия этого файла и отображается она
    :param photo_file: путь к файлу, который надо показать
    :return: соответствует ли ориентация той, что считана в showinfo заранее, если нет - выбрать обратную
    """
    data = read_exif(photo_file)
    im = Image.open(photo_file)

    meta_orientation = data['EXIF:Orientation']
    match meta_orientation:
        case 1:
            im_flipped = im
            photo_show = photo_file
            orientation = 1
        case 2:
            im_flipped = im.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
            photo_show = photo_file
            orientation = 1
        case 3:
            im_flipped = im.transpose(method=Image.Transpose.ROTATE_180)
            photo_show = photo_file
            orientation = 1
        case 4:
            im_flipped = im.transpose(method=Image.Transpose.FLIP_TOP_BOTTOM)
            photo_show = photo_file
            orientation = 1
        case 5:
            im_flipped_temp = im.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
            # im_flipped = im_flipped_temp.transpose(method=Image.Transpose.ROTATE_270)
            im_flipped = im.transpose(method=Image.Transpose.ROTATE_90)
            im_flipped.save(photo_file + '_temp', 'jpeg', quality=95, subsampling=0)
            photo_show = photo_file + '_temp'
            orientation = 0
        case 6:
            # im_flipped = im.transpose(method=Image.Transpose.ROTATE_90)
            im_flipped = im.transpose(method=Image.Transpose.ROTATE_270)
            im_flipped.save(photo_file + '_temp', 'jpeg', quality=95, subsampling=0)
            photo_show = photo_file + '_temp'
            orientation = 0
        case 7:
            im_flipped_temp = im.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
            # im_flipped = im_flipped_temp.transpose(method=Image.Transpose.ROTATE_90)
            im_flipped = im.transpose(method=Image.Transpose.ROTATE_270)
            im_flipped.save(photo_file + '_temp', 'jpeg', quality=95, subsampling=0)
            photo_show = photo_file + '_temp'
            orientation = 0
        case 8:
            # im_flipped = im.transpose(method=Image.Transpose.ROTATE_270)
            im_flipped = im.transpose(method=Image.Transpose.ROTATE_90)
            im_flipped.save(photo_file + '_temp', 'jpeg', quality=95, subsampling=0)
            photo_show = photo_file + '_temp'
            orientation = 0
        case _:
            im_flipped = im
            photo_show = photo_file
            orientation = 1

    return photo_show, orientation


# Ориентация миниатюры фотографии при разовом просмотре
def onlyshow_thumbnail_orientation(photo_file: str, thumbnail_file: str) -> None:
    """
    Если файл кривой, то надо повернуть его миниатюру (сначала создаётся миниатюра, потом поворачивается)
    :param photo_file: абсолютный путь фотографии (узнать ориентацию)
    :param thumbnail_file: абсолютный путь миниатюры
    :return: миниатюра ставится в корректное положение
    """
    data = read_exif(photo_file)
    thum = Image.open(thumbnail_file)
    meta_orientation = data['EXIF:Orientation']
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

    thum_flipped.save(thumbnail_file, 'jpeg', quality=95, subsampling=0)