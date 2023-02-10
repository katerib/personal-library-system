import pandas as pd
import sqlite3
import os

# read dataset into pandas dataframe
data_path = 'data/blank.csv'
headers = ['title', 'author', 'rating', 'pages']
data_table = pd.read_csv(data_path, header=0)

# clear shelf.db if it exists
if os.path.exists('shelf.db'):
    os.remove('shelf.db')

# create database
conn = sqlite3.connect('shelf.db', check_same_thread=False)

# add data to database
data_table.to_sql('data_table', conn, dtype={
    'title': 'VARCHAR(256)',
    'author': 'VARCHAR(256)',
    'rating': 'VARCHAR(256)',
    'pages': 'VARCHAR(256)',
})

conn.row_factory = sqlite3.Row


def sql_query(query):
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    return rows


def sql_edit_insert(query, var):
    cur = conn.cursor()
    cur.execute(query, var)
    conn.commit()


def sql_csv_insert(query, var):
    cur = conn.cursor()
    cur.executemany(query, var)
    conn.commit()


def sql_delete(query, var):
    cur = conn.cursor()
    cur.execute(query, var)


def sql_query2(query, var):
    cur = conn.cursor()
    cur.execute(query, var)
    rows = cur.fetchall()
    return rows