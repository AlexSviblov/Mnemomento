import logging

from PIL import Image   # type: ignore[import]
import os
import shutil
import Settings


# получение списка файлов формата jpg из папки
def get_images_list(directory: str) -> list[str]:
    """
    :param directory: абсолютный путь к папке, возвращается.
    :return: список абсолютных путей ко всем файлам формата JPG в directory.
    """
    file_list = list()
    for file in os.listdir(directory):
        if file.endswith(".jpg") or file.endswith(".JPG"):
            file_list.append(file)
    return file_list


# Создать миниатюры при добавлении папки или файлов "на постоянку" в основной каталог
def make_const_thumbnails(directory: str, file: str) -> None:
    """
    Используется (по состоянию на 05.09.22) только в FileDirs.transfer_const_photos.
    :param directory: передаётся абсолютный путь директории, где должна будет храниться миниатюра.
    :param file: передаётся абсолютный путь к файлу (фотографии), миниатюру которого надо создать.
    :return: в нужной папке в каталоге хранения миниатюр создаётся миниатюра добавленной в основной каталог фотографии.
    """
    destination_thumbs = Settings.get_destination_thumb()
    directory_splitted = directory.split('/')
    year = directory_splitted[-3]
    month = directory_splitted[-2]
    day = directory_splitted[-1]
    if not os.path.isdir(destination_thumbs + '/thumbnail/const/' + year):
        os.mkdir(destination_thumbs + '/thumbnail/const/' + year)
    if not os.path.isdir(destination_thumbs + '/thumbnail/const/' + year + '/' + month):
        os.mkdir(destination_thumbs + '/thumbnail/const/' + year + '/' + month)
    if not os.path.isdir(destination_thumbs + '/thumbnail/const/' + year + '/' + month + '/' + day):
        os.mkdir(destination_thumbs + '/thumbnail/const/' + year + '/' + month + '/' + day)

    image = Image.open(r"{}".format(directory + '/' + file))
    image.thumbnail((250, 250))     # TODO: размер кнопки 150*150, может поменять размер миниатюр
    date = year + '/' + month + '/' + day
    image.save(destination_thumbs + f'/thumbnail/const/{date}/thumbnail_{file}')
    image.close()


# Создать миниатюры при добавлении папки или файлов "на постоянку" в дополнительный каталог
def make_alone_thumbnails(directory_lastname: str, photofile: str, photofile_lastname: str) -> None:
    """
    Используется (по состоянию на 05.09.22) только в FileDirs.transfer_alone_photos.
    :param directory_lastname: название добавляемой папки.
    :param photofile: абсолютный путь к фотографии.
    :param photofile_lastname: имя файла, миниатюру которого надо сделать (IMG_4049.jpg).
    :return:
    """
    destination_thumbs = Settings.get_destination_thumb()
    if not os.path.isdir(destination_thumbs + '/thumbnail/alone/' + directory_lastname):
        os.mkdir(destination_thumbs + '/thumbnail/alone/' + directory_lastname)

    image = Image.open(r"{}".format(photofile))
    image.thumbnail((250, 250))
    image.save(destination_thumbs + '/thumbnail/alone/' + directory_lastname + f'/thumbnail_{photofile_lastname}')
    image.close()


# Сравнение, какие миниатюры лишние, каких недостаточно
def research_flaw_thumbnails(photo_directory: str, thumbnail_directory: str) -> tuple[list[str], list[str]]:
    """
    При выборе папки в доп.каталоге или даты в основном, проверяется, нет ли в директории миниатюр лишних файлов
    или, наоборот, недостающих. При нормальной работе программы это не должно понадобиться, но пусть будет.
    Так как применяется в нештатных ситуациях, то и в основном каталоге при выборе группировки по оборудованию
    и соцсетям, делать я это не стал.
    :param photo_directory: абсолютный путь к папке с фотографиями.
    :param thumbnail_directory: абсолютный путь к папке с миниатюрами.
    :return: список недостающих миниатюр, которые надо создать, и список избыточных миниатюр, которые надо удалить,
    чтобы память не занимали впустую.
    """
    destination_thumbs = Settings.get_destination_thumb()
    thumbnail_directory_splitted = thumbnail_directory.split('/')
    if '/const/' in thumbnail_directory:
        thumb_year = thumbnail_directory_splitted[-3]
        thumb_month = thumbnail_directory_splitted[-2]
        thumb_day = thumbnail_directory_splitted[-1]
        if not os.path.isdir(thumbnail_directory):
            if not os.path.isdir(destination_thumbs + '/thumbnail/const/' + thumb_year + '/' + thumb_month):
                if not os.path.isdir(destination_thumbs + '/thumbnail/const/' + thumb_year):
                    os.mkdir(destination_thumbs + '/thumbnail/const/' + thumb_year)
                else:
                    os.mkdir(destination_thumbs + '/thumbnail/const/' + thumb_year + '/' + thumb_month)
            else:
                os.mkdir(destination_thumbs + '/thumbnail/const/' + thumb_year + '/' + thumb_month + '/' + thumb_day)

    elif '/alone/' in thumbnail_directory:
        alone_dir = thumbnail_directory_splitted[-1]
        if not os.path.isdir(thumbnail_directory):
            os.mkdir(destination_thumbs + '/thumbnail/alone/' + alone_dir)

    thumbsfull_already = get_images_list(thumbnail_directory)
    thumbs_already = list()
    for thumb in thumbsfull_already:
        thumbs_already.append(thumb[10:])

    images_list = get_images_list(photo_directory)
    flaw_thumbs_result = list(set(images_list) - set(thumbs_already))  # есть фото, но нет миниатюр
    excess_thumbs_result = list(set(thumbs_already) - set(images_list))  # есть миниатюра, а фото нет
    return flaw_thumbs_result, excess_thumbs_result


