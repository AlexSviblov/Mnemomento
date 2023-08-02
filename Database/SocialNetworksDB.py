# coding: utf-8
import os
import sqlite3


conn = sqlite3.connect(f"file:{os.getcwd()}\\PhotoDB.db", check_same_thread=False, uri=True)
cur = conn.cursor()


def add_network(name: str) -> None:
    sql_str = f"ALTER TABLE socialnetworks ADD COLUMN {name} TEXT DEFAULT \'No value\'"
    try:
        cur.execute(sql_str)
    except sqlite3.OperationalError:  # название колонны не может начинаться с цифр и некоторых потенциально служебных символов
        textwithnum = "numnumnum" + name
        sql_str = f"ALTER TABLE socialnetworks ADD COLUMN {textwithnum} TEXT DEFAULT \'No value\'"
        cur.execute(sql_str)
    conn.commit()


def rename_network(old_name: str, new_name: str) -> None:
    sql_str = f"ALTER TABLE socialnetworks RENAME COLUMN {old_name} TO {new_name}"
    try:
        cur.execute(sql_str)
    except sqlite3.OperationalError:  # название колонны не может начинаться с цифр и некоторых потенциально служебных символов
        textwithnum = "numnumnum" + new_name
        sql_str = f"ALTER TABLE socialnetworks RENAME COLUMN {old_name} TO {textwithnum}"
        cur.execute(sql_str)
    conn.commit()


def delete_network(name: str) -> None:
    sql_str = f"ALTER TABLE socialnetworks DROP COLUMN {name}"
    cur.execute(sql_str)
    conn.commit()
