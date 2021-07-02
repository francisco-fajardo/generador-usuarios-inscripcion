#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import ttk
from tkinter import *

import secrets
import string
import os
import sqlite3

class App:
    data_dir = "data"
    db_file = os.path.join(data_dir, "database.db")

    version = "v1.0.0"

    def __init__(self, window):
        self.window = window
        self.window.title("Generador de usuarios {}".format(self.version))

        if (os.path.exists(self.data_dir) is False):
            os.mkdir(self.data_dir)

        if (os.path.exists(self.db_file) is False):
            with open(self.db_file, "w") as file:
                conn = sqlite3.connect(self.db_file)
                c = conn.cursor()

                c.execute("""
                    CREATE TABLE users (
                        user text,
                        password text
                    )
                """)

                conn.commit()

        try:
            self.conn = sqlite3.connect(self.db_file)
        except Error as e:
            return

        frame = LabelFrame(self.window, text = "Registrar un nuevo usuario")
        frame.grid(row = 0, column = 0, columnspan=1, padx=10, pady=10, sticky= W + E)

        # Cedula input
        Label(frame, text = "Cedula: ").grid(row = 1, column = 0, pady=10, padx=10)
        self.cedula = Entry(frame)
        self.cedula.focus()
        self.cedula.grid(row = 1, column = 1, padx=10)

        # Save user button
        ttk.Button(frame, text = "Generar usuario", command = self.generate_user).grid(row = 2, columnspan = 2, pady=20, padx=10, sticky = W + E)
        self.window.bind("<Return>", (lambda event: self.generate_user()))

        # Output messages
        self.message = Label(text = "", fg = "red", font=("Arial", 12, "bold"))
        self.message.grid(row = 2, column = 0, columnspan = 3, pady=10, sticky = W + E)

        # Table
        self.tree = ttk.Treeview(height = 10, columns = 2)
        self.tree.grid(row = 3, column = 0, columnspan = 3)
        self.tree.heading("#0", text = "Usuario", anchor = CENTER)
        self.tree.heading("#1", text = "Contraseña", anchor = CENTER)

        # Buttons
        ttk.Button(text = "Eliminar", command = self.delete_user).grid(row = 4, column = 0, sticky = W + E)

        self.users_total = Label(text = "Usuarios totales: {}".format(self.count_users()), font=("Arial", 11, "bold"))
        self.users_total.grid(row = 5, column = 0, sticky = W + E)

        # Filling the rows
        self.get_users()

    def generate_user(self):
        cedula = self.cedula.get()

        if str.isdigit(cedula) is False:
            self.message["text"] = "Cedula invalida"

            return False

        # verify if user is before created
        user_is_created = False
        db_rows = self.run_query("SELECT * FROM users WHERE user = ?", (cedula,))
        for row in db_rows:
            if bool(row):
                user_is_created = True
                pass

        if user_is_created:
            self.message["text"] = "Usuario ya creado"
            return

        # Generate password
        alphabet = string.ascii_uppercase + string.digits
        password = "".join(secrets.choice(alphabet) for i in range(8))

        # Insert data in the database
        query = "INSERT INTO users VALUES(?, ?)"
        parameters = (cedula, password)
        self.run_query(query, parameters)
        self.message["text"] = "Usuario: {}\nContraseña: {}".format(cedula, password)
        self.cedula.delete(0, END)
        self.get_users()

    def delete_user(self):
        try:
            self.tree.item(self.tree.selection())["text"][0]
        except IndexError as e:
            self.message["text"] = "Por favor selecciona un usuario"
            return

        cedula = self.tree.item(self.tree.selection())["text"]
        query = "DELETE FROM users WHERE user = ?"
        self.run_query(query, (cedula,))
        self.message["text"] = "Usuario eliminado satisfactoriamente"
        self.get_users()

    def get_users(self):
        # cleaning table
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)

        # getting data
        query = "SELECT rowid, * FROM users"
        db_rows = self.run_query(query)

        # filling data
        for row in db_rows:
            self.tree.insert("", row[0], text = row[1], values = row[2])

    def run_query(self, query, parameters = ()):
        cursor = self.conn.cursor()
        result = cursor.execute(query, parameters)
        self.conn.commit()

        return result

    def count_users(self):
        query = "SELECT * FROM users"
        result = self.run_query(query)

        return len(result.fetchall())

if __name__ == "__main__":
    window = Tk()
    window.geometry("405x470")
    application = App(window)
    window.mainloop()
