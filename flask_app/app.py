
#This is for smart ESP32 bird feeder camera that uses motion detection and a Flask dashboard for viewing pictures of birds that enter the feeder.
#app.py includes all of the flask code used to fetch image data from the esp32 cam microcontroller and display it onto a dashboard
#esp32 code is not included






from flask import Flask, request, jsonify, send_from_directory, make_response

# Flask — the thing that creates your server
# request — lets you access data that was sent TO your server (like a photo from ESP32)
# jsonify — lets you send JSON responses back (like {"message": "photo saved"})
# send from dir - send_from_directory() is a secure function used to serve files from a specific directory to a client.
# make_response — lets you add custom headers to responses (like cache control)

import os

# Lets you do file system stuff — create folders, build file paths, check if files exist

from datetime import datetime

# Lets you get the current date and time


# creates server
# A server is just a program that waits for requests and sends responses back.
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# creates name var for upload folder
# makes an upload folder directory


# checks to see if a photo was recieved from post request to server
# if not, error
# if yes, make photo name with time stamp, put in uploads folder, and send success message
@app.route("/upload", methods=["POST"])
def upload():
    # request and verify photo data from esp32
    # data is sent in raw jpeg bytes instead of multipart form data
    photo_data = request.data
    print(f"Incoming photo size: {len(photo_data)} bytes")

    if not photo_data:
        return jsonify({"error": "no photo received"}), 400

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"bird_{timestamp}.jpeg"
    # write raw bytes to file
    with open(os.path.join(UPLOAD_FOLDER, filename), "wb") as f:
        f.write(photo_data)
    print(f"saved: {filename}")
    return jsonify({"message": "photo saved"}), 200


# fetch a single photo
# makes request to get file when browser sees html img tag
# cache control headers tell browser never to cache images
# so deleted photos disappear and new ones show instantly
@app.route("/uploads/<filename>")
def serve_photo(filename):
    response = make_response(send_from_directory(UPLOAD_FOLDER, filename))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return response


# displays all photos in browser
# Looks inside the uploads folder
# filters out non-image files like .DS_Store
# Gets a list of every file in there and makes html page w a tag for each image
# auto refreshes every 5 seconds so new photos appear automatically
@app.route("/photos")
def photos():
    images = sorted(
        [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.jpeg') or f.endswith('.jpg')],
        reverse=True
    )
    html = """
    <!doctype html>
    <html lang="en">
    <head>
        <title>Bird Watch</title>
        <meta http-equiv="refresh" content="5">
        <meta http-equiv="Cache-Control" content="no-store, no-cache, must-revalidate">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            :root {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                color: #1f2a24;
                background: #f5f6f2;
            }

            body {
                max-width: 1200px;
                margin: 0 auto;
                padding: 24px 16px 40px;
            }

            h1 {
                margin: 0 0 18px;
                font-size: 1.6rem;
                font-weight: 600;
            }

            .photo-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, 400px);
                gap: 8px;
                justify-content: start;
            }

            .photo-grid img {
                display: block;
                width: 100%;
                aspect-ratio: 4 / 3;
                object-fit: cover;
                background: #e3e7df;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
    <h1>Bird Watch</h1>
    <main class="photo-grid">
    """
    for image in images:
        html += f'<img src="/uploads/{image}" alt="Bird photo">'
    html += "</main></body></html>"
    return html


# defines url endpoint
# An endpoint is a specific function on your server that handles a specific task.
# "If someone visits the homepage /, run the function below." essentially where requests and sent / recieved at addy
@app.route("/")
def home():
    return "BirdCam server running!"


# allows ESP32 to access your laptop on the same Wi-Fi
# start server, accept connections from other devices on the wifi, where server lives
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