# Создание недостающих миниатюр и удаление лишних
def make_or_del_thumbnails(flaw_thumbnails: list, excess_thumbs: list, photo_directory: str, thumbnail_directory: str) -> None:
    """
    Связано с предыдущей функций непосредственно # TODO: может их тогда объединить
    :param flaw_thumbnails: список фотографий, к которым недостаёт миниатюр, их адо создать.
    :param excess_thumbs: список миниатюр, к которым нет фотографий, их надо удалить.
    :param photo_directory: абсолютный путь к папке с фотографиями.
    :param thumbnail_directory: абсолютный путь к папке с миниатюрами.
    :return: баланс в папке миниатюр до следующего сбоя.
    """
    if flaw_thumbnails:
        for file in flaw_thumbnails:
            image = Image.open(r"{}".format(photo_directory + '/' + file))
            image.thumbnail((250, 250))
            image.save(thumbnail_directory + f'/thumbnail_{file}')
            image.close()

    if excess_thumbs:
        for file in excess_thumbs:
            os.remove(thumbnail_directory + '/thumbnail_' + file)


# Создание миниатюр для просмотра
def make_thumbnails_view(photo_file: str) -> None:
    """
    Создание миниатюр дял режима просмотра. Делать миниатюры для кнопок так и так надо. Если для основого и
    дополнительного каталогов, создание миниатюр один раз это ускорение последущих отображений миниатюр, то
    в режиме одноразового просмотра это необходимость.
    :param photo_file: абсолютный путь к фотографии, для которой надо создать миниатюру.
    :return: миниатюра для переданного фото (а в общем контексте - всем выбранным для разового просмотра файла) создана.
    """
    destination_thumbs = Settings.get_destination_thumb()
    photo_splitted = photo_file.split('/')
    photo_name = photo_splitted[-1]     # C:/Users/Александр/Desktop/PVF/Фото/2022/Июнь/25Настя/IMG_4090.jpg
    image = Image.open(r"{}".format(photo_file))
    image.thumbnail((250, 250))
    image.save(destination_thumbs + '/thumbnail/view' + f'/thumbnail_{photo_name}')
    image.close()


# удаление миниатюр фото для разового просмотра
def delete_exists() -> None:
    """
    То что прошлая функция создала, при закрытии программы надо стереть, чтобы просто так не валялось.
    Также применяется при повторном пользовании функцией разового просмотра в рамках 1 сессии.
    :return: папка view в диреткории хранения миниатюр пуста.
    """
    destination_thumbs = Settings.get_destination_thumb()
    existing_thumbs = get_images_list(destination_thumbs + '/thumbnail/view/')
    for file in existing_thumbs:
        os.remove(destination_thumbs + '/thumbnail/view/' + file)


# Удалить миниатюру файла, удаляемого из основного каталога
def delete_thumbnail_const(photoname: str, photodirectory: str) -> None:
    """
    При удалении файла производится в т.ч. и удаление миниатюры (чтобы не засорять память).
    :param photoname: имя файла (не путь).
    :param photodirectory: путь директории фотографии (не миниатюры).
    :return: миниатюра удалена.
    """
    destination_thumbs = Settings.get_destination_thumb()
    dir_splitted = photodirectory.split('/')
    date_part = dir_splitted[-3]+'/'+dir_splitted[-2]+'/'+dir_splitted[-1]
    thumb_dir = destination_thumbs + '/thumbnail/const/' + date_part
    os.remove(thumb_dir + '/thumbnail_' + photoname)


