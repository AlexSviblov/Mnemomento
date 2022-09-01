import logging
import os
import exif
from PIL import Image
import sqlite3


with open('C:/Users/Public/AppData/TestForPhotoPr/tests/new_jpg.jpg', 'rb') as img:
    img = exif.Image('C:/Users/Public/AppData/TestForPhotoPr/tests/new_jpg.jpg')

data = img.get_all()
keys = list(data.keys())

print(data)

for parameter in range(len(data)):
    print(keys[parameter])
    print(str(data[keys[parameter]]))
    print(type(data[keys[parameter]]))
    print("\n")



