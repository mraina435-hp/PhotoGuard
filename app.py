from fileinput import filename

from flask import Flask, render_template, request, send_from_directory
import os
import json
import hashlib
from datetime import datetime
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
RECORD_FILE = "photo_records.json"

HISTORY_FILE = "verification_history.json"

if not os.path.exists(HISTORY_FILE):

    with open(HISTORY_FILE, "w") as file:

        json.dump([], file)

# Create record file if it does not exist
if not os.path.exists(RECORD_FILE):
    with open(RECORD_FILE, "w") as file:
        json.dump([], file)

#allowed image files
ALLOWED_EXTENSION={
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp"
}

def allowed_file(filename):
    return(
        "." in filename
        and filename.rsplit(".",1)[1].lower()
        in ALLOWED_EXTENSION
    )


# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Generate SHA-256 hash
def calculate_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as file:
        while True:
            data = file.read(4096)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()
# Protect photo

@app.route("/protect", methods=["POST"])
def protect():
    photo = request.files.get("photo")
    if photo is None or photo.filename == "":
        return "Please select a photo."
    safe_filename=os.path.basename(photo.filename)
    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        photo.filename
    )
    photo.save(file_path)

    # Generate SHA-256 fingerprint
    photo_hash = calculate_sha256(file_path)

    # Read existing records

    with open(RECORD_FILE, "r") as file:
        records = json.load(file)

    # Create record

    record = {
        "filename": photo.filename,
        "sha256": photo_hash,
        "protected_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }
    records.append(record)

    # Save record
    with open(RECORD_FILE, "w") as file:
        json.dump(records, file, indent=4)
    return f"""
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>PhotoGuard - Protected</title>

    <style>

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 30px;
            font-family: Arial, Helvetica, sans-serif;
            background-color: bisque;
            text-align: center;
        }}

        .card {{
            max-width: 600px;
            margin: 40px auto;
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }}

        h1 {{
            margin-bottom: 20px;
        }}

        img {{
            max-width: 100%;
            max-height: 350px;
            border-radius: 10px;
            margin: 15px 0;
        }}

        .hash {{
            background-color: #f1f1f1;
            padding: 15px;
            border-radius: 8px;
            word-break: break-all;
            font-size: 14px;
        }}

        button {{
            border: none;
            padding: 12px 20px;
            margin: 6px;
            border-radius: 8px;
            cursor: pointer;
            background-color: gainsboro;
            font-size: 15px;
        }}

        button:hover {{
            transform: scale(1.03);
        }}

        a {{
            text-decoration: none;
        }}

        .success {{
            font-size: 18px;
            color: green;
            font-weight: bold;
        }}

        .label {{
            font-weight: bold;
        }}

        @media (max-width: 600px) {{

            body {{
                padding: 15px;
            }}

            .card {{
                padding: 20px;
                margin: 20px auto;
            }}

            h1 {{
                font-size: 28px;
            }}

            button {{
                width: 90%;
            }}

        }}

    </style>

</head>

<body>

    <div class="card">

        <h1>🔐 Photo Protected Successfully!</h1>

        <p class="success">
            Your photo has been securely protected.
        </p>

        <p class="label">
            📸 Protected Photo
        </p>

        <img src="/uploads/{photo.filename}"
             alt="Protected Photo">

        <p class="label">
            🔑 SHA-256 Photo ID
        </p>

        <div class="hash">
            <b>{photo_hash}</b>
        </div>

        <p>
            Keep this SHA-256 ID safe.
            It can be used to verify your photo.
        </p>

        <br>

        <a href="/download/{photo.filename}">
            <button>
                📥 Download Protected Photo
            </button>
        </a>

        <br>

        <a href="/verify">
            <button>
                🔍 Verify Photo
            </button>
        </a>

        <br>

        <a href="/history">
            <button>
                📜 Verification History
            </button>
        </a>

        <br><br>

        <a href="/">
            🏠 Go Back Home
        </a>

    </div>

</body>

</html>
"""
# Display uploaded photo

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )

# Download photo

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )

# Verification page

