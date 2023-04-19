from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os
import sqlite3
import socket
# import mimetypes
# from werkzeug.datastructures import FileStorage
import re
from filesecurity import allowed_file
import shutil

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

        file = request.files["file"]

        if file.filename == "":
            return "No selected file"

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) # such a cool function

            # ensure storage dir exists
            if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                os.makedirs(app.config["UPLOAD_FOLDER"])
        
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            conn = sqlite3.connect("files.db")
            c = conn.cursor()

            # the AUTOINCREMENT property in the CREATE TABLE statement will automatically generate a unique, sequential ID for the record. 
            # This ID will be used as the id value for the record, and it will be unique for each record in the table.
            # https://dev.mysql.com/doc/mysql-tutorial-excerpt/5.7/en/example-auto-increment.html

            # cursor = c.execute("INSERT INTO files (id, name, size) VALUES (id INTEGER PRIMARY KEY AUTOINCREMENT, ?, ?)", (id, filename, os.path.getsize(os.path.join(UPLOAD_FOLDER, filename)))) 
            cursor = c.execute("INSERT INTO files (name, size) VALUES (?, ?)", (filename, os.path.getsize(os.path.join(UPLOAD_FOLDER, filename)))) 

            conn.commit()
            conn.close()

            return redirect(url_for("home"))

        return "FILE NOT ALLOWED"
    # else get

    return redirect(url_for("home"))

@app.route("/", methods=["GET"])
def home():
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, size INTEGER)") #AUTOINCREMENT
    c.execute("SELECT * FROM files")
    files = c.fetchall()
    # print("num files:", files.__sizeof__())
    conn.close()

    # Render index.html template, passing the list of files as a variable
    return render_template("index.html", files=files)


@app.route("/delete", methods=["POST"])
def delete_file():
    fileID = request.form.get("fileid")
    filename = request.form.get("filename")
    # print("Delete: ", fileID) debug
    
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    # filename = c.execute("SELECT name FROM files WHERE id = ?", (fileID,))
    if DEBUG: print("\nline 84 filname: {}\n".format(filename))
    # c.execute("DELETE FROM files WHERE name = ?", (filename,))
    c.execute("DELETE FROM files WHERE id = ?", (fileID,))

    conn.commit()
    conn.close()

    # remove file from server
    delete(filename)

    return redirect(url_for("home"))

def delete(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        print("Successfully deleted: " + filename)
    return redirect(url_for("index"))



@app.route("/delete_all", methods=["POST"])
def delete_all_file():
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    c.execute("DELETE FROM files")
    conn.commit()
    conn.close()

    # file_path = os.path.join(app.config["UPLOAD_FOLDER"], "")
    # os.remove(file_path)

    # os.remove("UPLOAD_FOLDER") # OG used to work
    # apparently broken

    # Delete the uploads directory and all its contents
    shutil.rmtree(app.config['UPLOAD_FOLDER'])


    # os.remove(os.path(app.config["UPLOAD_FOLDER"]))

    return redirect(url_for("index"))


@app.route("/download/<filename>")
def download_file(filename):
    if DEBUG: print("/download ")
    # Check if file exists
    if os.path.isfile(os.path.join(UPLOAD_FOLDER, filename)):
        # Send file as response
        return send_file(os.path.join(UPLOAD_FOLDER, filename))

    return "Error 404 FILE NOT FOUND"


if __name__ == "__main__":
    # Get hostname
    hostname = socket.gethostname()

    # Get IP address
    ip_address = socket.gethostbyname(hostname)

    #function may return the loopback address (127.0.0.1) 
    # if your device is not connected to a network. 
    # In this case, you will not be able to use this IP address to make your program accessible to other devices on the local network.

    # print("Hostname:", hostname)

    app.run(host=ip_address)
    
