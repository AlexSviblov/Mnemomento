import os
import shutil

import Settings
import Metadata
import Thumbnail
import PhotoDataDB


# Достаёт список файлов расширения jpg из папки
def make_files_list_from_dir(directory: str) -> list[str]:
    """
    :param directory: абсолютный путь к папке, возвращается.
    :return: список абсолютных путей ко всем файлам формата JPG в directory.
    """
    file_list = list()
    for file in os.listdir(directory):
        if file.endswith(".jpg") or file.endswith(".JPG"):
            file_list.append(directory + '/' + file)
    return file_list


# Перенос файлов, создание записи в БД и создание миниатюры для основного каталога
def transfer_const_photos(file: str) -> str:
    """
    Для фото file проверяется его дата съёмки, при необходимости создаётся директория для этой даты в директории
    хранения фотографий, создаётся запись в БД, создаётся миниатюра.
    :param file: абсолютный путь фотографии = 'C:/Users/user/Pictures/1.jpg'
    :return: если такой файл уже добавлен (совпадение по имени и дате), то вернуть его.
    """
    destination = Settings.get_destination_media() + '/Media/Photo/const/'
    mode = Settings.get_photo_transfer_mode()
    file_dir = ''
    file_full = file.split(r'/')
    for i in range(len(file_full)-1):
        file_dir += file_full[i] + '/'      # file_dir = C:/Users/Александр/Desktop/PVF/Фото/2022/Июнь/25Настя/
                                            # file_full[-1] = IMG_3805.jpg
    error, day, month, year = Metadata.date_from_exif(file)

    fileexist = ''

    if mode == 'copy':
        if error == 0:
            if os.path.isdir(destination + str(year) + '/' + str(month) + '/' + str(day)):
                if os.path.exists(destination + str(year) + '/' + str(month) + '/' + str(day) + '/' + file_full[-1]):
                    fileexist = file_full[-1]
                else:
                    shutil.copy2(file, destination + str(year) + '/' + str(month) + '/' + str(day) + '/' + file_full[-1])
                    Metadata.check_photo_rotation(destination + str(year) + '/' + str(month) + '/' + str(day) + '/' + file_full[-1])
                    Thumbnail.make_const_thumbnails(destination + str(year) + '/' + str(month) + '/' + str(day), file_full[-1])
                    PhotoDataDB.add_to_database(file_full[-1], destination + str(year) + '/' + str(month) + '/' + str(day))
            else:
                if not os.path.isdir(destination + str(year)):
                    os.mkdir(destination + str(year))
                if not os.path.isdir(destination + str(year) + '/' + str(month)):
                    os.mkdir(destination + str(year) + '/' + str(month))
                if not os.path.isdir(destination + str(year) + '/' + str(month) + '/' + str(day)):
                    os.mkdir(destination + str(year) + '/' + str(month) + '/' + str(day))
                    shutil.copy2(file, destination + str(year) + '/' + str(month) + '/' + str(day) + '/' + file_full[-1])
                    Metadata.check_photo_rotation(destination + str(year) + '/' + str(month) + '/' + str(day) + '/' + file_full[-1])
                    Thumbnail.make_const_thumbnails(destination + str(year) + '/' + str(month) + '/' + str(day), file_full[-1])
                    PhotoDataDB.add_to_database(file_full[-1], destination + str(year) + '/' + str(month) + '/' + str(day))
        else:   # error == 1
            if os.path.isdir(destination + 'No_Date_Info/No_Date_Info/No_Date_Info'):
                if os.path.exists(destination + 'No_Date_Info/No_Date_Info/No_Date_Info/' + file_full[-1] ):
                    fileexist = file_full[-1]
                else:
                    shutil.copy2(file, destination + 'No_Date_Info/No_Date_Info/No_Date_Info/' + file_full[-1])
                    Metadata.check_photo_rotation(destination + 'No_Date_Info/No_Date_Info/No_Date_Info' + '/' + file_full[-1])
                    Thumbnail.make_const_thumbnails(destination + 'No_Date_Info/No_Date_Info/No_Date_Info', file_full[-1])
                    PhotoDataDB.add_to_database(file_full[-1], destination + 'No_Date_Info/No_Date_Info/No_Date_Info')
            else:
                os.mkdir(destination + 'No_Date_Info')
                os.mkdir(destination + 'No_Date_Info/No_Date_Info')
                os.mkdir(destination + 'No_Date_Info/No_Date_Info/No_Date_Info')
                shutil.copy2(file, destination + 'No_Date_Info/No_Date_Info/No_Date_Info/' + file_full[-1] )
                Metadata.check_photo_rotation(destination + 'No_Date_Info/No_Date_Info/No_Date_Info' + '/' + file_full[-1])
                Thumbnail.make_const_thumbnails(destination + 'No_Date_Info/No_Date_Info/No_Date_Info', file_full[-1])
                PhotoDataDB.add_to_database(file_full[-1], destination + 'No_Date_Info/No_Date_Info/No_Date_Info')
    else:   # mode == 'cut'
        if error == 0:
            if os.path.isdir(destination + str(year) + '/' + str(month) + '/' + str(day)):    # папка назначения существует
                if os.path.exists(destination + str(year) + '/' + str(month) + '/' + str(day) + '/' + file_full[-1]):
                    fileexist = file_full[-1]         # файл с таким именем уже есть
                else:
                    shutil.move(file, destination + str(year) + '/' + str(month) + '/' + str(day) + '/')
                    Metadata.check_photo_rotation(destination + str(year) + '/' + str(month) + '/' + str(day) + '/' + file_full[-1])
                    Thumbnail.make_const_thumbnails(destination + str(year) + '/' + str(month) + '/' + str(day), file_full[-1])
                    PhotoDataDB.add_to_database(file_full[-1], destination + str(year) + '/' + str(month) + '/' + str(day))
            else:   # папки назначения не существует -> надо её создать, проверка на наличие файла не требуется
                if not os.path.isdir(destination + str(year)):
                    os.mkdir(destination + str(year))
                if not os.path.isdir(destination + str(year) + '/' + str(month)):
                    os.mkdir(destination + str(year) + '/' + str(month))
                if not os.path.isdir(destination + str(year) + '/' + str(month) + '/' + str(day)):
                    os.mkdir(destination + str(year) + '/' + str(month) + '/' + str(day))
                    shutil.move(file, destination + str(year) + '/' + str(month) + '/' + str(day) + '/')
                    Metadata.check_photo_rotation(destination + str(year) + '/' + str(month) + '/' + str(day) + '/' + file_full[-1])
                    Thumbnail.make_const_thumbnails(destination + str(year) + '/' + str(month) + '/' + str(day), file_full[-1])
                    PhotoDataDB.add_to_database(file_full[-1], destination + str(year) + '/' + str(month) + '/' + str(day))
        else:   # error == 1, т.е. даты в exif нет
            if os.path.isdir(destination + 'No_Date_Info/No_Date_Info/No_Date_Info'):
                if os.path.exists(destination + 'No_Date_Info/No_Date_Info/No_Date_Info/' + file_full[-1]):
                    fileexist = file_full[-1]
                else:
                    shutil.move(file, destination + 'No_Date_Info/No_Date_Info/No_Date_Info')
                    Metadata.check_photo_rotation(destination + 'No_Date_Info/No_Date_Info/No_Date_Info' + '/' + file_full[-1])
                    Thumbnail.make_const_thumbnails(destination + 'No_Date_Info/No_Date_Info/No_Date_Info', file_full[-1])
                    PhotoDataDB.add_to_database(file_full[-1], destination + 'No_Date_Info/No_Date_Info/No_Date_Info')
            else:
                os.mkdir(destination + 'No_Date_Info')
                os.mkdir(destination + 'No_Date_Info/No_Date_Info')
                os.mkdir(destination + 'No_Date_Info/No_Date_Info/No_Date_Info')
                shutil.move(file, destination + 'No_Date_Info/No_Date_Info/No_Date_Info/')
                Metadata.check_photo_rotation(destination + 'No_Date_Info/No_Date_Info/No_Date_Info' + '/' + file_full[-1])
                Thumbnail.make_const_thumbnails(destination + 'No_Date_Info/No_Date_Info/No_Date_Info', file_full[-1])       # создать миниатюру
                PhotoDataDB.add_to_database(file_full[-1], destination + 'No_Date_Info/No_Date_Info/No_Date_Info')           # добавить файл в БД

    return fileexist


