from flask import Flask, request, render_template, send_file, redirect, url_for, make_response
from werkzeug.utils import secure_filename
import os
import sqlite3
import socket
# import mimetypes
from werkzeug.datastructures import FileStorage
import re
from filesecurity import allowed_file

UPLOAD_FOLDER = "./uploads"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

DEBUG = 0

@app.route("/uploads", methods=["GET", "POST"])
def index():
    # print("/upload index(), request: ", request.method) debug
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"

        # file = request.files["file"]
        file = request.files.get("file")

        if file.filename == "":
            return "No selected file"

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            
            #  file data/blob to store
            file_data = file.read()

            # Store file information in database
            conn = sqlite3.connect("uploads.db")
            c = conn.cursor()

            # the AUTOINCREMENT property in the CREATE TABLE statement will automatically generate a unique, sequential ID for the record. 
            # This ID will be used as the id value for the record, and it will be unique for each record in the table.
            # https://dev.mysql.com/doc/mysql-tutorial-excerpt/5.7/en/example-auto-increment.html

            # cursor = c.execute("INSERT INTO files (id, name, size) VALUES (id INTEGER PRIMARY KEY AUTOINCREMENT, ?, ?)", (id, filename, os.path.getsize(os.path.join(UPLOAD_FOLDER, filename)))) 
            # cursor = c.execute("INSERT INTO files (name, data) VALUES (?, ?)", (file.filename, file_data)) 
            cursor = c.execute("INSERT INTO files (name, data) VALUES (?, ?)", (filename, file_data)) 

            conn.commit()
            conn.close()

            return redirect(url_for("home"))

        return "FILE NOT ALLOWED"
    # else get

    return redirect(url_for("home"))

@app.route("/", methods=["GET"])
def home():
    # Retrieve
    conn = sqlite3.connect("uploads.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, data BLOB)") #AUTOINCREMENT
    # c.execute("SELECT * FROM files")
    c.execute("SELECT id, name FROM files")

    files = c.fetchall()
    # print("num files:", files.__sizeof__())
    conn.close()

    return render_template("index.html", files=files)


@app.route("/delete", methods=["POST"])
def delete_file():
    # Get filename from form data
    fileID = request.form.get("fileid")
    # print("Delete: ", fileID) debug
    
    # Delete file from database
    conn = sqlite3.connect("uploads.db")
    c = conn.cursor()
    # filename = c.execute("SELECT name FROM files WHERE id = ?", (fileID,))
    # c.execute("DELETE FROM files WHERE name = ?", (filename,))
    c.execute("DELETE FROM files WHERE id = ?", (fileID,))

    conn.commit()
    conn.close()


    # Redirect back to index page
    return redirect(url_for("home"))



@app.route("/delete_all", methods=["POST"])
def delete_all_file():
    conn = sqlite3.connect("uploads.db")
    c = conn.cursor()
    c.execute("DELETE FROM files")
    conn.commit()
    conn.close()

    return redirect(url_for("index"))


@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    conn = sqlite3.connect("uploads.db")
    cursor = conn.cursor()

    cursor.execute("SELECT data FROM files WHERE name=?", (filename,))
    file_data = cursor.fetchone()[0]

    # Send the file data to the client as a response
    response = make_response(file_data)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response




if __name__ == "__main__":
    # Get hostname
    hostname = socket.gethostname()

    # Get IP address
    ip_address = socket.gethostbyname(hostname)

    #function may return the loopback address (127.0.0.1) 
    # if your device is not connected to a network. 
    # In this case, you will not be able to use this IP address to make your program accessible to other devices on the local network.

    # ip_address = '0.0.0.0' # override

    # Get custom word
    # word = "app"

    # Get IP address
    # ip_address = socket.gethostbyname(word)

    # print("Hostname:", hostname)

    app.run(host=ip_address)
    