@app.route("/verify")
def verify_page():
    return """

<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"

          content="width=device-width, initial-scale=1.0">

    <title>PhotoGuard - Verify</title>

    <style>

        * {

            box-sizing: border-box;

        }

        body {

            margin: 0;

            padding: 30px;

            font-family: Arial, Helvetica, sans-serif;

            background-color: bisque;

            text-align: center;

        }

        .card {

            max-width: 600px;

            margin: 50px auto;

            background-color: white;

            padding: 35px;

            border-radius: 15px;

            box-shadow: 0 5px 15px rgba(0,0,0,0.15);

        }

        h1 {

            margin-bottom: 15px;

        }

        p {

            color: #555;

            line-height: 1.5;

        }

        input[type="file"] {

            margin: 25px 0;

            padding: 10px;

            max-width: 100%;

        }

        button {

            border: none;

            padding: 12px 22px;

            margin: 8px;

            border-radius: 8px;

            cursor: pointer;

            background-color: gainsboro;

            font-size: 16px;

        }

        button:hover {

            transform: scale(1.03);

        }

        a {

            text-decoration: none;

        }

        @media (max-width: 600px) {

            body {

                padding: 15px;

            }

            .card {

                padding: 20px;

                margin: 25px auto;

            }

            h1 {

                font-size: 28px;

            }

            input[type="file"] {

                width: 100%;

            }

            button {

                width: 90%;

            }

        }

    </style>

</head>

<body>

    <div class="card">

        <h1>🔍 Verify Photo</h1>

        <p>

            Upload a photo to check whether it matches

            a protected PhotoGuard record.

        </p>

        <form action="/verify"

              method="POST"

              enctype="multipart/form-data">

            <input type="file"

                   name="photo"

                   accept="image/*"

                   required>

            <br>

            <button type="submit">

                🔍 Verify Photo

            </button>

        </form>

        <br>

        <a href="/">

            🏠 Go Back Home

        </a>

    </div>

</body>

</html>

"""

# Verify photo