# перенос миниатюры при изменении даты в метаданных снимка
def transfer_equal_date_thumbnail(old_name: str, new_name: str, old_date: list[str], new_date: list[str], rename_name: str, chosen: str) -> None:
    """
    Если у фотографии в основном каталоге была изменена дата в метаданных, то фото переносится в другую папку,
    также необходимо перенести и миниатюру в соответствующую папку в каталоге хранения миниатюр.
    Применяется только, когда было совпадение имён, то есть папка назначения переноса гарантированно существует.
    :param old_name: имя файла в папке назначения .
    :param new_name: имя переносимого файла.
    :param old_date: новая дата съёмки изменённого файла.
    :param new_date: старая дата съёмки изменённого файла.
    :param rename_name: новое имя переименовываемого файла.
    :param chosen: какой файл переименовывается, переносимый или уже находящийся в папке назначения.
    :return: миниатюра перенесена в новую папку.
    """
    destination_thumbs = Settings.get_destination_thumb()

    if chosen == 'old':    # переименовывают файл уже находящийся в папке
        try:
            os.rename(destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/' + old_date[2] + f'/thumbnail_{old_name}',
                      destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/' + old_date[2] + f'/thumbnail_{rename_name}')
        except FileExistsError:
            os.remove(destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/' + old_date[2] + f'/thumbnail_{rename_name}')
            os.rename(destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/' + old_date[2] + f'/thumbnail_{old_name}',
                      destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/' + old_date[2] + f'/thumbnail_{rename_name}')
        shutil.move(destination_thumbs + '/thumbnail/const/' + new_date[0] + '/' + new_date[1] + '/' + new_date[2] + f'/thumbnail_{new_name}',
                    destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/' + old_date[2] + '/')
    else:   # chosen == 'new' - переименовывают переносимый файл
        try:
            os.rename(destination_thumbs + '/thumbnail/const/' + new_date[0] + '/' + new_date[1] + '/' + new_date[2] + f'/thumbnail_{new_name}',
                  destination_thumbs + '/thumbnail/const/' + new_date[0] + '/' + new_date[1] + '/' + new_date[2] + f'/thumbnail_{rename_name}')
        except FileExistsError:
            os.remove(destination_thumbs + '/thumbnail/const/' + new_date[0] + '/' + new_date[1] + '/' + new_date[2] + f'/thumbnail_{rename_name}')
            os.rename(destination_thumbs + '/thumbnail/const/' + new_date[0] + '/' + new_date[1] + '/' + new_date[2] + f'/thumbnail_{new_name}',
                      destination_thumbs + '/thumbnail/const/' + new_date[0] + '/' + new_date[1] + '/' + new_date[2] + f'/thumbnail_{rename_name}')

        shutil.move(destination_thumbs + '/thumbnail/const/' + new_date[0] + '/' + new_date[1] + '/' + new_date[2] + f'/thumbnail_{rename_name}',
                    destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/' + old_date[2] + '/')


# перенести миниатюру после переноса файла
def transfer_diff_date_thumbnail(photoname: str, new_date: list[str], old_date: list[str]) -> None:
    """
    Перенос миниатюры при переносе фотографии, вызванном изменением даты.
    :param photoname: имя фотографии.
    :param new_date: дата, из директории которой надо перенести.
    :param old_date: дата, в директорию которой надо перенести.
    :return: миниатюра перенесена.
    """
    destination_thumbs = Settings.get_destination_thumb()
    new_dir = destination_thumbs + '/thumbnail/const/' + new_date[0] + '/' + new_date[1] + '/' + new_date[2] + '/thumbnail_'
    old_dir = destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/' + old_date[2] + '/'
    if not os.path.isdir(old_dir):
        if not os.path.isdir(destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1]):
            if not os.path.isdir(destination_thumbs + '/thumbnail/const/' + old_date[0]):
                os.mkdir(destination_thumbs + '/thumbnail/const/' + old_date[0] + '/')
                os.mkdir(destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/')
                os.mkdir(destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/' + old_date[2] + '/')
            else:
                os.mkdir(destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/')
                os.mkdir(destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/' + old_date[2] + '/')
        else:
            os.mkdir(destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/' + old_date[2] + '/')
    shutil.move(new_dir + photoname, old_dir)


# Удалить миниатюру файла, удаляемого из дополнительного каталога
def delete_thumbnail_alone(photoname: str, photodirectory: str) -> None:
    """
    При удалении файла производится в т.ч. и удаление миниатюры (чтобы не засорять память).
    :param photoname: имя файла (не путь).
    :param photodirectory: путь директории фотографии (не миниатюры).
    :return: миниатюра удалена.
    """
    destination_thumbs = Settings.get_destination_thumb()
    dir_splitted = photodirectory.split('/')
    dir_name = dir_splitted[-1]
    thumb_dir = destination_thumbs + '/thumbnail/alone/' + dir_name
    os.remove(thumb_dir + '/thumbnail_' + photoname)


# Удалить все миниатюры и сами фото директории из доп.каталога
def delete_thumb_dir(photodirectory: str) -> None:
    """
    Если из дополнительного каталога удаляется папка - удалить её миниатюры.
    :param photodirectory: название папки.
    :return: удалены и миниатюры, и их папка.
    """
    destination_thumbs = Settings.get_destination_thumb()
    photo_dir_splitted = photodirectory.split('/')
    dir_name = photo_dir_splitted[-1]
    thumb_dir = destination_thumbs + '/thumbnail/alone/' + dir_name
    thumb_list = get_images_list(thumb_dir)
    for file in thumb_list:
        os.remove(destination_thumbs + f'/thumbnail/alone/{dir_name}/{file}')

    os.rmdir(destination_thumbs + f'/thumbnail/alone/{dir_name}')

