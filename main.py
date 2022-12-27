from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os
import sqlite3
import socket
# import mimetypes
from werkzeug.datastructures import FileStorage
import re

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg"}

HASH_ALGORITHM = "sha256"
MAX_FILE_SIZE = 10 * 1024 * 1024 # 10MB

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# FILE_NAME_PATTERN = r"[a-zA-Z0-9_\.-]+" 
FILE_NAME_PATTERN = r"[a-zA-Z0-9_\.-\s]+"

DEBUG = 1



def allowed_file(filename):

    # Check if the file extension is in the whitelist
    if not "." in filename or filename.rsplit(".", 1)[1].lower() not in ALLOWED_EXTENSIONS:
        if DEBUG: print("file extension is not in the whitelist")
        return False

    # Check if the file's MIME type matches the file extension
    file = request.files.get("file")
    if not isinstance(file, FileStorage):
        if DEBUG: print("not isinstance(file, FileStorage)")
        return False
    # if not file.mimetype.startswith(file.filename.rsplit(".", 1)[1].lower() + "/"):
    #     if DEBUG: print("mimetype lie")
    #     return False

    # Check if the file path is within the UPLOAD_FOLDER directory and return False if it is not
    # file_path = os.path.join(UPLOAD_FOLDER, filename)
    # if not os.path.realpath(file_path).startswith(UPLOAD_FOLDER):
    #     if DEBUG: print("attempted to move directory")
    #     return False

    # both of the above are broken

    # if file.size > MAX_FILE_SIZE:
    #     if DEBUG: print("File too big")
    #     return False

    # if not re.match(FILE_NAME_PATTERN, filename): # prevent stuff like ..
    #     if DEBUG: print("illegeal pattern detected in name")
    #     return False


    # if hasattr(file, "check_hash"):
    #     # can use sha256
    #     if not file.check_hash(HASH_ALGORITHM, file.filename):
    #         if DEBUG: print("checksum error")
    #         return False

    # # perform these checks on the server side, rather than the client side, to prevent malicious users from bypassing the checks.
    # if file.scan_for_virus() or file.scan_for_security_vulnerabilities():
    #     if DEBUG: print("virus detected error")
    #     return False

    # If the file passes all checks, it is allowed
    return True


    

# def allowed_file(filename):
#     # Get the MIME type of the file
#     file_mimetype = mimetypes.guess_type(filename)[0]
#     print("File MIME type: ", file_mimetype)

#     # Check if the MIME type is in the whitelist
#     return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS and file_mimetype in ALLOWED_MIMETYPES

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
            filename = secure_filename(file.filename)

            # Store file in uploads folder
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            # Store file information in database
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
    fileID = request.form.get("fileid")
    # print("Delete: ", fileID) debug
    
    # Delete file from database
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    # file_id = c.execute("SELECT id FROM files WHERE name = ?", (fileID,))
    # c.execute("DELETE FROM files WHERE name = ?", (filename,))
    c.execute("DELETE FROM files WHERE id = ?", (fileID,))

    conn.commit()
    conn.close()

    # Redirect back to index page
    return redirect(url_for("home"))



@app.route("/delete_all", methods=["POST"])
def delete_all_file():
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    c.execute("DELETE FROM files")
    conn.commit()
    conn.close()

    # Redirect back to index page
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

    # ip_address = '0.0.0.0' # override

    # Get custom word
    # word = "app"

    # Get IP address
    # ip_address = socket.gethostbyname(word)

    print("Hostname:", hostname)
    app.run(host=ip_address)
    
