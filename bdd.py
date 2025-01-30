import sqlite3
from datetime import datetime
from threading import local

thread_local = local()

def get_connection():
    if not hasattr(thread_local, "connection"):
        thread_local.connection = sqlite3.connect('emails.db')
    return thread_local.connection

# À appeler pour créer le emails.sb
def initialisation():
    conn = get_connection()
    cursor = conn.cursor()
    # Créer les tables si elles n'existent pas encore
    cursor.execute('''CREATE TABLE IF NOT EXISTS Email (
                        idm INTEGER NOT NULL PRIMARY KEY,
                        date TEXT NOT NULL,
                        sujet TEXT,
                        corps TEXT,
                        lieu TEXT,
                        theme TEXT)''')

    conn.commit()


def ajout_mail_bdd(uid: str, date: datetime, subject: str, text: str, folder: str | None):
    conn = get_connection()
    cursor = conn.cursor()
    if cursor.execute('''SELECT idm FROM Email WHERE idm = ?''', (uid,)).fetchone() is None:
                cursor.execute('''INSERT INTO Email (idm, date, sujet, corps, lieu) VALUES (?, ?, ?, ?, ?)''', 
                (uid, date, subject, text, folder))
                conn.commit()

def retirer_mail_bdd(uid: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM Email WHERE idm = ?''', (uid,))
    conn.commit()

def ajouter_theme(uid: str, theme: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''UPDATE Email SET theme = ? WHERE idm = ?''', (theme, uid,))
    conn.commit()