# Перенос файлов, создание записи в БД и создание миниатюры для дополнительного каталога
def transfer_alone_photos(photo_directory: str, photofile: str, exists_dir_name='', type_add='dir') -> None:
    """
    Для фото file выполняется перенос, создаётся запись в БД, создаётся миниатюра.
    :param photo_directory: путь к папке, которая добавляется = 'C:/Users/user/Pictures/СНГ'
    :param photofile: абсолютный путь к файлу = 'C:/Users/user/Pictures/СНГ/20191231133253_IMG_2339.jpg'
    :param exists_dir_name: если добавляются файлы к папке, которая уже добавлена - имя этой папки.
    :param type_add: файлы в существующую папку или добавление целиковой новой папки.
    :return: файлы перенесены, записаны в БД и созданы миниатюры.
    """
    destination = Settings.get_destination_media() + '/Media/Photo/alone/'
    mode = Settings.get_photo_transfer_mode()

    if type_add != 'files':
        photo_directory_lastname = photo_directory.split('/')[-1]
    else:
        photo_directory_lastname = exists_dir_name

    photofile_lastname = photofile.split('/')[-1]

    if mode == 'copy':
        shutil.copy2(photofile, destination + photo_directory_lastname + '/' + photofile_lastname)
    else:   # mode == 'cut
        shutil.move(photofile, destination + photo_directory_lastname + '/' + photofile_lastname)

    Metadata.check_photo_rotation(destination + photo_directory_lastname + '/' + photofile_lastname)
    Thumbnail.make_alone_thumbnails(photo_directory_lastname, destination + photo_directory_lastname + '/' + photofile_lastname, photofile_lastname)
    PhotoDataDB.add_to_database(photofile_lastname, destination + photo_directory_lastname)


# удалить все файлы и папку из доп.каталога
def del_alone_dir(photo_directory: str) -> None:
    """
    Удаляется папка из доп.каталога (именно сама папка, записи в БД и миниатюры удаляются не тут).
    :param photo_directory: абсолютный путь к папке.
    :return: папка очищена и удалена.
    """
    photo_list = Thumbnail.get_images_list(photo_directory)
    for file in photo_list:
        os.remove(photo_directory + '/' + file)
    os.rmdir(photo_directory)


# очистка пустых папок при закрытии
def clear_empty_dirs(path) -> None:
    """
    При закрытии программы осуществляется попытка удаления пустых папок основного каталога.
    :param path: папка Settings.get_destination_media() + "/Media/Photo/const/"
    :return: удаляются пустые папки (если есть папка месяца, где 1 пустой день и больше ничего, то при 1 закрытии
    удалится только пустая папка дня, а уже при следующем, пустая папка месяца)
    """
    for d in os.listdir(path):
        a = os.path.join(path, d)
        if os.path.isdir(a):
            clear_empty_dirs(a)
            if not os.listdir(a):
                os.rmdir(a)

