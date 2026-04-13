from flask import Flask, request, jsonify, send_from_directory

# Flask — the thing that creates your server
# request — lets you access data that was sent TO your server (like a photo from ESP32)
# jsonify — lets you send JSON responses back (like {"message": "photo saved"})

import os

# Lets you do file system stuff — create folders, build file paths, check if files exist

from datetime import datetime

# Lets you get the current date and time


# creates server
# A server is just a program that waits for requests and sends responses back.
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# checks to see if a photo was recieved from post request to server
# if not, error
# if yes, make photo name with time stamp, put in uploads folder, and send success message
@app.route("/upload", methods=["POST"])
def upload():
    if "photo" not in request.files:
        return jsonify({"error": "no photo received"}), 400
    photo = request.files["photo"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"bird_{timestamp}.jpeg"
    photo.save(os.path.join(UPLOAD_FOLDER, filename))
    print(f"saved: {filename}")
    return jsonify({"message": "photo saved"}), 200


# fetch a single photo
# makes request to get file when browser sees html img tag
@app.route("/uploads/<filename>")
def serve_photo(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# displays all photos in browser
# Looks inside the uploads folder
# Gets a list of every file in there and makes html page w a tag for each image
@app.route("/photos")
def photos():
    images = sorted(os.listdir(UPLOAD_FOLDER), reverse=True)
    html = "<h1>Bird Feeder Cam</h1>"
    for image in images:
        html += f'<img src="/uploads/{image}" width="400"><br>'
    return html


# defines url endpoint
# An endpoint is a specific function on your server that handles a specific task.
# “If someone visits the homepage /, run the function below.” essentially where requests and sent / recieved at addy
@app.route("/")
def home():
    return "BirdCam server running!"


# allows ESP32 to access your laptop on the same Wi-Fi
# start server, accept connections from other devices on the wifi, where server lives
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
