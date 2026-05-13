# app.py

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO
import threading
from worker import download_m3u8
import os

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")

DOWNLOAD_FOLDER = "downloads"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():

    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({
            "success": False
        })

    threading.Thread(
        target=download_m3u8,
        args=(socketio, url)
    ).start()

    return jsonify({
        "success": True
    })

@app.route("/downloads/<path:filename>")
def downloads(filename):
    return send_from_directory(
        DOWNLOAD_FOLDER,
        filename,
        as_attachment=True
    )

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000
    )
