from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os
import sqlite3
import socket

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/uploads", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"

        file = request.files["file"]

        if file.filename == "":
            return "No selected file"

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Store file in uploads folder
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            # Store file information in database
            conn = sqlite3.connect("files.db")
            c = conn.cursor()

            # the AUTOINCREMENT property in the CREATE TABLE statement will automatically generate a unique, sequential ID for the record. 
            # This ID will be used as the id value for the record, and it will be unique for each record in the table.
            # https://dev.mysql.com/doc/mysql-tutorial-excerpt/5.7/en/example-auto-increment.html

            cursor = c.execute("INSERT INTO files (name, size) VALUES (?, ?)", (filename, os.path.getsize(os.path.join(UPLOAD_FOLDER, filename)))) 
            file_id = cursor.lastrowid

            conn.commit()
            conn.close()

            return redirect(url_for("home"))

        return "Invalid file"
    # else get

    return redirect(url_for("home"))

@app.route("/", methods=["GET"])
def home():
        # Retrieve information about all files from database
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
    # Get filename from form data
    filename = request.form.get("filename")
    print("Delete: ", filename)
    

    # Delete file from database
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    file_id = c.execute("SELECT id FROM files WHERE name = ?", (filename,)).fetchone()[0]
    # c.execute("DELETE FROM files WHERE name = ?", (filename,))
    c.execute("DELETE FROM files WHERE id = ?", (file_id,))

    conn.commit()
    conn.close()

    # Redirect back to index page
    return redirect(url_for("home"))


@app.route("/download/<filename>")
def download_file(filename):
    # Check if file exists
    if os.path.isfile(os.path.join(UPLOAD_FOLDER, filename)):
        # Send file as response
        return send_file(os.path.join(UPLOAD_FOLDER, filename))

    return "File not found"



@app.route("/delete_all", methods=["POST"])
def delete_all_file():
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    c.execute("DELETE FROM files")
    conn.commit()
    conn.close()

    # Redirect back to index page
    return redirect(url_for("index"))



if __name__ == "__main__":
    # Get hostname
    hostname = socket.gethostname()

    # Get IP address
    ip_address = socket.gethostbyname(hostname)

    #function may return the loopback address (127.0.0.1) 
    # if your device is not connected to a network. 
    # In this case, you will not be able to use this IP address to make your program accessible to other devices on the local network.

    app.run(host=ip_address)
    
