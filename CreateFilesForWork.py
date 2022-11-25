import sqlite3
import json
import os

conn = sqlite3.connect(r'C:\Users\Public\AppData\TestForPhotoPr\PhotoDB.db')   # соединение с БД
cur = conn.cursor()

sql_str1 = 'CREATE TABLE photos (filename TEXT, catalog TEXT, camera TEXT, lens TEXT, shootingdate TEXT, shootingdatetime TEXT, additiondate TEXT, GPSdata TEXT)'

sql_str2 = 'CREATE TABLE socialnetworks (filename TEXT, catalog TEXT, shootingdate TEXT)'

cur.execute(sql_str1)
cur.execute(sql_str2)

conn.commit()
conn.close()


conn = sqlite3.connect('C:/Users/user/PycharmProjects/PhotoExeNotTouched/ErrorNames.db')   # соединение с БД
cur = conn.cursor()

sql_str3 = 'CREATE TABLE ernames (type TEXT, exifname TEXT, normname TEXT)'

cur.execute(sql_str3)

conn.commit()
conn.close()


jsondata_wr =   {
                            "files":
                                    {
                                    "destination_dir": "",
                                    "thumbs_dir": "",
                                    "transfer_mode": ""
                                    },
                            "view":
                                    {
                                    "thumbs_row": "",
                                    "color_theme": "",
                                    "social_networks_status": "",
                                    "sort_type": ""
                                    }
                            }

with open('settings.json', 'w') as json_file:
    json.dump(jsondata_wr, json_file, sort_keys=True, indent=4, separators=(',', ': '))

jsondata_wr =       {
                  "open_file": "Ctrl+S",
                  "edit_metadata": "Ctrl+E",
                  "open_explorer": "Ctrl+D",
                  "delete_file": "Del",
                  "show_stat_map": "Enter"
                    }

with open('hotkeys.json', 'w') as json_file:
    json.dump(jsondata_wr, json_file, sort_keys=True, indent=4, separators=(',', ': '))

jsondata_wr = {
    "last_opened_photo": "",
}

with open('last_opened.json', 'w') as json_file:
    json.dump(jsondata_wr, json_file, sort_keys=True, indent=4, separators=(',', ': '))

os.mkdir(f"{os.getcwd()}/Media")
os.mkdir(f"{os.getcwd()}/thumbnail")
os.mkdir(f"{os.getcwd()}/Media/Photo")
os.mkdir(f"{os.getcwd()}/Media/Photo/const")
os.mkdir(f"{os.getcwd()}/Media/Photo/alone")
os.mkdir(f"{os.getcwd()}/thumbnail/const")
os.mkdir(f"{os.getcwd()}/thumbnail/alone")
os.mkdir(f"{os.getcwd()}/thumbnail/view")



