from PIL import Image
import os
import shutil
import Settings

destination_thumbs = Settings.get_destination_thumb()


# получение списка файлов формата jpg из папки
def get_images_list(directory: str) -> list[str, ...]:
    file_list = list()
    for file in os.listdir(directory):
        if file.endswith(".jpg") or file.endswith(".JPG"):
            file_list.append(file)
    return file_list


# Создать миниатюры при добавлении папки или файлов "на постоянку" в основной каталог
def make_const_thumbnails(directory: str, file: str) -> None:
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
    image.thumbnail((250, 250))
    image.save('thumbnail_%s' % file)
    date = year + '/' + month + '/' + day
    os.replace('thumbnail_%s' % file, destination_thumbs + f'/thumbnail/const/{date}/thumbnail_{file}')
    image.close()


# Создать миниатюры при добавлении папки или файлов "на постоянку" в дополнительный каталог
def make_alone_thumbnails(directory_lastname: str, photofile: str, photofile_lastname: str) -> None:
    if not os.path.isdir(destination_thumbs + '/thumbnail/alone/' + directory_lastname):
        os.mkdir(destination_thumbs + '/thumbnail/alone/' + directory_lastname)

    image = Image.open(r"{}".format(photofile))
    image.thumbnail((250, 250))
    image.save('thumbnail_%s' % photofile_lastname)
    os.replace('thumbnail_%s' % photofile_lastname, destination_thumbs + '/thumbnail/alone/' + directory_lastname + f'/thumbnail_{photofile_lastname}')
    image.close()


# Сравнение, какие миниатюры лишние, каких недостаточно
def research_flaw_thumbnails(photo_directory: str, thumbnail_directory: str) -> tuple[list[str], list[str]]:
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
    nedostatok_thumbs_result = list(set(images_list) - set(thumbs_already))  # есть фото, но нет миниатюр
    excess_thumbs_result = list(set(thumbs_already) - set(images_list))  # есть миниатюра, а фото нет
    return nedostatok_thumbs_result, excess_thumbs_result


# Создание недостающих миниатюр и удаление лишних
def make_or_del_thumbnails(flaw_thumbnails: list, excess_thumbs: list, photo_directory: str, thumbnail_directory: str) -> None:
    if flaw_thumbnails:
        for file in flaw_thumbnails:
            image = Image.open(r"{}".format(photo_directory + '/' + file))
            image.thumbnail((250, 250))
            image.save('thumbnail_%s' % file)
            os.replace('thumbnail_%s' % file, thumbnail_directory + f'/thumbnail_{file}')
            image.close()

    if excess_thumbs:
        for file in excess_thumbs:
            os.remove(thumbnail_directory + '/thumbnail_' + file)


# Создание миниатюр для просмотра
def make_thumbnails_view(photo_file: str) -> None:
    photo_splitted = photo_file.split('/')
    photo_name = photo_splitted[-1]     # C:/Users/Александр/Desktop/PVF/Фото/2022/Июнь/25Настя/IMG_4090.jpg
    image = Image.open(r"{}".format(photo_file))
    image.thumbnail((250, 250))
    image.save('thumbnail_%s' % photo_name)
    os.replace('thumbnail_%s' % photo_name, destination_thumbs + '/thumbnail/view' + f'/thumbnail_{photo_name}')
    image.close()


# удаление миниатюр фото для разового просмотра
def delete_exists() -> None:
    existing_thumbs = get_images_list(destination_thumbs + '/thumbnail/view/')
    for file in existing_thumbs:
        os.remove(destination_thumbs + '/thumbnail/view/' + file)


# Удалить миниатюру файла, удаляемого из основного каталога
def delete_thumbnail_const(photoname: str, photodirectory: str) -> None:
    dir_splitted = photodirectory.split('/')
    date_part = dir_splitted[-3]+'/'+dir_splitted[-2]+'/'+dir_splitted[-1]
    thumb_dir = destination_thumbs + '/thumbnail/const/' + date_part
    os.remove(thumb_dir + '/thumbnail_' + photoname)


# перенос миниатюры при изменении даты в метаданных снимка
def transfer_equal_date_thumbnail(old_name: str, new_name: str, old_date: list[str, str, str], new_date: list[str, str, str], rename_name: str, chosen: str) -> None:
    if chosen == 'old':    # переименовывают файл уже находящийся в папке
        os.rename(destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/' + old_date[2] + f'/thumbnail_{old_name}',
                  destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/' + old_date[2] + f'/thumbnail_{rename_name}')
        shutil.move(destination_thumbs + '/thumbnail/const/' + new_date[0] + '/' + new_date[1] + '/' + new_date[2] + f'/thumbnail_{new_name}',
                    destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/' + old_date[2] + '/')

    else:   # chosen == 'new' - переименовывают переносимый файл
        os.rename(destination_thumbs + '/thumbnail/const/' + new_date[0] + '/' + new_date[1] + '/' + new_date[2] + f'/thumbnail_{new_name}',
                  destination_thumbs + '/thumbnail/const/' + new_date[0] + '/' + new_date[1] + '/' + new_date[2] + f'/thumbnail_{rename_name}')
        shutil.move(destination_thumbs + '/thumbnail/const/' + new_date[0] + '/' + new_date[1] + '/' + new_date[2] + f'/thumbnail_{rename_name}',
                    destination_thumbs + '/thumbnail/const/' + old_date[0] + '/' + old_date[1] + '/' + old_date[2] + '/')


# удалить миниатюру после переноса файла
def transfer_diff_date_thumbnail(photoname: str, new_date: list[str, str, str], old_date: list[str, str, str]) -> None:
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
    dir_splitted = photodirectory.split('/')
    dir_name = dir_splitted[-1]
    thumb_dir = destination_thumbs + '/thumbnail/alone/' + dir_name
    os.remove(thumb_dir + '/thumbnail_' + photoname)


# Удалить все миниатюры и сами фото директории из доп.каталога
def delete_thumb_dir(photodirectory: str) -> None:
    photo_dir_splitted = photodirectory.split('/')
    dir_name = photo_dir_splitted[-1]
    thumb_dir = destination_thumbs + '/thumbnail/alone/' + dir_name
    thumb_list = get_images_list(thumb_dir)
    for file in thumb_list:
        os.remove(destination_thumbs + f'/thumbnail/alone/{dir_name}/{file}')

    os.rmdir(destination_thumbs + f'/thumbnail/alone/{dir_name}')

