from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO
import subprocess
import threading
import uuid
import os
import json
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sans'

socketio = SocketIO(app, cors_allowed_origins="*")

DOWNLOAD_FOLDER = "downloads"
HISTORY_FILE = "history.json"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def load_history():

    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(data):

    history = load_history()

    history.insert(0, data)

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[:100], f, indent=4)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/history")
def history():
    return jsonify(load_history())

@app.route("/download", methods=["POST"])
def download():

    data = request.json

    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL"})

    file_id = str(uuid.uuid4())

    output = os.path.join(
        DOWNLOAD_FOLDER,
        f"{file_id}.mp4"
    )

    thread = threading.Thread(
        target=download_worker,
        args=(url, output, file_id)
    )

    thread.start()

    return jsonify({
        "success": True,
        "id": file_id
    })

@app.route("/file/<file_id>")
def get_file(file_id):

    path = os.path.join(
        DOWNLOAD_FOLDER,
        f"{file_id}.mp4"
    )

    if not os.path.exists(path):
        return "File not found"

    return send_file(
        path,
        as_attachment=True
    )

def download_worker(url, output, file_id):

    cmd = [
        "ffmpeg",
        "-i",
        url,
        "-c",
        "copy",
        output,
        "-y"
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    for line in process.stdout:

        socketio.emit("log", {
            "id": file_id,
            "message": line
        })

    process.wait()

    if process.returncode == 0:

        save_history({
            "url": url,
            "file": f"{file_id}.mp4",
            "time": int(time.time())
        })

        socketio.emit("done", {
            "id": file_id
        })

    else:

        socketio.emit("error", {
            "id": file_id
        })

if __name__ == "__main__":
    socketio.run(app, debug=True)