import os
import shutil
import Settings
import Metadata
import Thumbnail
import PhotoDataDB
import ErrorsAndWarnings


# Достаёт список файлов расширения jpg из папки
def make_files_list_from_dir(directory: str) -> list[str, ...]:
    file_list = list()
    for file in os.listdir(directory):
        if file.endswith(".jpg") or file.endswith(".JPG"):
            file_list.append(directory + '/' + file)
    return file_list


# Создание миниатюр для основного каталога
def transfer_const_photos(file: str) -> str:
    destination = Settings.get_destination_media() + '/Media/Photo/const/'
    mode = Settings.get_photo_transfer_mode()

    current_dir = os.getcwd()
    file_dir = ''
    file_full = file.split(r'/')
    for i in range(len(file_full)-1):
        file_dir += file_full[i] + '/'      # file_dir = C:/Users/Александр/Desktop/PVF/Фото/2022/Июнь/25Настя/
                                            # file_full[-1] = IMG_3805.jpg

    error, day, month, year = Metadata.date_from_exif(file_dir, current_dir, file_full[-1])

    fileexist = ''

    if mode == 'copy':
        if error == 0:
            if os.path.isdir(destination + str(year) + '/' + str(month) + '/' + str(day)):
                if os.path.exists(destination + str(year) + '/' + str(month) + '/' + str(day) + '/' + file_full[-1]):
                    fileexist = file_full[-1]
                else:
                    shutil.copy2(file, destination + str(year) + '/' + str(month) + '/' + str(day) + '/' + file_full[-1])
                    Thumbnail.make_const_thumbnails(destination + str(year) + '/' + str(month) + '/' + str(day), file_full[-1])
                    PhotoDataDB.add_to_database(file_full[-1], destination + str(year) + '/' + str(month) + '/' + str(day))
            else:
                if not os.path.isdir(destination + str(year)):
                    os.mkdir(destination + str(year))
                if not os.path.isdir(destination + str(year) + '/' + str(month)):
                    os.mkdir(destination + str(year) + '/' + str(month))
                if not os.path.isdir(destination + str(year) + '/' + str(month) + '/' + str(day)):
                    os.mkdir(destination + str(year) + '/' + str(month) + '/' + str(day))
                    shutil.copy2(file, destination + str(year) + '/' + str(month) + '/' + str(day) + '/' + file_full[-1] )
                    Thumbnail.make_const_thumbnails(destination + str(year) + '/' + str(month) + '/' + str(day), file_full[-1])
                    PhotoDataDB.add_to_database(file_full[-1], destination + str(year) + '/' + str(month) + '/' + str(day))
        else:   # error == 1
            if os.path.isdir(destination + 'No_Date_Info/No_Date_Info/No_Date_Info'):
                if os.path.exists(destination + 'No_Date_Info/No_Date_Info/No_Date_Info/' + file_full[-1] ):
                    fileexist = file_full[-1]
                else:
                    shutil.copy2(file, destination + 'No_Date_Info/No_Date_Info/No_Date_Info/' + file_full[-1])
                    Thumbnail.make_const_thumbnails(destination + 'No_Date_Info/No_Date_Info/No_Date_Info', file_full[-1])
                    PhotoDataDB.add_to_database(file_full[-1] , destination + 'No_Date_Info/No_Date_Info/No_Date_Info')
            else:
                os.mkdir(destination + 'No_Date_Info')
                os.mkdir(destination + 'No_Date_Info/No_Date_Info')
                os.mkdir(destination + 'No_Date_Info/No_Date_Info/No_Date_Info')
                shutil.copy2(file, destination + 'No_Date_Info/No_Date_Info/No_Date_Info/' + file_full[-1] )
                Thumbnail.make_const_thumbnails(destination + 'No_Date_Info/No_Date_Info/No_Date_Info', file_full[-1])
                PhotoDataDB.add_to_database(file_full[-1], destination + 'No_Date_Info/No_Date_Info/No_Date_Info')

    else:   # mode == 'cut'
        if error == 0:
            if os.path.isdir(destination + str(year) + '/' + str(month) + '/' + str(day)):    # папка назначения существует
                if os.path.exists(destination + str(year) + '/' + str(month) + '/' + str(day) + '/' + file_full[-1]):
                    fileexist = file_full[-1]         # файл с таким именем уже есть
                else:
                    shutil.move(file, destination + str(year) + '/' + str(month) + '/' + str(day) + '/')
                    Thumbnail.make_const_thumbnails(destination + str(year) + '/' + str(month) + '/' + str(day), file_full[-1])
                    PhotoDataDB.add_to_database(file_full[-1] , destination + str(year) + '/' + str(month) + '/' + str(day))
            else:   # папки назначения не существует -> надо её создать, проверка на наличие файла не требуется
                if not os.path.isdir(destination + str(year)):
                    os.mkdir(destination + str(year))
                if not os.path.isdir(destination + str(year) + '/' + str(month)):
                    os.mkdir(destination + str(year) + '/' + str(month))
                if not os.path.isdir(destination + str(year) + '/' + str(month) + '/' + str(day)):
                    os.mkdir(destination + str(year) + '/' + str(month) + '/' + str(day))
                    shutil.move(file, destination + str(year) + '/' + str(month) + '/' + str(day) + '/')
                    Thumbnail.make_const_thumbnails(destination + str(year) + '/' + str(month) + '/' + str(day), file_full[-1])
                    PhotoDataDB.add_to_database(file_full[-1], destination + str(year) + '/' + str(month) + '/' + str(day))
        else:   # error == 1, т.е. даты в exif нет
            if os.path.isdir(destination + 'No_Date_Info/No_Date_Info/No_Date_Info'):
                if os.path.exists(destination + 'No_Date_Info/No_Date_Info/No_Date_Info/' + file_full[-1]):
                    fileexist = file_full[-1]
                else:
                    shutil.move(file, destination + 'No_Date_Info/No_Date_Info/No_Date_Info')
                    Thumbnail.make_const_thumbnails(destination + 'No_Date_Info/No_Date_Info/No_Date_Info', file_full[-1])
                    PhotoDataDB.add_to_database(file_full[-1], destination + 'No_Date_Info/No_Date_Info/No_Date_Info')
            else:
                os.mkdir(destination + 'No_Date_Info')
                os.mkdir(destination + 'No_Date_Info/No_Date_Info')
                os.mkdir(destination + 'No_Date_Info/No_Date_Info/No_Date_Info')
                shutil.move(file, destination + 'No_Date_Info/No_Date_Info/No_Date_Info/')
                Thumbnail.make_const_thumbnails(destination + 'No_Date_Info/No_Date_Info/No_Date_Info', file_full[-1])       # создать миниатюру
                PhotoDataDB.add_to_database(file_full[-1], destination + 'No_Date_Info/No_Date_Info/No_Date_Info')           # добавить файл в БД
    return fileexist


# Создание миниатюр для дополнительного каталога
def transfer_alone_photos(photo_directory: str, photofile: str, exists_dir_name='', type_add='dir') -> None:
    destination = Settings.get_destination_media() + '/Media/Photo/alone/'
    mode = Settings.get_photo_transfer_mode()

    if type_add != 'files':
        photo_directory_lastname = photo_directory.split('/')[-1]
    else:
        photo_directory_lastname = exists_dir_name

    photofile_lastname = photofile.split('/')[-1]

    Thumbnail.make_alone_thumbnails(photo_directory_lastname, photofile, photofile_lastname)

    if mode == 'copy':
        shutil.copy2(photofile, destination + photo_directory_lastname + '/' + photofile_lastname)
    else:   # mode == 'cut
        shutil.move(photofile, destination + photo_directory_lastname + '/' + photofile_lastname)

    PhotoDataDB.add_to_database(photofile_lastname, destination + photo_directory_lastname)


# удалить все файлы и папку из доп.каталога
def del_alone_dir(photo_directory: str) -> None:
    photo_list = Thumbnail.get_images_list(photo_directory)
    for file in photo_list:
        os.remove(photo_directory + '/' + file)

    os.rmdir(photo_directory)
