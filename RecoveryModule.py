# предварительно спросить, сделать ли бэкап - реализовать позже
# 1 - пройтись по записям в бд, посмотреть наличие файлов, если файл есть в бд, но нет в каталоге - удалить запись в бд
# 2 - если была удалена запись в бд - удалить миниатюру, если оан есть
# 3 - проход по всем фото в каталоге, проверка наличия записей в БД, если нет - создать
# 4 - если создана запись в бд - создать миниатюру при её отстутствии

import os
import sqlite3
import Thumbnail
import FilesDirs
import PhotoDataDB
import Settings

def get_files_exists_list():
    media_path = Settings.get_destination_media()
    #we shall store all the file names in this list
    filelist = list()

    for root, dirs, files in os.walk(media_path):
        for file in files:
            #append the file name to the list
            filelist.append(os.path.join(root,file))

    truenames = list()
    #print all the file names
    for name in filelist:
        if '\\' in name:
            truenames.append(name.replace('\\', '/'))
        else:
            truenames.append(name)

    return truenames

def get_files_in_DB():

    pass
#можно учесть вариант, со сравнением имён файлов, но отличием папок
