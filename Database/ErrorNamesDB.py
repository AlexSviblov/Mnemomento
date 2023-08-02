# coding: utf-8
import os
import sqlite3


conn = sqlite3.connect(f"file:{os.getcwd()}\\ErrorNames.db", check_same_thread=False, uri=True)
cur = conn.cursor()


def edit_error_name(column: str, new_name: str, old_name: str) -> None:
    """
    Редактирование записи
    :param column: колонка (normname/exifname/type)
    :param new_name: новое значение клетки
    :param old_name: старое значение
    """
    sql_red_str = f"UPDATE ernames SET {column} = '{new_name}' WHERE {column} = '{old_name}'"
    cur.execute(sql_red_str)
    conn.commit()


def get_all_ernames() -> list[tuple[str]]:
    """
    Все данные из таблицы
    """
    cur.execute("SELECT * FROM ernames")
    all_results = cur.fetchall()
    return all_results


def add_ername(equip_type: str, error_name: str, norm_name: str) -> None:
    """
    Добавить новую запись в таблицу исправлений
    :param equip_type: тип (объектив/камера/производитель)
    :param error_name: неправильное название из метаданных
    :param norm_name: корректное название для отображения
    """
    enter_1 = "INSERT INTO ernames(type,exifname,normname) VALUES(?,?,?)"
    enter_2 = (equip_type, error_name, norm_name)

    try:
        cur.execute(enter_1, enter_2)
    except sqlite3.OperationalError:
        raise sqlite3.OperationalError

    conn.commit()


def delete_ername(exif_name: str) -> None:
    """
    Удалить запись из таблицы
    :param exif_name: заменяемое название
    """
    sql_del_str = f"DELETE FROM ernames WHERE exifname LIKE '{exif_name}'"
    cur.execute(sql_del_str)
    conn.commit()


def get_norname_for_exifname(name_type: str, exif_name: str) -> str:
    sql_str = f"SELECT normname FROM ernames WHERE type = \'{name_type}\' AND exifname = \'{exif_name}\'"
    cur.execute(sql_str)
    try:
        res = cur.fetchone()[0]
        return res
    except TypeError:
        return ""
