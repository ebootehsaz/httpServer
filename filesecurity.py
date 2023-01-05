from flask import request
from werkzeug.datastructures import FileStorage
import mimetypes
import os
import re

ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg"}
ALLOWED_MIMETYPES = { "text/plain", "application/pdf", "image/png", "image/jpeg",
}

HASH_ALGORITHM = "sha256"
MAX_FILE_SIZE = 10 * 1024 * 1024 # 10MB

# FILE_NAME_PATTERN = r"[a-zA-Z0-9_\.-]+" 
FILE_NAME_PATTERN = r"[a-zA-Z0-9_]+"

DEBUG = 1

# UPLOAD_FOLDER = "uploads"

def allowed_file(filename):
    # Check if the file extension is in the whitelist
    # Check if the file's MIME type matches the file extension

    file = request.files.get("file")
    if not isinstance(file, FileStorage):
        if DEBUG: print("not isinstance(file, FileStorage)")
        return False


    if not allowed_mimetype_and_extension(filename):
        return False

    # Check if the file path is within the UPLOAD_FOLDER directory and return False if it is not
    # flawed, can modify to check whole path within system but then more security issues
    # filename: uploads/file.txt
    # file_path = os.path.join(UPLOAD_FOLDER, filename)
    # if os.path.realpath(file_path).split("/")[-2] != (UPLOAD_FOLDER):
    #     if DEBUG: 
    #         print("{} \n{}".format(os.path.realpath(file_path).split("/")[-2], (UPLOAD_FOLDER)))
    #     return False



    # if file.size > MAX_FILE_SIZE:
    #     if DEBUG: print("File too big")
    #     return False

    if not re.match(FILE_NAME_PATTERN, filename): # prevent stuff like ..
        if DEBUG: print("illegeal pattern detected in name")
        return False


    # If the file passes all checks, it is allowed
    return True


def allowed_mimetype_and_extension(filename):
    # Get the MIME type of the file
    file_mimetype = mimetypes.guess_type(filename)[0]
    print("File MIME type: ", file_mimetype)

    # Check if the MIME type is in the whitelist
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS and file_mimetype in ALLOWED_MIMETYPES