@app.route("/verify", methods=["POST"])
def verify():
    photo = request.files.get("photo")
    if photo is None or photo.filename == "":
        return "Please select a photo."
 

    # Check file type
    if not allowed_file(photo.filename):
        return """
<!DOCTYPE html>
<html>
<head>
    <title>PhotoGuard - Invalid File</title>
</head>
<body style="
    text-align:center;
    font-family:Arial;
    background-color:bisque;
    padding:50px;
">
    <div style="
        max-width:500px;
        margin:auto;
        background:white;
        padding:35px;
        border-radius:15px;
        box-shadow:0 5px 15px rgba(0,0,0,0.15);
    ">
        <h1>❌ Invalid File</h1>
        <p>
            Please upload an image file only.
        </p>
        <p>
            Allowed formats:
            JPG, JPEG, PNG, GIF, WEBP
        </p>
        <br>
        <a href="/verify">
            <button style="
                padding:12px 20px;
                border:none;
                border-radius:8px;
            ">
                🔍 Try Again
            </button>
        </a>
    </div>
</body>
</html>
"""
    # Temporary verification file
    verify_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        "verify_" + photo.filename
    )
    photo.save(verify_path)


    # Generate SHA-256 of uploaded photo

    uploaded_hash = calculate_sha256(verify_path)

    # Read protected records

    with open(RECORD_FILE, "r") as file:
       records = json.load(file)
    
 

    # Compare exact SHA-256

    for record in records:
        if uploaded_hash == record["sha256"]:

        
        

            #save verification history
            with open(HISTORY_FILE,"r") as file:
                records=json.load(file)
                #compare exact SHA-256
                for record in records:
                    if uploaded_hash==record["sha256"]:
                        #save verification history
                        with open(HISTORY_FILE,"r") as file:
                            history = json.load(file)
                            history.append({
                                "filename":photo.filename,
                                "status":"verified",
                                "sha256":uploaded_hash,
                            "verified_at":datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            })
                        with open(HISTORY_FILE,"w") as file:
                                json.dump(history,file,indent=4)
                                if os.path.exists(verify_path):
                                    os.remove(verify_path)

            return f"""
            <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">
    <title>PhotoGuard - Verified</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            margin: 0;
            padding: 30px;
            font-family: Arial, Helvetica, sans-serif;
            background-color: bisque;
            text-align: center;
        }}
        .card {{
            max-width: 600px;
            margin: 50px auto;
            background-color: white;
            padding: 35px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }}
        .success {{
            color: green;
            font-size: 22px;
            font-weight: bold;
        }}
        .hash {{
            background-color: #f1f1f1;
            padding: 15px;
            border-radius: 8px;
            word-break: break-all;
            font-size: 14px;
        }}
        button {{
            border: none;
            padding: 12px 20px;
            margin: 7px;
            border-radius: 8px;
            cursor: pointer;
            background-color: gainsboro;
            font-size: 15px;
        }}
        button:hover {{
            transform: scale(1.03);
        }}
        a {{
            text-decoration: none;
        }}
        @media (max-width: 600px) {{
            body {{
                padding: 15px;
            }}
            .card {{
                padding: 20px;
            }}
            button {{
                width: 90%;
            }}
        }}
    </style>
</head>
<body>
    <div class="card">
        <h1>🛡️ PhotoGuard</h1>
        <p class="success">
            ✅ Photo Verified Successfully
        </p>
        <p>
            This is the exact protected photo.
        </p>
        <p>
            <b>📸 Photo Name:</b><br>
            {record["filename"]}
        </p>
        <p>
            <b>🔑 SHA-256 Photo ID:</b>
        </p>
        <div class="hash">
            {record["sha256"]}
        </div>
        <p>
            <b>🕒 Protected At:</b><br>
            {record.get("protected_at", "Not available")}
        </p>
        <br>
        <a href="/verify">
            <button>🔍 Verify Another Photo</button>
        </a>
        <a href="/history">
            <button>📜 Verification History</button>
        </a>
        <br>
        <a href="/">
            🏠 Go Back Home
        </a>
    </div>
</body>
</html>
"""
    # Save failed verification history

    with open(HISTORY_FILE, "r") as file:
        history = json.load(file)
    history.append({
        "filename": photo.filename,
        "status": "Not Verified",
        "sha256": uploaded_hash,
        "verified_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    })
    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)

    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">
    <title>PhotoGuard - Not Verified</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            margin: 0;
            padding: 30px;
            font-family: Arial, Helvetica, sans-serif;
            background-color: bisque;
            text-align: center;
        }
        .card {
            max-width: 600px;
            margin: 50px auto;
            background-color: white;
            padding: 35px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }
        .failed {
            color: #b00020;
            font-size: 22px;
            font-weight: bold;
        }
        button {
            border: none;
            padding: 12px 20px;
            margin: 7px;
            border-radius: 8px;
            cursor: pointer;
            background-color: gainsboro;
            font-size: 15px;
        }
        button:hover {
            transform: scale(1.03);
        }
        a {
            text-decoration: none;
        }
        @media (max-width: 600px) {
            body {
                padding: 15px;
            }
            .card {
                padding: 20px;
            }
            button {
                width: 90%;
            }
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>🛡️ PhotoGuard</h1>
        <p class="failed">
            ❌ Photo Not Verified
        </p>
        <p>
            This photo does not match any protected photo.
        </p>
        <p>
            The file may be different, cropped,
            edited, or modified.
        </p>
        <br>
        <a href="/verify">
            <button>🔍 Try Another Photo</button>
        </a>
        <a href="/history">
            <button>📜 Verification History</button>
        </a>
        <br>
        <a href="/">
            🏠 Go Back Home
        </a>
    </div>
</body>
</html>
"""
    
# Verification History

@app.route("/history")
def history():
    with open(RECORD_FILE, "r") as file:
        records = json.load(file)
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">
        <title>PhotoGuard - History</title>
        <style>
            * {
                box-sizing: border-box;
            }
            body {
                margin: 0;
                padding: 30px;
                font-family: Arial, Helvetica, sans-serif;
                background-color: bisque;
            }
            .container {
                max-width: 1000px;
                margin: auto;
            }
            h1 {
                text-align: center;
                margin-bottom: 30px;
            }
            .card {
                background-color: white;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.15);
                overflow-x: auto;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th {
                background-color: gainsboro;
                padding: 12px;
                border:1px solid #999;
            }
            td {
                padding: 12px;
                border: 1px solid #ddd;
                text-align: center;
            }
            button {
                border: none;
                padding: 9px 15px;
                border-radius: 7px;
                cursor: pointer;
                background-color: gainsboro;
            }
            button:hover {
                transform: scale(1.03);
            }
            .back {
                text-align: center;
                margin-top: 25px;
            }
            a {
                text-decoration: none;
            }
            @media (max-width: 600px) {
                body {

                    padding: 15px;
                }
                h1 {
                    font-size: 28px;
                }
                .card {
                    padding: 10px;
                }
                table {
                    font-size: 13px;
                }
                th, td {
                    padding: 8px;
                }
            }
        </style>
    </head>
    <body>
    <div class="container">
    <h1>📜 Verification History</h1>
    <div class="card">
    <table>
        <tr>
            <th>Photo Name</th>
            <th>SHA-256</th>
            <th>Protected At</th>
            <th>Details</th>
        </tr>
    """
    for record in records:
                html += f"""
            <tr>
                <td>{record["filename"]}</td>
                <td>{record["sha256"]}</td>
                <td>{record["protected_at"]}</td>
                <td>
                    <a href="/details/{record["filename"]}">
                        <button>Details</button>
                    </a>
                </td>
            </tr>
        """
    html += """
        </table>
<br><br>
        <div class="back-btn">
            <a href="/">
                <button>Go Back</button>
            </a>
        </div>

    </body>
    </html>
    """

    return html


# Protection Details
@app.route("/details/<filename>")
def protection_details(filename):

    with open(RECORD_FILE, "r") as file:
        records = json.load(file)

    for record in records:

        if record["filename"] == filename:

            return f"""
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>PhotoGuard - Protection Details</title>

    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 30px;
            font-family: Arial, Helvetica, sans-serif;
            background-color: bisque;
            text-align: center;
        }}

        .card {{
            max-width: 650px;
            margin: 40px auto;
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }}

        h1 {{
            margin-bottom: 25px;
        }}

        .photo {{
            max-width: 100%;
            max-height: 350px;
            border-radius: 10px;
            margin: 15px 0 25px;
        }}

        .detail {{
            text-align: left;
            background-color: #f5f5f5;
            padding: 15px;
            margin: 12px 0;
            border-radius: 8px;
        }}

        .label {{
            font-weight: bold;
        }}

        .hash {{
            word-break: break-all;
            margin-top: 8px;
            font-size: 14px;
        }}

        .status {{
            color: green;
            font-weight: bold;
        }}

        button {{
            border: none;
            padding: 12px 20px;
            margin: 7px;
            border-radius: 8px;
            cursor: pointer;
            background-color: gainsboro;
            font-size: 15px;
        }}

        button:hover {{
            transform: scale(1.03);
        }}

        a {{
            text-decoration: none;
        }}

        @media (max-width: 600px) {{
            body {{
                padding: 15px;
            }}

            .card {{
                padding: 20px;
                margin: 20px auto;
            }}

            h1 {{
                font-size: 28px;
            }}

            button {{
                width: 90%;
            }}
        }}
    </style>

</head>

<body>

<div class="card">

    <h1>🔐 Protection Details</h1>

    <img class="photo"
         src="/uploads/{record["filename"]}"
         alt="Protected Photo">

    <div class="detail">

        <span class="label">
            📸 Photo Name:
        </span>

        <br>

        {record["filename"]}

    </div>


    <div class="detail">

        <span class="label">
            🛡️ Protection Status:
        </span>

        <br>

        <span class="status">
            ✅ Protected
        </span>

    </div>


    <div class="detail">

        <span class="label">
            🔑 SHA-256 Photo ID:
        </span>

        <div class="hash">
            {record["sha256"]}
        </div>

    </div>


    <div class="detail">

        <span class="label">
            🕒 Protected At:
        </span>

        <br>

        {record.get("protected_at", "Not available")}

    </div>


    <br>


    <!-- DELETE BUTTON -->

    <form action="/delete/{filename}"
          method="POST"
          onsubmit="return confirm('Are you sure you want to delete this protected photo?');">

        <button type="submit" class="delete-button">
            🗑️ Delete Photo
        </button>

    </form>


    <!-- HISTORY BUTTON -->

    <a href="/history">

        <button type="button">
            📜 Back to History
        </button>

    </a>


    <!-- HOME BUTTON -->

    <a href="/">

        <button type="button">
            🏠 Home
        </button>

    </a>

</div>

</body>

</html>
"""

    return """
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>PhotoGuard - Photo Not Found</title>

</head>

<body style="text-align:center;
             font-family:Arial;
             padding:50px;
             background-color:bisque;">

    <div style="background:white;
                max-width:600px;
                margin:50px auto;
                padding:40px;
                border-radius:15px;">

        <h1>⚠️ Photo Not Found</h1>

        <p>
            The requested photo record could not be found.
        </p>

        <br>

        <a href="/history">

            <button type="button">
                📜 Back to History
            </button>

        </a>

        <a href="/">

            <button type="button">
                🏠 Home
            </button>

        </a>

    </div>

</body>

</html>
"""


        

@app.route("/delete/<filename>", methods=["POST"])

def delete_photo(filename):

    with open(RECORD_FILE, "r") as file:

        records = json.load(file)

    updated_records = []

    found = False

    for record in records:

        if record["filename"] == filename:

            found = True

            file_path = os.path.join(

                app.config["UPLOAD_FOLDER"],

                filename

            )

            if os.path.exists(file_path):

                os.remove(file_path)

        else:

            updated_records.append(record)

    with open(RECORD_FILE, "w") as file:

        json.dump(updated_records, file, indent=4)

    if found:

        return """

        <!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"

          content="width=device-width, initial-scale=1.0">

    <title>PhotoGuard - Photo Deleted</title>

    <style>

        * {

            box-sizing: border-box;

        }

        body {

            margin: 0;

            padding: 30px;

            font-family: Arial, Helvetica, sans-serif;

            background-color: bisque;

            text-align: center;

        }

        .card {

            max-width: 600px;

            margin: 70px auto;

            background-color: white;

            padding: 40px 30px;

            border-radius: 15px;

            box-shadow: 0 5px 15px rgba(0,0,0,0.15);

        }

        .icon {

            font-size: 55px;

            margin-bottom: 10px;

        }

        h1 {

            margin-bottom: 15px;

        }

        .success {

            color: green;

            font-size: 20px;

            font-weight: bold;

        }

        p {

            color: #555;

            line-height: 1.5;

        }

        .info {

            background-color: #f5f5f5;

            padding: 15px;

            border-radius: 8px;

            margin: 20px 0;

        }

        button {

            border: none;

            padding: 12px 22px;

            margin: 7px;

            border-radius: 8px;

            cursor: pointer;

            background-color: gainsboro;

            font-size: 15px;

        }

        button:hover {

            transform: scale(1.03);

        }

        a {

            text-decoration: none;

        }

        @media (max-width: 600px) {

            body {

                padding: 15px;

            }

            .card {

                margin: 30px auto;

                padding: 25px 20px;

            }

            button {

                width: 90%;

            }

        }

    </style>

</head>

<body>

    <div class="card">

        <div class="icon">

            🗑️

        </div>

        <h1>

            Photo Deleted

        </h1>

        <p class="success">

            ✅ Photo Deleted Successfully

        </p>

        <div class="info">

            <p>

                The protected photo and its

                PhotoGuard protection record

                have been permanently removed.

            </p>

            <p>

                🔐 The SHA-256 protection record

                is no longer stored.

            </p>

        </div>

        <a href="/history">

            <button>

                📜 Back to History

            </button>

        </a>

        <a href="/">

            <button>

                🏠 Go Back Home

            </button>

        </a>

    </div>

</body>

</html>

"""

    return """

<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"

          content="width=device-width, initial-scale=1.0">

    <title>PhotoGuard - Error</title>

</head>

<body style="text-align:center; font-family:Arial; padding:50px;">

    <h1>⚠️ Photo Not Found</h1>

    <p>

        The requested photo record could not be found.

    </p>

    <br>

    <a href="/history">

        <button>📜 Back to History</button>

    </a>

    <a href="/">

        <button>🏠 Home</button>

    </a>

</body>

</html>


        """
    
    return "Photo record not found."

@app.route("/about")
def about():
    return """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>PhotoGuard - About</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 30px;
            font-family: Arial, Helvetica, sans-serif;
            background-color: bisque;
            text-align: center;
        }

        .card {
            max-width: 650px;
            margin: 30px auto;
            background-color: white;
            padding: 35px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }

        .step {
            text-align: left;
            background-color: #f5f5f5;
            padding: 15px;
            margin: 12px 0;
            border-radius: 10px;
        }

        button {
            border: none;
            padding: 12px 22px;
            margin-top: 15px;
            border-radius: 8px;
            cursor: pointer;
            background-color: gainsboro;
            font-size: 15px;
        }

        a {
            text-decoration: none;
        }

    </style>

</head>

<body>

    <div class="card">

        <h1>🛡️ About PhotoGuard</h1>

        <p>
            PhotoGuard helps protect and verify personal photos
            using SHA-256 digital fingerprints.
        </p>

        <div class="step">
            <h3>📤 1. Upload Photo</h3>
            <p>Upload your photo to PhotoGuard.</p>
        </div>

        <div class="step">
            <h3>🔑 2. Generate SHA-256</h3>
            <p>
                PhotoGuard creates a unique SHA-256 fingerprint
                for the uploaded photo.
            </p>
        </div>

        <div class="step">
            <h3>🛡️ 3. Protect Photo</h3>
            <p>
                The fingerprint and protection details are stored
                for future verification.
            </p>
        </div>

        <div class="step">
            <h3>🔍 4. Verify Photo</h3>
            <p>
                The uploaded photo is compared with the stored
                SHA-256 fingerprint.
            </p>
        </div>

        <div class="step">
            <h3>❌ 5. Detect Changes</h3>
            <p>
                If the photo is cropped, edited, or modified,
                its SHA-256 fingerprint changes.
            </p>
        </div>

        <a href="/">
            <button>🏠 Go Back Home</button>
        </a>

    </div>

</body>

</html>
"""

@app.route("/help")
def help_page():
    return """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>PhotoGuard - Help</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 30px;
            font-family: Arial, Helvetica, sans-serif;
            background-color: bisque;
            text-align: center;
        }

        .card {
            max-width: 650px;
            margin: 30px auto;
            background-color: white;
            padding: 35px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }

        .question {
            text-align: left;
            background-color: #f5f5f5;
            padding: 15px;
            margin: 12px 0;
            border-radius: 10px;
        }

        .question h3 {
            margin-top: 0;
        }

        button {
            border: none;
            padding: 12px 22px;
            margin-top: 15px;
            border-radius: 8px;
            cursor: pointer;
            background-color: gainsboro;
            font-size: 15px;
        }

        a {
            text-decoration: none;
        }

        @media (max-width: 600px) {

            body {
                padding: 15px;
            }

            .card {
                padding: 20px;
            }

        }

    </style>

</head>

<body>

    <div class="card">

        <h1>❓ PhotoGuard Help</h1>

        <div class="question">
            <h3>🔐 How do I protect a photo?</h3>
            <p>
                Select your photo on the Home page and click
                "Protect My Photo".
            </p>
        </div>

        <div class="question">
            <h3>🔍 How do I verify a photo?</h3>
            <p>
                Open Verify Photo, select the photo and click
                "Verify Photo".
            </p>
        </div>

        <div class="question">
            <h3>❌ Why is my photo Not Verified?</h3>
            <p>
                If the photo has been cropped, edited, modified,
                or is not the original protected file, its
                SHA-256 fingerprint will be different.
            </p>
        </div>

        <div class="question">
            <h3>📜 Where can I see my records?</h3>
            <p>
                Open Verification History to view protected
                photo records and SHA-256 details.
            </p>
        </div>

        <div class="question">
            <h3>🔑 What is SHA-256?</h3>
            <p>
                SHA-256 is a cryptographic hash function that
                creates a unique fingerprint for a file.
            </p>
        </div>

        <a href="/">
            <button>🏠 Go Back Home</button>
        </a>

    </div>

</body>

</html>
"""

if __name__ == "__main__":
    app.run(debug=True)